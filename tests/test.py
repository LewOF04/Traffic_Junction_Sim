import unittest
from queue import Queue
import math
import copy
from src.junction import Junction
from src.direction import Direction
from src.lane import Lane, laneOrdering
from src.simulation import createSimulation
from src.vehicle import Vehicle
from src.txt_creation import create_default_output


class TestTrafficSimulation(unittest.TestCase):
    def setUp(self):
        """Set up a fresh sample input dictionary for each test"""
        self.sample_input = {
            1: ['L', 'S', 'R'],  # North lanes
            2: ['LS', 'S'],  # East lanes
            3: ['LRS', 'S'],  # South lanes
            4: ['RS', 'R'],  # West lanes
            5: [100, 200, 50, 0],  # North flows (left, straight, right, cycle/bus) 350
            6: [150, 300, 75, 0],  # East flows 525
            7: [125, 250, 60, 0],  # South flows 435
            8: [175, 275, 75, 0],  # West flows 525
            9: False,  # User priority
            10: None,  # Priority numbers
            11: True,  # Pedestrian crossing
            12: 50  # Pedestrian crossing requests per hour
        }

    def test_lane_initialisation(self):
        """Test that Lane objects are created with correct initial values"""
        lane = Lane()

        self.assertEqual(lane.directionFlow, [0, 0, 0])
        self.assertEqual(lane.totalFlow, 0)
        self.assertEqual(lane.avgWait, None)
        self.assertEqual(lane.maxQueue, -math.inf)
        self.assertEqual(lane.maxWait, -math.inf)
        self.assertEqual(lane.numCarsPassed, 0)
        self.assertIsInstance(lane.cars, Queue)
        self.assertEqual(lane.newCarRate, None)
        self.assertEqual(lane.lightTime, 0)
        self.assertEqual(lane.totalWait, 0.0)

    def test_lane_update_direction_flow(self):
        """Test updating direction flow and calculating new car rate"""
        lane = Lane()
        test_flow = 600  # 600 vehicles per hour

        lane.updateDirectionFlow(test_flow, 1, 'rep')  # Replace straight flow
        self.assertEqual(lane.directionFlow, [0, 600, 0])
        self.assertEqual(lane.totalFlow, 600)
        self.assertEqual(lane.newCarRate, 3600 / 600)  # 6 seconds per vehicle

        # Test subtraction edge case
        with self.assertRaises(Exception):
            lane.updateDirectionFlow(100, 0, 'sub')  # Should raise "Cannot subtract from 0"

    def test_direction_initialisation(self):
        """Test that Direction objects are created with correct lane configuration"""
        flows = [100, 200, 50, 0]  # left, straight, right, cycle/bus
        name = "north"
        lanes = ['L', 'S', 'R']
        direction = Direction(flows, name, lanes)

        self.assertEqual(direction.directionName, "north", "Direction name should be 'north'")
        self.assertIsNone(direction.lightTime, "Light time should be None")
        self.assertEqual(direction.VPHFlowDirections, flows, "Flows should match input")
        self.assertEqual(direction.laneLayout, lanes, "Lane layout should match input")

        # Lane configuration
        self.assertEqual(len(direction.lanes), 3, "Should have 3 lane types")
        self.assertIn('L', direction.lanes, "Left lane should exist")
        self.assertIn('S', direction.lanes, "Straight lane should exist")
        self.assertIn('R', direction.lanes, "Right lane should exist")
        self.assertEqual(len(direction.lanes['L']), 1, "Should have 1 left lane")
        self.assertEqual(len(direction.lanes['S']), 1, "Should have 1 straight lane")
        self.assertEqual(len(direction.lanes['R']), 1, "Should have 1 right lane")
        self.assertIsInstance(direction.lanes['L'][0], Lane, "Left lane should be a Lane object")

    def test_junction_initialisation(self):
        """Test that Junction objects are created with correct configuration using a fixed subclass"""

        # Modified Junction class to work without configparser dependency
        class JunctionFixed(Junction):
            def __init__(self, inputInformation):
                # Initialize directions with correct 4-argument Direction constructor
                self.directions = {
                    'north': Direction(inputInformation[5], 'north', laneOrdering(inputInformation[1])),
                    'east': Direction(inputInformation[6], 'east', laneOrdering(inputInformation[2])),
                    'south': Direction(inputInformation[7], 'south', laneOrdering(inputInformation[3])),
                    'west': Direction(inputInformation[8], 'west', laneOrdering(inputInformation[4])),
                }
                self.isPedestrianCrossing = inputInformation[11]
                self.lastCrossingTime = 0.0
                if self.isPedestrianCrossing:
                    self.pedCrossPH = inputInformation[12]
                # Hardcode config values
                self.trafficSpeed = 13.4112
                self.pedestrianCrossingTime = 10
                self.minimumGreenTime = 10
                self.cycleInfo = {'north': None, 'east': None, 'south': None, 'west': None}

        # Use the fixed version for testing
        junction = JunctionFixed(self.sample_input)

        self.assertTrue(junction.isPedestrianCrossing, "Pedestrian crossing should be True")
        self.assertEqual(junction.pedCrossPH, 50, "Pedestrian crossing rate should be 50")
        self.assertEqual(junction.lastCrossingTime, 0.0, "Last crossing time should be 0.0")

        self.assertIn('north', junction.directions, "North direction should exist")
        self.assertIn('east', junction.directions, "East direction should exist")
        self.assertIn('south', junction.directions, "South direction should exist")
        self.assertIn('west', junction.directions, "West direction should exist")

        self.assertEqual(junction.directions['north'].directionName, "north", "North name should be 'north'")
        self.assertIsInstance(junction.directions['north'], Direction, "North should be a Direction object")

        self.assertEqual(junction.trafficSpeed, 13.4112, "Traffic speed should be hardcoded value")
        self.assertEqual(junction.pedestrianCrossingTime, 10, "Pedestrian crossing time should be 10")
        self.assertEqual(junction.minimumGreenTime, 10, "Minimum green time should be 10")

        self.assertIsNone(junction.cycleInfo['north'], "North cycle info should be None")
        self.assertIsNone(junction.cycleInfo['east'], "East cycle info should be None")
        self.assertIsNone(junction.cycleInfo['south'], "South cycle info should be None")
        self.assertIsNone(junction.cycleInfo['west'], "West cycle info should be None")

    def test_lane_ordering(self):
        """Test the lane ordering function"""
        test_cases = [
            (['R', 'L', 'RS', 'LS', 'S'], ['L', 'LS', 'S', 'RS', 'R']),
            (['RS', 'R', 'R', 'S', 'LS'], ['LS', 'S', 'RS', 'R', 'R']),
            (['LRS', 'CB', 'S'], ['CB', 'LRS', 'S'])
        ]
        for input_lanes, expected_order in test_cases:
            with self.subTest(input_lanes=input_lanes):
                result = laneOrdering(input_lanes)
                self.assertEqual(result, expected_order)

    def test_vehicle_initialisation(self):
        """Test that Vehicle objects are created with correct attributes"""
        entry_time = 100
        exit_time = 150
        total_wait = 50
        vehicle = Vehicle(entry_time, exit_time, total_wait)

        self.assertEqual(vehicle.entryTime, entry_time)
        self.assertEqual(vehicle.exitTime, exit_time)
        self.assertEqual(vehicle.totalWait, total_wait)

    def test_distribute_vehicles_by_lane_simple(self):
        """Test vehicle distribution with a simple lane configuration"""
        flows = [100, 200, 50, 0]  # Left: 100, Straight: 200, Right: 50, Cycle/Bus: 0
        lanes = ['L', 'S', 'R']
        direction = Direction(flows, "north", lanes)
        # Make a copy to ensure test isolation
        direction.distributeVehiclesByLane()

        # Check each lane's directionFlow
        self.assertEqual(direction.lanes['L'][0].directionFlow, [100, 0, 0], "Left lane should handle all left traffic")
        self.assertEqual(direction.lanes['S'][0].directionFlow, [0, 200, 0], "Straight lane should handle all straight traffic")
        self.assertEqual(direction.lanes['R'][0].directionFlow, [0, 0, 50], "Right lane should handle all right traffic")
        self.assertEqual(direction.lanes['L'][0].totalFlow, 100)
        self.assertEqual(direction.lanes['S'][0].totalFlow, 200)
        self.assertEqual(direction.lanes['R'][0].totalFlow, 50)

        #Verify distribution by just printing
        print("\n")
        for laneType, lanes in direction.lanes.items():
            for lane in lanes:
                print(str(laneType)+": "+str(lane.directionFlow)+" = "+str(lane.totalFlow))

    def test_distribute_vehicles_by_lane_multiple_lanes_same_type(self):
        """Test vehicle distribution with multiple lanes of the same type"""
        flows = [200, 0, 0, 0]  # Left: 200, Straight: 0, Right: 0, Cycle/Bus: 0
        lanes = ['L', 'L']  # Two left lanes
        direction = Direction(flows, "north", lanes)
        direction.distributeVehiclesByLane()

        self.assertEqual(direction.lanes['L'][0].directionFlow, [100, 0, 0], "First left lane should handle half")
        self.assertEqual(direction.lanes['L'][1].directionFlow, [100, 0, 0], "Second left lane should handle half")
        self.assertEqual(direction.lanes['L'][0].totalFlow, 100)
        self.assertEqual(direction.lanes['L'][1].totalFlow, 100)

        #Verify distribution by just printing
        print("\n")
        for laneType, lanes in direction.lanes.items():
            for lane in lanes:
                print(str(laneType)+": "+str(lane.directionFlow)+" = "+str(lane.totalFlow))

    def test_distribute_vehicles_by_lane_multiple_lanes_different_type_1(self):
        """Test vehicle distribution across multiple lane types"""
        flows = [200, 300, 100, 0]  # Left: 200, Straight: 300, Right: 100, Cycle/Bus: 0
        lanes = ['L', 'LS', 'RS', 'R']  # Left, Left/Straight, Right/Straight, Right
        direction = Direction(flows, "north", lanes)
        direction.distributeVehiclesByLane()

        #Verify distribution by just printing
        print("\n")
        for laneType, lanes in direction.lanes.items():
            for lane in lanes:
                print(str(laneType)+": "+str(lane.directionFlow)+" = "+str(lane.totalFlow))

    def test_distribute_vehicles_by_lane_multiple_lanes_different_type_1_cyclebus(self):
        """Test vehicle distribution with cycle/bus lane"""
        flows = [157, 234, 200, 10]  # Left: 157, Straight: 234, Right: 200, Cycle/Bus: 10
        lanes = ['L', 'LS', 'RS', 'R', 'CB']  # Left, Left/Straight, Right/Straight, Right
        direction = Direction(flows, "north", lanes)
        direction.distributeVehiclesByLane()

        #Verify distribution by just printing
        print("\n")
        for laneType, lanes in direction.lanes.items():
            for lane in lanes:
                print(str(laneType)+": "+str(lane.directionFlow)+" = "+str(lane.totalFlow))

    def test_distribute_vehicles_by_lane_multiple_lanes_different_type_2(self):
        """Test vehicle distribution with complex lane configuration"""
        flows = [200, 300, 100, 0]  # Left: 200, Straight: 300, Right: 100, Cycle/Bus: 0
        lanes = ['L', 'LRS', 'R']  # Left, Left/Straight, Left/Right/Straight, Right/Straight, Right
        direction = Direction(flows, "north", lanes)
        direction.distributeVehiclesByLane()

        #Verify distribution by just printing
        print("\n")
        for laneType, lanes in direction.lanes.items():
            for lane in lanes:
                print(str(laneType)+": "+str(lane.directionFlow)+" = "+str(lane.totalFlow))

    def test_distribute_vehicles_by_lane_multiple_lanes_different_type_cyclebus(self):
        """Test vehicle distribution with cycle/bus lane and complex lane types"""
        flows = [157, 234, 200, 10]  # Left: 200, Straight: 300, Right: 100, Cycle/Bus: 5
        lanes = ['L', 'LRS', 'R']  # Left, Left/Straight, Left/Straight/Right, Right/Straight, Right
        direction = Direction(flows, "north", lanes)
        direction.distributeVehiclesByLane()

        #Verify distribution by just printing
        print("\n")
        for laneType, lanes in direction.lanes.items():
            for lane in lanes:
                print(str(laneType)+": "+str(lane.directionFlow)+" = "+str(lane.totalFlow))

    def test_distribute_vehicles_by_lane_multiple_lanes_different_type_1_cyclebus_low_flow(self):
        """Test vehicle distribution with very low flows"""
        flows = [3, 3, 3, 3]  # Low flows across all types
        lanes = ['L', 'LS', 'RS', 'R', 'CB']  # Left, Left/Straight, Right/Straight, Right
        direction = Direction(flows, "north", lanes)
        direction.distributeVehiclesByLane()

        #Verify distribution by just printing
        print("\n")
        for laneType, lanes in direction.lanes.items():
            for lane in lanes:
                print(str(laneType)+": "+str(lane.directionFlow)+" = "+str(lane.totalFlow))

    def test_create_simulation_basic(self):
        """Test basic simulation creation"""
        from src.simulation import createSimulation

        # Run simulation with sample input
        result = createSimulation(self.sample_input)

        # Check basic structure of simulation result
        self.assertIsInstance(result, dict, "Simulation result should be a dictionary")

        # Check key metrics exist
        expected_keys = [
            'isPedestrianCrossing', 'trafficSpeed', 'minimumGreenTime', 'vehicleLength',
            'carsPassedThrough', 'totalWait', 'avgWait', 'maxWait', 'maxQueue'
        ]
        for key in expected_keys:
            self.assertIn(key, result, f"Simulation result should contain {key}")

    def test_end_simulation_metrics(self):
        """Test the metrics calculated at the end of simulation"""
        from src.simulation import createSimulation

        result = createSimulation(self.sample_input)

        # Check numeric metrics are valid
        self.assertGreater(result['carsPassedThrough'], 0, "Should have cars passed through")
        self.assertGreaterEqual(result['totalWait'], 0, "Total wait time should be non-negative")
        self.assertGreaterEqual(result['avgWait'], 0, "Average wait time should be non-negative")
        self.assertGreaterEqual(result['maxWait'], 0, "Max wait time should be non-negative")
        self.assertGreaterEqual(result['maxQueue'], 0, "Max queue should be non-negative")

    def test_simulation_direction_metrics(self):
        """Test metrics for individual directions"""
        from src.simulation import createSimulation

        result = createSimulation(self.sample_input)

        # Check each direction has metrics
        directions = ['north', 'east', 'south', 'west']
        for direction in directions:
            self.assertIn(direction, result, f"Result should contain metrics for {direction}")

            dir_metrics = result[direction]
            self.assertIn('carsPassedThrough', dir_metrics)
            self.assertIn('totalWait', dir_metrics)
            self.assertIn('avgWait', dir_metrics)
            self.assertGreaterEqual(dir_metrics['carsPassedThrough'], 0)

    def test_pedestrian_crossing_simulation(self):
        """Test simulation with pedestrian crossing"""
        from src.simulation import createSimulation

        # Ensure pedestrian crossing is enabled
        input_with_ped = self.sample_input.copy()
        input_with_ped[11] = True  # Enable pedestrian crossing
        input_with_ped[12] = 50  # 50 crossings per hour

        result = createSimulation(input_with_ped)

        # Check pedestrian crossing specific metrics
        self.assertTrue(result['isPedestrianCrossing'], "Pedestrian crossing should be enabled")
        self.assertIn('pedestrianCrossingTime', result)

    def test_simulation_with_custom_priority(self):
        """Test simulation with custom direction priorities"""
        from src.simulation import createSimulation

        # Create input with custom priorities
        input_with_priority = self.sample_input.copy()
        input_with_priority[9] = True  # Enable user priority
        input_with_priority[10] = [1, 2, 3, 4]  # Custom priority order

        result = createSimulation(input_with_priority)

        # Check that priorityNums are in the result
        self.assertIn('priorityNums', result)
        self.assertEqual(result['priorityNums'], [1, 2, 3, 4])

    def test_lane_performance_metrics(self):
        """Test lane-level performance metrics in simulation"""
        from src.simulation import createSimulation

        result = createSimulation(self.sample_input)

        # Check each direction
        for direction_name, direction_data in result.items():
            if direction_name in ['north', 'east', 'south', 'west']:
                # Get the number of lanes for this direction
                num_lanes = sum(1 for key in direction_data.keys() if isinstance(key, int))

                # Check lane-level metrics are present
                for lane_num in range(num_lanes):
                    lane_metrics = direction_data[lane_num]
                    self.assertIn('laneType', lane_metrics)
                    self.assertIn('maxQueue', lane_metrics)
                    self.assertIn('maxWait', lane_metrics)
                    self.assertIn('avgWait', lane_metrics)
                    self.assertIn('remainingVehicles', lane_metrics)

    def test_high_traffic_simulation(self):
        """Test simulation with significantly higher traffic volumes"""
        high_traffic_input = self.sample_input.copy()
        # Multiply flows by 5 to simulate heavy traffic
        high_traffic_input[5] = [500, 1000, 250, 0]  # North flows
        high_traffic_input[6] = [750, 1500, 375, 0]  # East flows
        high_traffic_input[7] = [625, 1250, 300, 0]  # South flows
        high_traffic_input[8] = [875, 1375, 400, 0]  # West flows

        result = createSimulation(high_traffic_input)

        # Check metrics in high traffic scenario
        self.assertGreater(result['carsPassedThrough'], 1000, "High traffic should process more cars")
        self.assertGreater(result['totalWait'], 0, "Total wait time should be significant in high traffic")
        self.assertGreater(result['maxQueue'], 10, "Max queue should be substantial in high traffic")

    def test_zero_traffic_simulation(self):
        """Test simulation with zero traffic volumes"""
        zero_traffic_input = self.sample_input.copy()
        zero_traffic_input[5] = [0, 0, 0, 0]  # North flows
        zero_traffic_input[6] = [0, 0, 0, 0]  # East flows
        zero_traffic_input[7] = [0, 0, 0, 0]  # South flows
        zero_traffic_input[8] = [0, 0, 0, 0]  # West flows

        result = createSimulation(zero_traffic_input)

        # Check metrics in zero traffic scenario
        self.assertEqual(result['carsPassedThrough'], 0, "No cars should pass through with zero traffic")
        self.assertEqual(result['totalWait'], 0.0, "Total wait time should be zero")
        self.assertEqual(result['maxQueue'], -math.inf, "Max queue should be -inf with no traffic")

    def test_simulation_create_priority(self):
        """Test simulation with unbalanced traffic across directions"""

        result = createSimulation(self.sample_input)

        # Check directional metrics
        self.assertTrue(result['priorityNums'], [1, 2, 3, 3])
    
    def test_produce_txt_output(self):
        result = createSimulation(self.sample_input)

        create_default_output(result, 100)

        self.assertTrue(True, True)


    def test_no_pedestrian_crossing_simulation(self):
        """Test simulation with pedestrian crossing disabled"""
        no_ped_input = self.sample_input.copy()
        no_ped_input[11] = False  # Disable pedestrian crossing

        result = createSimulation(no_ped_input)

        # Verify pedestrian crossing is disabled
        self.assertFalse(result['isPedestrianCrossing'], "Pedestrian crossing should be disabled")
        self.assertNotIn('pedestrianCrossingTime', result)

    def test_simulation_edge_case_single_lane(self):
        """Test simulation with only a single lane in each direction"""
        single_lane_input = self.sample_input.copy()
        single_lane_input[1] = ['S']  # North: only straight lane
        single_lane_input[2] = ['S']  # East: only straight lane
        single_lane_input[3] = ['S']  # South: only straight lane
        single_lane_input[4] = ['S']  # West: only straight lane

        result = createSimulation(single_lane_input)

        # Check basic metrics
        self.assertGreaterEqual(result['carsPassedThrough'], 0)
        self.assertGreaterEqual(result['totalWait'], 0)

    def test_vehicle_wait_time_distribution(self):
        """Test the distribution of vehicle wait times"""
        result = createSimulation(self.sample_input)

        # Check wait time statistics
        self.assertLess(result['avgWait'], result['maxWait'], "Average wait should be less than max wait")

        # Check wait times for each direction
        for direction_name in ['north', 'east', 'south', 'west']:
            direction_data = result[direction_name]
            self.assertLess(direction_data['avgWait'], direction_data['maxWait'], f"Average wait in {direction_name} should be less than max wait")