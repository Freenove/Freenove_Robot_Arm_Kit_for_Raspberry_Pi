# -*- coding: utf-8 -*-
#!/usr/bin/env python

class MessageParser:
    def __init__(self):
        self.inputCommandArray = []
        self.commandArray = []
        self.stringParameter = []
        self.floatParameter = []
        self.intParameter = []
        self.commandChar = None
        
    def parser(self, msg):
        self.clearParameters()                                          #清空命令解析数组
        inputStringTemp = msg.strip()                                   #删除头尾空格
        self.inputCommandArray = inputStringTemp.split(" ")             #将指令按空格拆分开并存进list 
        for i in self.inputCommandArray:                                #将列表元素解析并存入不同的list中
            self.commandArray.append(i[0:1])
            self.stringParameter.append(i[1:])
        self.commandChar = self.commandArray[0][0:1]                    #取命令第一个字节
        if self.commandChar == "G" or self.commandChar == "S":
            self.floatParameter = [float(x) for x in self.stringParameter]  #将参数全部转化为浮点型
            self.intParameter = [round(x) for x in self.floatParameter]     #将参数全部转化为整形
        else:
            print("messageParser.py, line 24, error command.")
        
    def clearParameters(self):
        self.inputCommandArray.clear()
        self.commandArray.clear()
        self.stringParameter.clear()
        self.floatParameter.clear()
        self.intParameter.clear()
        self.commandChar = None

if __name__ == '__main__':
    msg = MessageParser()
    msg.parser("G1.0 X1.0 Y2.3 Z4.55 F1500")
    print(msg.commandArray)
    print(msg.stringParameter)
    print(msg.floatParameter)
    print(msg.intParameter)
    print(msg.commandChar)
    

