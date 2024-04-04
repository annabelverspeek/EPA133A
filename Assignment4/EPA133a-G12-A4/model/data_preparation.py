import os
import pandas as pd

#########################
##cleaning traffic data##
#########################
#all (relevant) traffic data from all roads is scraped from all htmls and combined into 1 dataframe.
data_folder = '../data/raw/RMMS'
html_folder = os.path.join(data_folder, 'RMMS')
html_files = [file for file in os.listdir(html_folder) if file.endswith('.traffic.htm')]
list_data = []

for file in html_files:
    file_path = os.path.join(html_folder, file)

    dfs = pd.read_html(file_path)

    dfs = dfs[4]
    new_header = dfs.iloc[2]
    dfs = dfs[3:]
    dfs.columns = new_header
    list_data.append(dfs)

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

# only leaving the road name of all rows and parsing all data into a csv file
traffic['road'] = traffic['road'].apply(lambda x: x.split('-')[0])
traffic.drop('segment_number',
  axis='columns', inplace=True)

traffic['Chainage'] = traffic['Chainage'].astype(float)
traffic = traffic.sort_values(by=["road", "Chainage"])

traffic['name'] = traffic['name'].str.replace("(Left)", "")

traffic.to_csv('traffic.csv', index=False)

