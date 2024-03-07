# importing the needed libraries
import pandas as pd
import numpy as np

# the cleaned bridges dataset is imported
excel_file_bridge = 'BMMS_overview2.xlsx'
df_bridge = pd.read_excel(excel_file_bridge)
# only the columns in the bridge dataset are imported that align with the demofile.
# As extra, the condition of the bridges is added. The column condition is also added in the run methods to make sure this column is taken along.
df_bridge = df_bridge[['road', 'name', 'lat', 'lon', 'length', 'condition', 'chainage', 'type']]

# Filter data for road 'N1'. Change to other road if you want to research other roads
df_bridge = df_bridge[df_bridge['road'] == 'N1']

# removing double values for the bridges. Same latitudes and longitudes measured twice. Values with shortest length remain.
# the duplicates are removed so lengths of bridges are not counted double.
df_bridge = df_bridge.sort_values('length')
df_bridge = df_bridge.drop_duplicates(subset=['lat', 'lon'], keep='last')
df_bridge = df_bridge[['road', 'name', 'lat', 'lon', 'length', 'condition', 'chainage', 'type']]
df_bridge = df_bridge.sort_values('chainage')

# print(df_bridge)
# an empty list is created for data. This list will function as list to contain the information on the source, the bridges, the links and the sink of the analysis.
data = []

# Initializing the variables. A counter is initialized so every source, bridge, link or sink has a unique id.
id_counter = 1000000
bridge_counter = 1  # Initialize bridge counter
link_chainage = 0    # Initialize link chainage


# append source. As source the beginning of the road in Dhaka has been defined with specified latitudes and longitudes:
data.append({'road': 'N1', 'id': id_counter, 'model_type': 'source', 'name': 'source', 'lat': 23.7060278, 'lon': 90.443333, 'length': 0, 'condition': np.nan})
id_counter += 1  # Otherwise similar id for the source and the first bridge!

for index, row in df_bridge.iterrows():
    # Extract required attributes
    road = row['road']
    name = row['name']
    lat = row['lat']
    lon = row['lon']
    length = row['length']
    condition = row['condition']

    chainage_str = str(row['chainage'])  # Convert chainage to string
    # we do the chainage times 1000 to go from meters to kilometers
    chainage = (float(chainage_str.replace(',', '.')))*1000  # Replace commas and convert to float

    # Append links
    if index > 0:
        link_length = chainage - link_chainage  # Calculate the length of the link
        data.append(
            {'road': road, 'id': id_counter, 'model_type': 'link', 'name': f'link {index}', 'lat': lat,
             'lon': lon, 'length': link_length, 'condition': np.nan})
        id_counter += 1
        link_chainage = chainage  # Update link chainage after calculating link_length

    # Append bridges. All types of bridges are taken along
    if row['type'] == 'PC Girder Bridge' or row['type'] == 'Box Culvert' or row['type'] == 'PC Box' or row['type'] == 'RCC Girder Bridge' or row['type'] == 'Slab Culvert' or row['type'] == 'Steel Beam & RCC Slab' or row['type'] == 'Arch Masonry' or row['type'] == 'RCC Bridge' or row['type'] == 'Baily with Steel Deck' or row['type'] == 'Truss with Steel Deck' or row['type'] == 'Truss with RCC Slab' or row['type'] == 'Baily with Timber Deck' or row['type'] == 'Pipe Culvert':  # Check if it's a bridge
        bridge_name = f"bridge {bridge_counter}"  # Use generic name for bridge
        data.append({'road': road, 'id': id_counter, 'model_type': 'bridge', 'name': bridge_name, 'lat': lat, 'lon': lon, 'length': length, 'condition': condition})
        id_counter += 1
        bridge_counter += 1  # Increment bridge counter

    # if the latitude of the bridges pass the latitude of the sink, the adding of bridges to data is stopped.
    if row['lat'] < 22.3314716:
        break

# append sink to data
data.append({'road': 'N1', 'id': id_counter, 'model_type': 'sink', 'name': 'sink', 'lat': 22.3314716, 'lon': 91.8515556,
             'length': 0, 'condition': np.nan})
id_counter += 1

# Convert the list of dictionaries into a DataFrame
new_df_bridge = pd.DataFrame(data)
# print(new_df_bridge.head(10))


# Write the transformed data into a new CSV file
csv_file_path_N1 = 'transformed_data_N1.csv'
new_df_bridge.to_csv(csv_file_path_N1, index=False)
print(f"CSV file '{csv_file_path_N1}' has been created successfully.")
