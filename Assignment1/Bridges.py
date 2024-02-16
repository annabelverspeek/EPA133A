import pandas as pd
file = 'BMMS_overview.xlsx'

df_bridges = pd.read_excel(file)

df_bridges.head()

df_bridges.shape



#Algorithm that tries to identify the bridges that are not on a road:
def is_bridge_on_road(bridge_row, road_row):
    # Check if bridge coordinates fall within road coordinates
    bridge_lat = bridge_row['lat']
    bridge_lon = bridge_row['lon']
    road_coords = road_row['coords']  # Assuming 'coords' is a list of (lat, lon) tuples for road segment

    for i in range(len(road_coords) - 1):
        lat1, lon1 = road_coords[i]
        lat2, lon2 = road_coords[i + 1]

        # Check if bridge is between the two points of the road segment
        if (lat1 <= bridge_lat <= lat2 or lat2 <= bridge_lat <= lat1) and \
           (lon1 <= bridge_lon <= lon2 or lon2 <= bridge_lon <= lon1):
            return True

    return False

bridges_not_on_roads = []

# Iterate over bridges and roads
for index, bridge_row in df_bridges.iterrows():
    on_road = False
    for index, road_row in df_roads.iterrows():
        if is_bridge_on_road(bridge_row, road_row):
            on_road = True
            break  # Exit inner loop if bridge is found on a road
    if not on_road:
        bridges_not_on_roads.append(bridge_row)

# Output bridges not on roads
for bridge in bridges_not_on_roads:
    print("Bridge ID:", bridge['bridge_id'], "is not on any road.")

#Als we dan een lijst hebben met bridges die niet op een road zitten en hun index en lon/lat hebben, wat doen we er dan mee?

count_commas = 0
for idx, row in df_bridges.iterrows():
    if ',' in str(row['lat']):
        df_bridges.at[idx, 'lat'] = str(row['lat']).replace(',', '.')
        count_commas += 1
    if ',' in str(row['lon']):
        df_bridges.at[idx, 'lon'] = str(row['lon']).replace(',', '.')
        count_commas += 1

print("Number of commas replaced:", count_commas)

# Check for reversed latitude and longitude
reversed_coordinates = []
for idx, row in df_bridges.iterrows():
    lat = row['lat']
    lon = row['lon']
    for inner_idx, inner_row in df_bridges.iterrows():
        if idx != inner_idx:  # Skip comparing with the same row
            if lat == inner_row['lon'] and lon == inner_row['lat']:
                reversed_coordinates.append((idx, inner_idx))
                break

# Output reversed coordinate pairs
for pair in reversed_coordinates:
    print(f"Row {pair[0]} and Row {pair[1]} have reversed latitude and longitude.")


duplicate_coordinates = df_bridges[df_bridges.duplicated(['lat', 'lon'], keep=False)]

if not duplicate_coordinates.empty:
    print("Duplicate coordinates found:")
    print(duplicate_coordinates)
else:
    print("No duplicate coordinates found.")

a1 = 0
a2 = 0
def lat_long_around(lat, long):
    for lat, long in df_bridges:
        if lat > 30 and long < 80:
            a1 = lat 
            a2 = long
            lat = a2 
            long = a1 
        else:
            continue
