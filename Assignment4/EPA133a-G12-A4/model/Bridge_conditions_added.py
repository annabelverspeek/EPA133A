import pandas as pd

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

# Now you can save this to a CSV or proceed with other operations

# Merge the counts DataFrame with the traffic DataFrame on Road_Segment_ID
merged_df = pd.merge(traffic_df, road_segment_conditions_df, on='name', how='left')
# Save the result to a new CSV file
merged_df.to_csv('bridge_condition_counts.csv', index=False)

# ------------------
# # Create a dictionary to store the counts of bridge conditions for each road segment
# road_segment_conditions = {'Road_Segment_Name': [], 'Condition_A_Count': 0, 'Condition_B_Count': 0, 'Condition_C_Count': 0, 'Condition_D_Count': 0}
#
# # Iterate through bridges in the BMMS DataFrame
# for index, bridge_row in bmms_df.iterrows():
#     bridge_road = bridge_row['road']
#     bridge_condition = bridge_row['condition']
#     bridge_chainage = bridge_row['chainage']
#
#     # Find the road segment where the bridge chainage falls within its range
#     matching_segments = traffic_df[(traffic_df['road'] == bridge_road) & (traffic_df['Chainage Start'] <= bridge_chainage) & (traffic_df['Chainage End'] >= bridge_chainage)]
#
#     # Increment the count of the bridge condition for each matching road segment
#     for i, segment_row in matching_segments.iterrows():
#         segment_name = segment_row['name']
#
#         # If the segment name is not already in the dictionary, add it
#         if segment_name not in road_segment_conditions['Road_Segment_Name']:
#             road_segment_conditions['Road_Segment_Name'].append(segment_name)
#             road_segment_conditions['Condition_A_Count'].append(0)
#             road_segment_conditions['Condition_B_Count'].append(0)
#             road_segment_conditions['Condition_C_Count'].append(0)
#             road_segment_conditions['Condition_D_Count'].append(0)
#
#         # Now you can increment the count without worrying about index errors
#         index = road_segment_conditions['Road_Segment_Name'].index(segment_name)
#         if bridge_condition == 'A':
#             road_segment_conditions['Condition_A_Count'] += 1
#         elif bridge_condition == 'B':
#             road_segment_conditions['Condition_B_Count'] += 1
#         elif bridge_condition == 'C':
#             road_segment_conditions['Condition_C_Count'] += 1
#         elif bridge_condition == 'D':
#             road_segment_conditions['Condition_D_Count'] += 1
#
# # Convert the dictionary to a DataFrame
# road_segment_conditions_df = pd.DataFrame(road_segment_conditions)
# print(road_segment_conditions_df.head())
#
# # Merge the counts DataFrame with the traffic DataFrame on Road_Segment_ID
# # merged_df = pd.merge(traffic_df, road_segment_conditions_df, on='Road_Segment_Name', how='left')
#
# # Save the result to a new CSV file
# road_segment_conditions_df.to_csv('bridge_condition_counts.csv', index=False)
#
#
