#!/usr/bin/env python3

import time
import sys
import signal
from threading import Thread, Event
from piolib_ws2812 import WS2812, LedType
from piolib_pwm import PWM
from piolib_servo import Servo

strip = None
pwm_instance = None
servo_instance = None
shutdown_event = Event()

def rainbow_cycle(strip, wait_ms=50, cycles=1):
    """
    Display rainbow cycle effect
    
    Args:
        strip: WS2812 instance
        wait_ms: Delay time (milliseconds)
        cycles: Number of cycles to run
    """
    for _ in range(cycles * 256):
        if shutdown_event.is_set():
            return
        for i in range(strip.get_led_count()):
            rgb_values = strip.wheel((i * 256 // strip.get_led_count() + _) & 255)
            strip.set_led_color_data(i, rgb_values[0], rgb_values[1], rgb_values[2])
        strip.show()
        time.sleep(wait_ms / 1000.0)

def breathing_effect(pwm, cycle_time=2.0):
    """
    Breathing light effect using PWM
    
    Args:
        pwm: PWM instance
        cycle_time: Time for one complete breath cycle
    """
    steps = 50
    half_cycle = cycle_time / 2.0
    step_delay = half_cycle / steps
    
    try:
        # Brightening
        for i in range(steps + 1):
            if shutdown_event.is_set():
                return
            duty = int(255 * (i / steps) ** 2)
            pwm.set_duty_cycle(duty)
            time.sleep(step_delay)
        
        # Dimming
        for i in range(steps, -1, -1):
            if shutdown_event.is_set():
                return
            duty = int(255 * (i / steps) ** 2)
            pwm.set_duty_cycle(duty)
            time.sleep(step_delay)
            
    except Exception as e:
        if not shutdown_event.is_set():
            print(f"Error in breathing effect: {e}")

def servo_sweep(servo):
    """
    Sweep servo from 0 to 180 degrees and back
    
    Args:
        servo: Servo instance
    """
    try:
        # Sweep from 0 to 180
        for angle in range(0, 181, 5):
            if shutdown_event.is_set():
                return
            servo.set_angle(angle)
            time.sleep(0.02)
        
        time.sleep(0.5)
        
        # Sweep from 180 to 0
        for angle in range(180, -1, -5):
            if shutdown_event.is_set():
                return
            servo.set_angle(angle)
            time.sleep(0.02)
            
    except Exception as e:
        if not shutdown_event.is_set():
            print(f"Error in servo sweep: {e}")

def ws2812_thread_function(strip):
    """Thread function for WS2812 rainbow effect"""
    while not shutdown_event.is_set():
        rainbow_cycle(strip, 10, 2)

def pwm_thread_function(pwm):
    """Thread function for PWM breathing effect"""
    while not shutdown_event.is_set():
        breathing_effect(pwm, 2.0)

def servo_thread_function(servo):
    """Thread function for servo sweep"""
    while not shutdown_event.is_set():
        servo_sweep(servo)

def signal_handler(sig, frame):
    """Signal handler for graceful shutdown"""
    print('\nShutting down program...')
    shutdown_event.set()

def main():
    global strip, pwm_instance, servo_instance
    
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Default pin assignments
    ws2812_pin = 18  # GPIO pin for WS2812
    pwm_pin = 26     # GPIO pin for PWM
    servo_pin = 21   # GPIO pin for Servo
    num_leds = 8     # Number of LEDs in the strip
    
    # Parse command line arguments if provided
    if len(sys.argv) > 1:
        ws2812_pin = int(sys.argv[1])
    if len(sys.argv) > 2:
        pwm_pin = int(sys.argv[2])
    if len(sys.argv) > 3:
        servo_pin = int(sys.argv[3])
    if len(sys.argv) > 4:
        num_leds = int(sys.argv[4])
    
    threads = []
    
    try:
        # Initialize WS2812
        strip = WS2812(gpio_pin=ws2812_pin, num_leds=num_leds, led_type=LedType.LED_TYPE_GRB)
        strip.set_led_brightness(100)  # Set brightness to about 40%
        print(f"WS2812 initialized on GPIO {ws2812_pin} with {num_leds} LEDs")
        
        # Initialize PWM
        pwm_instance = PWM(gpio_pin=pwm_pin)
        pwm_instance.set_frequency(1000)
        pwm_instance.start()
        print(f"PWM initialized on GPIO {pwm_pin} with frequency 1000Hz")
        
        # Initialize Servo
        servo_instance = Servo(gpio_pin=servo_pin)
        print(f"Servo initialized on GPIO {servo_pin}")
        
        print("Starting all effects. Press Ctrl+C to exit.")
        
        # Create and start threads
        ws2812_thread = Thread(target=ws2812_thread_function, args=(strip,))
        pwm_thread = Thread(target=pwm_thread_function, args=(pwm_instance,))
        servo_thread = Thread(target=servo_thread_function, args=(servo_instance,))
        
        ws2812_thread.daemon = True
        pwm_thread.daemon = True
        servo_thread.daemon = True
        
        ws2812_thread.start()
        pwm_thread.start()
        servo_thread.start()
        
        threads = [ws2812_thread, pwm_thread, servo_thread]
        
        # Keep main thread alive
        while not shutdown_event.is_set():
            time.sleep(0.1)
            
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        # Signal shutdown to all threads
        shutdown_event.set()
        
        # Wait for threads to finish (with timeout)
        for thread in threads:
            thread.join(timeout=2.0)
        
        # Clean up resources
        if strip is not None:
            try:
                strip.deinit()
                print("WS2812 resources released")
            except Exception:
                pass
                
        if pwm_instance is not None:
            try:
                pwm_instance.stop()
                pwm_instance.deinit()
                print("PWM resources released")
            except Exception:
                pass
                
        if servo_instance is not None:
            try:
                servo_instance.stop()
                servo_instance.deinit()
                print("Servo resources released")
            except Exception:
                pass
        
        print("All resources released. Program terminated.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("Usage: python multi_demo.py [ws2812_pin] [pwm_pin] [servo_pin] [num_leds]")
        print("  ws2812_pin: GPIO pin for WS2812 LED strip (default: 18)")
        print("  pwm_pin:    GPIO pin for PWM breathing light (default: 26)")
        print("  servo_pin:  GPIO pin for Servo motor (default: 21)")
        print("  num_leds:   Number of LEDs in strip (default: 8)")
        sys.exit(0)
        
    main()