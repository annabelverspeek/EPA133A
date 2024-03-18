import pandas as pd

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

#Step 2: we scrape data from html files with the lrps of the roads to find the intersections of roads
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

# Concatenate the filtered rows into a single DataFrame
filtered_df = pd.concat(filtered_rows, ignore_index=True)

#print(filtered_df.head(30))

# Get unique road names from filtered_df
filtered_road_names = filtered_df['road name'].unique()

# Filter df_sourcesinks to contain only roads present in filtered_df
filtered_sourcesinks = df_sourcesinks[df_sourcesinks['road'].isin(filtered_road_names)]

filtered_sourcesinks['name'] = ['SoSi' + str(i) for i in range(1, len(filtered_sourcesinks) + 1)]

print(filtered_sourcesinks.head(16))
