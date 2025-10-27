# -*- coding: utf-8 -*-
#!/usr/bin/env python

NODE="/sys/class/pwm/pwmchip2"  
PWM_CHANNELS=("0" "1" "2" "3")  
PIN_FUNCTIONS=("a0" "a0" "a0" "a0" "a3" "a3") 
  
function parse_args {  
    if [ "$#" -ne 3 ]; then  
        usage  
        exit 1  
    fi  
  
    local PIN=$1  
    local PERIOD=$2  
    local DUTY_CYCLE=$3 
  
    if ! [[ "$PIN" =~ ^(12|13|14|15|18|19)$ ]]; then  
        echo "Unknown pin $PIN."  
        exit 1  
    fi  
  
    if [ "$PERIOD" = "off" ]; then  
        disable_pwm "$PIN"  
        exit 0  
    fi  
  
    if ! [[ "$PERIOD" =~ ^[0-9]+$ ]] || ! [[ "$DUTY_CYCLE" =~ ^[0-9]+$ ]]; then  
        usage  
        exit 1  
    fi  
  
    setup_pwm "$PIN" "$PERIOD" "$DUTY_CYCLE"  
}  
  
function usage {  
    printf "Usage: $0 <channel> <period> <duty_cycle>\n"  
    printf "    channel - one of 12, 13, 14, 15, 18 or 19\n"  
    printf "    period - PWM period in nanoseconds (or 'off' to disable PWM)\n"  
    printf "    duty_cycle - Duty Cycle (on period) in nanoseconds\n"  
}  
  
function disable_pwm {  
    local PIN=$1  
    local CHANNEL=${PWM_CHANNELS[$(($PIN - 12))]}  
  
    if [ -d "$NODE/pwm$CHANNEL" ]; then  
        sudo sh -c "echo 0 > $NODE/pwm$CHANNEL/enable"  
        sudo sh -c "echo $CHANNEL > $NODE/unexport"  
        pinctrl set $PIN no  
    fi  
}  
  
function setup_pwm {  
    local PIN=$1  
    local PERIOD=$2  
    local DUTY_CYCLE=$3  
    local CHANNEL=${PWM_CHANNELS[$(($PIN - 12))]}  
    local FUNC=${PIN_FUNCTIONS[$(($PIN - 12))]}  
  
    if [ ! -d "$NODE/pwm$CHANNEL" ]; then  
        sudo sh -c "echo $CHANNEL > $NODE/export"  
    fi  
  
    sudo sh -c "echo 0 > $NODE/pwm$CHANNEL/enable"  
    sudo sh -c "echo $PERIOD > $NODE/pwm$CHANNEL/period"  
  
    if [ $? -ne 0 ]; then  
        sudo sh -c "echo $DUTY_CYCLE > $NODE/pwm$CHANNEL/duty_cycle"  
        sudo sh -c "echo $PERIOD > $NODE/pwm$CHANNEL/period"  
    else  
        sudo sh -c "echo $DUTY_CYCLE > $NODE/pwm$CHANNEL/duty_cycle"  
    fi  
  
    sudo sh -c "echo 1 > $NODE/pwm$CHANNEL/enable"  
    pinctrl set $PIN $FUNC  
  
    echo "GPIO $PIN (Ch. $CHANNEL, Fn. $FUNC) set to $PERIOD ns, $DUTY_CYCLE ns."  
}  
  
parse_args "$@"