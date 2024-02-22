# First, we imported some necessary libraries to execute the data cleaning.
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


file = 'BMMS_overview.xlsx' # The file with all the information on bridges in Bangladesh.

df_bridges = pd.read_excel(file) # We convert the file into a Pandas dataframe.

# Lines to investigate the Pandas dataframe.
# df_bridges.head()
# df_bridges.shape


# We read the cleaned tsv file of the roads into a Pandas dataframe that we can use to clean the bridges.
dtypes = {'LRP': str, 'LAT': float, 'LON': float} # Make sure all values of LRP, LAT and LON are in the correct dtype.
df_roads = pd.read_csv("roads_cleaned.tsv", delimiter="\t", dtype=dtypes)


# We create seperate dataframes for each road in df_roads. These dataframes are put into a dictionary, where the key is the road_name.
roads_df_dict = {} # Create an empty dictionary.
for road in df_roads.itertuples(index=False): # Iterate through the roads.
    road_name = road[0] # The first column in the row contains the road_name.

    data = [] # A list to store all the data of lrp's on this road.
    for i in range(1, len(road), 3): # Iterate through all the columns, with steps of 3. Every three columns contains a LRP with LON and LAT.
        lrp = [road[i], road[i + 1], road[i + 2]] # Get the lrp name, lon and lat for every lrp on the road.
        if pd.isna(road[i]): # Break if there is a nan value.
            break
        else:
            data.append(lrp) # Append the data of this lrp to the list 'data'.

    df_road = pd.DataFrame(data, columns=['LRP', 'LAT', 'LON']) # Create a dataframe with all the data of all the lrp's on that particular road.
    roads_df_dict[road_name] = df_road # Add the dataframe to the dictionary of dataframes, with the key road_name.


# We wrote a function to plot the bridges on a certain road.
def plot_bridges(road_name, df_bridges):
    df_road = df_bridges[df_bridges['road'] == road_name] # Create a dataframe df_road with only the bridges on the road similar to road_name.
    #print(df_road.head())
    plt.figure(figsize=(10, 6)) # Set up the figure.
    df_road['lon'] = df_road['lon'].astype(float) # Once again make sure the longitude and latitude are of type float.
    df_road['lat'] = df_road['lat'].astype(float)
    plt.plot(df_road['lon'], df_road['lat'], marker='o', linestyle='-') # Plot all bridges in df_road based on their latitude and longtitude.
    plt.title(f"{road_name} Bridges")
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.grid(True)
    plt.show()


# The following function is written to correct the latitude and longitude of bridges.
# We expect the lrp name of a bridge to be correct. Based on the lrp name we change the latitude and longtitude of the bridge.

def correct_lon_lat(road, df_bridges, roads_df_dict): # The function requires the road we want to correct, the df_bridges and the dictionary with dataframes of each road.

    if road in roads_df_dict: # Check if the road we want to correct has a dataframe with lrp's in roads_df_dict.
        road_road = roads_df_dict[road] # If so, get the dataframe of that particular road out of the dictionary.

        for index, row in df_bridges[df_bridges['road']==road].iterrows(): # Iterate through the bridges that are on the road.

            lrp_name = row['LRPName'].strip() # Get the LRP name from that bridge.

            if lrp_name in road_road['LRP'].astype(str).values: # Check if the LRP name exists in df_road of this road.
                lrp_name = str(lrp_name)

                corresponding_row = road_road[road_road['LRP'] == lrp_name].iloc[0] # Get the corresponding row from df_road where LRPName matches

                # Update the longitude and latitude values in df_bridges
                df_bridges.loc[index, 'lat'] = corresponding_row['LAT']
                df_bridges.loc[index, 'lon'] = corresponding_row['LON']

    return df_bridges # Return the updated df_bridges with the correct latitude and longitude of the bridges.

# Another function is written to correct bridges where the latitude and longitude are reversed.
# In Bangladesh this is the case if the latitude is more than 28 and the longitude is less than 88.
def lat_long_around(df):
    for index, row in df.iterrows(): # Iterate through all the bridges.
        lat = row['lat'] # Extract the latitude and the longitude out of the row.
        long = row['lon']
        if lat > 28 and long < 88:
            df.loc[index, 'lat'], df.loc[index, 'lon'] = long, lat # Swap the latitude and longitude
    return df  # Return the modified DataFrame


lat_long_around(df_bridges)  # Execute the function lat_long_around for df_bridges.

unique_roads = df_bridges['road'].unique() #Extract all the unique roads in df_bridges.
for road in unique_roads: # Iterate through all the unique roads in df_bridges.
    correct_lon_lat(road,df_bridges , roads_df_dict) # For each unique road, correct the latitudes and longitudes.

plot_bridges('N1', df_bridges) # Plot a particular bridge to see how the latitude and longitude of bridges are changed and the outliers are fixed.

