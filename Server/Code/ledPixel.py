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
    from piolib_ws2812 import WS2812
    library_type = "piolib"
else:
    from rpilib_ws2812 import WS2812
    library_type = "rpilib"

class LedPixel:
    def __init__(self):
        # Create NeoPixel object with appropriate configuration.
        if library_type == "piolib":
            self.strip = WS2812(led_pin=18, led_count=8, order="GRB")
        else: 
            self.strip = WS2812(led_pin=18, led_count=8, order="RGB")
        
        self.animation_states = {}
        self.last_update_time = {}
    
    # Set the lights one by one and display
    def colorWipe(self, color, wait_ms=50, interval_ms=1000):
        if 'colorWipe' not in self.animation_states:
            self.animation_states['colorWipe'] = {
                'step': 0,
                'phase': 0,  # 0: wiping, 1: interval waiting
                'start_time': time.time()
            }
        state = self.animation_states['colorWipe']
        current_time = time.time()
        if state['phase'] == 0:  # wiping phase
            if (current_time - state['start_time']) * 1000 >= wait_ms:
                if state['step'] < self.strip.numPixels():
                    self.strip.setBrightness(255)
                    self.strip.setPixelColor(state['step'], (color[0], color[1], color[2]))
                    self.strip.show()
                    state['step'] += 1
                    state['start_time'] = current_time
                    return True
                else:
                    # Wiping complete, move to interval phase
                    state['phase'] = 1
                    state['start_time'] = current_time
                    return True
        else:  # interval waiting phase
            if (current_time - state['start_time']) * 1000 >= interval_ms:
                # Interval complete, reset for next use
                if 'colorWipe' in self.animation_states:
                    del self.animation_states['colorWipe']
                return False
        return True

    # Custom RGB
    def RGBLed(self, color, wait_ms=100):
        if 'RGBLed' not in self.animation_states:
            self.animation_states['RGBLed'] = {
                'started': False,
                'start_time': time.time()
            }
        state = self.animation_states['RGBLed']
        current_time = time.time()
        if not state['started']:
            self.strip.setBrightness(255)
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, (color[0], color[1], color[2]))
            self.strip.show()
            state['started'] = True
            state['start_time'] = current_time
            return True
        else:
            if (current_time - state['start_time']) * 1000 >= wait_ms:
                # Display time complete, remove state
                if 'RGBLed' in self.animation_states:
                    del self.animation_states['RGBLed']
                return False
        return True

    # Following lights
    def followingLed(self, color, wait_ms=60):
        if 'followingLed' not in self.animation_states:
            self.animation_states['followingLed'] = {
                'step': 0,
                'start_time': time.time()
            }
        state = self.animation_states['followingLed']
        current_time = time.time()
        if (current_time - state['start_time']) * 1000 >= wait_ms:
            self.strip.setBrightness(255)
            ledShow = [(color[0]//8, color[1]//8, color[2]//8),
                    (color[0]//4, color[1]//4, color[2]//4),
                    (color[0]//2, color[1]//2, color[2]//2),
                    (color[0]//1, color[1]//1, color[2]//1)]
            ledNum = self.strip.numPixels()
            state['step'] = state['step'] % ledNum
            for i in range(ledNum):
                self.strip.setPixelColor(i, (0, 0, 0))
            for j in range(len(ledShow)):
                idx = (state['step'] + j) % ledNum
                self.strip.setPixelColor(idx, ledShow[j])
            self.strip.show()
            state['step'] += 1
            state['start_time'] = current_time
            return True
        return True

    # Blink lights
    def blinkLed(self, color, wait_ms=300):
        if 'blinkLed' not in self.animation_states:
            self.animation_states['blinkLed'] = {
                'step': 0,
                'start_time': time.time()
            }
        
        state = self.animation_states['blinkLed']
        current_time = time.time()
        
        if (current_time - state['start_time']) * 1000 >= wait_ms:
            self.strip.setBrightness(255)
            ledNum = self.strip.numPixels()
            
            if state['step'] == 0:
                for i in range(ledNum):
                    self.strip.setPixelColor(i, (color[0], color[1], color[2]))
                self.strip.show()
                state['step'] = 1
                state['start_time'] = current_time
                return True
            else:
                for i in range(ledNum):
                    self.strip.setPixelColor(i, (0, 0, 0))
                self.strip.show()
                state['step'] = 0
                state['start_time'] = current_time
        return True
        
    # Breathing lights      
    def breathLight(self, color, wait_ms=15):
        if 'breathLight' not in self.animation_states:
            self.animation_states['breathLight'] = {
                'step': 0,
                'direction': 1,
                'start_time': time.time()
            }
            
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, (color[0], color[1], color[2]))
        
        state = self.animation_states['breathLight']
        current_time = time.time()
        
        if (current_time - state['start_time']) * 1000 >= wait_ms:
            if state['direction'] == 1:  
                if state['step'] < 100:
                    self.strip.setBrightness(state['step'])
                    self.strip.show()
                    state['step'] += 1
                    state['start_time'] = current_time
                    return True
                else:
                    state['direction'] = -1  
                    state['step'] = 100
            else: 
                if state['step'] > 0:
                    self.strip.setBrightness(state['step'])
                    self.strip.show()
                    state['step'] -= 1
                    state['start_time'] = current_time
                    return True
                else:
                    state['direction'] = 1
                    state['step'] = 0
            state['start_time'] = current_time
        return True
    
    # Rainbow light
    def rainbowCycle(self, wait_ms=3, iterations=1):
        if 'rainbowCycle' not in self.animation_states:
            self.animation_states['rainbowCycle'] = {
                'step': 0,
                'max_steps': 256 * iterations,
                'start_time': time.time()
            }
        state = self.animation_states['rainbowCycle']
        current_time = time.time()
        if (current_time - state['start_time']) * 1000 >= wait_ms:
            if state['step'] < state['max_steps']:
                self.strip.setBrightness(50)
                for i in range(self.strip.numPixels()):
                    color = self.strip.wheel((int(i * 256 / self.strip.numPixels()) + state['step']) & 255)
                    self.strip.setPixelColor(i, color)
                self.strip.show()
                
                state['step'] += 1
                state['start_time'] = current_time
                return True
            else:
                state['step'] = 0
                state['start_time'] = current_time
        return True

    # Gradient rainbow light
    def gradualChange(self, wait_ms=10, iterations=1):
        if 'gradualChange' not in self.animation_states:
            self.animation_states['gradualChange'] = {
                'step': 0,
                'max_steps': 256 * iterations,
                'start_time': time.time()
            }
        state = self.animation_states['gradualChange']
        current_time = time.time()
        
        if (current_time - state['start_time']) * 1000 >= wait_ms:
            if state['step'] < state['max_steps']:
                self.strip.setBrightness(50)
                for i in range(self.strip.numPixels()):
                    color = self.strip.wheel((i + state['step']) & 255)
                    self.strip.setPixelColor(i, color)
                self.strip.show()
                
                state['step'] += 1
                state['start_time'] = current_time
                return True
            else:
                state['step'] = 0
                state['start_time'] = current_time
        
        return True

    # Rotating lights can be customed
    def rotateLed(self, color, number=2, wait_ms=50):
        if 'rotateLed' not in self.animation_states:
            self.animation_states['rotateLed'] = {
                'step': 0,
                'start_time': time.time()
            }
        state = self.animation_states['rotateLed']
        current_time = time.time()
        if (current_time - state['start_time']) * 1000 >= wait_ms:
            self.strip.setBrightness(255)
            ledNum = self.strip.numPixels()
            state['step'] = state['step'] % ledNum
            for i in range(ledNum):
                self.strip.setPixelColor(i, (0, 0, 0))
            for j in range(number):
                idx = (state['step'] + j * (ledNum // number)) % ledNum
                self.strip.setPixelColor(idx, (color[0], color[1], color[2]))
            self.strip.show()
            state['step'] += 1
            state['start_time'] = current_time
            return True
        return True
    
    # The colored light displays the function, which needs to be executed using a thread loop. data contains four parameters, 0:mode, 1:R, 2:G, and 3:B
    def light(self, data):
        self.LedMod = data[0]
        self.color = data[1:4]
        if self.LedMod == 0:                                                    # close
            self.color = [0, 0, 0]
            self.colorWipe(self.color)
        elif self.LedMod == 1:                                                  # RGB
            self.RGBLed(self.color)
        elif self.LedMod == 2:                                                  # Following
            self.followingLed(self.color)
        elif self.LedMod == 3:                                                  # Blink
            self.blinkLed(self.color)
        elif self.LedMod == 4:                                                  # Breathing
            self.breathLight(self.color)
        elif self.LedMod == 5:                                                  # Rainbow
            self.rainbowCycle()
        elif self.LedMod == 6:                                                  # Gradual
            self.gradualChange()
        elif self.LedMod == 7:                                                  # The two lights rotate symmetrically
            self.rotateLed(self.color, 2, 50)
        elif self.LedMod == 8:                                                  # The four lights rotate symmetrically
            self.rotateLed(self.color, 4, 100)                                   
        elif self.LedMod >= 9 or self.LedMod < 0:
            self.LedMod = 0
            print("parameter error! Press Ctrl+c to exit and re-enter the parameters, please.")
            time.sleep(1)

# Main program logic follows:
if __name__ == '__main__':
    import sys
    
    led = LedPixel()   
    led.strip.setBrightness(255)
    print ('Program is starting ... ')
    
    try:
        if len(sys.argv) < 5 and len(sys.argv) >= 2:
            strParameter = sys.argv[1:]
            intParameter = [int(strParameter[i]) for i in range(len(strParameter))]
            parameter = [intParameter[0], 128, 0, 0]
            while True:
                led.light(parameter)
        elif len(sys.argv) < 2:
            print("Enter a parameter, 'sudo python ledPixel.py 1 0 0 255'")
            print("or 'sudo python ledPixel.py 1'")
        else:
            strParameter = sys.argv[1:5]
            intParameter = [int(strParameter[i]) for i in range(len(strParameter))]
            while True:
                led.light(intParameter)
                
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        for i in range(8):
            led.strip.setPixelColor(i, (0, 0, 0))
        led.strip.show()