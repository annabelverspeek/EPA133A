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
#combined_df.to_csv('combined_lrps.csv', index=False)

print(combined_df.columns)
