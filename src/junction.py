import configparser
import math
import pathlib
from src.direction import Direction
from src.lane import laneOrdering

class Junction:
    """The class object containing all of the junction information

    Attributes:
        directions(Dictionary): a dictionary containing all of the direction objects within the junction
        priorityNums(Array): an array containing the priority of each direction [North, East, South, West] in a range 1-4
        isPedestrianCrossing(Bool): whether or not this junction has a pedestrain crossing
        pedCrossPH(int): the number of pedestrian crossings that occur within an hour
        lastCrossingTime(float): the time that the last pedestrian crossing occured within the junction (during simulation)
        trafficSpeed(float): the speed of the traffic in m/s
        pedestrianCrossingTime(float): the time of a pedestrian crossing in seconds
        minimumGreenTime(float): the minimum amount of time that a green light is on
        vehicleLength(float): the average length of a vehicle in metres

    Methods:
        __init__(self, inputInformation): initialises the Junction object
        distributeVehicles(self): distributes vehicles within each direction to the lanes
        calculateDirectionPriority(self): given the distribution of traffic calculate the priority for each direction

    Notes:
        pedCrossPH, lastCrossingTime and pedestrianCrossingTime are only set if isPedestrianCrossing is equal to True.
        trafficSpeed, pedestrianCrossingTime, minimumGreenTime and vehicleLength are set using the system.cfg file.

    """

    def __init__(self, inputInformation):
        """Initialises the junction object

        Args:
            self(Junction): the junction that is being initialised
            inputInformation(Dictionary): a dictionary containing all of the information inputted by the user

        """
        # Read the configuration
        config_path = pathlib.Path(__file__).parent.absolute() / "system.cfg"
        config = configparser.ConfigParser()
        config.read(config_path)
        self.directions = {}
        self.directions['north'] = Direction(inputInformation[5], 'north', laneOrdering(inputInformation[1]))  # creates the direction for north
        self.directions['east'] = Direction(inputInformation[6], 'east', laneOrdering(inputInformation[2]))  # creates the direction for east
        self.directions['south'] = Direction(inputInformation[7], 'south', laneOrdering(inputInformation[3]))  # creates the direction for south
        self.directions['west'] = Direction(inputInformation[8], 'west', laneOrdering(inputInformation[4]))  # creates the direction for west

        self.priorityNums = None  # an array with the priorities of the junction directions

        self.isPedestrianCrossing = inputInformation[11]  # store whether or not this direction contains a pedestrian crossing
        if (self.isPedestrianCrossing == True):
            self.pedCrossPH = inputInformation[12]  # stores the amount of pedestrain crossing requests there will be in an hour
            self.lastCrossingTime = 0.0  # the the time of the last pedestrain crossing

        try:
            self.trafficSpeed = float(config.get('Settings', 'traffic_speed'))
            self.minimumGreenTime = float(config.get('Settings', 'minimum_green_light_time'))
            self.vehicleLength = float(config.get('Settings', 'vehicle_length'))


            if inputInformation[11] == True:  # checks whether there is a pedestrian crossing
                self.pedestrianCrossingTime = inputInformation[13] #float(config.get('Settings', 'pedestrian_crossing_time'))  # gets the pedestrain crossing time from the config file
        except:
            raise Exception(
                "There is a formatting error within the system.cfg file, please correct before system use.")

    def distributeVehicles(self):
        """
        Distributes the vehicles within each direction of the junction to provide optimal traffic flow

        Args:
            self: the junction that the lanes are in
        """
        self.directions['north'].distributeVehiclesByLane()
        self.directions['east'].distributeVehiclesByLane()
        self.directions['south'].distributeVehiclesByLane()
        self.directions['west'].distributeVehiclesByLane()

    def calculateDirectionPriority(self):
        """
        This calculates which directions have the highest VPH and returns a priority ranking based on those VPH

        Args:
            self(Junction): the junction which contains all of the directions

        Returns:
            array(int): an array storing the priority of the directions in the order [North, East, South, West]
        """
        directionHighFlows = []  # an array to store the highest flows of each direction in the order [North, East, South, West]

        # finds the highest VPH in a lane for each direction
        for direction in self.directions.values():  # iterates over all directions in the junction
            maxVPH = 0  # sets the current maxVPH to be 0
            for lanes in direction.lanes.values():  # iterates over all of the laneTypes in the junction
                for lane in lanes:  # iterates over all the lanes of the lane type
                    maxVPH = max(lane.totalFlow, maxVPH)  # sets the maxVPH to be the highest of the maxVPH or the current lanes vph

            directionHighFlows.append(maxVPH)  # adds the maxVPH to directionHighFlows


        if all(flow == 0 for flow in directionHighFlows):
            return [1, 1, 1, 1]

        # puts the VPH into a dictionary of the form {VPH, index in the original array}
        numberDict = {}
        for j in range(len(directionHighFlows)):
            numberDict[j] = int(directionHighFlows[j])  # creates a dictionary with the flow rate as the key and their position in the original array as the value
        numberDict = dict(sorted(numberDict.items(), key=lambda item: item[1])) # sorts the dictionary by the flow rates and stores in numberDict


        
        # iterates through the dictionary and stores the values in separate arrays
        indexOrder = []  # initialises the array to store the original indexes of the values
        flowOrder = []  # initialises the array to store the flow of the values
        for index, VPH in numberDict.items():  # iterates over the items in the dictionary
            indexOrder.append(index)  # adds the index to the array
            flowOrder.append(VPH)  # adds the flow to the array

        # adds the number of 0's to the array as directions
        ranks = []  # initialises ranks
        for i in range(len(indexOrder)):  # iterates for the amount of directions
            ranks.append(0)  # adds 0 to the array

        # produces the array of the ranks
        rank = 1  # initialises the rank as 1
        for i in range(len(flowOrder)):  # iterates over the number of directions
            if i > 0 and flowOrder[i] != flowOrder[i - 1]:  # checks whether two score are the same or not
                rank += 1  # increases the rank by 1
            ranks[indexOrder[i]] = rank  # assigns the rank into ranks at the index the flow was originally in

        return ranks  # returns the array of ranks in the order [North, East, South, West]
