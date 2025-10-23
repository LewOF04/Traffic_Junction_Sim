import math
from src.vehicle import Vehicle
from src.junction import Junction

def endSimulation(junction):
    """
    Description: Gathers all information and packages it into a dictionary to be passed off for processing

    Args:
        junction(Junction): the junction that the information is being gathered from

    Returns:
        Dictionary: simulationDict - the dictionary containing all information about the simulation run
    """

    simulationDict = {} #creates a dictionary to store each direction and the overall simulation information
    #add information about the junction itself and the simulation parameters
    simulationDict['isPedestrianCrossing'] = junction.isPedestrianCrossing #whether the junction has a pedestrain crossing or not
    
    if junction.isPedestrianCrossing:
        simulationDict['pedestrianCrossingTime'] = junction.pedestrianCrossingTime #the crossing time for pedestrians
        simulationDict['pedCrossPH'] = junction.pedCrossPH #the pedestrian crossings per hour

    simulationDict['trafficSpeed'] = junction.trafficSpeed #the traffic speed of the vehicles
    simulationDict['minimumGreenTime'] = junction.minimumGreenTime #the minimum time a green light must be on
    simulationDict['vehicleLength'] = junction.vehicleLength #the average length of a vehicle
    simulationDict['priorityNums'] = junction.priorityNums #the priority of each direction

    #initialises counters for cars, wait time and queue numbers
    simulationCarsPassedThrough = 0
    simulationTotalWait = 0
    simulationDict['maxQueue'] = 0
    simulationDict['maxWait'] = 0


    #creates each dictionary that stores the information for each direction
    for directionName, direction in junction.directions.items():
        directionDict = {} #creates a dicitionary for this direction

        #initialises values for cars, wait and queue numbers
        directionCarsPassedThrough = 0
        directionTotalWait = 0
        directionDict['maxWait'] = 0
        directionDict['maxQueue'] = 0
        
        #stores relevant values into the direction dictionary
        directionDict['lightTime'] = direction.lightTime
        directionDict['VPHFlowDirections'] = direction.VPHFlowDirections
        directionDict['laneLayout'] = direction.laneLayout


        #creates dictionary for each lane within the dictionary
        laneIteration = 0
        for laneType, lanes in direction.lanes.items():
            for lane in lanes:
                if lane.numCarsPassed > 0:
                    lane.avgWait = lane.totalWait / lane.numCarsPassed #calculates the average wait for this lane
                else:
                    lane.avgWait = 0

                #stores all the information about this lane in the laneDict 
                laneDict = {}
                laneDict['laneType'] = laneType
                laneDict['maxQueue'] = lane.maxQueue
                laneDict['maxWait'] = lane.maxWait
                laneDict['avgWait'] = lane.avgWait
                laneDict['remainingVehicles'] = lane.cars.qsize()
                laneDict['directionFlow'] = lane.directionFlow
                laneDict['totalFlow'] = lane.totalFlow
                laneDict['carsPassedThrough'] = lane.numCarsPassed
                laneDict['totalWait'] = lane.totalWait

                #adds to the total counters for the direction
                directionCarsPassedThrough += lane.numCarsPassed
                directionTotalWait += lane.totalWait

                #updates the maxWait and maxQueue for the direction
                directionDict['maxWait'] = max(laneDict['maxWait'], directionDict['maxWait'])
                directionDict['maxQueue'] = max(laneDict['maxQueue'], directionDict['maxQueue'])

                directionDict[laneIteration] = laneDict #stores the lane dictionary in the directionDict
                laneIteration += 1 #increments the lane iteration
        

        directionDict['carsPassedThrough'] = directionCarsPassedThrough #the number of vehicles passed through this direction
        directionDict['totalWait'] = directionTotalWait #the total wait time of all direction vehicles
        if directionCarsPassedThrough > 0:
            directionDict['avgWait'] = directionTotalWait / directionCarsPassedThrough  #the average wait over the entire direction
        else:
            directionDict['avgWait'] = 0


        #adds to the total counter for the simulation
        simulationTotalWait += directionTotalWait
        simulationCarsPassedThrough += directionCarsPassedThrough

        simulationDict[directionName] = directionDict #adds a dictionary to store the information about that direction
        simulationDict['maxQueue'] = max(simulationDict['maxQueue'], directionDict['maxQueue']) #calculates the maxQueue for the entire simulation
        simulationDict['maxWait'] = max(simulationDict['maxWait'], directionDict['maxWait']) #calculates the maxWait for the entire simulation

    if simulationCarsPassedThrough > 0:
        simulationDict['avgWait'] = simulationTotalWait / simulationCarsPassedThrough #calculates the average wait across the whole simulation
    else:
        simulationDict['avgWait'] = 0

    simulationDict['carsPassedThrough'] = simulationCarsPassedThrough #the total number of vehicles processed by the junction
    simulationDict['totalWait'] = simulationTotalWait #the total wait time of all vehicles
    
    return simulationDict #returns the final dictionary of the simulationDictionary    


def runSimulation(junction):
    """
    Description: Runs the simulation for the given junction

    Args:
        junction(Junction): the junction that the simulation processed for
    
    Methods:
        processGreenLane(lane, currentTime, junction): Processes vehicle during greenlight time for a lane
        processGreen(direction, direction, currentTime, junction): Processes the green light for all lanes of a direction
        shouldActivatePedestrianCrossing(junction, currentTime, crossingRequests): checks whether the pedestrian crossing should ne activated given the current time
        processWaitingVehiclesLane(lane, currentTime): processes the vehicles that've arrived up to the currentTime
        processWaitingVehicles(direction, currentTime, CB): processes the vehicles that've arrived for a whole direction
        processOppositeLane(lane, lightTime, currentTime, junction): processes opposing left lane

    Returns:
        Dictionary: the simulationDict of all information about the simulation after it has run
    """
    def processOppositeLane(lane, lightTime, currentTime, junction):
        """
        Description: When a left-lane from the opposite direction as the light, is able to run unimpeded, this method processes the traffic

        Args:
            lane(Lane): The lane which is being processed
            lightTime(float): The time that the light should be on for
            currentTime(float): The current time of the simulation
            junction(Junction): The junction that the simulation is running in

        Methods:
            processWaitingVehiclesLane(lane, time): Processes vehicles waiting in the lane up until the specified time
        """
        time = currentTime  # starts the time as the currentTime
        end_time = currentTime + lightTime

        while time < end_time:
            if lane.getQueueSize() != 0:  # checks whether there is a vehicle on the queue
                time += junction.vehicleLength / junction.trafficSpeed  # adds to the time the time it takes for a vehicle to travel one vehicle length
                vehicle = lane.cars.get()  # removes a vehicle from the front of the queue

                lane.totalWait += time - vehicle.entryTime  # adds to the total wait time of the lane
                lane.numCarsPassed += 1  # adds to the number of vehicles that have passed through the lane
                lane.maxWait = max(lane.maxWait, (
                            time - vehicle.entryTime))  # determines if this vehicle has had the longest wait so far

                processWaitingVehiclesLane(lane,
                                           time)  # adds any vehicles that have entered the lane whilst this vehicle was leaving

            else:  # otherwise if there are no vehicles in the lane
                # Attempt to find next vehicle entry time or break the loop
                if lane.newCarRate is None or lane.newCarRate <= 0:
                    break  # Exit if no new cars are expected

                next_car_time = lane.lastCarTime + lane.newCarRate

                if next_car_time >= end_time:
                    break  # Exit if next car would arrive after light time

                time = next_car_time  # Update time to next car's arrival
                lane.numCarsPassed += 1  # add that the vehicle has passed the junction
                lane.lastCarTime = time  # updates the last time a vehicle entered

        return time  # Optional: return final time for potential further use


    def processGreenLane(lane, laneNum, direction, oppositeDirection, currentTime, junction):
        """
        Description: Processes the vehicles during the green light time of the given lane

        Args:
            lane(Lane): the lane that the vehicles are being processed in
            currentTime(float): the time of the simulation currently
            junction(Junction): the junction that the simulation is in
            direction(Direction): the direction that the lane belongs to
            oppositeDirection(Direction): the direction opposite in the junction to direction
            laneNum(int): the number of this lane in the direction (from left to right, i.e. the leftmost lane is 0, next 1 and so on)
        
        Returns:
            float: (currentTime + lane.lightTime) the time of the simulation after the green light
        
        Methods:
            processWaitingVehiclesLane(lane, time): processes all the waiting vehicles for a lane
        
        Notes:
            Left turn lanes in the opposite direction are allowed to operate except when there are multiple right turn lanes in the current direction (impossible due to lane crossover) or when there is significant right turn traffic so they have no right of way

        """

        normalRun = True #boolean to check whether this lane needs to operate as normal or consider an opposing left lane

        #check if there is a left turn lane opposite and that this is the right-most lane of the current direction
        if((list(oppositeDirection.lanes.keys())[0] == 'L') and (laneNum == (len(direction.laneLayout) - 1))):
            #check if this lane contains right turning traffic
            if(('R' in direction.laneLayout[-1] and lane.newCarRate != 0)):
                #if it does contain right turn traffic

                allowLeft = True #checks whether a left lane is allowed to flow
                if(len(direction.laneLayout) > 1): #checks if there are more than 1 lane
                    
                    #check whether there are multiple lanes turning right (if so it is unsafe to run a left turn lane, so no left turn lanes are allowed to run)
                    if ('R' in direction.laneLayout[-2]): #if there is right turning in the second last lane
                        allowLeft = False #left lanes cannot go

                if allowLeft: #checks whether left lane traffic in the opposite direction is allowed to flow
                    normalRun = False #the logic now must be different to accomodate for the opposite left turn lane

                    time = currentTime #starts the time as the currentTime
                    while(time < (currentTime + lane.lightTime)): #iterates as long as the time is less than the finishing time of the green light
                        if(lane.getQueueSize() != 0): #checks whether there is a vehicle on the queue
                            time += junction.vehicleLength / junction.trafficSpeed #adds to the time the time it takes for a vehicle to travel one vehicle length
                            vehicle = lane.cars.get() #removes a vehicle from the front of the queue

                            lane.totalWait += time - vehicle.entryTime #adds to the total wait time of the lane
                            lane.numCarsPassed += 1 #adds to the number of vehicles that have passed through the lane
                            lane.maxWait = max(lane.maxWait, (time - vehicle.entryTime)) #determines if this vehicle has had the longest wait so far

                            processWaitingVehiclesLane(lane, time) #adds any vehicles that have entered the lane whilst this vehicle was leaving

                        else: #otherwise if there are no vehicles in the lane
                            #once there are no vehicles in the lane, the opposing left lanes have the opportunity to go
                            time = lane.lastCarTime + lane.newCarRate #updates the time to be when the next vehicle joins
                            
                            #iterates over all opposing left turn lanes
                            for laneL in oppositeDirection.lanes['L']:
                                if laneL.newCarRate == 0:
                                    continue

                                LTime = lane.lastCarTime + 5 #starts the LTime as the time that the last right-turn lane has gone (+5 for the buffer between the right car to cross before an opposing vehicle can go)
                                #loops until the LTime is greater than either the time that the next right-turning vehicle comes OR the time of the total light
                                #(-5 is used to provide a safety buffer between vehicles)
                                while (LTime < min((time - 5), (currentTime + lane.lightTime))):
                                    #process vehicles for the left-turn lane lanes

                                    if(laneL.getQueueSize() != 0): #checks whether there is a vehicle on the queue
                                        LTime += junction.vehicleLength / junction.trafficSpeed #adds to the time the time it takes for a vehicle to travel one vehicle length
                                        
                                        if(LTime > min((time - 5), (currentTime + lane.lightTime))):
                                            #if the LTime is now higher than the 
                                            break #exits the while loop
                                            
                                        vehicle = laneL.cars.get() #removes a vehicle from the front of the queue

                                        laneL.totalWait += LTime - vehicle.entryTime #adds to the total wait time of the lane
                                        laneL.numCarsPassed += 1 #adds to the number of vehicles that have passed through the lane
                                        laneL.maxWait = max(laneL.maxWait, (LTime - vehicle.entryTime)) #determines if this vehicle has had the longest wait so far

                                        processWaitingVehiclesLane(laneL, LTime) #adds any vehicles that have entered the lane whilst this vehicle was leaving

                                    else: #once there are no vehicles left in the L lane
                                        LTime = laneL.lastCarTime + laneL.newCarRate #updates the time to be when the next vehicle joins
                                        if(LTime < min((time - 5), (currentTime + lane.lightTime))): #if this vehicle would've joined before the end of the light OR before the next right vehicle 
                                            laneL.numCarsPassed += 1 #add that the vehicle has passed the junction
                                            laneL.lastCarTime = LTime #updates the last time a vehicle entered
                                        
                            if(time < (currentTime + lane.lightTime)): #if this vehicle would've joined before the end of the light
                                lane.numCarsPassed += 1 #add that the vehicle has passed the junction
                                lane.lastCarTime = time #updates the last time a vehicle entered
                
            else: #this direction has no right turn traffic so the opposite left turn lanes can operate independently
                if(len(direction.laneLayout) > 1): #checks if there are more than 1 lane
                    
                    #check whether there are multiple lanes turning right (if so it is unsafe to run a left turn lane, so no left turn lanes are allowed to run)
                    if ('R' not in direction.laneLayout[-2]): #if there is left turning in the second last lane
                        for laneL in oppositeDirection.lanes['L']: #iterates over all left turn lanes
                            if laneL.newCarRate == 0:
                                continue
                
                            processOppositeLane(laneL, lane.lightTime, currentTime, junction) #runs the green light for the left lane
                
                else:
                    for laneL in oppositeDirection.lanes['L']: #iterates over all left turn lanes
                        if laneL.newCarRate == 0:
                            continue
                        processOppositeLane(laneL, lane.lightTime, currentTime, junction) #runs the green light for the left lane
        
        #if there is no left lane specific logic then the lane can run as normal
        if normalRun:
            time = currentTime #starts the time as the currentTime
            while(time < (currentTime + lane.lightTime)): #iterates as long as the time is less than the finishing time of the green light
                if(lane.getQueueSize() != 0): #checks whether there is a vehicle on the queue
                    time += junction.vehicleLength / junction.trafficSpeed #adds to the time the time it takes for a vehicle to travel one vehicle length
                    vehicle = lane.cars.get() #removes a vehicle from the front of the queue

                    lane.totalWait += time - vehicle.entryTime #adds to the total wait time of the lane
                    lane.numCarsPassed += 1 #adds to the number of vehicles that have passed through the lane
                    lane.maxWait = max(lane.maxWait, (time - vehicle.entryTime)) #determines if this vehicle has had the longest wait so far

                    processWaitingVehiclesLane(lane, time) #adds any vehicles that have entered the lane whilst this vehicle was leaving

                else: #otherwise if there are no vehicles in the lane

                    if lane.newCarRate == 0:
                        break

                    time = lane.lastCarTime + lane.newCarRate #updates the time to be when the next vehicle joins
                    if(time < (currentTime + lane.lightTime)): #if this vehicle would've joined before the end of the light
                        lane.numCarsPassed += 1 #add that the vehicle has passed the junction
                        lane.lastCarTime = time #updates the last time a vehicle entered
        
        return (currentTime + lane.lightTime) #returns what the new time is


    def processGreen(direction, oppositeDirection, currentTime, junction):
        """
        Description: processes the light being green for all lanes in the junction apart from CB

        Args:
            direction(Direction): the direction which is being processed
            currentTime(Float): the currentTime of the simulation
            junction(Junction): the junction that the simulation is being run in
        
        Returns:
            float: newTime - the time after the direction has been processed
        
        Methods:
            processGreenlane(lane, direction, currentTime, junction): processes the green light for a specific lane
        """
        iteration = 0 #counts which lane in the direction this is
        for laneType, lanes in direction.lanes.items(): #iterates over all lane types in the direction
            if(laneType != 'CB'): #as long as this lane isn't the CB lane
                for lane in lanes: #iterates over all lanes in the direction
                    newTime = processGreenLane(lane, iteration, direction, oppositeDirection, currentTime, junction) #processes the lane being green
                    iteration += 1 #increments to the next lane

        return newTime #returns the time after the direction has been processed


    def shouldActivatePedestrianCrossing(junction, currentTime, crossingRequests):
        """
        Description: Calculates whether there should be a pedestrain crossing given the current time and last pedestrian crossing

        Args:
            junction(Junction): junction of the pedestrain crossing
            currentTime(float): time of the simulation at the point of the check
            crossingRequests(Array): array of times that crossing requests will be made
        
        Returns:
            True/False whether a pedestrian crossing has occurred
        """
        if (junction.lastCrossingTime == 0.0): #if there has yet to be a crossing time
            if (currentTime > crossingRequests[0]): #check whether the current time is greater than the first crossing time
                return True
            else:
                return False

        for i in range(len(crossingRequests)):
            #if this crossing request ocurred after the last crossing and before the current time, then a crossing needs to occur
            if (crossingRequests[i] > junction.lastCrossingTime) and (crossingRequests[i] <= currentTime):
                return True
        return False
            

    def processWaitingVehiclesLane(lane, currentTime):
        """
        Description: Processes the vehicles that have entered the lane up until the currentTime

        Args:
            lane(Lane): the lane that the vehicles are being processed in
            currentTime(float): the time of the simulation currently
        """
        #check if the lane has any traffic
        if(lane.totalFlow == 0):
            return #skip if no traffic

        #if no vehicles have yet to enter the lane
        if (lane.lastCarTime == 0.0):
            time = lane.newCarRate #starts the time at the time when the first vehicle would enter
        else: #if this isn't the first green
            time = lane.lastCarTime + lane.newCarRate #starts the time at the next vehicle entry point
                    
        #iterate whilst the time is less than the current time
        while(time < currentTime):
            vehicle = Vehicle(time, None, None) #creates the vehicle with the entry time as the time
            lane.cars.put(vehicle) #adds the vehicle to the queue
            lane.lastCarTime = time #updates the time that the last vehicle entered
            lane.maxQueue = max(lane.maxQueue, lane.cars.qsize()) #updates the maximum queue if the current queue is now longer

            time += lane.newCarRate #increments the time to when the next vehicle joins


    def processWaitingVehicles(direction, currentTime, CB):
        """
        Description: Processes all lanes for the vehicles before the currentTime
        
        Args:
            direction(Direction): the direction object that the vehicles are being processed for
            currentTime(float): the time of the simulation
            CB(int): whether or not the cycle or bus lane should be processed (1 - Yes, 0 - No)
        
        Methods:
            processWaitingVehiclesLane(lane, currentTime): processes the waiting vehicles for a specific lane

        """
        if (currentTime != 0.0): #As long as the current time isn't 0
            for lane_type, lanes in direction.lanes.items(): #iterates over all lane types
                for lane in lanes: #iterates over all lanes
                    if((lane_type != 'CB') or (CB == 1)): #as long as the lane isn't a CB lane or if we should be processing the CB lane
                        processWaitingVehiclesLane(lane, currentTime) #sends to function to process the lane 
       
    currentTime = 0.0
    simDuration = 3600 #1 hour = 3600 seconds

    #gets the times that a pedestrian crossing will be made
    if junction.isPedestrianCrossing:
        timeBetweenCrossings = 3600 / junction.pedCrossPH #Calculate average time between crossings
        time = 0.0
        crossingRequests = []
        while (time < 3600):
            crossingRequests.append(time + timeBetweenCrossings) #adds the time of this request to the list
            time += timeBetweenCrossings #increments the time by the next crossing gap

    # Main simulation loop
    while currentTime < simDuration: #runs the simulation as long as the time is less than the length of the simulation

        # Handle pedestrian crossing if enabled
        if junction.isPedestrianCrossing:
            if shouldActivatePedestrianCrossing(junction, currentTime, crossingRequests): #function checks whether there has been a pedestrain request between now and the last cycle
                currentTime += junction.pedestrianCrossingTime #adds the time of the pedestrain crossing to the time
                junction.lastCrossingTime = currentTime #sets the last time the pedestrian crossing was on to the current time

        # Process each direction in the junction
        for directionName, direction in junction.directions.items():

            #find what the opposite direction is
            match direction.directionName:
                case 'north':
                    oppositeDirection = junction.directions['south']
                case 'south':
                    oppositeDirection = junction.directions['north']
                case 'west':
                    oppositeDirection = junction.directions['east']
                case 'east':
                    oppositeDirection = junction.directions['west']

            #check if there have been any vehicles entering the junction since the last time
            processWaitingVehicles(direction, currentTime, 1)

            #checks whether this direction has any traffic in it 
            if (direction.hasTraffic() == False):
                currentTime += 1 #add 1 second to the time if there is no traffic
            else:
                if(('CB' in direction.lanes) and (direction.lanes['CB'][0].getQueueSize() != 0)): 
                    #if there is a cycle or bus lane, then run this lane first
                    currentTime = processGreenLane(direction.lanes['CB'][0], -1, direction, oppositeDirection, currentTime, junction) #processes the green light
                    processWaitingVehicles(direction, currentTime, 0) #processes the waiting vehicles for all but the CB lane
                    
                if direction.hasTraffic(): #checks if there is any traffic in the direction
                    currentTime = processGreen(direction, oppositeDirection, currentTime, junction) #process the green light for that direction
    
    return endSimulation(junction) #sends the junction of to have all of the statistics gathered
                    

def createSimulation(inputInformation):
    """
    Creates the simulation with all user inputs

    Args: 
        inputInformation(Dictionary) - a dictionary containing the user inputted data

    Returns:
        Dictionary: simulationDict - the dictionary containing all information about the simulation run

    """
    junction = Junction(inputInformation) #creates the junction
    junction.distributeVehicles() #distribute the vehicles within the junction

    if inputInformation[9]: #checks whether the user has specified the priority of the directions or not
        priorityNums = inputInformation[10] #sets the priority numbers to be the priority specified by the user
    else: #otherwise, if the user has left it to the system to decide
        priorityNums = junction.calculateDirectionPriority() #calculates the priority direction numbers and/or the time for the green light in each direction

    junction.priorityNums = priorityNums #add the priorityNums to the junction
    

    #set the green time of each direction, based off of the priority
    iteration = 0
    for name, direction in junction.directions.items():
        
        #check what the number is for this direction in the priorityNums
        match priorityNums[iteration]:
            case 1:
                direction.lightTime = junction.minimumGreenTime
            case 2:
                direction.lightTime = junction.minimumGreenTime * 1.25
            case 3:
                direction.lightTime = junction.minimumGreenTime * 1.5
            case 4:
                direction.lightTime = junction.minimumGreenTime * 1.75

        for laneType, lanes in direction.lanes.items():
            for lane in lanes:
                lane.lightTime = direction.lightTime #set the light time within each lane to be the same as its parent direction

        iteration += 1
        
    return runSimulation(junction) #runs the simulation once it has been successfully created
