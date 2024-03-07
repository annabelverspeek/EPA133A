from model import BangladeshModel
from components import Vehicle
import os
import pandas as pd
import matplotlib.pyplot as plt


"""
    Run simulation
    Print output at terminal
"""

# ---------------------------------------------------------------

# run time 5 x 24 hours; 1 tick 1 minute
# run_length = 5 * 24 * 60

# run time 1000 ticks
run_length = 7200

dfs_dict = {}

# Run scenario 0 with only one seed
# scenario = 0
# seed = 1
# sim_model = BangladeshModel(seed=seed, scenario=scenario)
# for i in range(run_length):
#     sim_model.step()
# df = Vehicle.create_dataframe()
# dfs_dict = {(scenario, seed): df}



# Run scenarios 1-8 with 10 seeds each
scenarios = range(1, 9)
seeds = range(1, 11)

for scenario in scenarios:
    dfs_duration = []  # List to store vehicle duration dataframes for each seed
    dfs_delay = []     # List to store vehicle delay dataframes for each seed

    for seed in seeds:
        sim_model = BangladeshModel(seed=seed, scenario=scenario)
        for i in range(run_length):
            sim_model.step()
        df_duration = Vehicle.create_dataframe()
        df_delay = Vehicle.create_vehicle_delay_dataframe()

        # Add a column for seed number to the dataframes
        df_duration['Seed'] = seed
        df_delay['Seed'] = seed

        dfs_duration.append(df_duration)
        dfs_delay.append(df_delay)

    # Combine dataframes for each seed into one dataframe for each scenario
    combined_df_duration = pd.concat(dfs_duration, ignore_index=True)
    combined_df_delay = pd.concat(dfs_delay, ignore_index=True)

    # Save combined dataframes to CSV files
    filename_duration = f'duration_scenario_{scenario}.csv'
    combined_df_duration.to_csv(filename_duration, index=False)

    filename_delay = f'delay_scenario_{scenario}.csv'
    combined_df_delay.to_csv(filename_delay, index=False)
# Plot the average time per scenario
# Create an empty list to store average delay time for each scenario
l_average_model_time = []

# Iterate over scenarios to calculate average delay time for each scenario
for scenario in range(9):  # Assuming scenarios are numbered from 0 to 8
    total_time_in_model = 0
    total_trucks = 0  # Initialize total trucks counter
    num_seeds = 0
    for seed in range(1, 11):  # Seeds range from 1 to 10
        if (scenario, seed) in dfs_dict:
            df = dfs_dict[(scenario, seed)]
            total_time_in_model += df['Time_In_Model'].sum()
            total_trucks += len(df)  # Count the number of rows in the DataFrame, which represents the number of trucks
            num_seeds += 1
    if num_seeds > 0:
        average_time_per_truck = total_time_in_model / total_trucks  # Calculate average time per truck
        l_average_model_time.append(average_time_per_truck)
    else:
        l_average_model_time.append(0)

# Create an empty list to store dataframes for each scenario
scenario_dataframes = []

for scenario in scenarios:
    # Read duration and delay CSV files for the current scenario
    filename_duration = f'duration_scenario_{scenario}.csv'
    filename_delay = f'delay_scenario_{scenario}.csv'
    df_duration = pd.read_csv(filename_duration)
    df_delay = pd.read_csv(filename_delay)

    # Extract unique vehicle IDs from the duration dataframe
    unique_vehicle_ids_duration = set(df_duration['Unique_ID'])

    # Filter rows from the delay dataframe where vehicle ID is in the duration dataframe
    filtered_delay_df = df_delay[df_delay['Vehicle_ID'].isin(unique_vehicle_ids_duration)]

    # Add the filtered delay dataframe to the list
    scenario_dataframes.append(filtered_delay_df)

# Concatenate dataframes from all scenarios
delays_total_df = pd.concat(scenario_dataframes, ignore_index=True)

# Save the combined dataframe to a CSV file
delays_total_df.to_csv('delays_total.csv', index=False)

# Read the combined duration files for each scenario
dfs_dict = {}
for scenario in range(1, 9):
    file_name = f'duration_scenario_{scenario}.csv'
    df = pd.read_csv(file_name)
    dfs_dict[scenario] = df

# Calculate average duration for each scenario
average_durations = {}
for scenario, df in dfs_dict.items():
    average_duration = df['Time_In_Model'].mean()
    average_durations[scenario] = average_duration

# Create a DataFrame to store average driving times
average_durations_df = pd.DataFrame(list(average_durations.items()), columns=['Scenario', 'Average_Duration'])

# Write the DataFrame to a CSV file
average_durations_df.to_csv('average_driving_times.csv', index=False)


## This part creates a new csv called cumulative_bridge_delay which shows all the bridges and their cumulative delays
## over all the runs in the scenario's 1-7
# List of scenarios (1 to 7)

scenarios = range(1, 8)

# Dictionary to store cumulative delay time for each bridge
bridge_delay_dict = {}

# Iterate over scenarios
for scenario in scenarios:
    # Read delay CSV file for the current scenario
    filename_delay = f'delay_scenario_{scenario}.csv'
    df_delay = pd.read_csv(filename_delay)

    # Group by bridge ID and sum the delay times
    bridge_delay_scenario = df_delay.groupby('Bridge_ID')['Delay'].sum()

    # Update the cumulative delay dictionary
    for bridge_id, delay_time in bridge_delay_scenario.items():
        if bridge_id in bridge_delay_dict:
            bridge_delay_dict[bridge_id] += delay_time
        else:
            bridge_delay_dict[bridge_id] = delay_time

# Create a dataframe from the cumulative delay dictionary
bridge_delay_df = pd.DataFrame(list(bridge_delay_dict.items()), columns=['Bridge_ID', 'Cumulative_Delay'])

# Round off the delay times to whole numbers
bridge_delay_df['Cumulative_Delay'] = bridge_delay_df['Cumulative_Delay'].round().astype(int)

# Convert the Bridge_ID column to type string
bridge_delay_df['Bridge_ID'] = bridge_delay_df['Bridge_ID'].astype(str)

# Sort the dataframe based on the largest delay to the smallest delay
bridge_delay_df = bridge_delay_df.sort_values(by='Cumulative_Delay', ascending=False)

# Save the dataframe to a CSV file
bridge_delay_df.to_csv('cumulative_bridge_delay.csv', index=False)

##below displays the bridges with the most delays
# Read the cumulative bridge delay CSV file
bridge_delay_df = pd.read_csv('cumulative_bridge_delay.csv')

# Sort the dataframe by cumulative delay in descending order
sorted_delay_df = bridge_delay_df.sort_values(by='Cumulative_Delay', ascending=False)

# Select the top 5 most delayed bridges
top_5_delayed_bridges = sorted_delay_df.head(5)

# Create a bar plot
plt.figure(figsize=(10, 6))
plt.barh(top_5_delayed_bridges['Bridge_ID'].astype(str), top_5_delayed_bridges['Cumulative_Delay'], color='skyblue')

# Add labels and title
plt.xlabel('Cumulative Delay (minutes)')
plt.ylabel('Bridge ID')
plt.title('Top 5 Most Delayed Bridges')

# Show the plot
plt.tight_layout()
plt.show()
