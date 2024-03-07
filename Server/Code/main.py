# -*- coding: utf-8 -*-
#!/usr/bin/env python

import time
import socket
import fcntl
import struct
import messageThread
import messageQueue
import messageParser
import messageRecord
import command
import arm
import buzzer
import servo
import ledPixel

class ArmServer:
    def __init__(self):
        self.robotAction = arm.Arm()                                                                   #It's used to control a robotic arm
        self.robotServo = servo.Servo()                                                                #It's used to control servo
        self.robotLed = ledPixel.LedPixel()                                                            #It's used to control ledpixel
        self.robotBuzzer = buzzer.Buzzer()                                                             #It's used to control buzzer
        self.robotFile = messageRecord.MessageRecord()                                                 #Is used to read and write json data
        self.cmd = command.Command()                                                                   #Communication command
        self.queueParser = messageParser.MessageParser()                                               #Message queue command parsing
        self.queueActionParser = messageParser.MessageParser()                                         #Action command parsing
        self.queueBuzzerParser = messageParser.MessageParser()                                         #Buzzer command parsing
        self.queueLedParser = messageParser.MessageParser()                                            #LedPixel command parsing
        self.queueAction = messageQueue.MessageQueue()                                                 #The message queue is used to store the movement instructions of the robot arm
        self.queueLed = messageQueue.MessageQueue()                                                    #The message queue is used to store the control instructions of the colored lights
        self.queueBuzzer = messageQueue.MessageQueue()                                                 #Message queue, which is used to store buzzer instructions
        self.last_pozition = [0,0,0]
        self.plane_axis_state = [0,0,0,0,0,0]                                                          #It is used to temporarily store the calibration status of the robot arm
        self.calibration_height = 20                                                                   #Raise pen height in place when calibrating                                                          
        self.thread_led_parameter = [0,0,0,0]                                                          #Is used to store the mode and RGB color values of the color lights
        self.threadingReceive = None                                                                   #Receive processing thread
        self.threadingArm = None                                                                       #The thread that controls the movement of the robot arm
        self.threadingLed = None                                                                       #Light thread
        self.threadingBuzzer = None                                                                    #Buzzer thread
        self.threadingActionFeedback = None                                                            #The number of motion feedback commands of the robot arm
        self.threadings_state = 0                                                                      #0-- Run all server threads, 1-- shut down all server threads and restart all server threads, 2-- shut down all server threads and exit the code. 3-- Normal running code.
        self.robotAction.setClampLength(self.robotFile.readJsonObject("Clamp Length"))                 #Set the Y-axis offset of the end point of the manipulator
        self.robotAction.setOriginHeight(self.robotFile.readJsonObject("Original Height"))             #Set the height of the rotating shaft of the mechanical arm from the bottom surface
        self.robotAction.setGroundHeight(self.robotFile.readJsonObject("Ground Height"))               #Set the height between the bottom of the robot arm and the ground
        self.robotAction.setPenHeight(self.robotFile.readJsonObject("Pen Height"))                     #Set the Z-axis offset of the end point of the manipulator (change due to the height of the pen)
        self.robotAction.setMsxMode(self.robotFile.readJsonObject("A4988 MSx"))                        #Set the subdivision of the mechanical arm stepper motor drive module
        self.robotAction.setFrequency(self.robotFile.readJsonObject("A4988 CLK"))                      #Set the stepper motor pulse frequency
        self.robotAction.setArmOffseAngle(self.robotFile.readJsonObject("Home Angle Offset"))          #Set the arm calibration Angle offset
        self.homePoint = self.robotFile.readJsonObject("Home point")                                   #Obtain the coordinate position of the robotic arm's Home point
        self.armState = self.robotFile.readJsonObject("Arm State")
        self.plane_axis_original_1 = [-100, 200, self.last_pozition[2]]                                
        self.plane_axis_original_2 = [100, 200, self.last_pozition[2]]                                
        self.plane_axis_original_3 = [0, 150, self.last_pozition[2]]                                  
        self.plane_axis_original_4 = [0, 250, self.last_pozition[2]]                                 
        self.plane_axis_offset_1 = self.robotFile.readJsonObject("Point 1")                          
        self.plane_axis_offset_2 = self.robotFile.readJsonObject("Point 2")                           
        self.plane_axis_offset_3 = self.robotFile.readJsonObject("Point 3")                      
        self.plane_axis_offset_4 = self.robotFile.readJsonObject("Point 4")                          
        plane_x_z_value = self.robotFile.readJsonObject("Plane X-Z")                                   
        self.robotAction.setPlaneXZ(plane_x_z_value[0], plane_x_z_value[1], plane_x_z_value[2], plane_x_z_value[3])
        plane_y_z_value = self.robotFile.readJsonObject("Plane Y-Z")                                   
        self.robotAction.setPlaneYZ(plane_y_z_value[0], plane_y_z_value[1], plane_y_z_value[2], plane_y_z_value[3])
        self.robotActionCheck = 0                                                                      #It is used to query the command status of the robot arm
        self.threadCheckServer = messageThread.create_thread(self.threadingCheckServer)                #Define a thread to check that the server is properly connected
        self.threadCheckServer.start()                                                                 #Start thread
    #Set the message receiving thread
    def setThreadingReceiveState(self, state):
        try:
            buf_state = self.threadingReceive.is_alive()   
            if state != buf_state:
                if state == True:
                    self.threadingReceive = messageThread.create_thread(self.threadingReceiveInstruction)
                    self.threadingReceive.start()
                elif state == False:
                    messageThread.stop_thread(self.threadingReceive)
        except:
            #print("setThreadingReceiveState error.")
            pass
    #Set the robot arm to move thread
    def setThreadingArmState(self, state):
        try:
            buf_state = self.threadingArm.is_alive()   
            if state != buf_state:
                if state == True:
                    self.threadingArm = messageThread.create_thread(self.threadingRobotAction)
                    self.threadingArm.start()
                elif state == False:
                    messageThread.stop_thread(self.threadingArm)
        except:
            print("setThreadingArmState error.")
    #Set the light thread  
    def setThreadingLedState(self, state):
        try:
            buf_state = self.threadingLed.is_alive()
            if state != buf_state:
                if state == True:
                    self.threadingLed = messageThread.create_thread(self.threadingRobotLed)
                    self.threadingLed.start()
                elif state == False:
                    messageThread.stop_thread(self.threadingLed)
        except:
            print("setThreadingLedState error.")
    #Set the buzzer thread
    def setThreadingBuzzerState(self, state):
        try:
            buf_state = self.threadingBuzzer.is_alive()   
            if state != buf_state:
                if state == True:
                    self.threadingBuzzer = messageThread.create_thread(self.threadingRobotBuzzer)
                    self.threadingBuzzer.start()
                elif state == False:
                    messageThread.stop_thread(self.threadingBuzzer)
        except:
            print("setThreadingBuzzerState error.")
    #Set the feedback thread      
    def setThreadingFeedbackState(self, state):
        try:
            buf_state = self.threadingActionFeedback.is_alive()   
            if state != buf_state:
                if state == True:
                    self.threadingActionFeedback = messageThread.create_thread(self.threadingRobotActionFeedback)
                    self.threadingActionFeedback.start()
                elif state == False:
                    messageThread.stop_thread(self.threadingActionFeedback)
        except:
            print("setThreadingFeedbackState error.")  
    #Buzzer instructions are generated according to the parameters and sent to the message queue
    def setRobotBuzzer(self, frequency, delayms, times):
        cmd = self.cmd.CUSTOM_ACTION + str("2") + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.BUZZER_ACTION + str("0") + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.BUZZER_ACTION + str(frequency) + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.BUZZER_ACTION + str(delayms) + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.BUZZER_ACTION + str(times)
        self.queueBuzzer.put(cmd)
    #Generate light instructions according to the parameters and send them to the message queue
    def setRobotLED(self, mode, r, g, b):
        cmd = self.cmd.CUSTOM_ACTION + str("1") + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.WS2812_MODE + str(mode) + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.WS2812_RED + str(r) + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.WS2812_GREEN + str(g) + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.WS2812_BLUE + str(b)
        self.queueLed.put(cmd)
    #The move instruction is generated according to the parameters and sent to the message queue
    def setRobotAction(self, axis):
        cmd = self.cmd.MOVE_ACTION + str("0") + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.AXIS_X_ACTION + str(axis[0]) + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.AXIS_Y_ACTION + str(axis[1]) + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.AXIS_Z_ACTION + str(axis[2])
        self.queueAction.put(cmd)
    #Get the IP address of the Raspberry PI
    def get_interface_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s',b'wlan0'[:15]))[20:24])
    #socket sending function
    def serverSend(self,data):
        self.connection.send(data.encode('utf-8'))
    #Opening the socket Server
    def turn_on_server(self):
        SOCKET_IP = self.get_interface_ip()                                                            #Get the IP address of the Raspberry PI
        self.server_socket = socket.socket()                                                           #Create a socket object
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT,1)                        #Configuring sockets
        self.server_socket.bind((SOCKET_IP, 5000))                                                     #Bind this socket object to port 5000
        self.server_socket.listen(1)                                                                   #Set the number of listening clients to 1
        print("main.py,", 'Server address: ' + SOCKET_IP)                                              #Print IP
        self.threadingReceive = messageThread.create_thread(self.threadingReceiveInstruction)          #Request a thread and assign a value to a variable
        self.threadingArm = messageThread.create_thread(self.threadingRobotAction)                     #Request a thread and assign a value to a variable程
        self.threadingLed = messageThread.create_thread(self.threadingRobotLed)                        #Request a thread and assign a value to a variable
        self.threadingBuzzer = messageThread.create_thread(self.threadingRobotBuzzer)                  #Request a thread and assign a value to a variable
        self.threadingActionFeedback = messageThread.create_thread(self.threadingRobotActionFeedback)  #Request a thread and assign a value to a variable 
        self.setThreadingReceiveState(True)                                                            #Start thread
        self.setThreadingArmState(True)                                                                #Start thread
        self.setThreadingLedState(True)                                                                #Start thread
        self.setThreadingBuzzerState(True)                                                             #Start thread
    #Disable the socket server
    def turn_off_server(self):
        try:
            self.thread_led_parameter = [0,0,0,0]
            self.setThreadingReceiveState(False)  
            self.setThreadingArmState(False) 
            self.setThreadingBuzzerState(False) 
            self.setThreadingFeedbackState(False)
            self.setThreadingLedState(False) 
            self.connection.close()
        except:
            print("Turn off server failed.")
    #Check the installation and operation status of mechanical arm
    def safetyOperationInspection(self):
        cmd = None
        if self.robotActionCheck == 0:   
            cmd = self.cmd.CUSTOM_ACTION + str("8") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_ENABLE + str("0") + str('\r\n')
            self.serverSend(cmd)
            print("Please enable the motor.")
        elif self.robotActionCheck == 1:   
            cmd = self.cmd.CUSTOM_ACTION + str("10") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_SENSOR_POINT + str("0") + str('\r\n')
            self.serverSend(cmd)
            print("Please calibrate the sensor point.")
        elif self.robotActionCheck == 2:    
            cmd = self.cmd.CUSTOM_ACTION + str("10") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_SENSOR_POINT + str("1") + str('\r\n')
            self.serverSend(cmd)
            print("Please goto the sensor point.")
        elif self.robotActionCheck == 3:   
            cmd = self.cmd.CUSTOM_ACTION + str("3") + self.cmd.DECOLLATOR_CHAR + self.cmd.GROUND_HEIGHT + str("?") + str('\r\n')
            self.serverSend(cmd)
            print("Please set the height of the bottom of the robot arm to the ground.")
        elif self.robotActionCheck == 4:   
            cmd = self.cmd.CUSTOM_ACTION + str("4") + self.cmd.DECOLLATOR_CHAR + self.cmd.CLAMP_LENGTH + str("?") + str('\r\n')
            self.serverSend(cmd)
            print("Please set the length of the clamp.")
        elif self.robotActionCheck == 5:  
            cmd = self.cmd.CUSTOM_ACTION + str("5") + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.AXIS_X_ACTION + str("?") + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.AXIS_Y_ACTION + str("?") + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.AXIS_Z_ACTION + str("?") + str('\r\n')
            self.serverSend(cmd)
            print("Please set the original coordinates of the home point.")
        elif self.robotActionCheck == 6:   
            cmd = self.cmd.CUSTOM_ACTION + str("11") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_CALIBRATION_START + str("?") + str('\r\n')
            self.serverSend(cmd)
            print("Please select the point you want to calibrate first.")
        elif self.robotActionCheck == 7:  
            cmd = self.cmd.CUSTOM_ACTION + str("11") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_CALIBRATION_END + str("0") + str('\r\n')
            self.serverSend(cmd)
            print("Failed to calibrate the home point.")
        elif self.robotActionCheck == 8:   
            cmd = self.cmd.CUSTOM_ACTION + str("11") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_CALIBRATION_END + str("1") + str('\r\n')
            self.serverSend(cmd)
            print("Failed to calibrate the point 1.")
        elif self.robotActionCheck == 9:     
            cmd = self.cmd.CUSTOM_ACTION + str("11") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_CALIBRATION_END + str("2") + str('\r\n')
            self.serverSend(cmd)
            print("Failed to calibrate the point 2.")
        elif self.robotActionCheck == 10:    
            cmd = self.cmd.CUSTOM_ACTION + str("11") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_CALIBRATION_END + str("3") + str('\r\n')
            self.serverSend(cmd)
            print("Failed to calibrate the point 3.")
        elif self.robotActionCheck == 11:   
            cmd = self.cmd.CUSTOM_ACTION + str("11") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_CALIBRATION_END + str("4") + str('\r\n')
            self.serverSend(cmd)
            print("Failed to calibrate the point 4.")
        if self.robotActionCheck == 12:   
            return 1
        elif self.robotActionCheck != 12:
            self.setRobotBuzzer(1000, 100, 1)
            if 6 <= self.robotActionCheck <= 11:
                self.robotActionCheck = 12 
            return 0
    #Message receiving thread
    def threadingReceiveInstruction(self):
        try:
            self.connection, self.client_address = self.server_socket.accept()
            print ("main.py, Client connection successful!")
        except:
            print ("main.py, Client connect failed")
        self.server_socket.close()  
        self.receiveData = None
        try:
            while True:
                try:
                    self.receiveData = self.connection.recv(1024).decode('utf-8')
                except:
                    #如果没办法获取socket缓冲区数据，说明自身socket没开。
                        self.threadings_state = 1
                        print("main.py, The socket was disconnected.")
                        break
                #If there is no data in the buffer, the client is disconnected.
                if self.receiveData == "":
                    self.threadings_state = 1
                #The buffer data is obtained and processed
                else:
                    cmdArray = self.receiveData.split('\r\n')   #Split the command with "\r\n", ['S13 N1', '']
                    print("main.py,", cmdArray)                 #Print the received command
                    if cmdArray[-1] !=" ":                      #If the command does not have a return, the command is invalid
                        cmdArray = cmdArray[:-1]
                        for i in range(len(cmdArray)):
                            try:
                                self.queueParser.parser(cmdArray[i])  #command parsing
                            except:
                                print("main.py,", cmdArray[i])
                                self.queueParser.clearParameters()
                                continue 
                            if self.queueParser.commandArray[0] == self.cmd.MOVE_ACTION:                 #movement command
                                if self.queueParser.intParameter[0] == 0 or self.queueParser.intParameter[0]==1 or self.queueParser.intParameter[0]==4:
                                    result = self.safetyOperationInspection()
                                    if result == 1:
                                        self.queueAction.put(cmdArray[i])
                                else:
                                    print("main.py, G{0} is error.".format(self.queueParser.intParameter[0]))
                            elif self.queueParser.commandArray[0] == self.cmd.CUSTOM_ACTION:             #custom command 
                                if self.queueParser.commandArray[1] == self.cmd.WS2812_MODE:             #Light command S1
                                    self.queueLed.put(cmdArray[i])
                                elif self.queueParser.commandArray[1] == self.cmd.BUZZER_ACTION:         #Buzzer command S2
                                    self.queueBuzzer.put(cmdArray[i])
                                elif self.queueParser.commandArray[1] == self.cmd.GROUND_HEIGHT:         #Set the height from the bottom of the robot arm to the ground S3
                                    self.robotAction.setGroundHeight(self.queueParser.intParameter[1])
                                    self.robotFile.writeJsonObject("Ground Height", self.queueParser.intParameter[1])
                                    self.robotActionCheck = 4
                                    self.armState[1] = 1
                                    self.robotFile.writeJsonObject("Arm State", self.armState)
                                elif self.queueParser.commandArray[1] == self.cmd.CLAMP_LENGTH:          #Set clamp length S4
                                    self.robotAction.setClampLength(self.queueParser.intParameter[1])
                                    self.robotFile.writeJsonObject("Clamp Length", self.queueParser.intParameter[1])
                                    self.robotActionCheck = 5
                                    self.armState[2] = 1
                                    self.robotFile.writeJsonObject("Arm State", self.armState)
                                elif self.queueParser.commandArray[1] == self.cmd.AXIS_X_ACTION:         #Home point command S5
                                    self.homePoint = [self.queueParser.floatParameter[i] for i in range(1,4)]   
                                    self.robotFile.writeJsonObject("Home point", self.homePoint)
                                    cmd = self.cmd.MOVE_ACTION + str("0") + self.cmd.DECOLLATOR_CHAR \
                                        + self.cmd.AXIS_X_ACTION + str(self.homePoint[0]) + self.cmd.DECOLLATOR_CHAR \
                                        + self.cmd.AXIS_Y_ACTION + str(self.homePoint[1]) + self.cmd.DECOLLATOR_CHAR \
                                        + self.cmd.AXIS_Z_ACTION + str(self.homePoint[2])
                                    self.queueAction.put(cmd)
                                    self.robotActionCheck = 12
                                    self.armState[3] = 1
                                    self.robotFile.writeJsonObject("Arm State", self.armState)
                                elif self.queueParser.commandArray[1] == self.cmd.ARM_FREQUENCY:         #Set the pulse frequency S6
                                    self.robotAction.setFrequency(self.queueParser.intParameter[1])
                                    self.robotFile.writeJsonObject("A4988 CLK", self.queueParser.intParameter[1])
                                elif self.queueParser.commandArray[1] == self.cmd.ARM_MSX:               #Set the arm subdivision S7
                                    self.robotAction.writeA4988Clk(self.queueParser.intParameter[1])
                                    self.robotFile.writeJsonObject("A4988 MSx", self.queueParser.intParameter[1])
                                elif self.queueParser.commandArray[1] == self.cmd.ARM_ENABLE:            #Enable/disable motor S8
                                    self.robotAction.setArmEnable(self.queueParser.intParameter[1]) 
                                    if self.queueParser.intParameter[1] == 0:
                                        if self.armState[0] == 0:
                                            self.robotActionCheck = 1    
                                        else:
                                            self.robotActionCheck = 2  
                                    else:
                                        self.robotActionCheck = 0                                          
                                elif self.queueParser.commandArray[1] == self.cmd.ARM_SERVO_INDEX:       #Servo command S9
                                    self.queueAction.put(cmdArray[i])
                                elif self.queueParser.commandArray[1] == self.cmd.ARM_SENSOR_POINT:      #Sensor calibration and return to sensor center point S10
                                    if self.robotActionCheck == 1 or self.robotActionCheck == 2 or self.robotActionCheck == 3 or self.robotActionCheck == 12:
                                        self.queueAction.put(cmdArray[i])   
                                        if self.armState[0] == 1 and self.armState[1] == 1 and self.armState[2] == 1 and self.armState[3] == 1:
                                            self.robotActionCheck = 12
                                        else:
                                            self.robotActionCheck = 3
                                    else:
                                        self.safetyOperationInspection()
                                elif self.queueParser.commandArray[1] == self.cmd.ARM_CALIBRATION_START: #Calibration mode starts S11
                                    self.queueAction.put(cmdArray[i])
                                elif self.queueParser.commandArray[1] == self.cmd.ARM_CALIBRATION_POINT: #Calibration mode process S11
                                    self.queueAction.put(cmdArray[i])
                                elif self.queueParser.commandArray[1] == self.cmd.ARM_CALIBRATION_END:   #Calibration mode ends S11
                                    self.queueAction.put(cmdArray[i])
                                elif self.queueParser.commandArray[1] == self.cmd.ARM_QUERY:             #Received a request from the host computer to send signal S12
                                    if self.queueParser.intParameter[1] == 1:                            #If the parameter is 1, enable feedback thread
                                        self.setThreadingFeedbackState(True)
                                    elif self.queueParser.intParameter[1] == 0:                          #If the instruction is 0, turn off feedback thread
                                        self.setThreadingFeedbackState(False)
                                elif self.queueParser.commandArray[1] == self.cmd.ARM_STOP:              #Stop command S13
                                    self.threadings_state = 2
                                    self.receiveData = ""
                                    self.robotAction.setArmEnable(1)
                            else:                                                                        #Command incomplete
                                print("main.py, The received command was incomplete.")
                            self.queueParser.clearParameters()
                    else:
                        print("main.py, The received data is incomplete.")
        except SystemExit:
            pass
    #The moving action thread
    def threadingRobotAction(self):
        while True:
            if self.queueAction.len() > 0:
                data = self.queueAction.get()
                self.queueActionParser.parser(data)
                #print("threadingRobotAction:", data)
                if self.queueActionParser.commandArray[0] == self.cmd.MOVE_ACTION:        #G-code Command
                    if self.queueActionParser.intParameter[0] == 0 or self.queueActionParser.intParameter[0]==1:        #G0/G1
                        x_index = None
                        y_index = None
                        z_index = None
                        if self.cmd.AXIS_X_ACTION in self.queueActionParser.commandArray:                              
                            x_index = self.queueActionParser.commandArray.index(self.cmd.AXIS_X_ACTION)             
                            self.last_pozition[0] = self.queueActionParser.floatParameter[x_index]                  
                        if self.cmd.AXIS_Y_ACTION in self.queueActionParser.commandArray:                           
                            y_index = self.queueActionParser.commandArray.index(self.cmd.AXIS_Y_ACTION)              
                            self.last_pozition[1] = self.queueActionParser.floatParameter[y_index]                 
                        if self.cmd.AXIS_Z_ACTION in self.queueActionParser.commandArray:                           
                            z_index = self.queueActionParser.commandArray.index(self.cmd.AXIS_Z_ACTION)             
                            self.last_pozition[2] = self.queueActionParser.floatParameter[z_index]                      
                        x = self.last_pozition[0]
                        y = self.last_pozition[1]
                        z = self.last_pozition[2]
                        min_sphere = self.robotAction.is_point_inside_sphere(x,y,z,80)    #The motion range of the plane is limited to the radius of 80mm-270mm
                        max_sphere = self.robotAction.is_point_inside_sphere(x,y,z,270)
                        if (min_sphere == 1 or min_sphere == 2) and (max_sphere==0):    #Inside a large ball with a radius of 270mm and outside a ball with a radius of 80mm
                            #The height limit is between -100 and 200mm
                            #self.last_pozition[2] = self.robotAction.constrain(self.last_pozition[2], -100, 180)
                            #Determine whether it passes through the central cylinder area
                            data, circle_axis_1, circle_axis_2 = self.robotAction.calculate_valid_axis(self.robotAction.last_axis, self.last_pozition, 80)
                            if data[0] == 1:                                                         #Existential intersection
                                if data[1] == 2:                                                     #Two intersecting points are between a line segment formed by a starting point and an ending point
                                    self.robotAction.moveStepMotorToTargetAxis(circle_axis_1)        
                                    self.robotAction.moveStepMotorToTargetAxis(circle_axis_2, 2)        
                                    self.robotAction.moveStepMotorToTargetAxis(self.last_pozition)   
                                elif data[1] == 1:                                                   #There is a point of intersection between the line segments formed by the beginning and the end
                                    self.robotAction.moveStepMotorToTargetAxis(circle_axis_1)        
                                elif data[1] == 0:                                                   #The starting point is on the circle, and the end point is in the circle, which does not meet the conditions of movement
                                    pass
                            elif data[0] == 0:                                                       #Start and end are outside the circle, moving directly
                                self.robotAction.moveStepMotorToTargetAxis(self.last_pozition)      
                        else:
                            print("min_sphere, max_sphere, self.last_pozition: ", min_sphere, max_sphere, self.last_pozition)
                            self.setRobotBuzzer(2000,100,1)     
                    elif self.queueActionParser.intParameter[0]==4:                                                     #G4
                        if self.cmd.DELAY_T_ACTION in self.queueActionParser.commandArray:                             
                            t_index = self.queueActionParser.commandArray.index(self.cmd.DELAY_T_ACTION)             
                            delay_ms = self.queueActionParser.intParameter[t_index]                                     
                            time.sleep(delay_ms/1000.0)                                                                 
                        else:                                                                                        
                            print("main.py, G{0} is error.".format(self.queueActionParser.intParameter[0]))
                    else:
                        self.queueActionParser.clearParameters()
                elif self.queueActionParser.commandArray[0] == self.cmd.CUSTOM_ACTION:    #custom Command
                    if self.queueActionParser.intParameter[0] == 10:      
                        if self.queueActionParser.intParameter[1]==0:                     
                            record_pulse = self.robotAction.setArmToSensorPoint()                      #Adjust the sensor center position and return the pulse offset
                            self.robotFile.writeJsonObject("Sensor Pulse Offset", record_pulse)        #Record the pulse offset to a local file
                            self.armState[0] = 1
                            self.robotFile.writeJsonObject("Arm State", self.armState)
                        elif self.queueActionParser.intParameter[1]==1:     
                            if self.armState[0] == 0:
                                record_pulse = self.robotAction.setArmToSensorPoint()                
                                self.robotFile.writeJsonObject("Sensor Pulse Offset", record_pulse)   
                                self.armState[0] = 1
                                self.robotFile.writeJsonObject("Arm State", self.armState)
                            else:
                                pulse_count = self.robotFile.readJsonObject("Sensor Pulse Offset")     #Read the pulse offset of the local file
                                self.robotAction.setArmToSensorPointNoAdjust(pulse_count)              #Return to sensor center position
                        self.setRobotBuzzer(2000,100,1)                                                #Buzzer tone
                    elif self.queueActionParser.intParameter[0] == 11:
                        if self.queueActionParser.commandArray[1] == self.cmd.ARM_CALIBRATION_START:
                            if self.queueActionParser.intParameter[1] == 0:
                                self.robotAction.setArmOffseAngle([0,0,0])                                                                #Set the pulse offset of the sensor center to 0
                                self.original_axis_position = self.homePoint.copy()                                                       #Gets the Home point coordinates
                                self.adjust_axis_position = self.original_axis_position.copy()                                            #The offset coordinates match the original coordinates
                                self.original_adjust_point_angle = self.robotAction.coordinateToAngle(self.original_axis_position)        #Convert coordinates to angular values
                                self.setRobotAction(self.original_axis_position)                                                          #Generate a move command based on the parameters
                                self.setRobotBuzzer(2000,100,1)                                                                           #Generate a buzzer command based on the parameters
                                self.robotActionCheck = 7
                            elif self.queueActionParser.intParameter[1] == 1:
                                self.robotAction.setPlaneXZ(0,0,0,0)
                                last_pozition = self.last_pozition.copy()                                                    #Obtain the current coordinate position of the robot arm
                                last_pozition[2] = last_pozition[2] + self.calibration_height                                #Move up a short distance
                                self.setRobotAction(last_pozition)                           
                                self.plane_axis_original_1 = [-100, 200, self.homePoint[2]]                                  #Obtain the original coordinate data of point 1    
                                self.plane_axis_original_1[2] = self.plane_axis_original_1[2] + self.calibration_height      #Move above point 1
                                self.setRobotAction(self.plane_axis_original_1)                                   
                                self.plane_axis_original_1[2] = self.plane_axis_original_1[2] - self.calibration_height      #Move to point 1
                                self.setRobotAction(self.plane_axis_original_1) 
                                self.last_pozition = self.plane_axis_original_1.copy()
                                self.setRobotBuzzer(2000, 100, 1)                                                                   
                                self.robotActionCheck = 8
                            elif self.queueActionParser.intParameter[1] == 2:
                                self.robotAction.setPlaneXZ(0,0,0,0)
                                last_pozition = self.last_pozition.copy()                                                    
                                last_pozition[2] = last_pozition[2] + self.calibration_height                               
                                self.setRobotAction(last_pozition)                           
                                self.plane_axis_original_2 = [100, 200, self.homePoint[2]]                                  
                                self.plane_axis_original_2[2] = self.plane_axis_original_2[2] + self.calibration_height
                                self.setRobotAction(self.plane_axis_original_2) 
                                self.plane_axis_original_2[2] = self.plane_axis_original_2[2] - self.calibration_height
                                self.setRobotAction(self.plane_axis_original_2) 
                                self.last_pozition = self.plane_axis_original_2.copy()
                                self.setRobotBuzzer(2000, 100, 1)
                                self.robotActionCheck = 9
                            elif self.queueActionParser.intParameter[1] == 3:
                                self.robotAction.setPlaneYZ(0,0,0,0)
                                last_pozition = self.last_pozition.copy()                                                  
                                last_pozition[2] = last_pozition[2] + self.calibration_height                              
                                self.setRobotAction(last_pozition)                           
                                self.plane_axis_original_3 = [0, 150, self.homePoint[2]]                                     
                                self.plane_axis_original_3[2] = self.plane_axis_original_3[2] + self.calibration_height
                                self.setRobotAction(self.plane_axis_original_3) 
                                self.plane_axis_original_3[2] = self.plane_axis_original_3[2] - self.calibration_height
                                self.setRobotAction(self.plane_axis_original_3) 
                                self.last_pozition = self.plane_axis_original_3.copy()
                                self.setRobotBuzzer(2000, 100, 1)
                                self.robotActionCheck = 10
                            elif self.queueActionParser.intParameter[1] == 4:
                                self.robotAction.setPlaneYZ(0,0,0,0)
                                last_pozition = self.last_pozition.copy()                                            
                                last_pozition[2] = last_pozition[2] + self.calibration_height                               
                                self.setRobotAction(last_pozition)                           
                                self.plane_axis_original_4 = [0, 250, self.homePoint[2]]                                     
                                self.plane_axis_original_4[2] = self.plane_axis_original_4[2] + self.calibration_height
                                self.setRobotAction(self.plane_axis_original_4) 
                                self.plane_axis_original_4[2] = self.plane_axis_original_4[2] - self.calibration_height
                                self.setRobotAction(self.plane_axis_original_4) 
                                self.last_pozition = self.plane_axis_original_4.copy()
                                self.setRobotBuzzer(2000, 100, 1)
                                self.robotActionCheck = 11
                            elif self.queueActionParser.intParameter[1] == -1:
                                self.robotActionCheck = 6 
                                self.safetyOperationInspection()
                        elif self.queueActionParser.commandArray[1] == self.cmd.ARM_CALIBRATION_POINT:
                            if self.queueActionParser.intParameter[1] == 0 and self.robotActionCheck == 7:
                                self.adjust_axis_position = [self.queueActionParser.floatParameter[i] for i in range(2,5)]  #Get the coordinates of the calibration point
                                self.setRobotAction(self.adjust_axis_position)                                              #Control the robot arm to move to the target position
                            elif self.queueActionParser.intParameter[1] == 1 and self.robotActionCheck == 8:
                                self.plane_axis_offset_1 = [self.queueActionParser.floatParameter[i] for i in range(2,5)]   #Get the coordinates of the calibration point
                                self.setRobotAction(self.plane_axis_offset_1)                                               #Control the robot arm to move to the target position
                                self.last_pozition = self.plane_axis_offset_1.copy()                                        #Store this location
                            elif self.queueActionParser.intParameter[1] == 2 and self.robotActionCheck == 9:
                                self.plane_axis_offset_2 = [self.queueActionParser.floatParameter[i] for i in range(2,5)]   
                                self.setRobotAction(self.plane_axis_offset_2)                      
                                self.last_pozition = self.plane_axis_offset_2.copy()                                   
                            elif self.queueActionParser.intParameter[1] == 3 and self.robotActionCheck == 10:
                                self.plane_axis_offset_3 = [self.queueActionParser.floatParameter[i] for i in range(2,5)] 
                                self.setRobotAction(self.plane_axis_offset_3)                     
                                self.last_pozition = self.plane_axis_offset_3.copy()                                   
                            elif self.queueActionParser.intParameter[1] == 4 and self.robotActionCheck == 11:
                                self.plane_axis_offset_4 = [self.queueActionParser.floatParameter[i] for i in range(2,5)] 
                                self.setRobotAction(self.plane_axis_offset_4)                    
                                self.last_pozition = self.plane_axis_offset_4.copy()                                    
                            elif self.queueActionParser.intParameter[1] == -1:
                                self.robotActionCheck = 6 
                                self.safetyOperationInspection()
                        elif self.queueActionParser.commandArray[1] == self.cmd.ARM_CALIBRATION_END:
                            if self.queueActionParser.intParameter[1] == 0 and self.robotActionCheck == 7:
                                self.adjust_axis_position = [self.queueActionParser.floatParameter[i] for i in range(2,5)]                #Get the coordinates of the calibration point
                                self.after_adjust_point_angle = self.robotAction.coordinateToAngle(self.adjust_axis_position)             #Convert coordinates to angular values
                                offset_angle = [self.after_adjust_point_angle[i] - self.original_adjust_point_angle[i] for i in range(3)] #Calculate the calibration offset Angle difference
                                self.robotAction.setArmOffseAngle(offset_angle)                                                           #The set Angle offset takes effect
                                self.robotFile.writeJsonObject("Home Angle Offset", offset_angle)                                         #Record the angular offset value to a local file
                                axis = self.homePoint.copy()                                                                              #Gets the original coordinates of the home point
                                axis[2] = axis[2] + self.calibration_height                                                               #Z-axis plus some height
                                self.setRobotAction(axis)                                                                                 #Move above the home point
                                axis = self.homePoint.copy()                                                                              #Gets the original coordinates of the home point
                                self.setRobotAction(axis)                                                                                 #Move to target position
                                self.setRobotBuzzer(2000,100,3)                                                                           #Buzzer tone
                                self.robotActionCheck = 12
                                self.armState[4] = 1
                                self.robotFile.writeJsonObject("Arm State", self.armState)
                            elif self.queueActionParser.intParameter[1] == 1 and self.robotActionCheck == 8:
                                self.plane_axis_offset_1 = [self.queueActionParser.floatParameter[i] for i in range(2,5)] #Get the coordinates of the calibration point
                                self.robotFile.writeJsonObject("Point 1", self.plane_axis_offset_1)                       #Record Point1 to a local file
                                self.robotActionCheck = 12
                                self.armState[5] = 1
                                self.robotFile.writeJsonObject("Arm State", self.armState)
                                if self.armState[5] == 1 and self.armState[6] == 1:
                                    plane_x_z_value = [0, 0, 0, 0]
                                    plane_x_z_value[0] = self.plane_axis_original_1[0]
                                    plane_x_z_value[1] = self.plane_axis_original_2[0]
                                    plane_x_z_value[2] = self.plane_axis_offset_1[2] - self.plane_axis_original_1[2]
                                    plane_x_z_value[3] = self.plane_axis_offset_2[2] - self.plane_axis_original_2[2]
                                    self.robotFile.writeJsonObject("Plane X-Z", plane_x_z_value)                          
                                    self.robotAction.setPlaneXZ(plane_x_z_value[0], plane_x_z_value[1], plane_x_z_value[2], plane_x_z_value[3])  
                                last_pozition = self.last_pozition.copy()                                                
                                last_pozition[2] = last_pozition[2] + self.calibration_height
                                self.setRobotAction(last_pozition) 
                                axis = self.homePoint.copy()                                                             
                                axis[2] = axis[2] + self.calibration_height
                                self.setRobotAction(axis)  
                                axis[2] = axis[2] - self.calibration_height                                              
                                self.setRobotAction(axis)  
                                self.last_pozition = axis.copy()
                                self.setRobotBuzzer(2000,100,3)
                            elif self.queueActionParser.intParameter[1] == 2 and self.robotActionCheck == 9:
                                self.plane_axis_offset_2 = [self.queueActionParser.floatParameter[i] for i in range(2,5)]
                                self.robotFile.writeJsonObject("Point 2", self.plane_axis_offset_2)                      
                                self.robotActionCheck = 12
                                self.armState[6] = 1
                                self.robotFile.writeJsonObject("Arm State", self.armState)
                                if self.armState[5] == 1 and self.armState[6] == 1:
                                    plane_x_z_value = [0, 0, 0, 0]
                                    plane_x_z_value[0] = self.plane_axis_original_1[0]
                                    plane_x_z_value[1] = self.plane_axis_original_2[0]
                                    plane_x_z_value[2] = self.plane_axis_offset_1[2] - self.plane_axis_original_1[2]
                                    plane_x_z_value[3] = self.plane_axis_offset_2[2] - self.plane_axis_original_2[2]
                                    self.robotFile.writeJsonObject("Plane X-Z", plane_x_z_value)                          
                                    self.robotAction.setPlaneXZ(plane_x_z_value[0], plane_x_z_value[1], plane_x_z_value[2], plane_x_z_value[3])
                                last_pozition = self.last_pozition.copy()                                               
                                last_pozition[2] = last_pozition[2] + self.calibration_height
                                self.setRobotAction(last_pozition) 
                                axis = self.homePoint.copy()                                                           
                                axis[2] = axis[2] + self.calibration_height
                                self.setRobotAction(axis)  
                                axis[2] = axis[2] - self.calibration_height                                             
                                self.setRobotAction(axis)  
                                self.last_pozition = axis.copy()
                                self.setRobotBuzzer(2000,100,3)
                            elif self.queueActionParser.intParameter[1] == 3 and self.robotActionCheck == 10:
                                self.plane_axis_offset_3 = [self.queueActionParser.floatParameter[i] for i in range(2,5)] 
                                self.robotFile.writeJsonObject("Point 3", self.plane_axis_offset_3)                      
                                self.robotActionCheck = 12
                                self.armState[7] = 1
                                self.robotFile.writeJsonObject("Arm State", self.armState)
                                if self.armState[7] == 1 and self.armState[8] == 1:
                                    plane_y_z_value = [0, 0, 0, 0]
                                    plane_y_z_value[0] = self.plane_axis_original_3[1]
                                    plane_y_z_value[1] = self.plane_axis_original_4[1]
                                    plane_y_z_value[2] = self.plane_axis_offset_3[2] - self.plane_axis_original_3[2]
                                    plane_y_z_value[3] = self.plane_axis_offset_4[2] - self.plane_axis_original_4[2]
                                    self.robotFile.writeJsonObject("Plane Y-Z", plane_y_z_value)                          
                                    self.robotAction.setPlaneYZ(plane_y_z_value[0], plane_y_z_value[1], plane_y_z_value[2], plane_y_z_value[3])
                                last_pozition = self.last_pozition.copy()                                                 
                                last_pozition[2] = last_pozition[2] + self.calibration_height
                                self.setRobotAction(last_pozition) 
                                axis = self.homePoint.copy()                                                              
                                axis[2] = axis[2] + self.calibration_height
                                self.setRobotAction(axis)  
                                axis[2] = axis[2] - self.calibration_height                                              
                                self.setRobotAction(axis)  
                                self.last_pozition = axis.copy()
                                self.setRobotBuzzer(2000,100,3)
                            elif self.queueActionParser.intParameter[1] == 4 and self.robotActionCheck == 11:
                                self.plane_axis_offset_4 = [self.queueActionParser.floatParameter[i] for i in range(2,5)] 
                                self.robotFile.writeJsonObject("Point 4", self.plane_axis_offset_4)                      
                                self.robotActionCheck = 12
                                self.armState[8] = 1
                                self.robotFile.writeJsonObject("Arm State", self.armState)
                                if self.armState[7] == 1 and self.armState[8] == 1:
                                    plane_y_z_value = [0, 0, 0, 0]
                                    plane_y_z_value[0] = self.plane_axis_original_3[1]
                                    plane_y_z_value[1] = self.plane_axis_original_4[1]
                                    plane_y_z_value[2] = self.plane_axis_offset_3[2] - self.plane_axis_original_3[2]
                                    plane_y_z_value[3] = self.plane_axis_offset_4[2] - self.plane_axis_original_4[2]
                                    self.robotFile.writeJsonObject("Plane Y-Z", plane_y_z_value)                        
                                    self.robotAction.setPlaneYZ(plane_y_z_value[0], plane_y_z_value[1], plane_y_z_value[2], plane_y_z_value[3])
                                last_pozition = self.last_pozition.copy()                                                 
                                last_pozition[2] = last_pozition[2] + self.calibration_height
                                self.setRobotAction(last_pozition) 
                                axis = self.homePoint.copy()                                                              
                                axis[2] = axis[2] + self.calibration_height
                                self.setRobotAction(axis)  
                                axis[2] = axis[2] - self.calibration_height                                              
                                self.setRobotAction(axis)  
                                self.last_pozition = axis.copy()
                                self.setRobotBuzzer(2000,100,3)
                            elif self.queueActionParser.intParameter[1] == -1:
                                self.robotActionCheck = 6 
                                self.safetyOperationInspection() 
                    elif self.queueActionParser.intParameter[0] == 9:
                        index = self.queueActionParser.intParameter[1]
                        original_angle = self.queueActionParser.intParameter[2]
                        range_angle = self.robotAction.constrain(original_angle, 0, 150)
                        offset_angle = self.robotAction.map(range_angle, 0, 150, 15, 165)
                        self.robotServo.setServoAngle(index, offset_angle)
    #Light thread
    def threadingRobotLed(self):
        while True:
            if self.queueLed.len()>0:
                data = self.queueLed.end()
                self.queueLed.clear()
                self.queueLedParser.parser(data)
                self.thread_led_parameter = self.queueLedParser.intParameter[1:5]
            self.robotLed.light(self.thread_led_parameter)
    #Buzzer thread
    def threadingRobotBuzzer(self):
        while True:
            if self.queueBuzzer.len()>0:
                data = self.queueBuzzer.get()
                self.queueBuzzerParser.parser(data)
                if self.queueBuzzerParser.intParameter[1] != 0:                            #S2 D2000, buzzer sounds at fixed frequency
                    self.robotBuzzer.buzzerRun(self.queueBuzzerParser.intParameter[1])    
                elif self.queueBuzzerParser.intParameter[1] == 0:                          #S2 D0, Determine if there are any parameters behind it?
                    if len(self.queueBuzzerParser.intParameter)==2:                        #S2 D0, with no parameters, turn off the buzzer and stop making sound
                        self.robotBuzzer.buzzerRun(self.queueBuzzerParser.intParameter[1])   
                    elif len(self.queueBuzzerParser.intParameter)==5:                      #S2 D0 D2000 D100 D3, With 3 parameters, 2000 represents the frequency, 100 represents the time of each sound, and 3 represents the number of sounds
                        self.robotBuzzer.buzzerRunXms(self.queueBuzzerParser.intParameter[2],self.queueBuzzerParser.intParameter[3],self.queueBuzzerParser.intParameter[4]) 
            else:
                time.sleep(0.1)
    #Feedback thread
    def threadingRobotActionFeedback(self):
        while True:
            if self.threadings_state == 3:               #If the server is running
                quese_count = self.queueAction.len()     #Gets the number of current robotic arm action message queues
                cmd = self.cmd.CUSTOM_ACTION + str("12") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_QUERY + str(quese_count) + str('\r\n')
                self.serverSend(cmd)
            time.sleep(0.5)
    #Server check thread
    def threadingCheckServer(self):
        while self.threadings_state != 4:
            if self.threadings_state == 0:   #Start the server
                self.threadings_state = 3
                self.turn_on_server()
                time.sleep(0.1)
            elif self.threadings_state == 1: #Shut down the server and prepare to restart the server
                self.threadings_state = 0
                self.turn_off_server()
                time.sleep(0.1)
            elif self.threadings_state == 2: #Shut down the server and exit the code
                self.threadings_state = 4
                self.turn_off_server()
                break
            elif self.threadings_state == 3: #The server is running properly
                time.sleep(0.5)
            else:
                pass
        print("main.py, The robot arm stops running, please press ctrl+c to exit.")
       
if __name__ == '__main__':
    import os
    os.system("sudo pigpiod")
    time.sleep(1)
    arm = ArmServer()
    try:
        print("Please use your computer or mobile phone to connect the robot arm.")
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        pass













