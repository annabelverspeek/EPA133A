from model import BangladeshModel
from components import Vehicle
import pandas as pd
import os
import matplotlib.pyplot as plt
"""
    Run simulation
    Print output at terminal
"""

# Run simulation parameters
run_length = 5 * 24 * 60  # 5 days, 24 hours, 60 minutes per hour

scenario = 0
seed = 1
sim_model = BangladeshModel(seed=seed, scenario=scenario)
for _ in range(run_length):
    sim_model.step()
df = Vehicle.create_average_time_dataframe()
print(df)

# Create DataFrame with seed and Time_In_Model values
data = {'Seed': seed, 'Time_In_Model': df['Time_In_Model'].iloc[0]}
df_to_save = pd.DataFrame(data, index=[0])

# Save data to CSV
output_directory = 'output/'
# Ensure that the output directory exists, create it if it doesn't
os.makedirs(output_directory, exist_ok=True)
filename = 'scenario_0_seed_1_data.csv'

df_to_save.to_csv(os.path.join(output_directory, filename), index=False)

# Define scenarios and seeds
scenarios = range(1, 5)
seeds = range(1, 11)

# Run simulations for each scenario and seed
for scenario in scenarios:
    dfs_duration = []
    dfs_delay = []
    bridge_delay_dict = {}  # Initialize dictionary for cumulative delays

    for seed in seeds:
        sim_model = BangladeshModel(seed=seed, scenario=scenario)
        for _ in range(run_length):
            sim_model.step()
        df_duration = Vehicle.create_average_time_dataframe()
        df_delay = Vehicle.create_vehicle_delay_dataframe()

        df_duration['Seed'] = seed
        df_delay['Seed'] = seed

        dfs_duration.append(df_duration)
        dfs_delay.append(df_delay)

        # Calculate cumulative delays per seed
        df_delay_seed = df_delay[df_delay['Seed'] == seed]
        if not df_delay_seed.empty:
            first_vehicle_delay = df_delay_seed.iloc[0]['Delay']  # Get delay of the first vehicle
            bridge_delay_dict[seed] = first_vehicle_delay
        else:
            bridge_delay_dict[seed] = None


    combined_df_duration = pd.concat(dfs_duration, ignore_index=True)
    combined_df_delay = pd.concat(dfs_delay, ignore_index=True)

    # Calculate average time in model per seed
    avg_time_per_seed = combined_df_duration.groupby('Seed')['Time_In_Model'].mean().reset_index()
    avg_time_per_seed.rename(columns={'Time_In_Model': 'Average_Time'}, inplace=True)

    # Calculate average delay per seed
    avg_delay_per_seed = combined_df_delay.groupby('Seed')['Delay'].mean().reset_index()  # Replace 'Delay_Column_Name' with actual column name
    avg_delay_per_seed.rename(columns={'Delay': 'Average_Delay'}, inplace=True)

    # Create DataFrame for cumulative delays
    cumulative_delay_df = pd.DataFrame(list(bridge_delay_dict.items()), columns=['Seed', 'Cumulative_Delay'])

    # Merge all dataframes
    final_df = pd.merge(avg_time_per_seed, avg_delay_per_seed, on='Seed', how='outer')
    final_df = pd.merge(final_df, cumulative_delay_df, on='Seed', how='outer')


    # Construct the filename
    filename = f'metrics_scenario_{scenario}.csv'
    final_df.to_csv(os.path.join(output_directory, filename), index=False)

    # Save the DataFrame to CSV

# Plot the average time per scenario
l_average_model_time = []

# for scenario in range(5):
#     total_time_in_model = 0
#     total_trucks = 0
#     num_seeds = 0
#     for seed in range(1, 11):
#         if (scenario, seed) in dfs_dict:
#             df = dfs_dict[(scenario, seed)]
#             if 'Time_In_Model' in df:
#                 total_time_in_model += df['Time_In_Model'].sum()
#                 total_trucks += len(df)
#                 num_seeds += 1
#     if num_seeds > 0:
#         average_time_per_truck = total_time_in_model / total_trucks
#         l_average_model_time.append(average_time_per_truck)
#     else:
#         l_average_model_time.append(0)

# Create an empty list to store dataframes for each scenario
# scenario_dataframes = []
#
# for scenario in scenarios:
#     filename_duration = f'duration_scenario_{scenario}.csv'
#     filename_delay = f'delay_scenario_{scenario}.csv'
#     df_duration = pd.read_csv(filename_duration)
#     df_delay = pd.read_csv(filename_delay)
#
#     unique_vehicle_ids_duration = set(df_duration['Unique_ID'])
#
#     filtered_delay_df = df_delay[df_delay['Vehicle_ID'].isin(unique_vehicle_ids_duration)]
#
#     scenario_dataframes.append(filtered_delay_df)
#
# # Concatenate dataframes from all scenarios
# delays_total_df = pd.concat(scenario_dataframes, ignore_index=True)
#
# delays_total_df.to_csv('delays_total.csv', index=False)
#
# dfs_dict = {}
# for scenario in range(1, 5):
#     file_name = f'duration_scenario_{scenario}.csv'
#     df = pd.read_csv(file_name)
#     dfs_dict[scenario] = df
#
# average_durations = {}
# for scenario, df in dfs_dict.items():
#     if 'Time_In_Model' in df:
#         average_duration = df['Time_In_Model'].mean()
#         average_durations[scenario] = average_duration
#
# average_durations_df = pd.DataFrame(list(average_durations.items()), columns=['Scenario', 'Average_Duration'])
# average_durations_df.to_csv('average_driving_times.csv', index=False)
#
# # Calculate cumulative delays per scenario, per seed
# bridge_delay_dict = {}
#
# for scenario in scenarios:
#     filename_delay = f'delay_scenario_{scenario}.csv'
#     df_delay = pd.read_csv(filename_delay)
#
#     if not df_delay.empty:
#         for seed in seeds:
#             df_delay_seed = df_delay[df_delay['Seed'] == seed]
#             if not df_delay_seed.empty:
#                 first_vehicle_delay = df_delay_seed.iloc[0]['Delay']  # Get delay of the first vehicle
#                 bridge_delay_dict[(scenario, seed)] = first_vehicle_delay

# cumulative_delay_df = pd.DataFrame(list(bridge_delay_dict.items()), columns=['Scenario_Seed', 'Cumulative_Delay'])

# cumulative_delay_df.to_csv('cumulative_delay_per_scenario_per_seed.csv', index=False)

#Plot the average time per truck for each scenario
# plt.figure(figsize=(10, 6))
# plt.bar(range(len(l_average_model_time)), l_average_model_time)
# plt.title('Average Time in Model per Truck for Each Scenario')
# plt.xlabel('Scenario')
# plt.ylabel('Average Time in Model per Truck')
# plt.xticks(range(len(l_average_model_time)), [0, 1, 2, 3, 4])  # Assuming scenarios are numbered from 0 to 5
# plt.grid(False)
# plt.show()

#Print a message indicating the process is finished
print("CSV files for average time per truck per seed for each scenario have been created.")
