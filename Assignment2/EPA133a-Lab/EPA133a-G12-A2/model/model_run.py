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
run_length = 300

scenarios = range(9)
seeds = [1,2,3,4,5,6,7,8,9,10]

sim_model = BangladeshModel(seed=seed)

# Check if the seed is set
#print("SEED " + str(sim_model._seed))


# # One run with given steps
# for i in range(run_length):
#     sim_model.step()
#
# df = Vehicle.create_dataframe() #dataframe functie wordt aangeroepen, zodat df wordt gemaakt van de vehicle_duration
# print(df)

for scenario in scenarios:
    for seed in seeds:
        sim_model = BangladeshModel(seed=seed, scenario = scenario)  # Initialize model for each scenario and replicate
        for i in range(run_length):
            sim_model.step()  # Run the model for the specified number of steps
        df = Vehicle.create_dataframe()

