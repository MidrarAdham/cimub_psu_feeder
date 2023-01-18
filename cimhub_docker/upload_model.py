import os
import time
import json
import subprocess
import pandas as pd
import cimhub.api as cimhub
from pathlib import Path as path
import xml.etree.ElementTree as et
from datetime import datetime as dt
import cimhub.CIMHubConfig as CIMHubConfig

# Empty blazegraph repository.
os.system('curl -D- -X POST $DB_URL --data-urlencode "update=drop all"')

# Export Uuids version from the DSS file
dss_name = 'Master'

# Directory path:
current_dir = path().absolute()

#Create folders if they don't exist
path('dss').mkdir(parents=False, exist_ok=True)
path('glm').mkdir(parents=False, exist_ok=True)


def dss_config_files(dss_name, exp_dat_files):
    exp_dat_files = open('exp_dss_data.dss', 'w')

    print(f'redirect {dss_name}.dss', file=exp_dat_files)
    print(f'solve', file=exp_dat_files)
    print(f'export uuids {dss_name}.json', file=exp_dat_files)
    print(f'export cim100 substation=Fictitious geo=Texas subgeo=Austin file={dss_name}.xml', file=exp_dat_files)

    exp_dat_files.close()

    # Run the dss file to export the dat file
    p1 = subprocess.Popen('dss exp_dss_data.dss', shell=True)
    p1.wait()


def get_mrids ():
    mytree = et.parse('Master.xml')
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
    print("\n\n===============uploading xml===============\n\n")
    os.system(f'curl -D- -H "Content-Type: application/xml" --upload-file {dss_name}.xml -X POST $DB_URL')

    # list feeders in the blazegraph
    print("\n\n===============listing feeders===============\n\n")
    os.system('java -cp "./target/libs/*:./target/cimhub-0.0.1-SNAPSHOT.jar" gov.pnnl.gridappsd.cimhub.CIMImporter -u=$DB_URL -o=idx test')

    # Create dss and glm files:
    print("\n\n===============creating dss and glms===============\n\n")
    os.system(f'java -cp "./target/libs/*:./target/cimhub-0.0.1-SNAPSHOT.jar" gov.pnnl.gridappsd.cimhub.CIMImporter -s={fd_mrid} -u=$DB_URL -o=both -l=1.0 -i=1 -h=0 -x=0 -t=1 master')


def test_exported_files():
    # Change to dss directory
    os.chdir("./dss/")

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
    os.chdir('../glm/')

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


def list_insert_meas(fd_mrid):
    os.chdir('../meas/')

    run_meas = open ('run_meas.sh','w')
    print('bash ./list_measurements.sh', file=run_meas)
    print('bash ./insert_measurements.sh', file=run_meas)
    run_meas.close()

    list_meas =  open('list_measurements.sh','w')
    print(f'python3 ListMeasureables.py psu_13_node_feeder_7 {fd_mrid}', file=list_meas)
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

    p1 = subprocess.Popen('bash ./run_meas.sh', shell=True)
    p1.wait()

