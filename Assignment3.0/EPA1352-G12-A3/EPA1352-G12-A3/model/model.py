from mesa import Model
from mesa.time import BaseScheduler
from mesa.space import ContinuousSpace
from components import Source, Sink, SourceSink, Bridge, Link, Intersection
import pandas as pd
from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt


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
        G = nx.DiGraph()

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
    def generate_model(self):
        """
        generate the simulation model according to the csv file component information

        Warning: the labels are the same as the csv column labels
        """

        df = pd.read_csv(self.file_name)

        # a list of names of roads to be generated
        # TODO You can also read in the road column to generate this list automatically
        roads = ['N1', 'N2']


        df_sourcesinks = df[df['model_type'] == 'sourcesink']
        df_objects_all = []


        for road in roads:
            # Select all the objects on a particular road in the original order as in the cvs
            df_objects_on_road = df_sourcesinks[df_sourcesinks['road'] == road]

            if not df_objects_on_road.empty:
                df_objects_all.append(df_objects_on_road)

                sinksource_names = df_objects_on_road['sourcesink'].unique()

                pairs = list(combinations(sinksource_names, 2))

                for pair in pairs:
                    self.path_ids_dict[(road, pair[0], pair[1])] = df_objects_on_road['id'].tolist()



                """
                Set the path 
                1. get the serie of object IDs on a given road in the cvs in the original order
                2. add the (straight) path to the path_ids_dict
                3. put the path in reversed order and reindex
                4. add the path to the path_ids_dict so that the vehicles can drive backwards too
                """
                path_ids = df_objects_on_road['id'] # --> deze veranderen/deleten
                path_ids.reset_index(inplace=True, drop=True)
                self.path_ids_dict[path_ids[0], path_ids.iloc[-1]] = path_ids
                self.path_ids_dict[path_ids[0], None] = path_ids
                path_ids = path_ids[::-1]
                path_ids.reset_index(inplace=True, drop=True)
                self.path_ids_dict[path_ids[0], path_ids.iloc[-1]] = path_ids
                self.path_ids_dict[path_ids[0], None] = path_ids
                print('dictionary path', self.path_ids_dict)

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
    # def make_networkx(self, df):
    #     #graph = networkx nog te maken
    #         #include lon lat on position
    #         #include length on links as weight om shortest path te bepalen
    #     #return self.graph
    #
    #     # Assuming df is your DataFrame with similar structure
    #     # Group by Road
    #     grouped = df.groupby('road')
    #
    #     # Create Networkx Graphs
    #     graphs = {}
    #     for road, data in grouped:
    #         # Initialize graph
    #         G = nx.Graph()
    #
    #         # Add edges within the same road
    #         for _, row in data.iterrows():
    #             if row['model_type'] == 'link':
    #                 G.add_edge(row['id'], row['id'] + 1, weight=row['length'])
    #
    #         # Add edges to other start and end points
    #         for _, row in data.iterrows():
    #             if row['model_type'] == 'sourcesink':
    #                 for _, other_row in data.iterrows():
    #                     if other_row['model_type'] == 'sourcesink' and other_row['id'] != row['id']:
    #                         G.add_edge(row['id'], other_row['id'], weight=1)  # Assuming weight of 1 for now
    #
    #         graphs[road] = G
    #
    #     # Visualization (Optional)
    #     # Visualize graphs as needed
    #
    #     # Accessing a specific graph


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
    # in seth path def wordt moet dit worden aangeroepen (hij doet nu gwn get straight route)
    # Get random source and random sink
    # Find shortest path if in dictionary
    # not in distionary calculate shortest path.
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
