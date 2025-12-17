import ctypes
import os
import time

lib_path = '/usr/local/lib/libfreenove_ws2812_lib.so'
if not os.path.exists(lib_path):
    raise FileNotFoundError(f"Library not found at {lib_path}")

lib = ctypes.CDLL(lib_path)

class WS2812:
    def __init__(self, led_pin=18, led_count=8,  order="GRB", led_brightness=255):
        lib.begin.argtypes = [ctypes.c_int, ctypes.c_int]
        lib.begin.restype = ctypes.c_void_p
        
        lib.setPixelColor.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8]
        lib.setPixelColor.restype = None

        lib.show.argtypes = [ctypes.c_void_p]
        lib.show.restype = None
        
        lib.stop.argtypes = [ctypes.c_void_p]
        lib.stop.restype = None
        
        lib.setBrightness.argtypes = [ctypes.c_void_p, ctypes.c_uint8]
        lib.setBrightness.restype = None
        
        lib.numPixels.argtypes = [ctypes.c_void_p]
        lib.numPixels.restype = ctypes.c_int

        lib.wheel.argtypes = [ctypes.c_uint8]
        lib.wheel.restype = ctypes.c_uint32

        self.instance = lib.begin(led_pin, led_count)
        if not self.instance:
            raise RuntimeError("Failed to initialize WS2812")
        
        self.led_pin = led_pin
        self.led_count = led_count
        self.led_order = order
        self.led_brightness = led_brightness

        self.setBrightness(led_brightness)
        self.setAllPixelColor((0,0,0))

    def __del__(self):
        try:
            self.deinit()
        except:
            pass

    def getLedType(self):
        return self.order

    def setLedType(self, order):
        self.order = order

    def setBrightness(self, brightness):
        self.led_brightness = brightness
        lib.setBrightness(self.instance, brightness)

    def getBrightness(self):
        return self.led_brightness  

    def setPixelColor(self, index, color):
        r,g,b = color
        if self.led_order == "GRB":
            lib.setPixelColor(self.instance, index, g, r, b)
        elif self.led_order == "RGB":
            lib.setPixelColor(self.instance, index, r, g, b)
        elif self.led_order == "BRG":
            lib.setPixelColor(self.instance, index, b, r, g)
        elif self.led_order == "RBG":
            lib.setPixelColor(self.instance, index, r, b, g)
        elif self.led_order == "GBR":
            lib.setPixelColor(self.instance, index, g, b, r)
        elif self.led_order == "BGR":
            lib.setPixelColor(self.instance, index, b, g, r)
        else:
            lib.setPixelColor(self.instance, index, g, r, b)
    
    def setAllPixelColor(self, color):
        for i in range(self.led_count):
            self.setPixelColor(i, color)
    
    def show(self):
        lib.show(self.instance)
        time.sleep(0.0001)

    def clear(self):
        self.setAllPixelColor((0,0,0))
        self.show()
        time.sleep(0.0001)

    def numPixels(self):
        return self.led_count

    def wheel(self, pos):
        pos = pos & 0xFF
        wheel_pos = 255 - pos
        if wheel_pos < 85:
            r = 255 - (wheel_pos * 3)
            g = 0
            b = wheel_pos * 3
        elif wheel_pos < 170:
            wheel_pos -= 85
            r = 0
            g = wheel_pos * 3
            b = 255 - (wheel_pos * 3)
        else:
            wheel_pos -= 170
            r = wheel_pos * 3
            g = 255 - (wheel_pos * 3)
            b = 0
        return (r, g, b)

    def deinit(self):
        if hasattr(self, 'instance') and self.instance:
            lib.stop(self.instance)
            self.instance = None


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