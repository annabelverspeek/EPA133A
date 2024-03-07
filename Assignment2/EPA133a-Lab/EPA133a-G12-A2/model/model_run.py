from model import BangladeshModel
from components import Vehicle
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
scenario = 0
seed = 1
sim_model = BangladeshModel(seed=seed, scenario=scenario)
for i in range(run_length):
    sim_model.step()
df = Vehicle.create_dataframe()
print(df)
dfs_dict = {(scenario, seed): df}

# Run scenarios 1-8 with 10 seeds each
scenarios = [1,8]
seeds = range(1, 3)
for scenario in scenarios:
    for seed in seeds:
        sim_model = BangladeshModel(seed=seed, scenario=scenario)
        for i in range(run_length):
            sim_model.step()
        df = Vehicle.create_dataframe()
        dfs_dict[(scenario, seed)] = df

print(dfs_dict)

# Plot the average time per scenario
# Create an empty list to store average delay time for each scenario
# l_average_model_time = []
# #
# # # Iterate over scenarios to calculate average delay time for each scenario
# for scenario in [0,1,8]:  # Assuming scenarios are numbered from 0 to 8
#     total_time_in_model = 0
#     total_trucks = 0  # Initialize total trucks counter
#     num_seeds = 0
#     for seed in range(1, 3):  # Seeds range from 1 to 10
#         if (scenario, seed) in dfs_dict:
#             df = dfs_dict[(scenario, seed)]
#             total_time_in_model += df['Time_In_Model'].sum()
#             total_trucks += len(df)  # Count the number of rows in the DataFrame, which represents the number of trucks
#             num_seeds += 1
#     if num_seeds > 0:
#         average_time_per_truck = total_time_in_model / total_trucks  # Calculate average time per truck
#         l_average_model_time.append(average_time_per_truck)
#     else:
#         l_average_model_time.append(0)
#
#
# plt.figure(figsize=(10, 6))
# plt.bar(range(3), l_average_model_time)
# plt.title('Average Time in Model per Truck for Each Scenario')
# plt.xlabel('Scenario')
# plt.ylabel('Average Time in Model per Truck')
# plt.xticks(range(3))  # Assuming scenarios are numbered from 0 to 2
# plt.grid(False)
# plt.show()
#
# # Iterate over scenarios
# for scenario in [0,1,8]:  # Assuming scenarios are numbered from 0 to 8
#     # Create an empty list to store DataFrames for each seed
#     dfs = []
#
#     # Iterate over seeds
#     for seed in range(1, 3):  # Seeds range from 1 to 10
#         total_time_in_model = 0
#         num_trucks = 0
#         if (scenario, seed) in dfs_dict:
#             df = dfs_dict[(scenario, seed)]
#             total_time_in_model = df['Time_In_Model'].sum()
#             num_trucks = len(df)
#
#         average_time_per_truck = total_time_in_model / num_trucks if num_trucks > 0 else 0
#
#         # Create a DataFrame for the current seed
#         seed_df = pd.DataFrame({'Seed': [seed], 'Average_Time_In_Model': [average_time_per_truck]})
#         dfs.append(seed_df)
#
#     # Concatenate DataFrames for all seeds into one DataFrame for the current scenario
#     scenario_df = pd.concat(dfs, ignore_index=True)
#
#     # Save the DataFrame to a CSV file for the current scenario
#     scenario_df.to_csv(f'scenario_{scenario}_average_time_per_truck.csv', index=False)
#
# # Print a message indicating the process is finished
# print("CSV files for average time per truck per seed for each scenario have been created.")



# Create an empty list to store average time per truck per scenario
l_average_model_time = []

# Create an empty list to store DataFrames for each scenario
dfs_combined = []

# Iterate over scenarios
for scenario in [0, 1, 8]:  # Assuming scenarios are numbered from 0 to 8
    total_time_in_model = 0
    total_trucks = 0  # Initialize total trucks counter
    num_seeds = 0

    # Create an empty list to store DataFrames for each seed
    dfs = []

    # Iterate over seeds
    for seed in range(1, 11):  # Seeds range from 1 to 10
        if (scenario, seed) in dfs_dict:
            df = dfs_dict[(scenario, seed)]
            total_time_in_model += df['Time_In_Model'].sum()
            total_trucks += len(df)  # Count the number of rows in the DataFrame, which represents the number of trucks
            num_seeds += 1

            # Calculate average time per truck for the current seed
            average_time_per_truck = df['Time_In_Model'].sum() / len(df) if len(df) > 0 else 0

            # Create a DataFrame for the current seed
            seed_df = pd.DataFrame({'Seed': [seed], 'Average_Time_In_Model': [average_time_per_truck]})
            dfs.append(seed_df)

    # Concatenate DataFrames for all seeds into one DataFrame for the current scenario
    scenario_df = pd.concat(dfs, ignore_index=True)

    # Calculate average time per truck for the current scenario
    average_time_per_scenario = total_time_in_model / total_trucks if total_trucks > 0 else 0
    l_average_model_time.append(average_time_per_scenario)

    # Calculate average delay time for the current scenario
    # average_delay_time = 0
    # if scenario != 0:
    #     df_scenario_0 = dfs_dict[(0, 1)]
    #     average_time_per_scenario_0 = df_scenario_0['Time_In_Model'].mean()
    #     average_delay_time = average_time_per_scenario - average_time_per_scenario_0
    # scenario_df['Average_Delay_Time'] = average_delay_time

    # Save the DataFrame to a CSV file for the current scenario
    scenario_df.to_csv(f'scenario_{scenario}.csv', index=False)

# Plot the average time per truck for each scenario
plt.figure(figsize=(10, 6))
plt.bar(range(len(l_average_model_time)), l_average_model_time)
plt.title('Average Time in Model per Truck for Each Scenario')
plt.xlabel('Scenario')
plt.ylabel('Average Time in Model per Truck')
plt.xticks(range(len(l_average_model_time)), [0, 1, 8])  # Assuming scenarios are numbered from 0 to 8
plt.grid(False)
plt.show()

# Print a message indicating the process is finished
print("CSV files for average time per truck per seed for each scenario have been created.")


