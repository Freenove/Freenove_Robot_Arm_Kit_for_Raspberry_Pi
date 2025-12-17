#!/usr/bin/env python3

import time
import sys
import signal
from piolib_servo import Servo

servo_instance = None
shutdown_requested = False

def sweep_test(servo):
    print("Performing sweep test...")
    for angle in range(0, 181, 10):
        if shutdown_requested:
            return
        servo.set_angle(angle)
        time.sleep(0.05)
    
    time.sleep(0.5)
    
    for angle in range(180, -1, -10):
        if shutdown_requested:
            return
        servo.set_angle(angle)
        time.sleep(0.05)

def interactive_mode(servo):
    print("Entering interactive mode...")
    print("Please enter an angle value (0-180), or 'q' to quit:")
    
    while not shutdown_requested:
        try:
            user_input = input("Enter angle (0-180): ").strip()
            
            if user_input.lower() == 'q':
                print("Exiting interactive mode...")
                break
                
            angle = int(user_input)
            
            if 0 <= angle <= 180:
                servo.set_angle(angle)
                print(f"Servo moved to {angle} degrees")
            else:
                print("Please enter a value between 0 and 180")
                
        except ValueError:
            print("Invalid input. Please enter a number between 0 and 180, or 'q' to quit")
        except EOFError:
            print("\nEOF received, exiting interactive mode...")
            break

def signal_handler(sig, frame):
    global servo_instance, shutdown_requested
    shutdown_requested = True
    print('\nShutting down program...')

def main():
    global servo_instance, shutdown_requested
    
    signal.signal(signal.SIGINT, signal_handler)
    
    gpio_pin = 18
    angle = None
    
    if len(sys.argv) > 1:
        gpio_pin = int(sys.argv[1])
    if len(sys.argv) > 2:
        angle = int(sys.argv[2])
    
    try:
        servo_instance = Servo(gpio_pin=gpio_pin)
        print(f"Servo initialized on GPIO {servo_instance.get_gpio()}")
        print(f"Frequency set to: {servo_instance.get_frequency()} Hz")
        
        print("Starting servo demo...")
        print("Press Ctrl+C to exit")
        
        if angle is not None:
            servo_instance.set_angle(angle)
            print(f"Set servo angle to: {angle} degrees")
            interactive_mode(servo_instance)
        else:
            sweep_test(servo_instance)
            
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
        shutdown_requested = True
    except Exception as e:
        print(f"Error occurred: {e}")
        shutdown_requested = True
    finally:
        if servo_instance is not None:
            try:
                servo_instance.stop()
                servo_instance.deinit()
                print("Servo resources released")
            except Exception:
                pass
        
        print("Program terminated.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("Usage: python servo_demo.py [gpio_pin] [angle]")
        print("  gpio_pin: GPIO pin number (default: 18)")
        print("  angle:    Servo angle (0-180), if not specified, run interactive mode")
        sys.exit(0)
        
    main()