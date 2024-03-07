import os
import sys
import time

flag=0x00
for x in range(1,4):
    if os.system("sudo apt-get update") == 0:
        flag=flag | 0x01
        break
for x in range(1,4):
    if os.system("sudo apt install python3-pip") == 0:
        flag=flag | 0x02
        break
for x in range(1,4):
    if os.system("sudo python3 -m pip install --upgrade pip --user") == 0:
        flag=flag | 0x04
        break
for x in range(1,4):
    if os.system("sudo pip3 install PyQt5==5.15.10") == 0:
        if os.system("sudo apt install pyqt5*") == 0:
            flag=flag | 0x08
            break
for x in range(1,4):
    if os.system("sudo pip3 install pyinstaller==6.4.0") == 0:
        flag=flag | 0x10
        break
for x in range(1,4):
    if os.system("sudo pip3 install numpy") == 0:
        flag=flag | 0x20
        break
for x in range(1,4):
    if os.system("sudo apt install libopencv-dev python3-opencv") == 0:
            flag=flag | 0x40
            break
for x in range(1,4):
    if os.system("sudo apt-get install dbus-x11") == 0:
        break
if flag==0x7f:
        #os.system("gsettings set org.gnome.desktop.interface font-name 'FontName 9'")
        os.system("sudo pip3 list")
        print("\nAll libraries installed successfully")
else:
    if flag&0x01==0x00:
        print("\nsudo apt-get update failed.")
    if flag&0x02==0x00:
        print("\nsudo apt install python3-pip failed.")
    if flag&0x04==0x00:
        print("\nsudo python3 -m pip install --upgrade pip --user failed.")
    if flag&0x08==0x00:
        print("\nsudo pip3 install PyQt5 failed.")   
    if flag&0x10==0x00:
        print("\nsudo apt install pyinstaller failed.")
    if flag&0x20==0x00:
        print("\nsudo pip3 install numpy failed.")
    if flag&0x40==0x00:
        print("\nsudo apt install libopencv-dev python3-opencv failed.")
    print ("\nSome libraries have not been installed yet. Please run 'sudo python setup.py' again")