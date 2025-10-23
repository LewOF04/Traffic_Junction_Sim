import os
from datetime import datetime
import tkinter as tk
from tkinter import filedialog

def create_default_output(input: dict, junctionScore):
    """Outputs the results as a .txt file.
 
    Description:
        Outputs the result of an sql query in a universally accesible file format (.txt).
 
    Args:
        output_path (str, os.PathLike): The directory where the text file will be saved.
        input (dict): Will attempt to write any input to a string
        junctionScore(float): the score of the junction
 
    """
    file_path = os.path.join(os.path.expanduser("~"), "Downloads") #gets the filepath of the download folder
    
    # Create the file path
    try:
        f = open(os.path.join(file_path, f"{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}_junction_information.txt"), "x")
    except PermissionError as e:
        print(e, "ensure you have access to the folder you are trying to write to!")
 
    # Write to text file
    strVal = "------------------------Junction Information Pack------------------------"
    f.write(" "*(50 - round(len(strVal)/2)) + strVal + "\n")
    
    strVal = "Junction created on "+datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    f.write("\n" + " "*(50 - round(len(strVal)/2)) + strVal + "\n")

    strVal = "Produced with: Traffic Wizard Simulator 3000 (TM)"
    f.write(" "*(50 - round(len(strVal)/2)) + strVal + "\n")
    
    strVal = "============================JUNCTION SCORING============================"
    f.write("\n" + " "*(50 - round(len(strVal)/2)) + "="*len(strVal))
    f.write("\n" + " "*(50 - round(len(strVal)/2)) + strVal)
    f.write("\n" + " "*(50 - round(len(strVal)/2)) + "="*len(strVal) + "\n\n")

    strVal = "Total Junction Score: "+str(junctionScore)+"/100"
    f.write(" "*(50 - round(len(strVal)/2)) + strVal + "\n")

    strVal = "Maximum Queue: "+str(input['maxQueue'])+"  ||  Maximum Wait: "+str(input['maxWait'])+"s  ||  Average Wait: "+str(input['avgWait'])+"s"
    f.write(" "*(50 - round(len(strVal)/2)) + strVal + "\n")
    
    strVal = "Cars processed by junction: "+str(input['carsPassedThrough'])+"  ||  Total wait of all vehicles: "+str(input['totalWait'])+"s"
    f.write(" "*(50 - round(len(strVal)/2)) + strVal + "\n")
    
    strVal = "==========================SIMULATION SETTINGS==========================="
    f.write("\n\n" + " "*(50 - round(len(strVal)/2)) + "="*len(strVal))
    f.write("\n" + " "*(50 - round(len(strVal)/2)) + strVal)
    f.write("\n" + " "*(50 - round(len(strVal)/2)) + "="*len(strVal) + "\n\n")
    
    strVal = "Vehicle Length(m): "+str(input['vehicleLength'])+"m"
    f.write(" "*(50 - round(len(strVal)/2)) + strVal + "\n")
    
    strVal = "Traffic Speed(m/s): "+str(input['trafficSpeed'])+"m/s"
    f.write(" "*(50 - round(len(strVal)/2)) + strVal + "\n")

    strVal = "Minimum Green Light Time(s): "+str(input['minimumGreenTime'])+"s"
    f.write(" "*(50 - round(len(strVal)/2)) + strVal + "\n")

    if(input['isPedestrianCrossing']==True):
        strVal = "Pedestrian Crossing: Yes"
        f.write(" "*(50 - round(len(strVal)/2)) + strVal + "\n")

        strVal = "Crossing Time(s): "+str(input['pedestrianCrossingTime'])+"s"
        f.write(" "*(50 - round(len(strVal)/2)) + strVal + "\n")

        strVal = "Crossings per hour: "+str(input['pedCrossPH'])
        f.write(" "*(50 - round(len(strVal)/2)) + strVal)
        
    else:
        strVal = "Pedestrian Crossing: No"
        f.write(" "*(50 - round(len(strVal)/2)) + strVal)
    
    strVal = "=========================DIRECTION INFORMATION=========================="
    f.write("\n\n\n\n\n\n\n" + " "*(50 - round(len(strVal)/2)) + "="*len(strVal))
    f.write("\n" + " "*(50 - round(len(strVal)/2)) + strVal)
    f.write("\n" + " "*(50 - round(len(strVal)/2)) + "="*len(strVal) + "\n\n\n")
    
    for i in range(1, 5):
        match i:
            case 1:
                arm = input['north']
                strVal = "------------------------------North Junction Arm------------------------------"
                f.write(" "*(50 - round(len(strVal)/2)) + "-"*len(strVal))
                f.write("\n" + " "*(50 - round(len(strVal)/2)) + strVal)
                f.write("\n" + " "*(50 - round(len(strVal)/2)) + "-"*len(strVal) +"\n\n")
            
            case 2:
                arm = input['east']
                strVal = "------------------------------East Junction Arm------------------------------"
                f.write(" "*(50 - round(len(strVal)/2)) + "-"*len(strVal))
                f.write("\n" + " "*(50 - round(len(strVal)/2))+ strVal)
                f.write("\n" + " "*(50 - round(len(strVal)/2)) + "-"*len(strVal) +"\n\n")
            
            case 3:
                arm = input['south']
                strVal = "------------------------------South Junction Arm------------------------------"
                f.write(" "*(50 - round(len(strVal)/2)) + "-"*len(strVal))
                f.write("\n" + " "*(50 - round(len(strVal)/2)) + strVal)
                f.write("\n" + " "*(50 - round(len(strVal)/2)) + "-"*len(strVal) +"\n\n")
            
            case 4:
                arm = input['west']
                strVal = "------------------------------West Junction Arm------------------------------"
                f.write(" "*(50 - round(len(strVal)/2)) + "-"*len(strVal))
                f.write("\n" + " "*(50 - round(len(strVal)/2)) + strVal)
                f.write("\n" + " "*(50 - round(len(strVal)/2)) + "-"*len(strVal) +"\n\n")
        
        priority = input['priorityNums'][i - 1]
    
        strVal = "Direction Scores:"
        f.write(" "*(50 - round(len(strVal)/2)) + strVal +"\n")

        strVal = "Max Wait: "+str(arm['maxWait'])+"s"
        f.write(" "*(50 - round(len(strVal)/2)) + strVal +"\n")

        strVal = "Max Queue: "+str(arm['maxQueue'])
        f.write(" "*(50 - round(len(strVal)/2)) + strVal +"\n")

        strVal = "Average Wait: "+str(arm['avgWait'])+"s"
        f.write(" "*(50 - round(len(strVal)/2)) + strVal +"\n")

        strVal = "Additional Statistics:"
        f.write("\n"+" "*(50 - round(len(strVal)/2)) + strVal +"\n")

        strVal = "Cars processed by arm: "+str(arm['carsPassedThrough'])
        f.write(" "*(50 - round(len(strVal)/2)) + strVal +"\n")

        strVal = "Total wait of all vehicles: "+str(arm['totalWait'])+"s"
        f.write(" "*(50 - round(len(strVal)/2)) + strVal +"\n")

        strVal = "Direction Settings:"
        f.write("\n" + " "*(50 - round(len(strVal)/2)) + strVal +"\n")

        strVal = "Light on time: "+str(arm['lightTime'])+"s"
        f.write(" "*(50 - round(len(strVal)/2)) + strVal +"\n")

        strVal = "Direction Priority: "+str(priority)
        f.write(" "*(50 - round(len(strVal)/2)) + strVal +"\n")

        strVal = "Lane layout: "+str(arm['laneLayout'])
        f.write(" "*(50 - round(len(strVal)/2)) + strVal +"\n")

        strVal = "Total Traffic(VPH): "+str(arm['VPHFlowDirections'][0] + arm['VPHFlowDirections'][1] + arm['VPHFlowDirections'][2])
        f.write(" "*(50 - round(len(strVal)/2)) + strVal +"\n")

        strVal = "Left Traffic(VPH): "+str(arm['VPHFlowDirections'][0])
        f.write(" "*(50 - round(len(strVal)/2)) + strVal +"\n")

        strVal = "Straight Traffic(VPH): "+str(arm['VPHFlowDirections'][1])
        f.write(" "*(50 - round(len(strVal)/2)) + strVal +"\n")

        strVal = "Right Traffic(VPH): "+str(arm['VPHFlowDirections'][2])
        f.write(" "*(50 - round(len(strVal)/2)) + strVal +"\n")
        
        for j in [0,2,4]:
            try:
                lane = arm[j]
                try:
                    lane2 = arm[j+1]

                    strVal = "-----Lane "+str(j+1)+" ("+str(lane['laneType'])+")-----"
                    f.write("\n\n\n" + "-"*len(strVal) + " "*(50 - len(strVal))+ " "*12 + "-"*len("-----Lane "+str(j+2)+" ("+str(lane2['laneType'])+")-----") + "\n")
                    f.write(strVal +" "*(50 - len(strVal))+ "||"+" "*10 + "-----Lane "+str(j+2)+" ("+str(lane2['laneType'])+")-----" + "\n")
                    f.write("-"*len(strVal) + " "*(50 - len(strVal))+ " "*12 + "-"*len("-----Lane "+str(j+2)+" ("+str(lane2['laneType'])+")-----"))

                    strVal = "Lane Scores:"
                    f.write("\n\n"+ strVal +" "*(50 - len(strVal))+ "||"+" "*10 + strVal)

                    strVal = "   Max Queue: "+str(lane['maxQueue'])
                    f.write("\n"+ strVal +" "*(50 - len(strVal))+ "||"+" "*10 + "Max Queue: "+str(lane2['maxQueue']))

                    strVal = "   Max Wait: "+str(lane['maxWait'])+"s"
                    f.write("\n"+ strVal +" "*(50 - len(strVal))+ "||"+" "*10 + "Max Wait: "+str(lane2['maxWait']))

                    strVal = "   Average Wait: "+str(lane['avgWait'])+"s"
                    f.write("\n"+ strVal +" "*(50 - len(strVal))+ "||"+" "*10 + "Average Wait: "+str(lane2['avgWait']))

                    strVal = "Additional Statistics:" 
                    f.write("\n\n"+ strVal +" "*(50 - len(strVal))+ "||"+" "*10 + "Additional Statistics:")

                    strVal = "Vehicles in lane at end of simulation: "+str(lane['remainingVehicles'])
                    f.write("\n"+ strVal +" "*(50 - len(strVal))+ "||"+" "*10 + "Vehicles in lane at end of simulation: "+str(lane2['remainingVehicles']))

                    strVal = "   Cars processed by lane: "+str(lane['carsPassedThrough'])
                    f.write("\n"+ strVal +" "*(50 - len(strVal))+ "||"+" "*10 + "Cars processed by lane: "+str(lane2['carsPassedThrough']))

                    strVal = "   Total wait of all vehicles: "+str(lane['totalWait'])+"s"
                    f.write("\n"+ strVal +" "*(50 - len(strVal))+ "||"+" "*10 + "Total wait of all vehicles: "+str(lane2['totalWait']))

                    strVal = "Lane Settings:"
                    f.write("\n\n"+ strVal +" "*(50 - len(strVal))+"||"+" "*10 + strVal)

                    strVal = "   Total Traffic(VPH): "+str(lane['totalFlow'])
                    f.write("\n"+ strVal +" "*(50 - len(strVal))+ "||"+" "*10 + "   Total Traffic(VPH): "+str(lane2['totalFlow']))

                    strVal = "       Left Traffic(VPH): "+str(lane['directionFlow'][0])
                    f.write("\n"+ strVal +" "*(50 - len(strVal))+ "||"+" "*10 + "       Left Traffic(VPH): "+str(lane2['directionFlow'][0]))

                    strVal = "       Straight Traffic(VPH): "+str(lane['directionFlow'][1])
                    f.write("\n"+ strVal +" "*(50 - len(strVal))+ "||"+" "*10 + "       Straight Traffic(VPH): "+str(lane2['directionFlow'][1]))

                    strVal = "       Right Traffic(VPH): "+str(lane['directionFlow'][2])
                    f.write("\n"+ strVal +" "*(50 - len(strVal))+ "||"+" "*10 + "       Right Traffic(VPH): "+str(lane2['directionFlow'][2]))
                
                except:
                    strVal = "-----Lane "+str(j+1)+" ("+str(lane['laneType'])+")-----"
                    f.write("\n\n\n" + " "*(50 - round(len(strVal)/2)) + "-"*len(strVal))
                    f.write("\n" + " "*(50 - round(len(strVal)/2))+ strVal)
                    f.write("\n" + " "*(50 - round(len(strVal)/2)) + "-"*len(strVal))

                    strVal = "Lane Scores:"
                    f.write("\n\n"+ " "*(50 - round(len(strVal)/2))+ strVal)

                    strVal = "Max Queue: "+str(lane['maxQueue'])
                    f.write("\n"+ " "*(50 - round(len(strVal)/2))+ strVal)

                    strVal = "Max Wait: "+str(lane['maxWait'])+"s"
                    f.write("\n"+ " "*(50 - round(len(strVal)/2))+ strVal)

                    strVal = "Average Wait: "+str(lane['avgWait'])+"s"
                    f.write("\n"+ " "*(50 - round(len(strVal)/2))+ strVal)

                    strVal = "Additional Statistics:" 
                    f.write("\n\n"+ " "*(50 - round(len(strVal)/2))+ strVal)

                    strVal = "Vehicles in lane at end of simulation: "+str(lane['remainingVehicles'])
                    f.write("\n"+ " "*(50 - round(len(strVal)/2))+ strVal)

                    strVal = "Cars processed by lane: "+str(lane['carsPassedThrough'])
                    f.write("\n"+ " "*(50 - round(len(strVal)/2))+ strVal)

                    strVal = "Total wait of all vehicles: "+str(lane['totalWait'])+"s"
                    f.write("\n"+ " "*(50 - round(len(strVal)/2))+ strVal)

                    strVal = "Lane Settings:"
                    f.write("\n\n"+ " "*(50 - round(len(strVal)/2))+ strVal)

                    strVal = "Total Traffic(VPH): "+str(lane['totalFlow'])
                    f.write("\n"+ " "*(50 - round(len(strVal)/2))+ strVal)

                    strVal = "Left Traffic(VPH): "+str(lane['directionFlow'][0])
                    f.write("\n"+ " "*(50 - round(len(strVal)/2))+ strVal)

                    strVal = "Straight Traffic(VPH): "+str(lane['directionFlow'][1])
                    f.write("\n"+ " "*(50 - round(len(strVal)/2))+ strVal)

                    strVal = "Right Traffic(VPH): "+str(lane['directionFlow'][2])
                    f.write("\n"+ " "*(50 - round(len(strVal)/2))+ strVal)
                
            except:                
                break
        
        f.write("\n\n\n\n\n")
