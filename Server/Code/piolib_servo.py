import ctypes
import os

# Load shared library
lib_path = '/usr/local/lib/libfreenove_pwm_lib.so'
if not os.path.exists(lib_path):
    raise FileNotFoundError(f"Library not found at {lib_path}")

lib = ctypes.CDLL(lib_path)

def _initialize_pwm_library():
    """Initialize the PWM library functions once"""
    global lib
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


class PiolibServo:
    def __init__(self):
        """
        Initialize servo controller
        """
        _initialize_pwm_library()
        self.servo_pin = 13
        self.current_instance = None
        self.current_pin = None
        self._ensure_pin_initialized(self.servo_pin)

    def _ensure_pin_initialized(self, pin):
        """Ensure the specified pin is currently active"""
        if self.current_pin != pin:
            # Deinitialize current pin if there's one
            if self.current_instance is not None:
                lib.pwm_deinit(self.current_instance)
            
            # Initialize the requested pin
            self.current_instance = lib.pwm_init(pin)
            if not self.current_instance:
                raise RuntimeError(f"Failed to initialize PWM for servo on pin {pin}")
            
            # Set PWM frequency to 50Hz (standard for servos)
            self._set_frequency(self.current_instance, 50)
            
            # Start PWM output
            lib.pwm_start(self.current_instance)
            
            self.current_pin = pin

    def _set_frequency(self, instance, frequency):
        """Internal method to set PWM frequency"""
        if not instance:
            raise RuntimeError("Servo not initialized")
        
        result = lib.pwm_set_frequency(instance, frequency)
        if result != 0:
            raise ValueError("Failed to set frequency")

    def setServoAngle(self, pin, angle):
        """
        Set the angle of the servo on the specified pin
        
        Args:
            pin: Pin number
            angle: Angle to set (0-180)
        
        Returns:
            Pulse width in microseconds
        """
        # Constrain angle between 0 and 180
        if angle < 0:
            angle = 0
        elif angle > 180:
            angle = 180
            
        # Ensure the correct pin is active
        self._ensure_pin_initialized(pin)
        
        # Convert angle to pulse width in microseconds (500-2500μs range)
        servo_duty = 500 + (2000 / 180) * angle
        
        # Calculate duty cycle (based on 50Hz frequency, 20ms period = 20000μs)
        duty_cycle = int((servo_duty / 20000.0) * 255)
        
        # Limit duty cycle range
        duty_cycle = max(0, min(255, duty_cycle))
        
        result = lib.pwm_set_duty_cycle(self.current_instance, duty_cycle)
        if result != 0:
            raise ValueError("Failed to set servo angle")
        
        return servo_duty

    def relaxServo(self):
        """Release the servo on the specified pin"""
        if self.current_instance is not None:
            lib.pwm_stop(self.current_instance)

    def servoClose(self):
        """Release all servo resources"""
        if self.current_instance is not None:
            lib.pwm_deinit(self.current_instance)
            self.current_instance = None
            self.current_pin = None

    def constrain(self, value, min_val, max_val):
        """Constrain a value between min and max"""
        if value > max_val:
            value = max_val
        if value < min_val:
            value = min_val
        return value


# Usage example
if __name__ == "__main__":
    import sys
    import time
    
    servo = None
    
    try:
        # Create servo object
        servo = PiolibServo()
        print("Servo controller initialized")
        
        print("Moving servos to different angles...")
        print("Press Ctrl+C to exit")
        SERVO_PIN = [13, 16, 19, 20, 26]
        # Test each pin individually - complete all movements on one pin before moving to next
        for pin_index in range(len(SERVO_PIN)):
            print(f"Controlling servo on pin {SERVO_PIN[pin_index]} (index {pin_index})")
            
            # Complete movement sequence for this pin
            for j in range(0, 180, 10):
                servo.setServoAngle(SERVO_PIN[pin_index], j)
                time.sleep(0.1)  # Delay for the movement
            
            # Cycle through angles for this pin
            for angle in range(0, 181, 10):
                servo.setServoAngle(SERVO_PIN[pin_index], angle)
                time.sleep(0.05)
                
            for angle in range(180, -1, -10):
                servo.setServoAngle(SERVO_PIN[pin_index], angle)
                time.sleep(0.05)
        
        # Continuous loop - each pin gets its turn
        while True:
            for pin_index in range(len(SERVO_PIN)):
                print(f"Controlling servo on pin {SERVO_PIN[pin_index]} (index {pin_index})")
                
                # Move this pin through its range
                for angle in range(0, 181, 10):
                    servo.setServoAngle(SERVO_PIN[pin_index], angle)
                    time.sleep(0.05)
                    
                for angle in range(180, -1, -10):
                    servo.setServoAngle(SERVO_PIN[pin_index], angle)
                    time.sleep(0.05)
                
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        # Release resources
        if servo:
            servo.servoClose()
        sys.exit(0)