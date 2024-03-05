from mesa import Agent
from enum import Enum
import pandas as pd
import random

file = 'transformed_data_N1.csv'
df_N1 = pd.read_csv(file)
#print(df_N1.head())

# Initialize vehicle_durations list and the vehicle delay list
vehicle_durations = []
vehicle_delay = []
# total_delay_time = 0
# for i in Vehicle.vehicle_delay:
#     total_delay_time += i
# return total_delay_time
# ---------------------------------------------------------------
class Infra(Agent):
    """
    Base class for all infrastructure components

    Attributes
    __________
    vehicle_count : int
        the number of vehicles that are currently in/on (or totally generated/removed by)
        this infrastructure component

    length : float
        the length in meters
    ...

    """

    def __init__(self, unique_id, model, length=0,
                 name='Unknown', road_name='Unknown'):
        super().__init__(unique_id, model)
        self.length = length
        self.name = name
        self.road_name = road_name
        self.vehicle_count = 0

    def step(self):
        pass

    def __str__(self):
        return type(self).__name__ + str(self.unique_id)


# ---------------------------------------------------------------
class Bridge(Infra):
    """
    Creates delay time

    Attributes
    __________
    condition:
        condition of the bridge

    delay_time: int
        the delay (in ticks) caused by this bridge
    ...

    """
    #
    # def __init__(self, unique_id, model, length=0,
    #              name='Unknown', road_name='Unknown', condition='Unknown'):
    #     super().__init__(unique_id, model, length, name, road_name)
    #
    #     self.condition = condition
    #
    #     # TODO
    #     self.delay_time = self.random.randrange(0, 10)
    #     # print(self.delay_time)
    #
    # # TODO
    # def get_delay_time(self):
    #     return self.delay_time

    def __init__(self, unique_id, model, length=0, name='Unknown', road_name='Unknown', condition='Unknown'):
        super().__init__(unique_id, model, length, name, road_name)


        self.broken = False

        self.get_delay_time()


    def get_delay_time(self): #toegevoegd, om delay time te berekenen
        self.break_bridge() #De bridges door het ingevoerde scenario --> zie def break_bridge()
        if not self.broken:
            self.delay_time = 0
        else:
            if self.length > 200: #Length wordt bepaald in model.py dus kunnen we gwn gebruiken
                self.delay_time = random.triangular(1, 2, 4) * 60  # Convert hours to minutes
            elif 50 <= self.length <= 200:
                self.delay_time = random.uniform(45, 90)
            elif 10 <= self.length < 50:
                self.delay_time = random.uniform(15, 60)
            else:
                self.delay_time = random.uniform(10, 20)
        return self.delay_time

    #?

    def get_condition(self): #condition wordt nog niet bepaald in model.py, dus zelf invoeren door deze functie
        for index, row in df_N1.iterrows():
            if self.unique_id == row['id']:
                self.condition = row['condition']
        return self.condition

    # def get_delay_time(self):
    #     return self.delay_time


    def break_bridge(self): #Deze functie wordt gebruikt om de delay time te bepalen voor een brug.
        condition = self.get_condition()
        if condition == 'A' and random.random() < self.model.cat_a_percent: #self.model.cat_a_percent wordt bepaald in model.py met de functie: def initialize_scenario(self, scenario): geeft voor elke categorie aan wat de kans is dat de brug breekt.
            self.broken = True
            self.get_delay_time()

        if condition == 'B' and random.random() < self.model.cat_b_percent:
            self.broken = True
            self.get_delay_time()

        if condition == 'C' and random.random() < self.model.cat_c_percent:
            self.broken = True
            self.get_delay_time()

        if condition == 'D' and random.random() < self.model.cat_d_percent:
            self.broken = True
            self.get_delay_time()
        return self.broken #, self.get_delay_time()


# ---------------------------------------------------------------
class Link(Infra):
    pass


# ---------------------------------------------------------------
class Sink(Infra): #Hier is niks aan veranderd
    """
    Sink removes vehicles

    Attributes
    __________
    vehicle_removed_toggle: bool
        toggles each time when a vehicle is removed
    ...

    """
    vehicle_removed_toggle = False

    def remove(self, vehicle):
        self.model.schedule.remove(vehicle)
        self.vehicle_removed_toggle = not self.vehicle_removed_toggle
        #print(str(self) + ' REMOVE ' + str(vehicle))


# ---------------------------------------------------------------

class Source(Infra):
    """
    Source generates vehicles

    Class Attributes:
    -----------------
    truck_counter : int
        the number of trucks generated by ALL sources. Used as Truck ID!

    Attributes
    __________
    generation_frequency: int
        the frequency (the number of ticks) by which a truck is generated

    vehicle_generated_flag: bool
        True when a Truck is generated in this tick; False otherwise
    ...

    """

    truck_counter = 0
    generation_frequency = 5
    vehicle_generated_flag = False

    def step(self):
        if self.model.schedule.steps % self.generation_frequency == 0:
            self.generate_truck()
        else:
            self.vehicle_generated_flag = False

    def generate_truck(self):
        """
        Generates a truck, sets its path, increases the global and local counters
        """
        try:
            agent = Vehicle('Truck' + str(Source.truck_counter), self.model, self)
            if agent:
                self.model.schedule.add(agent)

                agent.set_path()
                Source.truck_counter += 1
                self.vehicle_count += 1
                self.vehicle_generated_flag = True
                print(str(self) + " GENERATE " + str(agent))
        except Exception as e:
            print("Oops!", e.__class__, "occurred.")


# ---------------------------------------------------------------
class SourceSink(Source, Sink):
    """
    Generates and removes trucks
    """
    pass


# ---------------------------------------------------------------
class Vehicle(Agent): #Eigenlijk niks in veranderd behalve de dataframe van de vehicle_duration gemaakt.
    """

    Attributes
    __________
    speed: float
        speed in meter per minute (m/min)

    step_time: int
        the number of minutes (or seconds) a tick represents
        Used as a base to change unites

    state: Enum (DRIVE | WAIT)
        state of the vehicle

    location: Infra
        reference to the Infra where the vehicle is located

    location_offset: float
        the location offset in meters relative to the starting point of
        the Infra, which has a certain length
        i.e. location_offset < length

    path_ids: Series
        the whole path (origin and destination) where the vehicle shall drive
        It consists the Infras' uniques IDs in a sequential order

    location_index: int
        a pointer to the current Infra in "path_ids" (above)
        i.e. the id of self.location is self.path_ids[self.location_index]

    waiting_time: int
        the time the vehicle needs to wait

    generated_at_step: int
        the timestamp (number of ticks) that the vehicle is generated

    removed_at_step: int
        the timestamp (number of ticks) that the vehicle is removed
    ...

    """

    # 50 km/h translated into meter per min
    speed = 50 * 1000 / 60
    # One tick represents 1 minute
    step_time = 1

    vehicle_durations  = []
    vehicle_delay = []

    class State(Enum):
        DRIVE = 1
        WAIT = 2

    def __init__(self, unique_id, model, generated_by,
                 location_offset=0, path_ids=None):
        super().__init__(unique_id, model)
        self.generated_by = generated_by
        self.generated_at_step = model.schedule.steps
        self.location = generated_by
        self.location_offset = location_offset
        self.pos = generated_by.pos
        self.path_ids = path_ids

        # default values
        self.state = Vehicle.State.DRIVE
        self.location_index = 0
        self.waiting_time = 0
        self.waited_at = None
        self.removed_at_step = None
        self.time_in_model = None

    def __str__(self):
        return "Vehicle" + str(self.unique_id) + \
               " +" + str(self.generated_at_step) + " -" + str(self.removed_at_step) + \
               " " + str(self.state) + '(' + str(self.waiting_time) + ') ' + \
               str(self.location) + '(' + str(self.location.vehicle_count) + ') ' + str(self.location_offset)

    def set_path(self):
        """
        Set the origin destination path of the vehicle
        """
        self.path_ids = self.model.get_random_route(self.generated_by.unique_id)

    def step(self):
        """
        Vehicle waits or drives at each step
        """
        if self.state == Vehicle.State.WAIT:
            self.waiting_time = max(float(self.waiting_time) - 1, 0)
            if float(self.waiting_time) == 0:
                self.waited_at = self.location
                self.state = Vehicle.State.DRIVE

        if self.state == Vehicle.State.DRIVE:
            self.drive()

        """
        To print the vehicle trajectory at each step
        """
        print(self)

    def drive(self):

        # the distance that vehicle drives in a tick
        # speed is global now: can change to instance object when individual speed is needed
        distance = Vehicle.speed * Vehicle.step_time
        distance_rest = self.location_offset + distance - self.location.length

        if distance_rest > 0:
            # go to the next object
            self.drive_to_next(distance_rest)
        else:
            # remain on the same object
            self.location_offset += distance

    def drive_to_next(self, distance):
        """
        vehicle shall move to the next object with the given distance
        """

        self.location_index += 1
        next_id = self.path_ids[self.location_index]
        next_infra = self.model.schedule._agents[next_id]  # Access to protected member _agents

        if isinstance(next_infra, Sink):
            # arrive at the sink
            #print("Vehicle {} arrived at the sink".format(self.unique_id))  # Debug print statement
            self.arrive_at_next(next_infra, 0)
            self.removed_at_step = self.model.schedule.steps
            self.time_in_model = self.removed_at_step - self.generated_at_step
            #print('I was in the model for:', self.time_in_model) #Om te testen
            Vehicle.vehicle_durations.append({'Unique_ID': self.unique_id, 'Time_In_Model': self.time_in_model})
            print(vehicle_durations)
            self.location.remove(self)
            return
        elif isinstance(next_infra, Bridge):
            self.waiting_time = next_infra.get_delay_time()
            if float(self.waiting_time) > 0:
                # arrive at the bridge and wait
                self.arrive_at_next(next_infra, 0)
                self.state = Vehicle.State.WAIT
                #Vehicle.vehicle_delay.append({'Unique_ID': self.unique_id, 'Delay_In_Model': self.waiting_time})
                return
            # else, continue driving


        if next_infra.length > distance:
            # stay on this object:
            self.arrive_at_next(next_infra, distance)
        else:
            # drive to next object:
            self.drive_to_next(distance - next_infra.length)

    def arrive_at_next(self, next_infra, location_offset):
        """
        Arrive at next_infra with the given location_offset
        """
        self.location.vehicle_count -= 1
        self.location = next_infra
        self.location_offset = location_offset
        self.location.vehicle_count += 1

    def create_dataframe(): #Dit maakt een dataframe om te kunnen terug kijken wat de tijd is dat een bepaalde vehicle in het model is geweest
        """
        Create a DataFrame from the vehicle_durations list.
        """
        df = pd.DataFrame(Vehicle.vehicle_durations) #total_delay_time)
        return df


# EOF -----------------------------------------------------------


