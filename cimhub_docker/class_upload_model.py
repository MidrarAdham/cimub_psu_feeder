import os
import sys
import csv
import time
import json
import argparse
import subprocess
import pandas as pd
import cimhub.api as cimhub
from pprint import pprint as pp
from gridappsd import GridAPPSD
from pathlib import Path as path
from gridappsd import topics as t
import xml.etree.ElementTree as et
from datetime import datetime as dt
import cimhub.CIMHubConfig as CIMHubConfig
from gridappsd.simulation import Simulation

'''
This script uploads a customized IEEE-13 Node Feeder to GridAPPS-D Blazegraph. 

Feeder Properties:
    
    1- The feeder is designed to handle approximately 1000 loads.
    2- Each load is customized with several home appliances (dishwashers, water heaters, etc)
    3- The feeder is tested to run without overloading issues for a week.
    4- The feeder is originally designed in GridLAB-D. It was then converted to OpenDSS.

Script main functionalities:

    1- Uploads the feeder to the Blazegraph.
    2- Creates testing scripts to compare the powerflow of the GridLAB-D and OpenDSS 
    versions of the feeder.
    3- Creates the needed configuration files and historical data to run the Modeling Environment (ME)

'''
class upload_feeder_blazegraph():

    def __init__(self):
        
        # Get Paths
        self.current_dir = path().absolute()

        # Set up exported files folders
        path('dss').mkdir(parents=False, exist_ok=True)
        path('glm').mkdir(parents=False, exist_ok=True)
        path('config').mkdir(parents=False, exist_ok=True)

        # Setup file names:
        self.dss_name = 'Master'

    def upload_model_to_blazegraph(self):
        os.system(f'curl -D- -H "Content-Type: application/xml" --upload-file {self.current_dir}/dss/{self.dss_name}.xml -X POST {CIMHubConfig.blazegraph_url}')
    
    def list_feeders(self):
        os.system(f'java -cp "./target/libs/*:./target/cimhub-0.0.1-SNAPSHOT.jar" gov.pnnl.gridappsd.cimhub.CIMImporter -u={CIMHubConfig.blazegraph_url} -o=idx test')

class dss_configuration_file ():
    
    def __init__(self):

        # Set file names:
        self.setting_file_name = 'cim_test.dss'

        self.feeder = upload_feeder_blazegraph()

        # Change directory to OpenDSS folder:
        os.chdir(f"{self.feeder.current_dir}/dss/")

        # OS Compatibility:
        if sys.platform == 'win32':
            self.shfile_glm = './glm/checkglm.bat'
            self.shfile_run = 'checkglm.bat'
        else:
            self.shfile_glm = './glm/checkglm.sh'
            self.shfile_run = './checkglm.sh'

    def connect_to_gridappsd(self):
        
        os.environ['GRIDAPPSD_USER'] = 'tutorial_user'
        os.environ['GRIDAPPSD_PASSWORD'] = '12345!'
        os.environ['GRIDAPPSD_ADDRESS'] = 'localhost'
        os.environ['GRIDAPPSD_PORT'] = '61613'
        self.gapps_session = GridAPPSD()
        assert self.gapps_session.connected
    
    def set_query(self):
        self.message = {
        "requestType": "QUERY_MODEL_INFO",
        "resultFormat": "JSON"
        }
    
    def get_query_response(self):
        topic = t.REQUEST_POWERGRID_DATA
        self.query_resp = self.gapps_session.get_response(topic, self.message)

    def get_mrids (self):
        
        for i in range(len(self.query_resp['data']['models'])):
            if self.query_resp['data']['models'][i]['modelName'].startswith('psu_'):
                self.mrids = {
                    'line_name':self.query_resp['data']['models'][i]['modelId'],
                    'geo_rgn':self.query_resp['data']['models'][i]['regionId'],
                    'sub_rgn':self.query_resp['data']['models'][i]['subRegionId'],
                    'simulation_name':self.query_resp['data']['models'][i]['modelName']
                    }
        
    def OpenDSS_Settings(self):
    
        self.cases = [
            {'dssname':self.feeder.dss_name, 'root':self.feeder.dss_name, 'mRID':f'"{self.mrids["line_name"]}"',
             'substation':'Fictitious', 'region':'Oregon', 'subregion':'Portland', 'skip_gld': False,
             'glmvsrc': 2400, 'bases':[208, 480, 2400, 4160], 'export_options':' -l=1.0 -p=1.0 -e=carson',
             'check_branches':[{'dss_link': 'Transformer.T633-634', 'dss_bus': 'N633'},
                               {'dss_link': 'Line.OL632-6321', 'dss_bus': 'N632'},
                               {'gld_link': 'xf_t633-634', 'gld_bus': 'n633'}]},
                    ]

    def export_dss_test_file(self):
        cim_test = open(f'{self.setting_file_name}', 'w')
        for row in self.cases:
            dssname = row['dssname']
            root = row['root']
            mRID = row['mRID']
            sub = row['substation']
            subrgn = row['subregion']
            rgn = row['region']
            print (f'redirect {dssname}.dss', file=cim_test)
            print (f'//uuids {root.lower()}_uuids.dat', file=cim_test)
            print (f'export cim100 fid={mRID} substation={sub} subgeo={subrgn} geo={rgn} file={root}.xml', file=cim_test)
            print (f'export uuids {root}_uuids.dat', file=cim_test)
            print (f'export summary   {root}_s.csv', file=cim_test)
            print (f'export voltages  {root}_v.csv', file=cim_test)
            print (f'export currents  {root}_i.csv', file=cim_test)
            print (f'export taps      {root}_t.csv', file=cim_test)
            print (f'export nodeorder {root}_n.csv', file=cim_test)
            
        cim_test.close ()

    def run_opendss_file(self):
        p1 = subprocess.Popen(f'dss {self.setting_file_name}', shell=True)
        p1.wait()


class gld_configuration_file():

    def __init__(self):

        self.feeder = upload_feeder_blazegraph()

        os.chdir(f"{self.feeder.current_dir}/glm/")

        # self.upload_feeder = upload_feeder_blazegraph()

        self.setting_file_name = 'master_run.glm'

    def GirdLABD_Settings(self):
        '''
        The settings below are set constant for many reasons. For example, GridAPPS-D currently
        only runs NR method. The same applies for the other settings. Most of these constraints
        are set by GridAPPS-D
        '''
        self.glm_run = open('master_run.glm', 'w')
        
        print("clock {\n\ttimezone EST+5EDT;\n\tstarttime '2000-01-01 0:00:00';\n\tstoptime '2000-01-01 0:00:00';\n};", file=self.glm_run)
        print('#set relax_naming_rules=1\n#set profiler=1', file=self.glm_run)
        print("module powerflow {\n\tsolver_method NR;\n\tline_capacitance TRUE;\n};", file=self.glm_run)
        print("module climate;\nmodule generators;\nmodule tape;\nmodule reliability {\n\treport_event_log false;\n};", file=self.glm_run)
        print("object climate {\n\tname climate;\n\tlatitude 45.0;\n\tsolar_direct 93.4458;\n}", file=self.glm_run)
        print('#define VSOURCE=2400\n#include "master_base.glm";\n#ifdef WANT_VI_DUMP\n', file=self.glm_run)
        print("object voltdump {\n\tfilename Master_volt.csv;\n\tmode POLAR;\n};", file=self.glm_run)
        print("object currdump {\n\tfilename Master_curr.csv;\n\tmode POLAR;\n};", file=self.glm_run)
        print("#endif", file=self.glm_run)

        self.glm_run.close()
    
    def run_glm_file(self):
        p1 = subprocess.Popen(f'gridlabd {self.glm_run}', shell=True)
        p1.wait()
    
# class simulation_configuration_file ():

#     def __init__(self):
        
        

#         # ME Simulation Configuration parameters:
#         self.simulation_duration = "21600"

#         # Set paths:
#         self.me_dir = '/home/deras/Desktop/midrar_work_github/cimhub_psu_feeder/midrar_me/'

    
#     def set_me_simulation_config_file (self):
#         self.sim_config = {
#             "power_system_config": {
#             "GeographicalRegion_name":self.mrids['geo_rgn'],
#             "SubGeographicalRegion_name":self.mrids['sub_rgn'],
#             "Line_name":self.mrids['line_name']
#             },
#             "application_config": {
#             "applications": []
#             },
#             "simulation_config": {
#             "start_time": "1672531200",
#             "duration": self.simulation_duration,
#             "simulator": "GridLAB-D",
#             "timestep_frequency": "1000",
#             "timestep_increment": "1000",
#             "run_realtime": "true",
#             "simulation_name": self.mrids['simulation_name'],
#             "power_flow_solver_method": "NR",
#             "model_creation_config": {
#                 "load_scaling_factor": "1",
#                 "schedule_name": "ieeezipload",
#                 "z_fraction": "0",
#                 "i_fraction": "1",
#                 "p_fraction": "0",
#                 "randomize_zipload_fractions": "false",
#                 "use_houses": "false"
#             }
#         },
#     }
        
#     def write_files_to_directory (self):

#         os.chdir(f'{self.me_dir}/Configuration/')

#         with open ('simulation_configuration.json', 'w') as output:
#             json.dump(self.sim_config, output, indent=4)
            
if __name__ == '__main__':
    feeder = upload_feeder_blazegraph()
    feeder.upload_model_to_blazegraph()

    dss = dss_configuration_file()

    dss.connect_to_gridappsd()
    dss.set_query()
    dss.get_query_response()
    dss.get_mrids()
    dss.OpenDSS_Settings()
    dss.export_dss_test_file()
    dss.run_opendss_file()

    gld = gld_configuration_file()

    gld.GirdLABD_Settings()
    gld.run_glm_file()
    
    # parser = argparse.ArgumentParser(description="whatever")
    # parser.add_argument('--u','--upload_model',type=str, help="Only Upload model and print its mRID")
    # arg = parser.parse_args()
    
    # if arg.upload_model:
    #     feeder = upload_feeder_blazegraph()
    #     feeder.upload_model_to_blazegraph()