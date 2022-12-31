from datetime import datetime as dt
import pandas as pd
import json
from pathlib import Path
import csv

'''
This script gathers the data from different files to construct the DERs info and write it in the DERSHistoricalDataInput.
1- A set of lists will be initialized to append DER data to them.
2- Get the starting simulation time (unix) from the configuration file within the Configuration folder.
    2A- Increment the starting time by 15 minutes until the full simulation time reaches one week (Will probably changed later)
    2B- Append the time values to its associated list so it can be written later to a csv file.
3- Get the DER[counter]_loc names from EGoT13_der_psu_uuid.txt; this file can be found in the DERScripts folder
    3A- Append these names in their associated it list so I can write it later in a csv file
4- Find the load profile used for the water heaters in Watts (somwhere in GitHub):
    4A- Read each power consumption for each DER from the load profile.
    4B- Directly append the power consumption values to a csv file.
    4C- The power consumption values SHALL be in a Watts, NOT kW.
'''

me_path = str(Path().absolute()) # takes you to me main directory

def get_loc_names(me_path):

    reader = csv.reader(open(me_path+"/DERScripts/EGoT13_der_psu_uuid.txt", 'r'), delimiter = ",")
    counter = 0                  # counter to the header file numbers
    
    for line in reader:
        if (line[0].split()[0] == 'Location'):
        
    