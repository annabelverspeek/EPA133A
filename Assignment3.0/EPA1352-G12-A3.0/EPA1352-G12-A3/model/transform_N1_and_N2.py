import pandas as pd
import numpy as np

# Step 1: filtering on rows that are longer than 25 km.
# Import the data of the overview of all roads
Overview_file = '_overview.xlsx'
Overview = pd.read_excel(Overview_file)

# we are starting with filtering which roads are longer than 25 km
filtered_df_length = Overview[Overview['length'] >= 25]

# Read the tsv file of roads that contain all lrps of the road
tsv_file = '_roads.tsv'
df_roads = pd.read_csv(tsv_file, sep='\t')
#print(df_roads.head())

#Step 2: defining the sources and sinks of all roads in Bangladesh.
df_sourcesinks = pd.DataFrame(columns=['road', 'model_type', 'name', 'lat', 'lon'])

# we create an empty list to store the sources and sinks
data = []

counter = 1

# Iterate over each unique road
for road in df_roads['road'].unique():
    road_data = df_roads[df_roads['road'] == road]

    # Extract the first LRP from the first row with the data needed to be the same format as the demo file
    road_row = road_data.iloc[0]
    data.append({
        'road': road_row['road'],
        'model_type': 'sourcesink',
        'name': f'SoSi{counter}',
        'lat': road_row['lat1'],
        'lon': road_row['lon1']
    })
    counter += 1

    # we select the last column of each road. Because not every road has the same amount of LRPs,
    # we find the last column that contains a value for each road. This is being found by skipping 3 steps every time to find the lon value
    last_col_id = len(road_row)-1
    i = last_col_id
    for i in range(last_col_id, 0, -3):
        if pd.notnull(road_row[i]) and pd.notnull(road_row[i-1]):        # THEN , IF NT NONE:
            data.append({
                'road': road_row['road'],
                'model_type': 'sourcesink',
                'name': f'SoSi{counter}',
                'lat': road_row[i-1],
                'lon': road_row[i]
            })
            counter += 1
            break

# we create a DataFrame from collected data
df_sourcesinks = pd.DataFrame(data)
#print(df_sourcesinks.head(30))


#the dataframe is stored as csv file
csv_file_sourcesink = 'sourcesink_roads.csv'
df_sourcesinks.to_csv(csv_file_sourcesink, index=False)
#print(f"CSV file '{csv_file_sourcesink}' has been created successfully.")

#Step 3: we scrape data from html files with the lrps of the roads to find the intersections of roads
# import the html file with the road descriptions. Everything is done for N1 and N2
file_path_N1 = 'N1.lrps.htm'
file_path_N2 = 'N2.lrps.htm'
df_list_N1 = pd.read_html(file_path_N1)
df_list_N2 = pd.read_html(file_path_N2)
# create a dataframe from the html file, the table is the fourth element in the html list
df_N1 = df_list_N1[4]
df_N2 = df_list_N2[4]

# cleaning the dataframe so that the correct rows are taken into account
df_N1 = df_N1.drop(index=0, columns=[df_N1.columns[0], df_N1.columns[-1]])
df_N1.columns = df_N1.iloc[0]
df_N1 = df_N1.drop(index=1)
filtered_df_N1 = df_N1[df_N1['LRP TYPE'].str.contains('Cross Road|Side Road')]

df_N2 = df_N2.drop(index=0, columns=[df_N2.columns[0], df_N2.columns[-1]])
df_N2.columns = df_N2.iloc[0]
df_N2 = df_N2.drop(index=1)
filtered_df_N2 = df_N2[df_N2['LRP TYPE'].str.contains('Cross Road|Side Road')]

# Initialize an empty list to store the filtered rows
filtered_rows = []

# Iterate over each row in filtered_length for N1.
for index, row in filtered_df_length.iterrows():
    road_name = row['road']
    if road_name.startswith('N'):
        # Exclude "N1" road name
        if road_name != "N1":
            # Filter rows in filtered_df where the "Description" column contains the road name
            matching_rows_N1 = filtered_df_N1[filtered_df_N1['Description'].str.contains(road_name, case=False)].copy()
            # Add a new column "road name" with the road name for each matching row
            matching_rows_N1['road name'] = road_name
            # Append the matching rows to the list
            filtered_rows.append(matching_rows_N1)

# Iterate over each row in filtered_length for N2.
for index, row in filtered_df_length.iterrows():
    road_name = row['road']
    if road_name.startswith('N'):
        # Exclude "N1" road name
        if road_name != "N2":
            # Filter rows in filtered_df where the "Description" column contains the road name
            matching_rows_N2 = filtered_df_N2[filtered_df_N2['Description'].str.contains(road_name, case=False)].copy()
            # Add a new column "road name" with the road name for each matching row
            matching_rows_N2['road name'] = road_name
            # Append the matching rows to the list
            filtered_rows.append(matching_rows_N2)


# Define a function to add "N1" or "N2" to the road name
def add_road_name(row):
    if row.name < 5:
        return 'N1'
    else:
        return 'N2'

# Apply the function to create the new column
filtered_df['road_name2'] = filtered_df.apply(lambda row: add_road_name(row), axis=1)

# Concatenate the filtered rows into a single DataFrame
filtered_df = pd.concat(filtered_rows, ignore_index=True)

# Get unique road names from filtered_df
filtered_road_names = filtered_df['road name'].unique()

#part of step 2
# Filter df_sourcesinks to contain only roads present in filtered_df
filtered_sourcesinks = df_sourcesinks[df_sourcesinks['road'].isin(filtered_road_names)]

filtered_sourcesinks['name'] = ['SoSi' + str(i) for i in range(1, len(filtered_sourcesinks) + 1)]

# #make csv of filtered sources and sinks
# csv_file_sourcesink_filtered = 'sourcesink_roads_filtered.csv'
# filtered_sourcesinks.to_csv(csv_file_sourcesink_filtered, index=False)
# print(f"CSV file '{csv_file_sourcesink_filtered}' has been created successfully.")

#print(filtered_sourcesinks.head(16))

############################
##MERGE TO FINAL DATAFRAME##
############################

# the cleaned bridges dataset is imported
excel_file_bridge = 'BMMS_overview.xlsx'
df_bridge = pd.read_excel(excel_file_bridge)

# a new dataframe is created to store the filtered bridges
filtered_bridges = pd.DataFrame(columns=['road', 'type', 'condition', 'name', 'lat', 'lon', 'length','chainage'])

# Filter data for the roads found in filtered_sourcesinks.
for road_name in filtered_sourcesinks['road'].unique():
    bridges_to_filter = df_bridge[df_bridge['road'] == road_name]
    filtered_bridges = pd.concat([filtered_bridges, bridges_to_filter], ignore_index=True)

filtered_bridges = filtered_bridges[['road', 'type', 'condition', 'name', 'lat', 'lon', 'length', 'chainage']]


# removing double values for the bridges. Same latitudes and longitudes measured twice. Values with shortest length remain.
# the duplicates are removed so lengths of bridges are not counted double.
filtered_bridges = filtered_bridges.sort_values('length')
filtered_bridges = filtered_bridges.drop_duplicates(subset=['lat', 'lon'], keep='last')
filtered_bridges = filtered_bridges.sort_values(by=['road','chainage'])

filtered_bridges = filtered_bridges[['road', 'type', 'condition', 'name', 'lat', 'lon', 'length']]

# csv_file_bridges = 'bridges.csv'
# filtered_bridges.to_csv(csv_file_bridges, index=False)
# print(f"CSV file '{csv_file_bridges}' has been created successfully.")

columns = ['road', 'type', 'condition', 'name', 'lat', 'lon', 'length']
filtered_sourcesinks = filtered_sourcesinks.rename(columns={'model_type':'type'})
filtered_sourcesinks = filtered_sourcesinks.reindex(columns=columns)

df_merge = pd.concat([filtered_bridges, filtered_sourcesinks], ignore_index=True)
df_merge = df_merge.sort_values(by=['road','lat'])
print(df_merge.head(500))

csv_file_merged = 'merged.csv'
df_merge.to_csv(csv_file_merged, index=False)
print(f"CSV file '{csv_file_merged}' has been created successfully.")

#### GIVING IDS TO EVERY BRIDGE + LINK #####
#### TO ADD LATER ####
# # print(df_bridge)
# # an empty list is created for data. This list will function as list to contain the information on the source, the bridges, the links and the sink of the analysis.
# data = []
#
# # Initializing the variables. A counter is initialized so every source, bridge, link or sink has a unique id.
# id_counter = 1000000
# bridge_counter = 1  # Initialize bridge counter
# link_chainage = 0    # Initialize link chainage
#
#
# # append source. As source the beginning of the road in Dhaka has been defined with specified latitudes and longitudes:
# data.append({'road': 'N1', 'id': id_counter, 'model_type': 'source', 'name': 'source', 'lat': 23.7060278, 'lon': 90.443333, 'length': 0, 'condition': np.nan})
# id_counter += 1  # Otherwise similar id for the source and the first bridge!
#
# for index, row in df_bridge.iterrows():
#     # Extract required attributes
#     road = row['road']
#     name = row['name']
#     lat = row['lat']
#     lon = row['lon']
#     length = row['length']
#     condition = row['condition']
#
#     chainage_str = str(row['chainage'])  # Convert chainage to string
#     # we do the chainage times 1000 to go from meters to kilometers
#     chainage = (float(chainage_str.replace(',', '.')))*1000  # Replace commas and convert to float
#
#     # Append links
#     if index > 0:
#         link_length = chainage - link_chainage  # Calculate the length of the link
#         data.append(
#             {'road': road, 'id': id_counter, 'model_type': 'link', 'name': f'link {index}', 'lat': lat,
#              'lon': lon, 'length': link_length, 'condition': np.nan})
#         id_counter += 1
#         link_chainage = chainage  # Update link chainage after calculating link_length
#
#     # Append bridges. All types of bridges are taken along
#     if row['type'] == 'PC Girder Bridge' or row['type'] == 'Box Culvert' or row['type'] == 'PC Box' or row['type'] == 'RCC Girder Bridge' or row['type'] == 'Slab Culvert' or row['type'] == 'Steel Beam & RCC Slab' or row['type'] == 'Arch Masonry' or row['type'] == 'RCC Bridge' or row['type'] == 'Baily with Steel Deck' or row['type'] == 'Truss with Steel Deck' or row['type'] == 'Truss with RCC Slab' or row['type'] == 'Baily with Timber Deck' or row['type'] == 'Pipe Culvert':  # Check if it's a bridge
#         data.append({'road': road, 'id': id_counter, 'model_type': 'bridge', 'name': name, 'lat': lat, 'lon': lon, 'length': length, 'condition': condition})
#         id_counter += 1
#         bridge_counter += 1  # Increment bridge counter
#
#     # if the latitude of the bridges pass the latitude of the sink, the adding of bridges to data is stopped.
#     if row['lat'] < 22.3314716:
#         break
#
# # append sink to data
# data.append({'road': 'N1', 'id': id_counter, 'model_type': 'sink', 'name': 'sink', 'lat': 22.3314716, 'lon': 91.8515556,
#              'length': 0, 'condition': np.nan})
# id_counter += 1
#
# # Convert the list of dictionaries into a DataFrame
# new_df_bridge = pd.DataFrame(data)
# # print(new_df_bridge.head(10))
#
#
# # Write the transformed data into a new CSV file
# csv_file_path_N1 = 'transformed_data_N1.csv'
# new_df_bridge.to_csv(csv_file_path_N1, index=False)
# print(f"CSV file '{csv_file_path_N1}' has been created successfully.")