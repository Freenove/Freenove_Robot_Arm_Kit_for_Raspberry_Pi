
class MessageQueue:
    def __init__(self):
        self.items = []

    def put(self, item):
        self.items.append(item)

    def get(self):
        if self.empty():
            return None
        return self.items.pop(0) 

    def gets(self):
        if self.empty():
            return None
        return self.items

    def delete(self, index):
        if self.empty() == False:
            del self.items[index]

    def len(self):
        return len(self.items)  

    def empty(self):
        return self.len() == 0 
    
    def clear(self):
        self.items.clear()      
        
if __name__ == '__main__':
    myQueue = MessageQueue()
    myQueue.clear()
    for i in range(10):
        myQueue.put(str(i))
    while myQueue.empty() is not True:
        print(myQueue.get())
    print(myQueue.empty())
