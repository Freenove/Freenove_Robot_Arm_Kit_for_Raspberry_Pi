import ctypes
import os

# Load shared library
lib_path = '/usr/local/lib/libfreenove_pwm_lib.so'
if not os.path.exists(lib_path):
    raise FileNotFoundError(f"Library not found at {lib_path}")

lib = ctypes.CDLL(lib_path)

class Servo:
    def __init__(self, gpio_pin, min_pulse=0.5, max_pulse=2.5, frequency=50):
        """
        Initialize servo controller
        
        Args:
            gpio_pin: GPIO pin number
            min_pulse: Minimum pulse width (ms), default 0.5ms
            max_pulse: Maximum pulse width (ms), default 2.5ms
            frequency: PWM frequency (Hz), default 50Hz
        """
        # Configure function parameters and return types
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
        
        # Initialize PWM
        self.instance = lib.pwm_init(gpio_pin)
        if not self.instance:
            raise RuntimeError("Failed to initialize PWM for servo")
        
        self.gpio_pin = gpio_pin
        self.min_pulse = min_pulse
        self.max_pulse = max_pulse
        self.frequency = frequency
        
        # Set PWM frequency
        self.set_frequency(frequency)
        
        # Start PWM output
        self.start()
    
    def __del__(self):
        """Destructor, automatically release resources"""
        try:
            self.deinit()
        except Exception as e:
            print(e)
    
    def deinit(self):
        """Release servo resources"""
        if self.instance:
            lib.pwm_deinit(self.instance)
            self.instance = None
    
    def set_frequency(self, frequency):
        """
        Set PWM frequency
        
        Args:
            frequency: Frequency value (Hz)
        """
        if not self.instance:
            raise RuntimeError("Servo not initialized")
        
        result = lib.pwm_set_frequency(self.instance, frequency)
        if result != 0:
            raise ValueError("Failed to set frequency")
        
        self.frequency = frequency
    
    def get_frequency(self):
        """
        Get current PWM frequency
        
        Returns:
            Current frequency value (Hz)
        """
        if not self.instance:
            raise RuntimeError("Servo not initialized")
        
        return lib.pwm_get_frequency(self.instance)
    
    def set_angle(self, angle):
        """
        Set servo angle
        
        Args:
            angle: Angle value (0-180 degrees)
        """
        if not self.instance:
            raise RuntimeError("Servo not initialized")
        
        if not (0 <= angle <= 180):
            raise ValueError("Angle must be between 0 and 180 degrees")
        
        # Convert angle to pulse width
        pulse_width = self.min_pulse + (self.max_pulse - self.min_pulse) * (angle / 180.0)
        
        # Calculate duty cycle (based on 50Hz frequency, 20ms period)
        duty_cycle = int((pulse_width / (1000.0 / self.frequency)) * 255)
        
        # Limit duty cycle range
        duty_cycle = max(0, min(255, duty_cycle))
        
        result = lib.pwm_set_duty_cycle(self.instance, duty_cycle)
        if result != 0:
            raise ValueError("Failed to set servo angle")
    
    def get_gpio(self):
        """
        Get GPIO pin number used by servo
        
        Returns:
            GPIO pin number
        """
        if not self.instance:
            raise RuntimeError("Servo not initialized")
        
        return lib.pwm_get_gpio(self.instance)
    
    def start(self):
        """Start PWM output"""
        if not self.instance:
            raise RuntimeError("Servo not initialized")
        
        lib.pwm_start(self.instance)
    
    def stop(self):
        """Stop PWM output"""
        if not self.instance:
            raise RuntimeError("Servo not initialized")
        
        lib.pwm_stop(self.instance)

# Usage example
if __name__ == "__main__":
    import sys
    import time
    
    servo = None
    
    try:
        # Create servo object, using GPIO 18
        servo = Servo(gpio_pin=18)
        print(f"Servo initialized on GPIO {servo.get_gpio()}")
        print(f"Frequency set to: {servo.get_frequency()} Hz")
        
        print("Moving servo to different angles...")
        print("Press Ctrl+C to exit")
        
        # Test different angles
        angles = [0, 45, 90, 135, 180]
        for angle in angles:
            print(f"Setting servo to {angle} degrees")
            servo.set_angle(angle)
            time.sleep(1)
        
        # Cycle through angles
        while True:
            # From 0 degrees to 180 degrees
            for angle in range(0, 181, 10):
                servo.set_angle(angle)
                time.sleep(0.1)
            
            # From 180 degrees to 0 degrees
            for angle in range(180, -1, -10):
                servo.set_angle(angle)
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        # Release resources
        if servo:
            servo.stop()
            servo.deinit()
        sys.exit(0)