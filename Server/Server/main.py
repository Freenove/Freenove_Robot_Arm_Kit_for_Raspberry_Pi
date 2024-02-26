# -*- coding: utf-8 -*-
#!/usr/bin/env python

import time
import socket
import fcntl
import struct
import threading
import math

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
        #申请对象
        self.robotAction = arm.Arm()                                                                   #用来控制机械臂(步进电机+舵机)
        self.robotLed = ledPixel.LedPixel()                                                            #用来控制彩灯
        self.robotBuzzer = buzzer.Buzzer()                                                             #用来控制蜂鸣器
        self.robotFile = messageRecord.MessageRecord()                                                 #用来读写机械臂参数
        self.cmd = command.Command()                                                                   #命令关键字
        self.queueParser = messageParser.MessageParser()                                               #全局命令解析
        self.queueActionParser = messageParser.MessageParser()                                         #动作命令解析
        self.queueBuzzerParser = messageParser.MessageParser()                                         #蜂鸣器指令解析
        self.queueLedParser = messageParser.MessageParser()                                            #彩灯指令解析
        self.queueAction = messageQueue.MessageQueue()                                                 #消息队列，用来存储机械臂移动指令
        self.queueLed = messageQueue.MessageQueue()                                                    #消息队列，用来存储彩灯控制指令
        self.queueBuzzer = messageQueue.MessageQueue()                                                 #消息队列，用来存储蜂鸣器指令      

        #普通变量区
        self.last_pozition = [0,0,0]
        self.plane_axis_state = [0,0,0,0,0,0]                                                          #用来临时存储机械臂校准状态
        self.calibration_height = 20                                                                   #校准时原地抬笔高度                                                                    
        self.thread_led_parameter = [0,0,0,0]                                                          #用来存储彩灯的模式，RGB颜色值
        self.threadingReceive = None                                                                   #指令接收处理线程
        self.threadingArm = None                                                                       #机械臂移动线程
        self.threadingLed = None                                                                       #彩灯线程
        self.threadingBuzzer = None                                                                    #蜂鸣器线程
        self.threadingActionFeedback = None                                                            #机械臂运动反馈指令数目  
        self.threadings_state = 0                                                                      #0--运行服务器全部线程，1--关闭服务器全部线程，再重启服务器全部线程，2--关闭服务器全部线程，退出代码。3--正常运行代码。

        #加载本地参数
        self.robotAction.setClampLength(self.robotFile.readJsonObject("Clamp Length"))                 #设置机械臂末端点y轴偏移
        self.robotAction.setOriginHeight(self.robotFile.readJsonObject("Original Height"))             #设置机械臂转轴轴心距离底面高度
        self.robotAction.setGroundHeight(self.robotFile.readJsonObject("Ground Height"))               #设置机械臂底面距离地面高度
        self.robotAction.setPenHeight(self.robotFile.readJsonObject("Pen Height"))                     #设置机械臂末端点z轴偏移（笔具高度带来的变化）
        self.robotAction.setMsxMode(self.robotFile.readJsonObject("A4988 MSx"))                        #设置机械臂步进电机驱动模块细分度
        self.robotAction.setFrequency(self.robotFile.readJsonObject("A4988 CLK"))                      #设置步进电机脉冲频率
        self.robotAction.setArmOffseAngle(self.robotFile.readJsonObject("Home Angle Offset"))          #设置机械臂校准角度偏移

        self.homePoint = self.robotFile.readJsonObject("Home point")                                   #获取机械臂Home点坐标位置
        self.last_pozition = [float(self.homePoint[i]) for i in range(len(self.homePoint))]            #用来存储机械臂末端临时位置
        #加载机械臂配置状态信息（第一位代表传感器校准，第二位是底面高度设置，
        #第三位是夹具长度设置，第四位是home点原始位置坐标设置，第五位是home点角度偏移校准，
        #第六到九位是point1-point4坐标校准
        self.armState = self.robotFile.readJsonObject("Arm State")

        self.plane_axis_original_1 = [-100, 200, self.last_pozition[2]]                                #用来存储校准点1原始坐标位置
        self.plane_axis_original_2 = [100, 200, self.last_pozition[2]]                                 #用来存储校准点2原始坐标位置
        self.plane_axis_original_3 = [0, 150, self.last_pozition[2]]                                   #用来存储校准点3原始坐标位置
        self.plane_axis_original_4 = [0, 250, self.last_pozition[2]]                                   #用来存储校准点4原始坐标位置
        self.plane_axis_offset_1 = self.robotFile.readJsonObject("Point 1")                            #用来存储校准点1校准后坐标位置
        self.plane_axis_offset_2 = self.robotFile.readJsonObject("Point 2")                            #用来存储校准点2校准后坐标位置
        self.plane_axis_offset_3 = self.robotFile.readJsonObject("Point 3")                            #用来存储校准点3校准后坐标位置
        self.plane_axis_offset_4 = self.robotFile.readJsonObject("Point 4")                            #用来存储校准点4校准后坐标位置
        plane_x_z_value = self.robotFile.readJsonObject("Plane X-Z")                                   #设置机械臂校准参数
        self.robotAction.setPlaneXZ(plane_x_z_value[0], plane_x_z_value[1], plane_x_z_value[2], plane_x_z_value[3])
        plane_y_z_value = self.robotFile.readJsonObject("Plane Y-Z")                                   #设置机械臂校准参数
        self.robotAction.setPlaneYZ(plane_y_z_value[0], plane_y_z_value[1], plane_y_z_value[2], plane_y_z_value[3])
        #print(plane_x_z_value, plane_y_z_value)
        #核心代码
        self.robotActionCheck = 0                                                                      #用来查询机械臂的指令状态
        self.threadCheckServer = threading.Thread(target=self.threadingCheckServer)                    #定义一个线程，启动检查服务器连接是否正常
        self.threadCheckServer.start()                                                                 #启动线程

    #设置消息接收线程的状态
    def setThreadingReceiveState(self, state):
        try:
            buf_state = self.threadingReceive.is_alive()   
            if state == buf_state:
                #print("threadingReceive state is: " + str(state))
                pass
            else:
                if state == True:
                    self.threadingReceive = threading.Thread(target=self.threadingReceiveInstruction)
                    self.threadingReceive.start()
                    #print("threadingReceive start.")
                elif state == False:
                    messageThread.stop_thread(self.threadingReceive)
                    #print("threadingReceive close.")
        except:
            #print("setThreadingReceiveState error.")
            pass
    #设置机械臂移动线程的状态        
    def setThreadingArmState(self, state):
        try:
            buf_state = self.threadingArm.is_alive()   
            if state == buf_state:
                #print("threadingArm state is: " + str(state))
                pass
            else:
                if state == True:
                    self.threadingArm = threading.Thread(target=self.threadingRobotAction)
                    self.threadingArm.start()
                    #print("threadingArm start.")
                elif state == False:
                    messageThread.stop_thread(self.threadingArm)
                    #print("threadingArm close.")
        except:
            print("setThreadingArmState error.")
    #设置彩灯线程的状态        
    def setThreadingLedState(self, state):
        try:
            buf_state = self.threadingLed.is_alive()
            if state == buf_state:
                #print("threadingLed state is: " + str(state))
                pass
            else:
                if state == True:
                    self.threadingLed = threading.Thread(target=self.threadingRobotLed)
                    self.threadingLed.start()
                    #print("threadingLed start.")
                elif state == False:
                    messageThread.stop_thread(self.threadingLed)
                    #print("threadingLed close.")
        except:
            print("setThreadingLedState error.")
    #设置蜂鸣器线程的状态        
    def setThreadingBuzzerState(self, state):
        try:
            buf_state = self.threadingBuzzer.is_alive()   
            if state == buf_state:
                #print("threadingBuzzer state is: " + str(state))
                pass
            else:
                if state == True:
                    self.threadingBuzzer = threading.Thread(target=self.threadingRobotBuzzer)
                    self.threadingBuzzer.start()
                    #print("threadingBuzzer start.")
                elif state == False:
                    messageThread.stop_thread(self.threadingBuzzer)
                    #print("threadingBuzzer close.")
        except:
            print("setThreadingBuzzerState error.")
    #设置机械臂运动指令条目反馈线程的反馈        
    def setThreadingFeedbackState(self, state):
        try:
            buf_state = self.threadingActionFeedback.is_alive()   
            if state == buf_state:
                #print("threadingActionFeedback state is: " + str(state))
                pass
            else:
                if state == True:
                    self.threadingActionFeedback = threading.Thread(target=self.threadingRobotActionFeedback)
                    self.threadingActionFeedback.start()
                    #print("threadingActionFeedback start.")
                elif state == False:
                    messageThread.stop_thread(self.threadingActionFeedback)
                    #print("threadingActionFeedback close.")
        except:
            print("setThreadingFeedbackState error.")
    
    #机械臂蜂鸣器指令压入消息队列
    def setRobotBuzzer(self, frequency, delayms, times):
        cmd = self.cmd.CUSTOM_ACTION + str("2") + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.BUZZER_ACTION + str("0") + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.BUZZER_ACTION + str(frequency) + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.BUZZER_ACTION + str(delayms) + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.BUZZER_ACTION + str(times)
        self.queueBuzzer.put(cmd)
    #机械臂彩灯指令压入消息队列
    def setRobotLED(self, mode, r, g, b):
        cmd = self.cmd.CUSTOM_ACTION + str("1") + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.WS2812_MODE + str(mode) + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.WS2812_RED + str(r) + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.WS2812_GREEN + str(g) + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.WS2812_BLUE + str(b)
        self.queueLed.put(cmd)
    #机械臂动作指令压入消息队列
    def setRobotAction(self, axis):
        cmd = self.cmd.MOVE_ACTION + str("0") + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.AXIS_X_ACTION + str(axis[0]) + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.AXIS_Y_ACTION + str(axis[1]) + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.AXIS_Z_ACTION + str(axis[2])
        self.queueAction.put(cmd)

    #获取树莓派的IP地址
    def get_interface_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s',b'wlan0'[:15]))[20:24])
    #socket发送函数
    def serverSend(self,data):
        self.connection.send(data.encode('utf-8'))   #TCP数据发送函数
    #开启socket服务器功能，开始接收数据
    def turn_on_server(self):
        SOCKET_IP = self.get_interface_ip()                                                            #获取树莓派的IP地址
        self.server_socket = socket.socket()                                                           #创建一个socket对象
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT,1)                        #配置socket
        self.server_socket.bind((SOCKET_IP, 5000))                                                     #将这个socket对象绑定端口5000
        self.server_socket.listen(1)                                                                   #监听客户端数设置为1
        print("main.py,", 'Server address: ' + SOCKET_IP)                                       #在终端打印IP地址
        
        self.threadingReceive = threading.Thread(target=self.threadingReceiveInstruction)              #指令接收处理线程
        self.threadingArm = threading.Thread(target=self.threadingRobotAction)                         #机械臂移动线程
        self.threadingLed = threading.Thread(target=self.threadingRobotLed)                            #彩灯线程
        self.threadingBuzzer = threading.Thread(target=self.threadingRobotBuzzer)                      #蜂鸣器线程
        self.threadingActionFeedback = threading.Thread(target=self.threadingRobotActionFeedback)      #机械臂运动反馈指令数目  
        self.setThreadingReceiveState(True)                                                            #开启消息接收线程   
        self.setThreadingArmState(True)                                                                #开启机械臂移动线程
        self.setThreadingLedState(True)                                                                #开启彩灯线程
        self.setThreadingBuzzerState(True)                                                             #开启蜂鸣器线程
    #关闭socket服务器功能，停止接收数据
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

    #机械臂安装操作状态检查
    def safetyOperationInspection(self):
        cmd = None
        if self.robotActionCheck == 0:       #还没使能机械臂S8 E0
            cmd = self.cmd.CUSTOM_ACTION + str("8") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_ENABLE + str("0") + str('\r\n')
            self.serverSend(cmd)
        elif self.robotActionCheck == 1:     #还没进行传感器校准S10 F0
            cmd = self.cmd.CUSTOM_ACTION + str("10") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_SENSOR_POINT + str("0") + str('\r\n')
            self.serverSend(cmd)
        elif self.robotActionCheck == 2:     #还没回到传感器中心点S10 F1
            cmd = self.cmd.CUSTOM_ACTION + str("10") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_SENSOR_POINT + str("1") + str('\r\n')
            self.serverSend(cmd)
        elif self.robotActionCheck == 3:     #还没配置底面距离地面高度
            cmd = self.cmd.CUSTOM_ACTION + str("3") + self.cmd.DECOLLATOR_CHAR + self.cmd.GROUND_HEIGHT + str("?") + str('\r\n')
            self.serverSend(cmd)
        elif self.robotActionCheck == 4:     #还没配置机械臂夹具长度
            cmd = self.cmd.CUSTOM_ACTION + str("4") + self.cmd.DECOLLATOR_CHAR + self.cmd.CLAMP_LENGTH + str("?") + str('\r\n')
            self.serverSend(cmd)
        elif self.robotActionCheck == 5:     #还没告知机械臂home原始坐标位置
            cmd = self.cmd.CUSTOM_ACTION + str("5") + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.AXIS_X_ACTION + str("?") + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.AXIS_Y_ACTION + str("?") + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.AXIS_Z_ACTION + str("?") + str('\r\n')
            self.serverSend(cmd)

        elif self.robotActionCheck == 6:     #还没收到校准点home开始信号
            cmd = self.cmd.CUSTOM_ACTION + str("11") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_CALIBRATION_START + str("?") + str('\r\n')
            self.serverSend(cmd)
        elif self.robotActionCheck == 7:     #还没发送home点校准配置完成信号
            cmd = self.cmd.CUSTOM_ACTION + str("11") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_CALIBRATION_END + str("0") + str('\r\n')
            self.serverSend(cmd)
        elif self.robotActionCheck == 8:     #还没发送测试点1校准配置完成信号
            cmd = self.cmd.CUSTOM_ACTION + str("11") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_CALIBRATION_END + str("1") + str('\r\n')
            self.serverSend(cmd)
        elif self.robotActionCheck == 9:     #还没发送测试点2校准配置完成信号
            cmd = self.cmd.CUSTOM_ACTION + str("11") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_CALIBRATION_END + str("2") + str('\r\n')
            self.serverSend(cmd)
        elif self.robotActionCheck == 10:    #还没发送测试点3校准配置完成信号
            cmd = self.cmd.CUSTOM_ACTION + str("11") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_CALIBRATION_END + str("3") + str('\r\n')
            self.serverSend(cmd)
        elif self.robotActionCheck == 11:    #还没发送测试点4校准配置完成信号
            cmd = self.cmd.CUSTOM_ACTION + str("11") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_CALIBRATION_END + str("4") + str('\r\n')
            self.serverSend(cmd)
        if self.robotActionCheck == 12:    #全部准备工作已经完成
            return 1
        elif self.robotActionCheck != 12:
            self.setRobotBuzzer(1000, 100, 1)
            return 0

    #消息接收线程
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
                #如果获取到缓冲区没数据，说明客户端已经断开。
                if self.receiveData == "":
                    self.threadings_state = 1
                #获取到缓冲区数据，进行处理
                else:
                    cmdArray = self.receiveData.split('\r\n')   #以回车换行符为为分割线，将命令分割出来,['S13 N1', '']
                    print("main.py,", cmdArray)
                    if cmdArray[-1] !=" ":             #如果指令没有回车，默认指令无效
                        cmdArray = cmdArray[:-1]
                        for i in range(len(cmdArray)):
                            #print("main.py,", cmdArray[i])
                            try:
                                self.queueParser.parser(cmdArray[i])  #对指令进行解析
                            except:
                                print("main.py,", cmdArray[i])
                                self.queueParser.clearParameters()
                                continue 
                            if self.queueParser.commandArray[0] == self.cmd.MOVE_ACTION:         #机械臂移动指令(指令符合格式，添加到消息队列，指令不符合格式，打印提示信息)
                                if self.queueParser.intParameter[0] == 0 or self.queueParser.intParameter[0]==1 or self.queueParser.intParameter[0]==4:
                                    result = self.safetyOperationInspection()
                                    if result == 1:
                                        self.queueAction.put(cmdArray[i])
                                else:
                                    print("main.py, G{0} is error.".format(self.queueParser.intParameter[0]))
                            elif self.queueParser.commandArray[0] == self.cmd.CUSTOM_ACTION:     #机械臂自定义指令  
                                if self.queueParser.commandArray[1] == self.cmd.WS2812_MODE:             #彩灯指令S1
                                    self.queueLed.put(cmdArray[i])
                                elif self.queueParser.commandArray[1] == self.cmd.BUZZER_ACTION:         #蜂鸣器指令S2
                                    self.queueBuzzer.put(cmdArray[i])
                                elif self.queueParser.commandArray[1] == self.cmd.GROUND_HEIGHT:         #设置机械臂底面距离地面高度S3
                                    self.robotAction.setGroundHeight(self.queueParser.intParameter[1])
                                    self.robotFile.writeJsonObject("Ground Height", self.queueParser.intParameter[1])
                                    self.robotActionCheck = 4
                                    self.armState[1] = 1
                                    self.robotFile.writeJsonObject("Arm State", self.armState)
                                elif self.queueParser.commandArray[1] == self.cmd.CLAMP_LENGTH:          #设置夹具长度S4
                                    self.robotAction.setClampLength(self.queueParser.intParameter[1])
                                    self.robotFile.writeJsonObject("Clamp Length", self.queueParser.intParameter[1])
                                    self.robotActionCheck = 5
                                    self.armState[2] = 1
                                    self.robotFile.writeJsonObject("Arm State", self.armState)
                                elif self.queueParser.commandArray[1] == self.cmd.AXIS_X_ACTION:         #机械臂Home指令S5
                                    self.homePoint = [self.queueParser.floatParameter[i] for i in range(1,4)]   
                                    self.robotFile.writeJsonObject("Home point", self.homePoint)
                                    cmd = self.cmd.MOVE_ACTION + str("0") + self.cmd.DECOLLATOR_CHAR \
                                        + self.cmd.AXIS_X_ACTION + str(self.homePoint[0]) + self.cmd.DECOLLATOR_CHAR \
                                        + self.cmd.AXIS_Y_ACTION + str(self.homePoint[1]) + self.cmd.DECOLLATOR_CHAR \
                                        + self.cmd.AXIS_Z_ACTION + str(self.homePoint[2])
                                    self.queueAction.put(cmd)
                                    self.robotActionCheck = 6
                                    self.armState[3] = 1
                                    self.robotFile.writeJsonObject("Arm State", self.armState)
                                elif self.queueParser.commandArray[1] == self.cmd.ARM_FREQUENCY:         #设置机械臂脉冲频率S6
                                    self.robotAction.setFrequency(self.queueParser.intParameter[1])
                                    self.robotFile.writeJsonObject("A4988 CLK", self.queueParser.intParameter[1])
                                elif self.queueParser.commandArray[1] == self.cmd.ARM_MSX:               #设置机械臂细分度S7
                                    self.robotAction.writeA4988Clk(self.queueParser.intParameter[1])
                                    self.robotFile.writeJsonObject("A4988 MSx", self.queueParser.intParameter[1])
                                elif self.queueParser.commandArray[1] == self.cmd.ARM_ENABLE:            #使能/失能机械臂S8
                                    self.robotAction.setArmEnable(self.queueParser.intParameter[1]) 
                                    if self.queueParser.intParameter[1] == 0:
                                        if self.armState[0] == 0:
                                            self.robotActionCheck = 1    
                                        else:
                                            self.robotActionCheck = 2  
                                    else:
                                        self.robotActionCheck = 0                                          
                                elif self.queueParser.commandArray[1] == self.cmd.ARM_SERVO_INDEX:       #机械臂舵机控制指令S9
                                    self.queueAction.put(cmdArray[i])
                                elif self.queueParser.commandArray[1] == self.cmd.ARM_SENSOR_POINT:      #机械臂传感器校准和回传感器中心点S10
                                    if self.robotActionCheck == 1 or self.robotActionCheck == 2 or self.robotActionCheck == 12:
                                        self.queueAction.put(cmdArray[i])   
                                        if self.armState[0] == 1 and self.armState[1] == 1 and self.armState[2] == 1 and self.armState[3] == 1 and self.armState[4] == 1:
                                            self.robotActionCheck = 12
                                        else:
                                            self.robotActionCheck = 3
                                    else:
                                        self.safetyOperationInspection()
                                elif self.queueParser.commandArray[1] == self.cmd.ARM_CALIBRATION_START: #机械臂校准模式开始S11
                                    self.queueAction.put(cmdArray[i])
                                elif self.queueParser.commandArray[1] == self.cmd.ARM_CALIBRATION_POINT: #机械臂校准模式过程S11
                                    self.queueAction.put(cmdArray[i])
                                elif self.queueParser.commandArray[1] == self.cmd.ARM_CALIBRATION_END:   #机械臂校准模式结束S11
                                    self.queueAction.put(cmdArray[i])
                                elif self.queueParser.commandArray[1] == self.cmd.ARM_QUERY:             #接收到来自上位机的请求发送信号S12
                                    if self.queueParser.intParameter[1] == 1:                            #如果参数为1，开启线程反馈
                                        self.setThreadingFeedbackState(True)
                                    elif self.queueParser.intParameter[1] == 0:                          #如果指令为0，关闭线程反馈
                                        self.setThreadingFeedbackState(False)
                                elif self.queueParser.commandArray[1] == self.cmd.ARM_STOP:              #紧急急停指令S13
                                    self.threadings_state = 2
                                    self.receiveData = ""
                                    self.robotAction.setArmEnable(1)
                            else:                                                                #指令混乱异常，打印提示信息
                                print("main.py, The received command was incomplete.")
                            self.queueParser.clearParameters()
                    else:
                        print("main.py, The received data is incomplete.")
        except SystemExit:
            pass
    #机械臂运行线程
    def threadingRobotAction(self):
        while True:
            if self.queueAction.len() > 0:
                data = self.queueAction.get()
                self.queueActionParser.parser(data)
                #print("threadingRobotAction:", data)
                if self.queueActionParser.commandArray[0] == self.cmd.MOVE_ACTION:        #G代码指令
                    if self.queueActionParser.intParameter[0] == 0 or self.queueActionParser.intParameter[0]==1:        #G0/G1
                        x_index = None
                        y_index = None
                        z_index = None
                        if self.cmd.AXIS_X_ACTION in self.queueActionParser.commandArray:                               #如果指令中有X
                            x_index = self.queueActionParser.commandArray.index(self.cmd.AXIS_X_ACTION)                 #查找X的位置
                            self.last_pozition[0] = self.queueActionParser.floatParameter[x_index]                      #将参数赋值给目标坐标系[0]
                        if self.cmd.AXIS_Y_ACTION in self.queueActionParser.commandArray:                               #如果指令中有Y
                            y_index = self.queueActionParser.commandArray.index(self.cmd.AXIS_Y_ACTION)                 #查找Y的位置
                            self.last_pozition[1] = self.queueActionParser.floatParameter[y_index]                      #将参数赋值给目标坐标系[1]
                        if self.cmd.AXIS_Z_ACTION in self.queueActionParser.commandArray:                               #如果指令中有Z
                            z_index = self.queueActionParser.commandArray.index(self.cmd.AXIS_Z_ACTION)                 #查找Z的位置
                            self.last_pozition[2] = self.queueActionParser.floatParameter[z_index]                      #将参数赋值给目标坐标系[2]
                        #将平面的运动范围限制在半径100mm-270mm之间，高度限制在-100-200mm之间
                        x = self.last_pozition[0]
                        y = self.last_pozition[1]
                        z = self.last_pozition[2]
                        min_sphere = self.robotAction.is_point_inside_sphere(x,y,z,100)
                        max_sphere = self.robotAction.is_point_inside_sphere(x,y,z,270)
                        print("min_sphere, max_sphere, self.last_pozition: ", min_sphere, max_sphere, self.last_pozition)
                        if (min_sphere == 1 or min_sphere == 2) and (max_sphere==0):#在以转轴为球心，半径为270mm的大球内，半径为100mm的小球外
                            #self.last_pozition[0]
                            #self.last_pozition[1]
                            #self.last_pozition[2] = self.robotAction.constrain(self.last_pozition[2], -100, 180)
                            #判断是否经过中心圆柱区域
                            data, circle_axis_1, circle_axis_2 = self.robotAction.calculate_valid_axis(self.robotAction.last_axis, self.last_pozition, 100)
                            print(data, self.robotAction.last_axis, self.last_pozition, circle_axis_1, circle_axis_2)
                            if data[0] == 1:                                                         #存在相交点
                                if data[1] == 2:                                                     #两个相交点在起点和终点形成的线段之间
                                    self.robotAction.moveStepMotorToTargetAxis(circle_axis_1)        
                                    self.robotAction.moveStepMotorToTargetAxis(circle_axis_2, 2)        
                                    self.robotAction.moveStepMotorToTargetAxis(self.last_pozition)   
                                elif data[1] == 1:                                                   #有一个相交点在起点和终点形成的线段之间
                                    self.robotAction.moveStepMotorToTargetAxis(circle_axis_1)        
                                elif data[1] == 0:                                                   #起点在圆上，终点在圆内，不符合移动条件
                                    pass
                            elif data[0] == 1:                                                       #起点和终点在圆外，直接移动
                                self.robotAction.moveStepMotorToTargetAxis(self.last_pozition)      
                        else:
                            self.setRobotBuzzer(2000,100,1)     

                    elif self.queueActionParser.intParameter[0]==4:                                                     #G4
                        if self.cmd.DELAY_T_ACTION in self.queueActionParser.commandArray:                              #如果指令中有T
                            t_index = self.queueActionParser.commandArray.index(self.cmd.DELAY_T_ACTION)                #查找X的位置
                            delay_ms = self.queueActionParser.intParameter[t_index]                                     #将参数赋值给目标坐标系[0]
                            time.sleep(delay_ms/1000.0)                                                                 #暂停动作delay_ms毫秒
                        else:                                                                                           #G指令错误
                            print("main.py, G{0} is error.".format(self.queueActionParser.intParameter[0]))
                    else:
                        self.queueActionParser.clearParameters()
                elif self.queueActionParser.commandArray[0] == self.cmd.CUSTOM_ACTION:    #自定义指令
                    if self.queueActionParser.intParameter[0] == 10:      
                        if self.queueActionParser.intParameter[1]==0:                     
                            record_pulse = self.robotAction.setArmToZeroPoint()                                                       #自动调整机械臂的传感器零点，并反馈脉冲偏移量
                            self.robotFile.writeJsonObject("Sensor Pulse Offset", record_pulse)                                       #记录调零脉冲偏移量到本地文件中
                            self.armState[0] = 1
                            self.robotFile.writeJsonObject("Arm State", self.armState)
                        elif self.queueActionParser.intParameter[1]==1:     
                            if self.armState[0] == 0:
                                record_pulse = self.robotAction.setArmToZeroPoint()                                                       #自动调整机械臂的传感器零点，并反馈脉冲偏移量
                                self.robotFile.writeJsonObject("Sensor Pulse Offset", record_pulse)                                       #记录调零脉冲偏移量到本地文件中
                                self.armState[0] = 1
                                self.robotFile.writeJsonObject("Arm State", self.armState)
                            else:
                                pulse_count = self.robotFile.readJsonObject("Sensor Pulse Offset")                                        #读取本地文件的调零脉冲偏移量
                                self.robotAction.setArmToZeroPointNoAdjust(pulse_count)                                                   #控制机械臂回到零点位置
                        self.setRobotBuzzer(2000,100,1)                                                                                   #蜂鸣器提示音
                    elif self.queueActionParser.intParameter[0] == 11:
                        if self.queueActionParser.commandArray[1] == self.cmd.ARM_CALIBRATION_START:
                            if self.queueActionParser.intParameter[1] == 0:
                                self.robotAction.setArmOffseAngle([0,0,0])                                                                #让机械臂回归初始无偏移状态
                                self.original_axis_position = self.homePoint.copy()                                                       #获取校准点原始坐标
                                self.adjust_axis_position = self.original_axis_position.copy()                                            #偏移坐标初始化为和原始坐标一致
                                self.original_adjust_point_angle = self.robotAction.coordinateToAngle(self.original_axis_position)        #将坐标转化为角度值
                                self.setRobotAction(self.original_axis_position)                                                          #控制机械臂移动到目标位置
                                self.setRobotBuzzer(2000,100,1)                                                                           #蜂鸣器提示音
                                self.robotActionCheck = 7
                                self.robotFile.writeJsonObject("Home Angle Offset", [0, 0, 0])                                            #清除本地原有偏移参数
                                self.armState[4] = 0
                                self.robotFile.writeJsonObject("Arm State", self.armState)
                            elif self.queueActionParser.intParameter[1] == 1:
                                self.robotAction.setPlaneXZ(0,0,0,0)
                                last_pozition = self.last_pozition.copy()                                                                 #获取机械臂当前坐标位置
                                last_pozition[2] = last_pozition[2] + self.calibration_height                                             #z轴抬高
                                self.robotAction.moveStepMotorToTargetAxis(last_pozition)                           
                                self.plane_axis_original_1 = [-100, 200, self.homePoint[2]]                                               #获取校准点1原始坐标数据         
                                self.plane_axis_original_1[2] = self.plane_axis_original_1[2] + self.calibration_height                   #移动到校准点1原始坐标上方
                                self.robotAction.moveStepMotorToTargetAxis(self.plane_axis_original_1)                                   
                                self.plane_axis_original_1[2] = self.plane_axis_original_1[2] - self.calibration_height                   #移动到校准点1原始坐标位置
                                self.robotAction.moveStepMotorToTargetAxis(self.plane_axis_original_1) 
                                self.last_pozition = self.plane_axis_original_1.copy()
                                self.setRobotBuzzer(2000, 100, 1)                                                                         #蜂鸣器发声
                                self.robotActionCheck = 8
                                self.robotFile.writeJsonObject("Point 1", [-100, 200, self.homePoint[2]])                                 #清除本地Point1参数
                                self.armState[5] = 0
                                self.robotFile.writeJsonObject("Arm State", self.armState)
                            elif self.queueActionParser.intParameter[1] == 2:
                                self.robotAction.setPlaneXZ(0,0,0,0)
                                last_pozition = self.last_pozition.copy()                                                    #获取机械臂当前坐标位置
                                last_pozition[2] = last_pozition[2] + self.calibration_height                                #z轴抬高
                                self.robotAction.moveStepMotorToTargetAxis(last_pozition)                           
                                self.plane_axis_original_2 = [100, 200, self.homePoint[2]]                                   #获取校准点2原始坐标数据     
                                self.plane_axis_original_2[2] = self.plane_axis_original_2[2] + self.calibration_height
                                self.robotAction.moveStepMotorToTargetAxis(self.plane_axis_original_2) 
                                self.plane_axis_original_2[2] = self.plane_axis_original_2[2] - self.calibration_height
                                self.robotAction.moveStepMotorToTargetAxis(self.plane_axis_original_2) 
                                self.last_pozition = self.plane_axis_original_2.copy()
                                self.setRobotBuzzer(2000, 100, 1)
                                self.robotActionCheck = 9
                                self.robotFile.writeJsonObject("Point 2", [100, 200, self.homePoint[2]])                     #清除本地Point2参数
                                self.armState[6] = 0
                                self.robotFile.writeJsonObject("Arm State", self.armState)
                            elif self.queueActionParser.intParameter[1] == 3:
                                self.robotAction.setPlaneYZ(0,0,0,0)
                                last_pozition = self.last_pozition.copy()                                                    #获取机械臂当前坐标位置
                                last_pozition[2] = last_pozition[2] + self.calibration_height                                #z轴抬高
                                self.robotAction.moveStepMotorToTargetAxis(last_pozition)                           
                                self.plane_axis_original_3 = [0, 150, self.homePoint[2]]                                     #获取校准点3原始坐标数据     
                                self.plane_axis_original_3[2] = self.plane_axis_original_3[2] + self.calibration_height
                                self.robotAction.moveStepMotorToTargetAxis(self.plane_axis_original_3) 
                                self.plane_axis_original_3[2] = self.plane_axis_original_3[2] - self.calibration_height
                                self.robotAction.moveStepMotorToTargetAxis(self.plane_axis_original_3) 
                                self.last_pozition = self.plane_axis_original_3.copy()
                                self.setRobotBuzzer(2000, 100, 1)
                                self.robotActionCheck = 10
                                self.robotFile.writeJsonObject("Point 3", [0, 150, self.homePoint[2]])                       #清除本地Point3参数
                                self.armState[7] = 0
                                self.robotFile.writeJsonObject("Arm State", self.armState)
                            elif self.queueActionParser.intParameter[1] == 4:
                                self.robotAction.setPlaneYZ(0,0,0,0)
                                last_pozition = self.last_pozition.copy()                                                    #获取机械臂当前坐标位置
                                last_pozition[2] = last_pozition[2] + self.calibration_height                                #z轴抬高
                                self.robotAction.moveStepMotorToTargetAxis(last_pozition)                           
                                self.plane_axis_original_4 = [0, 250, self.homePoint[2]]                                     #获取校准点4原始坐标数据     
                                self.plane_axis_original_4[2] = self.plane_axis_original_4[2] + self.calibration_height
                                self.robotAction.moveStepMotorToTargetAxis(self.plane_axis_original_4) 
                                self.plane_axis_original_4[2] = self.plane_axis_original_4[2] - self.calibration_height
                                self.robotAction.moveStepMotorToTargetAxis(self.plane_axis_original_4) 
                                self.last_pozition = self.plane_axis_original_4.copy()
                                self.setRobotBuzzer(2000, 100, 1)
                                self.robotActionCheck = 11
                                self.robotFile.writeJsonObject("Point 4", [0, 250, self.homePoint[2]])                       #清除本地Point4参数
                                self.armState[8] = 0
                                self.robotFile.writeJsonObject("Arm State", self.armState)
                        elif self.queueActionParser.commandArray[1] == self.cmd.ARM_CALIBRATION_POINT:
                            if self.queueActionParser.intParameter[1] == 0:
                                self.adjust_axis_position = [self.queueActionParser.floatParameter[i] for i in range(2,5)]                #获取校准点坐标
                                self.setRobotAction(self.adjust_axis_position)                                                            #控制机械臂移动到目标位置
                                #self.setRobotBuzzer(2000,100,1)                                                                           #蜂鸣器提示音
                            elif self.queueActionParser.intParameter[1] == 1:
                                self.plane_axis_offset_1 = [self.queueActionParser.floatParameter[i] for i in range(2,5)] #获取校准点坐标
                                self.robotAction.moveStepMotorToTargetAxis(self.plane_axis_offset_1)                      #移动到该坐标
                                self.last_pozition = self.plane_axis_offset_1.copy()                                      #记录当前位置
                                #self.setRobotBuzzer(2000,100,1)                                                          #蜂鸣器发声
                            elif self.queueActionParser.intParameter[1] == 2:
                                self.plane_axis_offset_2 = [self.queueActionParser.floatParameter[i] for i in range(2,5)] #获取校准点坐标
                                self.robotAction.moveStepMotorToTargetAxis(self.plane_axis_offset_2)                      #移动到该坐标
                                self.last_pozition = self.plane_axis_offset_2.copy()                                      #记录当前位置
                                #self.setRobotBuzzer(2000,100,1)                                                          #蜂鸣器发声
                            elif self.queueActionParser.intParameter[1] == 3:
                                self.plane_axis_offset_3 = [self.queueActionParser.floatParameter[i] for i in range(2,5)] #获取校准点坐标
                                self.robotAction.moveStepMotorToTargetAxis(self.plane_axis_offset_3)                      #移动到该坐标
                                self.last_pozition = self.plane_axis_offset_3.copy()                                      #记录当前位置
                                #self.setRobotBuzzer(2000,100,1)                                                          #蜂鸣器发声
                            elif self.queueActionParser.intParameter[1] == 4:
                                self.plane_axis_offset_4 = [self.queueActionParser.floatParameter[i] for i in range(2,5)] #获取校准点坐标
                                self.robotAction.moveStepMotorToTargetAxis(self.plane_axis_offset_4)                      #移动到该坐标
                                self.last_pozition = self.plane_axis_offset_4.copy()                                      #记录当前位置
                                #self.setRobotBuzzer(2000,100,1)                                                          #蜂鸣器发声
                            elif self.queueActionParser.intParameter[1] == -1:
                                self.robotActionCheck = 6 
                                self.safetyOperationInspection()
                        elif self.queueActionParser.commandArray[1] == self.cmd.ARM_CALIBRATION_END:
                            if self.queueActionParser.intParameter[1] == 0:
                                self.adjust_axis_position = [self.queueActionParser.floatParameter[i] for i in range(2,5)]                #获取校准点坐标
                                self.after_adjust_point_angle = self.robotAction.coordinateToAngle(self.adjust_axis_position)             #将坐标转化为角度值
                                offset_angle = [self.after_adjust_point_angle[i] - self.original_adjust_point_angle[i] for i in range(3)] #计算校准偏移角度差值
                                self.robotAction.setArmOffseAngle(offset_angle)                                                           #设置机械臂角度偏移值，使配置生效
                                self.robotFile.writeJsonObject("Home Angle Offset", offset_angle)                                         #将校准偏移角度差记录到本地文件中
                                axis = self.homePoint.copy()                                                                              #获取校准点原始坐标
                                axis[2] = axis[2] + self.calibration_height                                                               #z轴加一定高度
                                self.robotAction.moveStepMotorToTargetAxis(axis)                                                          #移动到校准点原始坐标上方
                                axis = self.homePoint.copy()                                                                              #获取校准点原始坐标
                                self.robotAction.moveStepMotorToTargetAxis(axis)                                                          #控制机械臂移动到目标位置
                                self.setRobotBuzzer(2000,100,3)                                                                           #蜂鸣器提示音
                                self.robotActionCheck = 12
                                self.armState[4] = 1
                                self.robotFile.writeJsonObject("Arm State", self.armState)
                            elif self.queueActionParser.intParameter[1] == 1:
                                self.plane_axis_offset_1 = [self.queueActionParser.floatParameter[i] for i in range(2,5)] #获取校准点坐标
                                self.robotFile.writeJsonObject("Point 1", self.plane_axis_offset_1)                       #记录本地Point1参数
                                self.robotActionCheck = 12
                                self.armState[5] = 1
                                self.robotFile.writeJsonObject("Arm State", self.armState)
                                if self.armState[5] == 1 and self.armState[6] == 1:
                                    plane_x_z_value = [0, 0, 0, 0]
                                    plane_x_z_value[0] = self.plane_axis_original_1[0]
                                    plane_x_z_value[1] = self.plane_axis_original_2[0]
                                    plane_x_z_value[2] = self.plane_axis_offset_1[2] - self.plane_axis_original_1[2]
                                    plane_x_z_value[3] = self.plane_axis_offset_2[2] - self.plane_axis_original_2[2]
                                    self.robotFile.writeJsonObject("Plane X-Z", plane_x_z_value)                          #设置机械臂校准参数
                                    self.robotAction.setPlaneXZ(plane_x_z_value[0], plane_x_z_value[1], plane_x_z_value[2], plane_x_z_value[3])
                                last_pozition = self.last_pozition.copy()                                                 #原地抬笔
                                last_pozition[2] = last_pozition[2] + self.calibration_height
                                self.robotAction.moveStepMotorToTargetAxis(last_pozition) 
                                axis = self.homePoint.copy()                                                              #移动到校准点上方
                                axis[2] = axis[2] + self.calibration_height
                                self.robotAction.moveStepMotorToTargetAxis(axis)  
                                axis[2] = axis[2] - self.calibration_height                                               #移动到校准后的位置
                                self.robotAction.moveStepMotorToTargetAxis(axis)  
                                self.last_pozition = axis.copy()
                                self.setRobotBuzzer(2000,100,3)
                            elif self.queueActionParser.intParameter[1] == 2:
                                self.plane_axis_offset_2 = [self.queueActionParser.floatParameter[i] for i in range(2,5)] #获取校准点坐标
                                self.robotFile.writeJsonObject("Point 2", self.plane_axis_offset_2)                       #记录本地Point2参数
                                self.robotActionCheck = 12
                                self.armState[6] = 1
                                self.robotFile.writeJsonObject("Arm State", self.armState)
                                if self.armState[5] == 1 and self.armState[6] == 1:
                                    plane_x_z_value = [0, 0, 0, 0]
                                    plane_x_z_value[0] = self.plane_axis_original_1[0]
                                    plane_x_z_value[1] = self.plane_axis_original_2[0]
                                    plane_x_z_value[2] = self.plane_axis_offset_1[2] - self.plane_axis_original_1[2]
                                    plane_x_z_value[3] = self.plane_axis_offset_2[2] - self.plane_axis_original_2[2]
                                    self.robotFile.writeJsonObject("Plane X-Z", plane_x_z_value)                          #设置机械臂校准参数
                                    self.robotAction.setPlaneXZ(plane_x_z_value[0], plane_x_z_value[1], plane_x_z_value[2], plane_x_z_value[3])
                                last_pozition = self.last_pozition.copy()                                                 #原地抬笔
                                last_pozition[2] = last_pozition[2] + self.calibration_height
                                self.robotAction.moveStepMotorToTargetAxis(last_pozition) 
                                axis = self.homePoint.copy()                                                              #移动到校准点上方
                                axis[2] = axis[2] + self.calibration_height
                                self.robotAction.moveStepMotorToTargetAxis(axis)  
                                axis[2] = axis[2] - self.calibration_height                                               #移动到校准后的位置
                                self.robotAction.moveStepMotorToTargetAxis(axis)  
                                self.last_pozition = axis.copy()
                                self.setRobotBuzzer(2000,100,3)
                            elif self.queueActionParser.intParameter[1] == 3:
                                self.plane_axis_offset_3 = [self.queueActionParser.floatParameter[i] for i in range(2,5)] #获取校准点坐标
                                self.robotFile.writeJsonObject("Point 3", self.plane_axis_offset_3)                       #记录本地Point3参数
                                self.robotActionCheck = 12
                                self.armState[7] = 1
                                self.robotFile.writeJsonObject("Arm State", self.armState)
                                if self.armState[7] == 1 and self.armState[8] == 1:
                                    plane_y_z_value = [0, 0, 0, 0]
                                    plane_y_z_value[0] = self.plane_axis_original_3[1]
                                    plane_y_z_value[1] = self.plane_axis_original_4[1]
                                    plane_y_z_value[2] = self.plane_axis_offset_3[2] - self.plane_axis_original_3[2]
                                    plane_y_z_value[3] = self.plane_axis_offset_4[2] - self.plane_axis_original_4[2]
                                    self.robotFile.writeJsonObject("Plane Y-Z", plane_y_z_value)                          #设置机械臂校准参数
                                    self.robotAction.setPlaneYZ(plane_y_z_value[0], plane_y_z_value[1], plane_y_z_value[2], plane_y_z_value[3])
                                last_pozition = self.last_pozition.copy()                                                 #原地抬笔
                                last_pozition[2] = last_pozition[2] + self.calibration_height
                                self.robotAction.moveStepMotorToTargetAxis(last_pozition) 
                                axis = self.homePoint.copy()                                                              #移动到校准点上方
                                axis[2] = axis[2] + self.calibration_height
                                self.robotAction.moveStepMotorToTargetAxis(axis)  
                                axis[2] = axis[2] - self.calibration_height                                               #移动到校准后的位置
                                self.robotAction.moveStepMotorToTargetAxis(axis)  
                                self.last_pozition = axis.copy()
                                self.setRobotBuzzer(2000,100,3)
                            elif self.queueActionParser.intParameter[1] == 4:
                                self.plane_axis_offset_4 = [self.queueActionParser.floatParameter[i] for i in range(2,5)] #获取校准点坐标
                                self.robotFile.writeJsonObject("Point 4", self.plane_axis_offset_4)                       #记录本地Point3参数
                                self.robotActionCheck = 12
                                self.armState[8] = 1
                                self.robotFile.writeJsonObject("Arm State", self.armState)
                                if self.armState[7] == 1 and self.armState[8] == 1:
                                    plane_y_z_value = [0, 0, 0, 0]
                                    plane_y_z_value[0] = self.plane_axis_original_3[1]
                                    plane_y_z_value[1] = self.plane_axis_original_4[1]
                                    plane_y_z_value[2] = self.plane_axis_offset_3[2] - self.plane_axis_original_3[2]
                                    plane_y_z_value[3] = self.plane_axis_offset_4[2] - self.plane_axis_original_4[2]
                                    self.robotFile.writeJsonObject("Plane Y-Z", plane_y_z_value)                          #设置机械臂校准参数
                                    self.robotAction.setPlaneYZ(plane_y_z_value[0], plane_y_z_value[1], plane_y_z_value[2], plane_y_z_value[3])
                                last_pozition = self.last_pozition.copy()                                                 #原地抬笔
                                last_pozition[2] = last_pozition[2] + self.calibration_height
                                self.robotAction.moveStepMotorToTargetAxis(last_pozition) 
                                axis = self.homePoint.copy()                                                              #移动到校准点上方
                                axis[2] = axis[2] + self.calibration_height
                                self.robotAction.moveStepMotorToTargetAxis(axis)  
                                axis[2] = axis[2] - self.calibration_height                                               #移动到校准后的位置
                                self.robotAction.moveStepMotorToTargetAxis(axis)  
                                self.last_pozition = axis.copy()
                                self.setRobotBuzzer(2000,100,3)
                            elif self.queueActionParser.intParameter[1] == -1:
                                self.robotActionCheck = 6 
                                self.safetyOperationInspection() 
            else:
                pass
    #彩灯显示线程
    def threadingRobotLed(self):
        while True:
            if self.queueLed.len()>0:
                data = self.queueLed.end()
                self.queueLed.clear()
                #print("threadingRobotLed:", data)
                self.queueLedParser.parser(data)
                self.thread_led_parameter = self.queueLedParser.intParameter[1:5]
            self.robotLed.light(self.thread_led_parameter)
    #蜂鸣器线程
    def threadingRobotBuzzer(self):
        while True:
            if self.queueBuzzer.len()>0:
                data = self.queueBuzzer.get()
                #print("threadingRobotBuzzer:", data)
                self.queueBuzzerParser.parser(data)
                if self.queueBuzzerParser.intParameter[1] != 0:                            #D2000，控制蜂鸣器出固定频率的声音
                    self.robotBuzzer.buzzerRun(self.queueBuzzerParser.intParameter[1])    
                elif self.queueBuzzerParser.intParameter[1] == 0:                          #D0，进一步判断。不带参数，则停止发出声音，带参数，则根据参数发出声音
                    if len(self.queueBuzzerParser.intParameter)==2:                        #不带参数，关闭蜂鸣器，停止发出声音
                        self.robotBuzzer.buzzerRun(self.queueBuzzerParser.intParameter[1])   
                    elif len(self.queueBuzzerParser.intParameter)==5:                      #带3个参数，D0 D2000 D100 D3:2000表示频率，100表示每次发出声音的时间，3表示发出声音的次数
                        self.robotBuzzer.buzzerRunXms(self.queueBuzzerParser.intParameter[2],self.queueBuzzerParser.intParameter[3],self.queueBuzzerParser.intParameter[4]) 
            else:
                time.sleep(0.1)
    #执行指令数目反馈线程 
    def threadingRobotActionFeedback(self):
        while True:
            if self.threadings_state == 3:               #如果服务器正在运行
                quese_count = self.queueAction.len()     #获取当前机械臂动作消息队列数目
                cmd = self.cmd.CUSTOM_ACTION + str("12") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_QUERY + str(quese_count) + str('\r\n')
                #print("cmd:" + cmd)
                self.serverSend(cmd)
            time.sleep(0.5)
    #服务器检查线程
    def threadingCheckServer(self):
        while self.threadings_state != 4:
            if self.threadings_state == 0:   #开启服务器
                self.threadings_state = 3
                self.turn_on_server()
                time.sleep(0.1)
            elif self.threadings_state == 1: #关闭服务器，并准备重启服务器
                self.threadings_state = 0
                self.turn_off_server()
                time.sleep(0.1)
            elif self.threadings_state == 2: #关闭服务器，并退出代码
                self.threadings_state = 4
                self.turn_off_server()
                break
            elif self.threadings_state == 3: #服务器正常运行
                time.sleep(0.5)
            else:
                pass
        print("main.py, The robot arm stops running, please press ctrl+c to exit.")
       
    

if __name__ == '__main__':
    import os
    os.system("sudo pigpiod")
    time.sleep(1)
    os.system("sudo pigpiod")
    arm = ArmServer()
    try:
        print("Please use your computer or mobile phone to connect the robot arm.")
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        pass













