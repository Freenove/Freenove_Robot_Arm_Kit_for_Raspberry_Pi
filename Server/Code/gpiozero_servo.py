# -*- coding: utf-8 -*-
#!/usr/bin/env python

from gpiozero import PWMOutputDevice  
import time  

class GpiozeroServo:
    def __init__(self):
        self.servo = None 
        self.current_pin = None
        self._ensure_pin_initialized(self.current_pin)

    def _ensure_pin_initialized(self, pin):
        """Ensure the specified pin is currently active"""
        if self.current_pin != pin:
            # Close the previous servo if exists
            if self.servo is not None:
                try:
                    self.servo.off()
                    self.servo.close()
                except:
                    pass  # Ignore errors when closing
            # Create a new servo for the requested pin
            self.current_pin = pin
            self.servo = PWMOutputDevice(pin, initial_value=0)

    def constrain(self, value, min_val, max_val):
        if value > max_val:
            value = max_val
        if value < min_val:
            value = min_val
        return value
    
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

        servo_duty = 500 + (2000/180) * angle
        self.servo.frequency = 50 
        self.servo.value = servo_duty/20000
        return servo_duty
    
    def relaxServo(self):
        """Release the servo on the specified pin"""
        if self.servo is not None:
            try:
                self.servo.off()
            except:
                pass  # Ignore errors when turning off
    
    def servoClose(self):
        if self.servo is not None:
            try:
                self.servo.off()
                self.servo.close()
            except:
                pass  # Ignore errors when closing

# Main program logic follows:
if __name__ == '__main__':
    import sys
    import time

    servo = None
    
    try:
        # Create servo object
        servo = GpiozeroServo()
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