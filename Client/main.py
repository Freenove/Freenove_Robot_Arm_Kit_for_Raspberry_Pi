import sys
import os
import threading
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from fileDialogHelper import FileDialogHelper
import cv2
from client import Client
from ui.ui_arm import Ui_Arm
from configuration import Configuration
from led import LED
import messageThread
import messageParser
import messageRecord
import messageQueue
import command
import numpy as np
from datetime import datetime
import platform


class myClientWindow(QMainWindow, Ui_Arm):
    # 定义一些信号通道用来传递数据
    ui_arm_btn_connect = QtCore.pyqtSignal(str)   # 用来给线程设置UI界面中，控件pushButton_Arm_Connect的显示内容
    threading_cmd = QtCore.pyqtSignal(str)        # 用来发送线程中的指令

    def __init__(self, parent=None):
        super(myClientWindow, self).__init__(parent)
        self.setupUi(self)  # 初始化界面
        self.setFixedSize(1074, 617)
        self.binary_img = None
        self.contour_img = None
        self.hierarchy_data = None
        self.configurationWindow = None
        self.read_cmd_handling = None
        self.message_handling = None
        self.folder_path = None
        self.raw_img = None
        self.gray_img = None
        self.axis_paint_function = None
        self.ledWindow = None

        self.main_position_mode_length = 0.0  # 测试模式长度
        self.main_clamp_mode_length = 40.0  # 笔具模式长度
        self.main_servo_mode_length = 50.0  # 夹爪模式长度
        self.client = Client()  # 申请socket对象
        self.record = messageRecord.MessageRecord()  # 参数保存对象
        self.label_Arm_Video.setScaledContents(False)  # 不缩放（缩放会导致图片拉伸变形）
        ip_validator = QRegExpValidator(QRegExp('^((2[0-4]\d|25[0-5]|\d?\d|1\d{2})\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)$'))  # 4位，每一位用'.'隔开，每一位范围0-255
        self.lineEdit_Arm_IP_Address.setValidator(ip_validator)  # IP地址输入框格式限制
        servo_validator = QRegExpValidator(QRegExp('^(?:[1-9][0-9]?|1[0-7][0-9]?|180)$'))
        self.lineEdit_Arm_Servo_Angle_Value.setValidator(servo_validator)
        self.lineEdit_Arm_IP_Address.setText(self.record.read_remote_ip())  # 从文件中读取IP地址
        self.client.ip = self.lineEdit_Arm_IP_Address.text()  # 获取界面的IP地址
        print("Remote IP: " + self.client.ip)  # 打印IP地址
        self.message_parser = messageParser.MessageParser()  # 指令解析函数
        self.gcode_command = messageQueue.MessageQueue()  # 创建一个消息队列，用来存储G指令
        self.painter_point = messageQueue.MessageQueue()  # 创建一个消息队列，用来存储画布坐标点信息
        self.send_g_code_state = False  # 判断什么时候发送g代码
        self.cmd = command.Command()  # 指令集
        self.client_busy = False  # TCP忙标志位
        self.original_position_axis = self.record.read_position_point()  # 获取本地存储中的home点的值
        self.ui_arm_show_label_axis(self.original_position_axis)  # 显示机械臂末端坐标点位置
        self.record_last_command = None  # 用来记录最后的命令
        self.record_area_data_queue = messageQueue.MessageQueue()  # 用来记录手动操作的指令
        self.threshold_value = 100  # 二值化阈值
        self.gauss_value = 3  # 高斯模糊值
        self.sharpen_value = 5  # 锐化值
        self.img_flag = 0  # 图片类型标识位
        self.last_axis_point = [0, 200]  # 上位机home点坐标
        self.label_videl_size = [self.label_Arm_Video.width(), self.label_Arm_Video.height()]  # 控件显示框的大小
        self.axis_map_x = [-100, 100]  # 坐标转G代码X轴范围设置
        self.axis_map_y = [250, 150]  # 坐标转G代码Y轴范围设置
        self.lastPoint = [0, 0]  # 用来记录最后界面画布坐标点
        self.currentPoint = [0, 0]  # 用来记录当前界面画布坐标点
        self.isDrawing = False  # 绘制规律标识
        self.painter_line_style = 0  # 线段和曲线切换标识
        self.contours_data = None  # 用来记录图案轮廓数据
        self.white_image = np.zeros((self.label_videl_size[1], self.label_videl_size[0], 3), dtype=np.uint8)  # 创建一个600x300的黑色图片
        self.white_image[:, :, :] = [255, 255, 255]  # 将图片设置为白色
        img = QImage(self.white_image.data.tobytes(), self.white_image.shape[1], self.white_image.shape[0], QImage.Format_RGB888)  # 将图片转化为QImage格式
        self.label_Arm_Video.setPixmap(QPixmap.fromImage(img))  # 加载到显示区上
        self.original_label_img = self.white_image.copy()  # 用来临时存放画线或者画轨迹模式下的原始图片
        self.line_curves_count = 1  # 记录有多少条线
        self.current_line_curves = 0  # 记录当前正在绘制的是第几条线
        self.angle_value = 90  # 舵机角度值
        self.arm_switched_value = 10  # 行程切换
        self.arm_move_value = 1.0  # 行程距离
        self.arm_command_count = 0  # 下位机剩余指令数目
        self.filePath = FileDialogHelper()
        self.connect()  # 控件关联槽函数

    # 信号槽函数
    def connect(self):
        self.lineEdit_Arm_IP_Address.textChanged.connect(self.save_ip_address)  # 每次IP地址发生变化时，修改并保存IP地址，方便下次启动时读取
        self.pushButton_Arm_Connect.clicked.connect(self.btn_connect_remote_ip)  # 连接远程IP地址
        self.ui_arm_btn_connect.connect(self.ui_arm_show_btn_connect_content)  # 设置控件pushButton_Arm_Connect的显示内容
        self.threading_cmd.connect(self.socket_send)
        self.pushButton_Arm_Stop_Arm.clicked.connect(self.btn_stop_arm)  # 向下位机发送紧急制动指令
        self.pushButton_Arm_Zero_Point.clicked.connect(self.btn_move_to_zero_point)  # 控制机械臂回到零点
        self.pushButton_Arm_Load_Relax.clicked.connect(self.btn_load_relax_arm)  # 控制机械臂使能和失能
        self.pushButton_Arm_Buzzer.pressed.connect(lambda: self.btn_control_buzzer(self.pushButton_Arm_Buzzer))  # 按键控制蜂鸣器发声
        self.pushButton_Arm_Buzzer.released.connect(lambda: self.btn_control_buzzer(self.pushButton_Arm_Buzzer))  # 按键控制蜂鸣器发声
        self.pushButton_Arm_Position.clicked.connect(self.btn_move_to_position_point)  # 控制机械臂移动到home位置
        self.pushButton_Arm_Home_Up.clicked.connect(self.btn_move_to_above_home_point)  # 控制机械臂移动到home位置上方
        self.pushButton_Arm_Axis_X_Subtract.clicked.connect(lambda: self.btn_move_to_anywhere(self.pushButton_Arm_Axis_X_Subtract))  # 控制机械臂移动到任意位置
        self.pushButton_Arm_Axis_Y_Subtract.clicked.connect(lambda: self.btn_move_to_anywhere(self.pushButton_Arm_Axis_Y_Subtract))  # 控制机械臂移动到任意位置
        self.pushButton_Arm_Axis_Z_Subtract.clicked.connect(lambda: self.btn_move_to_anywhere(self.pushButton_Arm_Axis_Z_Subtract))  # 控制机械臂移动到任意位置
        self.pushButton_Arm_Axis_X_Add.clicked.connect(lambda: self.btn_move_to_anywhere(self.pushButton_Arm_Axis_X_Add))  # 控制机械臂移动到任意位置
        self.pushButton_Arm_Axis_Y_Add.clicked.connect(lambda: self.btn_move_to_anywhere(self.pushButton_Arm_Axis_Y_Add))  # 控制机械臂移动到任意位置
        self.pushButton_Arm_Axis_Z_Add.clicked.connect(lambda: self.btn_move_to_anywhere(self.pushButton_Arm_Axis_Z_Add))  # 控制机械臂移动到任意位置
        self.pushButton_Arm_Axis_Switched.clicked.connect(lambda: self.btn_move_to_anywhere(self.pushButton_Arm_Axis_Switched))  # 控制机械臂移动到任意位置
        self.pushButton_Arm_Record_Command.clicked.connect(lambda: self.btn_arm_operation(self.pushButton_Arm_Record_Command))  # 操作记录机械臂
        self.pushButton_Arm_Withdraw_Command.clicked.connect(lambda: self.btn_arm_operation(self.pushButton_Arm_Withdraw_Command))  # 操作记录机械臂
        self.pushButton_Arm_Execute_Record_Command.clicked.connect(lambda: self.btn_arm_operation(self.pushButton_Arm_Execute_Record_Command))  # 操作记录机械臂
        self.pushButton_Arm_Import_Record_Command.clicked.connect(lambda: self.btn_arm_operation(self.pushButton_Arm_Import_Record_Command))  # 操作记录机械臂
        self.pushButton_Arm_Save_Record_Command.clicked.connect(lambda: self.btn_arm_operation(self.pushButton_Arm_Save_Record_Command))  # 操作记录机械臂

        self.radioButton_Arm_Img_Mode.clicked.connect(lambda: self.radioButton_arm_select_mode(self.radioButton_Arm_Img_Mode))  # 选择机械臂绘图模式
        self.radioButton_Arm_Line_Mode.clicked.connect(lambda: self.radioButton_arm_select_mode(self.radioButton_Arm_Line_Mode))  # 选择机械臂绘图模式
        self.radioButton_Arm_Curves_Mode.clicked.connect(lambda: self.radioButton_arm_select_mode(self.radioButton_Arm_Curves_Mode))  # 选择机械臂绘图模式
        self.pushButton_Arm_Import_Picture.clicked.connect(lambda: self.set_img_action(self.pushButton_Arm_Import_Picture))  # 加载图片
        self.pushButton_Arm_Gray_Picture.clicked.connect(lambda: self.set_img_action(self.pushButton_Arm_Gray_Picture))  # 灰度图
        self.pushButton_Arm_Binaryzation_Picture.clicked.connect(lambda: self.set_img_action(self.pushButton_Arm_Binaryzation_Picture))  # 二值化
        self.pushButton_Arm_Contour_Picture.clicked.connect(lambda: self.set_img_action(self.pushButton_Arm_Contour_Picture))  # 轮廓
        self.pushButton_Arm_Clear_All.clicked.connect(lambda: self.set_img_action(self.pushButton_Arm_Clear_All))  # 清除数据
        self.pushButton_Arm_Change_Gcode.clicked.connect(lambda: self.set_img_action(self.pushButton_Arm_Change_Gcode))  # 转G代码
        self.pushButton_Arm_Execute_Gcode.clicked.connect(lambda: self.set_img_action(self.pushButton_Arm_Execute_Gcode))  # 执行G代码
        if platform.system() == "Windows":
            self.horizontalSlider_Arm_Threshold.sliderReleased.connect(lambda: self.img_slider_control(self.horizontalSlider_Arm_Threshold))  # 轮廓阈值调节
            self.horizontalSlider_Arm_Gauss.sliderReleased.connect(lambda: self.img_slider_control(self.horizontalSlider_Arm_Gauss))  # 高斯模糊调节
            self.horizontalSlider_Arm_Sharpen.sliderReleased.connect(lambda: self.img_slider_control(self.horizontalSlider_Arm_Sharpen))  # 锐化调节
            self.horizontalSlider_Arm_Pen_Height.sliderReleased.connect(lambda: self.img_slider_control(self.horizontalSlider_Arm_Pen_Height))  # 抬笔高度调节
        else:
            self.horizontalSlider_Arm_Threshold.valueChanged.connect(lambda: self.img_slider_control(self.horizontalSlider_Arm_Threshold))  # 轮廓阈值调节
            self.horizontalSlider_Arm_Gauss.valueChanged.connect(lambda: self.img_slider_control(self.horizontalSlider_Arm_Gauss))  # 高斯模糊调节
            self.horizontalSlider_Arm_Sharpen.valueChanged.connect(lambda: self.img_slider_control(self.horizontalSlider_Arm_Sharpen))  # 锐化调节
            self.horizontalSlider_Arm_Pen_Height.valueChanged.connect(lambda: self.img_slider_control(self.horizontalSlider_Arm_Pen_Height))  # 抬笔高度调节
        self.pushButton_Arm_Servo_Turn_On.clicked.connect(lambda: self.control_servo_angle(self.pushButton_Arm_Servo_Turn_On))  # 控制舵机打开
        self.pushButton_Arm_Servo_Turn_Off.clicked.connect(lambda: self.control_servo_angle(self.pushButton_Arm_Servo_Turn_Off))  # 控制舵机关闭
        self.pushButton_Arm_Parameter_UI.clicked.connect(self.configure_parameter_ui)  # 配置机械臂参数界面
        self.pushButton_Arm_Led_UI.clicked.connect(self.configure_led_ui)  # 配置机械臂彩灯界面

    # 数值映射函数，将数据从一个范围映射到另一个范围
    @staticmethod
    def map(value, fromLow, fromHigh, toLow, toHigh, num):
        return round(((toHigh - toLow) * (value - fromLow) / (fromHigh - fromLow) + toLow), num)

    # 数值限制函数，将数值限制在安全范围内
    @staticmethod
    def constrain(value, range_min, range_max):
        if value > range_max:
            value = range_max
        if value < range_min:
            value = range_min
        return value

    # 记录命令
    def record_command(self, cmd):
        self.record_last_command = cmd

    # 通过socket发送命令
    def socket_send(self, cmd):
        if self.client.connect_flag:
            if self.pushButton_Arm_Load_Relax.text() == "Relax Motor":
                self.client_busy = True
                self.client.send_messages(cmd + "\r\n")
                self.record_command(cmd)
                self.client_busy = False
            else:
                if cmd.split(" ")[0][0] == "S":
                    self.client_busy = True
                    self.client.send_messages(cmd + "\r\n")
                    self.record_command(cmd)
                    self.client_busy = False
                else:
                    print("Please press the \"Load Motor\" button first.")
        else:
            print("Connect the remote IP address first.")

    # 显示机械臂末端坐标点位置
    def ui_arm_show_label_axis(self, axis):
        self.label_Arm_Axis_X_Value.setText(str(axis[0]))  # 加载坐标点的值到界面中
        self.label_Arm_Axis_Y_Value.setText(str(axis[1]))  # 加载坐标点的值到界面中
        self.label_Arm_Axis_Z_Value.setText(str(axis[2]))  # 加载坐标点的值到界面中

    # 在指令记录区显示记录的指令内容
    def ui_arm_show_record_area(self):
        self.textEdit_Arm_Record_Area.clear()
        cmd = self.record_area_data_queue.gets()
        for i in range(self.record_area_data_queue.len()):
            self.textEdit_Arm_Record_Area.append(cmd[i])

    # 保存IP地址
    def save_ip_address(self):
        self.record.write_remote_ip(self.lineEdit_Arm_IP_Address.text())

    # 消息处理函数
    def process_message(self):
        while True:
            # 检查远程服务器是否断开，如果断开，则关闭socket，并将界面连接按键文本改为Connect
            if not self.client.connect_flag:
                self.client.disconnect()
                print("Disconnected the remote ip.")
                self.ui_arm_btn_connect.emit("Connect")
                break
            # 如果接收到来自下位机的指令，消息队列不为空
            if self.client.data_queue.empty() is not True:
                buf = self.client.data_queue.get()
                self.message_parser.parser(buf)
                if self.message_parser.commandArray[0] == self.cmd.CUSTOM_ACTION:  # 如果收到来自下位机的自定义指令
                    if self.message_parser.commandArray[1] == self.cmd.ARM_QUERY:  # 请求发送g代码指令
                        if self.gcode_command.len() > 0:  # 只要还有指令未发送
                            self.arm_command_count = self.message_parser.intParameter[1]
                            self.send_g_code_state = True  # 将标志位打开，开发新一轮指令的发送
                        elif self.gcode_command.len() == 0:  # 如果指令已经全部发送完毕
                            self.arm_command_count = 0
                            self.send_g_code_state = False
                            cmd = self.cmd.CUSTOM_ACTION + str('12') + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_QUERY + str('0')
                            self.threading_cmd.emit(cmd)
                else:
                    self.message_parser.clearParameters()
            else:
                pass

    # 按键槽函数，用于连接远程IP
    def btn_connect_remote_ip(self):
        if self.pushButton_Arm_Connect.text() == "Connect":  # 如果还没连接远程IP
            self.client.ip = self.lineEdit_Arm_IP_Address.text()
            if self.client.connect(self.client.ip):  # 向远程服务器发起连接，并判断是否连接成功。连接成功，打印提示，并开启两个线程，一个用来接收消息，一个用来处理消息
                print("Connected the remote ip.")
                self.read_cmd_handling = threading.Thread(target=self.client.receive_messages)  # 消息接收线程
                self.read_cmd_handling.start()  # 开启消息接收线程
                self.message_handling = threading.Thread(target=self.process_message)  # 消息处理线程
                self.message_handling.start()  # 开启消息处理线程
                self.pushButton_Arm_Connect.setText("Disconnect")  # 将界面连接按键文本改为Disconnect
            else:  # 连接失败，打印提示，保持界面文本不变，不开启线程
                print("Failed to connect the remote ip.")
                self.pushButton_Arm_Connect.setText("Connect")  # 将界面连接按键文本改为Connect
        elif self.pushButton_Arm_Connect.text() == "Disconnect":  # 如果已经连接远程IP
            try:
                messageThread.stop_thread(self.read_cmd_handling)  # 手动关闭消息接收线程
                messageThread.stop_thread(self.message_handling)  # 手动关闭消息处理线程
            except:
                pass
            self.client.disconnect()  # 关闭socket
            print("Disconnected the remote ip.")
            self.pushButton_Arm_Connect.setText("Connect")  # 将界面连接按键文本改为Connect
            self.pushButton_Arm_Load_Relax.setText("Load Motor")

    # 设置控件pushButton_Arm_Connect的显示内容
    def ui_arm_show_btn_connect_content(self, content):
        self.pushButton_Arm_Connect.setText(content)

    # 向下位机发送紧急制动指令
    def btn_stop_arm(self):
        if self.client.connect_flag:
            self.client_busy = True
            cmd = self.cmd.CUSTOM_ACTION + str("13") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_STOP + str("1")
            self.threading_cmd.emit(cmd)
            self.client_busy = False
            self.pushButton_Arm_Load_Relax.setText("Load Motor")
        else:
            print("Connect the remote IP address first.")

    # 控制机械臂回到零点
    def btn_move_to_zero_point(self):
        cmd = self.cmd.CUSTOM_ACTION + str("10") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_SENSOR_POINT + str("1")
        self.threading_cmd.emit(cmd)

    # 控制机械臂使能和失能
    def btn_load_relax_arm(self):
        if self.client.connect_flag:
            cmd = None
            if self.pushButton_Arm_Load_Relax.text() == "Load Motor":
                cmd = self.cmd.CUSTOM_ACTION + str("8") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_ENABLE + str("0")
                self.pushButton_Arm_Load_Relax.setText("Relax Motor")
            elif self.pushButton_Arm_Load_Relax.text() == "Relax Motor":
                cmd = self.cmd.CUSTOM_ACTION + str("8") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_ENABLE + str("1")
                self.pushButton_Arm_Load_Relax.setText("Load Motor")
            self.threading_cmd.emit(cmd)
        else:
            print("Connect the remote IP address first.")

    # 控制蜂鸣器发出声音
    def btn_control_buzzer(self, index):
        if self.client.connect_flag:
            self.client_busy = True
            cmd = None
            if index.isDown():
                cmd = self.cmd.CUSTOM_ACTION + str("2") + self.cmd.DECOLLATOR_CHAR + self.cmd.BUZZER_ACTION + str("2000")
            elif not index.isDown():
                cmd = self.cmd.CUSTOM_ACTION + str("2") + self.cmd.DECOLLATOR_CHAR + self.cmd.BUZZER_ACTION + str("0")
            self.threading_cmd.emit(cmd)
            self.client_busy = False

    # 控制机械臂移动到home位置
    def btn_move_to_position_point(self):
        if self.client.connect_flag:
            if self.pushButton_Arm_Load_Relax.text() == "Relax Motor":
                self.client_busy = True
                if self.record_last_command == "S8 E0":  # 电机失能状态
                    cmd = self.cmd.CUSTOM_ACTION + str("10") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_SENSOR_POINT + str("1")
                    self.threading_cmd.emit(cmd)
                    cmd = self.cmd.MOVE_ACTION + str("0") + self.cmd.DECOLLATOR_CHAR \
                        + self.cmd.AXIS_X_ACTION + str(self.original_position_axis[0]) + self.cmd.DECOLLATOR_CHAR \
                        + self.cmd.AXIS_Y_ACTION + str(self.original_position_axis[1]) + self.cmd.DECOLLATOR_CHAR \
                        + self.cmd.AXIS_Z_ACTION + str(self.original_position_axis[2])
                    self.threading_cmd.emit(cmd)
                    self.record_command(cmd)
                    self.last_axis_point = [round(float(self.original_position_axis[0]), 1),
                                            round(float(self.original_position_axis[1]), 1)]
                    self.ui_arm_show_label_axis(self.original_position_axis)
                else:
                    cmd = self.cmd.MOVE_ACTION + str("0") + self.cmd.DECOLLATOR_CHAR \
                        + self.cmd.AXIS_X_ACTION + str(self.original_position_axis[0]) + self.cmd.DECOLLATOR_CHAR \
                        + self.cmd.AXIS_Y_ACTION + str(self.original_position_axis[1]) + self.cmd.DECOLLATOR_CHAR \
                        + self.cmd.AXIS_Z_ACTION + str(self.original_position_axis[2])
                    self.threading_cmd.emit(cmd)
                    self.record_command(cmd)
                    self.last_axis_point = [round(float(self.original_position_axis[0]), 1),
                                            round(float(self.original_position_axis[1]), 1)]
                    self.ui_arm_show_label_axis(self.original_position_axis)
                self.client_busy = False
            else:
                print("Please press the \"Load Motor\" button first.")
        else:
            print("Connect the remote IP address first.")

    # 控制机械臂移动到home点上方位置
    def btn_move_to_above_home_point(self):
        if self.client.connect_flag:
            if self.pushButton_Arm_Load_Relax.text() == "Relax Motor":
                self.client_busy = True
                if self.record_last_command == "S8 E0":  # 电机失能状态
                    cmd = self.cmd.CUSTOM_ACTION + str("10") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_SENSOR_POINT + str("1")
                    self.threading_cmd.emit(cmd)
                    home_up_height = self.horizontalSlider_Arm_Pen_Height.value()
                    cmd = self.cmd.MOVE_ACTION + str("0") + self.cmd.DECOLLATOR_CHAR \
                        + self.cmd.AXIS_X_ACTION + str(self.original_position_axis[0]) + self.cmd.DECOLLATOR_CHAR \
                        + self.cmd.AXIS_Y_ACTION + str(self.original_position_axis[1]) + self.cmd.DECOLLATOR_CHAR \
                        + self.cmd.AXIS_Z_ACTION + str(float(self.original_position_axis[2]) + home_up_height)
                    self.threading_cmd.emit(cmd)
                    self.record_command(cmd)
                    self.last_axis_point = [round(float(self.original_position_axis[0]), 1),
                                            round(float(self.original_position_axis[1]), 1)]
                    ui_show_axis = self.original_position_axis.copy()
                    ui_show_axis[2] = float(ui_show_axis[2]) + home_up_height
                    self.ui_arm_show_label_axis(ui_show_axis)
                else:
                    home_up_height = self.horizontalSlider_Arm_Pen_Height.value()
                    cmd = self.cmd.MOVE_ACTION + str("0") + self.cmd.DECOLLATOR_CHAR \
                        + self.cmd.AXIS_X_ACTION + str(self.original_position_axis[0]) + self.cmd.DECOLLATOR_CHAR \
                        + self.cmd.AXIS_Y_ACTION + str(self.original_position_axis[1]) + self.cmd.DECOLLATOR_CHAR \
                        + self.cmd.AXIS_Z_ACTION + str(float(self.original_position_axis[2]) + home_up_height)
                    self.threading_cmd.emit(cmd)
                    self.record_command(cmd)
                    self.last_axis_point = [round(float(self.original_position_axis[0]), 1),
                                            round(float(self.original_position_axis[1]), 1)]
                    ui_show_axis = self.original_position_axis.copy()
                    ui_show_axis[2] = float(ui_show_axis[2]) + home_up_height
                    self.ui_arm_show_label_axis(ui_show_axis)
                self.client_busy = False
            else:
                print("Please press the \"Load Motor\" button first.")
        else:
            print("Connect the remote IP address first.")

    # 控制机械臂移动到任意位置
    def btn_move_to_anywhere(self, index):
        int_axis = [0, 0, 0]
        int_axis[0] = float(self.label_Arm_Axis_X_Value.text())
        int_axis[1] = float(self.label_Arm_Axis_Y_Value.text())
        int_axis[2] = float(self.label_Arm_Axis_Z_Value.text())
        if index.objectName() == "pushButton_Arm_Axis_X_Subtract":
            int_axis[0] = int_axis[0] - (self.arm_move_value * self.arm_switched_value)
        elif index.objectName() == "pushButton_Arm_Axis_X_Add":
            int_axis[0] = int_axis[0] + (self.arm_move_value * self.arm_switched_value)
        elif index.objectName() == "pushButton_Arm_Axis_Y_Subtract":
            int_axis[1] = int_axis[1] - (self.arm_move_value * self.arm_switched_value)
        elif index.objectName() == "pushButton_Arm_Axis_Y_Add":
            int_axis[1] = int_axis[1] + (self.arm_move_value * self.arm_switched_value)
        elif index.objectName() == "pushButton_Arm_Axis_Z_Subtract":
            int_axis[2] = int_axis[2] - (self.arm_move_value * self.arm_switched_value)
        elif index.objectName() == "pushButton_Arm_Axis_Z_Add":
            int_axis[2] = int_axis[2] + (self.arm_move_value * self.arm_switched_value)
        elif index.objectName() == "pushButton_Arm_Axis_Switched":
            if self.arm_switched_value == 10:
                self.arm_switched_value = 1
                self.pushButton_Arm_Axis_Switched.setText("Step: X1")
            else:
                self.arm_switched_value = 10
                self.pushButton_Arm_Axis_Switched.setText("Step: X10")
        if self.client.connect_flag:
            if index.objectName() != "pushButton_Arm_Axis_Switched":
                if self.pushButton_Arm_Load_Relax.text() == "Relax Motor":
                    self.client_busy = True
                    cmd = self.cmd.MOVE_ACTION + str("0") + self.cmd.DECOLLATOR_CHAR \
                        + self.cmd.AXIS_X_ACTION + str(round(int_axis[0], 1)) + self.cmd.DECOLLATOR_CHAR \
                        + self.cmd.AXIS_Y_ACTION + str(round(int_axis[1], 1)) + self.cmd.DECOLLATOR_CHAR \
                        + self.cmd.AXIS_Z_ACTION + str(round(int_axis[2], 1))
                    self.threading_cmd.emit(cmd)
                    self.record_command(cmd)
                    self.last_axis_point = [round(int_axis[0], 1), round(int_axis[1], 1)]
                    self.client_busy = False
                else:
                    print("1, Please press the \"Load Motor\" button first.")
                    print("2, Please press the \"Sensor Point\" button second.")
            else:
                print("Connect the remote IP address first.")
            str_axis = [str(round(int_axis[i], 1)) for i in range(3)]
            self.ui_arm_show_label_axis(str_axis)

    # 机械臂操作控件集合（记录、撤回、执行、导入、保存）
    def btn_arm_operation(self, index):
        if index.objectName() == "pushButton_Arm_Record_Command":
            if self.client.connect_flag:
                if self.record_last_command is not None:
                    self.record_area_data_queue.put(self.record_last_command)
                    self.ui_arm_show_record_area()
                else:
                    print("No instruction was detected to be logged.")
            else:
                print("Connect the remote IP address first.")
        elif index.objectName() == "pushButton_Arm_Withdraw_Command":
            if self.record_area_data_queue.len() > 0:
                self.record_area_data_queue.delete(self.record_area_data_queue.len() - 1)
                self.ui_arm_show_record_area()
            else:
                print("Withdraw failed. The record area is None.")
        elif index.objectName() == "pushButton_Arm_Execute_Record_Command":
            if self.client.connect_flag:
                self.client_busy = True
                record_area_data_queue_command = self.record_area_data_queue.gets()
                if record_area_data_queue_command is not None:
                    for i in range(self.record_area_data_queue.len()):
                        self.threading_cmd.emit(record_area_data_queue_command[i])
                else:
                    print("Execute failed. The record area is None.")
                self.client_busy = False
            else:
                print("Connect the remote IP address first.")
        elif index.objectName() == "pushButton_Arm_Save_Record_Command":
            if self.textEdit_Arm_Record_Area.toPlainText() != "":
                now = datetime.now()
                file_name = now.strftime("./Record/record_%Y%m%d_%H%M%S.txt")
                if os.path.exists(file_name) is True:
                    os.remove(file_name)
                fb = open(file_name, "w")
                fb.seek(0)
                fb.truncate()
                record_area_data_queue_command = self.record_area_data_queue.gets()
                for i in range(self.record_area_data_queue.len()):
                    fb.write(record_area_data_queue_command[i] + "\n")
                fb.close()
            else:
                print("No instructions need to be saved.")
        elif index.objectName() == "pushButton_Arm_Import_Record_Command":
            if not os.path.exists("./record"):
                os.mkdir("./record")
            self.folder_path = self.filePath.getFilePath("./record/*")  # 打开窗口获取文件路径
            print(self.folder_path)
            if self.folder_path is not None:
                if self.folder_path.split(".")[1] == "txt":  # 判断文件是否是txt文件
                    fb = open(self.folder_path, "r")  # 打开文件
                    self.record_area_data_queue.clear()  # 清除指令消息队列
                    line = fb.readline()  # 读取一行内容
                    while line:  # 读取到内容
                        txt_command = line.split("\n")[0]  # 获取内容
                        self.record_area_data_queue.put(txt_command)  # 将内容压入消息队列
                        line = fb.readline()  # 读取下一行内容
                    self.ui_arm_show_record_area()  # 将内容显示在上位机
                    fb.close()  # 关闭文件
            else:
                print("Cancel the instructions in the import file.")

    # 图像按键对滑条的使能和失能
    def img_btn_slider_enable(self, enable):
        self.pushButton_Arm_Import_Picture.setEnabled(enable)
        self.pushButton_Arm_Gray_Picture.setEnabled(enable)
        self.pushButton_Arm_Binaryzation_Picture.setEnabled(enable)
        self.pushButton_Arm_Contour_Picture.setEnabled(enable)
        self.horizontalSlider_Arm_Threshold.setEnabled(enable)
        self.horizontalSlider_Arm_Gauss.setEnabled(enable)
        self.horizontalSlider_Arm_Sharpen.setEnabled(enable)
        self.lineEdit_Arm_Threshold_Value.setEnabled(enable)
        self.lineEdit_Arm_Gauss_Value.setEnabled(enable)
        self.lineEdit_Arm_Sharpen_Value.setEnabled(enable)
        str_push_button = "QAbstractButton{\n" \
                          "border-style:none;\n" \
                          "border-radius:0px;\n" \
                          "padding:5px;\n" \
                          "color:#DCDCDC;\n" \
                          "background:qlineargradient(spread:pad,x1:0,y1:0,x2:0,y2:1,stop:0 #858585,stop:1 #383838);\n" \
                          "}\n" \
                          "QAbstractButton:hover{\n" \
                          "color:#000000;\n" \
                          "background-color:#008aff;\n" \
                          "}\n" \
                          "QAbstractButton:pressed{\n" \
                          "color:#DCDCDC;\n" \
                          "border-style:solid;\n" \
                          "border-width:0px 0px 0px 4px;\n" \
                          "padding:4px 4px 4px 2px;\n" \
                          "border-color:#008aff;\n" \
                          "background-color:#444444;\n" \
                          "}\n"
        str_line_edit = "QLineEdit{\n" \
                        "border:1px solid #242424;\n" \
                        "border-radius:3px;\n" \
                        "padding:2px;\n" \
                        "background:none;\n" \
                        "selection-background-color:#484848;\n" \
                        "selection-color:#DCDCDC;\n" \
                        "}\n" \
                        "QLineEdit:focus,QLineEdit:hover{\n" \
                        "border:1px solid #242424;\n" \
                        "}\n" \
                        "QLineEdit{\n" \
                        "border:1px solid #242424;\n" \
                        "border-radius:3px;\n" \
                        "padding:2px;\n" \
                        "background:none;\n" \
                        "selection-background-color:#484848;\n" \
                        "selection-color:#DCDCDC;\n" \
                        "}\n" \
                        "\n" \
                        "QLineEdit:focus,QLineEdit:hover{\n" \
                        "border:1px solid #242424;\n" \
                        "}\n" \
                        "QLineEdit{\n" \
                        "lineedit-password-character:9679;\n" \
                        "}\n"
        if not enable:
            self.pushButton_Arm_Import_Picture.setStyleSheet("background-color: rgb(195, 195, 195);")
            self.pushButton_Arm_Gray_Picture.setStyleSheet("background-color: rgb(195, 195, 195);")
            self.pushButton_Arm_Binaryzation_Picture.setStyleSheet("background-color: rgb(195, 195, 195);")
            self.pushButton_Arm_Contour_Picture.setStyleSheet("background-color: rgb(195, 195, 195);")
            self.lineEdit_Arm_Threshold_Value.setStyleSheet("background-color: rgb(195, 195, 195);")
            self.lineEdit_Arm_Gauss_Value.setStyleSheet("background-color: rgb(195, 195, 195);")
            self.lineEdit_Arm_Sharpen_Value.setStyleSheet("background-color: rgb(195, 195, 195);")
        else:
            self.pushButton_Arm_Import_Picture.setStyleSheet(str_push_button)
            self.pushButton_Arm_Gray_Picture.setStyleSheet(str_push_button)
            self.pushButton_Arm_Binaryzation_Picture.setStyleSheet(str_push_button)
            self.pushButton_Arm_Contour_Picture.setStyleSheet(str_push_button)
            self.lineEdit_Arm_Threshold_Value.setStyleSheet(str_line_edit)
            self.lineEdit_Arm_Gauss_Value.setStyleSheet(str_line_edit)
            self.lineEdit_Arm_Sharpen_Value.setStyleSheet(str_line_edit)

    # 绘图模式选择
    def radioButton_arm_select_mode(self, index):
        if index.objectName() == "radioButton_Arm_Img_Mode":
            self.radioButton_Arm_Line_Mode.setChecked(False)
            self.radioButton_Arm_Curves_Mode.setChecked(False)
            self.radioButton_Arm_Img_Mode.setChecked(True)
            self.img_btn_slider_enable(True)
            self.painter_line_style = 0
            if self.img_flag == 0:
                self.original_label_img = self.white_image.copy()
            elif self.img_flag == 1:
                self.original_label_img = self.raw_img.copy()
            elif self.img_flag == 2:
                self.original_label_img = self.gray_img.copy()
            elif self.img_flag == 3:
                self.original_label_img = self.binary_img.copy()
            elif self.img_flag == 4:
                self.original_label_img = self.contour_img.copy()
            self.lastPoint = [0, 0]
            self.currentPoint = [0, 0]
            self.updata_label_show()
        elif index.objectName() == "radioButton_Arm_Line_Mode":
            self.radioButton_Arm_Line_Mode.setChecked(True)
            self.radioButton_Arm_Curves_Mode.setChecked(False)
            self.radioButton_Arm_Img_Mode.setChecked(False)
            self.img_btn_slider_enable(False)
            self.painter_line_style = 1
        elif index.objectName() == "radioButton_Arm_Curves_Mode":
            self.radioButton_Arm_Line_Mode.setChecked(False)
            self.radioButton_Arm_Curves_Mode.setChecked(True)
            self.radioButton_Arm_Img_Mode.setChecked(False)
            self.img_btn_slider_enable(False)
            self.painter_line_style = 2

    # 图像轮廓数据发送线程
    def send_Image_command(self):
        if not self.gcode_command.empty():
            if self.client.connect_flag:
                self.client_busy = True
                cmd = self.cmd.CUSTOM_ACTION + str("12") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_QUERY + str("1")
                self.threading_cmd.emit(cmd)
                # 等待下位机命令
                while self.gcode_command.len() > 0:
                    if self.send_g_code_state:
                        if self.arm_command_count < 50:
                            send_num = 50 - self.arm_command_count
                            if self.gcode_command.len() < send_num:
                                send_num = self.gcode_command.len()
                            for i in range(send_num):
                                buf = self.gcode_command.get()
                                if buf is not None:
                                    self.threading_cmd.emit(buf)
                self.client_busy = False
        else:
            print("Connect the remote IP address first.")

    # 图片转代码总处理函数
    def set_img_action(self, index):
        if index.objectName() == "pushButton_Arm_Import_Picture":  # 导入图片
            try:
                self.folder_path = self.filePath.getFilePath("./picture/*")  # 打开窗口获取文件路径
                if self.folder_path is not None:
                    print(self.folder_path)
                    white_image = self.white_image.copy()  # 创建一张白色的图片
                    self.img_flag = 1
                    img = cv2.imread(self.folder_path)  # 根据文件路径获取
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # 将BGR图转化为RGB图
                    img_h, img_w = img.shape[:2]
                    label_h = self.label_videl_size[1]
                    label_w = self.label_videl_size[0]
                    if img_h <= label_h and img_w <= label_w:  # 如果图片小于等于控件大小
                        picture_center = ((label_h - img_h) // 2, (label_w - img_w) // 2)  # 计算图片在控件中心区的起始位置
                        white_image[picture_center[0]:picture_center[0] + img_h, picture_center[1]:picture_center[1] + img_w] = img
                    elif img_h > label_h or img_w > label_w:  # 如果图片大于控件的大小
                        scale = min(label_h / img_h, label_w / img_w)  # 选择较小的缩放比例
                        new_img_h = int(scale * img_h)
                        new_img_w = int(scale * img_w)
                        resized_img = cv2.resize(img, (new_img_w, new_img_h), interpolation=cv2.INTER_AREA)
                        picture_center = ((label_h - new_img_h) // 2, (label_w - new_img_w) // 2)
                        white_image[picture_center[0]:picture_center[0] + new_img_h, picture_center[1]:picture_center[1] + new_img_w] = resized_img
                    img = white_image.copy()
                    self.raw_img = img.copy()  # 将原始RGB图复制给self.raw_img
                    img = QImage(img.data.tobytes(), img.shape[1], img.shape[0], QImage.Format_RGB888)  # 将图片转化为QImage格式
                    self.label_Arm_Video.setPixmap(QPixmap.fromImage(img))  # 将图片显示在控件上
                    self.original_label_img = self.raw_img.copy()
                else:
                    print("Folder path is None.")
            except:
                self.img_flag = 0
                print("Load picture failed.")
                self.axis_paint_function = False  # 不启动画布界面
                img = QImage(self.white_image.data.tobytes(), self.white_image.shape[1], self.white_image.shape[0], QImage.Format_RGB888)  # 将图片转化为QImage格式
                self.label_Arm_Video.setPixmap(QPixmap.fromImage(img))  # 将图片显示在控件上
                self.original_label_img = self.white_image.copy()
        elif index.objectName() == "pushButton_Arm_Gray_Picture":  # 转化为灰度图
            try:
                if len(self.raw_img):
                    self.img_flag = 2
                    self.gray_img = cv2.cvtColor(self.raw_img, cv2.COLOR_BGR2GRAY)  # 将原始RGB图转化为灰度图并保存在self.gray_img中
                    img = QImage(self.gray_img.data.tobytes(), self.gray_img.shape[1], self.gray_img.shape[0], QImage.Format_Indexed8)  # 将图片转化为QImage格式
                    self.label_Arm_Video.setPixmap(QPixmap.fromImage(img))  # 将图片显示在控件上
                    self.original_label_img = self.gray_img.copy()
            except:
                print("Show gary picture failed.")
        elif index.objectName() == "pushButton_Arm_Binaryzation_Picture":  # 转化为二值化图                                                                    # 已加载二值化图
            try:
                if len(self.gray_img):
                    self.img_flag = 3
                    img = self.gray_img.copy()  # 将灰度图图复制给img
                    ret, binary = cv2.threshold(img, self.threshold_value, 255, cv2.THRESH_BINARY)  # 使用滑条阈值对图片进行二值化处理
                    img = cv2.GaussianBlur(binary, (self.gauss_value, self.gauss_value), 0, 0)  # 对图片进行高斯模糊运算
                    kernel = np.array([[0, -1, 0], [-1, self.sharpen_value, -1], [0, -1, 0]], np.float32)  # 设置锐化卷积核
                    img = cv2.filter2D(img, -1, kernel=kernel)  # 对图片进行卷积运算
                    self.binary_img = img.copy()  # 将二值化图复制给self.binary_img
                    img = QImage(img.data.tobytes(), img.shape[1], img.shape[0], QImage.Format_Indexed8)  # 将图片转化为QImage格式
                    self.label_Arm_Video.setPixmap(QPixmap.fromImage(img))  # 将图片显示在控件上
                    self.original_label_img = self.binary_img.copy()
            except:
                print("Show binaryzation picture failed.")
        elif index.objectName() == "pushButton_Arm_Contour_Picture":
            try:
                if len(self.binary_img):
                    self.img_flag = 4
                    img = self.binary_img.copy()  # 复制二值化图片
                    self.contours_data = None  # 清空轮廓数据
                    self.hierarchy_data = None  # 清空轮廓数据继承关系
                    # self.contours_data, self.hierarchy_data = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)     # 存储所有的轮廓点，相邻的两个点的像素位置差不超过 1
                    self.contours_data, self.hierarchy_data = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # 压缩水平方向，垂直方向，对角线方向的元素，只保留该方向的终点坐标，一个矩阵轮廓只需 4 个点来保存轮廓信息
                    img1 = self.raw_img.copy()
                    img1 = np.zeros(shape=img.shape, dtype=np.uint8)  # 根据送进来的图像，建立一个二维数组
                    img1 += 255  # 将整个图像像素点都设置为白色
                    cv2.drawContours(img1, self.contours_data, -1, (0, 0, 0), 1)  # 在图像基础上画出轮廓线
                    self.contour_img = img1.copy()  # 将轮廓图复制给self.contour
                    img1 = QImage(img1.data.tobytes(), img1.shape[1], img1.shape[0], QImage.Format_Indexed8)  # 将图片转化为QImage格式
                    self.label_Arm_Video.setPixmap(QPixmap.fromImage(img1))  # 将图片显示在控件上
                    self.original_label_img = self.contour_img.copy()
            except:
                print("Show contour picture failed.")
        elif index.objectName() == "pushButton_Arm_Clear_All":
            self.line_curves_count = 1
            self.current_line_curves = 0
            self.gcode_command.clear()
            self.painter_point.clear()
            self.textEdit_Arm_Gcode_Area.clear()
            if self.img_flag == 0:
                self.original_label_img = self.white_image.copy()
            elif self.img_flag == 1:
                self.original_label_img = self.raw_img.copy()
            elif self.img_flag == 2:
                self.original_label_img = self.gray_img.copy()
            elif self.img_flag == 3:
                self.original_label_img = self.binary_img.copy()
            elif self.img_flag == 4:
                self.original_label_img = self.contour_img.copy()
            self.lastPoint = [0, 0]
            self.currentPoint = [0, 0]
            self.updata_label_show()
        elif index.objectName() == "pushButton_Arm_Change_Gcode":
            try:
                z_height = float(self.lineEdit_Arm_Pen_Height_Value.text()) + float(self.original_position_axis[2])
                z_axis = float(self.original_position_axis[2])
                if self.radioButton_Arm_Img_Mode.isChecked():
                    if len(self.contour_img):
                        self.gcode_command.clear()
                        for i in range(1, len(self.contours_data)):
                            track_last_point_command = None
                            for j in range(len(self.contours_data[i])):
                                buf = list(self.contours_data[i][j][0])
                                if j == 0:  # 起点下笔位置
                                    # 移动到机械臂最后停留位置（没有则默认为home位置）
                                    gcode_change_command = self.cmd.MOVE_ACTION + str("0") + self.cmd.DECOLLATOR_CHAR \
                                        + self.cmd.AXIS_X_ACTION + str(self.last_axis_point[0]) + self.cmd.DECOLLATOR_CHAR \
                                        + self.cmd.AXIS_Y_ACTION + str(self.last_axis_point[1]) + self.cmd.DECOLLATOR_CHAR \
                                        + self.cmd.AXIS_Z_ACTION + str(round(z_height, 1))
                                    self.gcode_command.put(gcode_change_command)
                                    # 移动到目标点上方
                                    x = self.map(buf[0], 0, self.label_videl_size[0], self.axis_map_x[0], self.axis_map_x[1], 1)
                                    y = self.map(buf[1], 0, self.label_videl_size[1], self.axis_map_y[0], self.axis_map_y[1], 1)
                                    gcode_change_command = self.cmd.MOVE_ACTION + str("0") + self.cmd.DECOLLATOR_CHAR \
                                        + self.cmd.AXIS_X_ACTION + str(x) + self.cmd.DECOLLATOR_CHAR \
                                        + self.cmd.AXIS_Y_ACTION + str(y) + self.cmd.DECOLLATOR_CHAR \
                                        + self.cmd.AXIS_Z_ACTION + str(round(z_height, 1))
                                    self.gcode_command.put(gcode_change_command)
                                    # 下笔
                                    gcode_change_command = self.cmd.MOVE_ACTION + str("0") + self.cmd.DECOLLATOR_CHAR \
                                        + self.cmd.AXIS_X_ACTION + str(x) + self.cmd.DECOLLATOR_CHAR \
                                        + self.cmd.AXIS_Y_ACTION + str(y) + self.cmd.DECOLLATOR_CHAR \
                                        + self.cmd.AXIS_Z_ACTION + str(z_axis)
                                    self.gcode_command.put(gcode_change_command)
                                    track_last_point_command = [x, y]
                                    self.last_axis_point = [x, y]
                                else:  # 轨迹位置
                                    x = self.map(buf[0], 0, self.label_videl_size[0], self.axis_map_x[0], self.axis_map_x[1], 1)
                                    y = self.map(buf[1], 0, self.label_videl_size[1], self.axis_map_y[0], self.axis_map_y[1], 1)
                                    gcode_change_command = self.cmd.MOVE_ACTION + str("0") + self.cmd.DECOLLATOR_CHAR \
                                        + self.cmd.AXIS_X_ACTION + str(x) + self.cmd.DECOLLATOR_CHAR \
                                        + self.cmd.AXIS_Y_ACTION + str(y) + self.cmd.DECOLLATOR_CHAR \
                                        + self.cmd.AXIS_Z_ACTION + str(z_axis)
                                    self.gcode_command.put(gcode_change_command)
                                    self.last_axis_point = [x, y]
                            gcode_change_command = self.cmd.MOVE_ACTION + str("0") + self.cmd.DECOLLATOR_CHAR \
                                + self.cmd.AXIS_X_ACTION + str(track_last_point_command[0]) + self.cmd.DECOLLATOR_CHAR \
                                + self.cmd.AXIS_Y_ACTION + str(track_last_point_command[1]) + self.cmd.DECOLLATOR_CHAR \
                                + self.cmd.AXIS_Z_ACTION + str(z_axis)
                            self.gcode_command.put(gcode_change_command)
                            self.last_axis_point = [track_last_point_command[0], track_last_point_command[1]]
                        # 原地抬笔
                        gcode_change_command = self.cmd.MOVE_ACTION + str("0") + self.cmd.DECOLLATOR_CHAR \
                            + self.cmd.AXIS_X_ACTION + str(self.last_axis_point[0]) + self.cmd.DECOLLATOR_CHAR \
                            + self.cmd.AXIS_Y_ACTION + str(self.last_axis_point[1]) + self.cmd.DECOLLATOR_CHAR \
                            + self.cmd.AXIS_Z_ACTION + str(round(z_height, 1))
                        self.gcode_command.put(gcode_change_command)
                        # 移动回到原点
                        self.last_axis_point = [0, 200]
                        gcode_change_command = self.cmd.MOVE_ACTION + str("0") + self.cmd.DECOLLATOR_CHAR \
                            + self.cmd.AXIS_X_ACTION + str(self.last_axis_point[0]) + self.cmd.DECOLLATOR_CHAR \
                            + self.cmd.AXIS_Y_ACTION + str(self.last_axis_point[1]) + self.cmd.DECOLLATOR_CHAR \
                            + self.cmd.AXIS_Z_ACTION + str(round(z_height, 1))
                        self.gcode_command.put(gcode_change_command)
                        self.textEdit_Arm_Gcode_Area.clear()
                        gcode_change_command = self.gcode_command.gets()
                        for i in range(self.gcode_command.len()):
                            self.textEdit_Arm_Gcode_Area.append(gcode_change_command[i])
                    else:
                        self.textEdit_Arm_Gcode_Area.clear()
                else:
                    self.gcode_command.clear()  # 清空G代码消息队列
                    self.textEdit_Arm_Gcode_Area.clear()
                    if self.painter_point.len() > 0:  # 判断消息队列是否有数据
                        self.current_line_curves = 0
                        buf_point = self.painter_point.gets()
                        for i in range(self.painter_point.len()):
                            # print(buf_point[i])
                            if self.current_line_curves != buf_point[i][2]:  # 需要开始绘制新的线，抬笔，移动到新坐标，下笔，绘制线
                                # 原地抬笔
                                x = self.last_axis_point[0]
                                y = self.last_axis_point[1]
                                gcode_change_command = self.cmd.MOVE_ACTION + str("0") + self.cmd.DECOLLATOR_CHAR \
                                    + self.cmd.AXIS_X_ACTION + str(x) + self.cmd.DECOLLATOR_CHAR \
                                    + self.cmd.AXIS_Y_ACTION + str(y) + self.cmd.DECOLLATOR_CHAR \
                                    + self.cmd.AXIS_Z_ACTION + str(round(z_height, 1))
                                self.gcode_command.put(gcode_change_command)
                                # 移动到起始目标点上方
                                x = self.map(buf_point[i][0][0], 0, self.label_videl_size[0], self.axis_map_x[0], self.axis_map_x[1], 1)
                                y = self.map(buf_point[i][0][1], 0, self.label_videl_size[1], self.axis_map_y[0], self.axis_map_y[1], 1)
                                gcode_change_command = self.cmd.MOVE_ACTION + str("0") + self.cmd.DECOLLATOR_CHAR \
                                    + self.cmd.AXIS_X_ACTION + str(x) + self.cmd.DECOLLATOR_CHAR \
                                    + self.cmd.AXIS_Y_ACTION + str(y) + self.cmd.DECOLLATOR_CHAR \
                                    + self.cmd.AXIS_Z_ACTION + str(round(z_height, 1))
                                self.gcode_command.put(gcode_change_command)
                                # 下笔
                                gcode_change_command = self.cmd.MOVE_ACTION + str("0") + self.cmd.DECOLLATOR_CHAR \
                                    + self.cmd.AXIS_X_ACTION + str(x) + self.cmd.DECOLLATOR_CHAR \
                                    + self.cmd.AXIS_Y_ACTION + str(y) + self.cmd.DECOLLATOR_CHAR \
                                    + self.cmd.AXIS_Z_ACTION + str(z_axis)
                                self.gcode_command.put(gcode_change_command)
                                # 移动到目标点
                                x = self.map(buf_point[i][1][0], 0, self.label_videl_size[0], self.axis_map_x[0], self.axis_map_x[1], 1)
                                y = self.map(buf_point[i][1][1], 0, self.label_videl_size[1], self.axis_map_y[0], self.axis_map_y[1], 1)
                                gcode_change_command = self.cmd.MOVE_ACTION + str("0") + self.cmd.DECOLLATOR_CHAR \
                                    + self.cmd.AXIS_X_ACTION + str(x) + self.cmd.DECOLLATOR_CHAR \
                                    + self.cmd.AXIS_Y_ACTION + str(y) + self.cmd.DECOLLATOR_CHAR \
                                    + self.cmd.AXIS_Z_ACTION + str(z_axis)
                                self.gcode_command.put(gcode_change_command)
                                self.last_axis_point = [x, y]
                                self.current_line_curves = buf_point[i][2]  # 更新当前正在绘制的是第几根线
                            else:  # 不抬笔，直接绘制线
                                # 移动到目标点
                                x = self.map(buf_point[i][1][0], 0, self.label_videl_size[0], self.axis_map_x[0], self.axis_map_x[1], 1)
                                y = self.map(buf_point[i][1][1], 0, self.label_videl_size[1], self.axis_map_y[0], self.axis_map_y[1], 1)
                                gcode_change_command = self.cmd.MOVE_ACTION + str("0") + self.cmd.DECOLLATOR_CHAR \
                                    + self.cmd.AXIS_X_ACTION + str(x) + self.cmd.DECOLLATOR_CHAR \
                                    + self.cmd.AXIS_Y_ACTION + str(y) + self.cmd.DECOLLATOR_CHAR \
                                    + self.cmd.AXIS_Z_ACTION + str(z_axis)
                                self.gcode_command.put(gcode_change_command)
                                self.last_axis_point = [x, y]
                        # 原地抬笔
                        x = self.last_axis_point[0]
                        y = self.last_axis_point[1]
                        gcode_change_command = self.cmd.MOVE_ACTION + str("0") + self.cmd.DECOLLATOR_CHAR \
                            + self.cmd.AXIS_X_ACTION + str(x) + self.cmd.DECOLLATOR_CHAR \
                            + self.cmd.AXIS_Y_ACTION + str(y) + self.cmd.DECOLLATOR_CHAR \
                            + self.cmd.AXIS_Z_ACTION + str(round(z_height, 1))
                        self.gcode_command.put(gcode_change_command)
                        # 移动到出发点
                        self.last_axis_point = [0, 200]
                        x = self.last_axis_point[0]
                        y = self.last_axis_point[1]
                        gcode_change_command = self.cmd.MOVE_ACTION + str("0") + self.cmd.DECOLLATOR_CHAR \
                            + self.cmd.AXIS_X_ACTION + str(x) + self.cmd.DECOLLATOR_CHAR \
                            + self.cmd.AXIS_Y_ACTION + str(y) + self.cmd.DECOLLATOR_CHAR \
                            + self.cmd.AXIS_Z_ACTION + str(round(z_height, 1))
                        self.gcode_command.put(gcode_change_command)
                        gcode_change_command = self.gcode_command.gets()
                        for i in range(self.gcode_command.len()):
                            self.textEdit_Arm_Gcode_Area.append(gcode_change_command[i])
            except:
                print("Change Picture to G-Code failed.")
        elif index.objectName() == "pushButton_Arm_Execute_Gcode":
            if self.client.connect_flag:
                if self.gcode_command.len() > 0:
                    if self.pushButton_Arm_Load_Relax.text() == "Relax Motor":
                        execte_handle = threading.Thread(target=self.send_Image_command)
                        execte_handle.start()
                    else:
                        print("Please press the \"Load Motor\" button first.")
                else:
                    self.textEdit_Arm_Gcode_Area.clear()
            else:
                print("Connect the remote IP address first.")

    # 图像界面滑条控制槽函数
    def img_slider_control(self, index):
        # 图像界面，滑条对灰度图进行二值化，膨胀，腐蚀处理
        if index.objectName() == "horizontalSlider_Arm_Threshold":  # 二值化处理
            self.threshold_value = index.value()  # 获取滑条键值
            self.lineEdit_Arm_Threshold_Value.setText(str(self.threshold_value))  # 显示在控件上
        elif index.objectName() == "horizontalSlider_Arm_Gauss":
            self.gauss_value = index.value()  # 获取滑条键值
            if self.gauss_value % 2 == 0:  # 如果滑条键值为偶数，加一设置为奇数
                self.gauss_value = self.gauss_value + 1  # 高斯模糊卷积核只能为奇数
            self.lineEdit_Arm_Gauss_Value.setText(str(self.gauss_value))  # 显示滑条值
            index.setValue(self.gauss_value)  # 设置滑条值
        elif index.objectName() == "horizontalSlider_Arm_Sharpen":
            self.sharpen_value = index.value()  # 获取滑条键值
            self.lineEdit_Arm_Sharpen_Value.setText(str(self.sharpen_value))  # 显示滑条值
        elif index.objectName() == "horizontalSlider_Arm_Pen_Height":
            self.lineEdit_Arm_Pen_Height_Value.setText(str(index.value()))
        if self.img_flag >= 3:
            try:
                img = self.gray_img.copy()  # 将灰度图图复制给img
                ret, binary = cv2.threshold(img, self.threshold_value, 255, cv2.THRESH_BINARY)  # 使用滑条阈值对图片进行二值化处理
                img = cv2.GaussianBlur(binary, (self.gauss_value, self.gauss_value), 0, 0)  # 对图片进行高斯模糊运算
                kernel = np.array([[0, -1, 0], [-1, self.sharpen_value, -1], [0, -1, 0]], np.float32)  # 设置锐化卷积核
                img = cv2.filter2D(img, -1, kernel=kernel)  # 对图片进行卷积运算
                self.binary_img = img.copy()  # 将二值化图复制给self.binary_img
                self.original_label_img = img.copy()
                if self.img_flag == 4:
                    self.contours_data = None  # 清空轮廓数据
                    self.hierarchy_data = None  # 清空轮廓数据继承关系
                    # self.contours_data, self.hierarchy_data = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)   # 存储所有的轮廓点，相邻的两个点的像素位置差不超过 1
                    self.contours_data, self.hierarchy_data = cv2.findContours(img, cv2.RETR_TREE,
                                                                               cv2.CHAIN_APPROX_SIMPLE)  # 压缩水平方向，垂直方向，对角线方向的元素，只保留该方向的终点坐标，一个矩阵轮廓只需 4 个
                    img1 = np.zeros(shape=img.shape, dtype=np.uint8)  # 根据送进来的图像，建立一个二维数组
                    img1 += 255  # 将整个图像像素点都设置为白色
                    cv2.drawContours(img1, self.contours_data, -1, (0, 0, 0), 1)  # 在图像基础上画出轮廓线
                    self.contour_img = img1.copy()  # 将轮廓图复制给self.contour
                    self.original_label_img = img1.copy()
                    img1 = QImage(img1.data.tobytes(), img1.shape[1], img1.shape[0],
                                  QImage.Format_Indexed8)  # 将图片转化为QImage格式
                    self.label_Arm_Video.setPixmap(QPixmap.fromImage(img1))  # 将图片显示在控件上
                else:
                    img = QImage(img.data.tobytes(), img.shape[1], img.shape[0],
                                 QImage.Format_Indexed8)  # 将图片转化为QImage格式
                    self.label_Arm_Video.setPixmap(QPixmap.fromImage(img))  # 将图片显示在控件上
            except:
                print("Show binaryzation picture failed.")

    # 舵机控制函数
    def control_servo_angle(self, index):
        if index.objectName() == "pushButton_Arm_Servo_Turn_On":
            self.angle_value = int(self.lineEdit_Arm_Servo_Angle_Value.text()) + 5
            self.angle_value = self.constrain(self.angle_value, 0, 180)
            self.lineEdit_Arm_Servo_Angle_Value.setText(str(self.angle_value))
        elif index.objectName() == "pushButton_Arm_Servo_Turn_Off":
            self.angle_value = int(self.lineEdit_Arm_Servo_Angle_Value.text()) - 5
            self.angle_value = self.constrain(self.angle_value, 0, 180)
            self.lineEdit_Arm_Servo_Angle_Value.setText(str(self.angle_value))
        if self.client.connect_flag:
            self.client_busy = True
            cmd = self.cmd.CUSTOM_ACTION + str("9") + self.cmd.DECOLLATOR_CHAR \
                + self.cmd.ARM_SERVO_INDEX + str(self.comboBox_Arm_Servo.currentIndex()) + self.cmd.DECOLLATOR_CHAR \
                + self.cmd.ARM_SERVO_ANGLE + self.lineEdit_Arm_Servo_Angle_Value.text()
            self.threading_cmd.emit(cmd)
            self.record_command(cmd)
            self.client_busy = False
        else:
            print("Connect the remote IP address first.")

    # 更新label控件显示内容
    def updata_label_show(self):
        img = None
        start_point = (self.lastPoint[0], self.lastPoint[1])  # 指定起点的坐标
        end_point = (self.currentPoint[0], self.currentPoint[1])  # 指定终点的坐标
        if self.painter_line_style == 1:
            if self.isDrawing:
                img = self.original_label_img.copy()  # 复制一份背景图
            else:
                img = self.original_label_img  # 调用原始背景图
        else:
            img = self.original_label_img
        if start_point != end_point:
            cv2.line(img, start_point, end_point, (0, 0, 0), 1, cv2.LINE_AA)  # 在背景图层上画一根线，设置起点，终点，线颜色，线宽，抗锯齿
        if self.img_flag <= 1:
            img = QImage(img.data.tobytes(), img.shape[1], img.shape[0], QImage.Format_RGB888)  # 注意，没加载图片或者加载原图时，色彩丰富，需要转化为Format_RGB888
        else:
            img = QImage(img.data.tobytes(), img.shape[1], img.shape[0], QImage.Format_Indexed8)  # 注意，灰度图，二值化图，轮廓图，色彩较单一，需要转化为Format_Indexed8
        self.label_Arm_Video.setPixmap(QPixmap.fromImage(img))  # 将图片显示在控件上

    # 鼠标按下
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:  # 如果鼠标左键按下
            if self.painter_line_style != 0:
                x = self.constrain(event.pos().x(), 0, self.label_videl_size[0])
                y = self.constrain(event.pos().y(), 0, self.label_videl_size[1])
                self.currentPoint = [x, y]  # 获得当前坐标，作为划线的终点
                self.lastPoint = self.currentPoint.copy()  # 获得当前坐标，作为划线的起点
                self.isDrawing = True

    # 鼠标移动
    def mouseMoveEvent(self, event):
        if event.buttons() and Qt.LeftButton:  # 如果鼠标左键一直按着
            if self.painter_line_style != 0:
                x = self.constrain(event.pos().x(), 0, self.label_videl_size[0])
                y = self.constrain(event.pos().y(), 0, self.label_videl_size[1])
                self.currentPoint = [x, y]  # 获得当前坐标，作为划线的过程
                self.updata_label_show()
                if self.painter_line_style == 2:
                    self.painter_point.put([self.lastPoint, self.currentPoint, self.line_curves_count])
                    self.lastPoint = self.currentPoint.copy()

    # 鼠标释放
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:  # 鼠标左键释放
            if self.painter_line_style != 0:
                x = self.constrain(event.pos().x(), 0, self.label_videl_size[0])
                y = self.constrain(event.pos().y(), 0, self.label_videl_size[1])
                self.currentPoint = [x, y]
                if self.lastPoint[0] == self.currentPoint[0] and self.lastPoint[1] == self.currentPoint[1]:
                    pass
                else:
                    self.painter_point.put([self.lastPoint, self.currentPoint, self.line_curves_count])
                self.isDrawing = False
                self.updata_label_show()
                self.line_curves_count = self.line_curves_count + 1

    # 每次关闭配置参数页面，重新加载一遍坐标
    def close_parameter_ui(self, data):
        data = data.split(",")
        if data[3] == "1":
            self.ui_arm_show_label_axis(data[:3])
            self.original_position_axis = data[:3]
            self.pushButton_Arm_Parameter_UI.setEnabled(True)
            # print("close parameter ui.")
        elif data[3] == "0":
            self.ui_arm_show_label_axis(data[:3])
            self.original_position_axis = data[:3]

    # 配置机械臂参数界面
    def configure_parameter_ui(self):
        if self.client.connect_flag:
            if self.pushButton_Arm_Load_Relax.text() == "Relax Motor":
                self.pushButton_Arm_Parameter_UI.setEnabled(False)
                self.configurationWindow = Configuration()
                self.configurationWindow.setWindowModality(Qt.NonModal)
                self.configurationWindow.show()
                self.configurationWindow.position_axis_channel.connect(self.close_parameter_ui)
                self.configurationWindow.send_cmd_channel.connect(self.socket_send)
            else:
                print("Please press the \"Load Motor\" button first.")
        else:
            print("Connect the remote IP address first.")

    # 每次关闭led页面，重新恢复按键使能
    def close_led_ui(self):
        self.pushButton_Arm_Led_UI.setEnabled(True)

    # 配置机械臂彩灯界面
    def configure_led_ui(self):
        if self.client.connect_flag:
            self.pushButton_Arm_Led_UI.setEnabled(False)
            self.ledWindow = LED()
            self.ledWindow.setWindowModality(Qt.NonModal)
            self.ledWindow.show()
            self.ledWindow.signal_channel.connect(self.close_led_ui)
            self.ledWindow.send_cmd_channel.connect(self.socket_send)
        else:
            print("Connect the remote IP address first.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myshow = myClientWindow()
    myshow.show()
    sys.exit(app.exec_())
