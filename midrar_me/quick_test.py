import os
import ast
import csv
import sys
import time
import json
import shutil
import subprocess
import pandas as pd
import cimhub.api as cimhub
from pprint import pprint as pp
from pathlib import Path as path
from gridappsd import topics as t
import xml.etree.ElementTree as et
from datetime import datetime as dt
from SPARQLWrapper import SPARQLWrapper2
import cimhub.CIMHubConfig as CIMHubConfig
from gridappsd.simulation import Simulation
from gridappsd import GridAPPSD, DifferenceBuilder


def connect_gridappsd ():                           #Not called in main
    os.environ['GRIDAPPSD_USER'] = 'tutorial_user'
    os.environ['GRIDAPPSD_PASSWORD'] = '12345!'
    os.environ['GRIDAPPSD_ADDRESS'] = 'localhost'
    os.environ['GRIDAPPSD_PORT'] = '61613'

    gapps_session = GridAPPSD()
    assert gapps_session.connected
    return gapps_session

dss_name = '/home/deras/Desktop/midrar_work_github/cimhub_psu_feeder/cimhub_docker/dss/Master'
me_dir = '/home/deras/Desktop/midrar_work_github/cimhub_psu_feeder/midrar_me/'
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


df = pd.read_csv(me_dir+'DERSHistoricalDataInput/psu_13_feeder_ders_s.csv')
starting_time = df.loc[0]['Time']
config_parameters = {
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

gapps_session = connect_gridappsd()

sim_session = Simulation(gapps_session,config_parameters)
topic = t.REQUEST_POWERGRID_DATA

cimhub_file = './DERScripts/cimhubconfig.json'
CIMHubConfig.ConfigFromJsonFile (cimhub_file)
sparql = SPARQLWrapper2(CIMHubConfig.blazegraph_url)
sparql.method = 'POST'

mRID = '_F5D1950C-1E11-45AC-9EED-2ABB0EB1BE63'
drop_loc_template = """DELETE {{
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:Location.CoordinateSystem ?crs.
}} WHERE {{
 VALUES ?uuid {{\"{res}\"}}
 VALUES ?class {{c:Location}}
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:Location.CoordinateSystem ?crs.
}}
"""

qstr = CIMHubConfig.prefix+drop_loc_template.format(res=mRID)
sparql.setQuery(qstr)
ret = sparql.query()


# print('deleting', ret.response.reason)