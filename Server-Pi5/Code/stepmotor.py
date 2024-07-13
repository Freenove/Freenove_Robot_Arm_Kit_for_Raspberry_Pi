  # -*- coding: utf-8 -*-
#!/usr/bin/env python

from gpiozero import OutputDevice  
import time
import math
import threading
import sensor
import messageThread

class StepMotor:
    def __init__(self):
        self.turn_direction = 1                                 
        self.A4988_EN = 9                                       
        self.A4988_MSX = [10, 24, 23]                           
        self.A4988_DIR = [14, 15, 27]                         
        self.A4988_STEP = [4, 17, 22]                       
        self.tcrt5000 = sensor.TCRT5000()                        
        self.initA4988()                                         
        self.setA4988Enable(1)                               
        self.setA4988MsxMode(5)                                
        self.A4988MsxModeValue = 5                              
        self.A4988ClkFrequency = [1000,1000,1000]             
        self.pulse_margin = [0,0,0]                             
        self.pulse_margin_dir = [0,0,0]                         
        self.zeroAngle = [90, 110, -12]                          
        self.lastAngle = self.zeroAngle.copy() 

    def initA4988(self):
        self.MODULE_EN = OutputDevice(self.A4988_EN, initial_value=False) 
        self.MODULE_MS1 = OutputDevice(self.A4988_MSX[0], initial_value=False) 
        self.MODULE_MS2 = OutputDevice(self.A4988_MSX[1], initial_value=False) 
        self.MODULE_MS3 = OutputDevice(self.A4988_MSX[2], initial_value=False) 
        self.MODULE_DIR_1 = OutputDevice(self.A4988_DIR[0], initial_value=False) 
        self.MODULE_DIR_2 = OutputDevice(self.A4988_DIR[1], initial_value=False) 
        self.MODULE_DIR_3 = OutputDevice(self.A4988_DIR[2], initial_value=False) 
        self.MODULE_STEP_1 = OutputDevice(self.A4988_STEP[0], initial_value=False) 
        self.MODULE_STEP_2 = OutputDevice(self.A4988_STEP[1], initial_value=False) 
        self.MODULE_STEP_3 = OutputDevice(self.A4988_STEP[2], initial_value=False) 

    def stopA4988(self):
        self.MODULE_EN.close()
        self.MODULE_MS1.close()
        self.MODULE_MS2.close()
        self.MODULE_MS3.close()
        self.MODULE_DIR_1.close()
        self.MODULE_DIR_2.close()
        self.MODULE_DIR_3.close()
        self.MODULE_STEP_1.close()
        self.MODULE_STEP_2.close()
        self.MODULE_STEP_3.close()

    def setPinState(self, pin, state):
        if state == 1:
            pin.on()
        elif state == 0:
            pin.off()

    def setA4988Enable(self, enable):
        self.setPinState(self.MODULE_EN, enable)

    def setA4988MSx(self, ms1, ms2, ms3):
        self.setPinState(self.MODULE_MS1, ms1)
        self.setPinState(self.MODULE_MS2, ms2)
        self.setPinState(self.MODULE_MS3, ms3)
      
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
        turn_dir = direction
        if self.turn_direction == 1:
            if direction == 1:
                turn_dir = 0
            elif direction == 0:
                turn_dir = 1
        pulse_period = 1 / pulse_frequency                      
        half_pulse_period = pulse_period / 2                          
        if motor_number == 1:  
            self.setPinState(self.MODULE_DIR_3, turn_dir)                                      
            for i in range(pulse_count):
                self.setPinState(self.MODULE_STEP_3, 1)      
                self.myDelay(half_pulse_period)
                self.setPinState(self.MODULE_STEP_3, 0)   
                self.myDelay(half_pulse_period)   
        elif motor_number == 2:
            self.setPinState(self.MODULE_DIR_2, turn_dir)     
            for i in range(pulse_count):
                self.setPinState(self.MODULE_STEP_2, 1)  
                self.myDelay(half_pulse_period)
                self.setPinState(self.MODULE_STEP_2, 0)  
                self.myDelay(half_pulse_period)   
        elif motor_number == 3:
            self.setPinState(self.MODULE_DIR_1, turn_dir)     
            for i in range(pulse_count):
                self.setPinState(self.MODULE_STEP_1, 1)  
                self.myDelay(half_pulse_period)
                self.setPinState(self.MODULE_STEP_1, 0)  
                self.myDelay(half_pulse_period)      

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
        valueAngle = [(self.lastAngle[i] - targetAngle[i]) for i in range(3)] 
        direction = [0,0,0]                                                   
        pulse_count = [0,0,0]                                                
        for i in range(3):                                                   
            if valueAngle[i] >= 0:                                            
                direction[i] = 0                                              
            else:                                                             
                direction[i] = 1                                             
            pulse_count[i] = self.angleToPulseCount(math.fabs(valueAngle[i])) 
        return direction, pulse_count                                         

    def gotoMidSensorPoint1(self):
        self.motorRun(1,0,200,1000)
        direction = 1
        each_pulse_count = 0
        total_pulse_count = 0
        for i in range(6):
            s1 = self.tcrt5000.readTCRT5000S1()
            while s1 == 0:
                self.motorRun(1,direction,1,1000)
                s1 = self.tcrt5000.readTCRT5000S1()
            while s1 == 1 or each_pulse_count < 50:
                each_pulse_count = each_pulse_count + 1
                self.motorRun(1,direction,1,1000)
                s1 = self.tcrt5000.readTCRT5000S1()
            self.motorRun(1,direction,200,1000)
            if direction == 1:
                direction = 0
            else:
                direction = 1
            total_pulse_count = total_pulse_count + each_pulse_count
            each_pulse_count = 0
            time.sleep(0.5)
        s1 = self.tcrt5000.readTCRT5000S1() 
        while s1 == 0:
            self.motorRun(1,1,1,1000)
            s1 = self.tcrt5000.readTCRT5000S1()
        half_pulse_count = total_pulse_count / 2 / 6
        self.motorRun(1, 1, round(half_pulse_count), 1000)
        return (total_pulse_count / 2 / 6)
    def gotoMidSensorPoint2(self):
        s2 = self.tcrt5000.readTCRT5000S2()
        while s2 == 1:
            self.motorRun(2,0,1,1000)
            s2 = self.tcrt5000.readTCRT5000S2()
        self.motorRun(2,0,50,1000)
        direction = 1
        each_pulse_count = 0
        total_pulse_count = 0
        for i in range(6):
            s2 = self.tcrt5000.readTCRT5000S2()
            while s2 == 0:
                self.motorRun(2,direction,1,1000)
                s2 = self.tcrt5000.readTCRT5000S2()
            while s2 == 1 or each_pulse_count < 50:
                each_pulse_count = each_pulse_count + 1
                self.motorRun(2,direction,1,1000)
                s2 = self.tcrt5000.readTCRT5000S2()
            self.motorRun(2,direction,50,1000)
            if direction == 1:
                direction = 0
            else:
                direction = 1
            total_pulse_count = total_pulse_count + each_pulse_count
            each_pulse_count = 0
            time.sleep(0.5)
        while s2 == 0:
            self.motorRun(2,1,1,1000)
            s2 = self.tcrt5000.readTCRT5000S2()
        half_pulse_count = total_pulse_count / 2 / 6
        self.motorRun(2, 1, round(half_pulse_count), 1000) 
        return (total_pulse_count / 2 / 6)
    def gotoMidSensorPoint3(self):
        s3 = self.tcrt5000.readTCRT5000S3()
        while s3 == 1:
            self.motorRun(3,1,1,1000)
            s3 = self.tcrt5000.readTCRT5000S3()
        self.motorRun(3,1,50,1000)
        direction = 0
        each_pulse_count = 0
        total_pulse_count = 0
        for i in range(6):
            s3 = self.tcrt5000.readTCRT5000S3()
            while s3 == 0:
                self.motorRun(3,direction,1,1000)
                s3 = self.tcrt5000.readTCRT5000S3()
            while s3 == 1 or each_pulse_count < 50:
                each_pulse_count = each_pulse_count + 1
                self.motorRun(3,direction,1,1000)
                s3 = self.tcrt5000.readTCRT5000S3()
            self.motorRun(3,direction,50,1000)
            if direction == 1:
                direction = 0
            else:
                direction = 1
            total_pulse_count = total_pulse_count + each_pulse_count
            each_pulse_count = 0
            time.sleep(0.5)
        while s3 == 0:
            self.motorRun(3,0,1,1000)
            s3 = self.tcrt5000.readTCRT5000S3()
        half_pulse_count = total_pulse_count / 2 / 6
        self.motorRun(3, 0, round(half_pulse_count), 1000)
        return (total_pulse_count / 2 / 6)
    def caliSensorPoint(self):        
        self.motorRun(2,0,400,1000)
        self.motorRun(3,1,270,1000) 
        s2 = self.tcrt5000.readTCRT5000S2()                    
        s3 = self.tcrt5000.readTCRT5000S3()                    
        while s2 == 0 or s3 == 0:                                
            if s2==0 and s3==0:                                
                self.motorRun(2,1,1,1000)
                self.motorRun(3,0,1,1000)  
            elif s2==1 and s3==0:                               
                self.motorRun(3,0,1,1000) 
            elif s2==0 and s3==1:                               
                self.motorRun(2,1,1,1000)
            s2 = self.tcrt5000.readTCRT5000S2()                 
            s3 = self.tcrt5000.readTCRT5000S3()                  
        i = 0 
        direction = 1
        s1 = self.tcrt5000.readTCRT5000S1()
        msx = self.readA4988Msx()
        semicyclePluse = 200 * 3 * msx
        while s1 == 0:
            i = i + 1
            self.motorRun(1,direction,1,1000)
            s1 = self.tcrt5000.readTCRT5000S1()                 
            if i > semicyclePluse:
                direction = 0
        if direction == 0:
            while s1 == 1:
                self.motorRun(1,direction,1,1000)
                s1 = self.tcrt5000.readTCRT5000S1()                 
        pulse1 = self.gotoMidSensorPoint1()
        pulse2 = self.gotoMidSensorPoint2()
        pulse3 = self.gotoMidSensorPoint3()
        pulse = [pulse1,pulse2,pulse3]
        #print("stepmotor.py,", pulse)
        self.lastAngle = self.zeroAngle.copy()
        return pulse
    def gotoSensorPoint(self, pulse_count):   
        self.motorRun(2,0,400,1000)          
        self.motorRun(3,1,270,1000)         
        s2 = self.tcrt5000.readTCRT5000S2()                     
        s3 = self.tcrt5000.readTCRT5000S3()                      
        while s2 == 0 or s3 == 0:                               
            if s2==0 and s3==0:                                
                self.motorRun(2,1,1,1000)
                self.motorRun(3,0,1,1000)
            elif s2==1 and s3==0:                              
                self.motorRun(3,0,1,1000)
            elif s2==0 and s3==1:                             
                self.motorRun(2,1,1,1000)
            s2 = self.tcrt5000.readTCRT5000S2()                  
            s3 = self.tcrt5000.readTCRT5000S3()                  
        s1 = self.tcrt5000.readTCRT5000S1()

        i = 0 
        direction = 1
        msx = self.readA4988Msx()
        semicyclePluse = 200 * 3 * msx
        while s1 == 0:
            i = i + 1
            self.motorRun(1, direction, 1, 1000)
            s1 = self.tcrt5000.readTCRT5000S1()                  
            if i > semicyclePluse:
                direction = 0

        s1 = self.tcrt5000.readTCRT5000S1()
        while s1 == 1:
            self.motorRun(1,0,1,1000)
            s1 = self.tcrt5000.readTCRT5000S1()

        s2 = self.tcrt5000.readTCRT5000S2()
        while s2 == 1:
            self.motorRun(2,0,1,1000)
            s2 = self.tcrt5000.readTCRT5000S2()
        s3 = self.tcrt5000.readTCRT5000S3()
        while s3 == 1:
            self.motorRun(3,1,1,1000)
            s3 = self.tcrt5000.readTCRT5000S3()
        time.sleep(0.5)
        half_pulse_count = pulse_count[0]
        self.motorRun(1, 1, round(half_pulse_count), 1000)
        half_pulse_count = pulse_count[1]
        self.motorRun(2, 1, round(half_pulse_count), 1000)
        half_pulse_count = pulse_count[2]  
        self.motorRun(3, 0, round(half_pulse_count), 1000) 
        self.lastAngle = self.zeroAngle.copy()

    def moveStepMotorToTargetAngle(self, targetAngle):
        direction, pulse_count = self.angleToStepMotorParameter(targetAngle)                          
        self.lastAngle = targetAngle.copy()
        pulse_int_value = [0,0,0]                                                                   
        for i in range(3):                                                                          
            if direction[i] == self.pulse_margin_dir[i]:                                       
                pulse_int_value[i] = round(pulse_count[i] + self.pulse_margin[i])                  
                self.pulse_margin[i] = pulse_count[i] + self.pulse_margin[i] - pulse_int_value[i]    
            else:                                                                                    
                pulse_int_value[i] = round(pulse_count[i] - (self.pulse_margin[i]))                   
                self.pulse_margin[i] = pulse_count[i] - self.pulse_margin[i] - pulse_int_value[i]    
        #print("Stepmotor.py, ", pulse_count, pulse_int_value, direction, self.pulse_margin_dir, self.pulse_margin)
        self.pulse_margin_dir = direction.copy()                                                                                                                                                      
        buflist = pulse_count.copy()  
        buflist.sort(reverse=True)
        maxdata = buflist[0]
        
        if maxdata != 0:
            motor1 = threading.Thread(target=self.motorRun, args=(1, direction[0], pulse_int_value[0], self.A4988ClkFrequency[0],))
            motor2 = threading.Thread(target=self.motorRun, args=(2, direction[1], pulse_int_value[1], self.A4988ClkFrequency[1],))
            motor3 = threading.Thread(target=self.motorRun, args=(3, direction[2], pulse_int_value[2], self.A4988ClkFrequency[2],))
            motor1.start()
            motor2.start()
            motor3.start()
            try:
                motor1.join()
                motor2.join()
                motor3.join()
            except:
                #print("Stepmotor.py, Motor thread is False.")
                pass

if __name__ == '__main__':
    import sys
    time.sleep(1)
    motor = StepMotor()
    motor.setA4988Enable(0)
    try:
        if len(sys.argv)!=3:
            while True:
                print("The stepper motor turns in one direction.")
                motor1 = threading.Thread(target=motor.motorRun, args=(1,0,200,1000,))
                motor2 = threading.Thread(target=motor.motorRun, args=(2,0,200,1000,))
                motor3 = threading.Thread(target=motor.motorRun, args=(3,0,200,1000,))
                motor1.start()
                motor2.start()
                motor3.start()
                motor1.join()
                motor2.join()
                motor3.join()
                print("The stepper motor turns in the other direction.")
                motor1 = threading.Thread(target=motor.motorRun, args=(1,1,200,1000,))
                motor2 = threading.Thread(target=motor.motorRun, args=(2,1,200,1000,))
                motor3 = threading.Thread(target=motor.motorRun, args=(3,1,200,1000,))
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
                motor_threading = threading.Thread(target=motor.motorRun, args=(motor_number,direction,3200,1000,))
                motor_threading.start()
                motor_threading.join()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        if len(sys.argv)!=3:
            messageThread.stop_thread(motor1)
            messageThread.stop_thread(motor2)
            messageThread.stop_thread(motor3)
        elif len(sys.argv)==3:
            messageThread.stop_thread(motor_threading)
    finally:
        motor.setA4988Enable(1)
        motor.stopA4988()
        motor.tcrt5000.stopTCRT5000ALL()
        print("Program interrupted.")  

