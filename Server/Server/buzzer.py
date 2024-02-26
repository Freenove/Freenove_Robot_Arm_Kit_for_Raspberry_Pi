# -*- coding: utf-8 -*-
#!/usr/bin/env python

import pigpio
import time

class Buzzer:
    def __init__(self):
        self.BUZZER_PIN = 21
        self.PwmBuzzer = pigpio.pi()
        self.initBuzzer()
    
    def initBuzzer(self):
        self.PwmBuzzer.set_mode(self.BUZZER_PIN, pigpio.OUTPUT) 
        self.PwmBuzzer.set_PWM_frequency(self.BUZZER_PIN, 2000)
        self.PwmBuzzer.set_PWM_range(self.BUZZER_PIN, 100)
        self.PwmBuzzer.set_PWM_dutycycle(self.BUZZER_PIN, 0)

    def buzzerRun(self, frequency=2000):
        if frequency != 0:
            self.PwmBuzzer.set_PWM_dutycycle(self.BUZZER_PIN, 50)
            self.PwmBuzzer.set_PWM_frequency(self.BUZZER_PIN, frequency)
        else:
            self.PwmBuzzer.set_PWM_dutycycle(self.BUZZER_PIN, 0)
            self.PwmBuzzer.set_PWM_frequency(self.BUZZER_PIN, 0)
            
    def buzzerRunXms(self, frequency=2000, delayms=100, times=1):
        for i in range(times):
            self.buzzerRun(frequency)
            time.sleep(float(delayms/1000))
            self.buzzerRun(0)
            time.sleep(float(delayms/1000))
        self.buzzerRun(0)
            

# Main program logic follows:
if __name__ == '__main__':
    import os
    import sys
    os.system("sudo pigpiod")
    B=Buzzer() 
    try:
        if len(sys.argv)==1:
            B.buzzerRunXms(2000,100,3)     
        elif len(sys.argv)==2:
            B.buzzerRunXms(int(sys.argv[1]),100,3)   
        elif len(sys.argv)==3:
            B.buzzerRunXms(int(sys.argv[1]),int(sys.argv[2]),3)  
        elif len(sys.argv)==4:
            B.buzzerRunXms(int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]))   
        elif len(sys.argv)>4:
            print("Too many parameters.")
            B.buzzerRunXms(1000,300,2)  
    except KeyboardInterrupt:
        B.buzzerRun(0)
        print('quit')