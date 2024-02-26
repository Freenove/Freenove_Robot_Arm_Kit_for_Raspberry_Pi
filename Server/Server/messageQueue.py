# -*- coding: utf-8 -*-
#!/usr/bin/env python

class MessageQueue:
    def __init__(self):
        self.items = []

    def put(self, item):
        self.items.append(item)

    def get(self):
        if self.empty():
            return None
        return self.items.pop(0) #返回消息队列的第一个数据

    def gets(self):
        if self.empty():
            return None
        return self.items
        
    def delete(self, index):     #删除消息队列中的数据
        if self.empty() == False:
            #self.items.pop(index)
            del self.items[index]

    def len(self):
        return len(self.items)   #返回消息队列的长度

    def empty(self):
        return self.len() == 0   #数据为空则返回True
    
    def clear(self):
        self.items.clear()       #清空消息队列
    
    def end(self):
        data = self.items[-1]
        return data
        
if __name__ == '__main__':
    myQueue = MessageQueue()
    myQueue.clear()
    for i in range(10):
        myQueue.put(str(i))
    while myQueue.empty() is not True:
        print(myQueue.get())
    print(myQueue.empty())
