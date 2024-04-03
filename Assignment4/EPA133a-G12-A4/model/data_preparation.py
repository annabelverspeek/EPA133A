import os
import pandas as pd
import numpy as np

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

traffic.columns.values[:8] = ['road', 'name', 'LRP', 'Offset', 'Chainage',
                              'LRP_end', 'Óffset_end', 'Chainage_end']
###################################################
###averaging the left and right sides of traffic###
###################################################
def average_lr_rows(traffic):
    #finding all roads that have a left and right side and finding the average for all the value columns
    columns_to_average = [
        'Heavy Truck', 'Medium Truck', 'Small Truck', 'Large Bus', 'Medium Bus',
        'Micro Bus', 'Utility', 'Car', 'Auto Rickshaw', 'Motor Cycle', 'Bi-Cycle',
        'Cycle Rickshaw', 'Cart', 'Motorized', 'Non Motorized', 'Total AADT', '(AADT)'
    ]

    mask_lr = traffic['road'].str.contains(r'\d+[LR]$', regex=True)
    traffic_lr = traffic[mask_lr].copy()
    traffic_non_lr = traffic[~mask_lr].copy()

    traffic_lr['segment_number'] = traffic_lr['road'].str.extract(r'(.+-\d+)[RL]?')

    for col in columns_to_average:
        traffic_lr[col] = pd.to_numeric(traffic_lr[col], errors='coerce')

    averaged_rows = pd.DataFrame()

    grouped = traffic_lr.groupby('segment_number')
    for name, group in grouped:
        if len(group) == 2:
            avg_row = group.mean(numeric_only=True)
            avg_row = avg_row[columns_to_average]
            row_template = group.iloc[0].to_dict()
            row_template.update(avg_row.to_dict())
            row_template['road'] = name
            averaged_rows = pd.concat([pd.DataFrame([row_template]),
                                       averaged_rows], ignore_index=True)
    result = pd.concat([traffic_non_lr, averaged_rows], ignore_index=True)

    return result

# adding the rows with average values in the traffic dataframe
traffic = average_lr_rows(traffic)

# only leaving the road of all rows
traffic['road'] = traffic['road'].apply(lambda x: x.split('-')[0])
traffic.drop('segment_number',
  axis='columns', inplace=True)

traffic = traffic.sort_values(by=["road","Chainage"])
traffic.to_csv('traffic.csv', index=False)

# ################
# ##reading LRPs##
# ################
#
# # Define the path to the folder
# path = '../data/raw/RMMS/RMMS/'
#
# # Get a list of all files in the folder
# files = [f for f in os.listdir(path) if f.endswith('.lrps.htm')]
#
# # Initialize an empty list to store DataFrames
# dfs = []
#
# # Loop through each file
# for file in files:
#     # Read HTML tables into a list of DataFrames
#     tables = pd.read_html(os.path.join(path, file))
#
#     # Combine all tables into a single DataFrame
#     df = pd.concat(tables)
#
#     # Remove the first row and rows above row 9
#     df = df.iloc[9:].reset_index(drop=True)
#
#     # Set the correct header using the values from row 9
#     df.columns = df.iloc[0]
#
#     # Drop the now redundant row 9
#     df = df.iloc[1:].reset_index(drop=True)
#
#     # Drop the first and last columns
#     df = df.iloc[:, 1:-1]
#
#     # Add a new column for road number
#     road_number = file.split('.')[0]  # Extract road number from file name
#     df['road_number'] = road_number
#
#     # Append the DataFrame to the list
#     dfs.append(df)
#
# # Concatenate all DataFrames into one
# combined_df = pd.concat(dfs, ignore_index=True)
#
# combined_df = combined_df.rename(columns={'LRP No':'LRP','road_number':'road'})
#
# # Merge the two dataframes on 'road' and 'LRP' with a left join
# merged_df_traffic = pd.merge(traffic, combined_df, on=['road', 'LRP'], how='left')
#
# print(merged_df_traffic.head())
#
# # Save the merged dataframe to a CSV file
# merged_df_traffic.to_csv('merged_traffic_data.csv', index=False)
