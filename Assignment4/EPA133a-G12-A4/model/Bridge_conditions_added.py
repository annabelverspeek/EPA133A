import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd

# Load BMMS overview into a pandas DataFrame
bmms_df = pd.read_excel('BMMS_overview.xlsx')
# Load merged traffic data into a pandas DataFrame
traffic_df = pd.read_csv('latlonloads.csv')

# Replace empty strings with zeros in chainage column of BMMS DataFrame
bmms_df['chainage'] = bmms_df['chainage'].replace('', '0')

# Convert chainage column in BMMS DataFrame from string to float
bmms_df['chainage'] = bmms_df['chainage'].astype(str).str.replace(',', '.')

bmms_df['chainage'] = pd.to_numeric(bmms_df['chainage'], errors='coerce')
bmms_df['chainage'] = bmms_df['chainage'].astype(float)

# Convert chainage columns in traffic DataFrame from string to float
traffic_df['Chainage Start'] = traffic_df['Chainage Start'].astype(float)
traffic_df['Chainage End'] = traffic_df['Chainage End'].astype(float)

# Create a dictionary where each key will be a road segment name,
# and the value will be another dictionary holding the counts for each condition.
road_segment_conditions = {}

# Iterate through bridges in the BMMS DataFrame
for index, bridge_row in bmms_df.iterrows():
    bridge_road = bridge_row['road']
    bridge_condition = bridge_row['condition']
    bridge_chainage = bridge_row['chainage']

    # Find the road segment where the bridge chainage falls within its range
    matching_segments = traffic_df[(traffic_df['road'] == bridge_road) &
                                   (traffic_df['Chainage Start'] <= bridge_chainage) &
                                   (traffic_df['Chainage End'] >= bridge_chainage)]

    # Increment the count of the bridge condition for each matching road segment
    for i, segment_row in matching_segments.iterrows():
        segment_name = segment_row['name']

        # Initialize a new segment in the dictionary if it does not exist
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

# Merge the counts DataFrame with the traffic DataFrame on Road_Segment_ID
final_df = pd.merge(traffic_df, road_segment_conditions_df, on='name', how='left')

# Add a new column to merged_df for the weighted sum
final_df['Weighted_Sum'] = (final_df['Condition_A_Count'] * 1) + \
                             (final_df['Condition_B_Count'] * 2) + \
                             (final_df['Condition_C_Count'] * 3) + \
                             (final_df['Condition_D_Count'] * 4)

final_df.column()

# Save the result to a new CSV file
final_df.to_csv('bridge_condition_counts.csv', index=False)

# Plot the 10 most critical road segments according to the bridge condition.

# Sort the DataFrame based on 'Weighted_Sum' column in descending order
sorted_merged_df = final_df.sort_values('Weighted_Sum', ascending=False)

# Get the top 50 roads
top_100_df = sorted_merged_df.head(100)

# Get the top 10 roads within the top 50
top_10_df = top_100_df.head(10)

# Extract road names and weighted sum values for plotting, for the top 10 and top 50
road_names_100 = top_100_df['name']
weighted_values_100 = top_100_df['Weighted_Sum']

road_names_10 = top_10_df['name']
weighted_values_10 = top_10_df['Weighted_Sum']

# Plot the bar chart for the top 10 roads.
plt.figure(figsize=(10, 6))
plt.barh(road_names_10, weighted_values_10, color='skyblue')
plt.xlabel('Vulnerability of Roads based on Bridge Conditions')
plt.ylabel('Road Names')
plt.title(f'Top 10 Roads by Condition of Bridges')
plt.gca().invert_yaxis()  # Invert y-axis to display the highest-ranking road at the top
plt.show()

# Plot the bar chart for the top 100 roads.
plt.figure(figsize=(12, 8))
bars = plt.barh(road_names_100, weighted_values_100, color='skyblue')  # Plot all roads initially with blue color

# Highlight top 10 roads within top 100 by changing their color to red
for idx, bar in enumerate(bars):
    if road_names_100.iloc[idx] in top_10_df['name'].values:
        bar.set_color('red')

plt.xlabel('Vulnerability of Roads based on Bridge Conditions')
plt.ylabel('')
plt.title('Top 100 Roads by Condition of Bridges')
plt.gca().invert_yaxis()  # Invert y-axis to display the highest-ranking road at the top
plt.yticks([])
plt.show()

# Plot the vulnerability based on the condition of bridges spatially.

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

# Get the bounding box of the GeoDataFrame
minx, miny, maxx, maxy = gdf.total_bounds

# Create the base map with the bounding box
ax = plt.axes()
ax.set_xlim(minx, maxx)
ax.set_ylim(miny, maxy)

# Plot the GeoDataFrame with EVV values
gdf.plot(ax=ax, marker='o', markersize=5, column='EVV', cmap='coolwarm', legend=True, vmin=0, vmax=55000)

# Add title and show plot
plt.title('Economic Value of Roads')
plt.show()
