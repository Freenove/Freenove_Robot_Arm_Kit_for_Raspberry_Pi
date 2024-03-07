# -*- coding: utf-8 -*-
#!/usr/bin/env python

class MessageParser:
    def __init__(self):
        self.inputCommandArray = []
        self.commandArray = []
        self.stringParameter = []
        self.floatParameter = []
        self.intParameter = []
        self.commandChar = None
        
    def parser(self, msg):
        self.clearParameters()                                          #Clear the command array
        inputStringTemp = msg.strip()                                   #Delete beginning and end Spaces
        self.inputCommandArray = inputStringTemp.split(" ")             #Separate instructions by space and store them in the list
        for i in self.inputCommandArray:                                #Parses the list data and stores it in different lists
            self.commandArray.append(i[0:1])
            self.stringParameter.append(i[1:])
        self.commandChar = self.commandArray[0][0:1]                    #Takes the first byte of the command
        if self.commandChar == "G" or self.commandChar == "S":
            self.floatParameter = [float(x) for x in self.stringParameter]  #Convert all parameters to float type
            self.intParameter = [round(x) for x in self.floatParameter]     #Convert all parameters to int type
        else:
            print("messageParser.py, error command.")
        
    def clearParameters(self):
        self.inputCommandArray.clear()
        self.commandArray.clear()
        self.stringParameter.clear()
        self.floatParameter.clear()
        self.intParameter.clear()
        self.commandChar = None

if __name__ == '__main__':
    msg = MessageParser()
    msg.parser("G1.0 X1.0 Y2.3 Z4.55")
    print(msg.commandArray)
    print(msg.stringParameter)
    print(msg.floatParameter)
    print(msg.intParameter)
    print(msg.commandChar)
    

