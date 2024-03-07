# -*- coding: utf-8 -*-
#!/usr/bin/env python

import json
import os

class MessageRecord:
    # Format: 'String' : data (integer/floating point)
    def __init__(self):
        self.jsonData = {
            "Original Height" : 90.0,
            "Ground Height" : 0.0,
            "Clamp Length" : 15.0,
            "Pen Height" : 0.0,
            "A4988 CLK" : 1000,
            "A4988 MSx" : 5,
            "Home Angle Offset" : [0.0, 0.0, 0.0],
            "Sensor Pulse Offset" : [0.0, 0.0, 0.0],
            "Point 1" : [0.0, 0.0, 0.0],
            "Point 2" : [0.0, 0.0, 0.0],
            "Point 3" : [0.0, 0.0, 0.0],
            "Point 4" : [0.0, 0.0, 0.0],
            "Plane X-Z" : [0.0, 0.0, 0.0, 0.0],
            "Plane Y-Z" : [0.0, 0.0, 0.0, 0.0],
            "Home point" : [0.0, 200.0, 45.0],
            "Arm State" : [0, 0, 0, 0, 0, 0, 0, 0, 0]      
            #Robot arm configuration status information 
            #The first represents sensor calibration and the second is ground height
            #The third is the length of the clamp, the fourth is the coordinates of the home point, the fifth is the calibration of the home point,
            #The sixth to ninth digits are the point1-point4 calibration flags
        }
        self.fileInit()

    #Find if the target exists in the json
    def findData(self, targetValue):
        if targetValue in self.jsonData:
            return True
        else:
            return False
        
    #Delete a file in a specified path
    def deleteFile(self, filePath):
        try:
            os.remove(filePath)
        except OSError as e:
            print(f"The file '{e}' was not successfully deleted.")
            
    #Local json file initialization
    def fileInit(self):
        if os.path.exists("Parameter.json") is True:
            with open("Parameter.json", "r", encoding='utf-8') as fp:
                data = json.load(fp)
                if len(data) == len(self.jsonData):
                    self.readJsonFile()
                else:
                    self.deleteFile("Parameter.json")
                    self.writeJsonFile()
        else:
            self.writeJsonFile()
    
    #Read the local json file and store it in self.jsonData
    def readJsonFile(self):
        with open("Parameter.json", "r", encoding='utf-8') as fp:
            self.jsonData = json.load(fp)
    
    #Transcode self.jsonData into json format and write it to a local json file
    def writeJsonFile(self):
        with open("Parameter.json", "w", encoding='utf-8') as fp:
            json.dump(self.jsonData, fp, indent=4)
    
    #Reads the message for the specified object
    def readJsonObject(self, objectName):                         
        try:
            return self.jsonData[str(objectName)]
        except:
            print(f"Read the Json: '{objectName}' does not exist." )
    
    #Writes the message for the specified object to the local json
    def writeJsonObject(self, objectName, data):  
        try:
            self.jsonData[str(objectName)] = data
            self.writeJsonFile()
        except:
            print(f"Write the Json: '{objectName}' does not exist." )
    
if __name__ == '__main__':
    c = MessageRecord()
    c.deleteFile("Parameter.json")
   
    c.writeJsonObject("Original Height", 90.0)
    c.writeJsonObject("Ground Height", 0.0)
    c.writeJsonObject("Clamp Length", 15.0)
    c.writeJsonObject("Pen Height" , 0.0)
    c.writeJsonObject("A4988 CLK", 1000)
    c.writeJsonObject("A4988 MSx", 5)
    c.writeJsonObject("Home Angle Offset", [0.0, 0.0, 0.0])
    c.writeJsonObject("Sensor Pulse Offset", [0.0, 0.0, 0.0])
    c.writeJsonObject("Point 1", [0.0, 0.0, 0.0])
    c.writeJsonObject("Point 2", [0.0, 0.0, 0.0])
    c.writeJsonObject("Point 3", [0.0, 0.0, 0.0])
    c.writeJsonObject("Point 4", [0.0, 0.0, 0.0])
    c.writeJsonObject("Plane X-Z", [0.0, 0.0, 0.0, 0.0])
    c.writeJsonObject("Plane Y-Z", [0.0, 0.0, 0.0, 0.0])
    c.writeJsonObject("Home point", [0.0, 200.0, 45.0])
    c.writeJsonObject("Arm State", [0, 0, 0, 0, 0, 0, 0, 0, 0])
    
    print("Original Height:", c.readJsonObject("Original Height"))
    print("Ground Height:", c.readJsonObject("Ground Height"))
    print("Clamp Length:", c.readJsonObject("Clamp Length"))
    print("Pen Height:", c.readJsonObject("Pen Height"))
    print("A4988 CLK:", c.readJsonObject("A4988 CLK"))
    print("A4988 MSx:", c.readJsonObject("A4988 MSx"))
    print("Home Angle Offset:", c.readJsonObject("Home Angle Offset"))
    print("Sensor Pulse Offset:", c.readJsonObject("Sensor Pulse Offset"))
    print("Point 1:", c.readJsonObject("Point 1"))
    print("Point 2:", c.readJsonObject("Point 2"))
    print("Point 3:", c.readJsonObject("Point 3"))
    print("Point 4:", c.readJsonObject("Point 4"))
    print("Plane X-Z:", c.readJsonObject("Plane X-Z"))
    print("Plane Y-Z:", c.readJsonObject("Plane Y-Z"))
    print("Home point:", c.readJsonObject("Home point"))
    print("Arm State:", c.readJsonObject("Arm State"))
