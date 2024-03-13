import numpy as np
import pandas as pd

# Import the data of the overview
Overview_file = '_overview.xlsx'
Overview = pd.read_excel(Overview_file)

# Filter which roads are longer than 25 km
filtered_df = Overview[Overview['length'] >= 25]

# Read the tsv file of roads
tsv_file = '_roads.tsv'
df_roads = pd.read_csv(tsv_file, sep='\t')
#print(df_roads.head())

df_sourcesinks = pd.DataFrame(columns=['road', 'model_type', 'name', 'lat', 'lon'])

data = []

counter = 1

# Iterate over each unique road
for road in df_roads['road'].unique():
    road_data = df_roads[df_roads['road'] == road]
    # Extract the first LRP from the first row
    first_lrp = road_data.iloc[0]
    data.append({
        'road': first_lrp['road'],
        'model_type': 'sourcesink',
        'name': f'SoSi{counter}',
        'lat': first_lrp['lat1'],
        'lon': first_lrp['lon1']
    })
    counter += 1

    # Iterate over each unique road
    for road in df_roads['road'].unique():
        road_data = df_roads[df_roads['road'] == road]
        # Extract the first LRP from the first row
        first_lrp = road_data.iloc[0]
        data.append({
            'road': first_lrp['road'],
            'model_type': 'sourcesink',
            'name': f'SoSi{counter}',
            'lat': first_lrp['lat1'],
            'lon': first_lrp['lon1']
        })
        counter += 1

        # Extract the last LRP from the last row
        last_lrp = None
        last_lrp_lat = None
        last_lrp_lon = None

        # Iterate over rows in reverse order to find the last LRP with a non-null value
        for idx, row in road_data.iloc[1:][::-1].iterrows():  # Skip the first row (column names)
            # Find the last non-null value in the row
            last_valid_index = row.last_valid_index()
            if last_valid_index is not None:
                last_valid_index = int(last_valid_index)  # Convert to integer
                last_lrp_lat = row[last_valid_index - 1]  # Latitude is the value before the last valid index
                last_lrp_lon = row[last_valid_index]      # Longitude is the last valid value
                break

        data.append({
            'road': road,
            'model_type': 'sourcesink',
            'name': f'SoSi{counter}',
            'lat': last_lrp_lat,
            'lon': last_lrp_lon
        })
        counter += 1

# Create DataFrame from collected data
df_sourcesinks = pd.DataFrame(data)
print(df_sourcesinks.head())
