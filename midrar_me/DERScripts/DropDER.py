from SPARQLWrapper import SPARQLWrapper2
import sys
import re
import uuid
import os.path
import CIMHubConfig

#prefix_template = """PREFIX r: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
#PREFIX c: <{cimURL}>
#PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
#"""

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

drop_trm_template = """DELETE {{
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:Terminal.ConductingEquipment ?eq.
 ?m c:ACDCTerminal.sequenceNumber ?seq.
 ?m c:Terminal.ConnectivityNode ?cn.
}} WHERE {{
 VALUES ?uuid {{\"{res}\"}}
 VALUES ?class {{c:Terminal}}
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:Terminal.ConductingEquipment ?eq.
 ?m c:ACDCTerminal.sequenceNumber ?seq.
 ?m c:Terminal.ConnectivityNode ?cn.
}}
"""

drop_pec_template = """DELETE {{
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:Equipment.EquipmentContainer ?fdr.
 ?m c:PowerElectronicsConnection.PowerElectronicsUnit ?unit.
 ?m c:PowerSystemResource.Location ?loc.
 ?m c:PowerElectronicsConnection.maxIFault ?flt.
 ?m c:PowerElectronicsConnection.p ?p.
 ?m c:PowerElectronicsConnection.q ?q.
 ?m c:PowerElectronicsConnection.ratedS ?S.
 ?m c:PowerElectronicsConnection.ratedU ?U.
}} WHERE {{
 VALUES ?uuid {{\"{res}\"}}
 VALUES ?class {{c:PowerElectronicsConnection}}
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:Equipment.EquipmentContainer ?fdr.
 ?m c:PowerElectronicsConnection.PowerElectronicsUnit ?unit.
 ?m c:PowerSystemResource.Location ?loc.
 ?m c:PowerElectronicsConnection.maxIFault ?flt.
 ?m c:PowerElectronicsConnection.p ?p.
 ?m c:PowerElectronicsConnection.q ?q.
 ?m c:PowerElectronicsConnection.ratedS ?S.
 ?m c:PowerElectronicsConnection.ratedU ?U.
}}
"""

drop_syn_template = """DELETE {{
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:Equipment.EquipmentContainer ?fdr.
 ?m c:PowerSystemResource.Location ?loc.
 ?m c:SynchronousMachine.p ?p.
 ?m c:SynchronousMachine.q ?q.
 ?m c:SynchronousMachine.ratedS ?S.
 ?m c:SynchronousMachine.ratedU ?U.
}} WHERE {{
 VALUES ?uuid {{\"{res}\"}}
 VALUES ?class {{c:SynchronousMachine}}
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:Equipment.EquipmentContainer ?fdr.
 ?m c:PowerSystemResource.Location ?loc.
 ?m c:SynchronousMachine.p ?p.
 ?m c:SynchronousMachine.q ?q.
 ?m c:SynchronousMachine.ratedS ?S.
 ?m c:SynchronousMachine.ratedU ?U.
}}
"""

drop_pep_template = """DELETE {{
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:PowerElectronicsConnectionPhase.phase ?phs.
 ?m c:PowerElectronicsConnectionPhase.PowerElectronicsConnection ?pec.
 ?m c:PowerElectronicsConnectionPhase.p ?p.
 ?m c:PowerElectronicsConnectionPhase.q ?q.
 ?m c:PowerSystemResource.Location ?loc.
}} WHERE {{
 VALUES ?uuid {{\"{res}\"}}
 VALUES ?class {{c:PowerElectronicsConnectionPhase}}
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:PowerElectronicsConnectionPhase.phase ?phs.
 ?m c:PowerElectronicsConnectionPhase.PowerElectronicsConnection ?pec.
 ?m c:PowerElectronicsConnectionPhase.p ?p.
 ?m c:PowerElectronicsConnectionPhase.q ?q.
 ?m c:PowerSystemResource.Location ?loc.
}}
"""

drop_pv_template = """DELETE {{
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:PowerSystemResource.Location ?loc.
}} WHERE {{
 VALUES ?uuid {{\"{res}\"}}
 VALUES ?class {{c:PhotovoltaicUnit}}
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:PowerSystemResource.Location ?loc.
}}
"""

drop_EnergyConsumer_template = """DELETE {{
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:PowerSystemResource.Location ?loc.
}} WHERE {{
 VALUES ?uuid {{\"{res}\"}}
 VALUES ?class {{c:EnergyConsumer}}
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:PowerSystemResource.Location ?loc.
}}
"""
drop_bat_template = """DELETE {{
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:BatteryUnit.ratedE ?rated.
 ?m c:BatteryUnit.storedE ?stored.
 ?m c:BatteryUnit.batteryState ?state.
 ?m c:PowerSystemResource.Location ?loc.
}} WHERE {{
 VALUES ?uuid {{\"{res}\"}}
 VALUES ?class {{c:BatteryUnit}}
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:BatteryUnit.ratedE ?rated.
 ?m c:BatteryUnit.storedE ?stored.
 ?m c:BatteryUnit.batteryState ?state.
 ?m c:PowerSystemResource.Location ?loc.
}}
"""

if len(sys.argv) < 3:
  print ('usage: python3 DropDER.py cimhubconfig.json uuidfname')
  print (' cimhubconfig.json must define blazegraph_url and cim_ns')
  print (' Blazegraph server must already be started')
  exit()

CIMHubConfig.ConfigFromJsonFile (sys.argv[1])
sparql = SPARQLWrapper2(CIMHubConfig.blazegraph_url)
sparql.method = 'POST'

fp = open (sys.argv[2], 'r')
for ln in fp.readlines():
  toks = re.split('[,\s]+', ln)
  if len(toks) > 2 and not toks[0].startswith('//'):
    cls = toks[0]
    nm = toks[1]
    mRID = toks[2]
  qstr = None
  if cls == 'PowerElectronicsConnection':
    qstr = CIMHubConfig.prefix + drop_pec_template.format(res=mRID)
  elif cls == 'PowerElectronicsConnectionPhase':
    qstr = CIMHubConfig.prefix + drop_pep_template.format(res=mRID)
  elif cls == 'Terminal':
    qstr = CIMHubConfig.prefix + drop_trm_template.format(res=mRID)
  elif cls == 'Location':
    qstr = CIMHubConfig.prefix + drop_loc_template.format(res=mRID)
  elif cls == 'PhotovoltaicUnit':
    qstr = CIMHubConfig.prefix + drop_pv_template.format(res=mRID)
  elif cls == 'EnergyConsumer':
    qstr = CIMHubConfig.prefix + drop_EnergyConsumer_template.format(res=mRID)
  elif cls == 'BatteryUnit':
    qstr = CIMHubConfig.prefix + drop_bat_template.format(res=mRID)
  elif cls == 'SynchronousMachine':
    qstr = CIMHubConfig.prefix + drop_syn_template.format(res=mRID)
  elif cls == 'SynchronousMachinePhase':
    print ('*** ERROR: do not know how to drop SynchronousMachinePhase')
    print ('          (only 3-phase machines are currently supported)')
    exit()
  else:
    print(f'----> ERROR: CIM CLASS NOT FOUND <----\n----> CIM CLASS SHOULD BE LOCATED IN THE FIRST COLUMN <----')

  if qstr is not None:
#    print (qstr)
    sparql.setQuery(qstr)
    ret = sparql.query()
    print('deleting', cls, nm, ret.response.msg)
fp.close()