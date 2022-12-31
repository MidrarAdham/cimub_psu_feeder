import csv
import pandas as pd
import os
import random
from io import StringIO
import matplotlib.pyplot as plt
from collections import defaultdict
import pprint

dss_master_path = "/home/deras/Desktop/midrar_work_github/cimub_psu_feeder/cimhub/Master.dss"

bus_names_list = []
east_level_1 = []
east_level_2 = []
west_level_1 = []
west_level_2 = []
backbone = []
dict_nodes_coords = {}
dict_nodes2 = defaultdict(list) #used in the mapping func

'''
The read_by_tokens function is called in the extract_busses function. 
It is not called from main.
'''
def read_by_tokens(file_name): 
    for line in file_name:
        for token in line.split():
            yield token             #Remember to use yield because it remembers where it stopped and then return back
                                    #from the same position.
'''
The extract_busses reads the opendss file and extract all the bus names and appends them to a list.
It then deletes the repeated names from the list. Removing the repeated names is caused by configuration of the psu feeder.
OpenDSS takes the same node and consider it as a bus and then change the phases every time depending on the phases
considered for each node.
'''

def extract_busses(bus_names, dss_master_path):
    counter = 0
    with open(dss_master_path) as f:
        for token in read_by_tokens(f):
            if (token.startswith("Bus1")) or (token.startswith("bus")) or (token.startswith("bus1")) or (token.startswith("bus2")):
                filtered_token = token.split('=')[1].split('.')[0]
                if filtered_token not in bus_names: #Remove duplicated bus names
                    bus_names.append(filtered_token)
    # pprint.pprint(bus_names) This prints the SourceBus
    return bus_names

'''
The for_looping function helps in filtering each node and its associated components (loads, lines, xfmers, etc) and append
these components in their own lists.
'''
def for_looping(bus_names, node_number): # This function is not called in main.
    passed_list = []
    counter = 0
    for i in node_number:
        counter +=1
    '''
    The following for loop append the components of each set of nodes in their own lists. Note that each side of the
    feeder has a minimum number of two nodes. Therefore, the node_number attribute is a list of at least two items.
    '''
    for nodes in bus_names:
        if counter == 3:
            if ((node_number[0] in nodes) or (node_number[1] in nodes) or (node_number[2] in nodes)):
                passed_list.append(nodes)
        if counter == 2:
            if ((node_number[0] in nodes) or (node_number[1] in nodes)):
                passed_list.append(nodes)
        if counter > 3:
            # if (node_number[0] in nodes) or (node_number[1] in nodes) or (node_number[2] in nodes) or (node_number[3] in nodes) or (node_number[4] in nodes) or (node_number[5] in nodes) or (node_number[6] in nodes):
            # if (node_number[0] in nodes) or (node_number[1] in nodes) or (node_number[2] in nodes) or (node_number[3] in nodes) or (node_number[4] in nodes) or (node_number[5] in nodes):
            if (node_number[0] in nodes) or (node_number[1] in nodes) or (node_number[2] in nodes) or (node_number[3] in nodes) or (node_number[4] in nodes):
                passed_list.append(nodes)
    # pprint.pprint(passed_list) Here we go! SourceBus is here right now
    return passed_list

def get_backbone_coordinates(nodes_busses, level, level_coords, dec_cons):
    decrement = 100 # want the last item to get to zero
    for node in level:
        if (node.startswith("N")) or (node.startswith("S")):
            nodes_busses[node] = (int(level_coords[0]),int(level_coords[1]) - decrement)
            decrement += dec_cons
    return nodes_busses

def sides_coordinates(nodes_busses, level, level_coords, dec_cons):
    decrement = 0
    for node in level:
        if node.startswith("N"):
            if node == "N652":
                # nodes_busses[node] = (2000, int(level_coords[1])-1000)
                nodes_busses[node] = (2000, 1000)
            else:
                nodes_busses[node] = (int(level_coords[0])- decrement,int(level_coords[1]))
            decrement -= dec_cons
    return nodes_busses

def gather_data(bus_names, east_level_1, east_level_2, west_level_1, west_level_2, backbone):

    east_level_1 = for_looping(bus_names, ["633", "634"])
    east_level_2 = for_looping(bus_names, ["692", "675"])
    west_level_1 = for_looping(bus_names, ["645", "646"])
    west_level_2 = for_looping(bus_names, ["684", "611","652"])
    # backbone = for_looping(bus_names, ["SourceBus","650", "630" ,"6321","632","671","680"])
    backbone = for_looping(bus_names, ["630" ,"6321","632","671","680"])

    # Define the feeder backbone nodes locations (x,y) coordinates:
    
    # backbone_top = ["300","600"]

    # east_level_1_x = ["400","400"] #starting point for node 633. Incremenet by x += 100 for node 634
    # west_level_1_x = ["200","400"] #starting point for node 645. Decrement by x -= 100 for node 646
    # east_level_2_x = ["400","200"] #starting point for node 692. Increment by x += 100 for node 675
    # west_level_2_x = ["200","200"] #starting point for node 684. Decrement by x -= 100 for node 611
    backbone_top = ["3000","6000"]

    east_level_1_x = ["4000","4000"] #starting point for node 633. Incremenet by x += 100 for node 634
    west_level_1_x = ["2000","4000"] #starting point for node 645. Decrement by x -= 100 for node 646
    east_level_2_x = ["4000","2000"] #starting point for node 692. Increment by x += 100 for node 675
    west_level_2_x = ["2000","2000"] #starting point for node 684. Decrement by x -= 100 for node 611

    nodes_houses = get_backbone_coordinates(dict_nodes_coords,backbone,backbone_top, 1000)

    nodes_houses = sides_coordinates(dict_nodes_coords, east_level_1,east_level_1_x, 1000)
    nodes_houses = sides_coordinates(dict_nodes_coords, east_level_2,east_level_2_x, 1000)
    nodes_houses = sides_coordinates(dict_nodes_coords, west_level_1,west_level_1_x, -1000)
    nodes_houses = sides_coordinates(dict_nodes_coords, west_level_2,west_level_2_x, -1000)

    return nodes_houses

def dict_df(data):
    return pd.DataFrame.from_dict(data, orient='index')
    
def map_trip_loads(bus_names):
    coords = ["314","-10"]
    main_nodes = ["632","671","680","633","692","675","645","684","611","652"]
    fake_list = []
    for i in bus_names:
        spl1 = i.split("_")
        if (spl1[0] == 'xfmr') or ((spl1[0] == 'trip') and (spl1[1] == 'node')) or ((spl1[0] == 'trip') and (spl1[1] == 'load')) or (spl1[0] == 'meter'):
            for node in main_nodes:
                if (spl1[1] == node) or (spl1[2] == node):
                    fake_list.append(i)

    for i in fake_list:
        for node in main_nodes:
            spl = i.split("_")
            if (spl[1] == node) or (spl[2] == node):
                dict_nodes2[node].append(i)
    
    return dict_nodes2, main_nodes

def return_cords(dict_nodes2,nodes,x,y,x_l,inc_meter,inc_xfmr,x_node,x_load): # This is not called in main
    cords = {}
    inc_met = 0
    inc_met = 0
    inc_xfmr = 0
    inc_trip_n = 0
    inc_trip_l = 0
    for i in dict_nodes2[nodes]:
        if i.startswith("meter"):
            cords[i] = (x + inc_met,y)
            inc_met += inc_meter
        if i.startswith("xfmr"):
            cords[i] = (x + inc_xfmr,y)
            inc_xfmr += inc_xfmr
        if i.startswith("trip_node"):
            cords[i] = (x + inc_trip_n,y)
            inc_trip_n += x_node
        if i.startswith("trip_load"):
            cords[i] = (x_l + inc_trip_l,y)
            inc_trip_l += x_load
    return cords
    # keep_records = pd.DataFrame.from_dict(cords, orient = 'index')
    # keep_records.to_csv("try_this.csv", mode="a")
def set_coords(nodes_houses,dict_nodes2, main_nodes):
    file_headers = pd.DataFrame({'A':["N650","trans_N650_N630","N650_N630"], 'B':["3000","3000","3000"], 'C':["6500","6250","6000"]})
    file_headers.to_csv("./psu_feeder_coords.csv", mode="w", index=False, header=False)
    node_house = dict_df(nodes_houses)
    node_house.to_csv("./psu_feeder_coords.csv",mode = "a" ,header = False)
    
    x,y = (0,0)

    for nodes in main_nodes:
        if nodes == '671':
            cords = return_cords(dict_nodes2,nodes,2920,1800,2860,80,10,10,20)
            cords = dict_df(cords)
            cords.to_csv("./psu_feeder_coords.csv", mode="a", header = False)
        if nodes == '680':
            cords = return_cords(dict_nodes2,nodes,2920,800,2860,80,10,10,20)
            cords = dict_df(cords)
            cords.to_csv("./psu_feeder_coords.csv", mode="a", header = False)
        if nodes == '632':
            cords = return_cords(dict_nodes2,nodes,2920,3800,2860,80,10,10,20)
            cords = dict_df(cords)
            cords.to_csv("./psu_feeder_coords.csv", mode="a", header = False)
        if nodes == '633':
            cords = return_cords(dict_nodes2,nodes,4080,3900,3960,80,10,10,20)
            cords = dict_df(cords)
            cords.to_csv("./psu_feeder_coords.csv", mode="a", header = False)
        if nodes == '692':
            cords = return_cords(dict_nodes2,nodes,3920,1900,3920,80,10,10,20)
            cords = dict_df(cords)
            cords.to_csv("./psu_feeder_coords.csv", mode="a", header = False)
        if nodes == '675':
            cords = return_cords(dict_nodes2,nodes,4920,1900,4720,80,10,10,20)
            cords = dict_df(cords)
            cords.to_csv("./psu_feeder_coords.csv", mode="a", header = False)
        if nodes == '645':
            cords = return_cords(dict_nodes2,nodes,2100,3900,1920,-80,-10,-10,-20)
            cords = dict_df(cords)
            cords.to_csv("./psu_feeder_coords.csv", mode="a", header = False)
        if nodes == '684':
            cords = return_cords(dict_nodes2,nodes,2100,1900,1920,-80,-10,-10,-20)
            cords = dict_df(cords)
            cords.to_csv("./psu_feeder_coords.csv", mode="a", header = False)
        if nodes == '611':
            cords = return_cords(dict_nodes2,nodes,1100,1900,1220,-80,-10,-10,-20)
            cords = dict_df(cords)
            cords.to_csv("./psu_feeder_coords.csv", mode="a", header = False)
        if nodes == '652':
            cords = return_cords(dict_nodes2,nodes,2000,900,1920,-80,-10,-10,-20)
            cords = dict_df(cords)
            cords.to_csv("./psu_feeder_coords.csv", mode="a", header = False)

def wr_files(bus_names, east_level_1, east_level_2, west_level_1, west_level_2, backbone):
    file_headers = pd.DataFrame({'A':"SourceBus", 'B':"200", 'C':"400"}, index = [0]) #Index is for Headers
    file_data = pd.DataFrame({'A':bus_names,'xcoords':x_coords_list, 'ycoords':y_coords_list})
    file_headers.to_csv("./psu_feeder_coords.csv", mode="w", index=False, header=False)
    file_data.to_csv("./psu_feeder_coords.csv", mode="a", index=False, header=False)

def main(bus_names, dss_master_path, east_level_1, east_level_2, west_level_1, west_level_2, backbone):
    bus_names = extract_busses(bus_names_list, dss_master_path)
    nodes_houses= gather_data(bus_names, east_level_1, east_level_2, west_level_1, west_level_2, backbone)
    dict_nodes, main_nodes = map_trip_loads(bus_names)
    set_coords(nodes_houses,dict_nodes, main_nodes)
    # dict_df(nodes_houses)
    # wr_files(bus_names, x_coords_list, y_coords_list)


main(bus_names_list, dss_master_path, east_level_1, east_level_2, west_level_1, west_level_2, backbone)