#!/usr/bin/env python3

import time
import signal
import sys
from piolib_ws2812 import WS2812

def rainbow_cycle(strip, wait_ms=50):
    """
    Display rainbow cycle effect
    
    Args:
        strip: WS2812 instance
        wait_ms: Delay time (milliseconds)
    """
    for j in range(256):
        for i in range(strip.numPixels()):
            color = strip.wheel((i * 256 // strip.numPixels() + j) & 255)
            strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)

# Signal handler function for graceful exit
def signal_handler(sig, frame):
    print('\nShutting down program...')
    if 'strip' in globals():
        strip.clear()
        strip.deinit()
    sys.exit(0)

# Register signal handler
signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    # Get command line arguments
    gpio_pin = 18  # Default GPIO pin
    num_leds = 8   # Default LED count
    
    if len(sys.argv) > 1:
        gpio_pin = int(sys.argv[1])  # First argument as GPIO pin
    if len(sys.argv) > 2:
        num_leds = int(sys.argv[2])  # Second argument as LED count
        
    # Create WS2812 object
    try:
        strip = WS2812(led_pin=gpio_pin, led_count=num_leds, order="GRB")
        print(f"WS2812 initialization successful (GPIO: {gpio_pin}, LED count: {num_leds})")
        print("Press Ctrl+C to exit program")
        
        # Set brightness (optional)
        strip.setBrightness(100)  # Set brightness to about 40%
        
        # Loop to display rainbow effect
        while True:
            # Display rainbow cycle effect
            rainbow_cycle(strip, 10) 
            
    except Exception as e:
        print(f"Error occurred: {e}")
        sys.exit(1)