# -*- coding: utf-8 -*-
#!/usr/bin/env python

import time  

def get_raspberry_pi_model():  
    try:  
        with open('/proc/cpuinfo', 'r') as f:  
            cpuinfo = f.readlines()  
        for line in cpuinfo:  
            if line.startswith('Model'):  
                model_info = line.strip().split(':')[-1].strip().split("Model")[0].strip()
                return model_info  
        return 'Unknown Raspberry Pi Model'  
    except Exception as e:  
        print(f"Error reading /proc/cpuinfo: {e}")  
        return 'Error Reading' 

pi_model = get_raspberry_pi_model()
if "Pi 5" in pi_model:
    from piolib_servo import PiolibServo
    library_type = "piolib"
else:
    from gpiozero_servo import GpiozeroServo
    library_type = "gpiozero"

class Servo:
    def __init__(self):
        if library_type == "piolib":
            self.servo = PiolibServo()
        else:
            self.servo = GpiozeroServo()
        self.SERVO_PIN = [13, 16, 19, 20, 26]
        
    def constrain(self, value, min, max):
        if value > max:
            value = max
        if value < min:
            value = min
        return value
    
    def setServoAngle(self, index, angle):
        servo_duty = self.servo.setServoAngle(self.SERVO_PIN[index], angle)
        return servo_duty
    def relaxServo(self):
        self.servo.relaxServo()
    
    def servoClose(self):
        self.servo.servoClose()

# Main program logic follows:
if __name__ == '__main__':
    import os
    import sys
    time.sleep(1)
    servo = Servo()
    
    try:
        while True:
            if len(sys.argv)==1:
                for i in range(5):
                    print("Servo index:", i)
                    for j in range(0, 180, 10):
                        servo.setServoAngle(i, j)
                        time.sleep(0.05)
                    for j in range(0, 180, 10):
                        servo.setServoAngle(i, 180-j)
                        time.sleep(0.05)
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
        servo.relaxServo()
        time.sleep(0.5)