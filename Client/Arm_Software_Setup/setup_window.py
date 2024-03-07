import os
import sys
import time

flag=0x00
for x in range(1,4):
    if os.system("python -m pip install --upgrade pip --user") == 0:
        flag=flag | 0x01
        break
for x in range(1,4):
    if os.system("pip3 install PyQt5==5.15.4") == 0:
        flag=flag | 0x02
        break
for x in range(1,4):
    if os.system("pip3 install opencv-python==4.5.5.64") == 0:
        if os.system("pip3 install opencv-contrib-python==4.5.5.64") == 0:
            flag=flag | 0x04
            break
for x in range(1,4):
    if os.system("pip3 install numpy==1.24.1") == 0:
        flag=flag | 0x08
        break 
for x in range(1,4):
    if os.system("pip3 install pyinstaller==5.7.0") == 0:
        flag=flag | 0x10
        break 
if flag==0x1f:
        os.system("pip3 list")
        print("\nAll libraries installed successfully")
else:
    if flag&0x01==0x00:
        print("\naPip install --upgrade pip failed.")
    if flag&0x02==0x00:
        print("\nPyQt5 install failed.")
    if flag&0x04==0x00:
        print("\nOpencv install failed.")
    if flag&0x08==0x00:
        print("\nNumpy install failed.")
    if flag&0x08==0x00:
        print("\nPyinstaller install failed.")
    print ("\nSome libraries have not been installed yet. Please run 'sudo python setup.py' again")

