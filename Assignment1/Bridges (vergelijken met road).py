import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
# Assuming your data is stored in a DataFrame named 'df'

file = 'BMMS_overview.xlsx'

df_bridges = pd.read_excel(file)


df_bridges.head()

df_bridges.shape

#reading the excel file
# dtypes = {'LRP': str, 'LAT': float, 'LON': float}
# df_roads = pd.read_csv("_roads copy.tsv", delimiter="\t", dtype=dtypes)

# Group the DataFrame by road
#grouped_by_road = df.groupby('road')


# Assuming your data is stored in a DataFrame named 'df'

# Get the unique road names
unique_roads = df_bridges['road'].unique()

# Create an empty dictionary to store DataFrames for each road
bridges_per_road_dfs = {}

# Iterate over unique road names
for road_name in unique_roads:
    # Filter the DataFrame for the current road and select desired columns
    road_df = df_bridges[df_bridges['road'] == road_name][['LRPName', 'lat', 'lon']]
    # Store the DataFrame in the dictionary with the road name as key
    bridges_per_road_dfs[road_name] = road_df


print(bridges_per_road_dfs['N1'])


#bridges printen:
def plot_bridges(road_name, bridges_per_road_dfs):
    df_road = bridges_per_road_dfs.get(road_name)
    plt.figure(figsize=(10, 6))
    plt.plot(df_road['lon'], df_road['lat'], marker='o', linestyle='-')
    plt.title(f"{road_name} Bridges")
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.grid(True)
    plt.show()

plot_bridges('N1', bridges_per_road_dfs)

#Outlier definieren:
def calc_lrp_distance (df_rd_lrp):
    df_lrp_before = df_rd_lrp.shift()

    lrp_dist = np.sqrt((df_lrp_before['lat'] - df_rd_lrp['lat']) ** 2 + (df_lrp_before['lon'] - df_rd_lrp['lon']) ** 2)

    return lrp_dist

def get_lrps_off_rd (lrp_dist):
    threshold = lrp_dist.quantile(0.8)*20

    lrp_off_rd = lrp_dist.loc[(lrp_dist > threshold) & (lrp_dist.shift(-1) > threshold)]
    return lrp_off_rd

lrp_dist = calc_lrp_distance(bridges_per_road_dfs['N1'])
lrp_off_rd = get_lrps_off_rd(lrp_dist)

# Print LRPs that are off the road and their corresponding details
print('Off road LRPs:')
print(bridges_per_road_dfs['N1'].loc[lrp_off_rd.index])

#outliers op zn plek zetten:
    #Door te vergelijken of de LRP naam ook in de Roads df voorkomt, zo ja dan neemt de brug die lon en lat over.
def correct_lon_lat(bridges_per_road_dfs, df_road):
    # Iterate over each row in road_bridges_df
    for index, row in bridges_per_road_dfs.iterrows():
        # Get the LRPName from the current row
        lrp_name = row['LRPName']

        # Check if the LRPName exists in df_road
        if lrp_name in df_road['LRPName'].values:
            # Get the corresponding row from df_road where LRPName matches
            corresponding_row = df_road[df_road['LRPName'] == lrp_name].iloc[0]

            # Update the longitude and latitude values in road_bridges_df
            bridges_per_road_dfs.at[index, 'lon'] = corresponding_row['lon']
            bridges_per_road_dfs.at[index, 'lat'] = corresponding_row['lat']


# Call the function to correct lon/lat values for road 'N1'
correct_lon_lat(road_bridges_dfs['N1'], df_road)

#Funtie als er nog outliers over zijn: Gemiddelde nemen van bridge ervoor en bridge erna??