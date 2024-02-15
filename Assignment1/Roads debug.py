import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

#reading the excel file
dtypes = {'LRP': str, 'LAT': float, 'LON': float}
df_roads = pd.read_csv("_roads copy.tsv", delimiter="\t", dtype=dtypes)

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

def correct_lrps_off_rd(df_road, lrp_off_rd):
    df_road.loc[lrp_off_rd.index, 'LAT'] = (df_road['LAT'].shift().loc[lrp_off_rd.index] + df_road['LAT'].shift(-1).loc[lrp_off_rd.index]) / 2
    df_road.loc[lrp_off_rd.index, 'LON'] = (df_road['LON'].shift().loc[lrp_off_rd.index] + df_road['LON'].shift(-1).loc[lrp_off_rd.index]) / 2

    return df_road

df_road_new = correct_lrps_off_rd(df_road, lrp_off_rd)
lrp_changed_index = lrp_off_rd.index.tolist()
print(lrp_changed_index)

print(plot_rd(road_name, df_road))
print(plot_rd(road_name, df_road_new))

#|second round, ziet in grafiek dat er nog een outlier over is

#pull back deel

lrp_dist = calc_lrp_distance(df_road_new)
print(lrp_dist.describe())

def get_lrp_off_rd_2(lrp_dist):
    threshold = lrp_dist.quantile(0.8)*20

    lrp_off_rd = lrp_dist.loc[(lrp_dist>threshold)]

    return lrp_off_rd

lrp_off_rd = get_lrp_off_rd_2(lrp_dist)
df_road_new.loc[lrp_off_rd.index]

def correct_lrps_off_rd_2(df_road, lrp_off_rd):
    for i in range(0, len(lrp_off_rd.index), 2):
        lrp_start_index = lrp_off_rd.index[i]
        lrp_end_index = lrp_off_rd.index[i+1]
        lrp_nr = lrp_end_index - lrp_start_index

        lrp_before = df_road.iloc[lrp_start_index - 1]
        lrp_after = df_road.iloc[lrp_end_index]

        LAT_interval = (lrp_after.LAT - lrp_before.LAT) / (lrp_nr + 1)
        LON_interval = (lrp_after.LON - lrp_before.LON) / (lrp_nr + 1)

        for j in range(lrp_nr):
            df_road.at[lrp_start_index + j, 'LAT'] = lrp_before.LAT + LAT_interval * (j+1)
            df_road.at[lrp_start_index + j, 'LON'] = lrp_before.LON + LON_interval * (j+1)

            lrp_changed_index.append(lrp_start_index + j)

    return df_road

df_road_new2 = correct_lrps_off_rd_2(df_road_new.copy(), lrp_off_rd)
lrp_changed_index = list(set(lrp_changed_index))

lrp_changed_index.sort()

print(lrp_changed_index)

plot_rd(road_name, df_road)
plot_rd(road_name, df_road_new2)
