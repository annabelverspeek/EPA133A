import os
import pandas as pd

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

traffic.columns.values[:2] = ['road', 'name']

#for removing the - part
traffic['road'] = traffic['road'].apply(lambda x: x.split('-')[0])

print(traffic.head())