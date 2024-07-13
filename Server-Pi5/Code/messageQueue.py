# -*- coding: utf-8 -*-
#!/usr/bin/env python

class MessageQueue:
    def __init__(self):
        self.items = []

    def put(self, item):
        self.items.append(item)  #Data is sent to the message queue

    def get(self):
        if self.empty():
            return None
        return self.items.pop(0) #Returns the first data

    def gets(self):
        if self.empty():
            return None
        return self.items
        
    def delete(self, index):     #Delete the data corresponding to the index number
        if self.empty() == False:
            del self.items[index]

    def len(self):
        return len(self.items)   #Returns the length of the message queue

    def empty(self):
        return self.len() == 0   #Return True if the message queue is empty
    
    def clear(self):
        self.items.clear()       #Clear message queue
    
    def end(self):          
        data = self.items[-1]    #Gets data at the end of the message queue
        return data
        
if __name__ == '__main__':
    myQueue = MessageQueue()                #Request a message queue object
    myQueue.clear()                         #Clear the message queue
    for i in range(10):
        myQueue.put(str(i))                 #Feed the message queue 0-9
    while myQueue.empty() is not True:
        print(myQueue.get())                #Get the contents of the message queue and print it
    print(myQueue.empty())
