import pandas as pd

file1 = '../data/processed/BMMS_overview.xlsx'
bridges = pd.read_excel(file1, engine = 'openpyxl')

file2 = '../data/Vulnerability_water_distance.xlsx'
vulnerabilities = pd.read_excel(file2, engine = 'openpyxl')

bridges['condition_water'] = None

for index, row in bridges.iterrows():
    division = row['division']

    # Filter vulnerabilities DataFrame based on current division
    division_vulnerability = vulnerabilities[vulnerabilities['District'] == division]
    print(division_vulnerability)

    # Check if division exists in vulnerabilities DataFrame
    if not division_vulnerability.empty:
        score = division_vulnerability['Vulnerability']
        print(score)
        if score > 0.4 and score <= 0.45:
            bridges.loc[index, 'condition_water'] = 'A'
        elif score > 0.45 and score <= 0.5:
            bridges.loc[index, 'condition_water'] = 'B'
        elif score > 0.5 and score <= 0.55:
            bridges.loc[index, 'condition_water'] = 'C'
        elif score > 0.55 and score <= 0.6:
            bridges.loc[index, 'condition_water'] = 'D'
    # else: print(row['division'])

bridges.to_excel('../data/processed/BMMS_overview.xlsx', index=False)

