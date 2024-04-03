import os
import pandas as pd

# Define the path to the folder
path = '../data/raw/RMMS/RMMS/'

# Get a list of all files in the folder
files = [f for f in os.listdir(path) if f.endswith('.lrps.htm')]

# Initialize an empty list to store DataFrames
dfs = []

# Loop through each file
for file in files:
    # Read HTML tables into a list of DataFrames
    tables = pd.read_html(os.path.join(path, file))

    # Combine all tables into a single DataFrame
    df = pd.concat(tables)

    # Remove the first row and rows above row 9
    df = df.iloc[9:].reset_index(drop=True)

    # Set the correct header using the values from row 9
    df.columns = df.iloc[0]

    # Drop the now redundant row 9
    df = df.iloc[1:].reset_index(drop=True)

    # Drop the first and last columns
    df = df.iloc[:, 1:-1]

    # Add a new column for road number
    road_number = file.split('.')[0]  # Extract road number from file name
    df['road_number'] = road_number

    # Append the DataFrame to the list
    dfs.append(df)

# Concatenate all DataFrames into one
combined_df = pd.concat(dfs, ignore_index=True)

# Save the combined DataFrame to a CSV file
combined_df.to_csv('combined_lrps.csv', index=False)

combined_df.shape
combined_df.to_csv('combined_lrps.csv', index=False)

traffic_df = pd.read_csv('traffic.csv')
traffic_df.head()

traffic_df= traffic_df.rename(columns = { 'LRP':'LRP Start', 'Offset': 'Offset Start', 'Chainage':'Chainage Start', 'LRP.1':'LRP End', 'Offset.1': 'Offset End', 'Chainage.1':'Chainage End'})
print(traffic_df.shape)
print(combined_df.shape)

# Combining the different dataframes into one so we have the lat/lon values combined with the AADT values so we can calculate the different economic values for the road parts.
combined_lrps = pd.read_csv('combined_lrps.csv')

latlonload = pd.merge(traffic_df, combined_lrps, left_on=['LRP Start','road'], right_on=['LRP No', 'road_number'] )

#When merging we got 3 rows of each entry, we have dropped the duplicates below to ensure we do not get double entries.
latlonload = latlonload.drop_duplicates()
latlonload.to_csv('latlonloads.csv')

#To calculate the economic value of a roadpart, we have to assign economic value to different vehicle types.
# Afterwards we will multiply these values with the amount of sightings on each road to compute the economic value of a road.
# The logic behind the values is that for example trucks are able to carry a lot of goods, busses a lot of people and smaller vehicles are more individual focussed, hence the smaller economic impact.
# It should be noted that these are all estimates as we were unable to find research on the marginal economic impact of these vehicle types.

economic_value_vehicles = {'Heavy Truck':10,'Medium Truck': 8,'Small Truck':7,'Large Bus':7,'Medium Bus':6,'Micro Bus':5,'Utility':3,'Car':3,'Auto Rickshaw':2,'Motor Cycle': 1,'Bi-Cycle':0.5,'Cycle Rickshaw':1,'Cart':1}

# Calculate the sum of values for each row and multiply by the corresponding economic value
latlonload['EVV'] = latlonload.apply(lambda row: sum(row[col] * economic_value_vehicles[col] for col in latlonload.columns if col in economic_value_vehicles), axis=1)