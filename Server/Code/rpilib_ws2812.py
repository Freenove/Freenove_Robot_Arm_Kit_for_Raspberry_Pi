# rpilib_ws2812.py
import time
from rpi_ws281x import PixelStrip as Adafruit_NeoPixel, Color

class WS2812:
    def __init__(self, led_pin=18, led_count=8, order="GRB", led_brightness=255, 
                 led_freq_hz=800000, led_dma=10, led_invert=False, led_channel=0):
        self.led_pin = led_pin
        self.led_count = led_count
        self.led_order = order
        self.led_brightness = led_brightness
        
        self.strip = Adafruit_NeoPixel(
            led_count, led_pin, led_freq_hz, led_dma, 
            led_invert, led_brightness, led_channel
        )
        self.strip.begin()
        
        self.setAllPixelColor((0, 0, 0))

    def getLedType(self):
        return self.led_order

    def setLedType(self, order):
        self.led_order = order

    def setBrightness(self, brightness):
        self.led_brightness = brightness
        self.strip.setBrightness(brightness)

    def getBrightness(self):
        return self.led_brightness

    def _convert_color_order(self, r, g, b):
        if self.led_order == "GRB":
            return (g, r, b)
        elif self.led_order == "RGB":
            return (r, g, b)
        elif self.led_order == "BRG":
            return (b, r, g)
        elif self.led_order == "RBG":
            return (r, b, g)
        elif self.led_order == "GBR":
            return (g, b, r)
        elif self.led_order == "BGR":
            return (b, g, r)
        else:
            return (g, r, b)

    def setPixelColor(self, index, color):
        r, g, b = color
        converted_r, converted_g, converted_b = self._convert_color_order(r, g, b)
        self.strip.setPixelColor(index, Color(converted_r, converted_g, converted_b))

    def setAllPixelColor(self, color):
        for i in range(self.led_count):
            self.setPixelColor(i, color)

    def show(self):
        self.strip.show()
        time.sleep(0.0001)

    def clear(self):
        self.setAllPixelColor((0, 0, 0))
        self.show()
        time.sleep(0.0001)

    def numPixels(self):
        return self.led_count

    def wheel(self, pos):
        pos = pos & 0xFF
        if pos < 85:
            r = pos * 3
            g = 255 - pos * 3
            b = 0
        elif pos < 170:
            pos -= 85
            r = 255 - pos * 3
            g = 0
            b = pos * 3
        else:
            pos -= 170
            r = 0
            g = pos * 3
            b = 255 - pos * 3
        return (r, g, b)

    def deinit(self):
        self.clear()

if __name__ == "__main__":
    import sys
    strip = None  
    try:
        strip = WS2812(led_pin=18, led_count=8, order="GRB")
        print("WS2812 initialization successful")
        print("Press Ctrl+C to exit program")
        
        strip.setBrightness(100)
        
        strip.setAllPixelColor((255, 0, 0))
        strip.show()
        time.sleep(1)

        strip.setAllPixelColor((0, 255, 0))
        strip.show()
        time.sleep(1)

        strip.setAllPixelColor((0, 0, 255))
        strip.show()
        time.sleep(1)

        for i in range(255):
            strip.setBrightness(i)
            strip.show()
            time.sleep(0.01)
        for i in range(255, 0, -1):
            strip.setBrightness(i)
            strip.show()
            time.sleep(0.01)
        
        strip.setBrightness(50)
        for i in range(255):
            for j in range(strip.numPixels()):
                color = strip.wheel((j * 256 // strip.numPixels()) + i)
                strip.setPixelColor(j, color)
            strip.show()
            time.sleep(0.01)

    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        if strip is not None:
            strip.clear()
            strip.deinit()
        sys.exit(1)