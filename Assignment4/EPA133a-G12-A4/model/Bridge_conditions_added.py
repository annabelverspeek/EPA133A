import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from matplotlib.colors import LinearSegmentedColormap

###############################
### Prepare both data files ###
###############################

# Load BMMS overview into a pandas DataFrame
# This BMMS overview file now also contains the extra column flood_risk
path_bmms = '../data/processed/BMMS_overview.xlsx'
bmms_df = pd.read_excel(path_bmms)
# Load merged traffic data into a pandas DataFrame
traffic_df = pd.read_csv('latlonloads.csv')

# Replace empty strings with zeros in chainage column of BMMS DataFrame
bmms_df['chainage'] = bmms_df['chainage'].replace('', '0')

# Convert chainage column in BMMS DataFrame from string to float
bmms_df['chainage'] = bmms_df['chainage'].astype(str).str.replace(',', '.')

bmms_df['chainage'] = pd.to_numeric(bmms_df['chainage'], errors='coerce')
bmms_df['chainage'] = bmms_df['chainage'].astype(float)

# Convert chainage columns in traffic DataFrame from string to float
traffic_df['Chainage'] = traffic_df['Chainage Start'].astype(float)
traffic_df['Chainag_end'] = traffic_df['Chainage_end'].astype(float)

#######################################
### Prepare bridge condition counts ###
#######################################

# Create a dictionary where each key will be a road segment name,
# and the value will be another dictionary holding the counts for each bridge condition A,B,C or D.
road_segment_conditions = {}

# Iterate through bridges in the BMMS DataFrame
for index, bridge_row in bmms_df.iterrows():
    bridge_road = bridge_row['road']
    bridge_condition = bridge_row['condition']
    bridge_chainage = bridge_row['chainage']

    # Find the road segment where the bridge chainage falls within its range
    matching_segments = traffic_df[(traffic_df['road'] == bridge_road) &
                                   (traffic_df['Chainage Start'] <= bridge_chainage) &
                                   (traffic_df['Chainage_end'] >= bridge_chainage)]

    # Increment the count of the bridge condition for each matching road segment
    for i, segment_row in matching_segments.iterrows():
        segment_name = segment_row['name']

        # Initialize a new segment in the dictionary if it does not exist, set the initial value on zero.
        if segment_name not in road_segment_conditions:
            road_segment_conditions[segment_name] = {
                'Condition_A_Count': 0,
                'Condition_B_Count': 0,
                'Condition_C_Count': 0,
                'Condition_D_Count': 0
            }

        # Increment the counter for the bridge's condition
        if bridge_condition == 'A':
            road_segment_conditions[segment_name]['Condition_A_Count'] += 1
        elif bridge_condition == 'B':
            road_segment_conditions[segment_name]['Condition_B_Count'] += 1
        elif bridge_condition == 'C':
            road_segment_conditions[segment_name]['Condition_C_Count'] += 1
        elif bridge_condition == 'D':
            road_segment_conditions[segment_name]['Condition_D_Count'] += 1

# Now convert this nested dictionary into a DataFrame
road_segment_conditions_df = pd.DataFrame.from_dict(road_segment_conditions, orient='index')
road_segment_conditions_df.reset_index(inplace=True)
road_segment_conditions_df.rename(columns={'index': 'name'}, inplace=True)

##############################################
### Prepare bridge chancec on flood counts ###
##############################################

# Create a dictionary where each key will be a road segment name,
# and the value will be another dictionary holding the counts for each flood risk A,B,C or D.
road_segment_flood_risk = {}

# Iterate through bridges in the BMMS DataFrame
for index, bridge_row in bmms_df.iterrows():
    bridge_road = bridge_row['road']
    bridge_flood_risk = bridge_row['flood_risk']
    bridge_chainage = bridge_row['chainage']

    # Find the road segment where the bridge chainage falls within its range
    matching_segments = traffic_df[(traffic_df['road'] == bridge_road) &
                                   (traffic_df['Chainage Start'] <= bridge_chainage) &
                                   (traffic_df['Chainage_end'] >= bridge_chainage)]

    # Increment the count of the bridge condition for each matching road segment
    for i, segment_row in matching_segments.iterrows():
        segment_name = segment_row['name']

        # Initialize a new segment in the dictionary if it does not exist, set the initial on zero.
        if segment_name not in road_segment_flood_risk:
            road_segment_flood_risk[segment_name] = {
                'Flood_Risk_A_Count': 0,
                'Flood_Risk_B_Count': 0,
                'Flood_Risk_C_Count': 0,
                'Flood_Risk_D_Count': 0
            }

        # Increment the counter for the bridge's condition
        if bridge_flood_risk == 'A':
            road_segment_flood_risk[segment_name]['Flood_Risk_A_Count'] += 1
        elif bridge_flood_risk == 'B':
            road_segment_flood_risk[segment_name]['Flood_Risk_B_Count'] += 1
        elif bridge_flood_risk == 'C':
            road_segment_flood_risk[segment_name]['Flood_Risk_C_Count'] += 1
        elif bridge_flood_risk == 'D':
            road_segment_flood_risk[segment_name]['Flood_Risk_D_Count'] += 1

# Now convert this nested dictionary into a DataFrame
road_segment_flood_risk_df = pd.DataFrame.from_dict(road_segment_flood_risk, orient='index')
road_segment_flood_risk_df.reset_index(inplace=True)
road_segment_flood_risk_df.rename(columns={'index': 'name'}, inplace=True)

# Merge the counts DataFrame with the traffic DataFrame on name, both for the conditions counts
# as the flood risks counts.
final_df_1 = pd.merge(traffic_df, road_segment_conditions_df, on='name', how='left')
final_df = pd.merge(final_df_1, road_segment_flood_risk_df, on='name', how='left')

# Add a new column to final_df for the weighted sum
# The weighted sum is the count of A,B,C and D conditions and flood risks times a weight.
# Condition A and flood risk A have the lowest weight, these are the least vulnerable.
# Condition D and flood risk D have the highest weight, these are the most vulnerable.
final_df['Weighted_Sum'] = (final_df['Condition_A_Count'] * 1) + \
                             (final_df['Condition_B_Count'] * 2) + \
                             (final_df['Condition_C_Count'] * 3) + \
                             (final_df['Condition_D_Count'] * 4) + \
                             (final_df['Flood_Risk_A_Count'] * 1) + \
                             (final_df['Flood_Risk_B_Count'] * 2) + \
                             (final_df['Flood_Risk_C_Count'] * 3) + \
                             (final_df['Flood_Risk_D_Count'] * 4)


# Save the result to a new CSV file
final_df.to_csv('bridge_condition_counts.csv', index=False)

# Plot the 10 most critical road segments according to the weighted sum.

# Sort the DataFrame based on 'Weighted_Sum' column in descending order
sorted_final_df = final_df.sort_values('Weighted_Sum', ascending=False)

# Get the top 100 roads
top_100_df = sorted_final_df.head(100)

# Get the top 10 roads within the top 100
top_10_df = top_100_df.head(10)

# Extract road names and weighted sum values for plotting, for the top 10 and top 100
road_names_100 = top_100_df['name']
weighted_values_100 = top_100_df['Weighted_Sum']

road_names_10 = top_10_df['name']
weighted_values_10 = top_10_df['Weighted_Sum']

# Plot the bar chart for the top 10 roads.
plt.figure(figsize=(10, 6))
plt.barh(road_names_10, weighted_values_10, color='red')
plt.xlabel('Vulnerability of Roads')
plt.ylabel('Road Names')
plt.title(f'Top 10 Roads by Vulnerability')
plt.gca().invert_yaxis()  # Invert y-axis to display the highest-ranking road at the top
plt.show()

# Plot the bar chart for the top 100 roads.
plt.figure(figsize=(12, 8))
bars = plt.barh(road_names_100, weighted_values_100, color='skyblue')  # Plot all roads initially with blue color

# Highlight top 10 roads within top 100 by changing their color to red
for idx, bar in enumerate(bars):
    if road_names_100.iloc[idx] in top_10_df['name'].values:
        bar.set_color('red')

plt.xlabel('Vulnerability of Roads')
plt.ylabel('')
plt.title('Top 100 Roads by Vulnerability')
plt.gca().invert_yaxis()  # Invert y-axis to display the highest-ranking road at the top
plt.yticks([])
plt.show()

# Plot the vulnerability based on the condition of bridges and the flood risk of bridges spatially.

# Load the shapefile of Bangladesh roads and waterways
roads = gpd.read_file("osm/roads.shp")
waterways = gpd.read_file("osm/waterways.shp")

# Convert latitude and longitude columns to numeric types, handling errors
final_df['Latitude Decimal'] = pd.to_numeric(final_df['Latitude Decimal'], errors='coerce')
final_df['Longitude Decimal'] = pd.to_numeric(final_df['Longitude Decimal'], errors='coerce')

# Define a small range around lat/lon 0/0
tolerance = 0.01

# Remove rows with latitude and longitude values close to 0/0
final_df = final_df[
    (final_df['Latitude Decimal'].abs() > tolerance) &
    (final_df['Longitude Decimal'].abs() > tolerance)
]

# Create a GeoDataFrame from the filtered latlonload DataFrame
gdf = gpd.GeoDataFrame(final_df, geometry=gpd.points_from_xy(final_df['Longitude Decimal'], final_df['Latitude Decimal']))

# Define a colormap for the economic value of roads
cmap = LinearSegmentedColormap.from_list('evv', ['#0066ff', '#ffffff', '#ff0000'])

# Plot the map of Bangladesh roads
ax = roads.plot(color='white', edgecolor='black', figsize=(10, 6), linewidth=0.5)
waterways.plot(ax=ax, color='lightblue', linewidth=0.5)
gdf.plot(ax=ax, marker='o', markersize=3, column='Weighted_Sum', cmap=cmap, legend=True, vmin=0, vmax=300)
plt.title('Vulnerability of Road Segments')
plt.show()
