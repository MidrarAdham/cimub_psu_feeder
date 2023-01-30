import os
import csv
import json
import pandas as pd
from pprint import pprint as pp
from pathlib import Path as path
from gridappsd import topics as t
import xml.etree.ElementTree as et
from datetime import datetime as dt
from gridappsd.simulation import Simulation
from gridappsd import GridAPPSD, DifferenceBuilder

current_dir = path().absolute()
os.chdir("../")
ckt_name = 'psu_13_node_feeder_7'       # Type your ckt name. It can be found in the dat file.
mytree = et.parse('/home/deras/Desktop/midrar_work_github/cimhub_psu_feeder/cimhub_docker/Master.xml')
sim_start_time = '2023-01-01 00:00:00'
sim_stop_time = '2023-01-02 00:00:00'


def query_feeder (fd_id):
    
    
    loads_query = f'''
    
    # loads (need to account for 2+ unequal EnergyConsumerPhases per EnergyConsumer) - DistLoad
    PREFIX r:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX c:  <http://iec.ch/TC57/CIM100#>
    SELECT ?name ?bus ?basev ?p ?q ?pz ?qz ?pi ?qi ?pp ?qp ?pe ?qe ?fdrid ?t1id (group_concat(distinct ?phs) as ?phases) WHERE {{
    ?s r:type c:EnergyConsumer.
    ?s c:IdentifiedObject.name ?name.
    # feeder selection options - if all commented out, query matches all feeders
    VALUES ?fdrid {{"{fd_id}"}}
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
    OPTIONAL {{?lr c:LoadResponseCharacteristic.pVoltageExponent ?pe.}}
    OPTIONAL {{?lr c:LoadResponseCharacteristic.qVoltageExponent ?qe.}}
    OPTIONAL {{?ecp c:EnergyConsumerPhase.EnergyConsumer ?s.
    ?ecp c:EnergyConsumerPhase.phase ?phsraw.
        bind(strafter(str(?phsraw),"SinglePhaseKind.") as ?phs) }}
    ?t c:Terminal.ConductingEquipment ?s.
    ?t c:Terminal.ConnectivityNode ?cn. 
    ?t c:IdentifiedObject.mRID ?t1id. 
    ?cn c:IdentifiedObject.name ?bus
    }}
    GROUP BY ?name ?bus ?basev ?p ?q ?cnt ?conn ?pz ?qz ?pi ?qi ?pp ?qp ?pe ?qe ?fdrid ?t1id
    ORDER by ?name
    '''

    return loads_query

def get_mrids(mytree):
    root = mytree.getroot()
    mrids = []
    for child in root:
        geo = (child.tag).split("}")[1]
        if (geo =="GeographicalRegion") or (geo == 'SubGeographicalRegion') or (geo == 'Feeder'):
            for element in child.attrib:
                mrids.append(child.attrib[element])
    
    with open ('/home/deras/Desktop/midrar_work_github/cimhub_psu_feeder/cimhub_docker/master.dat','r') as f:
        for lines in f:
            if (lines.split()[0]).startswith('Circuit.'+ckt_name):
                line_name = (lines.split()[1]).strip('{ }')

    return mrids, line_name


def create_config_file(mrids, line_name):
    df = pd.read_csv('/home/deras/Desktop/midrar_work_github/midrar_me/DERSHistoricalDataInput/psu_13_feeder_ders_s.csv')
    starting_time = df.loc[0]['Time']
    sim_config = {
        "power_system_config": {
            "GeographicalRegion_name": mrids[0],
            "SubGeographicalRegion_name": mrids[1],
            "Line_name":line_name
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
    return sim_config

def create_mrid_files(config_parameters, loads_query):
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
    
    os.environ['GRIDAPPSD_USER'] = 'tutorial_user'
    os.environ['GRIDAPPSD_PASSWORD'] = '12345!'
    os.environ['GRIDAPPSD_ADDRESS'] = 'localhost'
    os.environ['GRIDAPPSD_PORT'] = '61613'

    gapps_session = GridAPPSD()
    assert gapps_session.connected

    sim_session = Simulation(gapps_session,config_parameters)
    topic = t.REQUEST_POWERGRID_DATA
    print(loads_query)
    resp = gapps_session.query_data(loads_query)
    print(resp)

    feeder_id.append(resp['data']['results']['bindings'][0]['fdrid']['value'])
    print(f"\n\n--------\n\n{feeder_id}\n\n----------\n\n")
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

    return df_files, df_data

def wr_json(sim_config):
    os.chdir('/home/deras/Desktop/midrar_work_github/midrar_me/Configuration/')
    with open ('simulation_configuration.json', 'w') as output:
        json.dump(sim_config, output, indent=4)
    
def wr_df(df_files, df_data):
    
    df_files.to_csv("/home/deras/Desktop/midrar_work_github/midrar_me/DERScripts/EGoT13_der_psu.txt", mode="w", index=False)
    df_data.to_csv("/home/deras/Desktop/midrar_work_github/midrar_me/DERScripts/EGoT13_der_psu.txt", mode="a", index=False, quoting=csv.QUOTE_NONE, escapechar=" ")

def main(current_dir, ckt_name, mytree, sim_start_time):
    mrids, line_name = get_mrids(mytree)
    query_loads = query_feeder (mrids[2])
    # print(query_loads)
    sim_config = create_config_file (mrids, line_name)
    df_files, df_data = create_mrid_files(sim_config, query_loads)
    os.chdir(current_dir)
    wr_json(sim_config)
    wr_df(df_files, df_data)
main(current_dir, ckt_name, mytree, sim_start_time)