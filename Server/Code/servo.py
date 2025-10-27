# -*- coding: utf-8 -*-
#!/usr/bin/env python

from gpiozero import PWMOutputDevice  
import time  
import subprocess

class Servo:
    def __init__(self):
        self.SERVO_PIN = [13,16,19,20,26] 
        self.servo = [PWMOutputDevice(pin, initial_value=0) for pin in self.SERVO_PIN]  

    def constrain(self, value, min, max):
        if value > max:
            value = max
        if value < min:
            value = min
        return value
    
    def setServoAngle(self, index, angle):
        if index < len(self.SERVO_PIN):
            angle = self.constrain(angle, 0, 180)
            servo_duty = 500+(2000/180)*angle
            self.servo[index].frequency = 50 
            self.servo[index].value = servo_duty/20000
            return servo_duty
    def relaxServo(self, index):
        self.servo[index].off()
    
    def servoClose(self):
        [self.servo[i].close() for i in range(len(self.SERVO_PIN))]

class Freenove_Servo:
    def __init__(self):
        self.SERVO_PIN = 13

    def constrain(self, value, min, max):
        if value > max:
            value = max
        if value < min:
            value = min
        return value
    
    def setPwm(self, pin, period, duty_cycle):
        script_path = './Freenove_PWM.sh'  
        command = [script_path, str(pin), str(period), str(duty_cycle)]  
        result = subprocess.run(command, check=True, text=True, capture_output=True)  
        if result.stderr:  
            print("Error:", result.stderr)  
        #if result.stdout:  
        #    print("Output:", result.stdout)  
    
    def setServoAngle(self, index, angle):
        angle = self.constrain(angle, 0, 180)
        servo_duty = 500+(2000/180)*angle
        self.setPwm(self.SERVO_PIN, 20000000, round(servo_duty*1000)) #12,13,14,15,18,19
        return servo_duty
    
    def relaxServo(self, index):
        self.setPwm(self.SERVO_PIN, 20000000, 0)

    def servoClose(self):
        self.relaxServo()

# Main program logic follows:
if __name__ == '__main__':
    import os
    import sys
    time.sleep(1)
    servo = Servo()
    #servo = Freenove_Servo()
    
    try:
        while True:
            if len(sys.argv)==1:
                for j in range(0, 180, 10):
                    for i in range(5):
                        servo.setServoAngle(i, j)
                    time.sleep(0.1)
                for j in range(0, 180, 10):
                    for i in range(5):  
                        servo.setServoAngle(i, 180-j)
                    time.sleep(0.1)
            elif len(sys.argv)==2:
                index = servo.constrain(int(sys.argv[1]), 0, 4)
                servo.setServoAngle(index, 90)
                time.sleep(0.1)
            elif len(sys.argv)==3:
                index = servo.constrain(int(sys.argv[1]), 0, 4)
                angle = servo.constrain(int(sys.argv[2]), 0, 180)
                servo.setServoAngle(index, angle)
                time.sleep(0.1)
            
    except KeyboardInterrupt:
        for i in range(5):
            servo.relaxServo(i)
        time.sleep(0.5)