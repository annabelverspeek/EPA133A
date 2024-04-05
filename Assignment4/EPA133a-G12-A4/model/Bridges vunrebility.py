import pandas as pd

'Reading in the files of the bridges and the file found through the Internet.\
#In addition, the unique values are printed to check if the number of districts matches\
#Indeed, it can be assumed that the disctrics and divisions contain the same value and are comparable'

file1 = '../data/processed/BMMS_overview.xlsx'
bridges = pd.read_excel(file1, engine = 'openpyxl')
print('count of unique divisions in dataframe bridges is',bridges['division'].nunique())

file2 = '../data/Vulnerability_water_distance_new.csv'
vulnerabilities = pd.read_csv(file2, delimiter =";")
print('count of unique District in dataframe vulnerabilities is',vulnerabilities['District'].nunique())



'Create a new column where we can store the vulnerabilities of the division' \
'These chain vulnerabilities are determined from the Vulnerability and are divided into ABCD. \
The higher the value the higher the vulnerability is the more vulnerable this division is. \
So this vulnerability gets the lowest value the D. '
bridges['condition_water'] = None
for index, row in bridges.iterrows():
    division = row['division']
    division_vulnerability = vulnerabilities[vulnerabilities['District'] == division]

    if not division_vulnerability.empty:
        score = division_vulnerability['Vulnerability'].iloc[0]
        if score >= 0.41 and score <= 0.45:
            bridges.loc[index, 'flood_risk'] = 'A'
        elif score > 0.45 and score <= 0.49:
            bridges.loc[index, 'flood_risk'] = 'B'
        elif score > 0.49 and score <= 0.53:
            bridges.loc[index, 'flood_risk'] = 'C'
        elif score > 0.53 and score <= 0.57:
            bridges.loc[index, 'flood_risk'] = 'D'

    else: print('This division is',row['division'])


'Check before saving if there are nan values in the new column if not\
#Return the dataframe to a csv file with the new column added'
none_values = bridges['flood_risk'].isna().sum()
print('aantal none values zijn',none_values)
bridges.to_excel('../data/processed/BMMS_overview.xlsx', index=False)