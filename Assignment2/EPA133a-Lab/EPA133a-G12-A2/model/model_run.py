from model import BangladeshModel
from components import Vehicle

"""
    Run simulation
    Print output at terminal
"""

# ---------------------------------------------------------------

# run time 5 x 24 hours; 1 tick 1 minute
# run_length = 5 * 24 * 60

# run time 1000 ticks
run_length = 100

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

    # Check if the seed is set
#print("SEED " + str(sim_model._seed))


# # One run with given steps
# for i in range(run_length):
#     sim_model.step()
#
# df = Vehicle.create_dataframe() #dataframe functie wordt aangeroepen, zodat df wordt gemaakt van de vehicle_duration
# print(df)

