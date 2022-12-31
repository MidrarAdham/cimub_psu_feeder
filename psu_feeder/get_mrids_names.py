from gridappsd import GridAPPSD,DifferenceBuilder
from gridappsd import topics as t
from gridappsd.simulation import Simulation
import ast
import pprint
import pandas as pd
import csv
import numpy as np
import os
from pathlib import Path
import json

loads_query = """
  
  # loads (need to account for 2+ unequal EnergyConsumerPhases per EnergyConsumer) - DistLoad
  PREFIX r:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
  PREFIX c:  <http://iec.ch/TC57/CIM100#>
  SELECT ?name ?bus ?basev ?p ?q ?pz ?qz ?pi ?qi ?pp ?qp ?pe ?qe ?fdrid ?t1id (group_concat(distinct ?phs) as ?phases) WHERE {
  ?s r:type c:EnergyConsumer.
  ?s c:IdentifiedObject.name ?name.
  # feeder selection options - if all commented out, query matches all feeders
  VALUES ?fdrid {"67CF8C4B-700E-4019-A03D-7C9E929ECAF9"}  # R2 12.47 3
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

list_meas_query = """
    list measurement points for ACLineSegments in a selected feeder
  PREFIX r:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
  PREFIX c:  <http://iec.ch/TC57/CIM100#>
  SELECT ?name ?bus1 ?bus2 ?id (group_concat(distinct ?phs;separator="") as ?phases) WHERE {
    SELECT ?name ?bus1 ?bus2 ?phs ?id WHERE {
   VALUES ?fdrid {"F234F944-6C06-4D13-8E87-3532CDB095FA"}  # R2 12.47 3
   ?fdr c:IdentifiedObject.mRID ?fdrid.
   ?s r:type c:ACLineSegment.
   ?s c:Equipment.EquipmentContainer ?fdr.
   ?s c:IdentifiedObject.name ?name.
   ?s c:IdentifiedObject.mRID ?id.
   ?t1 c:Terminal.ConductingEquipment ?s.
   ?t1 c:ACDCTerminal.sequenceNumber "1".
   ?t1 c:Terminal.ConnectivityNode ?cn1. 
   ?cn1 c:IdentifiedObject.name ?bus1.
   ?t2 c:Terminal.ConductingEquipment ?s.
   ?t2 c:ACDCTerminal.sequenceNumber "2".
   ?t2 c:Terminal.ConnectivityNode ?cn2. 
   ?cn2 c:IdentifiedObject.name ?bus2
  	OPTIONAL {?acp c:ACLineSegmentPhase.ACLineSegment ?s.
   	?acp c:ACLineSegmentPhase.phase ?phsraw.
     	bind(strafter(str(?phsraw),"SinglePhaseKind.") as ?phs) }
   } ORDER BY ?name ?phs
  }
  GROUP BY ?name ?bus1 ?bus2 ?id
  ORDER BY ?name
  """


xfmr_query =   """
  # loads (need to account for 2+ unequal EnergyConsumerPhases per EnergyConsumer) - DistLoad
  PREFIX r:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
  PREFIX c:  <http://iec.ch/TC57/CIM100#>
  SELECT ?name ?wnum ?bus ?eqid ?trmid WHERE {VALUES ?fdrid {"F234F944-6C06-4D13-8E87-3532CDB095FA"}
  ?s r:type c:PowerTransformer.
  ?s c:IdentifiedObject.name ?name.
  ?s c:IdentifiedObject.mRID ?eqid.
  ?tank c:TransformerTank.PowerTransformer ?s.
  ?end c:TransformerTankEnd.TransformerTank ?tank.
  ?end c:TransformerEnd.Terminal ?trm.
  ?end c:TransformerEnd.endNumber ?wnum.
  ?trm c:IdentifiedObject.mRID ?trmid. 
  ?trm c:Terminal.ConnectivityNode ?cn. 
  ?cn c:IdentifiedObject.name ?bus.
  OPTIONAL {?end c:TransformerTankEnd.phases ?phsraw.
    bind(strafter(str(?phsraw),"PhaseCode.") as ?phases)}
  }
  ORDER BY ?name ?wnum ?phs
  """

me_path = '/home/deras/Desktop/midrar_work_github/midrar_me/'
cimhub_path = '/home/deras/Desktop/midrar_work_github/cimub_psu_feeder/cimhub/'

'''
We need to create a new configuration file every time we runthe upload_feeder.sh script.
The upload_feeder.sh generates a new set of mRIDs every time we run it; this will change
the geographical and subgeographical region mRIDs that's been used previously.
'''

def generate_config_file(me_path, cimhub_path):
  '''
  This function reads the new generated mRID file by OpenDSS within the CIMHub repository.
  The file is called "master_uuids.dat". This function will copy the file from its current
  directory and paste it in the psu_feeder folder within the ME main directory. The functions
  will also extract The new mRIDs and write them in a new configuration file. The new mRIDs
  should located within the CIMHub directory.
  '''

  new_mrids = []

  # path = "/home/deras/Desktop/Midrar_work/gld_dss_cim_conversion/glm_files/conversion_trials/dss_files/CIMHub/tutorial"
  # os.system("cp "+cimhub_path+"/master_uuids.dat ./")
  reader = csv.reader(open(cimhub_path+"master_uuids.dat", "r"), delimiter="\t")
  for line in reader:
    if (line[0].split()[0] == 'GeoRgn=GeoRgn=1') or (line[0].split()[0] == 'SubGeoRgn=SubGeoRgn=1') or (line[0].split()[0] == 'Circuit.psu_13_node_feeder_7'):
      new_mrids.append(line[0].split()[1].strip('{ }'))

  with open(me_path+"Configuration/config_midrar.txt") as f:
    json_file = f.read()
    data = json.loads(json_file)
    data["power_system_config"]["GeographicalRegion_name"] = new_mrids[1]
    data["power_system_config"]["SubGeographicalRegion_name"] = new_mrids[2]
    data["power_system_config"]["Line_name"] = new_mrids[0]

    # Convert the data object to a JSON string and store it in a variable
    json_string = json.dumps(data, indent=2)

    # Print the JSON string
    print(json_string)

    # Write the JSON string to a file
    with open(me_path+"Configuration/psu_feeder_config.txt",'w') as wr_file:
        wr_file.write(json_string)




def connect_gridappsd():
  os.environ['GRIDAPPSD_USER'] = 'tutorial_user'
  os.environ['GRIDAPPSD_PASSWORD'] = '12345!'
  os.environ['GRIDAPPSD_ADDRESS'] = 'localhost'
  os.environ['GRIDAPPSD_PORT'] = '61613'

  gapps_session = GridAPPSD()
  assert gapps_session.connected
  return gapps_session



def create_mrid_files(me_path, loads_query, gapps_session):

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

  with open(me_path+"Configuration/psu_feeder_config.txt") as f:
      config_string = f.read()
      config_parameters = ast.literal_eval(config_string)

  line_mrid = config_parameters["power_system_config"]["Line_name"]
  sim_start_time = config_parameters["simulation_config"]["start_time"]
  sim_session = Simulation(gapps_session,config_parameters)  
  # topic = "goss.gridappsd.process.request.data.powergridmodel"
  # message = {"modelID":line_mrid,"requestType":"QUERY_OBJECT_MEASUREMENTS","resutFormat":"JSON",}
  # object_meas = gapps_session.get_response(topic,loads_query)
  topic = t.REQUEST_POWERGRID_DATA
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
  df_files.to_csv(me_path+"DERScripts/EGoT13_der_psu.txt", mode="w", index=False)
  df_data.to_csv(me_path+"DERScripts/EGoT13_der_psu.txt", mode="a", index=False, quoting=csv.QUOTE_NONE, escapechar=" ")


def main(me_path,cimhub_path,loads_query, list_meas_query, xfmr_query):
  generate_config_file(me_path, cimhub_path)
  gapps_session = connect_gridappsd()
  create_mrid_files(me_path, loads_query, gapps_session)
 
main(me_path, cimhub_path, loads_query, list_meas_query, xfmr_query)