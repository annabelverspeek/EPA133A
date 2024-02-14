import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

#reading the excel file
df_roads = pd.read_csv("_roads copy.tsv", delimiter="\t")

#function to plot the roads
def plot_rd(road_name, df_roads):
    plt.figure(figsize=(10, 6))
    plt.plot(df_road['LON'], df_road['LAT'], marker='o', linestyle='-')
    plt.title(road_name)
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.grid(True)
    plt.show()

#making sure the columns are rows. And that every row is a road
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

    plot_rd(road_name, df_road)

    break  # Remove this if you want to plot all roads

#print(df_road.describe())

def calc_lrp_distance (df_rd_lrp):
    df_lrp_before = df_rd_lrp.shift()

    lrp_dist = np.sqrt((df_lrp_before.LAT- df_rd_lrp.LAT)**2 + (df_lrp_before.LON-df_rd_lrp.LON)**2)

    return lrp_dist

lrp_dist = calc_lrp_distance(df_road)
print(lrp_dist)

def get_lrps_off_rd (lrp_dist):
    threshold = lrp_dist.quantile(0.8)*20

    lrp_off_rd = lrp_dist.loc[(lrp_dist > threshold) & (lrp_dist.shift(-1) > threshold)]
    return lrp_off_rd

lrp_off_rd = get_lrps_off_rd(lrp_dist)

print(lrp_off_rd)
print(df_road.loc[lrp_off_rd.index])