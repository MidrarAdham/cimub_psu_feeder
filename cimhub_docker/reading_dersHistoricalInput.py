import pandas as pd

df = pd.read_csv('/home/deras/Desktop/midrar_work_github/cimhub_psu_feeder/midrar_me/DERSHistoricalDataInput/psu_13_feeder_ders_s.csv')

print(df['DER0_loc'])
