import ast
from pathlib import Path as path
from pprint import pprint as pp
import pandas as pd
import os
from gridappsd.simulation import Simulation
from gridappsd import GridAPPSD, DifferenceBuilder
from gridappsd import topics as t
import xml.etree.ElementTree as et
loads_query = """
  
  # loads (need to account for 2+ unequal EnergyConsumerPhases per EnergyConsumer) - DistLoad
  PREFIX r:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
  PREFIX c:  <http://iec.ch/TC57/CIM100#>
  SELECT ?name ?bus ?basev ?p ?q ?pz ?qz ?pi ?qi ?pp ?qp ?pe ?qe ?fdrid ?t1id (group_concat(distinct ?phs) as ?phases) WHERE {
  ?s r:type c:EnergyConsumer.
  ?s c:IdentifiedObject.name ?name.
  # feeder selection options - if all commented out, query matches all feeders
  VALUES ?fdrid {"_0ACEC26F-C381-4D53-B0B3-92FCACD566B6"}  # R2 12.47 3
  #VALUES ?fdrid {"_49AD8E07-3BF9-A4E2-CB8F-C3722F837B62"}  # R2 12.47 3
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
  OPTIONAL {?lr c:LoadResponseCharacteristic.pVoltageExponent ?pe.}
  OPTIONAL {?lr c:LoadResponseCharacteristic.qVoltageExponent ?qe.}
  OPTIONAL {?ecp c:EnergyConsumerPhase.EnergyConsumer ?s.
  ?ecp c:EnergyConsumerPhase.phase ?phsraw.
    bind(strafter(str(?phsraw),"SinglePhaseKind.") as ?phs) }
  ?t c:Terminal.ConductingEquipment ?s.
  ?t c:Terminal.ConnectivityNode ?cn. 
  ?t c:IdentifiedObject.mRID ?t1id. 
  ?cn c:IdentifiedObject.name ?bus
  }
  GROUP BY ?name ?bus ?basev ?p ?q ?cnt ?conn ?pz ?qz ?pi ?qi ?pp ?qp ?pe ?qe ?fdrid ?t1id
  ORDER by ?name
  """



# current_dir = path().absolute()

# config_file = f'{current_dir}/config/simulation_configuration.json'
# with open (config_file) as f:
#     config_string = f.read()
#     config_parameters = ast.literal_eval (config_string)
#     sim_start_time = config_parameters["power_system_config"]["Line_name"]

# dersHistoricalDataInput = 1
# rwhDERS = 2
# ders_obj_list = {
#     'DERSHistoricalDataInput': 'dersHistoricalDataInput',
#     'RWHDERS': 'rwhDERS'
#     }
# for key, value in ders_obj_list.items():
#     print(f'key: {key} <---> value: {value}')
# ckt_name = 'psu_13_node_feeder_7'
# with open ('/home/deras/Desktop/midrar_work_github/cimhub_psu_feeder/cimhub_docker/master.dat','r') as f:
#     for lines in f:
#         if (lines.split()[0]).startswith('Circuit.'+ckt_name):
#             line_name = (lines.split()[1]).strip('{ }')

# print(line_name)

# df = pd.read_csv('/home/deras/Desktop/midrar_work_github/midrar_me/DERSHistoricalDataInput/psu_13_feeder_ders_s.csv')
# starting_time = df.loc[0]['Time']
# sim_config = {
#     "power_system_config": {
#         "GeographicalRegion_name": "_9B2C7A3B-01FB-4BB1-AB44-B86860396601",
#         "SubGeographicalRegion_name": "_A43A3BEC-0EB3-40AD-BAB9-D73A522CCF73",
#         "Line_name":"_0ACEC26F-C381-4D53-B0B3-92FCACD566B6"
#         },
#         "application_config": {
#             "applications": []
#             },
#         "simulation_config": {
#             "start_time": str(starting_time),
#             "duration": "30",
#             "simulator": "GridLAB-D",
#             "timestep_frequency": "1000",
#             "timestep_increment": "1000",
#             "run_realtime": "true",
#             "simulation_name": "psu_13_node_feeder_7",
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

os.environ['GRIDAPPSD_USER'] = 'tutorial_user'
os.environ['GRIDAPPSD_PASSWORD'] = '12345!'
os.environ['GRIDAPPSD_ADDRESS'] = 'localhost'
os.environ['GRIDAPPSD_PORT'] = '61613'

gapps_session = GridAPPSD()
assert gapps_session.connected

# sim_session = Simulation(gapps_session,sim_config)
topic = t.REQUEST_POWERGRID_DATA
resp = gapps_session.query_data(loads_query)
print(resp)
feeder_id = []
feeder_id.append(resp['data']['results']['bindings'][0]['fdrid']['value'])



tree = et.parse('/home/deras/Desktop/midrar_work_github/cimhub_psu_feeder/cimhub_docker/Master.xml')
root = tree.getroot()
mrids = []
for child in root:
        geo = (child.tag).split("}")[1]
        if (geo =="GeographicalRegion") or (geo == 'SubGeographicalRegion') or (geo == 'Feeder'):
            for element in child.attrib:
                mrids.append(child.attrib[element])
print(f"Geo\t{mrids[0]}")
print(f"Sub\t{mrids[1]}")
print(f"Feeder\t{mrids[2]}")
    