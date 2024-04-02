import pandas as pd

file1 = '../data/BMM.csv'
bridges = pd.read_csv(file)

file2 = '../data/vulnerability_water_distance.xls'
vulnerabilities = pd.read_excel(file2)


for index, row in bridges.iterrows():
    division = row['division']

    if row['division'] in vulnerabilities:
        score = vulnerabilities['vulnerability']
        if score > 0.4 and score <= 0.45:
            bridges.at[index, 'condition_water'] = 'A'
        elif score > 0.45 and score <= 0.5:
            bridges.at[index, 'condition_water'] = 'B'
        elif score > 0.5 and score <= 0.55:
            bridges.at[index, 'condition_water'] = 'C'
        elif score > 0.55 and score <= 0.6:
            bridges.at[index, 'condition_water'] = 'D'

bridges.to_csv('../model/BMM.csv', index=False)


