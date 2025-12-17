#include "freenove_ws2812.h"
#include <stdio.h>
#include <unistd.h>
#include <signal.h>
#include <stdlib.h>

#define GPIO_PIN 18
#define LED_NUMBER 8

static ws2812_instance_t* led_strip = NULL;

void signal_handler(int sig) {
    printf("\nReceived signal %d, cleaning up...\n", sig);
    if (led_strip) {
        stop(led_strip);
    }
    exit(0);
}

int main() {
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);

    led_strip = begin(GPIO_PIN, LED_NUMBER);
    if (!led_strip) {
        printf("Failed to initialize\n");
        return -1;
    }
    
    printf("Red LED\n");
    for (int i = 0; i < LED_NUMBER; i++) {
        setPixelColor(led_strip, i, 0, 255, 0);
        show(led_strip);
        usleep(100000);
    }

    printf("Green LED\n");
    for (int i = 0; i < LED_NUMBER; i++) {
        setPixelColor(led_strip, i, 255, 0, 0);
        show(led_strip);
        usleep(100000);
    }
    
    printf("Blue LED\n");
    for (int i = 0; i < LED_NUMBER; i++) {
        setPixelColor(led_strip, i, 0, 0, 255);
        show(led_strip);
        usleep(100000);
    }

    printf("Rainbow LED\n");
    for(int j = 0; j < 255; j++) {
        for (int i = 0; i < LED_NUMBER; i++) {
            uint32_t color = wheel((i * 256 / LED_NUMBER + j) & 255);
            uint8_t r = (color >> 16) & 255;
            uint8_t g = (color >> 8) & 255;
            uint8_t b = color & 255;
            setPixelColor(led_strip, i, r, g, b);
        }
        show(led_strip);
        usleep(10000);
    }

    printf("Breathing LED\n");
    for(int i=0; i<LED_NUMBER; i++){
        setPixelColor(led_strip, i, 0, 0, 255);
    }
    for(int i=0; i<255; i++){
        setBrightness(led_strip, i);
        show(led_strip);
        usleep(10000);
    }
    for(int i=255; i>=0; i--){
        setBrightness(led_strip, i);
        show(led_strip);
        usleep(10000);
    }

    stop(led_strip);
    printf("Done\n");
    return 0;
}