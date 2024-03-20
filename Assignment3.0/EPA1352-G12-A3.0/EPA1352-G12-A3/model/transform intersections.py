
#import the data of the overview

# x toevoegen
Overview_file = '_overview.xls'
Overview = pd.read_excel(Overview_file)

# Filteren welke wegen langer zijn dan 25 km
filtered_length = Overview[Overview['length'] >= 25]
#print(filtered_length.info)

# import the html file with the road descriptions
file_path = 'N1.lrps.htm'
df_list = pd.read_html(file_path)
# create a dataframe from the html file, the table is the fourth element in the html list
df = df_list[4]
# cleaning the dataframe so that the correct rows are taken into account
df = df.drop(index=0, columns=[df.columns[0], df.columns[-1]])
df.columns = df.iloc[0]
df = df.drop(index=1)
filtered_df = df[df['LRP TYPE'].str.contains('Cross Road|Side Road')]

# Initialize an empty list to store the filtered rows
filtered_rows = []

# Iterate over each row in filtered_length
for index, row in filtered_length.iterrows():
    road_name = row['road']
    # Exclude "N1" road name
    if road_name != "N1":
        # Filter rows in filtered_df where the "Description" column contains the road name
        matching_rows = filtered_df[filtered_df['Description'].str.contains(road_name, case=False)].copy()
        # Add a new column "road name" with the road name for each matching row
        matching_rows['road name'] = road_name
        # Append the matching rows to the list
        filtered_rows.append(matching_rows)

# Concatenate the filtered rows into a single DataFrame
filtered_df = pd.concat(filtered_rows, ignore_index=True)

filtered_df.head(30)

