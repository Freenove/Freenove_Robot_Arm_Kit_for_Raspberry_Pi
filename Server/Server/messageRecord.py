# -*- coding: utf-8 -*-
#!/usr/bin/env python

import time
import json
import os

class MessageRecord:
    #初始化函数，将要保存的配置信息直接写入下面的数组中即可。格式: '字符串' : 数据(整型/浮点型)
    def __init__(self):
        #self.jsonData = {}        #空白也可以，预先写入值也行
        self.jsonData = {
            "Original Height" : 90.0,
            "Ground Height" : 0.0,
            "Clamp Length" : 15.0,
            "Pen Height" : 0.0,
            "A4988 CLK" : 1000,
            "A4988 MSx" : 5,
            "Home Angle Offset" : [0.0, 0.0, 0.0],
            "Sensor Pulse Offset" : [0.0, 0.0, 0.0],
            "Point 1" : [0.0, 0.0, 0.0],
            "Point 2" : [0.0, 0.0, 0.0],
            "Point 3" : [0.0, 0.0, 0.0],
            "Point 4" : [0.0, 0.0, 0.0],
            "Plane X-Z" : [0.0, 0.0, 0.0, 0.0],
            "Plane Y-Z" : [0.0, 0.0, 0.0, 0.0],
            "Home point" : [0.0, 200.0, 45.0],
            "Arm State" : [0, 0, 0, 0, 0, 0, 0, 0, 0]       
            #加载机械臂配置状态信息（第一位代表传感器校准，第二位是底面高度设置，
            #第三位是夹具长度设置，第四位是home点原始位置坐标设置，第五位是home点角度偏移校准，
            #第六到九位是point1-point4坐标校准
        }
        self.fileInit()

    #数据查找函数
    def findData(self, targetValue):
        if targetValue in self.jsonData:
            return True
        else:
            return False
        
    #指定文件删除函数
    def deleteFile(self, filePath):
        try:
            os.remove(filePath)
        except OSError as e:
            print(f"The file '{e}' was not successfully deleted.")
            
    #文件初始化函数，如果文件存在，且文件的对象个数和self.jsonData的对象数目相等，则直接读取本地文件。对象数目不相等，或者文件不存在，则直接新建并写入json文件
    def fileInit(self):
        if os.path.exists("Parameter.json") is True:
            with open("Parameter.json", "r", encoding='utf-8') as fp:
                data = json.load(fp)
                if len(data) == len(self.jsonData):
                    self.readJsonFile()
                else:
                    self.deleteFile("Parameter.json")
                    self.writeJsonFile()
        else:
            self.writeJsonFile()
    
    #读取本地json文件，并将参数赋值给self.jsonData
    def readJsonFile(self):
        with open("Parameter.json", "r", encoding='utf-8') as fp: #以读的方式打开文件，执行操作后会自动关闭文件
            self.jsonData = json.load(fp)
    
    #将self.jsonData转码为json格式，并写入本地json文件
    def writeJsonFile(self):
        with open("Parameter.json", "w", encoding='utf-8') as fp: #以写的方式打开文件，执行操作后会自动关闭文件
            json.dump(self.jsonData, fp, indent=4)
    
    #读取本地json文件中，任意一个对象的参数信息
    def readJsonObject(self, objectName):                         
        try:
            return self.jsonData[str(objectName)]
        except:
            print(f"Read the Json: '{objectName}' does not exist." )
    
    #给self.jsonData中任意对象赋值，并写入本地json文件
    def writeJsonObject(self, objectName, data):  
        try:
            self.jsonData[str(objectName)] = data
            self.writeJsonFile()
        except:
            print(f"Write the Json: '{objectName}' does not exist." )
    
    
if __name__ == '__main__':
    c = MessageRecord()
    c.deleteFile("Parameter.json")
   
    c.writeJsonObject("Original Height", 90.0)
    c.writeJsonObject("Ground Height", 0.0)
    c.writeJsonObject("Clamp Length", 15.0)
    c.writeJsonObject("Pen Height" , 0.0)
    c.writeJsonObject("A4988 CLK", 1000)
    c.writeJsonObject("A4988 MSx", 5)
    c.writeJsonObject("Home Angle Offset", [0.0, 0.0, 0.0])
    c.writeJsonObject("Sensor Pulse Offset", [0.0, 0.0, 0.0])
    c.writeJsonObject("Point 1", [0.0, 0.0, 0.0])
    c.writeJsonObject("Point 2", [0.0, 0.0, 0.0])
    c.writeJsonObject("Point 3", [0.0, 0.0, 0.0])
    c.writeJsonObject("Point 4", [0.0, 0.0, 0.0])
    c.writeJsonObject("Plane X-Z", [0.0, 0.0, 0.0, 0.0])
    c.writeJsonObject("Plane Y-Z", [0.0, 0.0, 0.0, 0.0])
    c.writeJsonObject("Home point", [0.0, 200.0, 45.0])
    c.writeJsonObject("Arm State", [0, 0, 0, 0, 0, 0, 0, 0, 0])
    
    print("Original Height:", c.readJsonObject("Original Height"))
    print("Ground Height:", c.readJsonObject("Ground Height"))
    print("Clamp Length:", c.readJsonObject("Clamp Length"))
    print("Pen Height:", c.readJsonObject("Pen Height"))
    print("A4988 CLK:", c.readJsonObject("A4988 CLK"))
    print("A4988 MSx:", c.readJsonObject("A4988 MSx"))
    print("Home Angle Offset:", c.readJsonObject("Home Angle Offset"))
    print("Sensor Pulse Offset:", c.readJsonObject("Sensor Pulse Offset"))
    print("Point 1:", c.readJsonObject("Point 1"))
    print("Point 2:", c.readJsonObject("Point 2"))
    print("Point 3:", c.readJsonObject("Point 3"))
    print("Point 4:", c.readJsonObject("Point 4"))
    print("Plane X-Z:", c.readJsonObject("Plane X-Z"))
    print("Plane Y-Z:", c.readJsonObject("Plane Y-Z"))
    print("Home point:", c.readJsonObject("Home point"))
    print("Arm State:", c.readJsonObject("Arm State"))
