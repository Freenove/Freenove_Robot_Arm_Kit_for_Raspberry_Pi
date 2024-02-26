import socket
import messageQueue

class Client:
    def __init__(self):
        self.port = 5000  # 服务器端口
        self.ip = ''
        self.connect_flag = False
        self.data_queue = messageQueue.MessageQueue() # 申请一个消息队列用来处理数据
        self.data_queue.clear()                       # 将消息队列清空

    def connect(self, ip):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # 创建一个基于IPv4和TCP协议的套接字对象，用来网络通讯
            self.client_socket.settimeout(3.0)                                       # 设置连接超时时间为3秒
            self.client_socket.connect((ip, int(self.port)))                         # 向目标IP和端口号发起连接（阻塞状态，连接成功则正常运行，不成功则抛出异常）
            self.client_socket.settimeout(None)                                      # 取消连接超时时间（不取消，会导致socket只能连接3秒就断开，这函数明显不合理，先这样用）
            self.connect_flag = True                                                 # 连接状态标志位置位
        except:
            self.client_socket.close()                                               # 关闭套接字连接，并释放系统资源
            self.connect_flag = False                                                # 连接状态标志位取消置位
        return self.connect_flag                                                     # 返回连接状态标志位

    def disconnect(self):
        self.connect_flag = False          # 连接状态标志位取消置位
        self.client_socket.shutdown(2)     # 关闭套接字连接，停止发送和接收数据，套接字对象仍然存在
        self.client_socket.close()         # 关闭套接字连接，并释放系统资源

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












































