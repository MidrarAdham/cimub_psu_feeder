import glm
import json
import time
import os



# glm_file = "./gld_basecase.glm"
# json_file = "./gld_basecase.json"
# f_name = "./psu_13_feeder"
f_name = "./new_psu_13_feeder"


def to_json(f_name):
    if not os.path.isfile(f_name+".json"):
        os.system(f"glm2json -p {f_name}.glm --pretty >> ./{f_name}.json")
    json_file = f"{f_name}.json"
    return json_file


def clean_json(json_file):
    with open(json_file) as f:
        jf = json.load(f)
        new_obj = []
        obj = jf['objects']
        for i in obj:
            if not i['name'] == 'triplex_load' and not i['name'] == 'triplex_line' and not i['name'] == 'house' and not i['name'] == 'waterheater' and not i['name'] == 'multi_recorder' and not i['name'] == 'player':
                new_obj.append(i)
        jf['objects'] = new_obj
        
        with open('./gld_basecase.json','w') as out:
            json.dump(jf, out, indent=2)

def glm_dss(json_file):
    os.system(f"ditto-cli convert --input ./psu_13_node_feeder.glm --from gridlabd --to opendss --output ./another_trial/")

def main(f_name):
    json_file = to_json(f_name)
    cleaned_json = clean_json(json_file)

main(f_name)



    # if not os.path.isfile(json_file):
    #     cleaned_json = clean_json(json_file)
    # else:
    #     print(f"\tFile already exist in directory with name {json_file}\n")

#============= Working Script =======================

# path = "./gld_basecase.glm"
# f1 = glm.load(path)

# with open("./gld_basecase.json") as f:
#     jf = json.load(f)
#     obj = jf['objects']
#     new_obj = []
#     key = jf.keys()

#     print('BEFORE deletion\tsize: ',len(obj),len(jf['objects']))
#     for i in obj:
#         if not i['name'] == 'triplex_load' and not i['name'] == 'house' and not i['name'] == 'waterheater':
#             new_obj.append(i)
#     jf['objects'] = new_obj
#     print('AFTER deletion\tsize: ',len(obj),len(jf['objects']))

#     with open('./test_output.json','w') as out:
#         json.dump(jf, out, indent=2)