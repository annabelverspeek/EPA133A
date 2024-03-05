import pandas as pd
import numpy as np

excel_file_bridge = 'BMMS_overview2.xlsx'
df_bridge = pd.read_excel(excel_file_bridge)
df_bridge = df_bridge[['road','name','lat','lon','length', 'condition','chainage','type']]

# import the data from _roads3.csv
excel_file_road = '_roads3_2.csv'
df_roads = pd.read_csv(excel_file_road)
df_roads = df_roads[['road','name','lat','lon']]

# Filter data for road 'N1'
df_bridge = df_bridge[df_bridge['road'] == 'N1']
df_roads = df_roads[df_roads['road'] == 'N1']

#removing double values for the bridges. Same latitudes and longitudes measured twice. Values with shortest length remain.
df_bridge = df_bridge.sort_values('length')
df_bridge = df_bridge.drop_duplicates(subset=['lat', 'lon'], keep = 'last')
df_bridge = df_bridge[['road','name','lat','lon','length', 'condition','chainage','type']]
df_bridge = df_bridge.sort_values('chainage')

#print(df_bridge)

data = []

# Initializing the variables
id_counter = 1000000
link_chainage = 0

bridge_counter = 1  # Initialize bridge counter
link_chainage = 0    # Initialize link chainage

#df_roads.loc[0, "model_type"]="source"
#df_roads.loc[len(df_roads)-1, "model_type"] = "sink"

# append source. As source the beginning of the road in Chittagong has been defined with specified latitudes and longitudes:
data.append({'road': 'N1', 'id': id_counter, 'model_type': 'source', 'name': 'source', 'lat': 22.3314716, 'lon': 91.8515556, 'length': np.nan, 'condition': np.nan})

for index, row in df_bridge.iterrows():
    # Extract required attributes
    road = row['road']
    name = row['name']
    lat = row['lat']
    lon = row['lon']
    length = row['length']
    condition = row['condition']

    chainage_str = str(row['chainage'])  # Convert chainage to string
    chainage = float(chainage_str.replace(',', '.'))  # Replace commas and convert to float

    # Append link
    if index>0:
        link_length = chainage - link_chainage  # Calculate the length of the link
        #print(chainage, link_chainage)
        data.append({'road': road, 'id': id_counter, 'model_type': 'link', 'name': f'link {index}', 'lat': link_chainage, 'lon': link_chainage, 'length': link_length, 'condition': np.nan})
        id_counter += 1
        link_chainage = chainage  # Update link chainage

    # Append bridge
    if row['type'] == 'PC Girder Bridge' or row['type'] == 'Box Culvert' or row['type'] == 'PC Box' or row['type'] == 'RCC Girder Bridge' or row['type'] == 'Slab Culvert' or row['type'] == 'Steel Beam & RCC Slab' or row['type'] == 'Arch Masonry' or row['type'] == 'RCC Bridge' or row['type'] == 'Truss With Timber Deck':  # Check if it's a bridge
        bridge_name = f"bridge {bridge_counter}"  # Use generic name for bridge
        data.append({'road': road, 'id': id_counter, 'model_type': 'bridge', 'name': bridge_name, 'lat': lat, 'lon': lon, 'length': length, 'condition': condition})
        id_counter += 1
        bridge_counter += 1  # Increment bridge counter

# Append sink. The end of the N1 in Dhaka is the sink. Specified latitudes and longitudes.
data.append({'road': 'N1', 'id': id_counter, 'model_type': 'sink', 'name': 'sink', 'lat': 23.7060278, 'lon': 90.443333, 'length': np.nan, 'condition': np.nan})

# Convert the list of dictionaries into a DataFrame
new_df_bridge = pd.DataFrame(data)
#print(new_df_bridge.head(10))


# # Write the transformed data into a new CSV file
# csv_file_path = 'transformed_data.csv'
# new_df_bridge.to_csv(csv_file_path, index=False)
#
# print(f"CSV file '{csv_file_path}' has been created successfully.")

csv_file_path_N1 = 'transformed_data_N1.csv'
new_df_bridge.to_csv(csv_file_path_N1, index=False)
print(f"CSV file '{csv_file_path_N1}' has been created successfully.")
