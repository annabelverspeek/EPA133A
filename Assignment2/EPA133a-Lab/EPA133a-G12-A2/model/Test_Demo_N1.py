import pandas as pd
import numpy as np

# import the data from the excel file and read the data
excel_file = 'BMMS_overview2.xlsx'
df = pd.read_excel(excel_file)
print(df.shape)

#df['road'] = df['road'].str.strip().str.upper()
df = df[df['road'] == 'N1']
print(df.shape)

# I created an empty list to hold the data
data = []

# Initializing the variables
id_counter = 1000000
link_chainage = 0

bridge_counter = 1  # Initialize bridge counter
link_chainage = 0    # Initialize link chainage

for index, row in df.iterrows():
    # Extract required attributes
    road = row['road']
    lat = row['lat']
    lon = row['lon']
    length = row['length']
    condition = row['condition']

    chainage_str = str(row['chainage'])  # Convert chainage to string
    chainage = float(chainage_str.replace(',', '.'))  # Replace commas and convert to float

    # Append source
    if index == 0:
        data.append({'road': road, 'id': id_counter, 'model_type': 'source', 'name': 'source', 'lat': lat, 'lon': lon, 'length': 4, 'condition': np.nan})
        id_counter += 1

    # Append link
    if index > 0:
        link_length = chainage - link_chainage  # Calculate the length of the link
        data.append({'road': road, 'id': id_counter, 'model_type': 'link', 'name': f'link {index}', 'lat': link_chainage, 'lon': link_chainage, 'length': link_length, 'condition': np.nan})
        id_counter += 1
        link_chainage = chainage  # Update link chainage

    # Append bridge
    if row['type'] == 'PC Girder Bridge' or row['type'] == 'Box Culvert' or row['type'] == 'PC Box' or row['type'] == 'RCC Girder Bridge' or row['type'] == 'Slab Culvert' or row['type'] == 'Steel Beam & RCC Slab' or row['type'] == 'Arch Masonry' or row['type'] == 'RCC Bridge' or row['type'] == 'Truss With Timber Deck':  # Check if it's a bridge
        bridge_name = f"bridge {bridge_counter}"  # Use generic name for bridge
        data.append({'road': road, 'id': id_counter, 'model_type': 'bridge', 'name': bridge_name, 'lat': lat, 'lon': lon, 'length': length, 'condition': condition})
        id_counter += 1
        bridge_counter += 1  # Increment bridge counter

# Append sink
data.append({'road': road, 'id': id_counter, 'model_type': 'sink', 'name': 'sink', 'lat': chainage, 'lon': chainage, 'length': 20, 'condition': np.nan})

# Convert the list of dictionaries into a DataFrame
new_df = pd.DataFrame(data)
#print(new_df.head(10))


# # Write the transformed data into a new CSV file
# csv_file_path = 'transformed_data.csv'
# new_df.to_csv(csv_file_path, index=False)
#
# print(f"CSV file '{csv_file_path}' has been created successfully.")

csv_file_path_N1 = 'transformed_data_N1.csv'
new_df.to_csv(csv_file_path_N1, index=False)

print(f"CSV file '{csv_file_path_N1}' has been created successfully.")
