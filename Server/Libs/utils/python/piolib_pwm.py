import ctypes
import os
import time

lib_path = '/usr/local/lib/libfreenove_pwm_lib.so'
if not os.path.exists(lib_path):
    raise FileNotFoundError(f"Library not found at {lib_path}")

lib = ctypes.CDLL(lib_path)

class PWM:
    def __init__(self, gpio_pin):
        lib.pwm_init.argtypes = [ctypes.c_int]
        lib.pwm_init.restype = ctypes.c_void_p
        
        lib.pwm_deinit.argtypes = [ctypes.c_void_p]
        lib.pwm_deinit.restype = None
        
        lib.pwm_set_frequency.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        lib.pwm_set_frequency.restype = ctypes.c_int
        
        lib.pwm_get_frequency.argtypes = [ctypes.c_void_p]
        lib.pwm_get_frequency.restype = ctypes.c_uint32
        
        lib.pwm_set_duty_cycle.argtypes = [ctypes.c_void_p, ctypes.c_uint8]
        lib.pwm_set_duty_cycle.restype = ctypes.c_int
        
        lib.pwm_get_duty_cycle.argtypes = [ctypes.c_void_p]
        lib.pwm_get_duty_cycle.restype = ctypes.c_uint8
        
        lib.pwm_get_gpio.argtypes = [ctypes.c_void_p]
        lib.pwm_get_gpio.restype = ctypes.c_int
        
        lib.pwm_start.argtypes = [ctypes.c_void_p]
        lib.pwm_start.restype = None
        
        lib.pwm_stop.argtypes = [ctypes.c_void_p]
        lib.pwm_stop.restype = None
        
        self.instance = lib.pwm_init(gpio_pin)
        if not self.instance:
            raise RuntimeError("Failed to initialize PWM")
        
        self.gpio_pin = gpio_pin
    
    def __del__(self):
        try:
            self.deinit()
        except Exception as e:
            print(e)
    
    def deinit(self):
        if self.instance:
            lib.pwm_deinit(self.instance)
            self.instance = None
    
    def set_frequency(self, frequency):
        if not self.instance:
            raise RuntimeError("PWM not initialized")
        
        result = lib.pwm_set_frequency(self.instance, frequency)
        if result != 0:
            raise ValueError("Failed to set frequency")
    
    def get_frequency(self):
        if not self.instance:
            raise RuntimeError("PWM not initialized")
        
        return lib.pwm_get_frequency(self.instance)
    
    def set_duty_cycle(self, duty_cycle):
        if not self.instance:
            raise RuntimeError("PWM not initialized")
        
        if not (0 <= duty_cycle <= 255):
            raise ValueError("Duty cycle must be between 0 and 255")
        
        result = lib.pwm_set_duty_cycle(self.instance, duty_cycle)
        if result != 0:
            raise ValueError("Failed to set duty cycle")
    
    def get_duty_cycle(self):
        if not self.instance:
            raise RuntimeError("PWM not initialized")
        
        return lib.pwm_get_duty_cycle(self.instance)
    
    def get_gpio(self):
        if not self.instance:
            raise RuntimeError("PWM not initialized")
        
        return lib.pwm_get_gpio(self.instance)
    
    def start(self):
        if not self.instance:
            raise RuntimeError("PWM not initialized")
        
        lib.pwm_start(self.instance)
    
    def stop(self):
        if not self.instance:
            raise RuntimeError("PWM not initialized")
        lib.pwm_set_duty_cycle(self.instance, 0)
        lib.pwm_start(self.instance)
        time.sleep(0.001)
        lib.pwm_stop(self.instance)

def breathing_led(pwm, duration=5):
    steps = 100
    delay = duration / (2 * steps)
    
    for i in range(steps):
        duty = int(255 * (i / steps))
        pwm.set_duty_cycle(duty)
        time.sleep(delay)
    
    for i in range(steps, 0, -1):
        duty = int(255 * (i / steps))
        pwm.set_duty_cycle(duty)
        time.sleep(delay)

if __name__ == "__main__":
    import sys
    
    pwm_16 = None
    
    try:
        pwm_16 = PWM(gpio_pin=16)
        
        print(f"PWM initialized on GPIO {pwm_16.get_gpio()}")
        
        pwm_16.set_frequency(1000)
        
        print(f"Frequency set to: {pwm_16.get_frequency()} Hz")
        
        pwm_16.start()
        
        print("Starting breathing light effect...")
        print("Press Ctrl+C to exit")
        
        while True:
            breathing_led(pwm_16, 2)
            
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        if pwm_16 is not None:
            pwm_16.stop()
            pwm_16.deinit()
        sys.exit(0)