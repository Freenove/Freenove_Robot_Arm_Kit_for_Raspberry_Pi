# -*- coding: utf-8 -*-
#!/usr/bin/env python

import pigpio
import time

class Servo:
    def __init__(self):
        self.SERVO_CHANNEL_PIN = [13,16,19,20,26] 
        self.servo_index = -1
        
        self.PwmServo = pigpio.pi()
        self.initServo(self.servo_index)

    def map(self, value, fromLow, fromHigh, toLow, toHigh):
        return (toHigh-toLow)*(value-fromLow) / (fromHigh-fromLow) + toLow
    
    def constrain(self, value, min, max):
        if value > max:
            value = max
        if value < min:
            value = min
        return value
    
    def initServo(self, index):
        if self.servo_index != index:
            self.servo_index = self.constrain(index, 0, len(self.SERVO_CHANNEL_PIN))
            mode = self.PwmServo.get_mode(self.SERVO_CHANNEL_PIN[self.servo_index]) 
            freq = self.PwmServo.get_PWM_frequency(self.SERVO_CHANNEL_PIN[self.servo_index])
            pwm_range = self.PwmServo.get_PWM_range(self.SERVO_CHANNEL_PIN[self.servo_index])
            if (mode != pigpio.OUTPUT) or (freq != 50) or (pwm_range != 20000):
                self.PwmServo.set_mode(self.SERVO_CHANNEL_PIN[self.servo_index],pigpio.OUTPUT) 
                self.PwmServo.set_PWM_frequency(self.SERVO_CHANNEL_PIN[self.servo_index],50)
                self.PwmServo.set_PWM_range(self.SERVO_CHANNEL_PIN[self.servo_index], 20000)
    
    def setServoAngle(self, index, angle):
        if index < len(self.SERVO_CHANNEL_PIN):
            self.initServo(index)
            angle = self.constrain(angle, 0, 180)
            servo_duty = 500+(2000/180)*angle
            self.PwmServo.set_PWM_dutycycle(self.SERVO_CHANNEL_PIN[self.servo_index], servo_duty)
            return servo_duty
        
    def relaxServo(self, index):
        if index < len(self.SERVO_CHANNEL_PIN):
            self.PwmServo.set_PWM_dutycycle(self.SERVO_CHANNEL_PIN[self.servo_index], 20000)

    


# Main program logic follows:
if __name__ == '__main__':
    import os
    import sys
    os.system("sudo pigpiod")
    servo = Servo()
    print("")
    try:
        while True:
            if len(sys.argv)==1:
                for j in range(180):
                    for i in range(5):
                        servo.setServoAngle(i, j)
                    time.sleep(0.01)
                for j in range(180):
                    for i in range(5):  
                        servo.setServoAngle(i, 180-j)
                    time.sleep(0.01)
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
        servo.PwmServo.stop()
        print ("\nEnd of program")
        
       