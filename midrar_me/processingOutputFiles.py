import xml
import json
import pandas as pd
from pprint import pprint as pp
from pathlib import Path as path

me_dir = path().absolute()

output_logs = pd.read_csv(f"{me_dir}/Logged_Grid_State_Data/MeasOutputLogs.csv")
input_logs = pd.read_csv(f"{me_dir}/DERSHistoricalDataInput/psu_13_feeder_ders_s.csv")

cols = input_logs.columns
k = 0
print(input_logs[])
for i in cols:
    print(input_logs[i])
#     print("-----------")
#     print("-----------")
#     print("-----------")
#     k +=1
#     if k > 2:
#         break
    


cols = output_logs.columns

# print("===========")
# print("===========")
# print("===========")

# for i in cols:
#     print(i)

# for row in cols:
#     rows = output_logs[row]
#     print("\n\n------\n\nparsing rows\n\n------\n\n")
#     print(rows)
#     for i in rows:
#         print("\n\n$$$$$$$$$$$$$$$$$$$$\n\nparsing the above row\n\n$$$$$$$$$$$$$$$$$$$$\n\n")
#         print(i)
#     k +=1
#     if k > 2:
#         break
#     print("-----------")
#     print("-----------")
#     print("-----------")
