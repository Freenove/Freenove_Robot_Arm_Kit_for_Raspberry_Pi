#include "freenove_ws2812.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h> 

#include "pico/stdlib.h"
#include "hardware/pio.h"
#include "ws2812.pio.h"

#define DEFAULT_NUM_LEDS 256
#define IS_RGBW false
#define MAX_WS2812_INSTANCES 4

struct ws2812_instance {
    PIO pio;
    int sm;
    uint offset;
    uint gpio;
    int num_leds;
    uint32_t* led_show_buffer;
    uint32_t* led_original_buffer;
    int is_initialized;
    uint led_brightness;
};

static ws2812_instance_t ws2812_instances[MAX_WS2812_INSTANCES];
static int instances_initialized = 0;

static inline void put_pixel(ws2812_instance_t* instance, uint32_t pixel_grb) {
    if (instance->pio && instance->sm >= 0) {
        pio_sm_put_blocking(instance->pio, instance->sm, pixel_grb << 8u);
    }
}

ws2812_instance_t* begin(int gpio_pin, int leds) {
    if (!instances_initialized) {
        memset(ws2812_instances, 0, sizeof(ws2812_instances));
        instances_initialized = 1;
    }
    
    ws2812_instance_t* instance = NULL;
    for (int i = 0; i < MAX_WS2812_INSTANCES; i++) {
        if (!ws2812_instances[i].is_initialized) {
            instance = &ws2812_instances[i];
            break;
        }
    }
    
    if (!instance) {
        return NULL;
    }
    
    if (leds <= 0) {
        instance->num_leds = DEFAULT_NUM_LEDS;
    } else {
        instance->num_leds = leds;
    }
    
    instance->led_original_buffer = (uint32_t*)malloc(instance->num_leds * sizeof(uint32_t));
    instance->led_show_buffer = (uint32_t*)malloc(instance->num_leds * sizeof(uint32_t));
    if (!instance->led_original_buffer || !instance->led_show_buffer) {
        return NULL;
    }
    
    memset(instance->led_original_buffer, 0, instance->num_leds * sizeof(uint32_t));
    memset(instance->led_show_buffer, 0, instance->num_leds * sizeof(uint32_t));
    
    stdio_init_all();
    
    instance->pio = pio0;
    instance->sm = pio_claim_unused_sm(instance->pio, true);
    if (instance->sm < 0) {
        free(instance->led_original_buffer);
        free(instance->led_show_buffer);
        instance->led_original_buffer = NULL;
        instance->led_show_buffer = NULL;
        return NULL;
    }
    
    instance->offset = pio_add_program(instance->pio, &ws2812_program);
    ws2812_program_init(instance->pio, instance->sm, instance->offset, gpio_pin, 800000, IS_RGBW);
    
    instance->gpio = gpio_pin;
    instance->led_brightness = 255;
    instance->is_initialized = 1;
    
    return instance;
}

void stop(ws2812_instance_t* instance) {
    if (!instance || !instance->is_initialized) return;

    memset(instance->led_original_buffer, 0, instance->num_leds * sizeof(uint32_t));
    memset(instance->led_show_buffer, 0, instance->num_leds * sizeof(uint32_t));
    usleep(instance->num_leds*10);
    show(instance);
    usleep(instance->num_leds*10);

    if (instance->led_original_buffer) {
        free(instance->led_original_buffer);
        free(instance->led_show_buffer);
        instance->led_original_buffer = NULL;
        instance->led_show_buffer = NULL;
    }
    
    if (instance->pio && instance->sm >= 0) {
        pio_sm_set_enabled(instance->pio, instance->sm, false);
    }
    
    instance->is_initialized = 0;
    instance->pio = NULL;
    instance->sm = -1;
    instance->offset = 0;
}

void setBrightness(ws2812_instance_t* instance, uint8_t brightness) {
    if (!instance || !instance->is_initialized) return;
    
    instance->led_brightness = brightness;
    for(int i=0;i<instance->num_leds;i++)
    {
        uint8_t d1 = (instance->led_original_buffer[i]>> 16) & 0xff;
        uint8_t d2 = (instance->led_original_buffer[i]>> 8) & 0xff;
        uint8_t d3 = instance->led_original_buffer[i] & 0xff;
        d1 = (d1 * instance->led_brightness) / 255;
        d2 = (d2 * instance->led_brightness) / 255;
        d3 = (d3 * instance->led_brightness) / 255;
        instance->led_show_buffer[i] = ((uint32_t)(d1) << 16) | ((uint32_t)(d2) << 8) | (uint32_t)(d3);
    }
}

void setPixelColor(ws2812_instance_t* instance, unsigned int index, uint8_t r, uint8_t g, uint8_t b) {
    if (!instance || !instance->is_initialized) return;

    if (index < (unsigned int)instance->num_leds) {
        uint8_t red = 0;
        uint8_t green = 0;
        uint8_t blue = 0;
        red = (r * instance->led_brightness) / 255;
        green = (g * instance->led_brightness) / 255;
        blue = (b * instance->led_brightness) / 255;
        instance->led_original_buffer[index] = ((uint32_t)(r) << 16) | ((uint32_t)(g) << 8) | (uint32_t)(b);
        instance->led_show_buffer[index] = ((uint32_t)(red) << 16) | ((uint32_t)(green) << 8) | (uint32_t)(blue);
    }
}

int numPixels(ws2812_instance_t* instance) { 
    if (!instance || !instance->is_initialized) return 0;
    return instance->num_leds;
}

void show(ws2812_instance_t* instance) {
    if (!instance || !instance->is_initialized) return;
    
    for (int i = 0; i < instance->num_leds; i++) {
        put_pixel(instance, instance->led_show_buffer[i]);
    }
}

uint32_t wheel(uint8_t wheel_pos){
    uint8_t r, g, b;
    wheel_pos = 255 - wheel_pos;
    
    if (wheel_pos < 85) {
        r = 255 - (wheel_pos * 3);
        g = 0;
        b = wheel_pos * 3;
        return ((uint32_t)(r) << 16) | ((uint32_t)(g) << 8) | (uint32_t)(b);
    }
    
    if (wheel_pos < 170) {
        wheel_pos -= 85;
        r = 0;
        g = wheel_pos * 3;
        b = 255 - (wheel_pos * 3);
        return ((uint32_t)(r) << 16) | ((uint32_t)(g) << 8) | (uint32_t)(b);
    }

    wheel_pos -= 170;
    r = wheel_pos * 3;
    g = 255 - (wheel_pos * 3);
    b = 0;
    
    return ((uint32_t)(r) << 16) | ((uint32_t)(g) << 8) | (uint32_t)(b);
}