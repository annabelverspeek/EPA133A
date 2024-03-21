# importing the needed libraries
import pandas as pd
import numpy as np
from scipy.spatial.distance import cdist

#########
##STEP1##
#########
# Step 1: filtering on rows that are longer than 25 km.
# for the filtering on length we use the _overview file
Overview_file = '_overview.xlsx'
Overview = pd.read_excel(Overview_file)

# we are starting with filtering which roads are longer than 25 km
filtered_df_length = Overview[Overview['length'] >= 25]

#########
##STEP2##
#########
# Step 2: we scrape data from html files with the lrps of the roads to find the intersections of roads
# import the html file with the road descriptions. Everything is done for N1 and N2
file_path_N1 = 'N1.lrps.htm'
file_path_N2 = 'N2.lrps.htm'
df_list_N1 = pd.read_html(file_path_N1)
df_list_N2 = pd.read_html(file_path_N2)
# we create a dataframe from the html file, the table is the fourth element in the html list
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
filtered_df_N2 = df_N2[
    df_N2['LRP TYPE'].str.contains('Cross Road|Side Road') | df_N2['Description'].str.contains('Road Start')]

filtered_df_N1['road name2'] = 'N1'
filtered_df_N2['road name2'] = 'N2'

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

# Concatenate the filtered rows into a single DataFrame
filtered_df = pd.concat(filtered_rows, ignore_index=True)

filtered_df = filtered_df.drop_duplicates(subset=['Road Chainage'])
print(filtered_df)
# Filter rows where "road name2" is "N1" and "road name" is "N2" in filtered_df
rows_to_swap = filtered_df[(filtered_df['road name2'] == 'N1') & (filtered_df['road name'] == 'N2')]

# Duplicate the filtered rows and swap "road name" and "road name2"
rows_to_swap_swapped = rows_to_swap.copy()
rows_to_swap_swapped['road name'] = 'N1'
rows_to_swap_swapped['road name2'] = 'N2'

# Concatenate filtered_df with the duplicated and swapped rows
filtered_df_combined = pd.concat([filtered_df, rows_to_swap_swapped], ignore_index=True)

filtered_df_combined.loc[5, 'road name'] = 'N105'
filtered_df_combined.loc[6, 'road name'] = 'N102'

#print(filtered_df_combined)

csv_file_combined = 'combined.csv'
filtered_df_combined.to_csv(csv_file_combined, index=False)

# # Define a function to add "N1" or "N2" to the road name
def add_road_name(row):
    if row.name < 5:
        return 'N1'
    else:
        return 'N2'


# Apply the function to create the new column
filtered_df['road2'] = filtered_df.apply(lambda row: add_road_name(row), axis=1)

# Concatenate the filtered rows into a single DataFrame
filtered_df = pd.concat(filtered_rows, ignore_index=True)
# print(filtered_df.columns)
# Get unique road names from filtered_df
filtered_road_names = filtered_df['road name'].unique()
# print(filtered_road_names)

# making sure the filtered dataframe has the correct columns for the merging later
filtered_df = filtered_df.rename(
    columns={'Latitude Decimal': 'lat', 'Longitued Decimal': 'lon', 'Road Chainage': 'chainage', 'road name': 'road'})
columns = ['road', 'road name2', 'model_type', 'condition', 'name', 'lat', 'lon', 'length', 'chainage']
filtered_df = filtered_df.reindex(columns=columns)
filtered_df = filtered_df.drop_duplicates(subset=['chainage'])
filtered_df['model_type'] = 'intersection'

#########
##STEP3##
#########
# Step 3: we find the sourcesinks for all filtered roads in Bangladesh
# Read the csv file of roads that contain all lrps of the road
csv_file = '_roads3.csv'
df_roads = pd.read_csv(csv_file, sep=',')

# Initialize an empty DataFrame to store the results with the right columns
df_sourcesinks = pd.DataFrame(columns=['road', 'model_type', 'name', 'lat', 'lon', 'chainage'])
df_roads = df_roads.rename(columns={'type': 'model_type'})
df_roads = df_roads.reindex(columns=columns)

selected_roads = filtered_df["road"].unique()

# Iterate over each unique road
for road in selected_roads:
    # Filter points for the current road
    road_points = df_roads[df_roads["road"] == road]

    # Find the first point with chainage 0
    first_point = road_points[road_points['chainage'] == 0].head(1)

    # Find the last point with highest chainage
    last_point = road_points.sort_values(by='chainage', ascending=False).head(1)

    # Concatenate first and last points into the result DataFrame
    df_sourcesinks = pd.concat([df_sourcesinks, first_point, last_point], ignore_index=True)

df_sourcesinks['model_type'] = 'sourcesink'
# werkt nog niet, later kijken hoe we alles SoSi + nummer kunnen geven
#print(df_sourcesinks)

#########
##STEP4##
#########
# Step 4: prepare the dataframe for the bridges

# the cleaned bridges dataset is imported
excel_file_bridge = 'BMMS_overview.xlsx'
df_bridge = pd.read_excel(excel_file_bridge)

# a new dataframe is created to store the filtered bridges
filtered_bridges = pd.DataFrame(columns=['road', 'model_type', 'condition', 'name', 'lat', 'lon', 'length', 'chainage'])

# Filter data for the roads found in df_sourcesinks.
for road_name in df_sourcesinks['road'].unique():
    bridges_to_filter = df_bridge[df_bridge['road'] == road_name]
    filtered_bridges = pd.concat([filtered_bridges, bridges_to_filter], ignore_index=True)

filtered_bridges = filtered_bridges[['road', 'model_type', 'condition', 'name', 'lat', 'lon', 'length', 'chainage']]

# removing double values for the bridges. Same latitudes and longitudes measured twice. Values with shortest length remain.
# the duplicates are removed so lengths of bridges are not counted double.
filtered_bridges = filtered_bridges.sort_values('length')
filtered_bridges = filtered_bridges.drop_duplicates(subset=['chainage'], keep='last')
filtered_bridges = filtered_bridges.sort_values(by=['road', 'chainage'])
filtered_bridges['model_type'] = 'bridge'

#########
##STEP5##
#########
# Step 5: merging the bridges with the sources and sinks
columns = ['road', 'model_type', 'condition', 'name', 'lat', 'lon', 'length', 'chainage']
df_sourcesinks = df_sourcesinks.reindex(columns=columns)

# after merging, the dataframes are sorted on road and then on chainage
df_merge = pd.concat([filtered_bridges, df_sourcesinks], ignore_index=True)
df_merge = df_merge.sort_values(by=['road', 'chainage'])

filtered_df = filtered_df.rename(columns={'road': 'road name2', 'road name2': 'road'})

df_merge_final = pd.concat([df_merge, filtered_df], ignore_index=True)

# Convert 'chainage' column to numeric data type
df_merge_final['chainage'] = pd.to_numeric(df_merge_final['chainage'], errors='coerce')

# Sort the DataFrame by 'road' column
df_merge_final = df_merge_final.sort_values(by='road')

# Then, sort by 'chainage' within each 'road' group
df_merge_final = df_merge_final.groupby('road').apply(lambda x: x.sort_values(by='chainage')).reset_index(drop=True)

# print(df_merge_final)
# later toevoegen --> SoSi namen bij sourcesink

#########
##STEP6##
#########
# Step 6: all intersections are duplicated for all roads except N1 and N2. (further explained in report)
filtered_df_copy = filtered_df.copy()
filtered_df_copy = filtered_df_copy[~filtered_df_copy['road name2'].isin(['N1', 'N2'])]

# Rename the columns
filtered_df_copy = filtered_df_copy.rename(columns={'road name2': 'road', 'road': 'road name2'})


# the chainages are selected based on whether the intersection is after the beginning or end of the road
def update_chainage(row, sourcesinks):
    # Get the latitude and longitude of the intersection
    intersection_lat = float(row['lat'])
    intersection_lon = float(row['lon'])

    # Initialize variables to store the closest sourcesinks
    closest_sourcesink_beginning = None
    closest_sourcesink_ending = None

    # Initialize variables to store the distances to the closest sourcesinks
    min_distance_beginning = float('inf')
    min_distance_ending = float('inf')

    # Iterate over sourcesinks to find the closest ones
    for index, sourcesink in sourcesinks.iterrows():
        sourcesink_lat = float(sourcesink['lat'])  # Convert to float
        sourcesink_lon = float(sourcesink['lon'])  # Convert to float
        distance = ((intersection_lat - sourcesink_lat) ** 2 + (intersection_lon - sourcesink_lon) ** 2) ** 0.5

        # Check if the sourcesink represents the beginning (chainage = 0) or the ending (chainage > 0) of the road
        if sourcesink['chainage'] == 0:
            # Sourcesink represents the beginning of the road
            if distance < min_distance_beginning:
                min_distance_beginning = distance
                closest_sourcesink_beginning = sourcesink
        else:
            # Sourcesink represents the ending of the road
            if distance < min_distance_ending:
                min_distance_ending = distance
                closest_sourcesink_ending = sourcesink

    # Check which sourcesink is closer to the intersection and adjust the chainage accordingly
    if min_distance_beginning < min_distance_ending:
        # The sourcesink representing the beginning of the road is closer
        new_chainage = closest_sourcesink_beginning['chainage'] + 0.1
    else:
        # The sourcesink representing the ending of the road is closer
        new_chainage = closest_sourcesink_ending['chainage'] - 0.1

    return new_chainage


# use update_chainage function
filtered_df_copy['chainage'] = filtered_df_copy.apply(update_chainage, args=(df_sourcesinks,), axis=1)
# print(filtered_df_copy)

# the intersections are now from both roads it is intersecting. Merged with previous dataframe
df_merge_final2 = pd.concat([df_merge_final, filtered_df_copy], ignore_index=True)

# Sort the DataFrame by 'road' column
df_merge_final2 = df_merge_final2.sort_values(by='road')

# do a check to see whether N1 and N2 have intersections with chainage 0 and make sure they will be placed after the sourcesinks:
df_merge_final2.loc[(df_merge_final2['model_type'] == 'intersection') & (df_merge_final2['road'].isin(['N1', 'N2'])) & (
            df_merge_final2['chainage'] == 0), 'chainage'] = 0.1

# Then, sort by 'chainage' within each 'road' group
df_merge_final2 = df_merge_final2.groupby('road').apply(lambda x: x.sort_values(by='chainage')).reset_index(drop=True)
# print(df_merge_final2)

#########
##STEP7##
##########
# Step 7: links are added between all objects
# # an empty list is created for data. This list will function as list to contain the information on the source, the bridges, the links and the sink of the analysis.
# Initialize an empty list to store the data for links
link_data = []

# Initialize variables to keep track of the previous chainage, model type, and object type
prev_chainage = None
prev_model_type = None
prev_object_type = None

# Iterate over each row in the merged DataFrame
for index, row in df_merge_final2.iterrows():
    # Extract required attributes
    road = row['road']
    model_type = row['model_type']
    name = row['name']
    lat = row['lat']
    lon = row['lon']
    chainage = row['chainage']

    # Skip the first row
    if index == 0:
        prev_chainage = chainage
        prev_model_type = model_type
        continue

    # Calculate the length of the link
    link_length = chainage - prev_chainage

    # Check if the current and previous objects are sourcesinks or intersections
    is_sourcesink = model_type == 'sourcesink'
    is_intersection = model_type == 'intersection'
    prev_is_sourcesink = prev_model_type == 'sourcesink'
    prev_is_intersection = prev_model_type == 'intersection'

    # Determine the object type of the current row
    if is_sourcesink or is_intersection:
        object_type = 'sourcesink_or_intersection'
    else:
        object_type = 'other'

    # Check if conditions for excluding a link are met
    if (is_sourcesink and prev_is_intersection) or (is_sourcesink and prev_is_sourcesink) or \
            (prev_object_type == 'sourcesink_or_intersection' and object_type == 'sourcesink_or_intersection'):
        # Exclude link creation between sourcesink and intersection, and between consecutive sourcesinks
        pass
    else:
        # Add link after sourcesink, bridge, or intersection
        if prev_model_type in ['sourcesink', 'bridge', 'intersection']:
            link_data.append({
                'road': road,
                'model_type': 'link',
                'condition': np.nan,
                'name': f'link_{index}',  # You can adjust this naming convention as needed
                'lat': lat,  # Use lat of the next object
                'lon': lon,  # Use lon of the next object
                'length': link_length,
                'chainage': prev_chainage  # Chainage of previous object
            })

    # Update previous chainage, model type, and object type
    prev_chainage = chainage
    prev_model_type = model_type
    prev_object_type = object_type

# Convert the list of dictionaries into a DataFrame
link_df = pd.DataFrame(link_data)

# Concatenate the original DataFrame and the link DataFrame
final_df_with_links = pd.concat([df_merge_final2, link_df], ignore_index=True)

# Sort the DataFrame by 'road' column
final_df_with_links = final_df_with_links.sort_values(by=['road', 'chainage'])


#########
##STEP8##
#########
# Step 8: all objects are given an ID

# merged_file.drop(columns=['chainage'], inplace=True)
final_df_with_links['lat'] = final_df_with_links['lat'].astype(float)
final_df_with_links['lon'] = final_df_with_links['lon'].astype(float)

def assign_id_counts(merged_file):
    # Initialize ID count dictionary
    id_counts = {}
    current_id = 1000000

    # Iterate over each row in the merged DataFrame
    for index, row in merged_file.iterrows():
        # Get the model type and latitude, longitude
        model_type = row['model_type']
        lat_lon = (round(row['lat'], 3), round(row['lon'], 3))  # Round to 3 decimal places

        # Check if the current object is an intersection or sourcesink
        if model_type in ['intersection']:
            # If it's an intersection or sourcesink, check if there's a similar lat_lon in the ID counts dictionary
            existing_id = None
            for key in id_counts.keys():
                if abs(key[0] - lat_lon[0]) < 0.001 and abs(key[1] - lat_lon[1]) < 0.001:
                    existing_id = id_counts[key]
                    break

            if existing_id is not None:
                # If similar lat_lon exists, assign the existing ID to the current row
                merged_file.at[index, 'id_count'] = int(existing_id)
            else:
                # If not, assign a new ID count
                id_counts[lat_lon] = current_id
                current_id += 1
                # Assign the ID count to the current row
                merged_file.at[index, 'id_count'] = int(id_counts[lat_lon])
        else:
            # For objects other than intersections and sourcesinks, generate a unique ID based on the index
            merged_file.at[index, 'id_count'] = int(current_id)
            current_id += 1

    return merged_file

# Call the function to assign ID counts to the merged DataFrame
merged_file = assign_id_counts(final_df_with_links)
merged_file = merged_file.rename(columns={'id_count': 'id'})

# making sure the ids are integers
merged_file['id'] = merged_file['id'].astype(int)

#print(merged_file[merged_file['model_type'] == 'intersection'])

# Display the DataFrame with ID counts
# print(merged_file)

csv_file_with_ids = 'final_df.csv'
merged_file.to_csv(csv_file_with_ids, index=False)

csv_file_intersections = 'intersections.csv'
filtered_df.to_csv(csv_file_intersections, index=False)