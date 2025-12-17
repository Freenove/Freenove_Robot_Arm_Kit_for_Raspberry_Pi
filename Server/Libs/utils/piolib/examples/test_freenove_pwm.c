#include <stdio.h>
#include <stdlib.h>
#include "pico/stdlib.h"
#include "freenove_pwm.h"

int main(int argc, const char **argv) {
    stdio_init_all();
    
    int gpio_pin = 21;
    if (argc == 2) {
        gpio_pin = (int)strtol(argv[1], NULL, 0);
    }
    
    pwm_instance_t* pwm = pwm_init(gpio_pin);
    if (!pwm) {
        printf("Failed to initialize PWM on GPIO %d\n", gpio_pin);
        return -1;
    }
    
    printf("PWM initialized on GPIO %d\n", gpio_pin);
    
    if (pwm_set_frequency(pwm, 10000) == 0) {
        printf("Set frequency to 10000 Hz\n");
    } else {
        printf("Failed to set frequency\n");
    }
    
    pwm_start(pwm);
    
    printf("Generating breathing light effect...\n");
    printf("Press Ctrl+C to stop\n");
    
    int duty_cycle = 0;
    int direction = 1;
    
    while (true) {
        pwm_set_duty_cycle(pwm, duty_cycle);
        if (duty_cycle >= 255) {
            duty_cycle = 255;
            direction = -1;
            sleep_ms(5000);
        } else if (duty_cycle <= 0) {
            duty_cycle = 0;
            direction = 1;
            sleep_ms(5000);
        }
        
        duty_cycle += direction;
        sleep_ms(100);
    }
    
    pwm_deinit(pwm);
    
    return 0;
}