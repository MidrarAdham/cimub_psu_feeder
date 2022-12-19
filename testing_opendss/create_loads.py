import json
from pprint import pprint as pp
import os 
import pandas as pd



#for i in range(1,961):
#    # print(f"New Loadshape.shape{i} npts=672 mult=(file=house_{i}.csv)")
#    print(f"Daily=shape{i} phases=2 Conn=Wye kV=0.208 kvar=0.0")


# namebusses = []

# def read_by_tokens(file_name): 
#     for line in file_name:
#         for token in line.split():
#             yield token 

# with open("./Master.dss", "r") as f:
#     for token in read_by_tokens(f):
#         if token.startswith("Bus1"):
#             spl1 = token.split("=")[1]
#             if not spl1.startswith("N"):
#                 namebusses.append(spl1)

# directory = "./"
# dump = "./no_time_csv_files/"
# file_names = os.listdir(directory)
# c = 1
# for files in file_names:
#     if files.startswith("house") and files.endswith('csv'):
#         df = pd.read_csv(os.path.join(directory,files))
#         df = df.drop(columns=df.columns[0])
#         df.to_csv(dump+files,index=False)


directory = "./"
dump = "./no_ts_csv_files/"
file_names = os.listdir(directory)
for files in file_names:
    if files.startswith("house") and files.endswith('csv'):
        df = pd.read_csv(directory+files)
        df = df.drop(columns=df.columns[0])
        df = df.iloc[:,0]/1000
        df.to_csv(dump+files, index=False)
