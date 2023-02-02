import os
import ast
import csv
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
me_dir = '/home/deras/Desktop/midrar_work_github/cimhub_psu_feeder/midrar_me/'

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

    print("-------------------------------------------------")
    print("\n\n----> Exporting UUIDs and CIM files <----\n\n")
    print("-------------------------------------------------")

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

def upload_to_blazegraph(dss_name,fd_mrid):
    
    # upload XML version to Blazegraph
    print("-------------------------------------------------")
    print(f"\n\n----> uploading xml <----\n\n")
    print("-------------------------------------------------")
    os.system(f'curl -D- -H "Content-Type: application/xml" --upload-file {dss_name}.xml -X POST $DB_URL')

    # list feeders in the blazegraph
    print("-------------------------------------------------")
    print(f"\n\n----> listing feeders <----\n\n")
    print("-------------------------------------------------")
    os.system('java -cp "./target/libs/*:./target/cimhub-0.0.1-SNAPSHOT.jar" gov.pnnl.gridappsd.cimhub.CIMImporter -u=$DB_URL -o=idx test')

    # Create dss and glm files:
    print("-------------------------------------------------")
    print(f"\n\n----> creating dss and glms <----\n\n")
    print("-------------------------------------------------")
    os.system(f'java -cp "./target/libs/*:./target/cimhub-0.0.1-SNAPSHOT.jar" gov.pnnl.gridappsd.cimhub.CIMImporter -s={fd_mrid} -u=$DB_URL -o=both -l=1.0 -i=1 -h=0 -x=0 -t=1 master')

def query_feeder (fd_mrid):   
    
    loads_query = f'''
    
    # loads (need to account for 2+ unequal EnergyConsumerPhases per EnergyConsumer) - DistLoad
    PREFIX r:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX c:  <http://iec.ch/TC57/CIM100#>
    SELECT ?name ?bus ?basev ?p ?q ?pz ?qz ?pi ?qi ?pp ?qp ?pe ?qe ?fdrid ?t1id (group_concat(distinct ?phs) as ?phases) WHERE {{
    ?s r:type c:EnergyConsumer.
    ?s c:IdentifiedObject.name ?name.
    # feeder selection options - if all commented out, query matches all feeders
    VALUES ?fdrid {{"{fd_mrid}"}}
    ?s c:Equipment.EquipmentContainer ?fdr.
    ?fdr c:IdentifiedObject.mRID ?fdrid.
    ?s c:IdentifiedObject.name ?name.
    ?s c:ConductingEquipment.BaseVoltage ?bv.
    ?bv c:BaseVoltage.nominalVoltage ?basev.
    ?s c:EnergyConsumer.p ?p.
    ?s c:EnergyConsumer.q ?q.
    ?s c:EnergyConsumer.LoadResponse ?lr.
    ?lr c:LoadResponseCharacteristic.pConstantImpedance ?pz.
    ?lr c:LoadResponseCharacteristic.qConstantImpedance ?qz.
    ?lr c:LoadResponseCharacteristic.pConstantCurrent ?pi.
    ?lr c:LoadResponseCharacteristic.qConstantCurrent ?qi.
    ?lr c:LoadResponseCharacteristic.pConstantPower ?pp.
    ?lr c:LoadResponseCharacteristic.qConstantPower ?qp.
    OPTIONAL {{?lr c:LoadResponseCharacteristic.pVoltageExponent ?pe.}}
    OPTIONAL {{?lr c:LoadResponseCharacteristic.qVoltageExponent ?qe.}}
    OPTIONAL {{?ecp c:EnergyConsumerPhase.EnergyConsumer ?s.
    ?ecp c:EnergyConsumerPhase.phase ?phsraw.
        bind(strafter(str(?phsraw),"SinglePhaseKind.") as ?phs) }}
    ?t c:Terminal.ConductingEquipment ?s.
    ?t c:Terminal.ConnectivityNode ?cn. 
    ?t c:IdentifiedObject.mRID ?t1id. 
    ?cn c:IdentifiedObject.name ?bus
    }}
    GROUP BY ?name ?bus ?basev ?p ?q ?cnt ?conn ?pz ?qz ?pi ?qi ?pp ?qp ?pe ?qe ?fdrid ?t1id
    ORDER by ?name
    '''

    return loads_query

def create_config_file(geo_rgn, sub_geo, fd_mrid, me_dir):
    df = pd.read_csv(me_dir+'DERSHistoricalDataInput/psu_13_feeder_ders_s.csv')
    starting_time = df.loc[0]['Time']
    sim_config = {
        "power_system_config": {
            "GeographicalRegion_name": geo_rgn,
            "SubGeographicalRegion_name": sub_geo,
            "Line_name":fd_mrid
        },
        "application_config": {
            "applications": []
        },
        "simulation_config": {
            "start_time": str(starting_time),
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
    return sim_config

def connect_gridappsd ():                           #Not called in main
    os.environ['GRIDAPPSD_USER'] = 'tutorial_user'
    os.environ['GRIDAPPSD_PASSWORD'] = '12345!'
    os.environ['GRIDAPPSD_ADDRESS'] = 'localhost'
    os.environ['GRIDAPPSD_PORT'] = '61613'

    gapps_session = GridAPPSD()
    assert gapps_session.connected
    return gapps_session

def create_mrid_files(config_parameters, loads_query):
    feeder_id = []
    names = []
    busses = []
    phases = []
    load_type = []
    rated_kva = []
    rated_kv = []
    kw = []
    kvar = []
    rated_kwh = []
    stored_kwh = []
    dfs = []
    
    gapps_session = connect_gridappsd()

    sim_session = Simulation(gapps_session,config_parameters)
    topic = t.REQUEST_POWERGRID_DATA
    print("-------------------------------------------------")
    print("----> Querying Loads Information <----")
    print("-------------------------------------------------")
    
    resp = gapps_session.query_data(loads_query)

    feeder_id.append(resp['data']['results']['bindings'][0]['fdrid']['value'])
    for i in range(len(resp['data']['results']['bindings'])):
        phases.append(resp['data']['results']['bindings'][i]['phases']['value'].replace(' ',''))
        names.append(resp['data']['results']['bindings'][i]['name']['value'])
        busses.append(resp['data']['results']['bindings'][i]['bus']['value'])
        load_type.append('Battery')
        rated_kva.append('1')
        rated_kv.append('0.12')
        kw.append('1')
        kvar.append('0')
        rated_kwh.append('0')
        stored_kwh.append('0')
    
    df_files = pd.DataFrame({'uuid_file':"feederID" ,'EGoT13_der_psu_uuid.txt':feeder_id})
    df_data = pd.DataFrame({'//name':names,'bus':busses,'phases(ABCs1s2)':phases,'type(Battery,Photovoltaic)':load_type, 'RatedkVA': rated_kva,'RatedkV':rated_kv,'kW':kw,'kVAR':kvar,'RatedkWH': rated_kwh,'StoredkWH': stored_kwh})

    return df_files, df_data

def wr_df(df_files, df_data):
    
    df_files.to_csv("/home/deras/Desktop/midrar_work_github/cimhub_psu_feeder/midrar_me/DERScripts/EGoT13_der_psu.txt", mode="w", index=False)
    df_data.to_csv("/home/deras/Desktop/midrar_work_github/cimhub_psu_feeder/midrar_me/DERScripts/EGoT13_der_psu.txt", mode="a", index=False, quoting=csv.QUOTE_NONE, escapechar=" ")

def wr_json(sim_config, me_dir):
    os.chdir(f'{me_dir}/Configuration/')
    with open ('simulation_configuration.json', 'w') as output:
        json.dump(sim_config, output, indent=4)

def test_exported_files(current_dir):

    os.chdir(f"{current_dir}/dss/")

    # test dss solution 
    test_dss = open('test_dss.dss', 'w')
    print(f'redirect Master_base.dss', file=test_dss)
    print(f'set maxiterations=20', file=test_dss)
    print(f'solve', file=test_dss)
    print(f'export summary sum_master.csv', file=test_dss)    
    time.sleep(1)
    print(f"\n\n----> Solving the Exported DSS File\n\n")
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

    print(f"\n\n----> Solving the Exported GLM File <----\n\n")
    p1 = subprocess.Popen('gridlabd master_run.glm', shell=True)
    p1.wait()


def list_insert_meas(fd_mrid,me_dir):

    os.chdir(f"{me_dir}/DERScripts/")
    print("-------------------------------------------------")
    print("----> Changing directory to:\n----> /home/deras/Desktop/midrar_work_github/cimhub_psu_feeder/midrar_me/DERScripts/ <----\n")

    drop_der = open('drop_der.sh','w')
    print(f'python3 $CIMHUB_UTILS/DropDER.py $CIMHUB_UTILS/cimhubconfig.json EGoT13_der_psu.txt', file=drop_der)
    drop_der.close()

    insert_der = open('insert_der.sh','w')
    print(f'python3 $CIMHUB_UTILS/InsertDER.py $CIMHUB_UTILS/cimhubconfig.json EGoT13_der_psu.txt', file=insert_der)
    insert_der.close()
    
    drop_all_measurements = open('drop_all_measurements.sh','w')
    print(f'python3 $CIMHUB_UTILS/DropMeasurements.py $CIMHUB_UTILS/cimhubconfig.json {fd_mrid}', file=drop_all_measurements)
    drop_all_measurements.close()

    list_meas =  open('list_measurements.sh','w')
    print(f'python3 $CIMHUB_UTILS/ListMeasureables.py psu_13_node_feeder_7 {fd_mrid}', file=list_meas)
    list_meas.close()

    insert_meas =  open('insert_measurements.sh','w')
    print('python3 InsertMeasurements.py psu_13_node_feeder_7_lines_pq.txt psu_13_node_feeder.json', file=insert_meas)
    print('python3 InsertMeasurements.py psu_13_node_feeder_7_loads.txt psu_13_node_feeder.json', file=insert_meas)
    print('python3 InsertMeasurements.py psu_13_node_feeder_7_node_v.txt psu_13_node_feeder.json', file=insert_meas)
    print('python3 InsertMeasurements.py psu_13_node_feeder_7_special.txt psu_13_node_feeder.json', file=insert_meas)
    print('python3 InsertMeasurements.py psu_13_node_feeder_7_switch_i.txt psu_13_node_feeder.json', file=insert_meas)
    print('python3 InsertMeasurements.py psu_13_node_feeder_7_xfmr_pq.txt psu_13_node_feeder.json', file=insert_meas)
    insert_meas.close()

    run_meas = open ('run_meas.sh','w')
    print('echo "\n\n---> running drop_der.sh file <----\n\n"', file=run_meas)
    print('bash ./drop_der.sh', file=run_meas)
    print('echo "\n\n----> running insert_der.sh file <----\n\n"', file=run_meas)
    print('bash ./insert_der.sh', file=run_meas)
    print('echo "\n\n----> running drop_all_measurements.sh file <----\n\n"', file=run_meas)
    print('bash ./drop_all_measurements.sh', file=run_meas)
    print('echo "\n\n----> running list_measurements.sh file <----\n\n"', file=run_meas)
    print('bash ./list_measurements.sh', file=run_meas)
    print('echo "\n\n----> running insert_measurements.sh file <----\n\n"', file=run_meas)
    print('bash ./insert_measurements.sh', file=run_meas)
    run_meas.close()

    # If running this script for the first time, uncomment the following three lines.
    
    os.chmod("run_meas.sh",0o775)
    os.chmod("drop_der.sh",0o775)
    os.chmod("drop_all_measurements.sh",0o775)
    os.chmod("insert_der.sh",0o775)
    os.chmod("list_measurements.sh",0o775)
    os.chmod("insert_measurements.sh",0o775)
    time.sleep(5)
    print(f'\n\n----> Running Measurements Scripts <----\n\n')
    p1 = subprocess.Popen('./run_meas.sh', shell=True)
    p1.wait()

def main (dss_name, current_dir, me_dir):
    dss_config_files(dss_name)
    geo_rgn, sub_rgn, fd_mrid = get_mrids (dss_name)
    print("-------------------------------------------------")
    print(f"\n\n----> geo rgn {geo_rgn}\n\n----> sub_rgn {sub_rgn}\n\n----> feeder mRID {fd_mrid}\n\n")
    print("-------------------------------------------------")
    upload_to_blazegraph(dss_name,fd_mrid)
    loads_query = query_feeder(fd_mrid)
    config_parameters = create_config_file(geo_rgn, sub_rgn, fd_mrid, me_dir)
    df_files, df_data = create_mrid_files(config_parameters, loads_query)
    wr_df(df_files, df_data)
    wr_json(config_parameters, me_dir)
    test_exported_files(current_dir)
    list_insert_meas(fd_mrid, me_dir)
main (dss_name, current_dir, me_dir)