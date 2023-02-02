import os
import ast
import csv
import json
import time
import pprint
import xmltodict
import pandas as pd
from dict2xml import dict2xml
from pprint import pprint as pp
from gridappsd import topics as t
import xml.etree.ElementTree as ET
from gridappsd.simulation import Simulation
from gridappsd import GridAPPSD, DifferenceBuilder

mc_file_directory = r"/home/deras/Desktop/midrar_work_github/cimhub_psu_feeder/midrar_me/"
config_file_path = mc_file_directory + r"Configuration/simulation_configuration.json"
ders_obj_list = {
    'DERSHistoricalDataInput': 'dersHistoricalDataInput',
    'RWHDERS': 'rwhDERS'
    # ,
    # 'EXAMPLEDERClassName': 'exampleDERObjectName'
    }
go_sensor_decision_making_manual_override = True
manual_service_filename = "manually_posted_service_input.xml"
output_log_name = 'Logged Grid State Data/MeasOutputLogs.csv'


with open(config_file_path) as f:
    config_string = f.read()
    config_parameters = ast.literal_eval(config_string)

os.environ['GRIDAPPSD_USER'] = 'tutorial_user'
os.environ['GRIDAPPSD_PASSWORD'] = '12345!'
os.environ['GRIDAPPSD_ADDRESS'] = 'localhost'
os.environ['GRIDAPPSD_PORT'] = '61613'

# Connect to GridAPPS-D Platform
gapps_session = GridAPPSD()
assert gapps_session.connected

def initialize_sim_mrid(self):
    sim_mrid = sim_session.simulation_id

line_mrid = config_parameters["power_system_config"]["Line_name"]
sim_start_time = config_parameters["simulation_config"]["start_time"]

sim_session = Simulation(gapps_session, config_parameters)

print(f"sim_session ---> \n{sim_session}")


def query_powergrid_models(topic, message):
    return gapps_session.get_response(topic, message)


# 
topic = "goss.gridappsd.process.request.config"
# message = {
#     "modelId": line_mrid,
#     "requestType": "QUERY_OBJECT_MEASUREMENTS",
#     "resultFormat": "JSON",
# }
# message = {
#         "requestType": "QUERY_MODEL_NAMES",
#         "resultFormat": "JSON"
# }
message = {
    'configurationType': 'CIM Dictionary',
    'parameters': {'model_id': line_mrid}
}

resp = query_powergrid_models(topic, message)
print(resp)

loads_query = '''
# list all measurements, with buses and equipments - DistMeasurement
PREFIX r: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX c: <http://iec.ch/TC57/CIM100#>
SELECT ?class ?type ?name ?bus ?phases ?eqtype ?eqname ?eqid ?trmid ?id WHERE {
 ?eq c:Equipment.EquipmentContainer ?fdr.
 ?fdr c:IdentifiedObject.mRID ?fdrid. 
{ ?s r:type c:Discrete. bind ("Discrete" as ?class)}
  UNION
{ ?s r:type c:Analog. bind ("Analog" as ?class)}
 ?s c:IdentifiedObject.name ?name .
 ?s c:IdentifiedObject.mRID ?id .
 ?s c:Measurement.PowerSystemResource ?eq .
 ?s c:Measurement.Terminal ?trm .
 ?s c:Measurement.measurementType ?type .
 ?trm c:IdentifiedObject.mRID ?trmid.
 ?eq c:IdentifiedObject.mRID ?eqid.
 ?eq c:IdentifiedObject.name ?eqname.
 ?eq r:type ?typeraw.
  bind(strafter(str(?typeraw),"#") as ?eqtype)
 ?trm c:Terminal.ConnectivityNode ?cn.
 ?cn c:IdentifiedObject.name ?bus.
 ?s c:Measurement.phases ?phsraw .
   {bind(strafter(str(?phsraw),"PhaseCode.") as ?phases)}
} ORDER BY ?class ?type ?name

'''

loads_query = '''
# list all measurements - not depending on valid model
PREFIX r: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX c: <http://iec.ch/TC57/CIM100#>
SELECT ?name ?phases ?type ?eqid ?trmid ?id WHERE {
{ ?s r:type c:Discrete. bind ("Discrete" as ?class)}
  UNION
{ ?s r:type c:Analog. bind ("Analog" as ?class)}
	?s c:IdentifiedObject.name ?name .
	?s c:IdentifiedObject.mRID ?id .
	?s c:Measurement.PowerSystemResource ?eq .
    ?eq c:IdentifiedObject.mRID ?eqid .
	?s c:Measurement.Terminal ?trm .
    ?trm c:IdentifiedObject.mRID ?trmid .
	?s c:Measurement.measurementType ?type .
  {?s c:Measurement.phases ?phsraw.
   bind(strafter(str(?phsraw),"PhaseCode.") as ?phases)}
} ORDER BY ?name ?type ?phases
'''

# resp = gapps_session.query_data(loads_query)
with open ('cim_dict_midrar.json', 'w') as output:
    json.dump(resp, output, indent=4)

# Query Model Info:
# # topic = "goss.gridappsd.process.request.data.powergridmodel"

# # mesaage = {}

# config_api_topic = 'goss.gridappsd.process.request.config'

# message = {
#     'configurationType': 'CIM Feeder Index',
#     'parameters': {'model_id': line_mrid}
# }

# cim_dict = gapps_session.get_response(config_api_topic, message, timeout=20)

# print(cim_dict)

# measdict = cim_dict['data']['feeders'][0]
# # cim_measurement_dict = measdict