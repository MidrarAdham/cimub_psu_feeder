# Copyright (C) 2022 Battelle Memorial Institute
# file: base123.py

import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import subprocess
import stat
import shutil
import os
import sys

if sys.platform == 'win32':
  shfile_export = 'go.bat'
  shfile_glm = './glm/checkglm.bat'
  shfile_run = 'checkglm.bat'
  cfg_json = 'cimhubjar.json'
else:
  shfile_export = './go.sh'
  shfile_glm = './glm/checkglm.sh'
  shfile_run = './checkglm.sh'
  cfg_json = 'cimhubdocker.json'

cwd = os.getcwd()

# make some random UUID values for additional feeders, from 
# "import uuid;idNew=uuid.uuid4();print(str(idNew).upper())"
# CBE09B55-091B-4BB0-95DA-392237B12640
# 

# cases = [
#   {'dssname':'Master', 'root':'Master', 'mRID':'C6A497A3-43DE-4432-A151-91D830CFB65E',
#    'substation':'Fictitious', 'region':'Texas', 'subregion':'Austin', 'skip_gld': True,
#    'glmvsrc': 2401.78, 'bases':[208.0, 480.0, 4160.0], 'export_options':' -l=1.0 -p=1.0 -e=carson',
#    'check_branches':[{'dss_link': 'Transformer.T633-634', 'dss_bus': 'N633'},
#                      {'dss_link': 'Line.OL632-6321', 'dss_bus': 'N632'}]},
# ]


# NOTE: psu feeder with loads. Feeder mRID: F234F944-6C06-4D13-8E87-3532CDB095FA
# Cases for the above feeder:

cases = [
  {'dssname':'Master', 'root':'Master', 'mRID':'67CF8C4B-700E-4019-A03D-7C9E929ECAF9',
   'substation':'Fictitious', 'region':'Texas', 'subregion':'Austin', 'skip_gld': False,
   'glmvsrc': 2400, 'bases':[120, 480, 2400, 4160], 'export_options':' -l=1.0 -p=1.0 -e=carson',
   'check_branches':[{'dss_link': 'Transformer.T633-634', 'dss_bus': 'N633'},
                     {'dss_link': 'Line.OL632-6321', 'dss_bus': 'N632'},
                     {'gld_link': 'xf_t633-634', 'gld_bus': 'n633'}]}, #maybe 630
]

'''
NOTE: psu feeder without loads. Feeder mRID: D2DF52A4-89F5-4515-A6F6-872B6A8FC6C7
Cases for the feeder without loads:
'''

# cases = [
#   {'dssname':'master_optimized', 'root':'master_optimized', 'mRID':'D2DF52A4-89F5-4515-A6F6-872B6A8FC6C7',
#    'substation':'Fictitious', 'region':'Texas', 'subregion':'Austin', 'skip_gld': False,
#    'glmvsrc': 2401.78, 'bases':[120, 480.0, 4160.0], 'export_options':' -l=1.0 -p=1.0 -e=carson',
#    'check_branches':[{'dss_link': 'Transformer.T633-634', 'dss_bus': 'n633'},
#                      {'dss_link': 'Line.S671-692', 'dss_bus': 'N671'},
#                      {'gld_link': 'Transformer.T633-634', 'gld_bus': 'N633'}]}, #maybe 630
# ]
# {'dss_link': 'Transformer.T633-634', 'dss_bus': 'n633', 'gld_link': 'xf_t633-634', 'gld_bus': 'n633'}
# {'dss_link': 'LINE.L115', 'dss_bus': '149', 'gld_link': 'LINE_L115', 'gld_bus': '149'}
CIMHubConfig.ConfigFromJsonFile (cfg_json)
cimhub.clear_db (cfg_json)

fp = open ('cim_test.dss', 'w')
for row in cases:
  dssname = row['dssname']
  root = row['root']
  mRID = row['mRID']
  sub = row['substation']
  subrgn = row['subregion']
  rgn = row['region']
  print ('redirect {:s}.dss'.format (dssname), file=fp)
  print ('//uuids {:s}_uuids.dat'.format (root.lower()), file=fp)
  print ('export cim100 fid={:s} substation={:s} subgeo={:s} geo={:s} file={:s}.xml'.format (mRID, sub, subrgn, rgn, root), file=fp)
  print ('export uuids {:s}_uuids.dat'.format (root), file=fp)
  print ('export summary   {:s}_s.csv'.format (root), file=fp)
  print ('export voltages  {:s}_v.csv'.format (root), file=fp)
  print ('export currents  {:s}_i.csv'.format (root), file=fp)
  print ('export taps      {:s}_t.csv'.format (root), file=fp)
  print ('export nodeorder {:s}_n.csv'.format (root), file=fp)
fp.close ()
p1 = subprocess.Popen ('opendsscmd cim_test.dss', shell=True)
p1.wait()

for row in cases:
  cmd = 'curl -D- -H "Content-Type: application/xml" --upload-file ' + row['root']+ '.xml' + ' -X POST ' + CIMHubConfig.blazegraph_url
  os.system (cmd)
cimhub.list_feeders (cfg_json)

cimhub.make_blazegraph_script (cases, './', 'dss/', 'glm/', shfile_export)
st = os.stat (shfile_export)
os.chmod (shfile_export, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
p1 = subprocess.call (shfile_export, shell=True)

cimhub.make_dssrun_script (casefiles=cases, scriptname='./dss/check.dss', bControls=False)
os.chdir('./dss')
p1 = subprocess.Popen ('opendsscmd check.dss', shell=True)
p1.wait()

os.chdir(cwd)
cimhub.make_glmrun_script (casefiles=cases, inpath='./glm/', outpath='./glm/', scriptname=shfile_glm)
st = os.stat (shfile_glm)
os.chmod (shfile_glm, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
os.chdir('./glm')
p1 = subprocess.call (shfile_run)

os.chdir(cwd)
cimhub.compare_cases (casefiles=cases, basepath='./', dsspath='./dss/', glmpath='./glm/')

