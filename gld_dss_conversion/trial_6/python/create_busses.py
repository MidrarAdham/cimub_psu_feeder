import json
import csv
import pprint
import json
path = "../../trial_5/glm/temp_cleaned_glm.json"

with open(path,'r') as f :
    data = json.load(f)
    objects = data['objects']
    for obj in objects:
        if obj['name'] == "triplex_line":
            print(f"New Load.{obj['attributes']['to']}\tBus1={obj['attributes']['from']}.1.2 phases=1 Conn=Wye kV=0.208 kW=3.0 kvar=0.0")
