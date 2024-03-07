

class MessageParser:
    def __init__(self):
        self.inputCommandArray = []
        self.commandArray = []
        self.stringParameter = []
        self.floatParameter = []
        self.intParameter = []
        self.commandChar = None
        
    def parser(self, msg):
        self.clearParameters()                                         
        inputStringTemp = msg.strip()                                 
        self.inputCommandArray = inputStringTemp.split(" ")            
        for i in self.inputCommandArray:                          
            self.commandArray.append(i[0:1])
            self.stringParameter.append(i[1:])
        self.commandChar = self.commandArray[0][0:1]                   
        try:
            self.floatParameter = [float(x) for x in self.stringParameter]  
            self.intParameter = [round(x) for x in self.floatParameter]    
        except:
            pass
        
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
    print(msg.inputCommandArray)
    print(msg.commandArray)
    print(msg.stringParameter)
    print(msg.floatParameter)
    print(msg.intParameter)
    print(msg.commandChar)
    

