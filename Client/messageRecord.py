import time
import json
import os
class MessageRecord:
    def __init__(self):
        self.python_data = {
            "remote ip": "192.168.1.253",
            "position point": ['0.0', '200.0', '45.0'],
            "axis point 1": ['0.0', '0.0', '0.0'],
            "axis point 2": ['0.0', '0.0', '0.0'],
            "axis point 3": ['0.0', '0.0', '0.0'],
            "axis point 4": ['0.0', '0.0', '0.0'],
            "axis point 5": ['0.0', '0.0', '0.0'],
            "pen height": "0.0",
            "frequency": "1000",
            "ground height": "0.0",
            "clamp length": "15.0",
            "clamp height": "45.0",
        }
        self.fileInit()

    # 指定文件删除函数
    def deleteFile(self, file_path):
        try:
            os.remove(file_path)
        except OSError as e:
            print(f"The file '{e}' was not successfully deleted.")
    # 文件初始化函数，如果文件存在，且文件的对象个数和self.python_data的对象数目相等，则直接读取本地文件。对象数目不相等，或者文件不存在，则直接新建并写入json文件
    def fileInit(self):
        if os.path.exists("Parameter.json") is True:
            with open("Parameter.json", "r", encoding='utf-8') as fp:
                data = json.load(fp)
                if len(data) == len(self.python_data):
                    self.readJsonFile()
                else:
                    self.deleteFile("Parameter.json")
                    self.writeJsonFile()
        else:
            self.writeJsonFile()
    # 读取本地json文件，并将参数赋值给self.python_data
    def readJsonFile(self):
        with open("Parameter.json", "r", encoding='utf-8') as fp:  # 以读的方式打开文件，执行操作后会自动关闭文件
            self.python_data = json.load(fp)
    # 将self.python_data转码为json格式，并写入本地json文件
    def writeJsonFile(self):
        with open("Parameter.json", "w", encoding='utf-8') as fp:  # 以写的方式打开文件，执行操作后会自动关闭文件
            json.dump(self.python_data, fp, indent=4)
    # 读取本地json文件中，任意一个对象的参数信息
    def readJsonObject(self, objectName):
        #self.readJsonFile()
        try:
            return self.python_data[str(objectName)]
        except:
            print(f"Read the Json: '{objectName}' does not exist.")
    # 给self.python_data中任意对象赋值，并写入本地json文件
    def writeJsonObject(self, objectName, data):
        try:
            self.python_data[str(objectName)] = data
            self.writeJsonFile()
        except:
            print(f"Write the Json: '{objectName}' does not exist.")

    def read_remote_ip(self):
        return self.readJsonObject("remote ip")
    def read_position_point(self):
        return self.readJsonObject("position point")
    def read_axis_point_1(self):
        return self.readJsonObject("axis point 1")
    def read_axis_point_2(self):
        return self.readJsonObject("axis point 2")
    def read_axis_point_3(self):
        return self.readJsonObject("axis point 3")
    def read_axis_point_4(self):
        return self.readJsonObject("axis point 4")
    def read_axis_point_5(self):
        return self.readJsonObject("axis point 5")
    def read_pen_height(self):
        return self.readJsonObject("pen height")
    def read_a4988_frequency(self):
        return self.readJsonObject("frequency")
    def read_ground_height(self):
        return self.readJsonObject("ground height")
    def read_clamp_length(self):
        return self.readJsonObject("clamp length")
    def read_clamp_height(self):
        return self.readJsonObject("clamp height")

    def write_remote_ip(self, ip_address):
        self.writeJsonObject("remote ip", str(ip_address))
    def write_position_point(self, x, y, z):
        self.writeJsonObject("position point", [str(x), str(y), str(z)])
    def write_axis_point_1(self, x, y, z):
        self.writeJsonObject("axis point 1", [str(x), str(y), str(z)])
    def write_axis_point_2(self, x, y, z):
        self.writeJsonObject("axis point 2", [str(x), str(y), str(z)])
    def write_axis_point_3(self, x, y, z):
        self.writeJsonObject("axis point 3", [str(x), str(y), str(z)])
    def write_axis_point_4(self, x, y, z):
        self.writeJsonObject("axis point 4", [str(x), str(y), str(z)])
    def write_axis_point_5(self, x, y, z):
        self.writeJsonObject("axis point 5", [str(x), str(y), str(z)])
    def write_pen_height(self, data):
        self.writeJsonObject("pen height", str(data))
    def write_a4988_frequency(self, data):
        self.writeJsonObject("frequency", str(data))
    def write_ground_height(self, height):
        self.writeJsonObject("ground height", str(height))
    def write_clamp_length(self, length):
        self.writeJsonObject("clamp length", str(length))
    def write_clamp_height(self, height):
        self.writeJsonObject("clamp height", str(height))

    def write_json_default_parameter(self):
        self.write_position_point("0.0", "200.0", "45.0")
        self.write_axis_point_1("0.0", "0.0", "0.0")
        self.write_axis_point_2("0.0", "0.0", "0.0")
        self.write_axis_point_3("0.0", "0.0", "0.0")
        self.write_axis_point_4("0.0", "0.0", "0.0")
        self.write_axis_point_5("0.0", "0.0", "0.0")
        self.write_pen_height("0.0")
        self.write_a4988_frequency("1000")
        self.write_ground_height("0.0")
        self.write_clamp_length("15.0")
        self.write_clamp_height("45.0")

if __name__ == '__main__':
    c = MessageRecord()

    c.write_remote_ip("192.168.1.253")
    c.write_position_point("0.0", "200.0", "45.0")
    c.write_axis_point_1("0.0", "0.0", "0.0")
    c.write_axis_point_2("0.0", "0.0", "0.0")
    c.write_axis_point_3("0.0", "0.0", "0.0")
    c.write_axis_point_4("0.0", "0.0", "0.0")
    c.write_axis_point_5("0.0", "0.0", "0.0")
    c.write_pen_height("0.0")
    c.write_a4988_frequency("1000")
    c.write_ground_height("0.0")
    c.write_clamp_length("15.0")
    c.write_clamp_height("45.0")

    print(c.read_remote_ip())
    print(c.read_position_point())
    print(c.read_axis_point_1())
    print(c.read_axis_point_2())
    print(c.read_axis_point_3())
    print(c.read_axis_point_4())
    print(c.read_axis_point_5())
    print(c.read_pen_height())
    print(c.read_a4988_frequency())
    print(c.read_ground_height())
    print(c.read_clamp_length())
    print(c.read_clamp_height())
