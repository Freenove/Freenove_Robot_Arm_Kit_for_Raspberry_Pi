#ifndef FREENOVE_WS2812_H
#define FREENOVE_WS2812_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>

typedef struct ws2812_instance ws2812_instance_t;

ws2812_instance_t* begin(int gpio_pin, int leds);
void stop(ws2812_instance_t* instance);
void setBrightness(ws2812_instance_t* instance, uint8_t brightness);
void setPixelColor(ws2812_instance_t* instance, unsigned int index, uint8_t r, uint8_t g, uint8_t b);
int numPixels(ws2812_instance_t* instance);
void show(ws2812_instance_t* instance);
uint32_t wheel(uint8_t wheel_pos);

#ifdef __cplusplus
}
#endif

#endif