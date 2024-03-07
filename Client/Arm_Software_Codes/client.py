import socket
import messageQueue

class Client:
    def __init__(self):
        self.port = 5000  
        self.ip = ''
        self.connect_flag = False
        self.data_queue = messageQueue.MessageQueue() 
        self.data_queue.clear()                      

    def connect(self, ip):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
            self.client_socket.settimeout(3.0)                                     
            self.client_socket.connect((ip, int(self.port)))                        
            self.client_socket.settimeout(None)                                      
            self.connect_flag = True                                                 
        except:
            self.client_socket.close()                                              
            self.connect_flag = False                                               
        return self.connect_flag                                                 

    def disconnect(self):
        self.connect_flag = False        
        self.client_socket.shutdown(2)     
        self.client_socket.close()       

    def send_messages(self, data):
        try:
            if self.connect_flag:
                self.client_socket.send(data.encode('utf-8'))
        except:
            print("Client send data failed.")

    def receive_messages(self):
        while True:
            try:
                data = self.client_socket.recv(1024).decode('utf-8')
                if data != '':
                    self.data_queue.put(data)
                else:
                    self.connect_flag = False
            except:
                self.connect_flag = False
                break


if __name__ == '__main__':
    wifi = Client()
    wifi.connect("192.168.1.139")
    wifi.send_messages("Hello world.")
    while True:
        if wifi.receive_messages()!= "":
            pass
        else:
            break
    wifi.disconnect()
    print("Close tcp.")
    pass












































