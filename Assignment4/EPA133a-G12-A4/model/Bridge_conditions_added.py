import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from matplotlib.colors import LinearSegmentedColormap

###############################
### Preparation data files ###
###############################

"""

Prepare both data files:

The BMMS_overview file is loaded into a pandas DataFrame. 
This file now also contains a column for the flood risk of a bridge. 
Also the latlonloads file including the column of EVV is loaded into a pandas DataFrame. 

To prepare the dataframes the values in the chainage column are changed to the correct type. 

"""

path_bmms = '../data/processed/BMMS_overview.xlsx'
bmms_df = pd.read_excel(path_bmms)

traffic_df = pd.read_csv('latlonloads.csv')

bmms_df['chainage'] = bmms_df['chainage'].replace('', '0')
bmms_df['chainage'] = bmms_df['chainage'].astype(str).str.replace(',', '.')
bmms_df['chainage'] = pd.to_numeric(bmms_df['chainage'], errors='coerce')
bmms_df['chainage'] = bmms_df['chainage'].astype(float)

traffic_df['Chainage'] = traffic_df['Chainage Start'].astype(float)
traffic_df['Chainag_end'] = traffic_df['Chainage_end'].astype(float)

#######################################
### Prepare bridge condition counts ###
#######################################

"""

This part creates a dictionary where each key will be a road segment and the value will be 
another dictionary holding the counts for each bridge condition A,B,C or D.

For this both the bmms_df and the traffic_df are used.
Based on the chainage of a bridge it was possible to calculate which bridges were on which road segment. 
Afterwards we calculated how many of these bridges had condition A,B,C and D. 

"""

road_segment_conditions = {}

for index, bridge_row in bmms_df.iterrows():
    bridge_road = bridge_row['road']
    bridge_condition = bridge_row['condition']
    bridge_chainage = bridge_row['chainage']

    matching_segments = traffic_df[(traffic_df['road'] == bridge_road) &
                                   (traffic_df['Chainage Start'] <= bridge_chainage) &
                                   (traffic_df['Chainage_end'] >= bridge_chainage)]

    for i, segment_row in matching_segments.iterrows():
        segment_name = segment_row['name']

        if segment_name not in road_segment_conditions:
            road_segment_conditions[segment_name] = {
                'Condition_A_Count': 0,
                'Condition_B_Count': 0,
                'Condition_C_Count': 0,
                'Condition_D_Count': 0
            }

        if bridge_condition == 'A':
            road_segment_conditions[segment_name]['Condition_A_Count'] += 1
        elif bridge_condition == 'B':
            road_segment_conditions[segment_name]['Condition_B_Count'] += 1
        elif bridge_condition == 'C':
            road_segment_conditions[segment_name]['Condition_C_Count'] += 1
        elif bridge_condition == 'D':
            road_segment_conditions[segment_name]['Condition_D_Count'] += 1


road_segment_conditions_df = pd.DataFrame.from_dict(road_segment_conditions, orient='index')
road_segment_conditions_df.reset_index(inplace=True)
road_segment_conditions_df.rename(columns={'index': 'name'}, inplace=True)

##############################################
### Prepare bridge chances on flood counts ###
##############################################

"""

In this part again a dictionary is created. The dictionary has as key a road segment
and the value is another dictionary holding the counts for each flood risk A,B,C or D.
The flood risk of a bridge is determined in Bridges vulnerability.py. 

"""

road_segment_flood_risk = {}

for index, bridge_row in bmms_df.iterrows():
    bridge_road = bridge_row['road']
    bridge_flood_risk = bridge_row['flood_risk']
    bridge_chainage = bridge_row['chainage']

    matching_segments = traffic_df[(traffic_df['road'] == bridge_road) &
                                   (traffic_df['Chainage Start'] <= bridge_chainage) &
                                   (traffic_df['Chainage_end'] >= bridge_chainage)]

    for i, segment_row in matching_segments.iterrows():
        segment_name = segment_row['name']

        if segment_name not in road_segment_flood_risk:
            road_segment_flood_risk[segment_name] = {
                'Flood_Risk_A_Count': 0,
                'Flood_Risk_B_Count': 0,
                'Flood_Risk_C_Count': 0,
                'Flood_Risk_D_Count': 0
            }

        if bridge_flood_risk == 'A':
            road_segment_flood_risk[segment_name]['Flood_Risk_A_Count'] += 1
        elif bridge_flood_risk == 'B':
            road_segment_flood_risk[segment_name]['Flood_Risk_B_Count'] += 1
        elif bridge_flood_risk == 'C':
            road_segment_flood_risk[segment_name]['Flood_Risk_C_Count'] += 1
        elif bridge_flood_risk == 'D':
            road_segment_flood_risk[segment_name]['Flood_Risk_D_Count'] += 1


road_segment_flood_risk_df = pd.DataFrame.from_dict(road_segment_flood_risk, orient='index')
road_segment_flood_risk_df.reset_index(inplace=True)
road_segment_flood_risk_df.rename(columns={'index': 'name'}, inplace=True)

##################################
### Determine the weighted sum ###
##################################

"""

This part creates a final_df containing the traffic data and the EVV column and both dictionaries:
- bridge conditions
- flood risks

Based on the eight columns added the weighted sum is determined.
The weighted sum is the count of A,B,C and D conditions and flood risks times a weight.
Condition A and flood risk A have the lowest weight, these are the least vulnerable.
Condition D and flood risk D have the highest weight, these are the most vulnerable.
A new column has been added to final_df for the weighted sum. 

"""

final_df_1 = pd.merge(traffic_df, road_segment_conditions_df, on='name', how='left')
final_df = pd.merge(final_df_1, road_segment_flood_risk_df, on='name', how='left')

final_df['Weighted_Sum'] = (final_df['Condition_A_Count'] * 1) + \
                             (final_df['Condition_B_Count'] * 2) + \
                             (final_df['Condition_C_Count'] * 3) + \
                             (final_df['Condition_D_Count'] * 4) + \
                             (final_df['Flood_Risk_A_Count'] * 1) + \
                             (final_df['Flood_Risk_B_Count'] * 2) + \
                             (final_df['Flood_Risk_C_Count'] * 3) + \
                             (final_df['Flood_Risk_D_Count'] * 4)


final_df.to_csv('bridge_condition_counts.csv', index=False)

########################
### Plot the results ###
########################

"""

This part plots the results for the vulnerability metrics. 

Based on the weighted sum, where a high value means a high vulnerability of the bridge, several plots are created.
- The first plot shows the top 10 most vulnerable roads according to the weighted sum. 

- The second plot shows the top 100 most vulnerable roads with the top 10 colored in red. 
This way it is possible to see the top 10 relative to a big part of the road segments. 

- The last plot shows the vulnerability based on the weighted sum spatially. 
Shapefiles of roads and waterways are used for this part.

"""

sorted_final_df = final_df.sort_values('Weighted_Sum', ascending=False)
sorted_final_df['name'].to_csv('../data/processed/Vulnerability.csv', index=False)

top_100_df = sorted_final_df.head(100)

top_10_df = top_100_df.head(10)

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
plt.gca().invert_yaxis()
plt.show()

# Plot the bar chart for the top 100 roads.
plt.figure(figsize=(12, 8))
bars = plt.barh(road_names_100, weighted_values_100, color='skyblue')

for idx, bar in enumerate(bars):
    if road_names_100.iloc[idx] in top_10_df['name'].values:
        bar.set_color('red')

plt.xlabel('Vulnerability of Roads')
plt.ylabel('')
plt.title('Top 100 Roads by Vulnerability')
plt.gca().invert_yaxis()
plt.yticks([])
plt.show()

# Plot the vulnerability based on the condition of bridges and the flood risk of bridges spatially.
roads = gpd.read_file("osm/roads.shp")
waterways = gpd.read_file("osm/waterways.shp")

final_df['Latitude Decimal'] = pd.to_numeric(final_df['Latitude Decimal'], errors='coerce')
final_df['Longitude Decimal'] = pd.to_numeric(final_df['Longitude Decimal'], errors='coerce')

tolerance = 0.01

final_df = final_df[
    (final_df['Latitude Decimal'].abs() > tolerance) &
    (final_df['Longitude Decimal'].abs() > tolerance)
]

gdf = gpd.GeoDataFrame(final_df, geometry=gpd.points_from_xy(final_df['Longitude Decimal'], final_df['Latitude Decimal']))

cmap = LinearSegmentedColormap.from_list('evv', ['#0066ff', '#ffffff', '#ff0000'])

ax = roads.plot(color='white', edgecolor='black', figsize=(10, 6), linewidth=0.5)
waterways.plot(ax=ax, color='lightblue', linewidth=0.5)
gdf.plot(ax=ax, marker='o', markersize=3, column='Weighted_Sum', cmap=cmap, legend=True, vmin=0, vmax=300)
plt.title('Vulnerability of Road Segments')
plt.show()