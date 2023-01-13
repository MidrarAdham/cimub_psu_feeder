import pandas as pd
import os
import subprocess
import time
import cimhub.CIMHubConfig as CIMHubConfig
import cimhub.api as cimhub


# Empty blazegraph repository.
os.system('curl -D- -X POST $DB_URL --data-urlencode "update=drop all"')

# Export Uuids version from the DSS file
dss_name = 'Master'

exp_dat_files = open('exp_dss_data.dss', 'w')

print(f'redirect {dss_name}.dss', file=exp_dat_files)
print(f'solve', file=exp_dat_files)
print(f'export uuids {dss_name}.dat', file=exp_dat_files)
print(f'export cim100 substation=Fictitious geo=Texas subgeo=Austin file={dss_name}.xml', file=exp_dat_files)

exp_dat_files.close()

with open('master.dat', 'r') as f:
    for lines in f:
        if lines.startswith('Circuit'):
            fd_mird = (lines.split()[1]).strip('{\}')
        
print(f"================ FYI ==================\n here is the feeder id\n{fd_mird}\n\n")
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
os.system(f'java -cp "./target/libs/*:./target/cimhub-0.0.1-SNAPSHOT.jar" gov.pnnl.gridappsd.cimhub.CIMImporter -s={fd_mird} -u=$DB_URL -o=both -l=1.0 -i=1 -h=0 -x=0 -t=1 master')

# test dss solution 
test_dss = open('test_dss.dss', 'w')
print(f'redirect Master_base.dss', file=test_dss)
print(f'set maxiterations=20', file=test_dss)
print(f'solve', file=test_dss)
print(f'export summary sum_master.csv', file=test_dss)

time.sleep(1)

p1 = subprocess.Popen('dss test_dss.dss', shell=True)
p1.wait()