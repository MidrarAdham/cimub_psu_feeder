import os
import ast
import time
import json
import subprocess
import pandas as pd
import cimhub.api as cimhub
from pathlib import Path as path
from gridappsd import topics as t
import xml.etree.ElementTree as et
from datetime import datetime as dt
import cimhub.CIMHubConfig as CIMHubConfig
from gridappsd.simulation import Simulation
from gridappsd import GridAPPSD, DifferenceBuilder

# Empty blazegraph repository.
os.system('curl -D- -X POST $DB_URL --data-urlencode "update=drop all"')

# Export Uuids version from the DSS file
dss_name = 'Master'

# Directory path:
current_dir = path().absolute()

#Create folders if they don't exist
path('dss').mkdir(parents=False, exist_ok=True)
path('glm').mkdir(parents=False, exist_ok=True)
path('config').mkdir(parents=False, exist_ok=True)


def dss_config_files(dss_name):

    exp_dat_files = open('exp_dss_data.dss', 'w')
    print(f'redirect {dss_name}.dss', file=exp_dat_files)
    print(f'solve', file=exp_dat_files)
    print(f'export uuids {dss_name}.json', file=exp_dat_files)
    print(f'export cim100 substation=Fictitious geo=Texas subgeo=Austin file={dss_name}.xml', file=exp_dat_files)

    exp_dat_files.close()

    # Run the dss file to export the dat file
    p1 = subprocess.Popen('dss exp_dss_data.dss', shell=True)
    p1.wait()


def get_mrids (dss_name):
    mytree = et.parse(dss_name+'.xml')
    root = mytree.getroot()
    mrids = []

    for child in root:
        feeder = (child.tag).split("}")[1]
        if (feeder == "GeographicalRegion") or (feeder == 'SubGeographicalRegion') or (feeder == 'Feeder'):
            for element in child.attrib:
                mrids.append(child.attrib[element])
    
    geo_rgn = mrids[0]
    sub_geo = mrids[1]
    fd_mrid = mrids[2]    
    
    return geo_rgn, sub_geo, fd_mrid

def upload_to_blazegraph(dss_name,mrids):
    
    # upload XML version to Blazegraph
    print("\n\n===============uploading xml===============\n\n")
    os.system(f'curl -D- -H "Content-Type: application/xml" --upload-file {dss_name}.xml -X POST $DB_URL')

    # list feeders in the blazegraph
    print("\n\n===============listing feeders===============\n\n")
    os.system('java -cp "./target/libs/*:./target/cimhub-0.0.1-SNAPSHOT.jar" gov.pnnl.gridappsd.cimhub.CIMImporter -u=$DB_URL -o=idx test')

    # Create dss and glm files:
    print("\n\n===============creating dss and glms===============\n\n")
    os.system(f'java -cp "./target/libs/*:./target/cimhub-0.0.1-SNAPSHOT.jar" gov.pnnl.gridappsd.cimhub.CIMImporter -s={mrids[2]} -u=$DB_URL -o=both -l=1.0 -i=1 -h=0 -x=0 -t=1 master')


def test_exported_files(current_dir):
    # Change to dss directory
    os.chdir(f"{current_dir}/dss/")

    # test dss solution 
    test_dss = open('test_dss.dss', 'w')
    print(f'redirect Master_base.dss', file=test_dss)
    print(f'set maxiterations=20', file=test_dss)
    print(f'solve', file=test_dss)
    print(f'export summary sum_master.csv', file=test_dss)
    
    time.sleep(1)
    p1 = subprocess.Popen('dss test_dss.dss', shell=True)
    p1.wait()

    # Change to glm direcoty
    os.chdir(f'{current_dir}/glm/')

    glm_run = open('master_run.glm', 'w')
    print('clock {\n\ttimezone EST+5EDT;\n\tstarttime 2000-01-01 0:00:00;\n\tstoptime 2000-01-01 0:00:00;\n};', file=glm_run)
    print('#set relax_naming_rules=1\n#set profiler=1', file=glm_run)
    print("module powerflow {\n\tsolver_method NR;\n\tline_capacitance TRUE;\n};", file=glm_run)
    print("module climate;\nmodule generators;\nmodule tape;\nmodule reliability {\n\treport_event_log false;\n};", file=glm_run)
    print("object climate {\n\tname climate;\n\tlatitude 45.0;\n\tsolar_direct 93.4458;\n}", file=glm_run)
    print('#define VSOURCE=2400\n#include "Master_base.glm";\n#ifdef WANT_VI_DUMP\n', file=glm_run)
    print("object voltdump {\n\tfilename Master_volt.csv;\n\tmode POLAR;\n};", file=glm_run)
    print("object currdump {\n\tfilename Master_curr.csv;\n\tmode POLAR;\n};", file=glm_run)
    print("#endif", file=glm_run)

    p1 = subprocess.Popen('gridlabd master_run.glm', shell=True)
    p1.wait()


def list_insert_meas(mrids,current_dir):

    os.chdir(f"{current_dir}/meas/")
    run_meas = open ('run_meas.sh','w')
    print('bash ./list_measurements.sh', file=run_meas)
    print('bash ./insert_measurements.sh', file=run_meas)
    run_meas.close()

    list_meas =  open('list_measurements.sh','w')
    print(f'python3 ListMeasureables.py psu_13_node_feeder_7 {mrids[2]}', file=list_meas)
    list_meas.close()

    insert_meas =  open('insert_measurements.sh','w')
    print('python3 InsertMeasurements.py psu_13_node_feeder_7_lines_pq.txt psu_13_node_feeder.json', file=insert_meas)
    print('python3 InsertMeasurements.py psu_13_node_feeder_7_loads.txt psu_13_node_feeder.json', file=insert_meas)
    print('python3 InsertMeasurements.py psu_13_node_feeder_7_node_v.txt psu_13_node_feeder.json', file=insert_meas)
    print('python3 InsertMeasurements.py psu_13_node_feeder_7_special.txt psu_13_node_feeder.json', file=insert_meas)
    print('python3 InsertMeasurements.py psu_13_node_feeder_7_switch_i.txt psu_13_node_feeder.json', file=insert_meas)
    print('python3 InsertMeasurements.py psu_13_node_feeder_7_xfmr_pq.txt psu_13_node_feeder.json', file=insert_meas)
    insert_meas.close()

    # If running this script for the first time, uncomment the following three lines.

    os.chmod("run_meas.sh",0o775)
    os.chmod("list_measurements.sh",0o775)
    os.chmod("insert_measurements.sh",0o775)

    # p1 = subprocess.Popen('bash ./run_meas.sh', shell=True)
    # p1.wait()

# Create a configuration file to be used when running the simulation
def sim_config_file (mrids, current_dir):

    ckt_name = 'psu_13_node_feeder_7'   # Type your ckt name. It can be found in the dat file.

    with open (f'{current_dir}/master.dat','r') as f:
        for lines in f:
            if (lines.split()[0]).startswith('Circuit.'+ckt_name):
                line_name = (lines.split()[1]).strip('{ }')
    
    sim_config = {
    "power_system_config": {
        "GeographicalRegion_name": mrids[0],
        "SubGeographicalRegion_name": mrids[1],
        "Line_name":line_name
    },
    "application_config": {
        "applications": []
    },
    "simulation_config": {
        "start_time": "1570041113",
        "duration": "30",
        "simulator": "GridLAB-D",
        "timestep_frequency": "1000",
        "timestep_increment": "1000",
        "run_realtime": "true",
        "simulation_name": "psu_13_node_feeder_7",
        "power_flow_solver_method": "NR",
        "model_creation_config": {
            "load_scaling_factor": "1",
            "schedule_name": "ieeezipload",
            "z_fraction": "0",
            "i_fraction": "1",
            "p_fraction": "0",
            "randomize_zipload_fractions": "false",
            "use_houses": "false" 
            }
        },
    }

    os.chdir(f'{current_dir}/config/')
    print(f'-------------------------\n\n\n{os.getcwd}\n\n\n-------------------------')
    with open ('simulation_configuration.json', 'w') as output:
        json.dump(sim_config, output, indent=4)

def connect_gridappsd ():
    os.environ['GRIDAPPSD_USER'] = 'tutorial_user'
    os.environ['GRIDAPPSD_PASSWORD'] = '12345!'
    os.environ['GRIDAPPSD_ADDRESS'] = 'localhost'
    os.environ['GRIDAPPSD_PORT'] = '61613'
    
    # Connect to GridAPPS-D Platform
    
    gapps_session = GridAPPSD()
    assert gapps_session.connected
    return gapps_session

# Load the configuration file created above.
def load_config_from_file (current_dir):
    
    config_file = f'{current_dir}/config/simulation_configuration.json'
    
    with open (config_file) as f:
        config_string = f.read()
        config_parameters = ast.literal_eval (config_string)
        sim_start_time = config_parameters["power_system_config"]["Line_name"]
    
    return config_parameters, sim_start_time

def connect_to_sim (gapps_session, config_parameters):
    sim_session = Simulation (gapps_session, config_parameters)
    sim_mrid = sim_session.simulation_id                          # returns none

    

def main (dss_name, current_dir):
    dss_config_files(dss_name)
    mrids = get_mrids (dss_name)
    upload_to_blazegraph(dss_name,mrids)
    test_exported_files(current_dir)
    list_insert_meas(mrids, current_dir)
    sim_config_file(mrids, current_dir)
    # Starting the simulation process:
    gapps_session = connect_gridappsd()
    config_parameters, sim_start_time = load_config_from_file(current_dir)
    connect_to_sim(gapps_session, config_parameters)


main (dss_name, current_dir)