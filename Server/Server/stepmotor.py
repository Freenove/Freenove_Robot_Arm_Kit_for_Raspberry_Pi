# -*- coding: utf-8 -*-
#!/usr/bin/env python

import pigpio
import time
import math
import threading
import os
import sensor

class StepMotor:
    def __init__(self):
        self.turn_direction = 1                                  #如果步进电机线序相反，将1改为0。目前是同向线
        self.A4988_EN = 9                                        #A4988模块使能引脚
        self.A4988_MSX = [10, 24, 23]                            #A4988模块细分度设置引脚
        self.A4988_DIR = [14, 15, 27]                            #A4988模块驱动电机旋转方向引脚
        self.A4988_STEP = [4, 17, 22]                            #A4988模块驱动电机脉冲信号引脚
        self.tcrt5000 = sensor.TCRT5000()                        #申请一个传感器对象
        self.initA4988()                                         #初始化控制A4988模块的引脚 
        self.setA4988Enable(1)                                   #设置电机为失能状态
        self.setA4988MsxMode(5)                                  #设置A4988模块细分度为5
        self.A4988MsxModeValue = 5                               #申请变量，用来记录电机驱动模块细分度
        self.A4988ClkFrequency = [1000,1000,1000]                #3个步进电机驱动模块的脉冲频率
        self.pulse_margin = [0,0,0]                              #脉冲余量
        self.pulse_margin_dir = [0,0,0]                          #脉冲余量方向
        self.zeroAngle = [90, 110, -12]                          #理论设计上，三个步进电机在传感器中心时的角度值
        self.offsetAngle = [0, 0, 0]                             #步进电机偏移角度,用来校准设置home点
        self.lastAngle = self.zeroAngle.copy()                   #用来记录最后一次动作的位置角度
        
    def initA4988(self):
        self.MODULE_EN = pigpio.pi()
        self.MODULE_EN.set_mode(self.A4988_EN, pigpio.OUTPUT)
        self.MODULE_MS1 = pigpio.pi()
        self.MODULE_MS1.set_mode(self.A4988_MSX[0], pigpio.OUTPUT)
        self.MODULE_MS2 = pigpio.pi()
        self.MODULE_MS2.set_mode(self.A4988_MSX[1], pigpio.OUTPUT)
        self.MODULE_MS3 = pigpio.pi()
        self.MODULE_MS3.set_mode(self.A4988_MSX[2], pigpio.OUTPUT)
        self.MODULE_DIR_1 = pigpio.pi()
        self.MODULE_DIR_1.set_mode(self.A4988_DIR[0], pigpio.OUTPUT)
        self.MODULE_DIR_2 = pigpio.pi()
        self.MODULE_DIR_2.set_mode(self.A4988_DIR[1], pigpio.OUTPUT)
        self.MODULE_DIR_3 = pigpio.pi()
        self.MODULE_DIR_3.set_mode(self.A4988_DIR[2], pigpio.OUTPUT)
        self.MODULE_STEP_1 = pigpio.pi()
        self.MODULE_STEP_1.set_mode(self.A4988_STEP[0], pigpio.OUTPUT)
        self.MODULE_STEP_2 = pigpio.pi()
        self.MODULE_STEP_2.set_mode(self.A4988_STEP[1], pigpio.OUTPUT)
        self.MODULE_STEP_3 = pigpio.pi()
        self.MODULE_STEP_3.set_mode(self.A4988_STEP[2], pigpio.OUTPUT)
    
    def setA4988Enable(self, enable):
        self.MODULE_EN.write(self.A4988_EN, enable)
        
    def setA4988MSx(self, ms1, ms2, ms3):
        self.MODULE_MS1.write(self.A4988_MSX[0], ms1)
        self.MODULE_MS2.write(self.A4988_MSX[1], ms2)
        self.MODULE_MS3.write(self.A4988_MSX[2], ms3)
    def readA4988Msx(self):
        if self.A4988MsxModeValue == 1:
            pll = 1
        elif self.A4988MsxModeValue == 2:
            pll = 2
        elif self.A4988MsxModeValue == 3:
            pll = 4
        elif self.A4988MsxModeValue == 4:
            pll = 8
        else:
            pll = 16
        return pll
    def setA4988MsxMode(self, mode):
        if mode == 1:
            self.A4988MsxModeValue = 1
            self.setA4988MSx(0,0,0)
        elif mode == 2:
            self.A4988MsxModeValue = 2
            self.setA4988MSx(1,0,0)
        elif mode == 3:
            self.A4988MsxModeValue = 3
            self.setA4988MSx(0,1,0)
        elif mode == 4:
            self.A4988MsxModeValue = 4
            self.setA4988MSx(1,1,0)
        elif mode == 5:
            self.A4988MsxModeValue = 5
            self.setA4988MSx(1,1,1)  
        else:
            self.A4988MsxModeValue = 5
            self.setA4988MSx(1,1,1) 
    def setA4988ClkFrequency(self, frequency):
        self.A4988ClkFrequency = frequency
    
    def myDelay(self, second):
        microsecond = second * 1000000
        start, end = 0,0
        start = time.time()
        t = (microsecond - 33) / 1000000
        while end - start < t:
            end = time.time()
        
    def motorRun(self, motor_number, direction, pulse_count, pulse_frequency):
        if pulse_count == 0 or pulse_frequency == 0:
            return
        turn_direction = direction
        if self.turn_direction == 1:
            if direction == 1:
                turn_direction = 0
            elif direction == 0:
                turn_direction = 1
        pulse_period = 1 / pulse_frequency                            # 计算脉冲周期，单位秒
        half_pulse_period = pulse_period / 2                          # 占空比50%，因此计算半个周期的时间，单位秒
        if motor_number == 1:                                         # 如果要控制电机1
            self.MODULE_DIR_3.write(self.A4988_DIR[2], turn_direction)
            for i in range(pulse_count):
                self.MODULE_STEP_3.write(self.A4988_STEP[2], 1)
                self.myDelay(half_pulse_period)
                self.MODULE_STEP_3.write(self.A4988_STEP[2], 0)
                self.myDelay(half_pulse_period)   
        elif motor_number == 2:
            self.MODULE_DIR_2.write(self.A4988_DIR[1], turn_direction)
            for i in range(pulse_count):
                self.MODULE_STEP_2.write(self.A4988_STEP[1], 1)
                self.myDelay(half_pulse_period)
                self.MODULE_STEP_2.write(self.A4988_STEP[1], 0)
                self.myDelay(half_pulse_period)   
        elif motor_number == 3:
            self.MODULE_DIR_1.write(self.A4988_DIR[0], turn_direction)# 设置电机转动方向
            for i in range(pulse_count):                              # 控制引脚发出特定频率的脉冲pulse_count个
                self.MODULE_STEP_1.write(self.A4988_STEP[0], 1)       # 控制引脚输出高电平
                self.myDelay(half_pulse_period)                       # 维持高电平半个脉冲周期
                self.MODULE_STEP_1.write(self.A4988_STEP[0], 0)       # 控制引脚输出低电平
                self.myDelay(half_pulse_period)                       # 维持低电平半个脉冲周期
       
    def gotoMidZeroPoint1(self):
        # 确保机械臂在零点的右边
        s1 = self.tcrt5000.readTCRT5000S1()
        while s1 == 1:
            motor1 = threading.Thread(target=self.motorRun, args=(1,0,1,1000,))
            motor1.start()
            motor1.join()
            s1 = self.tcrt5000.readTCRT5000S1()
        # 多走几个脉冲，确保待会测量数据的准确性
        count = 200 
        while count>0:
            motor1 = threading.Thread(target=self.motorRun, args=(1,0,1,1000,))
            motor1.start()
            motor1.join()
            count = count - 1

        # 控制机械臂来回摆动，记录脉冲数
        direction = 1
        each_pulse_count = 0
        total_pulse_count = 0
        #来回3遍，每次两边多走100个脉冲。
        for i in range(6):
            s1 = self.tcrt5000.readTCRT5000S1()
            while s1 == 0:
                motor = threading.Thread(target=self.motorRun, args=(1,direction,1,1000,))
                motor.start()
                motor.join()
                s1 = self.tcrt5000.readTCRT5000S1()
            while s1 == 1:
                each_pulse_count = each_pulse_count + 1
                motor = threading.Thread(target=self.motorRun, args=(1,direction,1,1000,))
                motor.start()
                motor.join()
                s1 = self.tcrt5000.readTCRT5000S1()
            count = 200 
            while count>0:
                motor = threading.Thread(target=self.motorRun, args=(1,direction,1,1000,))
                motor.start()
                motor.join()
                count = count - 1
            if direction == 1:
                direction = 0
            else:
                direction = 1
            total_pulse_count = total_pulse_count + each_pulse_count
            each_pulse_count = 0
            time.sleep(0.5)
        while s1 == 0:
            motor1 = threading.Thread(target=self.motorRun, args=(1,1,1,1000,))
            motor1.start()
            motor1.join()
            s1 = self.tcrt5000.readTCRT5000S1()
        half_pulse_count = total_pulse_count / 2 / 6
        while half_pulse_count>0:
            motor1 = threading.Thread(target=self.motorRun, args=(1, 1, 1, 1000,))
            motor1.start()
            motor1.join()
            half_pulse_count = half_pulse_count - 1
        return (total_pulse_count / 2 / 6)
    def gotoMidZeroPoint2(self):
        # 确保机械臂在零点的上边
        s2 = self.tcrt5000.readTCRT5000S2()
        while s2 == 1:
            motor2 = threading.Thread(target=self.motorRun, args=(2,0,1,1000,))
            motor2.start()
            motor2.join()
            s2 = self.tcrt5000.readTCRT5000S2()
        # 多走几个脉冲，确保待会测量数据的准确性
        count = 50 
        while count>0:
            motor2 = threading.Thread(target=self.motorRun, args=(2,0,1,1000,))
            motor2.start()
            motor2.join()
            count = count - 1
        # 控制机械臂来回摆动，记录脉冲数
        direction = 1
        each_pulse_count = 0
        total_pulse_count = 0
        #来回3遍，每次两边多走100个脉冲。
        for i in range(6):
            s2 = self.tcrt5000.readTCRT5000S2()
            while s2 == 0:
                motor = threading.Thread(target=self.motorRun, args=(2,direction,1,1000,))
                motor.start()
                motor.join()
                s2 = self.tcrt5000.readTCRT5000S2()
            while s2 == 1:
                each_pulse_count = each_pulse_count + 1
                motor = threading.Thread(target=self.motorRun, args=(2,direction,1,1000,))
                motor.start()
                motor.join()
                s2 = self.tcrt5000.readTCRT5000S2()
            count = 50 
            while count>0:
                motor = threading.Thread(target=self.motorRun, args=(2,direction,1,1000,))
                motor.start()
                motor.join()
                count = count - 1
            if direction == 1:
                direction = 0
            else:
                direction = 1
            total_pulse_count = total_pulse_count + each_pulse_count
            each_pulse_count = 0
            time.sleep(0.5)
        while s2 == 0:
            motor2 = threading.Thread(target=self.motorRun, args=(2,1,1,1000,))
            motor2.start()
            motor2.join()
            s2 = self.tcrt5000.readTCRT5000S2()
        half_pulse_count = total_pulse_count / 2 / 6
        while half_pulse_count>0:
            motor2 = threading.Thread(target=self.motorRun, args=(2, 1, 1, 1000,))
            motor2.start()
            motor2.join()
            half_pulse_count = half_pulse_count - 1
        return (total_pulse_count / 2 / 6)
    def gotoMidZeroPoint3(self):
        # 确保机械臂在零点的上边
        s3 = self.tcrt5000.readTCRT5000S3()
        while s3 == 1:
            motor3 = threading.Thread(target=self.motorRun, args=(3,1,1,1000,))
            motor3.start()
            s3 = self.tcrt5000.readTCRT5000S3()
        # 多走几个脉冲，确保待会测量数据的准确性
        count = 50 
        while count>0:
            motor3 = threading.Thread(target=self.motorRun, args=(3,1,1,1000,))
            motor3.start()
            motor3.join()
            count = count - 1
        # 控制机械臂来回摆动，记录脉冲数
        direction = 0
        each_pulse_count = 0
        total_pulse_count = 0
        #来回3遍，每次两边多走100个脉冲。
        for i in range(6):
            s3 = self.tcrt5000.readTCRT5000S3()
            while s3 == 0:
                motor = threading.Thread(target=self.motorRun, args=(3,direction,1,1000,))
                motor.start()
                motor.join()
                s3 = self.tcrt5000.readTCRT5000S3()
            while s3 == 1:
                each_pulse_count = each_pulse_count + 1
                motor = threading.Thread(target=self.motorRun, args=(3,direction,1,1000,))
                motor.start()
                motor.join()
                s3 = self.tcrt5000.readTCRT5000S3()
            count = 50 
            while count>0:
                motor = threading.Thread(target=self.motorRun, args=(3,direction,1,1000,))
                motor.start()
                motor.join()
                count = count - 1
            if direction == 1:
                direction = 0
            else:
                direction = 1
            total_pulse_count = total_pulse_count + each_pulse_count
            each_pulse_count = 0
            time.sleep(0.5)
        while s3 == 0:
            motor3 = threading.Thread(target=self.motorRun, args=(3,0,1,1000,))
            motor3.start()
            motor3.join()
            s3 = self.tcrt5000.readTCRT5000S3()
        half_pulse_count = total_pulse_count / 2 / 6
        while half_pulse_count>0:
            motor3 = threading.Thread(target=self.motorRun, args=(3, 0, 1, 1000,))
            motor3.start()
            motor3.join()
            half_pulse_count = half_pulse_count - 1
        return (total_pulse_count / 2 / 6)
    def gotoZeroPoint(self):        
        motor2 = threading.Thread(target=self.motorRun, args=(2,0,400,1000,))
        motor3 = threading.Thread(target=self.motorRun, args=(3,1,270,1000,))
        motor2.start()
        motor3.start()
        motor2.join()  
        motor3.join()  
        s2 = self.tcrt5000.readTCRT5000S2()                      # 获取传感器2的状态
        s3 = self.tcrt5000.readTCRT5000S3()                      # 获取传感器3的状态
        while s2 == 0 or s3 == 0:                                # 只要任一传感器不在零点处，开始校准2、3电机零点位置
            if s2==0 and s3==0:                                  # 如果两个电机都不在零点
                motor2 = threading.Thread(target=self.motorRun, args=(2,1,1,1000,))# 控制2号电机逆时针转动，16细分，1个脉冲信号，脉冲频率1200Hz。
                motor3 = threading.Thread(target=self.motorRun, args=(3,0,1,1000,))# 控制3号电机顺时针转动，16细分，1个脉冲信号，脉冲频率1200Hz。
                motor2.start()
                motor3.start()
                motor2.join()  
                motor3.join()    
            elif s2==1 and s3==0:                                # 如果2号电机已经到达零点，3号电机仍未到达零点位置
                motor3 = threading.Thread(target=self.motorRun, args=(3,0,1,1000,))
                motor3.start()
                motor3.join()  
            elif s2==0 and s3==1:                                # 如果3号电机已经到达零点，2号电机仍未到达零点位置
                motor2 = threading.Thread(target=self.motorRun, args=(2,1,1,1000,))
                motor2.start()
                motor2.join()  
            s2 = self.tcrt5000.readTCRT5000S2()                  # 刷新传感器2的状态
            s3 = self.tcrt5000.readTCRT5000S3()                  # 刷新传感器3的状态
        
        s1 = self.tcrt5000.readTCRT5000S1()
        i = 0 
        direction = 1
        while s1 == 0:
            i = i + 1
            motor1 = threading.Thread(target=self.motorRun, args=(1,direction,1,1000,))
            motor1.start()
            motor1.join()
            s1 = self.tcrt5000.readTCRT5000S1()                  # 刷新传感器1的状态
            msx = self.readA4988Msx()
            if i > (200 * 3 * msx):
                direction = 0
        pulse1 = self.gotoMidZeroPoint1()
        pulse2 = self.gotoMidZeroPoint2()
        pulse3 = self.gotoMidZeroPoint3()
        pulse = [pulse1,pulse2,pulse3]
        #print("stepmotor.py,", pulse)
        self.lastAngle = self.zeroAngle.copy()
        return pulse
    def gotoZeroPointNoAdjust(self, pulse_count):   
        motor2 = threading.Thread(target=self.motorRun, args=(2,0,400,1000,))
        motor3 = threading.Thread(target=self.motorRun, args=(3,1,50,1000,))
        motor2.start()
        motor3.start()
        motor2.join()  
        motor3.join()  
        s2 = self.tcrt5000.readTCRT5000S2()                      # 获取传感器2的状态
        s3 = self.tcrt5000.readTCRT5000S3()                      # 获取传感器3的状态
        while s2 == 0 or s3 == 0:                                # 只要任一传感器不在零点处，开始校准2、3电机零点位置
            if s2==0 and s3==0:                                  # 如果两个电机都不在零点
                motor2 = threading.Thread(target=self.motorRun, args=(2,1,1,16000,))# 控制2号电机逆时针转动，16细分，1个脉冲信号，脉冲频率1200Hz。
                motor3 = threading.Thread(target=self.motorRun, args=(3,0,1,16000,))# 控制3号电机顺时针转动，16细分，1个脉冲信号，脉冲频率1200Hz。
                motor2.start()
                motor3.start()
                motor2.join()  
                motor3.join()    
            elif s2==1 and s3==0:                                # 如果2号电机已经到达零点，3号电机仍未到达零点位置
                motor3 = threading.Thread(target=self.motorRun, args=(3,0,1,16000,))
                motor3.start()
                motor3.join()  
            elif s2==0 and s3==1:                                # 如果3号电机已经到达零点，2号电机仍未到达零点位置
                motor2 = threading.Thread(target=self.motorRun, args=(2,1,1,16000,))
                motor2.start()
                motor2.join()  
            s2 = self.tcrt5000.readTCRT5000S2()                  # 刷新传感器2的状态
            s3 = self.tcrt5000.readTCRT5000S3()                  # 刷新传感器3的状态
        s1 = self.tcrt5000.readTCRT5000S1()
        i = 0 
        direction = 1
        while s1 == 0:
            i = i + 1
            motor1 = threading.Thread(target=self.motorRun, args=(1,direction,1,16000,))
            motor1.start()
            motor1.join()
            s1 = self.tcrt5000.readTCRT5000S1()                  # 刷新传感器1的状态
            if s1 == 1:
                time.sleep(0.02)
                s1 = self.tcrt5000.readTCRT5000S1()
            msx = self.readA4988Msx()
            if i > (200 * 3 * msx):
                direction = 0
        s1 = self.tcrt5000.readTCRT5000S1()
        while s1 == 1:
            motor1 = threading.Thread(target=self.motorRun, args=(1,0,1,1000,))
            motor1.start()
            motor1.join()
            s1 = self.tcrt5000.readTCRT5000S1()
            if s1 == 0:
                time.sleep(0.02)
                s1 = self.tcrt5000.readTCRT5000S1()
        s2 = self.tcrt5000.readTCRT5000S2()
        while s2 == 1:
            motor2 = threading.Thread(target=self.motorRun, args=(2,0,1,1000,))
            motor2.start()
            motor2.join()
            s2 = self.tcrt5000.readTCRT5000S2()
            if s2 == 0:
                time.sleep(0.02)
                s2 = self.tcrt5000.readTCRT5000S2()
        s3 = self.tcrt5000.readTCRT5000S3()
        while s3 == 1:
            motor3 = threading.Thread(target=self.motorRun, args=(3,1,1,1000,))
            motor3.start()
            motor3.join()
            s3 = self.tcrt5000.readTCRT5000S3()
            if s3 == 0:
                time.sleep(0.02)
                s3 = self.tcrt5000.readTCRT5000S3()
        time.sleep(0.5)
        half_pulse_count = pulse_count[0]
        while half_pulse_count>0:
            motor1 = threading.Thread(target=self.motorRun, args=(1, 1, 1, 1000,))
            motor1.start()
            motor1.join()
            half_pulse_count = half_pulse_count - 1
        half_pulse_count = pulse_count[1]
        while half_pulse_count>0:
            motor2 = threading.Thread(target=self.motorRun, args=(2, 1, 1, 1000,))
            motor2.start()
            motor2.join()
            half_pulse_count = half_pulse_count - 1
        half_pulse_count = pulse_count[2]   
        while half_pulse_count>0:
            motor3 = threading.Thread(target=self.motorRun, args=(3, 0, 1, 1000,))
            motor3.start()
            motor3.join()
            half_pulse_count = half_pulse_count - 1
        self.lastAngle = self.zeroAngle.copy()
    
    def pulseCountToAngle(self, pulse_count):
        a4988Pll = self.readA4988Msx()
        angle = pulse_count * 360 / 6 / 200 / a4988Pll
        return angle
    def angleToPulseCount(self, angle):
        a4988Pll = self.readA4988Msx()
        if angle == 0:
            pulse_count = 0
        else:
            pulse_count = (angle / 360) * 6 * 200 * a4988Pll
        return pulse_count
    def angleToStepMotorParameter(self, targetAngle):
        valueAngle = [(self.lastAngle[i] - targetAngle[i]) for i in range(3)] # 计算角度差值
        direction = [0,0,0]                                                   # 定义个变量，用来存储步进电机转动方向
        pulse_count = [0,0,0]                                                 # 定义个变量，用来存储步进电机转动脉冲数
        for i in range(3):                                                    # 逐个处理角度差值
            if valueAngle[i] >= 0:                                            # 如果角度差值是个正数
                direction[i] = 0                                              # 转动方向为顺时钟方向
            else:                                                             # 如果角度差值是个负数
                direction[i] = 1                                              # 转动方向为逆时针方向
            pulse_count[i] = self.angleToPulseCount(math.fabs(valueAngle[i])) # 将角度转化为脉冲数
        return direction, pulse_count                                         # 返回电机转动方向和脉冲数  

    def moveStepMotorToTargetAngle(self, targetAngle):
        direction, pulse_count = self.angleToStepMotorParameter(targetAngle)                          # 计算三个电机的转动方向和脉冲数
        self.lastAngle = targetAngle.copy()
        pulse_int_value = [0,0,0]                                                                     # 定义个变量用来存储每次发送给步进电机的脉冲数
        for i in range(3):                                                                            # 逐个计算脉冲数和脉冲余量
            if direction[i] == self.pulse_margin_dir[i]:                                              # 如果脉冲余量转动方向与上一次相同
                pulse_int_value[i] = round(pulse_count[i] + self.pulse_margin[i])                     # 脉冲整数=脉冲原始值+脉冲余量
                self.pulse_margin[i] = pulse_count[i] + self.pulse_margin[i] - pulse_int_value[i]     # 脉冲余量=脉冲原始值-脉冲整数
            else:                                                                                     # 如果转动方向相反
                pulse_int_value[i] = round(pulse_count[i] - (self.pulse_margin[i]))                   # 脉冲整数=脉冲原始值+(-1*脉冲余量)
                self.pulse_margin[i] = pulse_count[i] + self.pulse_margin[i] - pulse_int_value[i]     # 脉冲余量=脉冲原始值-脉冲整数
        self.pulse_margin_dir = direction.copy()                                                      # 更新脉冲余量方向                                                                                                             
        buflist = pulse_count.copy()  
        buflist.sort(reverse=True)
        maxdata = buflist[0]
        #print("stepmotor.py,", targetAngle, pulse_count, pulse_int_value, self.pulse_margin)
        if maxdata != 0:
            self.motor1 = threading.Thread(target=self.motorRun, args=(1, direction[0], pulse_int_value[0], self.A4988ClkFrequency[0],))
            self.motor2 = threading.Thread(target=self.motorRun, args=(2, direction[1], pulse_int_value[1], self.A4988ClkFrequency[1],))
            self.motor3 = threading.Thread(target=self.motorRun, args=(3, direction[2], pulse_int_value[2], self.A4988ClkFrequency[2],))
            self.motor1.start()
            self.motor2.start()
            self.motor3.start()
            try:
                self.motor1.join()
                self.motor2.join()
                self.motor3.join()
            except:
                #print("Stepmotor.py, Motor thread is False.")
                pass

    def setStepMotorOffsetAngle(self, offsetAngle):
        self.offsetAngle = offsetAngle.copy()
        
if __name__ == '__main__':
    import sys
    os.system("sudo pigpiod")
    motor = StepMotor()
    motor.setA4988Enable(0)
    try:
        if len(sys.argv)!=3:
            while True:
                print("The stepper motor turns in one direction.")
                motor1 = threading.Thread(target=motor.motorRun, args=(1,0,3200,16000,))
                motor2 = threading.Thread(target=motor.motorRun, args=(2,0,3200,16000,))
                motor3 = threading.Thread(target=motor.motorRun, args=(3,0,3200,16000,))
                motor1.start()
                motor2.start()
                motor3.start()
                motor1.join()
                motor2.join()
                motor3.join()
                print("The stepper motor turns in the other direction.")
                motor1 = threading.Thread(target=motor.motorRun, args=(1,1,3200,16000,))
                motor2 = threading.Thread(target=motor.motorRun, args=(2,1,3200,16000,))
                motor3 = threading.Thread(target=motor.motorRun, args=(3,1,3200,16000,))
                motor1.start()
                motor2.start()
                motor3.start()
                motor1.join()
                motor2.join()
                motor3.join()
        elif len(sys.argv)==3:
            motor_number = int(sys.argv[1])
            direction = int(sys.argv[2])
            while True:
                print("The stepper motor turns in one direction:" , direction)
                motor_threading = threading.Thread(target=motor.motorRun, args=(motor_number,direction,3200,16000,))
                motor_threading.start()
                motor_threading.join()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        motor.setA4988Enable(1)


    
    

