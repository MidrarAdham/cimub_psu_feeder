import os
import json
from pathlib import Path as path
import xml.etree.ElementTree as et
from datetime import datetime as dt

current_dir = path().absolute()
os.chdir("../")
ckt_name = 'psu_13_node_feeder_7'       # Type your ckt name. It can be found in the dat file.
mytree = et.parse('Master.xml')
sim_start_time = '2023-01-01 00:00:00'
sim_stop_time = '2023-01-02 00:00:00'


def get_mrids(mytree):
    root = mytree.getroot()
    mrids = []
    for child in root:
        geo = (child.tag).split("}")[1]
        if (geo =="GeographicalRegion") or (geo == 'SubGeographicalRegion'):
            for element in child.attrib:
                mrids.append(child.attrib[element])
    
    with open ('master.dat','r') as f:
        for lines in f:
            if (lines.split()[0]).startswith('Circuit.'+ckt_name):
                line_name = (lines.split()[1]).strip('{ }')

    return mrids, line_name


def unix_ts(time):
    dt_time = dt.strptime(time, "%Y-%m-%d %H:%M:%S")
    unix_ts = dt_time.timestamp()
    return unix_ts

def create_config_file(mrids, line_name):
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
            "start_time": f"{unix_ts(sim_start_time)}",
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

def wr_json(sim_config):
    os.chdir("../Configuration/")
    with open ('simulation_configuration.json', 'w') as output:
        json.dump(sim_config, output, indent=4)

def main(current_dir, ckt_name, mytree, sim_start_time, sim_stop_time):
    mrids, line_name = get_mrids(mytree)
    sim_time = unix_ts(sim_start_time)
    sim_config = create_config_file(mrids, line_name)
    wr_json(sim_config)
main(current_dir, ckt_name, mytree, sim_start_time, sim_stop_time)