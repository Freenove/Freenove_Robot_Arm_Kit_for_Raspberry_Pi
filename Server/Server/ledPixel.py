# -*- coding: utf-8 -*-
#!/usr/bin/env python

import time
from rpi_ws281x import *

# Define functions which animate LEDs in various ways.
class LedPixel:
    def __init__(self):
        self.LedMod= 0
        self.color=[0,0,0]
        #Control the sending order of color data
        self.ORDER = "RGB"  
        # LED strip configuration:
        LED_COUNT      = 8      # Number of LED pixels.
        LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
        LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
        LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
        LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
        LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
        LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
        # Create NeoPixel object with appropriate configuration.
        self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        # Intialize the library (must be called once before other functions).
        self.strip.begin()
    
    #根据颜色类型，返回正确的颜色数据
    def LED_TYPR(self, R, G, B):
        Led_type = ["GRB", "GBR", "RGB", "RBG", "BRG", "BGR"]
        color = [Color(G, R, B), Color(G, B, R), Color(R, G, B), Color(R, B, G), Color(B, R, G), Color(B, G, R)]
        if self.ORDER in Led_type:
            return color[Led_type.index(self.ORDER)]
            
    #逐个设置彩灯并显示效果
    def colorWipe(self, color, wait_ms=50, interval_ms=1000):
        self.strip.setBrightness(255)
        colorShow = self.LED_TYPR(color[0], color[1], color[2])
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, colorShow)
            self.strip.show()
            time.sleep(wait_ms/1000.0)
        time.sleep(interval_ms/1000.0)

    #自定义RGB灯
    def RGBLed(self, color, wait_ms=100):
        self.strip.setBrightness(255)
        colorShow = self.LED_TYPR(color[0], color[1], color[2])
        for i in range(8):
            self.strip.setPixelColor(i, colorShow)
        self.strip.show()
        time.sleep(wait_ms/1000.0)

    #流水灯
    def followingLed(self, color, wait_ms=50):
        self.strip.setBrightness(255)
        ledShow = [self.LED_TYPR(color[0]//8, color[1]//8, color[2]//8), 
               self.LED_TYPR(color[0]//4, color[1]//4, color[2]//4), 
               self.LED_TYPR(color[0]//2, color[1]//2, color[2]//2),
               self.LED_TYPR(color[0]//1, color[1]//1, color[2]//1)]
        ledNum = self.strip.numPixels()
        for z in range(ledNum):
            for i in range(ledNum):
                self.strip.setPixelColor(i, Color(0,0,0))
            for j in range(len(ledShow)):
                self.strip.setPixelColor((z+j)%ledNum, ledShow[j])
            self.strip.show()
            time.sleep(wait_ms/1000.0)

    #闪烁
    def blinkLed(self, color, wait_ms=300):
        self.strip.setBrightness(255)
        colorShow = self.LED_TYPR(color[0], color[1], color[2])
        for i in range(8):
            self.strip.setPixelColor(i, colorShow)
        self.strip.show()
        time.sleep(wait_ms/1000.0)
        for i in range(8):
            self.strip.setPixelColor(i, Color(0, 0, 0))
        self.strip.show()
        time.sleep(wait_ms/1000.0)
        
    #呼吸灯        
    def breathLight(self, color, wait_ms=15):
        colorShow = self.LED_TYPR(color[0], color[1], color[2])
        for i in range(8):
            self.strip.setPixelColor(i, colorShow)
        for i in range(100):
            self.strip.setBrightness(i)
            self.strip.show()
            time.sleep(wait_ms/1000.0)
        for i in range(100):
            self.strip.setBrightness(100-i)
            self.strip.show()
            time.sleep(wait_ms/1000.0)
    
    #色盘取色
    def wheel(self, pos):
        """Generate rainbow colors across 0-255 positions."""
        if pos<0 or pos >255:
            r=g=b=0
        elif pos < 85:
            r=pos * 3
            g=255 - pos * 3
            b=0
        elif pos < 170:
            pos -= 85
            r=255 - pos * 3
            g=0
            b=pos * 3
        else:
            pos -= 170
            r=0
            g=pos * 3
            b=255 - pos * 3
        return self.LED_TYPR(r,g,b)

    #彩虹色旋转灯
    def rainbowCycle(self, wait_ms=3, iterations=1):
        self.strip.setBrightness(50)
        """Draw rainbow that uniformly distributes itself across all pixels."""
        for j in range(256*iterations):
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, self.wheel((int(i * 256 / self.strip.numPixels()) + j) & 255))
            self.strip.show()
            time.sleep(wait_ms/1000.0)

    #渐变彩虹色灯
    def gradualChange(self, wait_ms=10, iterations=1):
        self.strip.setBrightness(50)
        """Draw rainbow that fades across all pixels at once."""
        for j in range(256*iterations):
            for i in range(self.strip.numPixels()):
                 self.strip.setPixelColor(i, self.wheel((i+j) & 255))
            self.strip.show()
            time.sleep(wait_ms/1000.0)

    #可自定义的彩灯旋转
    def rotateLed(self, color, number=2, wait_ms=50):
        self.strip.setBrightness(255)
        colorShow = self.LED_TYPR(color[0], color[1], color[2])
        ledNum = self.strip.numPixels()
        for z in range(ledNum):
            for i in range(ledNum):
                self.strip.setPixelColor(i, Color(0,0,0))
            for j in range(number):
                self.strip.setPixelColor((z+j*(ledNum//number))%ledNum, colorShow)
            self.strip.show()
            time.sleep(wait_ms/1000.0)
    
    #彩灯显示函数，需要使用一个线程循环执行它。data包含4个参数，0:mode, 1:R, 2:G, 3:B
    def light(self, data):
        self.LedMod=data[0]
        for i in range(3):
            self.color[i]=int(data[i+1]%256)
        if self.LedMod==0:                                                    #关闭彩灯
            self.color = [0,0,0]
            self.colorWipe(self.color)
        elif self.LedMod==1:                                                  #RGB
            self.RGBLed(self.color)
        elif self.LedMod==2:                                                  #流水灯
            self.followingLed(self.color)
        elif self.LedMod==3:                                                  #闪烁
            self.blinkLed(self.color)
        elif self.LedMod==4:                                                  #呼吸灯
            self.breathLight(self.color)
        elif self.LedMod==5:                                                  #彩虹灯
            self.rainbowCycle()
        elif self.LedMod==6:                                                  #渐变灯
            self.gradualChange()
        elif self.LedMod==7:                                                  #两个灯旋转
            self.rotateLed(self.color, 2, 50)
        elif self.LedMod==8:                                                  #四个灯旋转
            self.rotateLed(self.color, 4, 100)                                   
        elif self.LedMod>=9 or self.LedMod < 0:
            self.LedMod = 0
            print("parameter error! Press Ctrl+c to exit and re-enter the parameters, please.")
            time.sleep(1)

# Main program logic follows:
if __name__ == '__main__':
    import sys
    
    led=LedPixel()   
    led.strip.setBrightness(255)
    print ('Program is starting ... ')
    col=[Color(255,0,0), Color(0,255,0), Color(0,0,255)]
    try:
        if len(sys.argv)<5 and len(sys.argv)>=2:
            strParameter = sys.argv[1:]
            intParameter = [int(strParameter[i]) for i in range(len(strParameter))]
            parameter = [intParameter[0], 128, 0, 0]
            while True:
                led.light(parameter)
        elif len(sys.argv)<2:
            print("Enter a parameter, 'sudo python ledPixel.py 1 0 0 255'")
            print("or 'sudo python ledPixel.py 1'")
        else:
            strParameter = sys.argv[1:5]
            intParameter = [int(strParameter[i]) for i in range(len(strParameter))]
            while True:
                led.light(intParameter)
                
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        for i in range(8):
            led.strip.setPixelColor(i, Color(0, 0, 0))
        led.strip.show()
        
