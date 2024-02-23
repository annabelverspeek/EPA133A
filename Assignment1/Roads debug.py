#importeren van functies
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

#reading the excel file
dtypes = {'LRP': str, 'LAT': float, 'LON': float}
df_roads = pd.read_csv("_roads copy.tsv", delimiter="\t", dtype=dtypes)
print(df_roads.dtypes)
df_roads_new = df_roads.copy()
# df_roads_new.set_index('road', inplace=True)
# df_roads.set_index('road', inplace=True)

#function to plot the roads
def plot_rd(road_name, df_roads):
    plt.figure(figsize=(10, 6))
    plt.plot(df_road['LON'], df_road['LAT'], marker='o', linestyle='-')
    plt.title(road_name)
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.grid(True)
    plt.show()

def lat_long_around(df):
    for idx, row in df.iterrows():
        lat = row['lat']
        long = row['lon']
        if lat > 27 and long < 87:
            # Swap latitude and longitude
            row['lat'], row['lon'] = long, lat
    return df  # Return the modified DataFrame

#first the functions are defined that calculate the distances to LRPs, at the end these functions are called and plotted
#this function calculates the distance between LON and LAT
def calc_lrp_distance (df_rd_lrp):
    df_lrp_before = df_rd_lrp.shift()

    lrp_dist = np.sqrt((df_lrp_before.LAT- df_rd_lrp.LAT)**2 + (df_lrp_before.LON-df_rd_lrp.LON)**2)

    return lrp_dist

#this function finds LRPs that have a longer distance between LON and LATS than the threshold. Making the threshold way bigger/smaller, does not remove the final outliers
def get_lrps_off_rd (lrp_dist):
    threshold = lrp_dist.quantile(0.8)*20

    lrp_off_rd = lrp_dist.loc[(lrp_dist > threshold) & (lrp_dist.shift(-1) > threshold)]
    return lrp_off_rd

def correct_lrps_off_rd(df_road, lrp_off_rd):
    df_road.loc[lrp_off_rd.index, 'LAT'] = (df_road['LAT'].shift().loc[lrp_off_rd.index] + df_road['LAT'].shift(-1).loc[lrp_off_rd.index]) / 2
    df_road.loc[lrp_off_rd.index, 'LON'] = (df_road['LON'].shift().loc[lrp_off_rd.index] + df_road['LON'].shift(-1).loc[lrp_off_rd.index]) / 2

    return df_road

#we perform a second round, to also remove consecutive outliers. In the example of N1, still one outlier remains.
def get_lrp_off_rd_2(lrp_dist):
    threshold = lrp_dist.quantile(0.8)*20

    lrp_off_rd = lrp_dist.loc[(lrp_dist>threshold)]

    return lrp_off_rd

def correct_lrps_off_rd_2(df_road, lrp_off_rd):
    lrp_changed_index = []
    for i in range(0, len(lrp_off_rd.index) - 1, 2):  # Adjust range to ensure pairs of indices
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

road_data_list = []

#making sure the columns are rows. And that every row is a road. The functions are performed for every road in the roads dataframe
for road in df_roads.itertuples(index=False):
    road_name = road[0]
    #print(road_name)

    data = []
    for i in range(1, len(road), 3):
        lrp = [road[i], road[i + 1], road[i + 2]]
        # Assuming pd is already imported
        if pd.isna(road[i]):
            break
        else:
            data.append(lrp)

    df_road = pd.DataFrame(data, columns=['LRP', 'LAT', 'LON'])
    df_road['LAT'] = df_road['LAT'].astype(float)
    df_road['LON'] = df_road['LON'].astype(float)
    #print(df_road)
    #print(df_road)
    # for col in ['LAT', 'LON']:
    #     df_road[col] = pd.to_numeric(df_road[col], errors='coerce').fillna(0)
#the functions are called for every road so the outliers are removed

    lrp_dist = calc_lrp_distance(df_road)
    lrp_off_rd = get_lrps_off_rd(lrp_dist)
    df_road_new = correct_lrps_off_rd (df_road, lrp_off_rd)
    df_road_new2 = correct_lrps_off_rd_2 (df_road_new, lrp_off_rd)
    # lrp_start_index = list(set(lrp_chdf_road_new2anged_index))
    # lrp_changed_index.sort()
    # print(lrp_start_index)
    new_row = ', '.join(df_road_new2.astype(str).values.ravel())
    new_row = new_row.split(", ")
    new_row = pd.DataFrame(new_row)
    #print(new_row)
    df_roads_new.iloc[1,len(new_row)] = new_row

print(df_roads_new.head())


    # Plotting the corrected road
#removing the # will run this line of code and plot all the roads --> pycharm breaks because there are too many roads to plot
    #plot_rd(road_name, df_road_new2)

#print(df_road_new2)
import pandas as pd

# Create a new row with NaN values to match the original df
new_row = pd.DataFrame([pd.Series([None] * len(df_roads_new.columns))], columns=df_roads_new.columns)

df_roads_new = pd.concat([new_row, df_roads_new], ignore_index=True)

# Display the DataFrame with the new row at the top

print(df_roads_new.dtypes)


df_roads_new.to_csv('roads_cleaned.tsv', sep='\t', index=False)
