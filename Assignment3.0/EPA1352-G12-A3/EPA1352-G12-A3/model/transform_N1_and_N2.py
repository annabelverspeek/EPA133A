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
    road_row = road_data.iloc[0]
    data.append({
        'road': road_row['road'],
        'model_type': 'sourcesink',
        'name': f'SoSi{counter}',
        'lat': road_row['lat1'],
        'lon': road_row['lon1']
    })
    counter += 1

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

# Create DataFrame from collected data
df_sourcesinks = pd.DataFrame(data)
#print(df_sourcesinks.head(30))

csv_file_sourcesink = 'sourcesink_roads.csv'
df_sourcesinks.to_csv(csv_file_sourcesink, index=False)
print(f"CSV file '{csv_file_sourcesink}' has been created successfully.")