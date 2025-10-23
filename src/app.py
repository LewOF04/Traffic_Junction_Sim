from flask import Flask, render_template, request, redirect, make_response, send_file, Response
import io
from src.db_functions import db_functions
from src.simulation import createSimulation
from src.txt_creation import create_default_output
import os
import src.app
import importlib
from inst import SQL


app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'

global output_dictionary
output_dictionary = {}

global current_efficiency_score 
current_efficiency_score = 0

@app.route('/', methods=["GET", "POST"])
def index():
    """ Funciton to take us to the main or results page
    Args:
        None

    Returns: 
        If it is a GET request, it will return the main page
        If it is a POST request (the form has been submitted), it will run the simulation using the inputted data, store the entered info in the database andreturn the results page 
    """
    if request.method == "GET":
        return render_template("index.html", errors = {})
    else:
#_______________________________________________________________________________________________
        errors = {}

        def validateBusLane(inputs, direction):
          """ Validates bus/cycle lane input for a given direction.

          Ensures that if the bus or the cycle lane checkbox is checked, a valid number of buses/cyclist per hour is provided.
          The number must be a non-negative integer.
    
          Args:
              inputs (dict): Dictionary containing form inputs.
              direction (str): Direction of the bus lane (e.g., "northbound").
    
          Returns:
              dict: A dictionary containing validation errors, if any.
          """
          
          buses_per_hour = inputs.get(f"{direction}_buses_per_hour")

          if inputs.get(f"{direction}_bus_lane") == "true":
            buses_per_hour = inputs.get(f"{direction}_buses_per_hour")

            if not buses_per_hour:
              return {f"{direction}_buses_per_hour" : f"The number of {direction} buses/cyclist per hour is required if bus lane is enabled."}

            try:
              num = int(buses_per_hour)
              if num < 0 :
                return {f"{direction}_buses_per_hour" : f"The number of {direction} buses/cyclist per hour must be a non-negative integer."}
            except ValueError:
              return {f"{direction}_buses_per_hour" : f"The number of {direction} buses/cyclist per hour must be a valid integer." }

          return {}

        def validatePedestrianCrossing(inputs):
          """
          Validates pedestrian crossing input.
    
          Ensures that if the pedestrian crossing checkbox is checked, valid values for crossing requests per hour and crossing duration are provided. These values must be non-negative integers.
    
          Args:
              inputs (dict): Dictionary containing form inputs.
    
          Returns:
              dict: A dictionary containing validation errors, if any.
          """
          errors = {}
          crossingRequestsPH = inputs.get("crossing_requests_PH")
          duration = inputs.get("duration")

          if inputs.get("pedestrian_crossing") == "true":
            if crossingRequestsPH == "":
              errors["crossing_requests"] = "The number of crossing requests per hour is required if pedestrian crossing is enabled."
            else:
              try:
                num = int(crossingRequestsPH)
                if num < 0:
                  errors["crossing_requests"] = "The number of crossing requests must be non-negative"
              except ValueError:
                errors["crossing_requests"] = "The number of crossing requests must be a valid integer."
            
            if duration == "":
              errors["duration"] = "The duration of the crossing requests is required if pedestrian crossing is enabled."
            else:
              try:
                num = int(duration)
                if num < 0:
                  errors["duration"] = "The duration of crossing requests must be non-negative"
              except ValueError:
                  errors["duration"] = "The duration of crossing requests must be a valid integer."

          return errors

        def validatePriority(inputs):
          """
          Validates priority lane input.
    
          Ensures that there are no duplicate priority values assigned.
    
          Args:
              inputs (dict): Dictionary containing form inputs.
    
          Returns:
              dict: A dictionary containing validation errors, if any.
          """
          errors = {}
          priorityValues = [value for value in inputs.values() if value != "-"]
          if len(priorityValues) != len(set(priorityValues)): 
            errors["priority_duplicate"] = "Priorities must be unique for each direction."
          #return errors
          return {}

        def validateFlows(inputs, direction):
          """
          Validates traffic flow input for a given direction.
    
          Ensures that the total exit flow matches the entered vehicles per hour (vph) and all values are non-negative integers.
    
          Args:
              inputs (dict): Dictionary containing form inputs.
              direction (str): Traffic direction (e.g., "northbound").
    
          Returns:
              dict: A dictionary containing validation errors, if any.
          """
          errors = {}
          vph_key = f"{direction}_vph"
          vph = inputs.get(vph_key)

          if not vph :
            errors[vph_key] = f"{direction.capitalize()} vehicles per hour (vph) is required."
          else:
            try:
              vph = int(vph)
              if vph < 0:
                  errors[vph_key] = f"{direction.capitalize()} vehicles per hour (vph) must be a non-negative integer."
            except ValueError:
              errors[vph_key] = f"{direction.capitalize()} vehicles per hour (vph) must be a valid integer."
          
          if direction == "northbound":
            exit_flows = {
              "north_exit": inputs.get("northbound_north_exit"),
              "east_exit": inputs.get("northbound_east_exit"),
              "west_exit": inputs.get("northbound_west_exit")
            }
          elif direction == "eastbound":
            exit_flows = {
              "north_exit": inputs.get("eastbound_north_exit"),
              "east_exit": inputs.get("eastbound_east_exit"),
              "south_exit": inputs.get("eastbound_south_exit")
            }
  
          elif direction == "westbound":
            exit_flows = {
              "west_exit": inputs.get("westbound_west_exit"),
              "north_exit": inputs.get("westbound_north_exit"),
              "south_exit": inputs.get("westbound_south_exit")
            }
          elif direction == "southbound":
            exit_flows = {
              "south_exit": inputs.get("southbound_south_exit"),
              "east_exit": inputs.get("southbound_east_exit"),
              "west_exit": inputs.get("southbound_west_exit")
            } 

          total_exits = 0
          for exit_key, exit_value in exit_flows.items():
            if not exit_value or exit_value == "":
              errors[f"{direction}_{exit_key}"] = f"•{direction.capitalize()} {exit_key.replace('_',' ')} is required."
            else:
              try:
                exit_value = int(exit_value)
                if exit_value < 0:
                  errors[f"{direction}_{exit_key}"] = f"•{direction.capitalize()} {exit_key.replace('_',' ')} must be a non-negative integer." 
                total_exits += exit_value
              except ValueError:
                errors[f"{direction}_{exit_key}"] = f"•{direction.capitalize()} {exit_key.replace('_',' ')} must be a valid integer."
          
          if total_exits != vph:
            errors[f"{direction}_exits"] = f"{direction.capitalize()} exit flow must sum to the total vehicles per hour (vph)."
          return errors

        def validateLaneCombo(laneInputs, busInput, cycle, rightTraffic, leftTraffic, straightTraffic, direction):
          """
          Validates lane configuration for a given direction to ensure logical consistency.

          Parameters:
          laneInputs (dict): A dictionary containing lane selections for the given direction.
          busInput (dict): A dictionary containing bus lane selections.
          cycle (str): Indicates whether a cycle lane is present ("true" if selected, otherwise not).
          rightTraffic (int): Number of vehicles turning right.
          leftTraffic (int): Number of vehicles turning left.
          straightTraffic (int): Number of vehicles going straight.
          direction (str): The traffic direction (e.g., "north", "south", etc.).

          Returns:
          dict: A dictionary containing validation errors, where keys represent invalid lane selections and values provide explanatory error messages.

          Validation Rules:
          - A direction cannot have both a cycle and a bus lane.
          - Selecting a left-right-straight lane prevents choosing any other lane type.
          - Selecting a left-right lane prevents straight traffic or straight lane selections.
          - If there is traffic turning left, right or straight, there must be a corresponding lane.
          - The total number of lanes must match the sum of selected lanes.

          Errors are returned in a dictionary with keys indicating the specific issue and values containing user-friendly error messages.
          """
          errors = {}
          cycleLane = cycle
          typeOfLanes = ["left_lane_count", "right_lane_count", "straight_lane_count", "straight_left_lane", "straight_right_lane", "left_right_straight_lane", "left_right_lane"  ]

          try:
            rightTraffic = int(rightTraffic)
            leftTraffic = int(leftTraffic)
            straightTraffic = int(straightTraffic)
          except (ValueError,TypeError):
            return errors 

          #each direction can have either a cycle or bus lane, not both.
          if cycleLane == "true" and busInput.get(f"{direction}_bus_lane") == "true":
            errors[f"{direction}_cycle_lane"] = "You can't have both a cycle and a bus lane"
          
          #if left/right/straight lane chosen then no other lanes can be chosen
          if laneInputs.get(f"{direction}_left_right_straight_lane") == "true":

            if (#laneInputs.get(f"{direction}_left_right_lane") == "true" or
             #laneInputs.get(f"{direction}_left_lane_count") != "0" or 
             #laneInputs.get(f"{direction}_right_lane_count") != "0" or 
             laneInputs.get(f"{direction}_straight_lane_count") != "0" or 
             laneInputs.get(f"{direction}_straight_left_lane") == "true" or 
             laneInputs.get(f"{direction}_straight_right_lane") == "true") :

              return {f"{direction}_left_right_straight_lane" : "If left-right-straight lane is selected, you may only add additional left or right lanes (safety reasons)."}

          #if left/right lane chosen, cannot have traffic going straight/ or any other way
          if laneInputs.get(f"{direction}_left_right_lane") == "true":
            if (laneInputs.get(f"{direction}_left_right_straight_lane") == "true" or
             laneInputs.get(f"{direction}_straight_lane_count") != "0" or 
             laneInputs.get(f"{direction}_straight_left_lane") == "true" or 
             laneInputs.get(f"{direction}_straight_right_lane") == "true" or straightTraffic > 0) :

              errors[f"{direction}_left_right_lane"] = "If left-right lane is selected, there cannot be traffic going straight and no straight lanes."
          
          if rightTraffic > 0 and laneInputs.get(f"{direction}_left_right_straight_lane") != "true" and laneInputs.get(f"{direction}_left_right_lane") != "true":
            if laneInputs.get(f"{direction}_left_lane_count") == "0" and laneInputs.get(f"{direction}_straight_left_lane") != "true":
              errors[f"{direction}_right_lane"] = "If there is left turning traffic, there must be space for a right turning lane."

          if leftTraffic > 0 and laneInputs.get(f"{direction}_left_right_straight_lane") != "true" and laneInputs.get(f"{direction}_left_right_lane") != "true":
            if laneInputs.get(f"{direction}_right_lane_count") == "0" and laneInputs.get(f"{direction}_straight_right_lane") != "true":
              errors[f"{direction}_left_lane"] = "If there is right turning traffic, there must be space for a left turning lane."

          if straightTraffic > 0 and laneInputs.get(f"{direction}_left_right_straight_lane") != "true" and laneInputs.get(f"{direction}_left_right_lane") != "true":
            if laneInputs.get(f"{direction}_straight_lane_count") == "0" and laneInputs.get(f"{direction}_straight_left_lane") != "true" and laneInputs.get(f"{direction}_straight_right_lane") != "true": 
              errors[f"{direction}_straight_lane"] = "If there is straight traffic, there must be space for a straight lane."
          
          #validates if the total lane count is greater than 1 but less than 5
          sumofLanes = 0
          for lane in typeOfLanes:
            laneValue = laneInputs.get(f"{direction}_{lane}")
            if laneValue not in [None, "-"]:
              try:
                sumofLanes += int(laneValue)
              except ValueError:
                if laneValue == "on":
                  sumofLanes += 1

          # If a bus lane was selected, increment the lane count by 1
          if busInput.get(f"{direction}_bus_lane") == 'true':
            sumofLanes += 1

          # if sumofLanes < 1:
          #   errors[f"{direction}_total_lane_count"] = "There must be at least one lane selected for the direction. "
          if sumofLanes > 5:
            errors[f"{direction}_total_lane_count"] = f"The total lane count must not exceed 5 (currently selected {sumofLanes})."

          return errors
     
        
        # NORTH INPUTS

        # Required Inputs (textboxes)
        northboundFlowInput = {
          "northbound_vph" : request.form.get("northbound_vph"),
          "northbound_north_exit" : request.form.get("northbound_north_exit"),
          "northbound_east_exit" : request.form.get("northbound_east_exit"),
          "northbound_west_exit" : request.form.get("northbound_west_exit")
        }

        #Check input for errors
        northFlowErrors = validateFlows(northboundFlowInput,"northbound")
        errors.update(northFlowErrors)

        #Cycle/Bus lane
        north_cycle_lane = request.form.get("north_cycle_lane")
        busInputsNorth = {
          "north_bus_lane" : request.form.get("north_bus_lane"),
          "north_buses_per_hour" : request.form.get("north_buses_per_hour")
        }

        #Check input for errors
        northBusErrors = validateBusLane(busInputsNorth, "north")
        errors.update(northBusErrors)
 
        northLaneInputs = {
          # CHECKBOXES
          # Will return "true" if user checked the box 
          "north_left_right_lane" : request.form.get("north_left_right_lane"),
          "north_left_right_straight_lane" : request.form.get("north_left_right_straight_lane"),
          "north_straight_right_lane" : request.form.get("north_straight_right_lane"),
          "north_straight_left_lane" : request.form.get("north_straight_left_lane"),

          # DROPDOWNS
          # Will reutrn the number they selected
          "north_left_lane_count" : request.form.get("north_left_lane_count"),
          "north_right_lane_count" : request.form.get("north_right_lane_count"),
          "north_straight_lane_count" : request.form.get("north_straight_lane_count"),
          "north_total_lane_count" : request.form.get("north_lane_count")
        }

        #Check input for errors
        northLaneCombo = validateLaneCombo(northLaneInputs, busInputsNorth, north_cycle_lane, northboundFlowInput.get("northbound_west_exit"), northboundFlowInput.get("northbound_east_exit"), northboundFlowInput.get("northbound_north_exit"), "north")

        errors.update(northLaneCombo)
        
        
#_______________________________________________________________________________________________
        # EAST INPUTS
        # Required Inputs (textboxes)
        eastboundFlowInput = {
          "eastbound_vph" : request.form.get("eastbound_vph"),
          "eastbound_north_exit" : request.form.get("eastbound_north_exit"),
          "eastbound_east_exit" : request.form.get("eastbound_east_exit"),
          "eastbound_south_exit" : request.form.get("eastbound_south_exit")
        }

        #Check input for errors
        eastFlowErrors = validateFlows(eastboundFlowInput,"eastbound")
        errors.update(eastFlowErrors)


        #Cycle/Bus lane
        east_cycle_lane = request.form.get("east_cycle_lane")
        busInputsEast = {
          "east_bus_lane" : request.form.get("east_bus_lane"),
          "east_buses_per_hour" : request.form.get("east_buses_per_hour")
        }

        #Check input for errors
        eastBusErrors = validateBusLane(busInputsEast, "east")
        errors.update(eastBusErrors)
       

        eastLaneInputs = {
          # CHECKBOXES
          # Will return "true" if user checked the box 
          "east_left_right_lane" : request.form.get("east_left_right_lane"),
          "east_left_right_straight_lane" : request.form.get("east_left_right_straight_lane"),
          "east_straight_right_lane" : request.form.get("east_straight_right_lane"),
          "east_straight_left_lane" : request.form.get("east_straight_left_lane"),
          
          # DROPDOWNS
          # Will reutrn the number they selected
          "east_left_lane_count" : request.form.get("east_left_lane_count"),
          "east_right_lane_count" :  request.form.get("east_right_lane_count"),
          "east_straight_lane_count" : request.form.get("east_straight_lane_count"),
          "east_total_lane_count" : request.form.get("east_lane_count")
        }

        #Check input for errors
        eastLaneCombo = validateLaneCombo(eastLaneInputs, busInputsEast, east_cycle_lane, eastboundFlowInput.get("eastbound_north_exit"), eastboundFlowInput.get("eastbound_south_exit"), eastboundFlowInput.get("eastbound_east_exit"), "east")
        errors.update(eastLaneCombo)

        
#_______________________________________________________________________________________________
        # SOUTH INPUTS
        # Required Inputs (textboxes)
        southboundFlowInput = {
          "southbound_vph" : request.form.get("southbound_vph"),
          "southbound_south_exit" : request.form.get("southbound_south_exit"),
          "southbound_east_exit" : request.form.get("southbound_east_exit"),
          "southbound_west_exit" : request.form.get("southbound_west_exit")
        }

        #Check input for errors
        southFlowErrors = validateFlows(southboundFlowInput,"southbound")
        errors.update(southFlowErrors)

        # CHECKBOXES
        # Will return "true" if user checked the box 
        south_cycle_lane = request.form.get("south_cycle_lane")
        busInputsSouth = {
          "south_bus_lane" : request.form.get("south_bus_lane"), "south_buses_per_hour" : request.form.get("south_buses_per_hour")
        }

        #Check input for errors
        southBusErrors = validateBusLane(busInputsSouth, "south")
        errors.update(southBusErrors)

        southLaneInputs = {
          # CHECKBOXES
          # Will return "true" if user checked the box 
          "south_left_right_lane" : request.form.get("south_left_right_lane"),
          "south_left_right_straight_lane" : request.form.get("south_left_right_straight_lane"),"south_straight_right_lane" : request.form.get("south_straight_right_lane"),
          "south_straight_left_lane" : request.form.get("south_straight_left_lane"),

          # DROPDOWNS
          # Will reutrn the number they selected
          "south_left_lane_count" : request.form.get("south_left_lane_count"),
          "south_right_lane_count" : request.form.get("south_right_lane_count"),
          "south_straight_lane_count" : request.form.get("south_straight_lane_count"),
          "south_total_lane_count" : request.form.get("south_lane_count")
        }

        #Check input for errors
        southLaneCombo = validateLaneCombo(southLaneInputs, busInputsSouth, south_cycle_lane, southboundFlowInput.get("southbound_east_exit"), southboundFlowInput.get("southbound_west_exit"), southboundFlowInput.get("southbound_south_exit"), "south")

        errors.update(southLaneCombo)
# _______________________________________________________________________________________________
        # WEST INPUTS
        # Required Inputs (textboxes)
        westboundFlowInput = {
          "westbound_vph" : request.form.get("westbound_vph"),
          "westbound_west_exit" : request.form.get("westbound_west_exit"),
          "westbound_north_exit" :request.form.get("westbound_north_exit"),
          "westbound_south_exit" : request.form.get("westbound_south_exit")
        }

        #Check input for errors
        westFlowErrors = validateFlows(westboundFlowInput,"westbound")
        errors.update(westFlowErrors)

        
        west_cycle_lane = request.form.get("west_cycle_lane")
        busInputsWest = {
          "west_bus_lane" : request.form.get("west_bus_lane"),
          "west_buses_per_hour" : request.form.get("west_buses_per_hour")
        }
        
        #Check input for errors
        westBusErrors = validateBusLane(busInputsWest,"west")
        errors.update(westBusErrors)


        westLaneInputs = {
          # CHECKBOXES
          # Will return "true" if user checked the box 
          "west_left_right_lane" : request.form.get("west_left_right_lane"),
          "west_left_right_straight_lane" : request.form.get("west_left_right_straight_lane"),
          "west_straight_right_lane" : request.form.get("west_straight_right_lane"),
          "west_straight_left_lane" : request.form.get("west_straight_left_lane"),

          # DROPDOWNS
          # Will reutrn the number they selected
          "west_left_lane_count" : request.form.get("west_left_lane_count"),
          "west_right_lane_count" : request.form.get("west_right_lane_count"),
          "west_straight_lane_count" : request.form.get("west_straight_lane_count"),
          "west_total_lane_count" : request.form.get("west_lane_count")
        }

        #Check input for errors
        westLaneCombo = validateLaneCombo(westLaneInputs, busInputsWest, west_cycle_lane, westboundFlowInput.get("westbound_south_exit"), westboundFlowInput.get("westbound_north_exit"), westboundFlowInput.get("westbound_west_exit"), "west")
        errors.update(westLaneCombo)
#_______________________________________________________________________________________________
        # GENERAL VARIABLES

        priorities = {
          "north_priority" : request.form.get("north_priority"),
          "east_priority" : request.form.get("east_priority"),
          "south_priority" : request.form.get("south_priority"),
          "west_priority" : request.form.get("west_priority")
        }

        errors.update(validatePriority(priorities))

        pedestrian_inputs = {
          "pedestrian_crossing" : request.form.get("north_pedestrian_crossing"),
          "duration" : request.form.get("duration"),
          "crossing_requests_PH":  request.form.get("crossing_requests_PH")
        }

        errors.update(validatePedestrianCrossing(pedestrian_inputs))

#_______________________________________________________________________________________________

        if errors:
          return render_template("index.html", errors = errors)

#_______________________________________________________________________________________________
        

        junction_info = {
            # NORTH INPUTS
            "northbound_vph": request.form.get("northbound_vph"),
            "northbound_north_exit": request.form.get("northbound_north_exit"), 
            "northbound_east_exit": request.form.get("northbound_east_exit"),
            "northbound_west_exit": request.form.get("northbound_west_exit"),
            "north_bus_lane": request.form.get("north_bus_lane"),
            "north_cycle_lane": request.form.get("north_bus_lane"),
            "north_left_right_lane": request.form.get("north_left_right_lane"),
            "north_left_right_straight_lane": request.form.get("north_left_right_straight_lane"),
            "north_left_lane_count": request.form.get("north_left_lane_count"),
            "north_right_lane_count": request.form.get("north_right_lane_count"),
            "north_straight_right_lane_count": request.form.get("north_straight_right_lane"),
            "north_straight_left_lane_count": request.form.get("north_straight_left_lane"),
            "north_straight_lane_count": request.form.get("north_straight_lane_count"),
            "north_priority": request.form.get("north_priority"),
            "north_total_lane_count": request.form.get("north_lane_count"),
            "north_buses_per_hour": request.form.get("north_buses_per_hour"),

            # EAST INPUTS
            "eastbound_vph": request.form.get("eastbound_vph"),
            "eastbound_north_exit": request.form.get("eastbound_north_exit"),
            "eastbound_east_exit": request.form.get("eastbound_east_exit"), 
            "eastbound_south_exit": request.form.get("eastbound_south_exit"),
            "east_bus_lane": request.form.get("east_bus_lane"),
            "east_cycle_lane": request.form.get("east_bus_lane"),
            "east_left_right_lane": request.form.get("east_left_right_lane"),
            "east_left_right_straight_lane": request.form.get("east_left_right_straight_lane"),
            "east_left_lane_count": request.form.get("east_left_lane_count"),
            "east_right_lane_count": request.form.get("east_right_lane_count"),
            "east_straight_right_lane_count": request.form.get("east_straight_right_lane"),
            "east_straight_left_lane_count": request.form.get("east_straight_left_lane"),
            "east_straight_lane_count": request.form.get("east_straight_lane_count"),
            "east_priority": request.form.get("east_priority"),
            "east_total_lane_count": request.form.get("east_lane_count"),
            "east_buses_per_hour": request.form.get("east_buses_per_hour"),

            # SOUTH INPUTS
            "southbound_vph": request.form.get("southbound_vph"),
            "southbound_south_exit": request.form.get("southbound_south_exit"),
            "southbound_east_exit": request.form.get("southbound_east_exit"),
            "southbound_west_exit": request.form.get("southbound_west_exit"),
            "south_bus_lane": request.form.get("south_bus_lane"),
            "south_cycle_lane": request.form.get("south_bus_lane"),
            "south_left_right_lane": request.form.get("south_left_right_lane"),
            "south_left_right_straight_lane": request.form.get("south_left_right_straight_lane"),
            "south_left_lane_count": request.form.get("south_left_lane_count"),
            "south_right_lane_count": request.form.get("south_right_lane_count"),
            "south_straight_right_lane_count": request.form.get("south_straight_right_lane"),
            "south_straight_left_lane_count": request.form.get("south_straight_left_lane"),
            "south_straight_lane_count": request.form.get("south_straight_lane_count"),
            "south_priority": request.form.get("south_priority"),
            "south_total_lane_count": request.form.get("south_lane_count"),
            "south_buses_per_hour": request.form.get("south_buses_per_hour"),

            # WEST INPUTS
            "westbound_vph": request.form.get("westbound_vph"),
            "westbound_west_exit": request.form.get("westbound_west_exit"),
            "westbound_north_exit": request.form.get("westbound_north_exit"),
            "westbound_south_exit": request.form.get("westbound_south_exit"),
            "west_bus_lane": request.form.get("west_bus_lane"),
            "west_cycle_lane": request.form.get("west_bus_lane"),
            "west_left_right_lane": request.form.get("west_left_right_lane"),
            "west_left_right_straight_lane": request.form.get("west_left_right_straight_lane"),
            "west_left_lane_count": request.form.get("west_left_lane_count"),
            "west_right_lane_count": request.form.get("west_right_lane_count"),
            "west_straight_right_lane_count": request.form.get("west_straight_right_lane"),
            "west_straight_left_lane_count": request.form.get("west_straight_left_lane"),
            "west_straight_lane_count": request.form.get("west_straight_lane_count"),
            "west_priority": request.form.get("west_priority"),
            "west_total_lane_count": request.form.get("west_lane_count"),
            "west_buses_per_hour": request.form.get("west_buses_per_hour"),

            # GENERAL VARIABLES
            "pedestrian_crossing": request.form.get("north_pedestrian_crossing"),
            "crossing_requests_PH": request.form.get("crossing_requests_PH"),
            "crossing_requests_duration": request.form.get("duration")
        }

        # If there are no errrors
        formatted_dict = db_functions.metaphor(junction_info)

        global output_dictionary
        output_dictionary = createSimulation(formatted_dict)

        current_efficiency_score = round((db_functions.getZScore(output_dictionary["maxWait"], 60, 15) * 2 + db_functions.getZScore(output_dictionary["maxQueue"], 10, 5) * 3 + db_functions.getZScore(output_dictionary["avgWait"], 30, 15) * 6)/11, 2)
        
        #create_table = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, 'inst', 'SQL', 'create_table.sql'))
        #sample_db = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, 'data', 'sample.db'))
        #junction_config = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, 'inst', 'SQL', 'INSERT_junction_config.sql'))
        #insert_east = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, 'inst', 'SQL', 'INSERT_traffic_flow_east.sql'))
        #insert_west = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, 'inst', 'SQL', 'INSERT_traffic_flow_west.sql'))
        #insert_south = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, 'inst', 'SQL', 'INSERT_traffic_flow_south.sql'))
        #insert_north = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, 'inst', 'SQL', 'INSERT_traffic_flow_north.sql'))
        #
        #insert_efficiency_score = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, 'inst', 'SQL', 'INSERT_efficiency_score_table.sql'))
        data_db = os.path.join('data', 'data.db')
        data_folder = os.path.join('data')
        if not os.path.exists(data_folder):
          os.mkdir(data_folder)

        # create_table = os.path.join('inst', 'SQL', 'create_table.sql')
        # junction_config = os.path.join('inst', 'SQL', 'INSERT_junction_config.sql')
        # insert_east = os.path.join('inst', 'SQL', 'INSERT_traffic_flow_east.sql')
        # insert_west = os.path.join('inst', 'SQL', 'INSERT_traffic_flow_west.sql')
        # insert_south = os.path.join('inst', 'SQL', 'INSERT_traffic_flow_south.sql')
        # insert_north = os.path.join('inst', 'SQL', 'INSERT_traffic_flow_north.sql')
        
        # insert_efficiency_score = os.path.join('inst', 'SQL', 'INSERT_efficiency_score_table.sql')

        create_table = 'create_table.sql'
        junction_config = 'INSERT_junction_config.sql'
        insert_east = 'INSERT_traffic_flow_east.sql'
        insert_west = 'INSERT_traffic_flow_west.sql'
        insert_south = 'INSERT_traffic_flow_south.sql'
        insert_north = 'INSERT_traffic_flow_north.sql'

        insert_efficiency_score = 'INSERT_efficiency_score_table.sql'


        db_functions.execute_sql_file_noinject(data_db, create_table)
        con = db_functions.get_conn(data_db)
        db_functions.execute_inject_query(con, junction_config, False, False, db_functions.get_pk(junction_info), junction_info["north_left_right_lane"], junction_info["north_left_right_straight_lane"], junction_info["north_left_lane_count"], junction_info["north_right_lane_count"], junction_info["north_straight_right_lane_count"], junction_info["north_straight_left_lane_count"], junction_info["north_straight_lane_count"], junction_info["north_priority"], junction_info["north_buses_per_hour"], junction_info["east_left_right_lane"], junction_info["east_left_right_straight_lane"], junction_info["east_left_lane_count"], junction_info["east_right_lane_count"], junction_info["east_straight_right_lane_count"], junction_info["east_straight_left_lane_count"], junction_info["east_straight_lane_count"], junction_info["east_priority"], junction_info["east_buses_per_hour"],  junction_info["south_left_right_lane"], junction_info["south_left_right_straight_lane"], junction_info["south_left_lane_count"], junction_info["south_right_lane_count"], junction_info["south_straight_right_lane_count"], junction_info["south_straight_left_lane_count"], junction_info["south_straight_lane_count"], junction_info["south_priority"], junction_info["south_buses_per_hour"], junction_info["west_left_right_lane"], junction_info["west_left_right_straight_lane"], junction_info["west_left_lane_count"], junction_info["west_right_lane_count"], junction_info["west_straight_right_lane_count"], junction_info["west_straight_left_lane_count"], junction_info["west_straight_lane_count"], junction_info["west_priority"], junction_info["west_buses_per_hour"], junction_info["pedestrian_crossing"], junction_info["crossing_requests_PH"], junction_info["crossing_requests_duration"])
        db_functions.close_conn(con)
        con = db_functions.get_conn(data_db)
        db_functions.execute_inject_query(con, insert_east, False, False, db_functions.get_pk(junction_info), junction_info["eastbound_vph"], junction_info["eastbound_north_exit"], junction_info["eastbound_east_exit"], junction_info["eastbound_south_exit"])
        db_functions.close_conn(con)
        con = db_functions.get_conn(data_db)
        db_functions.execute_inject_query(con, insert_north, False, False, db_functions.get_pk(junction_info), junction_info["northbound_vph"], junction_info["northbound_north_exit"], junction_info["northbound_east_exit"], junction_info["northbound_west_exit"])
        db_functions.close_conn(con)
        con = db_functions.get_conn(data_db)
        db_functions.execute_inject_query(con, insert_west, False, False, db_functions.get_pk(junction_info), junction_info["westbound_vph"], junction_info["westbound_west_exit"], junction_info["westbound_north_exit"], junction_info["westbound_south_exit"])
        db_functions.close_conn(con)
        con = db_functions.get_conn(data_db)
        result = db_functions.execute_inject_query(con, insert_south, False, False, db_functions.get_pk(junction_info), junction_info["southbound_vph"], junction_info["southbound_south_exit"], junction_info["southbound_east_exit"], junction_info["southbound_west_exit"])
        db_functions.close_conn(con)
        # If it is already in the DB just update the time it was added to the current time
        if result == "fail":        
           # Set up the file path to the query that we will need to update the time
          time_query = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, 'inst', 'SQL', 'update_time.sql'))
          # Enable connection
          con = db_functions.get_conn(data_db)
          # Execute teh query
          db_functions.execute_inject_query(con, time_query, False, False, db_functions.get_pk(junction_info))
          # Close the connection
          db_functions.close_conn(con)
        con = db_functions.get_conn(data_db)
        db_functions.execute_inject_query(con, insert_efficiency_score, False, False, db_functions.get_pk(junction_info), int(current_efficiency_score))
        db_functions.close_conn(con)

        # select_past_efficiency_scores = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, 'inst', 'SQL', 'retrieve_last_5.sql'))
        # select_past_efficiency_scores = os.path.join('inst', 'SQL', 'retrieve_last_5.sql')
        select_past_efficiency_scores = 'retrieve_last_5.sql'
        con = db_functions.get_conn(data_db)
        cur = db_functions.execute_inject_query(con, select_past_efficiency_scores, False, False)
        past_5_efficiency_scores = []
        for i in cur.fetchall():
          past_5_efficiency_scores.append(i[0])

        db_functions.close_conn(con)

        # select_past_buses = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, 'inst', 'SQL', 'retrieve_last_5_buses.sql'))
        # select_past_buses = os.path.join('inst', 'SQL', 'retrieve_last_5_buses.sql')
        select_past_buses = 'retrieve_last_5_buses.sql'
        con = db_functions.get_conn(data_db)
        cur = db_functions.execute_inject_query(con, select_past_buses, False, False, db_functions.get_pk(junction_info))
        

        bus_lane = False
        for i in cur.fetchall():
          for j in i:
            if j != 0:
              bus_lane = True
        db_functions.close_conn(con)

        # select_crossing = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, 'inst', 'SQL', 'retrieve_all_crossing.sql'))
        # select_crossing = os.path.join('inst', 'SQL', 'retrieve_all_crossing.sql')
        select_crossing = 'retrieve_all_crossing.sql'
        con = db_functions.get_conn(data_db)
        cur = db_functions.execute_inject_query(con, select_crossing, False, False, db_functions.get_pk(junction_info))
        

        pedestrian_crossing = False
        for i in cur.fetchall():
          for j in i:
            if j != 0:
              pedestrian_crossing = True
        db_functions.close_conn(con)

        return render_template("results.html", current_efficiency_score=current_efficiency_score, past_5_efficiency_scores=past_5_efficiency_scores, bus_lane = bus_lane, pedestrian_crossing = pedestrian_crossing, how_far_back = 0)

@app.route('/results', methods=["GET", "POST"])
def results():
    """ Function to take us to the results page
    Args:
        None

    Returns: 
        Returns the results page with the required junction efficiency scores
    """
    # DB People, please get the efficiency scores for the past 5 junctions
    past_5_efficiency_scores = []
    # DB People, please fill the above array with the past 5 efficiency scores. For now, it is hard-coded
    if request.method == "GET":
        current_efficiency_score = 60
        # DB People, please fill the above with the correct efficiency score
        return render_template("results.html", current_efficiency_score=current_efficiency_score, past_5_efficiency_scores=past_5_efficiency_scores)
    else:
        # Get which junction the user wants 
        past_junction = request.form.get("view_junction")

        # Set up DB
        # sample_db = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, 'data', 'sample.db'))
        data_db = os.path.join('data', 'data.db')
        # Set up the file path to the query that we will need to select the past 5 efficiency scores
        # select_past_efficiency_scores = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, 'inst', 'SQL', 'retrieve_last_5.sql'))
        # select_past_efficiency_scores = os.path.join('inst', 'SQL', 'retrieve_last_5.sql')
        select_past_efficiency_scores = 'retrieve_last_5.sql'
        # Open a connection to the DB
        con = db_functions.get_conn(data_db)
        # Execute the query
        cur = db_functions.execute_inject_query(con, select_past_efficiency_scores, False, False)
        # Set the array past_5_efficiency_scores to the output of the query
        past_5_efficiency_scores = []
        for i in cur.fetchall():
          past_5_efficiency_scores.append(i[0])

        # Close connection
        db_functions.close_conn(con)
        # The junction number needed is stored on the last index of the past_junction variable
        current_efficiency_score = past_5_efficiency_scores[int(past_junction[-1]) - 1]

        # Now we will get the Junction ID and store that in past_5_efficiency_id
        past_5_efficiency_id = []
        # Set up the file path to the qeury that we will need to select the past 5 id's
        # select_junction_id = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, 'inst', 'SQL', 'retrieve_last_5_id.sql'))
        # select_junction_id = os.path.join('inst', 'SQL', 'retrieve_last_5_id.sql')
        select_junction_id = 'retrieve_last_5_id.sql'
        # Open the conneciton
        con = db_functions.get_conn(data_db)
        # Run the query
        cur = db_functions.execute_inject_query(con, select_junction_id, False, False)
        past_5_efficiency_id = []
        # Put the results of the query in the array
        for i in cur.fetchall():
          past_5_efficiency_id.append(i[0])
        # Close the connection
        db_functions.close_conn(con)
        # The junction number needed is stored on the last index of the past_junction variable
        junction_id = past_5_efficiency_id[int(past_junction[-1]) - 1]

        # Check if there were any buses by running a query that checks if there is a bus lane in the past junction
        # select_past_buses = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, 'inst', 'SQL', 'retrieve_last_5_buses.sql'))
        # select_past_buses = os.path.join('inst', 'SQL', 'retrieve_last_5_buses.sql')
        select_past_buses =  'retrieve_last_5_buses.sql'
        con = db_functions.get_conn(data_db)
        cur = db_functions.execute_inject_query(con, select_past_buses, False, False, junction_id)
        
        # Check if the junction has a bus lane. If yes, then set bus_lane to true
        bus_lane = False
        for i in cur.fetchall():
          for j in i:
            if j != 0:
              bus_lane = True
        db_functions.close_conn(con)

        # Check if there were any pedestrian crossing by running a query that checks if there is a pedestrian crossing in the past junction
        # select_crossing = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, 'inst', 'SQL', 'retrieve_all_crossing.sql'))
        # select_crossing = os.path.join('inst', 'SQL', 'retrieve_all_crossing.sql')
        select_crossing = 'retrieve_all_crossing.sql'
        con = db_functions.get_conn(data_db)
        cur = db_functions.execute_inject_query(con, select_crossing, False, False, junction_id)
        
        # Check if the junction has a pedestrian crossing lane. If yes, then set pdestrian_crossing to true 
        pedestrian_crossing = False
        for i in cur.fetchall():
          for j in i:
            if j != 0:
              pedestrian_crossing = True
        db_functions.close_conn(con)


        return render_template("results.html", current_efficiency_score=current_efficiency_score, past_5_efficiency_scores=past_5_efficiency_scores, bus_lane = bus_lane, pedestrian_crossing = pedestrian_crossing, how_far_back = int(past_junction[-1]) - 1)


@app.route('/download_report', methods=["GET", "POST"])
def download_report():
    """ Function to download the report
    Args:
        None
    
    Returns:
        Returns the report to be downloaded as a PDF
    """
    if request.method == "POST":
      # Get which junction the user wants a report on
      past_junction = int(request.form.get("how_far_back"))

      # Set up DB
      # sample_db = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, 'data', 'sample.db'))
      data_db = os.path.join('data', 'data.db')
      # Set up the file path to the query that we will need to select the past 5 efficiency scores
      # select_past_efficiency_scores = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, 'inst', 'SQL', 'retrieve_last_5.sql'))
      # select_past_efficiency_scores = os.path.join('inst', 'SQL', 'retrieve_last_5.sql')
      select_past_efficiency_scores = 'retrieve_last_5.sql'
      # Open a connection to the DB
      con = db_functions.get_conn(data_db)
      # Execute the query
      cur = db_functions.execute_inject_query(con, select_past_efficiency_scores, False, False)
      # Set the array past_5_efficiency_scores to the output of the query
      past_5_efficiency_scores = []
      for i in cur.fetchall():
        past_5_efficiency_scores.append(i[0])

      # Close connection
      db_functions.close_conn(con)
      # The junction number needed is stored on the last index of the past_junction variable
      current_efficiency_score = past_5_efficiency_scores[past_junction]

      # Now we will get the Junction ID and store that in past_5_efficiency_id
      past_5_efficiency_id = []
      # Set up the file path to the qeury that we will need to select the past 5 id's
      # select_junction_id = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, 'inst', 'SQL', 'retrieve_last_5_id.sql'))
      # select_junction_id = os.path.join('inst', 'SQL', 'retrieve_last_5_id.sql')
      select_junction_id = 'retrieve_last_5_id.sql'
      # Open the conneciton
      con = db_functions.get_conn(data_db)
      # Run the query
      cur = db_functions.execute_inject_query(con, select_junction_id, False, False)
      past_5_efficiency_id = []
      # Put the results of the query in the array
      for i in cur.fetchall():
        past_5_efficiency_id.append(i[0])
      # Close the connection
      db_functions.close_conn(con)
      # The junction number needed is stored on the last index of the past_junction variable
      junction_id = past_5_efficiency_id[past_junction]


      con = db_functions.get_conn(data_db)
      # Run the query
      cur = db_functions.execute_inject_query(con, "SELECT * FROM junction_config WHERE junction_id = ?", False, False, junction_id)
      
      # Get all junction_config data 
      junction_config = cur.fetchall()[0][1:]
      # Close connection
      db_functions.close_conn(con)


      con = db_functions.get_conn(data_db)
      # Run the query
      cur = db_functions.execute_inject_query(con, "SELECT * FROM traffic_flow_north WHERE junction_id = ?", False, False, junction_id)
      # Get all junction_config data 
      north_config = cur.fetchall()[0][1:]
      # Close connection
      db_functions.close_conn(con)

      con = db_functions.get_conn(data_db)
      # Run the query
      cur = db_functions.execute_inject_query(con, "SELECT * FROM traffic_flow_east WHERE junction_id = ?", False, False, junction_id)
      # Get all junction_config data 
      east_config = cur.fetchall()[0][1:]
      # Close connection
      db_functions.close_conn(con)

      con = db_functions.get_conn(data_db)
      # Run the query
      cur = db_functions.execute_inject_query(con, "SELECT * FROM traffic_flow_south WHERE junction_id = ?", False, False, junction_id)
      # Get all junction_config data 
      south_config = cur.fetchall()[0][1:]
      # Close connection
      db_functions.close_conn(con)

      con = db_functions.get_conn(data_db)
      # Run the query
      cur = db_functions.execute_inject_query(con, "SELECT * FROM traffic_flow_west WHERE junction_id = ?", False, False, junction_id)
      # Get all junction_config data 
      west_config = cur.fetchall()[0][1:]
      # Close connection
      db_functions.close_conn(con)

      if junction_config[8] != 0:
        north_bus_lane = 1

      else:
        north_bus_lane = 0
      if junction_config[17] != 0:
        east_bus_lane = 1

      else:
        east_bus_lane = 0
      if junction_config[26] != 0:
        south_bus_lane = 1

      else:
        south_bus_lane = 0
      if junction_config[35] != 0:
        west_bus_lane = 1
      else:
        west_bus_lane = 0

      north_cycle_lane = 0
      east_cycle_lane = 0
      south_cycle_lane = 0
      west_cycle_lane = 0

      
      junction_info = {
            # NORTH INPUTS
            "northbound_vph": north_config[0],
            "northbound_north_exit": north_config[1], 
            "northbound_east_exit": north_config[2],
            "northbound_west_exit": north_config[3],
            "north_bus_lane" : north_bus_lane,
            "north_cycle_lane" : north_cycle_lane,
            "north_left_right_lane": junction_config[0],
            "north_left_right_straight_lane": junction_config[1],
            "north_left_lane_count": junction_config[2],
            "north_right_lane_count": junction_config[3],
            "north_straight_right_lane_count": junction_config[4],
            "north_straight_left_lane_count": junction_config[5],
            "north_straight_lane_count": junction_config[6],
            "north_priority": junction_config[7],
            "north_buses_per_hour": junction_config[8],

            # EAST INPUTS
            "eastbound_vph": east_config[0],
            "eastbound_north_exit": east_config[1],
            "eastbound_east_exit": east_config[2], 
            "eastbound_south_exit": east_config[3],
            "east_bus_lane" : east_bus_lane,
            "east_cycle_lane" : east_cycle_lane,
            "east_left_right_lane": junction_config[9],
            "east_left_right_straight_lane": junction_config[10],
            "east_left_lane_count": junction_config[11],
            "east_right_lane_count": junction_config[12],
            "east_straight_right_lane_count": junction_config[13],
            "east_straight_left_lane_count": junction_config[14],
            "east_straight_lane_count": junction_config[15],
            "east_priority": junction_config[16],
            "east_buses_per_hour": junction_config[17],

            # SOUTH INPUTS
            "southbound_vph": south_config[0],
            "southbound_south_exit": south_config[1],
            "southbound_east_exit": south_config[2],
            "southbound_west_exit": south_config[3],
            "south_bus_lane" : south_bus_lane,
            "south_cycle_lane" : south_cycle_lane,
            "south_left_right_lane": junction_config[18],
            "south_left_right_straight_lane": junction_config[19],
            "south_left_lane_count": junction_config[20],
            "south_right_lane_count": junction_config[21],
            "south_straight_right_lane_count": junction_config[22],
            "south_straight_left_lane_count": junction_config[23],
            "south_straight_lane_count": junction_config[24],
            "south_priority": junction_config[25],
            "south_buses_per_hour": junction_config[26],

            # WEST INPUTS
            "westbound_vph": west_config[0],
            "westbound_west_exit": west_config[1],
            "westbound_north_exit": west_config[2],
            "westbound_south_exit": west_config[3],
            "west_bus_lane" : west_bus_lane,
            "west_cycle_lane" : west_cycle_lane,
            "west_left_right_lane": junction_config[27],
            "west_left_right_straight_lane": junction_config[28],
            "west_left_lane_count": junction_config[29],
            "west_right_lane_count": junction_config[30],
            "west_straight_right_lane_count": junction_config[31],
            "west_straight_left_lane_count": junction_config[32],
            "west_straight_lane_count": junction_config[33],
            "west_priority": junction_config[34],
            "west_buses_per_hour": junction_config[35],

            # GENERAL VARIABLES
            "pedestrian_crossing": junction_config[36],
            "crossing_requests_PH": junction_config[37],
            "crossing_requests_duration": junction_config[38]
        }
      
      
      
      formatted_dict = db_functions.metaphor(junction_info)


      output = createSimulation(formatted_dict)

      current_efficiency_score = round((db_functions.getZScore(output["maxWait"], 60, 15) * 2 + db_functions.getZScore(output["maxQueue"], 10, 5) * 3 + db_functions.getZScore(output["avgWait"], 30, 15) * 6)/11, 2)

      create_default_output(output, current_efficiency_score)

      # select_past_buses = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, 'inst', 'SQL', 'retrieve_last_5_buses.sql'))
      # select_past_buses = os.path.join('inst', 'SQL', 'retrieve_last_5_buses.sql')
      select_past_buses = 'retrieve_last_5_buses.sql'
      con = db_functions.get_conn(data_db)
      cur = db_functions.execute_inject_query(con, select_past_buses, False, False, junction_id)
      
      # Check if the junction has a bus lane. If yes, then set bus_lane to true
      bus_lane = False
      for i in cur.fetchall():
        for j in i:
          if j != 0:
            bus_lane = True
      db_functions.close_conn(con)

      # Check if there were any pedestrian crossing by running a query that checks if there is a pedestrian crossing in the past junction
      # select_crossing = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, 'inst', 'SQL', 'retrieve_all_crossing.sql'))
      # select_crossing = os.path.join('inst', 'SQL', 'retrieve_all_crossing.sql')
      select_crossing = 'retrieve_all_crossing.sql'
      con = db_functions.get_conn(data_db)
      cur = db_functions.execute_inject_query(con, select_crossing, False, False, junction_id)
      
      # Check if the junction has a pedestrian crossing lane. If yes, then set pdestrian_crossing to true 
      pedestrian_crossing = False
      for i in cur.fetchall():
        for j in i:
          if j != 0:
            pedestrian_crossing = True
      db_functions.close_conn(con)

      return render_template("results.html", current_efficiency_score=current_efficiency_score, past_5_efficiency_scores=past_5_efficiency_scores, bus_lane = bus_lane, pedestrian_crossing = pedestrian_crossing, how_far_back = past_junction)


if __name__ == '__main__':
    app.run(debug=True)