import os
import csv
import time
import json
import shutil
import xmltodict
import subprocess
import pandas as pd
import cimhub.api as cimhub
from pprint import pprint as pp
from pathlib import Path as path
from gridappsd import topics as t
import xml.etree.ElementTree as et
from datetime import datetime as dt
import cimhub.CIMHubConfig as CIMHubConfig
from gridappsd.simulation import Simulation
from gridappsd import GridAPPSD, DifferenceBuilder

current_dir = path().absolute()
me_dir = '/home/deras/Desktop/midrar_work_github/cimhub_psu_feeder/midrar_me/DERScripts/'

def connect_to_GridAPPSD():
    os.environ['GRIDAPPSD_USER'] = 'tutorial_user'
    os.environ['GRIDAPPSD_PASSWORD'] = '12345!'
    os.environ['GRIDAPPSD_ADDRESS'] = 'localhost'
    os.environ['GRIDAPPSD_PORT'] = '61613'

    # Connect to GridAPPS-D Platform
    gapps_session = GridAPPSD()
    return gapps_session

def query(gapps_session, message):
    topic = t.REQUEST_POWERGRID_DATA
    return gapps_session.get_response(topic, message)

def request_types():
    # The following requestType and objectType are related to ONLY mRIDs for a specific set of feeders or set of equipment.
    # The message will need to be modified. Look at this link https://gridappsd-training.readthedocs.io/en/develop/api_usage/3.3-Using-the-PowerGrid-Models-API.html#CIM-Objects-Supported-by-PowerGrid-Models-API
    # Query the list of all model name mRIDs (Not really useful since only the psu model is in there!)
    modelNames = {
    "requestType": "QUERY_MODEL_NAMES",
    "resultFormat": "JSON"
    }
    
    # The following message returns the objectType mRIDs.
    objectType_mRIDs = {
    "requestType": "QUERY_OBJECT_IDS",
    "modelId": "_597ADC83-1B79-4560-83DB-DFBED03732D8",
    "objectType": "EnergyConsumer",
    "resultFormat": "JSON"
    }

    # Returns all specifics of a feeder or a SET of equipments
    objectInfo = {
    "requestType": "QUERY_OBJECT_DICT",
    "modelId": "_2D6CB195-3471-4F21-8609-09AD4865B205",
    "objectType": "EnergyConsumer",
    "resultFormat": "JSON"
    }
    # Returns the types of CIM classes. It is important to create the EGoT13_der_psu.txt
    CIMClassesTypes = {
    "requestType": "QUERY_OBJECT_TYPES",
    "resultFormat": "JSON"
    }

    # The following returns a specific object (objectID) attributes
    CIMObjectAttr = {
    "requestType": "QUERY_OBJECT",
    "resultFormat": "JSON",
    "modelId": "_597ADC83-1B79-4560-83DB-DFBED03732D8",
    "objectId": "_01300AA7-29D6-4DD6-B729-58AEDC1EA92F"
    }

    return objectInfo

def wr_csv(objType, objName, objmRID, me_dir):
    d = {'der_type':objType, 'der_name':objName, 'mRID':objmRID}
    df = pd.DataFrame(d)
    df.to_csv(f"{me_dir}EGoT13_orig_der_psu.txt",header=False, index=False)
    # with open('EGoT13_orig_der_psu.txt','w', newline='') as f:
    #     writer = csv.writer(f)
    #     writer.writerow(rows)


def config_file_to_remove_existing_ders(me_dir, object_info):
    objmRID = []
    objType = []
    objName = []
    for i in range(len(object_info['data'])):
        objmRID.append(object_info['data'][i]['IdentifiedObject.mRID'])
        objName.append(object_info['data'][i]['IdentifiedObject.name'])
        objType.append(object_info['data'][i]['type'])
    
    wr_csv(objType, objName, objmRID, me_dir)
    
def main(me_dir):
    gapps_session = connect_to_GridAPPSD()
    message = request_types()
    # Need one of the above queries? Return its variable in request_types func and uncomment the following line.
    resp = query(gapps_session, message)
    config_file_to_remove_existing_ders(me_dir, resp)

    
main(me_dir)