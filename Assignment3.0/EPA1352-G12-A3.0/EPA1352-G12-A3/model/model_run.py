# Import the packages that are needed.

from model import BangladeshModel
from components import Vehicle
import pandas as pd
import os
import matplotlib.pyplot as plt

"""
    This file: 
    - Runs the simulation
    - Is able to print outputs at the terminal
    - Stores the outputs in the 'output' map within model. 
"""

# Run simulation for a run_length of 7200 minutes.
run_length = 7200  # 5 days, 24 hours, 60 minutes per hour = 7200 minutes.

# Run scenario 0 for one seed where no bridges break down, the base case.
scenario = 0
seed = 1
sim_model = BangladeshModel(seed=seed, scenario=scenario)
for _ in range(run_length):
    sim_model.step()

# Store for scenario 0/seed 1 the time that a vehicle is within the model in a dataframe.
df = Vehicle.create_average_time_dataframe()
#print(df)

# Create DataFrame with seed and the average Time_In_Model for scenario 0
average_time_in_model = df['Time_In_Model'].mean()
data = {'Seed': seed, 'Time_In_Model': average_time_in_model}
df_scenario0 = pd.DataFrame(data, index=[0])

# Save all the outputs in a directory called 'output'
output_directory = 'output/'
# Create the output directory
os.makedirs(output_directory, exist_ok=True)
# Save data to CSV and put it in the output directory
filename = 'scenario_0_data.csv'
df_scenario0.to_csv(os.path.join(output_directory, filename), index=False)


# Now also run the simulation for the four scenarios with each 10 seeds
# Define scenarios and seeds
scenarios = range(1, 5)
seeds = range(1, 11)

# Run simulations for each scenario and seed
for scenario in scenarios:
    # Store the durations and the delays in a list
    dfs_duration = []
    dfs_delay = []

    for seed in seeds:
        sim_model = BangladeshModel(seed=seed, scenario=scenario)
        for _ in range(run_length):
            sim_model.step()
        # Create the dataframes for duration and delay information
        df_duration = Vehicle.create_average_time_dataframe()
        df_delay = Vehicle.create_vehicle_delay_dataframe()

        df_duration['Seed'] = seed
        df_duration['Scenario'] = scenario
        df_delay['Seed'] = seed

        dfs_duration.append(df_duration)
        #print(dfs_duration)
        dfs_delay.append(df_delay)


    combined_df_duration = pd.concat(dfs_duration, ignore_index=True)
    #print(combined_df_duration)
    combined_df_delay = pd.concat(dfs_delay, ignore_index=True)
    #combined_df_delay.to_csv('combined_delay_data.csv', index=False)
    #print(combined_df_delay)

    # Calculate average time in model per seed
    avg_time_per_seed = combined_df_duration.groupby('Seed')['Time_In_Model'].mean().reset_index()
    avg_time_per_seed.rename(columns={'Time_In_Model': 'Average_Time'}, inplace=True)
    #print(avg_time_per_seed)

    # Calculate average delay per seed
    sum_delay_per_seed = combined_df_delay.groupby('Seed')['Delay'].sum().reset_index()
    num_unique_vehicles = combined_df_duration['Unique_ID'].nunique()
    # print(num_unique_vehicles)
    avg_delay_per_seed = sum_delay_per_seed.copy()
    # print(avg_delay_per_seed)
    avg_delay_per_seed['Delay'] = avg_delay_per_seed['Delay'] / num_unique_vehicles
    avg_delay_per_seed.rename(columns={'Delay': 'Average_Delay'}, inplace=True)

    # Merge all dataframes
    final_df = pd.merge(avg_time_per_seed, avg_delay_per_seed, on='Seed', how='outer')

    # Construct the files per scenario and place them in the output directory
    filename = f'metrics_scenario_{scenario}.csv'
    final_df.to_csv(os.path.join(output_directory, filename), index=False)

# Plot the average time per scenario in a bar plot
# For some reason this code only plotted scenario 4, we provided the code here but didn't use it because it doesn't
# show us the output we want.

# #Calculate average time in model per scenario
# avg_times_per_scenario = combined_df_duration.groupby('Scenario')['Time_In_Model'].mean().reset_index()
#
# # Plotting the bar chart
# plt.figure(figsize=(10, 6))
# plt.bar(avg_times_per_scenario['Scenario'], avg_times_per_scenario['Time_In_Model'], color='skyblue')
# plt.xlabel('Scenario')
# plt.ylabel('Average Time in Model')
# plt.title('Average Time in Model for Each Scenario')
# plt.xticks(avg_times_per_scenario['Scenario'])
# plt.show()

print("CSV files for each scenario have been created.")
