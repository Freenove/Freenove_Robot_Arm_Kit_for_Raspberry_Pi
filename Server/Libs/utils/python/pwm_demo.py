#!/usr/bin/env python3

import time
import sys
import signal
from piolib_pwm import PWM

pwm_instance = None
shutdown_requested = False

def breathing_effect(pwm, cycle_time=2.0):
    global shutdown_requested
    steps = 50
    half_cycle = cycle_time / 2.0
    step_delay = half_cycle / steps
    
    try:
        for i in range(steps + 1):
            if shutdown_requested:
                return
            duty = int(255 * (i / steps) ** 2)
            pwm.set_duty_cycle(duty)
            time.sleep(step_delay)
        
        for i in range(steps, -1, -1):
            if shutdown_requested:
                return
            duty = int(255 * (i / steps) ** 2)
            pwm.set_duty_cycle(duty)
            time.sleep(step_delay)
            
    except Exception as e:
        if not shutdown_requested:
            print(f"Error in breathing effect: {e}")

# Signal handler function for graceful exit
def signal_handler(sig, frame):
    global pwm_instance, shutdown_requested
    shutdown_requested = True
    print('\nShutting down program...')

def main():
    global pwm_instance, shutdown_requested
    
    signal.signal(signal.SIGINT, signal_handler)

    gpio_pin = 18   
    frequency = 1000
    duty_cycle = None
    
    if len(sys.argv) > 1:
        gpio_pin = int(sys.argv[1])   
    if len(sys.argv) > 2:
        frequency = int(sys.argv[2]) 
    if len(sys.argv) > 3:
        duty_cycle = int(sys.argv[3]) 
    
    try:
        pwm_instance = PWM(gpio_pin=gpio_pin)
        print(f"PWM initialized on GPIO {pwm_instance.get_gpio()}")
        
        pwm_instance.set_frequency(frequency)
        print(f"Frequency set to: {pwm_instance.get_frequency()} Hz")
        
        pwm_instance.start()
        print("PWM started...")
        print("Press Ctrl+C to exit")
        
        if duty_cycle is not None:
            pwm_instance.set_duty_cycle(duty_cycle)
            print(f"Set duty cycle to: {duty_cycle}")
            while not shutdown_requested:
                time.sleep(0.1)
        else:
            print("Running breathing light effect...")
            while not shutdown_requested:
                breathing_effect(pwm_instance, 2.0)
            
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
        shutdown_requested = True
    except Exception as e:
        print(f"Error occurred: {e}")
        shutdown_requested = True
    finally:
        if pwm_instance is not None:
            try:
                pwm_instance.stop()
                pwm_instance.deinit()
                print("PWM resources released")
            except Exception:
                pass
        
        print("Program terminated.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("Usage: python pwm_demo.py [gpio_pin] [frequency] [duty_cycle]")
        print("  gpio_pin:   GPIO pin number (default: 18)")
        print("  frequency:  PWM frequency in Hz (default: 1000)")
        print("  duty_cycle: Duty cycle (0-255), if not specified, run breathing light effect")
        sys.exit(0)
        
    main()