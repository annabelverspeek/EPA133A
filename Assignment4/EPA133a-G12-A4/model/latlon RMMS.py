#This code creates one dataframe which contains all roads and lrps from the
# RMMS file as they are currently all separate files. It does this by creating a
# for loop which runs over all the files in RMMS and picks out the files which have
# .lrps.htm in the name as these are the files we are interested in.
# It then saves it as a csv file called combined_lrps.csv to use for further analysis.

import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

path = 'RMMS'
files = [f for f in os.listdir(path) if f.endswith('.lrps.htm')]
dfs = []

#Loop through each file in RMMS
for file in files:
    tables = pd.read_html(os.path.join(path, file))

    df = pd.concat(tables)

    df = df.iloc[9:].reset_index(drop=True)

    df.columns = df.iloc[0]

    df = df.iloc[1:].reset_index(drop=True)

    df = df.iloc[:, 1:-1]

    #Add new column for road number
    road_number = file.split('.')[0]
    df['road_number'] = road_number

    dfs.append(df)

combined_df = pd.concat(dfs, ignore_index=True)
combined_df.to_csv('combined_lrps.csv', index=False)

#Check the traffic dataframe
traffic_df = pd.read_csv('traffic.csv')
traffic_df.head()

#Renaming columns so it is more clear what data they represent.
traffic_df = traffic_df.rename(columns = { 'LRP':'LRP Start', 'Offset': 'Offset Start',
                                           'Chainage':'Chainage Start', 'LRP.1':'LRP End',
                                           'Offset.1': 'Offset End', 'Chainage.1':'Chainage End'})
print(traffic_df.shape)

# Combining the different dataframes into one so we have the lat/lon values combined with the AADT values
# so we can calculate the different economic values for the road parts.
latlonload = pd.merge(traffic_df, combined_df, left_on=['LRP Start','road'], right_on=['LRP No', 'road_number'] )

#When merging we got 3 rows of each entry, we have dropped the duplicates below to ensure we do not get double entries.
latlonload = latlonload.drop_duplicates()

#To calculate the economic value of a roadpart, we have to assign economic value to different vehicle types.
# Afterwards we will multiply these values with the amount of sightings on each road
# to compute the economic value of a road. The logic behind the values is that for example
# trucks are able to carry a lot of goods, busses a lot of people and smaller vehicles are more
# individual focussed, hence the smaller economic impact.
# It should be noted that these are all estimates as we were unable to find research on the
# marginal economic impact of these vehicle types. Furthermore this code drops all the 'NS' columns
# which do not contain any data.
# The is_float definition is used to ensure that we can multiply the columns so they do not given an error.

economic_value_vehicles = {'Heavy Truck':10, 'Medium Truck': 8, 'Small Truck':7, 'Large Bus':7, 'Medium Bus':6,
                           'Micro Bus':5, 'Utility':3, 'Car':3, 'Auto Rickshaw':2, 'Motor Cycle': 1,
                           'Bi-Cycle':0.5, 'Cycle Rickshaw':1, 'Cart':1}

latlonload = latlonload[~latlonload.apply(lambda row: (row == 'NS').any(), axis=1)]

economic_df = latlonload.loc[:, 'Heavy Truck':'Cart']

def is_float(x):
    try:
        float(x)
        return True
    except ValueError:
        return False

for col in economic_df.columns:
    non_numeric_values = economic_df[col][~economic_df[col].apply(is_float)]
    if not non_numeric_values.empty:
        print(f"Non-numeric values in column '{col}':")
        print(non_numeric_values)

# Converting values to floats to ensure no errors occur due to wrong type data,
# afterwards a new column is appended containing the economic value of a road.
economic_df = economic_df.astype(float)

latlonload['EVV'] = (
    economic_df.apply(lambda row: sum(row[col] * economic_value_vehicles[col] for col in economic_df.columns
                                                      if col in economic_value_vehicles), axis=1))

#renaming the column because of a spelling error
latlonload = latlonload.rename(columns={'Longitued Decimal':'Longitude Decimal'})

#Checking the EVV distribution to check what the vmax should be for good visualisation of the roads.
# This seems to be +- 55000 as this is the 75th percentile.
latlonload.describe()

# Loading the shapefiles from the roads and waterways to display them in our map
# together with the EVV values of the roads. This will give us an understanding of economically important roads.
# The rivers are used for sense of where the roads are as OSM and other ways did not give the desired backgrounds.
# One point with lat/lon 0/0 was removed as this was cause the map to fail loading.

roads = gpd.read_file("osm/roads.shp")
waterways = gpd.read_file("osm/waterways.shp")

latlonload['Latitude Decimal'] = pd.to_numeric(latlonload['Latitude Decimal'], errors='coerce')
latlonload['Longitude Decimal'] = pd.to_numeric(latlonload['Longitude Decimal'], errors='coerce')

tolerance = 0.01
latlonload = latlonload[
    (latlonload['Latitude Decimal'].abs() > tolerance) &
    (latlonload['Longitude Decimal'].abs() > tolerance)
]

gdf = gpd.GeoDataFrame(latlonload, geometry=gpd.points_from_xy(latlonload['Longitude Decimal'],
                                                               latlonload['Latitude Decimal']))
cmap = LinearSegmentedColormap.from_list('evv', ['#0066ff', '#ffffff', '#ff0000'])
ax = roads.plot(color='white', edgecolor='black', figsize=(10, 6), linewidth=0.5)
waterways.plot(ax=ax, color='lightblue', linewidth=0.5)
gdf.plot(ax=ax, marker='o', markersize=3, column='EVV', cmap=cmap, legend=True, vmin=0, vmax=55000)

plt.title('Economic Value of Roads')
plt.show()

# saving the dataframe for further use
latlonload.to_csv('latlonloads.csv')

# Sort the DataFrame based on 'EVV' column in descending order to show the top 10 EVV contributing road parts.
sorted_latlonload = latlonload.sort_values('EVV', ascending=False)
top_n = 10
top_n_df = sorted_latlonload.head(top_n)
road_names = top_n_df['name']
evv_values = top_n_df['EVV']

plt.figure(figsize=(10, 6))
plt.barh(road_names, evv_values, color='red')
plt.xlabel('Economic Value of Roads')
plt.ylabel('Road Names')
plt.title(f'Top {top_n} Roads by Economic Value')
plt.gca().invert_yaxis()  # Invert y-axis to display the highest-ranking road at the top
plt.show()

# Get the top 100 roads and afterwards plotting the top 10 to show contrast in road contributions.
top_100_df = sorted_latlonload.head(100)

top_10_within_100 = top_100_df.head(10)

plt.figure(figsize=(12, 8))
plt.barh(range(len(top_100_df)), top_100_df['EVV'], color='skyblue', label='Top 100 Contributors')
plt.barh(range(len(top_10_within_100)), top_10_within_100['EVV'], color='red', label='Top 10 within Top 100')

plt.xlabel('Economic Value of Roads')
plt.ylabel('Rank')
plt.title('Comparison of Top 10 within Top 100 and Other Contributors by Economic Value')
plt.legend()
plt.gca().invert_yaxis()  # Invert y-axis to display the highest-ranking road at the top
plt.show()

#Saving the top100 dataframe for further analysis
top_100_df['name'].to_csv('../data/processed/Criticality100.csv', index=False)

#Here we calculate the partial contributions to the total EVV of each vehicle, this gives insight as to what vehicles contribute most to the economic values of the roads.
latlonload = latlonload.apply(pd.to_numeric, errors='coerce')

total_evv_per_vehicle = {}
for vehicle, value in economic_value_vehicles.items():
    total_evv_per_vehicle[vehicle] = latlonload[vehicle].sum() * value

df_total_evv_per_vehicle = pd.DataFrame(total_evv_per_vehicle.items(), columns=['Vehicle', 'Total EVV'])

total_evv = df_total_evv_per_vehicle['Total EVV'].sum()

df_total_evv_per_vehicle['Percentage'] = (df_total_evv_per_vehicle['Total EVV'] / total_evv) * 100

plt.figure(figsize=(10, 6))
plt.bar(df_total_evv_per_vehicle['Vehicle'], df_total_evv_per_vehicle['Percentage'], color='skyblue')
plt.xlabel('Vehicle Type')
plt.ylabel('Percentage of Total EVV')
plt.title('Contribution of Vehicle Types to Total EVV')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

