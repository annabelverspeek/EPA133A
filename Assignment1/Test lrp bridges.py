import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

#bridges:
file = 'BMMS_overview.xlsx'

df_bridges = pd.read_excel(file)

#roads
dtypes = {'LRP': str, 'LAT': float, 'LON': float}
df_roads = pd.read_csv("_roads.tsv", delimiter="\t", dtype=dtypes)

road_data_list = []

for road in df_roads.itertuples(index=False):
    road_name = road[0]
    data = []

    for i in range(1, len(road), 3):
        if pd.isna(road[i]):
            break
        else:
            lrp = (road[i], road[i + 1], road[i + 2])
            data.append(lrp)

    df_road = pd.DataFrame(data, columns=['LRP', 'LAT', 'LON'])

    road_data_list.append(df_road)

print(road_data_list[0].head())

print(df_bridges.head())

all_lrps = []

for df_road in road_data_list:
    all_lrps.extend(df_road['LRP'].tolist())


for lrp in df_bridges('LRPName'):
    if lrp not in all_lrps:
        print(lrp)