class Vehicle:
    """
    Description: the object for the vehicles

    Attributes:
        entryTime(float): the time that the vehicle entered the simulation
        exitTime(float): the time that the vehicle left the simulation
        totalWait(float): the time that the vehicle had to wait

    Methods:
        __init__(self, entryTime, exitTime, totalWait): initialises the object
    """

    def __init__(self, entryTime, exitTime, totalWait):
        """
        Description: initialises the object

        Args:
            entryTime(float): the time that the vehicle entered the simulation
            exitTime(float): the time that the vehicle left the simulation
            totalWait(float): the time that the vehicle had to wait
        """
        self.entryTime = entryTime
        self.exitTime = exitTime
        self.totalWait = totalWait