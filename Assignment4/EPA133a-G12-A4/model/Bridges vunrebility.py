import pandas as pd

file1 = '../data/processed/BMMS_overview.xlsx'
bridges = pd.read_excel(file1, engine = 'openpyxl')

#print unique division values in bridges
print('count of unique divisions in dataframe bridges is',bridges['division'].nunique())

file2 = '../data/Vulnerability_water_distance_new.csv'
vulnerabilities = pd.read_csv(file2, delimiter =";")

#print unique district val
print('count of unique District in dataframe vulnerabilities is',vulnerabilities['District'].nunique())
# print('vulnerabilities', vulnerabilities)

bridges['flood_risk'] = None

for index, row in bridges.iterrows():
    division = row['division']
    # print('division', division)

    # Filter vulnerabilities DataFrame based on current division
    division_vulnerability = vulnerabilities[vulnerabilities['District'] == division]
    # print('division_vulnerability', division_vulnerability)

    # Check if division exists in vulnerabilities DataFrame
    if not division_vulnerability.empty:
        score = division_vulnerability['Vulnerability'].iloc[0]
        #print('score', score)
        if score >= 0.41 and score <= 0.45:
            bridges.loc[index, 'flood_risk'] = 'A'
            #print('condition_water',bridges.loc[index, 'condition_water'])
        elif score > 0.45 and score <= 0.49:
            bridges.loc[index, 'flood_risk'] = 'B'
            #print(bridges.loc[index, 'condition_water'])
        elif score > 0.49 and score <= 0.53:
            bridges.loc[index, 'flood_risk'] = 'C'
            #print(bridges.loc[index, 'condition_water'])
        elif score > 0.53 and score <= 0.57:
            bridges.loc[index, 'flood_risk'] = 'D'
            #print(bridges.loc[index, 'condition_water'])
    else: print('deze division',row['division'])

bridges.to_excel('../data/processed/BMMS_overview.xlsx', index=False)
#printing column condition_water in dataframe bridges
    #print(bridges['condition_water'])

# #printing the value counts of A,B,C,D
print(bridges['flood_risk'].value_counts())
#
# #printing the amount of none values
none_values = bridges['flood_risk'].isna().sum()
print('aantal none values zijn',none_values)
#
# # Filter de DataFrame op rijen waar de waarde van 'condition_water' gelijk is aan 'None'
# none_divisions = bridges[bridges['condition_water'].isna()]['division']
#
# # Print de unieke waarden van de kolom 'division' waar 'condition_water' gelijk is aan 'None'
# print("Divisies met 'None' in de kolom 'condition_water':")
# print(none_divisions.unique())
#
# unique_vulnerable = vulnerabilities['District'].unique()
# unique_bridges = bridges['division'].unique()
# print('unique vulnerable', unique_vulnerable)
# print('unique bridges districts', unique_bridges)
#
# # Convert to sets for easier comparison
# set_vulnerable = set(unique_vulnerable)
# set_bridges = set(unique_bridges)
#
# # Find unique entries in vulnerabilities not in bridges
# unique_in_vulnerable_not_in_bridges = set_vulnerable - set_bridges
#
# # Find unique entries in bridges not in vulnerabilities
# unique_in_bridges_not_in_vulnerable = set_bridges - set_vulnerable
#
# print("Unique in 'District' not in 'division':", unique_in_vulnerable_not_in_bridges)
# print("Unique in 'division' not in 'District':", unique_in_bridges_not_in_vulnerable)
