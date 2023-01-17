import pandas as pd
import os
import subprocess
import time
import cimhub.CIMHubConfig as CIMHubConfig
import cimhub.api as cimhub
import xml.etree.ElementTree as et


# Empty blazegraph repository.
os.system('curl -D- -X POST $DB_URL --data-urlencode "update=drop all"')

# Export Uuids version from the DSS file
dss_name = 'Master'

exp_dat_files = open('exp_dss_data.dss', 'w')

print(f'redirect {dss_name}.dss', file=exp_dat_files)
print(f'solve', file=exp_dat_files)
print(f'export uuids {dss_name}.json', file=exp_dat_files)
print(f'export cim100 substation=Fictitious geo=Texas subgeo=Austin file={dss_name}.xml', file=exp_dat_files)

exp_dat_files.close()

mytree = et.parse('Master.xml')
mroot = mytree.getroot()

for child in mroot:
    feeder = {child.tag.split('}')[1]}
    for i in feeder:
        if i == 'Feeder':
            fd_mrid = child.attrib
        
print(f"================ FYI ==================\n here is the feeder id\n{fd_mrid}\n\n")
# Run the dss file to export the dat file
p1 = subprocess.Popen('dss exp_dss_data.dss', shell=True)
p1.wait()

# upload XML version to Blazegraph
print("\n\n===============uploading xml===============\n\n")
os.system(f'curl -D- -H "Content-Type: application/xml" --upload-file {dss_name}.xml -X POST $DB_URL')

# list feeders in the blazegraph
print("\n\n===============listing feeders===============\n\n")
os.system('java -cp "./target/libs/*:./target/cimhub-0.0.1-SNAPSHOT.jar" gov.pnnl.gridappsd.cimhub.CIMImporter -u=$DB_URL -o=idx test')

# Create dss and glm files:
print("\n\n===============creating dss and glms===============\n\n")
os.system(f'java -cp "./target/libs/*:./target/cimhub-0.0.1-SNAPSHOT.jar" gov.pnnl.gridappsd.cimhub.CIMImporter -s={fd_mrid} -u=$DB_URL -o=both -l=1.0 -i=1 -h=0 -x=0 -t=1 master')

# test dss solution 
test_dss = open('test_dss.dss', 'w')
print(f'redirect Master_base.dss', file=test_dss)
print(f'set maxiterations=20', file=test_dss)
print(f'solve', file=test_dss)
print(f'export summary sum_master.csv', file=test_dss)

time.sleep(1)

p1 = subprocess.Popen('dss test_dss.dss', shell=True)
p1.wait()

os.chdir('meas/')

run_meas = open ('run_meas.sh','w')
print('bash ./list_measurements.sh', file=run_meas)
print('bash ./insert_measurements.sh', file=run_meas)
run_meas.close()

list_meas =  open('list_measurements.sh','w')
print(f'python3 ListMeasureables.py psu_13_node_feeder_7 _{fd_mrid}', file=list_meas)
list_meas.close()

insert_meas =  open('insert_measurements.sh','w')
print('python3 InsertMeasurements.py psu_13_node_feeder_7_lines_pq.txt', file=insert_meas)
print('python3 InsertMeasurements.py psu_13_node_feeder_7_loads.txt', file=insert_meas)
print('python3 InsertMeasurements.py psu_13_node_feeder_7_node_v.txt', file=insert_meas)
print('python3 InsertMeasurements.py psu_13_node_feeder_7_special.txt', file=insert_meas)
print('python3 InsertMeasurements.py psu_13_node_feeder_7_switch_i.txt', file=insert_meas)
print('python3 InsertMeasurements.py psu_13_node_feeder_7_xfmr_pq.txt', file=insert_meas)
insert_meas.close()

# If running this script for the first time, uncomment the following three lines.

os.chmod("run_meas.sh",0o775)
os.chmod("list_measurements.sh",0o775)
os.chmod("insert_measurements.sh",0o775)

# os.system('bash ./run_meas.sh')