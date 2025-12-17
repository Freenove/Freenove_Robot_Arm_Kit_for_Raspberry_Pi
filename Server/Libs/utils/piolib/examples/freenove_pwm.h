#ifndef PWM_H
#define PWM_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include "pico/stdlib.h"
#include "hardware/pio.h"

typedef struct pwm_instance pwm_instance_t;

pwm_instance_t* pwm_init(int gpio_pin);
void pwm_deinit(pwm_instance_t* instance);
int pwm_set_frequency(pwm_instance_t* instance, uint32_t frequency);
uint32_t pwm_get_frequency(pwm_instance_t* instance);
int pwm_set_duty_cycle(pwm_instance_t* instance, uint8_t duty_cycle);
uint8_t pwm_get_duty_cycle(pwm_instance_t* instance);
int pwm_get_gpio(pwm_instance_t* instance);
void pwm_start(pwm_instance_t* instance);
void pwm_stop(pwm_instance_t* instance);

#ifdef __cplusplus
}
#endif

#endif