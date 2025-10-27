# -*- coding: utf-8 -*-
#!/usr/bin/env python

from gpiozero import DigitalInputDevice  

class TCRT5000: 
    def __init__(self):
        self.TCRT5000_PIN = [8,11,7]
        self.sensors = [DigitalInputDevice(pin, pull_up=False, bounce_time=1) for pin in self.TCRT5000_PIN] 

    def readTCRT5000S1(self):
        return 1 if self.sensors[0].is_active else 0
    def readTCRT5000S2(self):
        return 1 if self.sensors[1].is_active else 0
    def readTCRT5000S3(self):
        return 1 if self.sensors[2].is_active else 0
    def readTCRT5000ALL(self):
        s1 = self.readTCRT5000S1()
        s2 = self.readTCRT5000S2()
        s3 = self.readTCRT5000S3()
        return [s1,s2,s3]
    
    def stopTCRT5000ALL(self):
        [self.sensors[i].close() for i in range(len(self.sensors))]
    
if __name__ == '__main__':
    import os
    import time
    current_state = [0,0,0]
    sensor_count = [0,0,0]
    sensor = TCRT5000()
    try:
        while True:
            sensor_state = sensor.readTCRT5000ALL()
            print("sensor_state:", sensor_state)
            if current_state[0] != sensor_state[0]:
                time.sleep(0.1)
                sensor_state = sensor.readTCRT5000ALL()
                if current_state[0] != sensor_state[0]:
                    current_state[0] = sensor_state[0]
                    sensor_count[0] = sensor_count[0] + 1
                if sensor_count[0] >= 2:
                    sensor_count[0] = 0
                    print("Sensor 1 is triggered.")
            elif current_state[1] != sensor_state[1]:
                time.sleep(0.1)
                sensor_state = sensor.readTCRT5000ALL()
                if current_state[1] != sensor_state[1]:
                    current_state[1] = sensor_state[1]
                    sensor_count[1] = sensor_count[1] + 1
                if sensor_count[1] >= 2:
                    sensor_count[1] = 0
                    print("Sensor 2 is triggered.")
            elif current_state[2] != sensor_state[2]:
                time.sleep(0.1)
                sensor_state = sensor.readTCRT5000ALL()
                if current_state[2] != sensor_state[2]:
                    current_state[2] = sensor_state[2]
                    sensor_count[2] = sensor_count[2] + 1
                if sensor_count[2] >= 2:
                    sensor_count[2] = 0
                    print("Sensor 3 is triggered.")
            else:
                time.sleep(0.3)
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        pass


    
    

