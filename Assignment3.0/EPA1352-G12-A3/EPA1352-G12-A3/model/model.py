from mesa import Model
from mesa.time import BaseScheduler
from mesa.space import ContinuousSpace
from components import Source, Sink, SourceSink, Bridge, Link, Intersection
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

    file_name = '../data/demo-4.csv'

    def __init__(self, seed=None, x_max=500, y_max=500, x_min=0, y_min=0):

        self.schedule = BaseScheduler(self)
        self.running = True
        self.path_ids_dict = defaultdict(lambda: pd.Series())
        self.space = None
        self.sources = []
        self.sinks = []

        # self.make_networkx()
        self.generate_model()


    # Assuming df is your DataFrame with similar structure
    # Group by Road
    def make_networkx(self, file):
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
                G.add_edge(source, target)

        # Add edges between sources and sinks within the same road
        for road in df['road'].unique():
            sourcesinks = df[(df['road'] == road) & (df['model_type'] == 'sourcesink')]
            for i in range(len(sourcesinks) - 1):
                source = sourcesinks.iloc[i]['id']
                target = sourcesinks.iloc[i + 1]['id']
                G.add_edge(source, target)

        # Add edges between sources and sinks of different roads through intersections
        for road1 in df['road'].unique():
            sourcesinks1 = df[(df['road'] == road1) & (df['model_type'] == 'sourcesink')]
            for road2 in df['road'].unique():
                if road1 != road2:
                    intersections = df[(df['road'] == road1) & (df['model_type'] == 'intersection')]
                    for source in sourcesinks1['id']:
                        for intersection in intersections['id']:
                            G.add_edge(source, intersection)

        # Visualize the graph
        pos = nx.get_node_attributes(G, 'pos')
        plt.figure(figsize=(10, 8))
        nx.draw(G, pos, with_labels=True, node_size=3000, node_color='lightblue', font_size=10, font_weight='bold')
        plt.show()
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
        # TODO You can also read in the road column to generate this list automatically
        roads = df['road'].unique()

        # Create a directed graph to represent the road network
        G = self.make_networkx(self.file_name)

        # Iterate over all pairs of source and sink roads
        for index, road_source_row in df[df['model_type'] == 'sourcesink'].iterrows():
            road_source_id = road_source_row['id']
            for index, road_sink_row in df[df['model_type'] == 'sourcesink'].iterrows():
                road_sink_id = road_sink_row['id']

                if road_source_id != road_sink_id:
                    shortest_path_forward = nx.shortest_path(G, source=road_source_id, target=road_sink_id)
                    shortest_path_backward = nx.shortest_path(G, source=road_sink_id, target=road_source_id)
                    self.path_ids_dict[(road_source_id, road_sink_id)] = shortest_path_forward
                    self.path_ids_dict[(road_sink_id, road_source_id)] = shortest_path_backward


            print('path ids dict', self.path_ids_dict)

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
                    agent = Link(row['id'], self, row['length'], name, row['road'])
                elif model_type == 'intersection':
                    if not row['id'] in self.schedule._agents:
                        agent = Intersection(row['id'], self, row['length'], name, row['road'])

                if agent:
                    self.schedule.add(agent)
                    y = row['lat']
                    x = row['lon']
                    self.space.place_agent(agent, (x, y))
                    agent.pos = (x, y)
        print('path_ids_dict', self.path_ids_dict)


    def get_random_route(self, source):
        """
        pick up a random route given an origin
        """
        while True:
            # different source and sink
            sink = self.random.choice(self.sinks)
            if sink is not source:
                break
        return self.path_ids_dict[source, sink]

    # TODO
    def get_route(self, source):
        return self.get_straight_route(source)

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
