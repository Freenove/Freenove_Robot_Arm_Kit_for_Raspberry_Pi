#include <stdio.h>
#include <stdlib.h>
#include <string.h> 

#include "pico/stdlib.h"
#include "hardware/pio.h"
#include "pwm.pio.h"
#include "freenove_pwm.h"

#define MAX_PWM_INSTANCES 8

struct pwm_instance {
    PIO pio;
    int sm;
    uint offset;
    uint gpio;
    uint32_t period;
    uint32_t level;
    uint8_t duty_cycle;
    uint32_t frequency;
    int is_active;
};

static pwm_instance_t pwm_instances[MAX_PWM_INSTANCES];
static int instances_initialized = 0;

pwm_instance_t* pwm_init(int gpio_pin) {
    if (!instances_initialized) {
        memset(pwm_instances, 0, sizeof(pwm_instances));
        instances_initialized = 1;
    }
    
    pwm_instance_t* instance = NULL;
    for (int i = 0; i < MAX_PWM_INSTANCES; i++) {
        if (!pwm_instances[i].is_active) {
            instance = &pwm_instances[i];
            break;
        }
    }
    
    if (!instance) {
        return NULL;
    }
    
    stdio_init_all();
    
    instance->pio = pio0;
    instance->sm = pio_claim_unused_sm(instance->pio, true);
    if (instance->sm < 0) {
        return NULL;
    }
    
    instance->offset = pio_add_program(instance->pio, &pwm_program);
    instance->gpio = gpio_pin;
    
    pwm_program_init(instance->pio, instance->sm, instance->offset, gpio_pin);
    pwm_set_frequency(instance, 1000);
    pwm_set_duty_cycle(instance, 0);
    
    instance->is_active = 1;
    return instance;
}

void pwm_deinit(pwm_instance_t* instance) {
    if (!instance || !instance->is_active) return;
    
    pio_sm_set_enabled(instance->pio, instance->sm, false);
    pio_sm_unclaim(instance->pio, instance->sm);
    
    instance->is_active = 0;
    instance->pio = NULL;
    instance->sm = 0;
    instance->offset = 0;
    instance->gpio = 0;
    instance->period = 0;
    instance->level = 0;
    instance->duty_cycle = 0;
    instance->frequency = 0;
}

int pwm_set_frequency(pwm_instance_t* instance, uint32_t frequency) {
    if (!instance || !instance->is_active || frequency == 0) {
        return -1;
    }
    uint32_t sys_clock_hz = (uint32_t)(133333333/2);
    uint32_t period = (uint32_t)(sys_clock_hz / frequency)-1;
    if (period > 0xFFFFFFFF) {
        return -1;
    }
    instance->period = period;
    instance->frequency = frequency;
    pio_sm_set_enabled(instance->pio, instance->sm, false);
    pio_sm_put_blocking(instance->pio, instance->sm, period);
    pio_sm_exec(instance->pio, instance->sm, pio_encode_pull(false, false));
    pio_sm_exec(instance->pio, instance->sm, pio_encode_out(pio_isr, 32));
    pwm_set_duty_cycle(instance, instance->duty_cycle);
    return 0;
}

uint32_t pwm_get_frequency(pwm_instance_t* instance) {
    if (!instance || !instance->is_active) {
        return 0;
    }
    return instance->frequency;
}

int pwm_set_duty_cycle(pwm_instance_t* instance, uint8_t duty_cycle) {
    if (!instance || !instance->is_active) {
        return -1;
    }
    uint32_t level = (uint32_t)((((uint64_t)instance->period * duty_cycle) + 128) / 255);
    instance->level = level;
    instance->duty_cycle = duty_cycle;
    pio_sm_put_blocking(instance->pio, instance->sm, level);
    return 0;
}

uint8_t pwm_get_duty_cycle(pwm_instance_t* instance) {
    if (!instance || !instance->is_active) {
        return 0;
    }
    return instance->duty_cycle;
}

int pwm_get_gpio(pwm_instance_t* instance) {
    if (!instance || !instance->is_active) {
        return -1;
    }
    return instance->gpio;
}

void pwm_start(pwm_instance_t* instance) {
    if (instance && instance->is_active) {
        pio_sm_set_enabled(instance->pio, instance->sm, true);
    }
}

void pwm_stop(pwm_instance_t* instance) {
    if (instance && instance->is_active) {
        pio_sm_set_enabled(instance->pio, instance->sm, false);
    }
}