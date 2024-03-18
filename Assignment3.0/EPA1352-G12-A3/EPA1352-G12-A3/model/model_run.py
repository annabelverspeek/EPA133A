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
run_length = 5 * 24 * 60

# seed = 1234567
#
# sim_model = BangladeshModel(seed=seed)
#
# # Check if the seed is set
# print("SEED " + str(sim_model._seed))
#
# # One run with given steps
# for i in range(run_length):
#     sim_model.step()

# create an empty dictionary dfs_dict
dfs_dict = {}

# Run scenario 0 with only one seed
scenario = 0
# use only one seed because no bridge will break
seed = 1
sim_model = BangladeshModel(seed=seed, scenario=scenario)

# creating a for loop: the number of iterations is determined by run_length
for i in range(run_length):
    sim_model.step()
df = Vehicle.create_dataframe()
print(df)

# storing the dataframe in the dictionary with the specified scenario
dfs_dict = {(scenario, seed): df}

# Run scenarios 1-4 with 10 seeds each
scenarios = range(1, 5)
seeds = range(1, 11)

# for each scenario multiple simulations are run with different seeds
for scenario in scenarios:
    for seed in seeds:
        sim_model = BangladeshModel(seed=seed, scenario=scenario)
        for i in range(run_length):
            sim_model.step()
        df = Vehicle.create_dataframe()
        dfs_dict[(scenario, seed)] = df

print(dfs_dict)


# Now we want to store the average time per truck per scenario
# Create an empty list
l_average_model_time = []

# Iterate over scenarios
for scenario in range(5):  # Assuming scenarios are numbered from 0 to 5
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

    # Save the DataFrame to a CSV file for the current scenario
    scenario_df.to_csv(f'scenario_{scenario}.csv', index=False)

# Plot the average time per truck for each scenario
plt.figure(figsize=(10, 6))
plt.bar(range(len(l_average_model_time)), l_average_model_time)
plt.title('Average Time in Model per Truck for Each Scenario')
plt.xlabel('Scenario')
plt.ylabel('Average Time in Model per Truck')
plt.xticks(range(len(l_average_model_time)), [0, 1, 2, 3, 4])  # Assuming scenarios are numbered from 0 to 5
plt.grid(False)
plt.show()

# Print a message indicating the process is finished
print("CSV files for average time per truck per seed for each scenario have been created.")