import pandas as pd

file1 = '../data/processed/BMMS_overview.xlsx'
bridges = pd.read_excel(file1, engine = 'openpyxl')

file2 = '../data/Vulnerability_water_distance.xlsx'
vulnerabilities = pd.read_excel(file2, engine = 'openpyxl')


for index, row in bridges.iterrows():
    division = row['division']

    if row['division'] in vulnerabilities:
        score = vulnerabilities['Vulnerability']
        if score > 0.4 and score <= 0.45:
            bridges.at[index, 'condition_water'] = 'A'
        elif score > 0.45 and score <= 0.5:
            bridges.at[index, 'condition_water'] = 'B'
        elif score > 0.5 and score <= 0.55:
            bridges.at[index, 'condition_water'] = 'C'
        elif score > 0.55 and score <= 0.6:
            bridges.at[index, 'condition_water'] = 'D'
    else: print(row['division'])

bridges.to_excel('../data/processed/BMMS_overview.xlsx', index=False)




# import pandas as pd
#
# file1 = '../data/processed/BMMS_overview.xlsx'
# bridges = pd.read_excel(file1)
#
# file2 = '../data/Vulnerability_water_distance.xlsx'
# vulnerabilities = pd.read_excel(file2)
#
# for index, row in bridges.iterrows():
#     division = row['division']
#
#     # Check if division exists in vulnerabilities DataFrame
#     if division in vulnerabilities['division'].values:
#         # Get vulnerability score for the current division
#         score = vulnerabilities.loc[vulnerabilities['division'] == division, 'vulnerability'].values[0]
#
#         # Assign condition rating based on the vulnerability score
#         if score > 0.4 and score <= 0.45:
#             bridges.at[index, 'condition_water'] = 'A'
#         elif score > 0.45 and score <= 0.5:
#             bridges.at[index, 'condition_water'] = 'B'
#         elif score > 0.5 and score <= 0.55:
#             bridges.at[index, 'condition_water'] = 'C'
#         elif score > 0.55 and score <= 0.6:
#             bridges.at[index, 'condition_water'] = 'D'
#     else:
#         print(row['division'])
#
# bridges.to_excel('../data/processed/BMMS_overview.xlsx', index=False)