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
    if os.system("python3 -m pip install --upgrade pip --user") == 0:
        flag=flag | 0x04
        break
for x in range(1,4):
	if os.system("sudo pip3 install PyQt5") == 0:
		flag=flag | 0x08
		break
for x in range(1,4):
	if os.system("sudo apt install pyqt5*") == 0:
		flag=flag | 0x10
		break
for x in range(1,4):
    if os.system("pip3 install Pillow") == 0:
        flag=flag | 0x20
        break
for x in range(1,4):
    if os.system("pip3 install numpy") == 0:
        flag=flag | 0x40
        break
for x in range(1,4):
    if os.system("sudo apt install libopencv-dev python3-opencv") == 0:
            flag=flag | 0x80
            break
for x in range(1,4):
    if os.system("sudo apt-get install dbus-x11") == 0:
        break
        
        
if flag==0xff:
        os.system("gsettings set org.gnome.desktop.interface font-name 'FontName 10'")
        os.system("pip3 list")
        print("\nAll libraries installed successfully")
else:
    if flag&0x01==0x00:
        print("\nsudo apt-get update failed.")
    if flag&0x02==0x00:
        print("\nsudo apt install python3-pip failed.")
    if flag&0x04==0x00:
        print("\npython3 -m pip install --upgrade pip --user failed.")
    if flag&0x08==0x00:
        print("\nsudo pip3 install PyQt5 failed.")   
    if flag&0x10==0x00:
        print("\nsudo apt install pyqt5* failed.")
    if flag&0x20==0x00:
        print("\npip3 install Pillow failed.")
    if flag&0x40==0x00:
        print("\npip3 install numpy failed.")
    if flag&0x80==0x00:
        print("\nsudo apt install libopencv-dev python3-opencv failed.")
    print ("\nSome libraries have not been installed yet. Please run 'sudo python setup.py' again")