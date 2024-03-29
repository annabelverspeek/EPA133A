import os
import pandas as pd

###################
##reading traffic##
###################

# Path to your data folder
data_folder = '../data/raw/RMMS'

# Path to the folder containing HTML files within the data folder
html_folder = os.path.join(data_folder, 'RMMS')

# List all HTML files ending with '.traffic.htm' in the html_folder
html_files = [file for file in os.listdir(html_folder) if file.endswith('.traffic.htm')]
list_data = []

# Iterate over each HTML file
for file in html_files:
    # Construct the full path to the HTML file
    file_path = os.path.join(html_folder, file)

    # Parse HTML tables into a list of DataFrames
    dfs = pd.read_html(file_path)

    # table is starting at 5th row
    dfs = dfs[4]
    new_header = dfs.iloc[2]
    dfs = dfs[3:]
    dfs.columns = new_header
    list_data.append(dfs)

# Concatenate all DataFrames in the list
traffic = pd.concat(list_data, ignore_index=True)

traffic.columns.values[:6] = ['road', 'name', 'LRP', 'Offset', 'Chainage', 'LRP_end']

#for removing the - part
traffic['road'] = traffic['road'].apply(lambda x: x.split('-')[0])

################
##reading LRPs##
################

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

combined_df = combined_df.rename(columns={'LRP No':'LRP','road_number':'road'})

# Merge the two dataframes on 'road' and 'LRP' with a left join
merged_df_traffic = pd.merge(traffic, combined_df, on=['road', 'LRP'], how='left'))


print(merged_df_traffic.head())

# Save the merged dataframe to a CSV file
merged_df_traffic.to_csv('merged_traffic_data.csv', index=False)
