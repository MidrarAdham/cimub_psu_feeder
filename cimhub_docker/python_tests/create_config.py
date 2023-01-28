import json
import xml.etree.ElementTree as et
from datetime import datetime as dt

ckt_name = 'psu_13_node_feeder_7'   # Type your ckt name. It can be found in the dat file.
mytree = et.parse('Master.xml')
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

sim_start_time = '2023-01-01 00:00:00'
sim_stop_time = '2023-01-07 00:00:00'


def unix_ts(time):
    dt_time = dt.strptime(time, "%Y-%m-%d %H:%M:%S")
    unix_ts = dt_time.timestamp()
    return unix_ts

unix_ts(sim_start_time)

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


with open ('simulation_configuration.json', 'w') as output:
    json.dump(sim_config, output, indent=4)


# def get_mrids ():
#     mytree = et.parse('Master.xml')
#     root = mytree.getroot()
#     mrids = []

#     for child in root:
#         feeder = (child.tag).split("}")[1]
#         # if feeder == 'Feeder':
#         #     for element in child.attrib:
#         #         elem = element
#         #     fd_mrid = child.attrib[elem]

#         if (feeder == "GeographicalRegion") or (feeder == 'SubGeographicalRegion') or (feeder == 'Feeder'):
#             for element in child.attrib:
#                 mrids.append(child.attrib[element])
#     print(f"---> FYI <---\n Feeder id is --> \t{mrids[2]}\n\n")
#     print(f"---> FYI <---\n geo is --> \t{mrids[0]}\n\n")
#     print(f"---> FYI <---\n sub geo is --> \t{mrids[1]}\n\n")

# get_mrids()