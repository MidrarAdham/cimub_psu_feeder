import pandas as pd
df = pd.read_csv("./DERSHistoricalDataInput/psu_13_feeder_ders_s.csv")

df = df.applymap(lambda x: x.lower() if type(x) == str else x)

df = df.iloc[:, :11]

print(df.head(5))

# list_ders = ['DER0','DER1', 'DER2', 'DER3', 'DER4']

# df = pd.read_csv("./DERSHistoricalDataInput/psu_13_feeder_ders_s.csv")
# for i in list_ders:
#     print(f'{df[i+"_loc"]}\n\n\nThe follwoing  is {i} magnitude \n\n\n{df[i+"_mag"]}')
# input_table = [
#     {
#         "Time": "1672531200",
#         "DER0_loc": "trip_load_684_C_h_1",
#         "DER0_mag": "640.0",
#         "DER1_loc": "trip_load_632_C_h_1",
#         "DER1_mag": "2400.0",
#         "DER2_loc": "trip_load_692_B_h_1",
#         "DER2_mag": "760.0",
#         "DER3_loc": "trip_load_671_C_h_1",
#         "DER3_mag": "520.0",
#         "DER4_loc": "trip_load_645_C_h_1",
#         "DER4_mag": "760.0"
#     },
#     {
#         "Time": "1672531201",
#         "DER0_loc": "trip_load_684_C_h_1",
#         "DER0_mag": "640.0",
#         "DER1_loc": "trip_load_632_C_h_1",
#         "DER1_mag": "2400.0",
#         "DER2_loc": "trip_load_692_B_h_1",
#         "DER2_mag": "760.0",
#         "DER3_loc": "trip_load_671_C_h_1",
#         "DER3_mag": "520.0",
#         "DER4_loc": "trip_load_645_C_h_1",
#         "DER4_mag": "760.0"
#     },
#     {
#         "Time": "1672531202",
#         "DER0_loc": "trip_load_684_C_h_1",
#         "DER0_mag": "640.0",
#         "DER1_loc": "trip_load_632_C_h_1",
#         "DER1_mag": "2400.0",
#         "DER2_loc": "trip_load_692_B_h_1",
#         "DER2_mag": "760.0",
#         "DER3_loc": "trip_load_671_C_h_1",
#         "DER3_mag": "520.0",
#         "DER4_loc": "trip_load_645_C_h_1",
#         "DER4_mag": "760.0"
#     },
#     {
#         "Time": "1672531203",
#         "DER0_loc": "trip_load_684_C_h_1",
#         "DER0_mag": "640.0",
#         "DER1_loc": "trip_load_632_C_h_1",
#         "DER1_mag": "2400.0",
#         "DER2_loc": "trip_load_692_B_h_1",
#         "DER2_mag": "760.0",
#         "DER3_loc": "trip_load_671_C_h_1",
#         "DER3_mag": "520.0",
#         "DER4_loc": "trip_load_645_C_h_1",
#         "DER4_mag": "760.0"
#     },
#     {
#         "Time": "1672531204",
#         "DER0_loc": "trip_load_684_C_h_1",
#         "DER0_mag": "640.0",
#         "DER1_loc": "trip_load_632_C_h_1",
#         "DER1_mag": "2400.0",
#         "DER2_loc": "trip_load_692_B_h_1",
#         "DER2_mag": "760.0",
#         "DER3_loc": "trip_load_671_C_h_1",
#         "DER3_mag": "520.0",
#         "DER4_loc": "trip_load_645_C_h_1",
#         "DER4_mag": "760.0"
#     },
#     {
#         "Time": "1672531205",
#         "DER0_loc": "trip_load_684_C_h_1",
#         "DER0_mag": "640.0",
#         "DER1_loc": "trip_load_632_C_h_1",
#         "DER1_mag": "2400.0",
#         "DER2_loc": "trip_load_692_B_h_1",
#         "DER2_mag": "760.0",
#         "DER3_loc": "trip_load_671_C_h_1",
#         "DER3_mag": "520.0",
#         "DER4_loc": "trip_load_645_C_h_1",
#         "DER4_mag": "760.0"
#     },
#     {
#         "Time": "1672531206",
#         "DER0_loc": "trip_load_684_C_h_1",
#         "DER0_mag": "640.0",
#         "DER1_loc": "trip_load_632_C_h_1",
#         "DER1_mag": "2400.0",
#         "DER2_loc": "trip_load_692_B_h_1",
#         "DER2_mag": "760.0",
#         "DER3_loc": "trip_load_671_C_h_1",
#         "DER3_mag": "520.0",
#         "DER4_loc": "trip_load_645_C_h_1",
#         "DER4_mag": "760.0"
#     },
#     {
#         "Time": "1672531207",
#         "DER0_loc": "trip_load_684_C_h_1",
#         "DER0_mag": "640.0",
#         "DER1_loc": "trip_load_632_C_h_1",
#         "DER1_mag": "2400.0",
#         "DER2_loc": "trip_load_692_B_h_1",
#         "DER2_mag": "760.0",
#         "DER3_loc": "trip_load_671_C_h_1",
#         "DER3_mag": "520.0",
#         "DER4_loc": "trip_load_645_C_h_1",
#         "DER4_mag": "760.0"
#     },
#     {
#         "Time": "1672531208",
#         "DER0_loc": "trip_load_684_C_h_1",
#         "DER0_mag": "640.0",
#         "DER1_loc": "trip_load_632_C_h_1",
#         "DER1_mag": "2400.0",
#         "DER2_loc": "trip_load_692_B_h_1",
#         "DER2_mag": "760.0",
#         "DER3_loc": "trip_load_671_C_h_1",
#         "DER3_mag": "520.0",
#         "DER4_loc": "trip_load_645_C_h_1",
#         "DER4_mag": "760.0"
#     },
#     {
#         "Time": "1672531209",
#         "DER0_loc": "trip_load_684_C_h_1",
#         "DER0_mag": "640.0",
#         "DER1_loc": "trip_load_632_C_h_1",
#         "DER1_mag": "2400.0",
#         "DER2_loc": "trip_load_692_B_h_1",
#         "DER2_mag": "760.0",
#         "DER3_loc": "trip_load_671_C_h_1",
#         "DER3_mag": "520.0",
#         "DER4_loc": "trip_load_645_C_h_1",
#         "DER4_mag": "760.0"
#     }
# ]

# location_lookup_dictionary = {
#     "DER0_loc": "DER0_mag",
#     "DER1_loc": "DER1_mag",
#     "DER2_loc": "DER2_mag",
#     "DER3_loc": "DER3_mag",
#     "DER4_loc": "DER4_mag"
# }

# list_of_ders = [
#     "DER0_loc",
#     "DER1_loc",
#     "DER2_loc",
#     "DER3_loc",
#     "DER4_loc"
# ]

# pp(input_table[0])
# print("===============")
# print("===============")
# print("===============")
# pp(location_lookup_dictionary)
# print("===============")
# print("===============")
# print("===============")

# for i in list_of_ders:
#     der_being_assigned = input_table[0][(location_lookup_dictionary[i])]
#     print(der_being_assigned)


# for i in list_of_ders:
#     der_being_assigned = input_table[0][(location_lookup_dictionary[i])]
#     print(der_being_assigned)
#     der_being_assigned[i] = input_table[0]
