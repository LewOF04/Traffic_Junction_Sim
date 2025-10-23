import math
from queue import Queue
def laneOrdering(lanes):
    """
    Description: Orders the array of lanes into the correct order

    Args:
        lanes(Array): an array representing the lanes of a junction direction.

    Returns:
        array: the lanes of a junction direction, with the lanes in the correct order from left to right.
    """
    #note that a junction must follow the rule: LRS xor S xor LR
    laneOrder = {'L': 0, 'CB': 1, 'LS': 2, 'LRS': 3, 'S': 4, 'LR': 5, 'RS': 6, 'R': 7, None: 8} #this is the required ordering of the junction lane types
    return sorted(lanes, key=lambda x: laneOrder[x]) #uses sorted to order the array based on the laneOrder


class Lane:
    """
    Description: object containing all of the information about a lane

    Attributes:
        directionFlow(array(int)): an array of the VPH of traffic for each direction [LeftVPH, StraightVPH, RightVPH]
        totalFlow(int): the total VPH of traffic for the direction
        lastCarTime(float): the time that the last vehicle entered the lane whilst running the direction
        avgWait(float): the average wait of a vehicle in this lane between entering and leaving the lane
        maxQueue(int): the longest queue of vehicles in this lane
        maxWait(float): the longest wait of a vehicle in this lane
        numCarsPassed(int): the number of vehicles that have passed through this lane
        cars(Queue(Vehicle)): the queue of vehicle objects
        newCarRate(float): how long is takes for a car to enter the lane
        lightTime(float): the time that the light of this lane will be on for
        totalWait(float): the total wait time of all vehicles in this lane

    Methods:
        getQueueSize(self): gives the size of the queue in the lane
        updateDirectionFlow(self, flow, flowType, updateType): Sets the flow of the lane and the newCarRate based on the new flow
    """

    def __init__(self):
        """
        Description: Initialises the lane object
        """
        self.directionFlow = [0, 0, 0]  # the VPH of the vehicles going through this lane [Left, Straight, Right]
        self.totalFlow = 0  # the total flow of the lane
        self.lastCarTime = 0.0  # the time when this lane last had a green light
        self.avgWait = None  # the average wait time of vehicles in this lane
        self.maxQueue = -math.inf  # the maximum length of the queue in this lane
        self.maxWait = -math.inf  # the maximum wait time for a vehicle in this lane
        self.numCarsPassed = 0  # the number of cars that have passed through this lane
        self.cars = Queue()  # the queue that will store all of the vehicles
        self.newCarRate = 0  # the # of seconds between cars entering this lane
        self.lightTime = 0  # the time that the green light will be on
        self.totalWait = 0.0

    def getQueueSize(self):
        """
        Description: Returns the size of the queue of cars in the lane

        Args:
            self(Lane): the lane in question

        Returns:
            int: the number of vehicles in the lane's queue
        """
        return self.cars.qsize()  # return the size of the queue in the lane

    def updateDirectionFlow(self, flow, flowType, updateType):
        """
        Description: Sets the flow of the lane and the newCarRate based on the new flow

        Args:
            flow(int): the VPH that is being updated
            flowType(int): which direction the flow is heading (0 = Left, 1 = Straight, 2 = Right)
            updateType(string): how the update should occur ('add' = add the flow to the current flow, 'sub' = subtract the flow from the current flow, 'rep' = replace the current flow with the new flow)
        """

        # if (self.directionFlow[flowType] == None):  # checks whether there hasn't been an entry to the direction flow already
        #     self.directionFlow[flowType] = 0  # if there hasn't then initialise it to 0

        if updateType == 'add':  # if the user is adding to the current flow
            self.directionFlow[flowType] += flow  # add the new flow to the lanes current direction flow

        if updateType == 'sub':  # if the user is taking away from the flow
            if (self.directionFlow[flowType] == 0):  # check that the user is not taking away from a 0 number
                raise Exception(
                    "Cannot subtract from 0 flow.")  # throws an error if it is attempting to take away from 0
            else:
                self.directionFlow[flowType] -= flow  # take away the new flow to the lanes current direction flow

        if updateType == 'rep':  # if the user is replacing the current flow
            self.directionFlow[flowType] = flow  # define the new flow

        self.totalFlow = sum(self.directionFlow)  # updates the total flow variable
        if (self.totalFlow == 0):
            newCarRate = 0
        else:
            self.newCarRate = 3600 / self.totalFlow  # sets the time between new cars, based on the new flow
