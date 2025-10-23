import math
from src.lane import Lane
class Direction:
    """
    Description: The class object containing all direction information

    Attributes:
        directionName(string): the name of the direction
        lightTime(float): the time that the light for this direction should be on for
        lanes(Dictionary): the dictionary containing all of the lanes
        VPHFlowDirections(array(int)): the VPH for each heading for this direction (Left, Straight, Right)
        laneLayout(array(string)): the array of strings inidcating the types of lanes in the direction

    Methods:
        __init__(self, flows, name, laneInput, inputInformation): initialises the direction object
        hasTraffic(self): indicates whether or not there is any traffic within this direction
        distributeVehiclesByLane(self): distributes the VPH for this direction between the lanes optimally
    """

    def __init__(self, flows, name, laneInput):
        """
        Description: initialises the direction object

        Args:
            flows(Array(int)): an array of the VPH for each exit direction for this junction entrance
            name(string): the name of the direction (north, east, south, west)
            laneInput(Array(String)): an array of what types of lanes are within this junction entrance

        """
        self.directionName = name  # the name of the direction
        self.lightTime = None  # the time that the light will be on in this direction
        self.lanes = {}  # a dictionary to store all of the lane objects
        self.VPHFlowDirections = flows  # the array storing the directions of traffic [Left, Straight, Right]
        self.laneLayout = laneInput  # the layout of the lanes in the junction

        # creates lane objects for each direction type provided that these lanes exist
        leftNum = laneInput.count('L')  # counts the number of left turning lanes for this direction
        if (leftNum != 0):  # if there exists a left turn lane
            self.lanes['L'] = [Lane() for _ in range(leftNum)] # adds the left lane to the lanes dict

        cycleOrBusNum = laneInput.count('CB')  # cycleOrBus
        if (cycleOrBusNum != 0):
            self.lanes['CB'] = [Lane() for _ in range(cycleOrBusNum)] # adds the cycle or bus lane to the lanes dict

        leftStraightNum = laneInput.count('LS')  # left or straight lane
        if (leftStraightNum != 0):
            self.lanes['LS'] = [Lane() for _ in range(leftStraightNum)] # adds the left or straight lane to the lanes dict

        leftRightStraightNum = laneInput.count('LRS')  # left, right or straight lane
        if (leftRightStraightNum != 0):
            self.lanes['LRS'] = [Lane() for _ in range(leftRightStraightNum)] # adds the left or right or straight lane to the lanes dict

        straightNum = laneInput.count('S')  # straight lane
        if (straightNum != 0):
            self.lanes['S'] = [Lane() for _ in range(straightNum)] # adds the straight lane to the lanes dict

        leftRightNum = laneInput.count('LR')  # left or right lane
        if (leftRightNum != 0):
            self.lanes['LR'] = [Lane() for _ in range(leftRightNum)] # adds the left or right lane to the lanes dict

        rightStraightNum = laneInput.count('RS')  # right or straight lane
        if (rightStraightNum != 0):
            self.lanes['RS'] = [Lane() for _ in range(rightStraightNum)] # adds the right or straight lane to the lanes dict

        rightNum = laneInput.count('R')  # right lane
        if (rightNum != 0):
            self.lanes['R'] = [Lane() for _ in range(rightNum)] # adds the right lane to the lanes dict

    def hasTraffic(self):
        """
        Checks through each lane to see if there is any traffic within the queues

        Returns:
            bool: True if there is traffic in any lane, False if there is no traffic
        """
        for lanes in self.lanes.values():  # iterates through the values (lane objects) in the lanes dictionary
            for lane in lanes:
                if (lane.getQueueSize() != 0):  # checks whether there is traffic in the lane object
                    return True  # if there is traffic then return true
        return False  # otherwise if there is no traffic in any of the lanes

    def distributeVehiclesByLane(self):
        """
        Distribute the vehicle traffic through all of the lanes within this direction to balance vehicle flows optimally

        Args:
            self - the direction which is being distributed

        Methods:
            distributeLRorLRS(laneType): handles traffic distribution if there is an LR or LRS lane in the direction
            distributeS(): handles traffic distribution if there is an S lane in the direction
            distributeElse(): handles traffic distribution if there is no LRS, LR or S lane in the junction
            maxRSGTminRight(maxRS, minRight, changeMade, RCounter): moves right traffic from RS to R
            maxLSGTminLeft(maxLS, minLeft, changeMade, LCounter): moves left traffic from LS to L
            maxLSGTminStraight(maxLS, minStraight, changeMade, SCounter): moves straight traffic from LS to S
            maxRSGTminStraight(maxRS, minStraight, changeMade, SCounter): moves straight traffic from RS to S
            maxLSGTmaxRS(maxLS, maxRS, changeMade): moves straight traffic from LS to RS
            maxRSGTmaxLS(maxRS, maxLS, changeMade): moves straight traffic from RS to LS
            minRightGTmaxRS(minRight, maxRS, changeMade, RCounter): moves right traffic from R to RS
            minLeftGTmaxLS(minLeft, maxLS, changeMade, LCounter): moves left traffic from L to LS
            minStraightGTmaxRS(minStraight, maxRS, changeMade, SCounter): moves straight traffic from S to RS
            minStraightGTmaxLS(minStraight, maxLS, changeMade, SCounter): moves straight traffic from S to LS
        """

        # self.VPHFlowDirections - the traffic directions in the form [left, straight, right, cycleOrBus]
        # self.lanes - a dictionary of lane objects, with the keys 'L', 'CB', 'LS', 'LRS', 'S', 'LR', 'RS', 'R'

        def maxRSGTminRight(maxRS, minRight, changeMade, RCounter):
            """
            Description: if maxRS is greater than minRight and there is right traffic in RS, add right traffic from RS to R

            Args:
                maxRS(int): the flow in the RS lane
                minRight(int): the lowest flow out of the R lanes
                changeMade(bool): whether or not a change has been made 
                RCounter(int): the counter to iterate through R lanes
            
            Returns:
                int: maxRS - the updated maxRS variable
                int: minRight - the updated minRight variable
                bool: changeMade - whether a change has been made
                int: RCounter - the updated counter of R lanes
            """
            nonlocal self
            #if maxRS is greater than minRight and there is right traffic in RS
            if((maxRS > minRight) and (self.lanes['RS'][0].directionFlow[2] != 0)):
                #add right traffic from RS to R
                changeMade = True
                self.lanes['RS'][0].updateDirectionFlow(1, 2, 'sub')
                self.lanes['R'][RCounter].updateDirectionFlow(1, 2, 'add')
                    
                maxRS = self.lanes['RS'][0].totalFlow
                minRight = min(lane.totalFlow for lane in self.lanes['R'])

                RCounter = (RCounter + 1) % len(self.lanes['R'])
            
            return maxRS, minRight, changeMade, RCounter
        
        def maxLSGTminLeft(maxLS, minLeft, changeMade, LCounter):
            """
            Description: if maxLS is greater than minLeft and there is left traffic in LS, add left traffic from LS to L

            Args:
                maxLS(int): the flow in the LS lane
                minLeft(int): the lowest flow out of the L lanes
                changeMade(bool): whether or not a change has been made 
                LCounter(int): the counter to iterate through L lanes
            
            Returns:
                int: maxLS - the updated maxLS variable
                int: minLeft - the updated minLeft variable
                bool: changeMade - whether a change has been made
                int: LCounter - the updated counter of L lanes
            """
            nonlocal self
            #if maxLS is greater than minLeft and there is left traffic in LS
            if((maxLS > minLeft) and (self.lanes['LS'][0].directionFlow[0] != 0)):
                #add left traffic from LS to L
                changeMade = True
                self.lanes['LS'][0].updateDirectionFlow(1, 0, 'sub')
                self.lanes['L'][LCounter].updateDirectionFlow(1, 0, 'add')

                maxLS = self.lanes['LS'][0].totalFlow
                minLeft = min(lane.totalFlow for lane in self.lanes['L'])

                LCounter = (LCounter + 1) % len(self.lanes['L'])

            return maxLS, minLeft, changeMade, LCounter
        
        def maxLSGTminStraight(maxLS, minStraight, changeMade, SCounter):
            """
            Description: if maxLS is greater than the minimum straight and there is straight traffic in LS, add straight traffic from LS to S

            Args:
                maxLS(int): the flow in the LS lane
                minStraight(int): the lowest flow out of the S lanes
                changeMade(bool): whether or not a change has been made 
                SCounter(int): the counter to iterate through S lanes
            
            Returns:
                int: maxLS - the updated maxLS variable
                int: minStraight - the updated minStraight variable
                bool: changeMade - whether a change has been made
                int: SCounter - the updated counter of S lanes
            """
            nonlocal self
            #if maxLS is greater than the minimum straight and there is straight traffic in LS
            if((maxLS > minStraight) and (self.lanes['LS'][0].directionFlow[1] != 0)):
                #add straight traffic from LS to S
                changeMade = True
                self.lanes['LS'][0].updateDirectionFlow(1, 1, 'sub')
                self.lanes['S'][SCounter].updateDirectionFlow(1, 1, 'add')

                maxLS = self.lanes['LS'][0].totalFlow
                minStraight = min(lane.totalFlow for lane in self.lanes['S'])

                SCounter = (SCounter + 1) % len(self.lanes['S'])
            
            return maxLS, minStraight, changeMade, SCounter
        
        def maxRSGTminStraight(maxRS, minStraight, changeMade, SCounter):
            """
            Description: if maxRS is greater than the minimum straight and there is straight traffic in RS, add straight traffic from RS to S
            Args:
                maxRS(int): the flow in the RS lane
                minStraight(int): the lowest flow out of the S lanes
                changeMade(bool): whether or not a change has been made 
                SCounter(int): the counter to iterate through S lanes
            
            Returns:
                int: maxRS - the updated maxRS variable
                int: minStraight - the updated minStraight variable
                bool: changeMade - whether a change has been made
                int: SCounter - the updated counter of S lanes
            """
            nonlocal self
            #if maxRS is greater than the minimum straight and there is straight traffic in RS
            if((maxRS > minStraight) and (self.lanes['RS'][0].directionFlow[1] != 0)):
                #add straight traffic from RS to S
                changeMade = True
                self.lanes['RS'][0].updateDirectionFlow(1, 1, 'sub')
                self.lanes['S'][SCounter].updateDirectionFlow(1, 1, 'add')

                maxRS = self.lanes['RS'][0].totalFlow
                minStraight = min(lane.totalFlow for lane in self.lanes['S'])

                SCounter = (SCounter + 1) % len(self.lanes['S'])
            
            return maxRS, minStraight, changeMade, SCounter

        def maxLSGTmaxRS(maxLS, maxRS, changeMade):
            """
            Description: if maxLS is greater than maxRS and LS has some straight traffic, move S traffic from LS to RS
            Args:
                maxRS(int): the flow in the RS lane
                maxLS(int): the flow in the LS lane
                changeMade(bool): whether or not a change has been made 
            
            Returns:
                int: maxRS - the updated maxRS variable
                int: maxLS - the updated maxLS variable
                bool: changeMade - whether a change has been made
            """
            nonlocal self
            #if maxLS is greater than maxRS and LS has some straight traffic
            if((maxLS > maxRS) and (self.lanes['LS'][0].directionFlow[1] != 0) and (maxLS != (maxRS + 1))):
                #move S traffic from LS to RS
                changeMade = True
                self.lanes['LS'][0].updateDirectionFlow(1, 1, 'sub')
                self.lanes['RS'][0].updateDirectionFlow(1, 1, 'add')

                maxLS = self.lanes['LS'][0].totalFlow
                maxRS = self.lanes['RS'][0].totalFlow
            
            return maxLS, maxRS, changeMade

        def maxRSGTmaxLS(maxRS, maxLS, changeMade):
            """
            Description: if maxRS is greater than maxLS and RS has some straight traffic, move S traffic from RS to LS
            Args:
                maxRS(int): the flow in the RS lane
                maxLS(int): the flow in the LS lane
                changeMade(bool): whether or not a change has been made 
            
            Returns:
                int: maxRS - the updated maxRS variable
                int: maxLS - the updated maxLS variable
                bool: changeMade - whether a change has been made
            """
            nonlocal self
            #if maxRS is greater than maxLS and RS has some straight traffic
            if((maxRS > maxLS) and (self.lanes['RS'][0].directionFlow[1] != 0) and (maxRS != (maxLS + 1))):
                #move S traffic from RS to LS
                changeMade = True
                self.lanes['RS'][0].updateDirectionFlow(1, 1, 'sub')
                self.lanes['LS'][0].updateDirectionFlow(1, 1, 'add')

                maxRS = self.lanes['RS'][0].totalFlow
                maxLS = self.lanes['LS'][0].totalFlow
            
            return maxRS, maxLS, changeMade

        def minRightGTmaxRS(minRight, maxRS, changeMade, RCounter):
            """
            Description: if minRight is greater than maxRS, move right traffic from R to RS
            Args:
                maxRS(int): the flow in the RS lane
                minRight(int): the lowest flow out of the R lanes
                changeMade(bool): whether or not a change has been made 
                RCounter(int): the counter to iterate through R lanes
            
            Returns:
                int: maxRS - the updated maxRS variable
                int: minRight - the updated minRight variable
                bool: changeMade - whether a change has been made
                int: RCounter - the updated counter of R lanes
            """
            nonlocal self
            #if minRight is greater than maxRS
            if((minRight > maxRS) and (minRight != (maxRS + 1))):
                #move right traffic from R to RS
                changeMade = True
                self.lanes['RS'][0].updateDirectionFlow(1, 2, 'add')
                self.lanes['R'][RCounter].updateDirectionFlow(1, 2, 'sub')

                maxRS = self.lanes['RS'][0].totalFlow
                minRight = min(lane.totalFlow for lane in self.lanes['R'])

                RCounter = (RCounter + 1) % len(self.lanes['R'])
            
            return minRight, maxRS, changeMade, RCounter

        def minLeftGTmaxLS(minLeft, maxLS, changeMade, LCounter):
            """
            Description: if minLeft is greater than maxLS, move left traffic from L to LS
            Args:
                maxLS(int): the flow in the LS lane
                minLeft(int): the lowest flow out of the L lanes
                changeMade(bool): whether or not a change has been made 
                LCounter(int): the counter to iterate through L lanes
            
            Returns:
                int: maxLS - the updated maxLS variable
                int: minLeft - the updated minLeft variable
                bool: changeMade - whether a change has been made
                int: LCounter - the updated counter of L lanes
            """
            nonlocal self
            #if minLeft is greater than maxLS
            if((minLeft > maxLS) and (minLeft != (maxLS + 1))):
                #move left traffic from L to LS
                changeMade = True
                self.lanes['LS'][0].updateDirectionFlow(1, 0, 'add')
                self.lanes['L'][LCounter].updateDirectionFlow(1, 0, 'sub')

                maxLS = self.lanes['LS'][0].totalFlow
                minLeft = min(lane.totalFlow for lane in self.lanes['L'])

                LCounter = (LCounter + 1) % len(self.lanes['L'])
            
            return minLeft, maxLS, changeMade, LCounter

        def minStraightGTmaxRS(minStraight, maxRS, changeMade, SCounter):
            """
            Description: if minStraight is greater than maxRS, move straight traffic from S to RS
            Args:
                maxRS(int): the flow in the RS lane
                minStraight(int): the lowest flow out of the S lanes
                changeMade(bool): whether or not a change has been made 
                SCounter(int): the counter to iterate through S lanes
            
            Returns:
                int: maxRS - the updated maxRS variable
                int: minStraight - the updated minStraight variable
                bool: changeMade - whether a change has been made
                int: SCounter - the updated counter of S lanes
            """
            nonlocal self
            #if minStraight is greater than maxRS
            if((minStraight > maxRS) and (minStraight != (maxRS + 1))):
                #move straight traffic from S to RS
                changeMade = True
                self.lanes['RS'][0].updateDirectionFlow(1, 1, 'add')
                self.lanes['S'][SCounter].updateDirectionFlow(1, 1, 'sub')

                maxRS = self.lanes['RS'][0].totalFlow
                minStraight = min(lane.totalFlow for lane in self.lanes['S'])

                SCounter = (SCounter + 1) % len(self.lanes['S'])
            
            return minStraight, maxRS, changeMade, SCounter

        def minStraightGTmaxLS(minStraight, maxLS, changeMade, SCounter):
            """
            Description: if minStraight is greater than maxLS, move straight traffic from S to LS
            Args:
                maxLS(int): the flow in the LS lane
                minStraight(int): the lowest flow out of the S lanes
                changeMade(bool): whether or not a change has been made 
                SCounter(int): the counter to iterate through S lanes
            
            Returns:
                int: maxLS - the updated maxLS variable
                int: minStraight - the updated minStraight variable
                bool: changeMade - whether a change has been made
                int: SCounter - the updated counter of S lanes
            """
            #if minStraight is greater than maxLS
            if((minStraight > maxLS) and (minStraight != (maxLS + 1))):
                #move straight traffic from S to LS
                changeMade = True
                self.lanes['LS'][0].updateDirectionFlow(1, 1, 'add')
                self.lanes['S'][SCounter].updateDirectionFlow(1, 1, 'sub')

                maxLS = self.lanes['LS'][0].totalFlow
                minStraight = min(lane.totalFlow for lane in self.lanes['S'])

                SCounter = (SCounter + 1) % len(self.lanes['S'])
        
            return minStraight, maxLS, changeMade, SCounter
        

        def distributeLRorLRS(laneType):
            nonlocal self
            """
            Description: This function performs the vehicle distribution when there is an LR or an LRS lane within the junction.

            Args:
                laneType(string): a string of either LR or LRS depending on the type of lane
            """
            
            LCounter, RCounter = 0, 0

            # firstly the traffic is evenly divided between the purely left turn lanes and the purely right turn lanes
            if 'L' in self.lanes:  # checks if there is a left turn lane in the junction
                # if there is a left turn lane, distribute the left-turn traffic between the left lanes
                laneFlow = self.VPHFlowDirections[0] // len(self.lanes['L'])  # divides the vehicles by the number of left turning lanes (without remainders)
                remainder = self.VPHFlowDirections[0] % len(self.lanes['L'])  # finds the remainder of this division between the lanes

                firstIteration = True  # initialises a first iteration check variable
                lanes = self.lanes['L']  # gets all of the lanes for the left direction
                for lane in lanes:  # iterates over the lanes
                    if (firstIteration):  # checks if this is the first iteration
                        lane.updateDirectionFlow((laneFlow + remainder), 0, 'rep')  # updates the left VPH for the lane, with the divided amount plus the remainder of the division
                        firstIteration = False
                    else:
                        lane.updateDirectionFlow(laneFlow, 0, 'rep')  # updates the left VPH for the lane with the divided amount

                maxLeft = max(lane.totalFlow for lane in self.lanes['L'])

            else:  # otherwise if there are no left lanes, then all left turn traffic should be added to the LR/LRS lane
                self.lanes[laneType][0].updateDirectionFlow(self.VPHFlowDirections[0], 0, 'add')  # adds the left traffic to the lane

            if 'R' in self.lanes:  # if there is a right turn lane in the junction
                # divide the right turn traffic amongst the right turn lanes
                laneFlow = self.VPHFlowDirections[2] // len(self.lanes['R'])  # divides the vehicles by the number of right turning lanes (without remainders)
                remainder = self.VPHFlowDirections[2] % len(self.lanes['R'])  # finds the remainder of this division between the lanes

                firstIteration = True  # initialises a first iteration check variable
                lanes = self.lanes['R']  # gets all of the lanes for the right direction
                for lane in lanes:  # iterates over the lanes
                    if (firstIteration):  # checks if this is the first iteration
                        lane.updateDirectionFlow((laneFlow + remainder), 2, 'rep')  # updates the right VPH for the lane, with the divided amount and the remainder
                        firstIteration = False
                    else:
                        lane.updateDirectionFlow(laneFlow, 2, 'rep')  # updates the right VPH for the lane

                # find the right turn lane with the maximum flow
                maxRight = max(lane.totalFlow for lane in self.lanes['R'])

            else:  # otherwise if there are no right lanes, then all right turn traffic should be added to the LR/LRS lane
                self.lanes[laneType][0].updateDirectionFlow(self.VPHFlowDirections[2], 2, 'add')  # adds the right traffic to the lane

            if (laneType == 'LRS'):
                self.lanes[laneType][0].updateDirectionFlow(self.VPHFlowDirections[1], 1, 'add')  # add all of the straight lane flow to the LRS lane

            # if there are both left turn lanes and right turn lanes
            if (('L' in self.lanes) and ('R' in self.lanes)):
                # if the right turn lanes have higher flow than the left turn lanes
                if (maxRight > maxLeft):
                    # while the maxRight is more than the left and whilst the maxRight is more than the LR/LRS lane
                    while ((maxRight > maxLeft) and (maxRight > self.lanes[laneType][0].totalFlow)):
                        if self.lanes['R'][RCounter].totalFlow > self.lanes[laneType][0].totalFlow:  # as long as the lane is less than the the LR/LRS lane
                            # add one flow from the lane to the LR/LRS lane
                            self.lanes['R'][RCounter].updateDirectionFlow(1, 2, 'sub')
                            self.lanes[laneType][0].updateDirectionFlow(1, 2, 'add')

                        # update the RCounter
                        RCounter = (RCounter + 1) % len(self.lanes['R'])

                        # update the maximum right flow
                        maxRight = max(lane.totalFlow for lane in self.lanes['R'])

                # if the left turn lanes have a higher flow than the right turn lanes
                elif (maxLeft > maxRight):
                    # while the maxLeft is more than the right and whilst the maxLeft is more than the LR/LRS lane
                    while ((maxLeft > maxRight) and (maxLeft > self.lanes[laneType][0].totalFlow)):
                        if self.lanes['L'][LCounter].totalFlow > self.lanes[laneType][0].totalFlow:  # as long as the lane is more than the the LR/LRS lane
                            # add one flow from the lane to the LR/LRS lane
                            self.lanes['L'][LCounter].updateDirectionFlow(1, 0, 'sub')
                            self.lanes[laneType][0].updateDirectionFlow(1, 0, 'add')

                        # update the LCounter
                        LCounter = (LCounter + 1) % len(self.lanes['L'])

                        # update the maxLeft variable
                        maxLeft = max(lane.totalFlow for lane in self.lanes['L'])

                # if either the maxLeft and maxRight is still greater than the LR/LRS lane after it's been distributed, we distribute from both lanes to the LR
                if (max(maxLeft, maxRight) > self.lanes[laneType][0].totalFlow):
                    # iterate until the LR/LRS is >= the maxLeft or maxRight
                    while (max(maxLeft, maxRight) > self.lanes[laneType][0].totalFlow):

                        if self.lanes['L'][LCounter].totalFlow > self.lanes[laneType][0].totalFlow:  # as long as the lane is less than the the LR/LRS lane
                            # add one flow from the lane to the LR/LRS lane
                            self.lanes['L'][LCounter].updateDirectionFlow(1, 0, 'sub')
                            self.lanes[laneType][0].updateDirectionFlow(1, 0, 'add')

                        # update the LCounter
                        LCounter = (LCounter + 1) % len(self.lanes['L'])

                        if self.lanes['R'][RCounter].totalFlow > self.lanes[laneType][0].totalFlow:  # as long as the lane is less than the the LR/LRS lane
                            # add one flow from the lane to the LR/LRS lane
                            self.lanes['R'][RCounter].updateDirectionFlow(1, 2, 'sub')
                            self.lanes[laneType][0].updateDirectionFlow(1, 2, 'add')

                        # update the RCounter
                        RCounter = (RCounter + 1) % len(self.lanes['R'])

                        # updates the maxLeft variable
                        maxLeft = max(lane.totalFlow for lane in self.lanes['L'])

                        # updates the maxRight variable
                        maxRight = max(lane.totalFlow for lane in self.lanes['R'])

            # if there is not any left turn lanes but there are right turn lanes
            elif (('L' not in self.lanes) and ('R' in self.lanes)):
                # while the maxRight is higher than the LR/LRS lane
                while (maxRight > self.lanes[laneType][0].totalFlow):
                    # iterate over the right-turn lanes
                    if self.lanes['R'][RCounter].totalFlow > self.lanes[laneType][0].totalFlow:  # as long as the lane is less than the the LR/LRS lane
                        # add one flow from the lane to the LR/LRS lane
                        self.lanes['R'][RCounter].updateDirectionFlow(1, 2, 'sub')
                        self.lanes[laneType][0].updateDirectionFlow(1, 2, 'add')

                    # update the RCounter
                    RCounter = (RCounter + 1) % len(self.lanes['R'])

                    # update the maxRight flow
                    maxRight = max(lane.totalFlow for lane in self.lanes['R'])

            # if there is not any right turn lanes but there are left turn lanes
            elif (('L' in self.lanes) and ('R' not in self.lanes)):
                # while the maxLeft is greater than the LR/LRS variable
                while (maxLeft > self.lanes[laneType][0].totalFlow):
                    if self.lanes['L'][LCounter].totalFlow > self.lanes[laneType][0].totalFlow:  # as long as the lane is less than the the LR/LRS lane
                        # add one flow from the lane to the LR/LRS lane
                        self.lanes['L'][LCounter].updateDirectionFlow(1, 0, 'sub')
                        self.lanes[laneType][0].updateDirectionFlow(1, 0, 'add')

                    # update the LCounter
                    LCounter = (LCounter + 1) % len(self.lanes['L'])

                    # update the maxLeft variable
                    maxLeft = max(lane.totalFlow for lane in self.lanes['L'])


        def distributeS():
            """
            Description: Distributes the traffic if there is an S lane in the direction

            Methods:
                

            """
            nonlocal self

            if (('LS' not in self.lanes) and ('RS' not in self.lanes)):
                if ('L' in self.lanes):
                    #distribute the left-turn traffic between the left lanes
                    laneFlow = self.VPHFlowDirections[0] // (len(self.lanes['L']))  # divides the vehicles by the number of left turning lanes (without remainders)
                    remainder = self.VPHFlowDirections[0] % (len(self.lanes['L']))  # finds the remainder of this division between the lanes
            
                    firstIteration = True  # initialises a first iteration check variable
                    lanes = self.lanes['L']  # gets all of the lanes for the left direction
                    for lane in lanes:  # iterates over the lanes
                        if (firstIteration):  # checks if this is the first iteration
                            lane.updateDirectionFlow((laneFlow + remainder), 0, 'rep')  # updates the left VPH for the lane, with the divided amount plus the remainder of the division
                            firstIteration = False
                        else:
                            lane.updateDirectionFlow(laneFlow, 0, 'rep')  # updates the left VPH for the lane with the divided amount

                    maxLeft = max(lane.totalFlow for lane in self.lanes['L'])
                    minLeft = min(lane.totalFlow for lane in self.lanes['L'])
                
                if ('R' in self.lanes):
                    #divide the right turn traffic amongst the right turn lanes
                    laneFlow = self.VPHFlowDirections[2] // (len(self.lanes['R']))  # divides the vehicles by the number of right turning lanes (without remainders)
                    remainder = self.VPHFlowDirections[2] % (len(self.lanes['R']))  # finds the remainder of this division between the lanes
            
                    firstIteration = True  # initialises a first iteration check variable
                    lanes = self.lanes['R']  # gets all of the lanes for the right direction
                    for lane in lanes:  # iterates over the lanes
                        if (firstIteration):  # checks if this is the first iteration
                            lane.updateDirectionFlow((laneFlow + remainder), 2, 'rep')  # updates the right VPH for the lane, with the divided amount and the remainder
                            firstIteration = False
                        else:
                            lane.updateDirectionFlow(laneFlow, 2, 'rep')  # updates the right VPH for the lane, with the divided lane flow

                #distributes the straight traffic between the S lanes
                laneFlow = self.VPHFlowDirections[1] // len(self.lanes['S'])  # divides the vehicles by the number of straight lanes (without remainders)
                remainder = self.VPHFlowDirections[1] % len(self.lanes['S'])  # finds the remainder of this division between the lanes

                firstIteration = True  # initialises a first iteration check variable
                lanes = self.lanes['S']  # gets all of the lanes for the straight direction
                for lane in lanes:  # itertates over the lanes
                    if (firstIteration):  # checks if this is the first iteration
                        lane.updateDirectionFlow((laneFlow + remainder), 1, 'rep')  # updates the straight VPH for the lane, with the divided amount and the remainder
                        firstIteration = False
                    else:
                        lane.updateDirectionFlow(laneFlow, 1, 'rep')  # updates the straight VPH for the lane, with the divided lane flow

            else:
                # defines initial values for maximum left and straight lane and maximum right and straight lane
                maxLS, maxRS = 0, 0
                RCounter, LCounter, SCounter = 0, 0, 0

                # if all pure lane types in the junction
                if (('R' in self.lanes) and ('L' in self.lanes)):

                    # if a left and straight and right and straight lane in the junction
                    if (('LS' in self.lanes) and ('RS' in self.lanes)):

                        #distribute the left-turn traffic between the left lanes and LS
                        laneFlow = self.VPHFlowDirections[0] // (len(self.lanes['L']) + 1)  # divides the vehicles by the number of left turning lanes (without remainders)
                        remainder = self.VPHFlowDirections[0] % (len(self.lanes['L']) + 1)  # finds the remainder of this division between the lanes
                
                        firstIteration = True  # initialises a first iteration check variable
                        lanes = self.lanes['L']  # gets all of the lanes for the left direction
                        for lane in lanes:  # iterates over the lanes
                            if (firstIteration):  # checks if this is the first iteration
                                lane.updateDirectionFlow((laneFlow + remainder), 0, 'rep')  # updates the left VPH for the lane, with the divided amount plus the remainder of the division
                                firstIteration = False
                            else:
                                lane.updateDirectionFlow(laneFlow, 0, 'rep')  # updates the left VPH for the lane with the divided amount
                
                        self.lanes['LS'][0].updateDirectionFlow(laneFlow, 0, 'rep')

                        maxLeft = max(lane.totalFlow for lane in self.lanes['L'])
                        minLeft = min(lane.totalFlow for lane in self.lanes['L'])


                        #divide the right turn traffic amongst the right turn lanes and RS
                        laneFlow = self.VPHFlowDirections[2] // (len(self.lanes['R']) + 1)  # divides the vehicles by the number of right turning lanes (without remainders)
                        remainder = self.VPHFlowDirections[2] % (len(self.lanes['R']) + 1)  # finds the remainder of this division between the lanes
                
                        firstIteration = True  # initialises a first iteration check variable
                        lanes = self.lanes['R']  # gets all of the lanes for the right direction
                        for lane in lanes:  # iterates over the lanes
                            if (firstIteration):  # checks if this is the first iteration
                                lane.updateDirectionFlow((laneFlow + remainder), 2, 'rep')  # updates the right VPH for the lane, with the divided amount and the remainder
                                firstIteration = False
                            else:
                                lane.updateDirectionFlow(laneFlow, 2, 'rep')  # updates the right VPH for the lane, with the divided lane flow
                        
                        self.lanes['RS'][0].updateDirectionFlow(laneFlow, 2, 'rep') #adds the right traffic to the RS lane

                        maxRight = max(lane.totalFlow for lane in self.lanes['R'])
                        minRight = min(lane.totalFlow for lane in self.lanes['R'])
                        

                        #distributes the straight traffic between the S, RS and LS lanes
                        laneFlow = self.VPHFlowDirections[1] // (len(self.lanes['S']) + 2)  # divides the vehicles by the number of straight lanes (without remainders)
                        remainder = self.VPHFlowDirections[1] % (len(self.lanes['S']) + 2)  # finds the remainder of this division between the lanes

                        firstIteration = True  # initialises a first iteration check variable
                        lanes = self.lanes['S']  # gets all of the lanes for the straight direction
                        for lane in lanes:  # itertates over the lanes
                            if (firstIteration):  # checks if this is the first iteration
                                lane.updateDirectionFlow((laneFlow + remainder), 1, 'rep')  # updates the straight VPH for the lane, with the divided amount and the remainder
                                firstIteration = False
                            else:
                                lane.updateDirectionFlow(laneFlow, 1, 'rep')  # updates the straight VPH for the lane, with the divided lane flow

                        # find the straight lane with the maximum flow
                        maxStraight = max(lane.totalFlow for lane in self.lanes['S'])
                        minStraight = min(lane.totalFlow for lane in self.lanes['S'])

                        #add the straight traffic to the LS and RS lanes
                        self.lanes['LS'][0].updateDirectionFlow(laneFlow, 1, 'add')
                        self.lanes['RS'][0].updateDirectionFlow(laneFlow, 1, 'add')

                        #sets maxRS and maxLS
                        maxRS = self.lanes['RS'][0].totalFlow
                        maxLS = self.lanes['LS'][0].totalFlow

                        changeMade = True

                        while(changeMade):
                            changeMade = False

                            maxRS, minRight, changeMade, RCounter = maxRSGTminRight(maxRS, minRight, changeMade, RCounter)
                            
                            maxLS, minLeft, changeMade, LCounter = maxLSGTminLeft(maxLS, minLeft, changeMade, LCounter)
                            
                            maxLS, minStraight, changeMade, SCounter = maxLSGTminStraight(maxLS, minStraight, changeMade, SCounter)
                            
                            maxRS, minStraight, changeMade, SCounter = maxRSGTminStraight(maxRS, minStraight, changeMade, SCounter)
                            
                            maxLS, maxRS, changeMade = maxLSGTmaxRS(maxLS, maxRS, changeMade)
                                
                            maxRS, maxLS, changeMade = maxRSGTmaxLS(maxRS, maxLS, changeMade)
                            
                            minRight, maxRS, changeMade, RCounter = minRightGTmaxRS(minRight, maxRS, changeMade, RCounter)
                            
                            minLeft, maxLS, changeMade, LCounter = minLeftGTmaxLS(minLeft, maxLS, changeMade, LCounter)
                            
                            minStraight, maxRS, changeMade, SCounter = minStraightGTmaxRS(minStraight, maxRS, changeMade, SCounter)
                            
                            minStraight, maxLS, changeMade, SCounter = minStraightGTmaxLS(minStraight, maxLS, changeMade, SCounter)

                    # if a right and straight lane but not a left and straight lane in the junction
                    elif (('LS' not in self.lanes) and ('RS' in self.lanes)):

                        #distribute the left-turn traffic between the left lanes
                        laneFlow = self.VPHFlowDirections[0] // len(self.lanes['L'])  # divides the vehicles by the number of left turning lanes (without remainders)
                        remainder = self.VPHFlowDirections[0] % len(self.lanes['L'])  # finds the remainder of this division between the lanes
                
                        firstIteration = True  # initialises a first iteration check variable
                        lanes = self.lanes['L']  # gets all of the lanes for the left direction
                        for lane in lanes:  # iterates over the lanes
                            if (firstIteration):  # checks if this is the first iteration
                                lane.updateDirectionFlow((laneFlow + remainder), 0, 'rep')  # updates the left VPH for the lane, with the divided amount plus the remainder of the division
                                firstIteration = False
                            else:
                                lane.updateDirectionFlow(laneFlow, 0, 'rep')  # updates the left VPH for the lane with the divided amount

                        maxLeft = max(lane.totalFlow for lane in self.lanes['L'])
                        minLeft = min(lane.totalFlow for lane in self.lanes['L'])


                        #divide the right turn traffic amongst the right turn lanes and RS
                        laneFlow = self.VPHFlowDirections[2] // (len(self.lanes['R']) + 1)  # divides the vehicles by the number of right turning lanes (without remainders)
                        remainder = self.VPHFlowDirections[2] % (len(self.lanes['R']) + 1)  # finds the remainder of this division between the lanes
                
                        firstIteration = True  # initialises a first iteration check variable
                        lanes = self.lanes['R']  # gets all of the lanes for the right direction
                        for lane in lanes:  # iterates over the lanes
                            if (firstIteration):  # checks if this is the first iteration
                                lane.updateDirectionFlow((laneFlow + remainder), 2, 'rep')  # updates the right VPH for the lane, with the divided amount and the remainder
                                firstIteration = False
                            else:
                                lane.updateDirectionFlow(laneFlow, 2, 'rep')  # updates the right VPH for the lane, with the divided lane flow
                        
                        self.lanes['RS'][0].updateDirectionFlow(laneFlow, 2, 'rep') #adds the right traffic to the RS lane

                        maxRight = max(lane.totalFlow for lane in self.lanes['R'])
                        minRight = min(lane.totalFlow for lane in self.lanes['R'])
                        

                        #distributes the straight traffic between the S, RS lanes
                        laneFlow = self.VPHFlowDirections[1] // (len(self.lanes['S']) + 1)  # divides the vehicles by the number of straight lanes (without remainders)
                        remainder = self.VPHFlowDirections[1] % (len(self.lanes['S']) + 1)  # finds the remainder of this division between the lanes

                        firstIteration = True  # initialises a first iteration check variable
                        lanes = self.lanes['S']  # gets all of the lanes for the straight direction
                        for lane in lanes:  # itertates over the lanes
                            if (firstIteration):  # checks if this is the first iteration
                                lane.updateDirectionFlow((laneFlow + remainder), 1, 'rep')  # updates the straight VPH for the lane, with the divided amount and the remainder
                                firstIteration = False
                            else:
                                lane.updateDirectionFlow(laneFlow, 1, 'rep')  # updates the straight VPH for the lane, with the divided lane flow

                        # find the straight lane with the maximum flow
                        maxStraight = max(lane.totalFlow for lane in self.lanes['S'])
                        minStraight = min(lane.totalFlow for lane in self.lanes['S'])

                        #add the straight traffic to the RS lane
                        self.lanes['RS'][0].updateDirectionFlow(laneFlow, 1, 'add')

                        #sets maxRS
                        maxRS = self.lanes['RS'][0].totalFlow

                        changeMade = True

                        while(changeMade):
                            changeMade = False

                            maxRS, minRight, changeMade, RCounter = maxRSGTminRight(maxRS, minRight, changeMade, RCounter)

                            maxRS, minStraight, changeMade, SCounter = maxRSGTminStraight(maxRS, minStraight, changeMade, SCounter)
                            
                            minRight, maxRS, changeMade, RCounter = minRightGTmaxRS(minRight, maxRS, changeMade, RCounter)
                            
                            minStraight, maxRS, changeMade, SCounter = minStraightGTmaxRS(minStraight, maxRS, changeMade, SCounter)

                    # if a left and straight lane but not a right and straight lane in the junction
                    elif (('LS' in self.lanes) and ('RS' not in self.lanes)):
                        #distribute the left-turn traffic between the left lanes and LS
                        laneFlow = self.VPHFlowDirections[0] // (len(self.lanes['L']) + 1)  # divides the vehicles by the number of left turning lanes (without remainders)
                        remainder = self.VPHFlowDirections[0] % (len(self.lanes['L']) + 1)  # finds the remainder of this division between the lanes
                
                        firstIteration = True  # initialises a first iteration check variable
                        lanes = self.lanes['L']  # gets all of the lanes for the left direction
                        for lane in lanes:  # iterates over the lanes
                            if (firstIteration):  # checks if this is the first iteration
                                lane.updateDirectionFlow((laneFlow + remainder), 0, 'rep')  # updates the left VPH for the lane, with the divided amount plus the remainder of the division
                                firstIteration = False
                            else:
                                lane.updateDirectionFlow(laneFlow, 0, 'rep')  # updates the left VPH for the lane with the divided amount
                
                        self.lanes['LS'][0].updateDirectionFlow(laneFlow, 0, 'rep')

                        maxLeft = max(lane.totalFlow for lane in self.lanes['L'])
                        minLeft = min(lane.totalFlow for lane in self.lanes['L'])


                        #divide the right turn traffic amongst the right turn lanes
                        laneFlow = self.VPHFlowDirections[2] // len(self.lanes['R'])  # divides the vehicles by the number of right turning lanes (without remainders)
                        remainder = self.VPHFlowDirections[2] % len(self.lanes['R'])  # finds the remainder of this division between the lanes
                
                        firstIteration = True  # initialises a first iteration check variable
                        lanes = self.lanes['R']  # gets all of the lanes for the right direction
                        for lane in lanes:  # iterates over the lanes
                            if (firstIteration):  # checks if this is the first iteration
                                lane.updateDirectionFlow((laneFlow + remainder), 2, 'rep')  # updates the right VPH for the lane, with the divided amount and the remainder
                                firstIteration = False
                            else:
                                lane.updateDirectionFlow(laneFlow, 2, 'rep')  # updates the right VPH for the lane, with the divided lane flow

                        maxRight = max(lane.totalFlow for lane in self.lanes['R'])
                        minRight = min(lane.totalFlow for lane in self.lanes['R'])
                        

                        #distributes the straight traffic between the S and LS lanes
                        laneFlow = self.VPHFlowDirections[1] // (len(self.lanes['S']) + 1)  # divides the vehicles by the number of straight lanes (without remainders)
                        remainder = self.VPHFlowDirections[1] % (len(self.lanes['S']) + 1)  # finds the remainder of this division between the lanes

                        firstIteration = True  # initialises a first iteration check variable
                        lanes = self.lanes['S']  # gets all of the lanes for the straight direction
                        for lane in lanes:  # itertates over the lanes
                            if (firstIteration):  # checks if this is the first iteration
                                lane.updateDirectionFlow((laneFlow + remainder), 1, 'rep')  # updates the straight VPH for the lane, with the divided amount and the remainder
                                firstIteration = False
                            else:
                                lane.updateDirectionFlow(laneFlow, 1, 'rep')  # updates the straight VPH for the lane, with the divided lane flow

                        # find the straight lane with the maximum flow
                        maxStraight = max(lane.totalFlow for lane in self.lanes['S'])
                        minStraight = min(lane.totalFlow for lane in self.lanes['S'])

                        #add the straight traffic to the LS lanes
                        self.lanes['LS'][0].updateDirectionFlow(laneFlow, 1, 'add')

                        #sets maxLS
                        maxLS = self.lanes['LS'][0].totalFlow

                        changeMade = True

                        while(changeMade):
                            changeMade = False
                            
                            maxLS, minLeft, changeMade, LCounter = maxLSGTminLeft(maxLS, minLeft, changeMade, LCounter)
                            
                            maxLS, minStraight, changeMade, SCounter = maxLSGTminStraight(maxLS, minStraight, changeMade, SCounter)
                            
                            minLeft, maxLS, changeMade, LCounter = minLeftGTmaxLS(minLeft, maxLS, changeMade, LCounter)
                            
                            minStraight, maxLS, changeMade, SCounter = minStraightGTmaxLS(minStraight, maxLS, changeMade, SCounter)

                ##########################################################
                # if S and R in the junction but not L
                elif (('R' in self.lanes) and ('L' not in self.lanes)):

                    # if RS is in the lanes and LS
                    if (('RS' in self.lanes) and ('LS' in self.lanes)):

                        self.lanes['LS'][0].updateDirectionFlow(self.VPHFlowDirections[0], 0, 'add')  # add all left turn traffic to the LS lane

                        #divide the right turn traffic amongst the right turn lanes and RS
                        laneFlow = self.VPHFlowDirections[2] // (len(self.lanes['R']) + 1)  # divides the vehicles by the number of right turning lanes (without remainders)
                        remainder = self.VPHFlowDirections[2] % (len(self.lanes['R']) + 1)  # finds the remainder of this division between the lanes
                
                        firstIteration = True  # initialises a first iteration check variable
                        lanes = self.lanes['R']  # gets all of the lanes for the right direction
                        for lane in lanes:  # iterates over the lanes
                            if (firstIteration):  # checks if this is the first iteration
                                lane.updateDirectionFlow((laneFlow + remainder), 2, 'rep')  # updates the right VPH for the lane, with the divided amount and the remainder
                                firstIteration = False
                            else:
                                lane.updateDirectionFlow(laneFlow, 2, 'rep')  # updates the right VPH for the lane, with the divided lane flow
                        
                        self.lanes['RS'][0].updateDirectionFlow(laneFlow, 2, 'rep') #adds the right traffic to the RS lane

                        maxRight = max(lane.totalFlow for lane in self.lanes['R'])
                        minRight = min(lane.totalFlow for lane in self.lanes['R'])
                        

                        #distributes the straight traffic between the S, RS and LS lanes
                        laneFlow = self.VPHFlowDirections[1] // (len(self.lanes['S']) + 2)  # divides the vehicles by the number of straight lanes (without remainders)
                        remainder = self.VPHFlowDirections[1] % (len(self.lanes['S']) + 2)  # finds the remainder of this division between the lanes

                        firstIteration = True  # initialises a first iteration check variable
                        lanes = self.lanes['S']  # gets all of the lanes for the straight direction
                        for lane in lanes:  # itertates over the lanes
                            if (firstIteration):  # checks if this is the first iteration
                                lane.updateDirectionFlow((laneFlow + remainder), 1, 'rep')  # updates the straight VPH for the lane, with the divided amount and the remainder
                                firstIteration = False
                            else:
                                lane.updateDirectionFlow(laneFlow, 1, 'rep')  # updates the straight VPH for the lane, with the divided lane flow

                        # find the straight lane with the maximum flow
                        maxStraight = max(lane.totalFlow for lane in self.lanes['S'])
                        minStraight = min(lane.totalFlow for lane in self.lanes['S'])

                        #add the straight traffic to the LS and RS lanes
                        self.lanes['LS'][0].updateDirectionFlow(laneFlow, 1, 'add')
                        self.lanes['RS'][0].updateDirectionFlow(laneFlow, 1, 'add')

                        #sets maxRS and maxLS
                        maxRS = self.lanes['RS'][0].totalFlow
                        maxLS = self.lanes['LS'][0].totalFlow

                        changeMade = True

                        while(changeMade):
                            changeMade = False

                            maxRS, minRight, changeMade, RCounter = maxRSGTminRight(maxRS, minRight, changeMade, RCounter)
                            
                            maxLS, minStraight, changeMade, SCounter = maxLSGTminStraight(maxLS, minStraight, changeMade, SCounter)
                            
                            maxRS, minStraight, changeMade, SCounter = maxRSGTminStraight(maxRS, minStraight, changeMade, SCounter)
                            
                            maxLS, maxRS, changeMade = maxLSGTmaxRS(maxLS, maxRS, changeMade)
                                
                            maxRS, maxLS, changeMade = maxRSGTmaxLS(maxRS, maxLS, changeMade)
                            
                            minRight, maxRS, changeMade, RCounter = minRightGTmaxRS(minRight, maxRS, changeMade, RCounter)
                            
                            minStraight, maxRS, changeMade, SCounter = minStraightGTmaxRS(minStraight, maxRS, changeMade, SCounter)
                            
                            minStraight, maxLS, changeMade, SCounter = minStraightGTmaxLS(minStraight, maxLS, changeMade, SCounter)

                    # if LS in lanes but not RS
                    elif (('RS' not in self.lanes) and ('LS' in self.lanes)):
                        self.lanes['LS'][0].updateDirectionFlow(self.VPHFlowDirections[0], 0, 'add')  # add all left turn traffic to the LS lane

                        #divide the right turn traffic amongst the right turn lanes and RS
                        laneFlow = self.VPHFlowDirections[2] // len(self.lanes['R'])  # divides the vehicles by the number of right turning lanes (without remainders)
                        remainder = self.VPHFlowDirections[2] % len(self.lanes['R'])  # finds the remainder of this division between the lanes
                
                        firstIteration = True  # initialises a first iteration check variable
                        lanes = self.lanes['R']  # gets all of the lanes for the right direction
                        for lane in lanes:  # iterates over the lanes
                            if (firstIteration):  # checks if this is the first iteration
                                lane.updateDirectionFlow((laneFlow + remainder), 2, 'rep')  # updates the right VPH for the lane, with the divided amount and the remainder
                                firstIteration = False
                            else:
                                lane.updateDirectionFlow(laneFlow, 2, 'rep')  # updates the right VPH for the lane, with the divided lane flow

                        maxRight = max(lane.totalFlow for lane in self.lanes['R'])
                        minRight = min(lane.totalFlow for lane in self.lanes['R'])
                        

                        #distributes the straight traffic between the S and LS lanes
                        laneFlow = self.VPHFlowDirections[1] // (len(self.lanes['S']) + 1)  # divides the vehicles by the number of straight lanes (without remainders)
                        remainder = self.VPHFlowDirections[1] % (len(self.lanes['S']) + 1)  # finds the remainder of this division between the lanes

                        firstIteration = True  # initialises a first iteration check variable
                        lanes = self.lanes['S']  # gets all of the lanes for the straight direction
                        for lane in lanes:  # itertates over the lanes
                            if (firstIteration):  # checks if this is the first iteration
                                lane.updateDirectionFlow((laneFlow + remainder), 1, 'rep')  # updates the straight VPH for the lane, with the divided amount and the remainder
                                firstIteration = False
                            else:
                                lane.updateDirectionFlow(laneFlow, 1, 'rep')  # updates the straight VPH for the lane, with the divided lane flow

                        # find the straight lane with the maximum flow
                        maxStraight = max(lane.totalFlow for lane in self.lanes['S'])
                        minStraight = min(lane.totalFlow for lane in self.lanes['S'])

                        #add the straight traffic to the LS lane
                        self.lanes['LS'][0].updateDirectionFlow(laneFlow, 1, 'add')

                        #sets maxLS
                        maxLS = self.lanes['LS'][0].totalFlow

                        changeMade = True

                        while(changeMade):
                            changeMade = False
                            
                            maxLS, minStraight, changeMade, SCounter = maxLSGTminStraight(maxLS, minStraight, changeMade, SCounter)
                            
                            minStraight, maxLS, changeMade, SCounter = minStraightGTmaxLS(minStraight, maxLS, changeMade, SCounter)

                    #if RS in lanes but not LS
                    elif(('RS' in self.lanes) and ('LS' not in self.lanes)):

                        #divide the right turn traffic amongst the right turn lanes and RS
                        laneFlow = self.VPHFlowDirections[2] // (len(self.lanes['R']) + 1)  # divides the vehicles by the number of right turning lanes (without remainders)
                        remainder = self.VPHFlowDirections[2] % (len(self.lanes['R']) + 1)  # finds the remainder of this division between the lanes
                
                        firstIteration = True  # initialises a first iteration check variable
                        lanes = self.lanes['R']  # gets all of the lanes for the right direction
                        for lane in lanes:  # iterates over the lanes
                            if (firstIteration):  # checks if this is the first iteration
                                lane.updateDirectionFlow((laneFlow + remainder), 2, 'rep')  # updates the right VPH for the lane, with the divided amount and the remainder
                                firstIteration = False
                            else:
                                lane.updateDirectionFlow(laneFlow, 2, 'rep')  # updates the right VPH for the lane, with the divided lane flow
                        
                        self.lanes['RS'][0].updateDirectionFlow(laneFlow, 2, 'rep') #adds the right traffic to the RS lane

                        maxRight = max(lane.totalFlow for lane in self.lanes['R'])
                        minRight = min(lane.totalFlow for lane in self.lanes['R'])
                        

                        #distributes the straight traffic between the S, RS and LS lanes
                        laneFlow = self.VPHFlowDirections[1] // (len(self.lanes['S']) + 1)  # divides the vehicles by the number of straight lanes (without remainders)
                        remainder = self.VPHFlowDirections[1] % (len(self.lanes['S']) + 1)  # finds the remainder of this division between the lanes

                        firstIteration = True  # initialises a first iteration check variable
                        lanes = self.lanes['S']  # gets all of the lanes for the straight direction
                        for lane in lanes:  # itertates over the lanes
                            if (firstIteration):  # checks if this is the first iteration
                                lane.updateDirectionFlow((laneFlow + remainder), 1, 'rep')  # updates the straight VPH for the lane, with the divided amount and the remainder
                                firstIteration = False
                            else:
                                lane.updateDirectionFlow(laneFlow, 1, 'rep')  # updates the straight VPH for the lane, with the divided lane flow

                        # find the straight lane with the maximum flow
                        maxStraight = max(lane.totalFlow for lane in self.lanes['S'])
                        minStraight = min(lane.totalFlow for lane in self.lanes['S'])

                        #add the straight traffic to the RS lanes
                        self.lanes['RS'][0].updateDirectionFlow(laneFlow, 1, 'add')

                        #sets maxRS 
                        maxRS = self.lanes['RS'][0].totalFlow

                        changeMade = True

                        while(changeMade):
                            changeMade = False

                            maxRS, minRight, changeMade, RCounter = maxRSGTminRight(maxRS, minRight, changeMade, RCounter)
                            
                            maxRS, minStraight, changeMade, SCounter = maxRSGTminStraight(maxRS, minStraight, changeMade, SCounter)
                            
                            minRight, maxRS, changeMade, RCounter = minRightGTmaxRS(minRight, maxRS, changeMade, RCounter)
                            
                            minStraight, maxRS, changeMade, SCounter = minStraightGTmaxRS(minStraight, maxRS, changeMade, SCounter)

                ##########################################################
                # if S and L in the junction but not R
                elif (('R' not in self.lanes) and ('L' in self.lanes)):
                    # if RS is in the lanes but not LS
                    if (('RS' in self.lanes) and ('LS' in self.lanes)):
                        self.lanes['RS'][0].updateDirectionFlow(self.VPHFlowDirections[2], 2, 'add')  # add all right turn traffic to the RS lane

                        #distribute the left-turn traffic between the left lanes and LS
                        laneFlow = self.VPHFlowDirections[0] // (len(self.lanes['L']) + 1)  # divides the vehicles by the number of left turning lanes (without remainders)
                        remainder = self.VPHFlowDirections[0] % (len(self.lanes['L']) + 1)  # finds the remainder of this division between the lanes
                
                        firstIteration = True  # initialises a first iteration check variable
                        lanes = self.lanes['L']  # gets all of the lanes for the left direction
                        for lane in lanes:  # iterates over the lanes
                            if (firstIteration):  # checks if this is the first iteration
                                lane.updateDirectionFlow((laneFlow + remainder), 0, 'rep')  # updates the left VPH for the lane, with the divided amount plus the remainder of the division
                                firstIteration = False
                            else:
                                lane.updateDirectionFlow(laneFlow, 0, 'rep')  # updates the left VPH for the lane with the divided amount
                
                        self.lanes['LS'][0].updateDirectionFlow(laneFlow, 0, 'rep')

                        maxLeft = max(lane.totalFlow for lane in self.lanes['L'])
                        minLeft = min(lane.totalFlow for lane in self.lanes['L'])
                        

                        #distributes the straight traffic between the S, RS and LS lanes
                        laneFlow = self.VPHFlowDirections[1] // (len(self.lanes['S']) + 2)  # divides the vehicles by the number of straight lanes (without remainders)
                        remainder = self.VPHFlowDirections[1] % (len(self.lanes['S']) + 2)  # finds the remainder of this division between the lanes

                        firstIteration = True  # initialises a first iteration check variable
                        lanes = self.lanes['S']  # gets all of the lanes for the straight direction
                        for lane in lanes:  # itertates over the lanes
                            if (firstIteration):  # checks if this is the first iteration
                                lane.updateDirectionFlow((laneFlow + remainder), 1, 'rep')  # updates the straight VPH for the lane, with the divided amount and the remainder
                                firstIteration = False
                            else:
                                lane.updateDirectionFlow(laneFlow, 1, 'rep')  # updates the straight VPH for the lane, with the divided lane flow

                        # find the straight lane with the maximum flow
                        maxStraight = max(lane.totalFlow for lane in self.lanes['S'])
                        minStraight = min(lane.totalFlow for lane in self.lanes['S'])

                        #add the straight traffic to the LS and RS lanes
                        self.lanes['LS'][0].updateDirectionFlow(laneFlow, 1, 'add')
                        self.lanes['RS'][0].updateDirectionFlow(laneFlow, 1, 'add')

                        #sets maxRS and maxLS
                        maxRS = self.lanes['RS'][0].totalFlow
                        maxLS = self.lanes['LS'][0].totalFlow

                        changeMade = True

                        while(changeMade):
                            changeMade = False
                            
                            maxLS, minLeft, changeMade, LCounter = maxLSGTminLeft(maxLS, minLeft, changeMade, LCounter)
                            
                            maxLS, minStraight, changeMade, SCounter = maxLSGTminStraight(maxLS, minStraight, changeMade, SCounter)
                            
                            maxRS, minStraight, changeMade, SCounter = maxRSGTminStraight(maxRS, minStraight, changeMade, SCounter)
                            
                            maxLS, maxRS, changeMade = maxLSGTmaxRS(maxLS, maxRS, changeMade)
                                
                            maxRS, maxLS, changeMade = maxRSGTmaxLS(maxRS, maxLS, changeMade)
                            
                            minLeft, maxLS, changeMade, LCounter = minLeftGTmaxLS(minLeft, maxLS, changeMade, LCounter)
                            
                            minStraight, maxRS, changeMade, SCounter = minStraightGTmaxRS(minStraight, maxRS, changeMade, SCounter)
                            
                            minStraight, maxLS, changeMade, SCounter = minStraightGTmaxLS(minStraight, maxLS, changeMade, SCounter)

                    # if RS in lanes but not LS
                    elif (('RS' in self.lanes) and ('LS' not in self.lanes)):
                        self.lanes['RS'][0].updateDirectionFlow(self.VPHFlowDirections[2], 2, 'add')  # add all right turn traffic to the RS lane

                        #distribute the left-turn traffic between the left lanes and LS
                        laneFlow = self.VPHFlowDirections[0] // len(self.lanes['L'])  # divides the vehicles by the number of left turning lanes (without remainders)
                        remainder = self.VPHFlowDirections[0] % len(self.lanes['L'])  # finds the remainder of this division between the lanes
                
                        firstIteration = True  # initialises a first iteration check variable
                        lanes = self.lanes['L']  # gets all of the lanes for the left direction
                        for lane in lanes:  # iterates over the lanes
                            if (firstIteration):  # checks if this is the first iteration
                                lane.updateDirectionFlow((laneFlow + remainder), 0, 'rep')  # updates the left VPH for the lane, with the divided amount plus the remainder of the division
                                firstIteration = False
                            else:
                                lane.updateDirectionFlow(laneFlow, 0, 'rep')  # updates the left VPH for the lane with the divided amount

                        maxLeft = max(lane.totalFlow for lane in self.lanes['L'])
                        minLeft = min(lane.totalFlow for lane in self.lanes['L'])
                        

                        #distributes the straight traffic between the S and RS lanes
                        laneFlow = self.VPHFlowDirections[1] // (len(self.lanes['S']) + 1)  # divides the vehicles by the number of straight lanes (without remainders)
                        remainder = self.VPHFlowDirections[1] % (len(self.lanes['S']) + 1)  # finds the remainder of this division between the lanes

                        firstIteration = True  # initialises a first iteration check variable
                        lanes = self.lanes['S']  # gets all of the lanes for the straight direction
                        for lane in lanes:  # itertates over the lanes
                            if (firstIteration):  # checks if this is the first iteration
                                lane.updateDirectionFlow((laneFlow + remainder), 1, 'rep')  # updates the straight VPH for the lane, with the divided amount and the remainder
                                firstIteration = False
                            else:
                                lane.updateDirectionFlow(laneFlow, 1, 'rep')  # updates the straight VPH for the lane, with the divided lane flow

                        # find the straight lane with the maximum flow
                        maxStraight = max(lane.totalFlow for lane in self.lanes['S'])
                        minStraight = min(lane.totalFlow for lane in self.lanes['S'])

                        #add the straight traffic to the RS lane
                        self.lanes['RS'][0].updateDirectionFlow(laneFlow, 1, 'add')

                        #sets maxRS
                        maxRS = self.lanes['RS'][0].totalFlow

                        changeMade = True

                        while(changeMade):
                            changeMade = False
                            
                            maxRS, minStraight, changeMade, SCounter = maxRSGTminStraight(maxRS, minStraight, changeMade, SCounter)
                            
                            minStraight, maxRS, changeMade, SCounter = minStraightGTmaxRS(minStraight, maxRS, changeMade, SCounter)

                    #if LS in lanes but not RS
                    elif(('RS' not in self.lanes) and ('LS' in self.lanes)):
                        #distribute the left-turn traffic between the left lanes and LS
                        laneFlow = self.VPHFlowDirections[0] // (len(self.lanes['L']) + 1)  # divides the vehicles by the number of left turning lanes (without remainders)
                        remainder = self.VPHFlowDirections[0] % (len(self.lanes['L']) + 1)  # finds the remainder of this division between the lanes
                
                        firstIteration = True  # initialises a first iteration check variable
                        lanes = self.lanes['L']  # gets all of the lanes for the left direction
                        for lane in lanes:  # iterates over the lanes
                            if (firstIteration):  # checks if this is the first iteration
                                lane.updateDirectionFlow((laneFlow + remainder), 0, 'rep')  # updates the left VPH for the lane, with the divided amount plus the remainder of the division
                                firstIteration = False
                            else:
                                lane.updateDirectionFlow(laneFlow, 0, 'rep')  # updates the left VPH for the lane with the divided amount
                
                        self.lanes['LS'][0].updateDirectionFlow(laneFlow, 0, 'rep')

                        maxLeft = max(lane.totalFlow for lane in self.lanes['L'])
                        minLeft = min(lane.totalFlow for lane in self.lanes['L'])
                        

                        #distributes the straight traffic between the S, RS and LS lanes
                        laneFlow = self.VPHFlowDirections[1] // (len(self.lanes['S']) + 1)  # divides the vehicles by the number of straight lanes (without remainders)
                        remainder = self.VPHFlowDirections[1] % (len(self.lanes['S']) + 1)  # finds the remainder of this division between the lanes

                        firstIteration = True  # initialises a first iteration check variable
                        lanes = self.lanes['S']  # gets all of the lanes for the straight direction
                        for lane in lanes:  # itertates over the lanes
                            if (firstIteration):  # checks if this is the first iteration
                                lane.updateDirectionFlow((laneFlow + remainder), 1, 'rep')  # updates the straight VPH for the lane, with the divided amount and the remainder
                                firstIteration = False
                            else:
                                lane.updateDirectionFlow(laneFlow, 1, 'rep')  # updates the straight VPH for the lane, with the divided lane flow

                        # find the straight lane with the maximum flow
                        maxStraight = max(lane.totalFlow for lane in self.lanes['S'])
                        minStraight = min(lane.totalFlow for lane in self.lanes['S'])

                        #add the straight traffic to the LS lane
                        self.lanes['LS'][0].updateDirectionFlow(laneFlow, 1, 'add')

                        #sets maxLS                    
                        maxLS = self.lanes['LS'][0].totalFlow

                        changeMade = True

                        while(changeMade):
                            changeMade = False
                            
                            maxLS, minLeft, changeMade, LCounter = maxLSGTminLeft(maxLS, minLeft, changeMade, LCounter)
                            
                            maxLS, minStraight, changeMade, SCounter = maxLSGTminStraight(maxLS, minStraight, changeMade, SCounter)
                            
                            minLeft, maxLS, changeMade, LCounter = minLeftGTmaxLS(minLeft, maxLS, changeMade, LCounter)
                            
                            minStraight, maxLS, changeMade, SCounter = minStraightGTmaxLS(minStraight, maxLS, changeMade, SCounter)

                ##########################################################
                # if S in the junction but not R and L
                elif (('R' not in self.lanes) and ('L' not in self.lanes)):
                    # if RS is in the lanes and LS
                    if (('RS' in self.lanes) and ('LS' in self.lanes)):
                        self.lanes['RS'][0].updateDirectionFlow(self.VPHFlowDirections[2], 2, 'add')  # add all right turn traffic to the RS lane
                        self.lanes['LS'][0].updateDirectionFlow(self.VPHFlowDirections[0], 0, 'add')  # add all left turn traffic to the LS lane
                        
                        #distributes the straight traffic between the S, RS and LS lanes
                        laneFlow = self.VPHFlowDirections[1] // (len(self.lanes['S']) + 2)  # divides the vehicles by the number of straight lanes (without remainders)
                        remainder = self.VPHFlowDirections[1] % (len(self.lanes['S']) + 2)  # finds the remainder of this division between the lanes

                        firstIteration = True  # initialises a first iteration check variable
                        lanes = self.lanes['S']  # gets all of the lanes for the straight direction
                        for lane in lanes:  # itertates over the lanes
                            if (firstIteration):  # checks if this is the first iteration
                                lane.updateDirectionFlow((laneFlow + remainder), 1, 'rep')  # updates the straight VPH for the lane, with the divided amount and the remainder
                                firstIteration = False
                            else:
                                lane.updateDirectionFlow(laneFlow, 1, 'rep')  # updates the straight VPH for the lane, with the divided lane flow

                        # find the straight lane with the maximum flow
                        maxStraight = max(lane.totalFlow for lane in self.lanes['S'])
                        minStraight = min(lane.totalFlow for lane in self.lanes['S'])

                        #add the straight traffic to the LS and RS lanes
                        self.lanes['LS'][0].updateDirectionFlow(laneFlow, 1, 'add')
                        self.lanes['RS'][0].updateDirectionFlow(laneFlow, 1, 'add')

                        #sets maxRS and maxLS
                        maxRS = self.lanes['RS'][0].totalFlow
                        maxLS = self.lanes['LS'][0].totalFlow

                        changeMade = True

                        while(changeMade):
                            changeMade = False
                            
                            maxLS, minStraight, changeMade, SCounter = maxLSGTminStraight(maxLS, minStraight, changeMade, SCounter)
                            
                            maxRS, minStraight, changeMade, SCounter = maxRSGTminStraight(maxRS, minStraight, changeMade, SCounter)
                            
                            maxLS, maxRS, changeMade = maxLSGTmaxRS(maxLS, maxRS, changeMade)
                                
                            maxRS, maxLS, changeMade = maxRSGTmaxLS(maxRS, maxLS, changeMade)
                            
                            minStraight, maxRS, changeMade, SCounter = minStraightGTmaxRS(minStraight, maxRS, changeMade, SCounter)
                            
                            minStraight, maxLS, changeMade, SCounter = minStraightGTmaxLS(minStraight, maxLS, changeMade, SCounter)

                    # if LS in lanes but not RS
                    elif (('RS' not in self.lanes) and ('LS' in self.lanes)):
                        self.lanes['LS'][0].updateDirectionFlow(self.VPHFlowDirections[0], 0, 'add')  # add all left turn traffic to the LS lane
                        
                        #distributes the straight traffic between the S, RS and LS lanes
                        laneFlow = self.VPHFlowDirections[1] // (len(self.lanes['S']) + 1)  # divides the vehicles by the number of straight lanes (without remainders)
                        remainder = self.VPHFlowDirections[1] % (len(self.lanes['S']) + 1)  # finds the remainder of this division between the lanes

                        firstIteration = True  # initialises a first iteration check variable
                        lanes = self.lanes['S']  # gets all of the lanes for the straight direction
                        for lane in lanes:  # itertates over the lanes
                            if (firstIteration):  # checks if this is the first iteration
                                lane.updateDirectionFlow((laneFlow + remainder), 1, 'rep')  # updates the straight VPH for the lane, with the divided amount and the remainder
                                firstIteration = False
                            else:
                                lane.updateDirectionFlow(laneFlow, 1, 'rep')  # updates the straight VPH for the lane, with the divided lane flow

                        # find the straight lane with the maximum flow
                        maxStraight = max(lane.totalFlow for lane in self.lanes['S'])
                        minStraight = min(lane.totalFlow for lane in self.lanes['S'])

                        #add the straight traffic to the LS lane
                        self.lanes['LS'][0].updateDirectionFlow(laneFlow, 1, 'add')

                        #sets maxLS
                        maxLS = self.lanes['LS'][0].totalFlow

                        changeMade = True

                        while(changeMade):
                            changeMade = False
                            
                            maxLS, minStraight, changeMade, SCounter = maxLSGTminStraight(maxLS, minStraight, changeMade, SCounter)
                            
                            minStraight, maxLS, changeMade, SCounter = minStraightGTmaxLS(minStraight, maxLS, changeMade, SCounter)

                    # if RS in lanes but not LS
                    elif (('RS' in self.lanes) and ('LS' not in self.lanes)):
                        self.lanes['RS'][0].updateDirectionFlow(self.VPHFlowDirections[2], 2, 'add')  # add all right turn traffic to the RS lane

                        #distributes the straight traffic between the S, RS and LS lanes
                        laneFlow = self.VPHFlowDirections[1] // (len(self.lanes['S']) + 1)  # divides the vehicles by the number of straight lanes (without remainders)
                        remainder = self.VPHFlowDirections[1] % (len(self.lanes['S']) + 1)  # finds the remainder of this division between the lanes

                        firstIteration = True  # initialises a first iteration check variable
                        lanes = self.lanes['S']  # gets all of the lanes for the straight direction
                        for lane in lanes:  # itertates over the lanes
                            if (firstIteration):  # checks if this is the first iteration
                                lane.updateDirectionFlow((laneFlow + remainder), 1, 'rep')  # updates the straight VPH for the lane, with the divided amount and the remainder
                                firstIteration = False
                            else:
                                lane.updateDirectionFlow(laneFlow, 1, 'rep')  # updates the straight VPH for the lane, with the divided lane flow

                        # find the straight lane with the maximum flow
                        maxStraight = max(lane.totalFlow for lane in self.lanes['S'])
                        minStraight = min(lane.totalFlow for lane in self.lanes['S'])

                        #add the straight traffic to the RS lane
                        self.lanes['RS'][0].updateDirectionFlow(laneFlow, 1, 'add')

                        #sets maxRS
                        maxRS = self.lanes['RS'][0].totalFlow

                        changeMade = True

                        while(changeMade):
                            changeMade = False
                            
                            maxRS, minStraight, changeMade, SCounter = maxRSGTminStraight(maxRS, minStraight, changeMade, SCounter)
                            
                            minStraight, maxRS, changeMade, SCounter = minStraightGTmaxRS(minStraight, maxRS, changeMade, SCounter)


        def distributeElse():
            """
            Description: Distributes the junction if there is no LRS, LR or S lane in the junction
            """
            nonlocal self

            if (('LS' not in self.lanes) and ('RS' not in self.lanes)):
                if ('L' in self.lanes):
                    #distribute the left-turn traffic between the left lanes
                    laneFlow = self.VPHFlowDirections[0] // (len(self.lanes['L']))  # divides the vehicles by the number of left turning lanes (without remainders)
                    remainder = self.VPHFlowDirections[0] % (len(self.lanes['L']))  # finds the remainder of this division between the lanes
            
                    firstIteration = True  # initialises a first iteration check variable
                    lanes = self.lanes['L']  # gets all of the lanes for the left direction
                    for lane in lanes:  # iterates over the lanes
                        if (firstIteration):  # checks if this is the first iteration
                            lane.updateDirectionFlow((laneFlow + remainder), 0, 'rep')  # updates the left VPH for the lane, with the divided amount plus the remainder of the division
                            firstIteration = False
                        else:
                            lane.updateDirectionFlow(laneFlow, 0, 'rep')  # updates the left VPH for the lane with the divided amount

                    maxLeft = max(lane.totalFlow for lane in self.lanes['L'])
                    minLeft = min(lane.totalFlow for lane in self.lanes['L'])
                
                if ('R' in self.lanes):
                    #divide the right turn traffic amongst the right turn lanes
                    laneFlow = self.VPHFlowDirections[2] // (len(self.lanes['R']))  # divides the vehicles by the number of right turning lanes (without remainders)
                    remainder = self.VPHFlowDirections[2] % (len(self.lanes['R']))  # finds the remainder of this division between the lanes
            
                    firstIteration = True  # initialises a first iteration check variable
                    lanes = self.lanes['R']  # gets all of the lanes for the right direction
                    for lane in lanes:  # iterates over the lanes
                        if (firstIteration):  # checks if this is the first iteration
                            lane.updateDirectionFlow((laneFlow + remainder), 2, 'rep')  # updates the right VPH for the lane, with the divided amount and the remainder
                            firstIteration = False
                        else:
                            lane.updateDirectionFlow(laneFlow, 2, 'rep')  # updates the right VPH for the lane, with the divided lane flow

            else:
                # defines initial values for maximum left and straight lane and maximum right and straight lane
                maxLS, maxRS = 0, 0
                RCounter, LCounter = 0, 0
            
                if (('L' in self.lanes) and ('R' in self.lanes)):
                    #if LS and RS in the lanes
                    if (('LS' in self.lanes) and ('RS' in self.lanes)):
                        
                        #distribute the left-turn traffic between the left lanes and LS
                        laneFlow = self.VPHFlowDirections[0] // (len(self.lanes['L']) + 1)  # divides the vehicles by the number of left turning lanes (without remainders)
                        remainder = self.VPHFlowDirections[0] % (len(self.lanes['L']) + 1)  # finds the remainder of this division between the lanes
                
                        firstIteration = True  # initialises a first iteration check variable
                        lanes = self.lanes['L']  # gets all of the lanes for the left direction
                        for lane in lanes:  # iterates over the lanes
                            if (firstIteration):  # checks if this is the first iteration
                                lane.updateDirectionFlow((laneFlow + remainder), 0, 'rep')  # updates the left VPH for the lane, with the divided amount plus the remainder of the division
                                firstIteration = False
                            else:
                                lane.updateDirectionFlow(laneFlow, 0, 'rep')  # updates the left VPH for the lane with the divided amount
                
                        self.lanes['LS'][0].updateDirectionFlow(laneFlow, 0, 'rep')

                        maxLeft = max(lane.totalFlow for lane in self.lanes['L'])
                        minLeft = min(lane.totalFlow for lane in self.lanes['L'])


                        #divide the right turn traffic amongst the right turn lanes and RS
                        laneFlow = self.VPHFlowDirections[2] // (len(self.lanes['R']) + 1)  # divides the vehicles by the number of right turning lanes (without remainders)
                        remainder = self.VPHFlowDirections[2] % (len(self.lanes['R']) + 1)  # finds the remainder of this division between the lanes
                
                        firstIteration = True  # initialises a first iteration check variable
                        lanes = self.lanes['R']  # gets all of the lanes for the right direction
                        for lane in lanes:  # iterates over the lanes
                            if (firstIteration):  # checks if this is the first iteration
                                lane.updateDirectionFlow((laneFlow + remainder), 2, 'rep')  # updates the right VPH for the lane, with the divided amount and the remainder
                                firstIteration = False
                            else:
                                lane.updateDirectionFlow(laneFlow, 2, 'rep')  # updates the right VPH for the lane, with the divided lane flow
                        
                        self.lanes['RS'][0].updateDirectionFlow(laneFlow, 2, 'rep') #adds the right traffic to the RS lane

                        maxRight = max(lane.totalFlow for lane in self.lanes['R'])
                        minRight = min(lane.totalFlow for lane in self.lanes['R'])
                        

                        #distributes the straight traffic between the RS and LS lanes
                        laneFlow = self.VPHFlowDirections[1] // 2
                        remainder = self.VPHFlowDirections[1] % 2

                        self.lanes['LS'][0].updateDirectionFlow(laneFlow, 1, 'add')
                        self.lanes['RS'][0].updateDirectionFlow(laneFlow + remainder, 1, 'add')

                        maxRS = self.lanes['RS'][0].totalFlow
                        maxLS = self.lanes['LS'][0].totalFlow

                        changeMade = True

                        while(changeMade):
                            changeMade = False

                            maxRS, minRight, changeMade, RCounter = maxRSGTminRight(maxRS, minRight, changeMade, RCounter)
                            
                            maxLS, minLeft, changeMade, LCounter = maxLSGTminLeft(maxLS, minLeft, changeMade, LCounter)
                            
                            maxLS, maxRS, changeMade = maxLSGTmaxRS(maxLS, maxRS, changeMade)
                                
                            maxRS, maxLS, changeMade = maxRSGTmaxLS(maxRS, maxLS, changeMade)
                            
                            minRight, maxRS, changeMade, RCounter = minRightGTmaxRS(minRight, maxRS, changeMade, RCounter)
                            
                            minLeft, maxLS, changeMade, LCounter = minLeftGTmaxLS(minLeft, maxLS, changeMade, LCounter)
                    
                    #if LS in lanes and not RS
                    elif (('LS' in self.lanes) and ('RS' not in self.lanes)):
                        # adds all straight traffic to the LS lane
                        self.lanes['LS'][0].updateDirectionFlow(self.VPHFlowDirections[1], 1, 'add')

                        #distribute the left-turn traffic between the left lanes and LS
                        laneFlow = self.VPHFlowDirections[0] // (len(self.lanes['L']) + 1)  # divides the vehicles by the number of left turning lanes (without remainders)
                        remainder = self.VPHFlowDirections[0] % (len(self.lanes['L']) + 1)  # finds the remainder of this division between the lanes
                
                        firstIteration = True  # initialises a first iteration check variable
                        lanes = self.lanes['L']  # gets all of the lanes for the left direction
                        for lane in lanes:  # iterates over the lanes
                            if (firstIteration):  # checks if this is the first iteration
                                lane.updateDirectionFlow((laneFlow + remainder), 0, 'rep')  # updates the left VPH for the lane, with the divided amount plus the remainder of the division
                                firstIteration = False
                            else:
                                lane.updateDirectionFlow(laneFlow, 0, 'rep')  # updates the left VPH for the lane with the divided amount
                
                        self.lanes['LS'][0].updateDirectionFlow(laneFlow, 0, 'rep')

                        maxLeft = max(lane.totalFlow for lane in self.lanes['L'])
                        minLeft = min(lane.totalFlow for lane in self.lanes['L'])


                        #divide the right turn traffic amongst the right turn lanes and RS
                        laneFlow = self.VPHFlowDirections[2] // (len(self.lanes['R']))  # divides the vehicles by the number of right turning lanes (without remainders)
                        remainder = self.VPHFlowDirections[2] % (len(self.lanes['R']))  # finds the remainder of this division between the lanes
                
                        firstIteration = True  # initialises a first iteration check variable
                        lanes = self.lanes['R']  # gets all of the lanes for the right direction
                        for lane in lanes:  # iterates over the lanes
                            if (firstIteration):  # checks if this is the first iteration
                                lane.updateDirectionFlow((laneFlow + remainder), 2, 'rep')  # updates the right VPH for the lane, with the divided amount and the remainder
                                firstIteration = False
                            else:
                                lane.updateDirectionFlow(laneFlow, 2, 'rep')  # updates the right VPH for the lane, with the divided lane flow

                        maxRight = max(lane.totalFlow for lane in self.lanes['R'])
                        minRight = min(lane.totalFlow for lane in self.lanes['R'])
            
                        changeMade = True
                        while(changeMade):
                            changeMade = False
                            
                            maxLS, minLeft, changeMade, LCounter = maxLSGTminLeft(maxLS, minLeft, changeMade, LCounter)
                            
                            minLeft, maxLS, changeMade, LCounter = minLeftGTmaxLS(minLeft, maxLS, changeMade, LCounter)
            
                    #if RS in lanes and not LS
                    elif (('LS' not in self.lanes) and ('RS' in self.lanes)):
                        #distribute the left-turn traffic between the left lanes and LS
                        laneFlow = self.VPHFlowDirections[0] // (len(self.lanes['L']))  # divides the vehicles by the number of left turning lanes (without remainders)
                        remainder = self.VPHFlowDirections[0] % (len(self.lanes['L']))  # finds the remainder of this division between the lanes
                
                        firstIteration = True  # initialises a first iteration check variable
                        lanes = self.lanes['L']  # gets all of the lanes for the left direction
                        for lane in lanes:  # iterates over the lanes
                            if (firstIteration):  # checks if this is the first iteration
                                lane.updateDirectionFlow((laneFlow + remainder), 0, 'rep')  # updates the left VPH for the lane, with the divided amount plus the remainder of the division
                                firstIteration = False
                            else:
                                lane.updateDirectionFlow(laneFlow, 0, 'rep')  # updates the left VPH for the lane with the divided amount


                        maxLeft = max(lane.totalFlow for lane in self.lanes['L'])
                        minLeft = min(lane.totalFlow for lane in self.lanes['L'])


                        #divide the right turn traffic amongst the right turn lanes and RS
                        laneFlow = self.VPHFlowDirections[2] // (len(self.lanes['R']) + 1)  # divides the vehicles by the number of right turning lanes (without remainders)
                        remainder = self.VPHFlowDirections[2] % (len(self.lanes['R']) + 1)  # finds the remainder of this division between the lanes
                
                        firstIteration = True  # initialises a first iteration check variable
                        lanes = self.lanes['R']  # gets all of the lanes for the right direction
                        for lane in lanes:  # iterates over the lanes
                            if (firstIteration):  # checks if this is the first iteration
                                lane.updateDirectionFlow((laneFlow + remainder), 2, 'rep')  # updates the right VPH for the lane, with the divided amount and the remainder
                                firstIteration = False
                            else:
                                lane.updateDirectionFlow(laneFlow, 2, 'rep')  # updates the right VPH for the lane, with the divided lane flow
                        
                        self.lanes['RS'][0].updateDirectionFlow(laneFlow, 2, 'rep') #adds the right traffic to the RS lane

                        maxRight = max(lane.totalFlow for lane in self.lanes['R'])
                        minRight = min(lane.totalFlow for lane in self.lanes['R'])
                        
                        # adds all straight traffic to the RS lane
                        self.lanes['RS'][0].updateDirectionFlow(self.VPHFlowDirections[1], 1, 'add')
            
                        changeMade = True
                        while(changeMade):
                            changeMade = False

                            maxRS, minRight, changeMade, RCounter = maxRSGTminRight(maxRS, minRight, changeMade, RCounter)
                            
                            minRight, maxRS, changeMade, RCounter = minRightGTmaxRS(minRight, maxRS, changeMade, RCounter)

            
                elif (('L' in self.lanes) and ('R' not in self.lanes)):
                    # if both LS and RS lanes in junction
                    if (('LS' in self.lanes) and ('RS' in self.lanes)):
            
                        #distribute the left-turn traffic between the left lanes and LS
                        laneFlow = self.VPHFlowDirections[0] // (len(self.lanes['L']) + 1)  # divides the vehicles by the number of left turning lanes (without remainders)
                        remainder = self.VPHFlowDirections[0] % (len(self.lanes['L']) + 1)  # finds the remainder of this division between the lanes
                
                        firstIteration = True  # initialises a first iteration check variable
                        lanes = self.lanes['L']  # gets all of the lanes for the left direction
                        for lane in lanes:  # iterates over the lanes
                            if (firstIteration):  # checks if this is the first iteration
                                lane.updateDirectionFlow((laneFlow + remainder), 0, 'rep')  # updates the left VPH for the lane, with the divided amount plus the remainder of the division
                                firstIteration = False
                            else:
                                lane.updateDirectionFlow(laneFlow, 0, 'rep')  # updates the left VPH for the lane with the divided amount
                
                        self.lanes['LS'][0].updateDirectionFlow(laneFlow, 0, 'rep')

                        maxLeft = max(lane.totalFlow for lane in self.lanes['L'])
                        minLeft = min(lane.totalFlow for lane in self.lanes['L'])
                        

                        #distributes the straight traffic between the RS and LS lanes
                        laneFlow = self.VPHFlowDirections[1] // 2
                        remainder = self.VPHFlowDirections[1] % 2

                        self.lanes['LS'][0].updateDirectionFlow(laneFlow, 1, 'add')
                        self.lanes['RS'][0].updateDirectionFlow(laneFlow + remainder, 1, 'add')

                        maxRS = self.lanes['RS'][0].totalFlow
                        maxLS = self.lanes['LS'][0].totalFlow

                        #adds all right traffic to the RS lane
                        self.lanes['RS'][0].updateDirectionFlow(self.VPHFlowDirections[2], 2, 'add')

                        changeMade = True

                        while(changeMade):
                            changeMade = False
                            
                            maxLS, minLeft, changeMade, LCounter = maxLSGTminLeft(maxLS, minLeft, changeMade, LCounter)
                            
                            maxLS, maxRS, changeMade = maxLSGTmaxRS(maxLS, maxRS, changeMade)
                                
                            maxRS, maxLS, changeMade = maxRSGTmaxLS(maxRS, maxLS, changeMade)
                            
                            minLeft, maxLS, changeMade, LCounter = minLeftGTmaxLS(minLeft, maxLS, changeMade, LCounter)
            
                    #if LS in lanes and RS is not
                    elif (('LS' in self.lanes) and ('RS' not in self.lanes)):
                        # adds all straight traffic to the LS lane
                        self.lanes['LS'][0].updateDirectionFlow(self.VPHFlowDirections[1], 1, 'add')
            
                        #distribute the left-turn traffic between the left lanes and LS
                        laneFlow = self.VPHFlowDirections[0] // (len(self.lanes['L']) + 1)  # divides the vehicles by the number of left turning lanes (without remainders)
                        remainder = self.VPHFlowDirections[0] % (len(self.lanes['L']) + 1)  # finds the remainder of this division between the lanes
                
                        firstIteration = True  # initialises a first iteration check variable
                        lanes = self.lanes['L']  # gets all of the lanes for the left direction
                        for lane in lanes:  # iterates over the lanes
                            if (firstIteration):  # checks if this is the first iteration
                                lane.updateDirectionFlow((laneFlow + remainder), 0, 'rep')  # updates the left VPH for the lane, with the divided amount plus the remainder of the division
                                firstIteration = False
                            else:
                                lane.updateDirectionFlow(laneFlow, 0, 'rep')  # updates the left VPH for the lane with the divided amount
                
                        self.lanes['LS'][0].updateDirectionFlow(laneFlow, 0, 'rep')

                        maxLeft = max(lane.totalFlow for lane in self.lanes['L'])
                        minLeft = min(lane.totalFlow for lane in self.lanes['L'])

                        #adds all straight traffic to the LS lane
                        self.lanes['LS'][0].updateDirectionFlow(self.VPHFlowDirections[1], 1, 'add')

                        changeMade = True

                        while(changeMade):
                            changeMade = False
                            
                            maxLS, minLeft, changeMade, LCounter = maxLSGTminLeft(maxLS, minLeft, changeMade, LCounter)
                            
                            minLeft, maxLS, changeMade, LCounter = minLeftGTmaxLS(minLeft, maxLS, changeMade, LCounter)

                    #if RS in lanes and RS is not
                    elif(('LS' not in self.lanes) and ('RS' in self.lanes)):
            
                        #distribute the left-turn traffic between the left lane
                        laneFlow = self.VPHFlowDirections[0] // len(self.lanes['L'])  # divides the vehicles by the number of left turning lanes (without remainders)
                        remainder = self.VPHFlowDirections[0] % len(self.lanes['L'])  # finds the remainder of this division between the lanes
                
                        firstIteration = True  # initialises a first iteration check variable
                        lanes = self.lanes['L']  # gets all of the lanes for the left direction
                        for lane in lanes:  # iterates over the lanes
                            if (firstIteration):  # checks if this is the first iteration
                                lane.updateDirectionFlow((laneFlow + remainder), 0, 'rep')  # updates the left VPH for the lane, with the divided amount plus the remainder of the division
                                firstIteration = False
                            else:
                                lane.updateDirectionFlow(laneFlow, 0, 'rep')  # updates the left VPH for the lane with the divided amount

                        maxLeft = max(lane.totalFlow for lane in self.lanes['L'])
                        minLeft = min(lane.totalFlow for lane in self.lanes['L'])

                        # adds all straight traffic to the RS lane
                        self.lanes['RS'][0].updateDirectionFlow(self.VPHFlowDirections[1], 1, 'add')
                        #adds all right traffic to the RS lane
                        self.lanes['RS'][0].updateDirectionFlow(self.VPHFlowDirections[2], 2, 'add')
            

                elif(('L' not in self.lanes) and ('R' in self.lanes)):
                    # if both LS and RS lanes in junction
                    if (('LS' in self.lanes) and ('RS' in self.lanes)):
            
                        #distribute the left-turn traffic between the left lanes and LS
                        laneFlow = self.VPHFlowDirections[2] // (len(self.lanes['R']) + 1)  # divides the vehicles by the number of left turning lanes (without remainders)
                        remainder = self.VPHFlowDirections[2] % (len(self.lanes['R']) + 1)  # finds the remainder of this division between the lanes
                
                        firstIteration = True  # initialises a first iteration check variable
                        lanes = self.lanes['R']  # gets all of the lanes for the left direction
                        for lane in lanes:  # iterates over the lanes
                            if (firstIteration):  # checks if this is the first iteration
                                lane.updateDirectionFlow((laneFlow + remainder), 2, 'rep')  # updates the left VPH for the lane, with the divided amount plus the remainder of the division
                                firstIteration = False
                            else:
                                lane.updateDirectionFlow(laneFlow, 2, 'rep')  # updates the left VPH for the lane with the divided amount
                
                        self.lanes['RS'][0].updateDirectionFlow(laneFlow, 2, 'rep')

                        maxRight = max(lane.totalFlow for lane in self.lanes['R'])
                        minRight = min(lane.totalFlow for lane in self.lanes['R'])
                        

                        #distributes the straight traffic between the RS and LS lanes
                        laneFlow = self.VPHFlowDirections[1] // 2
                        remainder = self.VPHFlowDirections[1] % 2

                        self.lanes['LS'][0].updateDirectionFlow(laneFlow, 1, 'add')
                        self.lanes['RS'][0].updateDirectionFlow(laneFlow + remainder, 1, 'add')

                        maxRS = self.lanes['RS'][0].totalFlow
                        maxLS = self.lanes['LS'][0].totalFlow

                        #adds all left traffic to the LS lane
                        self.lanes['LS'][0].updateDirectionFlow(self.VPHFlowDirections[0], 0, 'add')

                        changeMade = True

                        while(changeMade):
                            changeMade = False

                            maxRS, minRight, changeMade, RCounter = maxRSGTminRight(maxRS, minRight, changeMade, RCounter)
                            
                            maxLS, maxRS, changeMade = maxLSGTmaxRS(maxLS, maxRS, changeMade)
                                
                            maxRS, maxLS, changeMade = maxRSGTmaxLS(maxRS, maxLS, changeMade)
                            
                            minRight, maxRS, changeMade, RCounter = minRightGTmaxRS(minRight, maxRS, changeMade, RCounter)
                            
                    #if LS in lanes and RS is not
                    elif (('LS' in self.lanes) and ('RS' not in self.lanes)):
                        #distribute the right-turn traffic between the right lanes
                        laneFlow = self.VPHFlowDirections[2] // len(self.lanes['R'])  # divides the vehicles by the number of left turning lanes (without remainders)
                        remainder = self.VPHFlowDirections[2] % len(self.lanes['R'])  # finds the remainder of this division between the lanes
                
                        firstIteration = True  # initialises a first iteration check variable
                        lanes = self.lanes['R']  # gets all of the lanes for the left direction
                        for lane in lanes:  # iterates over the lanes
                            if (firstIteration):  # checks if this is the first iteration
                                lane.updateDirectionFlow((laneFlow + remainder), 2, 'rep')  # updates the left VPH for the lane, with the divided amount plus the remainder of the division
                                firstIteration = False
                            else:
                                lane.updateDirectionFlow(laneFlow, 2, 'rep')  # updates the left VPH for the lane with the divided amount

                        maxRight = max(lane.totalFlow for lane in self.lanes['R'])
                        minRight = min(lane.totalFlow for lane in self.lanes['R'])

                        # adds all straight traffic to the LS lane
                        self.lanes['LS'][0].updateDirectionFlow(self.VPHFlowDirections[1], 1, 'add')
                        #adds all left traffic to the LS lane
                        self.lanes['LS'][0].updateDirectionFlow(self.VPHFlowDirections[0], 0, 'add')

                    #if RS in lanes and RS is not
                    elif(('LS' not in self.lanes) and ('RS' in self.lanes)):
                        # adds all straight traffic to the RS lane
                        self.lanes['RS'][0].updateDirectionFlow(self.VPHFlowDirections[1], 1, 'add')
            
                        #distribute the right-turn traffic between the right lanes and RS
                        laneFlow = self.VPHFlowDirections[2] // (len(self.lanes['R']) + 1)  # divides the vehicles by the number of right turning lanes (without remainders)
                        remainder = self.VPHFlowDirections[2] % (len(self.lanes['R']) + 1)  # finds the remainder of this division between the lanes
                
                        firstIteration = True  # initialises a first iteration check variable
                        lanes = self.lanes['R']  # gets all of the lanes for the left direction
                        for lane in lanes:  # iterates over the lanes
                            if (firstIteration):  # checks if this is the first iteration
                                lane.updateDirectionFlow((laneFlow + remainder), 2, 'rep')  # updates the left VPH for the lane, with the divided amount plus the remainder of the division
                                firstIteration = False
                            else:
                                lane.updateDirectionFlow(laneFlow, 2, 'rep')  # updates the left VPH for the lane with the divided amount
                
                        self.lanes['RS'][0].updateDirectionFlow(laneFlow, 2, 'rep')

                        maxRight = max(lane.totalFlow for lane in self.lanes['R'])
                        minRight = min(lane.totalFlow for lane in self.lanes['R'])

                        #adds all straight traffic to the RS lane
                        self.lanes['RS'][0].updateDirectionFlow(self.VPHFlowDirections[1], 1, 'add')

                        changeMade = True

                        while(changeMade):
                            changeMade = False
                            
                            maxRS, minRight, changeMade, RCounter = maxRSGTminRight(maxRS, minRight, changeMade, RCounter)
                            
                            minRight, maxRS, changeMade, RCounter = minRightGTmaxRS(minRight, maxRS, changeMade, RCounter)
            

                elif (('L' not in self.lanes) and ('R' not in self.lanes)):
                    #if LS and RS in lanes
                    if (('LS' in self.lanes) and ('RS' in self.lanes)):
                        
                        #distributes the straight traffic between the RS and LS lanes
                        laneFlow = self.VPHFlowDirections[1] // 2
                        remainder = self.VPHFlowDirections[1] % 2

                        self.lanes['LS'][0].updateDirectionFlow(laneFlow, 1, 'add')
                        self.lanes['RS'][0].updateDirectionFlow(laneFlow + remainder, 1, 'add')

                        # adds all right traffic to the RS lane
                        self.lanes['RS'][0].updateDirectionFlow(self.VPHFlowDirections[2], 2, 'add')
            
                        # adds all left traffic to the LS lane
                        self.lanes['LS'][0].updateDirectionFlow(self.VPHFlowDirections[0], 0, 'add')

                        maxRS = self.lanes['RS'][0].totalFlow
                        maxLS = self.lanes['LS'][0].totalFlow

                        changeMade = True

                        while(changeMade):
                            changeMade = False
                            
                            maxLS, maxRS, changeMade = maxLSGTmaxRS(maxLS, maxRS, changeMade)
                                
                            maxRS, maxLS, changeMade = maxRSGTmaxLS(maxRS, maxLS, changeMade)
            
                    #if LS in lanes and not RS
                    elif (('LS' in self.lanes) and ('RS' not in self.lanes)):
                        # adds all left traffic to the LS lane
                        self.lanes['LS'][0].updateDirectionFlow(self.VPHFlowDirections[0], 0, 'add')
                        # adds all straight traffic to the LS lane
                        self.lanes['LS'][0].updateDirectionFlow(self.VPHFlowDirections[1], 1, 'add')
            
                    #if RS in lanes and not LS
                    elif (('LS' not in self.lanes) and ('RS' in self.lanes)):
                        # adds all right traffic to the RS lane
                        self.lanes['RS'][0].updateDirectionFlow(self.VPHFlowDirections[2], 2, 'add')
                        # adds all straight traffic to the RS lane
                        self.lanes['RS'][0].updateDirectionFlow(self.VPHFlowDirections[1], 1, 'add')

        #------------------------------------------#
        #dividing the flow of cycle or bus lanes
        if 'CB' in self.lanes: #checks whether there is a cycle or bus lane
            self.lanes['CB'][0].updateDirectionFlow(self.VPHFlowDirections[3], 1, 'rep') #sets the CB lane to have the CB direction flow

        # LR, LRS and S are exclusive from each other and so can't exist at the same time, therefore we consider the scenarios where each one exists and where none exist
        if 'LR' in self.lanes:  # when there is an LR lane
            # LS, RS, S and LRS cannot exist with this lane type
            distributeLRorLRS('LR')

        elif 'LRS' in self.lanes:  # when there is an LRS lane
            # LS, RS, S and LR cannot exist with this lane type
            distributeLRorLRS('LRS')

        elif 'S' in self.lanes:  # when there is an S lane
            # LR and LRS cannot exist with this lane type
            distributeS()

        else:  # when there are no S, LR or LRS lanes
            distributeElse()
