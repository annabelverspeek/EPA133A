import numpy as np
import pandas as pd

#import the data of the overview
Overview_file = '_overview.xlsx'
Overview = pd.read_excel(Overview_file)

# Filteren welke wegen langer zijn dan 25 km
filtered_df = Overview[Overview['length'] >= 25]
print(filtered_df.info)