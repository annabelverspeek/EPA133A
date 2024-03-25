from mesa import Model
from mesa.time import BaseScheduler
from mesa.space import ContinuousSpace
from components import Source, Sink, SourceSink, Bridge, Link, Vehicle, Intersection
import pandas as pd
from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt
from itertools import combinations


# ---------------------------------------------------------------
def set_lat_lon_bound(lat_min, lat_max, lon_min, lon_max, edge_ratio=0.02):
    """
    Set the HTML continuous space canvas bounding box (for visualization)
    give the min and max latitudes and Longitudes in Decimal Degrees (DD)

    Add white borders at edges (default 2%) of the bounding box
    """

    lat_edge = (lat_max - lat_min) * edge_ratio
    lon_edge = (lon_max - lon_min) * edge_ratio

    x_max = lon_max + lon_edge
    y_max = lat_min - lat_edge
    x_min = lon_min - lon_edge
    y_min = lat_max + lat_edge
    return y_min, y_max, x_min, x_max


# ---------------------------------------------------------------
class BangladeshModel(Model):
    """
    The main (top-level) simulation model

    One tick represents one minute; this can be changed
    but the distance calculation need to be adapted accordingly

    Class Attributes:
    -----------------
    step_time: int
        step_time = 1 # 1 step is 1 min

    path_ids_dict: defaultdict
        Key: (origin, destination)
        Value: the shortest path (Infra component IDs) from an origin to a destination

        Only straight paths in the Demo are added into the dict;
        when there is a more complex network layout, the paths need to be managed differently

    sources: list
        all sources in the network

    sinks: list
        all sinks in the network

    """

    step_time = 1

    file_name = '../model/final_df_manual7.csv'

    def __init__(self, seed=None, x_max=500, y_max=500, x_min=0, y_min=0, scenario = 0):

        self.schedule = BaseScheduler(self)
        self.running = True
        self.path_ids_dict = defaultdict(lambda: pd.Series())
        self.space = None
        self.sources = []
        self.sinks = []
        self.cat_a_percent = None
        self.cat_b_percent = None
        self.cat_c_percent = None
        self.cat_d_percent = None
        self.scenario = scenario

        self.initialize_scenario(self.scenario)

        self.generate_model()

        Vehicle.vehicle_durations = []
        Vehicle.vehicle_delay = []

    def initialize_scenario(self, scenario):
        """
        This function is created to initialize the four scenarios.
        cat_a_percent etc. is used in the function break_bridges in components.py.

        """
        scenario_map = {
            0: (0.0, 0.0, 0.0, 0.0),
            1: (0.0, 0.0, 0.0, 0.05),
            2: (0.0, 0.0, 0.05, 0.1),
            3: (0.0, 0.05, 0.1, 0.2),
            4: (0.05, 0.1, 0.2, 0.4),
        }

        if scenario in scenario_map:
            self.cat_a_percent, self.cat_b_percent, self.cat_c_percent, self.cat_d_percent = scenario_map[scenario]
        else:
            raise ValueError("Invalid scenario number")

        return self.cat_a_percent, self.cat_b_percent, self.cat_c_percent, self.cat_d_percent

    def make_networkx(self, file):
        """
        This function creates a networkx graph based on the file created in transform_n1_and_n2.
        The graph is used to determine the shortest path for a given sink and source.
        """
        df = pd.read_csv(file)
        # Create a directed graph
        G = nx.Graph()

        # Add nodes with positions
        for _, row in df.iterrows():
            node_id = row['id']
            pos = (row['lat'], row['lon'])
            G.add_node(node_id, pos=pos)

        # Add edges between consecutive nodes in the same road
        for road in df['road'].unique():
            road_df = df[df['road'] == road]
            for i in range(len(road_df) - 1):
                source = road_df.iloc[i]['id']
                target = road_df.iloc[i + 1]['id']
                weight = road_df.iloc[i]['length']*1000  # Get length from the 'length' column
                G.add_edge(source, target, weight=weight)

        # Plot the networkx graph
        # pos = nx.get_node_attributes(G, 'pos')
        # plt.figure(figsize=(10, 8))
        # nx.draw(G, pos, with_labels=False, node_size=10, node_color='blue', font_size=10, font_weight='bold')
        # plt.show()

        return G

    def generate_model(self):
        """
        generate the simulation model according to the csv file component information

        Warning: the labels are the same as the csv column labels

        """

        df = pd.read_csv(self.file_name)

        roads = df['road'].unique().tolist()

        df_objects_all = []
        for road in roads:
            # Select all the objects on a particular road in the original order as in the cvs
            df_objects_on_road = df[df['road'] == road]

            if not df_objects_on_road.empty:
                df_objects_all.append(df_objects_on_road)
        # a list of names of roads to be generated
        roads = df['road'].unique()

        # Create a directed graph to represent the road network
        G = self.make_networkx(self.file_name)

        # Iterate over all pairs of source and sink roads
        for index, road_source_row in df[df['model_type'] == 'sourcesink'].iterrows():
            road_source_id = road_source_row['id']
            for index, road_sink_row in df[df['model_type'] == 'sourcesink'].iterrows():
                road_sink_id = road_sink_row['id']

                if road_source_id != road_sink_id:
                    # If source and sink are not the same, calculate the shortest path for this source/sink combination.
                    path_ids = nx.shortest_path(G, source=road_source_id, target=road_sink_id, weight = 'length')
                    # Place the path into the dictionary path_ids_dict
                    self.path_ids_dict[(road_source_id, road_sink_id)] = path_ids

        # print('path ids dict', self.path_ids_dict)

        # put back to df with selected roads so that min and max and be easily calculated
        df = pd.concat(df_objects_all)
        y_min, y_max, x_min, x_max = set_lat_lon_bound(
            df['lat'].min(),
            df['lat'].max(),
            df['lon'].min(),
            df['lon'].max(),
            0.05
        )

        # ContinuousSpace from the Mesa package;
        # not to be confused with the SimpleContinuousModule visualization
        self.space = ContinuousSpace(x_max, y_max, True, x_min, y_min)

        for df in df_objects_all:
            for _, row in df.iterrows():  # index, row in ...

                # create agents according to model_type
                model_type = row['model_type'].strip()
                agent = None

                name = row['name']
                if pd.isna(name):
                    name = ""
                else:
                    name = name.strip()

                if model_type == 'source':
                    agent = Source(row['id'], self, row['length'], name, row['road'])
                    self.sources.append(agent.unique_id)
                elif model_type == 'sink':
                    agent = Sink(row['id'], self, row['length'], name, row['road'])
                    self.sinks.append(agent.unique_id)
                elif model_type == 'sourcesink':
                    agent = SourceSink(row['id'], self, row['length'], name, row['road'])
                    self.sources.append(agent.unique_id)
                    self.sinks.append(agent.unique_id)
                elif model_type == 'bridge':
                    agent = Bridge(row['id'], self, row['length'], name, row['road'], row['condition'])
                elif model_type == 'link':
                    agent = Link(row['id'], self, row['length']*1000, name, row['road'])
                elif model_type == 'intersection':
                    if not row['id'] in self.schedule._agents:
                        agent = Intersection(row['id'], self, row['length'], name, row['road'])

                if agent:
                    self.schedule.add(agent)
                    y = row['lat']
                    x = row['lon']
                    self.space.place_agent(agent, (x, y))
                    agent.pos = (x, y)


    def get_random_route(self, source):
        """
        pick up a random route given an origin
        get the shortest path for this source/sink combination out of path_ids_dict.
        """
        while True:
            # different source and sink
            sink = self.random.choice(self.sinks)
            if sink is not source:
                break
        return self.path_ids_dict[source, sink]


    def get_route(self, source):
        """
        This function gets the random route based on the function get_random_route.
        We are not using the get_straight_route anymore.
        """
        return self.get_random_route(source)

    # This function get_straight_route is currently not used, we are using get_random_route.
    def get_straight_route(self, source):
        """
        pick up a straight route given an origin
        """
        return self.path_ids_dict[source, None]

    def step(self):
        """
        Advance the simulation by one step.
        """
        self.schedule.step()

# EOF -----------------------------------------------------------
