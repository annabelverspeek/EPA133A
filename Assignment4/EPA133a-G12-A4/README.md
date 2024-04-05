# README File

Created by: EPA1352 Group 12 

|    Name                   | Student Number |
| :-----------------------: | :-------------:|
| Noë ter Avest             | 4955889        |
| Joost Klessens            | 4913299        |
| Anna Paardekooper         | 4909445        |
| Annabel Verspeek          | 5085241        |
| Suus Wielders             | 4955870        |
| Luisa Ximenez Bruidegom   | 5131197        |

## Introduction:
Assignment 4 is focused on identifying the most critical and vulnerable bridges and road segments. Data is used from the RMMS database and from the BMMS database. Combining these points of data was the initial phase to start the analysis. After the data was formatted in a manner that we could analyse it, calculations have been made on both the data on traffic and on the data for conditions of bridges. The goal of the assignment was to analyse multiple things:
1) Find out what the economic criticality was of every road segment. 
2) Find out the vulnerability of the bridges on every road segment for the conditions the bridges have.
3) Find out the vulnerability of the bridges on every road segment for the risk of a flood happening at that road segment. 
## How to Use
Per folder, there is a description how to use the files:
### data  
In the processed data, the data on the bridges can be found: *'BMMS_overview'*
In the folder of the raw data, the RMMS database can be found. For the data on traffic all files are read that end with '.traffic.htm'. For the location of the road segments, data is used from the files ending with '.lrps.htm'.
For the vulnerability of the bridges, the *'vulnerability_water_distance'* files are used that can be found in the processed data folder. 

### model
The model folder contains of 4 different folders, being the input folder, osm folder and the output folder.

#### input
The input folder contains all the python files that have been used to conduct the analysis. 
- The file *'data_preparation.py'* reads the traffic files and creates a cleaned dataframe out of all these files. This dataframe is saved as csv to *model/output/traffic.csv*
- The file *'latlon RMMS.py'* combines the data on traffic with the location (latitude & longitude) of all road segments. After this data is combined, it calculates for every road segment the economic value. Finally, the criticality is determined for every road segments and the outcomes are presented in visualisations which can be found in report/figures. The values for the EVV can be found in the output subfolder in the files *'combined_lrps.csv', 'criticality.csv', 'latlonloads.csv'*.
- After the files have been merged the risk of floods are added to the dataframe with the Python file *'Bridges vulnerability.py'*. In this python file, flood risks of certain districts in Bangladesh are aligned with the road segments. This to identify which road segments have highest risk of flooding. The python file creates a new bridges file in *'output/BMMS_overview.xlsv'*.
- The file *'Bridge_conditions_added'* reads the file *'output/BMMS_overview.xlsx'* and matches the conditions for every bridge to which road segment it belongs to. An overview is added of the amount of bridges per condition per road segment. This is needed to calculate the vulnerability of the road segments. Running the conditions file (needs to happen after running the *'Bridges vulnerability'* file) returns the file *'output/bridge_condition_counts.csv'*
- Lastly, a combination of the top 10 most critical and most vulnerable road segments is created in the file *'Criticality and vulnerability'*. This code returns the plot of *'criticality_and_vulnerability'* to define the top 10 most critical and vulnerable roads.

#### output 
The order of Python files mentioned above is also the order to run the files. All outputs will be found in the output folder

#### osm
The osm data is used to geographically visualize the vulnerability of the bridges and the criticality of the roads.

### notebook 
In the notebook folder one Jupyter file can be found that was used to do the first analyses. In the outcomes, this file is no longer used.

### report 
In the report folder, the final report can be found on our analysis. The visualized outcomes of the analysis can be found in report/figures.

###
The *requirements.txt* file contains all the required packages. 






