import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
# Assuming your data is stored in a DataFrame named 'df'

file = 'BMMS_overview.xlsx'

df_bridges = pd.read_excel(file)
df_bridges['lon'] = df_bridges['lon'].astype(str).str.replace(',', '.').astype(float)
print(df_bridges.dtypes)


df_bridges.head()

df_bridges.shape

#reading the excel file
dtypes = {'LRP': str, 'LAT': float, 'LON': float}
df_roads = pd.read_csv("roads_cleaned.tsv", delimiter="\t", dtype=dtypes)


#bridges printen:
def plot_bridges(road_name, df_bridges):
    df_road = df_bridges[df_bridges['road'] == road_name]
    print(df_road.head())
    plt.figure(figsize=(10, 6))
    df_road['lon'] = df_road['lon']#.astype(float)
    df_road['lat'] = df_road['lat'].astype(float)
    plt.plot(df_road['lon'], df_road['lat'], marker='o', linestyle='-')
    plt.title(f"{road_name} Bridges")
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.grid(True)
    plt.show()



#Outlier definieren:
def calc_lrp_distance (df_rd_lrp):
    df_lrp_before = df_rd_lrp.shift()

    lrp_dist = np.sqrt((df_lrp_before['lat'] - df_rd_lrp['lat']) ** 2 + (df_lrp_before['lon'] - df_rd_lrp['lon']) ** 2)

    return lrp_dist


#outliers op zn plek zetten:
    #Door te vergelijken of de LRP naam ook in de Roads df voorkomt, zo ja dan neemt de brug die lon en lat over.
def correct_lon_lat(road, df_bridges, roads_df_dict):
    # Iterate over each row in road_bridges_df

 #   bridges_road = df_bridges[df_bridges['road']==road]
    if road in roads_df_dict:
        road_road = roads_df_dict[road]
        #print("road list", road_road['LRP'])
        for index, row in df_bridges[df_bridges['road']==road].iterrows():
            # Get the LRPName from the current row
            lrp_name = row['LRPName'].strip()
            #print("per lrp", lrp_name)
            # Check if the LRPName exists in df_road
            if lrp_name in road_road['LRP'].astype(str).values:
                lrp_name = str(lrp_name)


            # Get the corresponding row from df_road where LRPName matches
                corresponding_row = road_road[road_road['LRP'] == lrp_name].iloc[0]

            # Update the longitude and latitude values in road_bridges_df

                df_bridges.loc[index, 'lat'] = corresponding_row['LAT']
                df_bridges.loc[index, 'lon'] = corresponding_row['LON']


    return df_bridges


def lat_long_around(df):
    for idx, row in df.iterrows():
        lat = row['lat']
        long = row['lon']
        if lat > 28 and long < 88:
            # Swap latitude and longitude
            df.loc[idx, 'lat'], df.loc[idx, 'lon'] = long, lat
    return df  # Return the modified DataFrame

def delete_duplicates(df):
    duplicate_coordinates = df[df.duplicated(['lat', 'lon'], keep=False)]

    if not duplicate_coordinates.empty:
        for index, row in duplicate_coordinates.iterrows():
            df.loc[index,:] = np.nan
            #print("duplicates deleted: ", row)
    else: print("No duplicate coordinates found.")
    return df

roads_df_dict = {}
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
    roads_df_dict[road_name] = df_road




lat_long_around(df_bridges)

delete_duplicates(df_bridges)

unique_roads = df_bridges['road'].unique()
for road in unique_roads:
    correct_lon_lat(road,df_bridges , roads_df_dict)

#put lon and lat in correct order to create a constant road
df_bridges = df_bridges.sort_values(by='road')
df_bridges = df_bridges.groupby('road').apply(lambda x: x.sort_values(by=['lat', 'lon']))

df_bridges.reset_index(drop=True, inplace=True)

plot_bridges('N1', df_bridges)

print(df_bridges.head())
# df_bridges['LAT'] = df_bridges['LAT'].astype(float)
# # df_bridges['LON'] = df_bridges['LON'].astype(float)
print('second', df_bridges.dtypes)


df_bridges.to_excel('bridges_cleaned.xlsx', index=False)
