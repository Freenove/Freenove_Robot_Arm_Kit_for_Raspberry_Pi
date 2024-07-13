import os
import sys
import time
os.system("cd /usr/bin && sudo rm python && sudo ln -s python3 python")
flag=0x00
for x in range(1,4):
    if os.system("sudo apt-get update") == 0:
        flag=flag | 0x01
        break
for x in range(1,4):
    if os.system("sudo apt-get install pigpio") == 0:
        flag=flag | 0x02
        break     
for x in range(1,4):
    if os.system("cd ./Libs/rpi-ws281x-python/library && sudo python3 setup.py install") == 0:
        flag=flag | 0x04
        break
for x in range(1,4):
    if os.system("cd ./Libs/pwm-pi5 && sudo python3 setup.py") == 0:
        flag=flag | 0x08
        break
        
if flag==0x0f:
        print("\nNow the installation is successful.")
        print("\nPlease restart raspberry pi")
else:
    if flag&0x01==0x00:
        print("\napt-get update failed.")
    if flag&0x02==0x00:
        print("\npigpio install failed.")
    if flag&0x04==0x00:
        print("\nrpi-ws281x-python install failed.")
    if flag&0x08==0x00:
        print("\npwm-pi5 install failed.")
    print ("\nSome libraries have not been installed yet. Please run 'sudo python setup.py' again")

