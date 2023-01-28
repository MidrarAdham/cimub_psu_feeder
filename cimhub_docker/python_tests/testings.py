import ast
from pathlib import Path as path

current_dir = path().absolute()

config_file = f'{current_dir}/config/simulation_configuration.json'
with open (config_file) as f:
    config_string = f.read()
    config_parameters = ast.literal_eval (config_string)
    sim_start_time = config_parameters["power_system_config"]["Line_name"]

dersHistoricalDataInput = 1
rwhDERS = 2
ders_obj_list = {
    'DERSHistoricalDataInput': 'dersHistoricalDataInput',
    'RWHDERS': 'rwhDERS'
    }
for key, value in ders_obj_list.items():
    print(f'key: {key} <---> value: {value}')