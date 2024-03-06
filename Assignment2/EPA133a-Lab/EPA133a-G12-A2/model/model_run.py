from model import BangladeshModel
from components import Vehicle
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
scenarios = range(1, 9)
seeds = range(1, 11)
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
#
# # # Plot the results
# # plt.figure(figsize=(10, 6))
# # plt.plot(range(3), l_average_model_time, marker='o', linestyle='-')
# # plt.title('Average Time in Model per Truck for Each Scenario')
# # plt.xlabel('Scenario')
# # plt.ylabel('Average Time in Model per Truck')
# # plt.xticks(range(3))  # Assuming scenarios are numbered from 0 to 8
# # plt.grid(True)
# # plt.show()
#
plt.figure(figsize=(10, 6))
plt.bar(range(9), l_average_model_time)
plt.title('Average Time in Model per Truck for Each Scenario')
plt.xlabel('Scenario')
plt.ylabel('Average Time in Model per Truck')
plt.xticks(range(9))  # Assuming scenarios are numbered from 0 to 2
plt.grid(False)
plt.show()


    # Check if the seed is set
#print("SEED " + str(sim_model._seed))


# # One run with given steps
# for i in range(run_length):
#     sim_model.step()
#
# df = Vehicle.create_dataframe() #dataframe functie wordt aangeroepen, zodat df wordt gemaakt van de vehicle_duration
# print(df)

