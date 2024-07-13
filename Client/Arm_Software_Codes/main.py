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
    ui_arm_btn_connect = QtCore.pyqtSignal(str)
    threading_cmd = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(myClientWindow, self).__init__(parent)
        self.setupUi(self)  
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

        self.main_position_mode_length = 0.0 
        self.main_clamp_mode_length = 40.0 
        self.main_servo_mode_length = 50.0  
        self.client = Client()  
        self.record = messageRecord.MessageRecord()  
        self.label_Arm_Video.setScaledContents(False)  
        ip_validator = QRegExpValidator(QRegExp('^((2[0-4]\d|25[0-5]|\d?\d|1\d{2})\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)$'))  
        self.lineEdit_Arm_IP_Address.setValidator(ip_validator)  
        servo_validator = QRegExpValidator(QRegExp('^(?:[1-9][0-9]?|1[0-7][0-9]?|180)$'))
        self.lineEdit_Arm_Servo_Angle_Value.setValidator(servo_validator)
        self.lineEdit_Arm_IP_Address.setText(self.record.read_remote_ip())  
        self.client.ip = self.lineEdit_Arm_IP_Address.text()
        print("Remote IP: " + self.client.ip) 
        self.message_parser = messageParser.MessageParser() 
        self.gcode_command = messageQueue.MessageQueue()
        self.painter_point = messageQueue.MessageQueue() 
        self.send_g_code_state = False  
        self.cmd = command.Command() 
        self.client_busy = False 
        self.original_position_axis = self.record.read_position_point()  
        self.ui_arm_show_label_axis(self.original_position_axis)  
        self.record_last_command = None  
        self.record_area_data_queue = messageQueue.MessageQueue()  
        self.threshold_value = 100  
        self.gauss_value = 3 
        self.sharpen_value = 5  
        self.img_flag = 0 
        self.last_axis_point = [0, 200]  
        self.label_videl_size = [self.label_Arm_Video.width(), self.label_Arm_Video.height()]  
        self.axis_map_x = [-100, 100]  
        self.axis_map_y = [250, 150]  
        self.lastPoint = [0, 0]  
        self.currentPoint = [0, 0]  
        self.isDrawing = False  
        self.painter_line_style = 0  
        self.contours_data = None  
        self.white_image = np.zeros((self.label_videl_size[1], self.label_videl_size[0], 3), dtype=np.uint8) 
        self.white_image[:, :, :] = [255, 255, 255]  
        img = QImage(self.white_image.data.tobytes(), self.white_image.shape[1], self.white_image.shape[0], QImage.Format_RGB888)  
        self.label_Arm_Video.setPixmap(QPixmap.fromImage(img)) 
        self.original_label_img = self.white_image.copy()  
        self.line_curves_count = 1  
        self.current_line_curves = 0  
        self.angle_value = 90  
        self.arm_switched_value = 10  
        self.arm_move_value = 1.0 
        self.arm_command_count = 0  
        self.filePath = FileDialogHelper()
        self.connect()  

    def connect(self):
        self.lineEdit_Arm_IP_Address.textChanged.connect(self.save_ip_address)  
        self.pushButton_Arm_Connect.clicked.connect(self.btn_connect_remote_ip) 
        self.ui_arm_btn_connect.connect(self.ui_arm_show_btn_connect_content)  
        self.threading_cmd.connect(self.socket_send)
        self.pushButton_Arm_Stop_Arm.clicked.connect(self.btn_stop_arm) 
        self.pushButton_Arm_Zero_Point.clicked.connect(self.btn_move_to_zero_point) 
        self.pushButton_Arm_Load_Relax.clicked.connect(self.btn_load_relax_arm)  
        self.pushButton_Arm_Buzzer.pressed.connect(lambda: self.btn_control_buzzer(self.pushButton_Arm_Buzzer))  
        self.pushButton_Arm_Buzzer.released.connect(lambda: self.btn_control_buzzer(self.pushButton_Arm_Buzzer))  
        self.pushButton_Arm_Position.clicked.connect(self.btn_move_to_position_point) 
        self.pushButton_Arm_Home_Up.clicked.connect(self.btn_move_to_above_home_point)  
        self.pushButton_Arm_Axis_X_Subtract.clicked.connect(lambda: self.btn_move_to_anywhere(self.pushButton_Arm_Axis_X_Subtract))  
        self.pushButton_Arm_Axis_Y_Subtract.clicked.connect(lambda: self.btn_move_to_anywhere(self.pushButton_Arm_Axis_Y_Subtract)) 
        self.pushButton_Arm_Axis_Z_Subtract.clicked.connect(lambda: self.btn_move_to_anywhere(self.pushButton_Arm_Axis_Z_Subtract)) 
        self.pushButton_Arm_Axis_X_Add.clicked.connect(lambda: self.btn_move_to_anywhere(self.pushButton_Arm_Axis_X_Add)) 
        self.pushButton_Arm_Axis_Y_Add.clicked.connect(lambda: self.btn_move_to_anywhere(self.pushButton_Arm_Axis_Y_Add)) 
        self.pushButton_Arm_Axis_Z_Add.clicked.connect(lambda: self.btn_move_to_anywhere(self.pushButton_Arm_Axis_Z_Add)) 
        self.pushButton_Arm_Axis_Switched.clicked.connect(lambda: self.btn_move_to_anywhere(self.pushButton_Arm_Axis_Switched)) 
        self.pushButton_Arm_Record_Command.clicked.connect(lambda: self.btn_arm_operation(self.pushButton_Arm_Record_Command)) 
        self.pushButton_Arm_Withdraw_Command.clicked.connect(lambda: self.btn_arm_operation(self.pushButton_Arm_Withdraw_Command))  
        self.pushButton_Arm_Execute_Record_Command.clicked.connect(lambda: self.btn_arm_operation(self.pushButton_Arm_Execute_Record_Command)) 
        self.pushButton_Arm_Import_Record_Command.clicked.connect(lambda: self.btn_arm_operation(self.pushButton_Arm_Import_Record_Command)) 
        self.pushButton_Arm_Save_Record_Command.clicked.connect(lambda: self.btn_arm_operation(self.pushButton_Arm_Save_Record_Command))  

        self.radioButton_Arm_Img_Mode.clicked.connect(lambda: self.radioButton_arm_select_mode(self.radioButton_Arm_Img_Mode)) 
        self.radioButton_Arm_Line_Mode.clicked.connect(lambda: self.radioButton_arm_select_mode(self.radioButton_Arm_Line_Mode))  
        self.radioButton_Arm_Curves_Mode.clicked.connect(lambda: self.radioButton_arm_select_mode(self.radioButton_Arm_Curves_Mode))  
        self.pushButton_Arm_Import_Picture.clicked.connect(lambda: self.set_img_action(self.pushButton_Arm_Import_Picture)) 
        self.pushButton_Arm_Gray_Picture.clicked.connect(lambda: self.set_img_action(self.pushButton_Arm_Gray_Picture))  
        self.pushButton_Arm_Binaryzation_Picture.clicked.connect(lambda: self.set_img_action(self.pushButton_Arm_Binaryzation_Picture)) 
        self.pushButton_Arm_Contour_Picture.clicked.connect(lambda: self.set_img_action(self.pushButton_Arm_Contour_Picture))
        self.pushButton_Arm_Clear_All.clicked.connect(lambda: self.set_img_action(self.pushButton_Arm_Clear_All)) 
        self.pushButton_Arm_Change_Gcode.clicked.connect(lambda: self.set_img_action(self.pushButton_Arm_Change_Gcode))
        self.pushButton_Arm_Execute_Gcode.clicked.connect(lambda: self.set_img_action(self.pushButton_Arm_Execute_Gcode)) 
        if platform.system() == "Windows":
            self.horizontalSlider_Arm_Threshold.sliderReleased.connect(lambda: self.img_slider_control(self.horizontalSlider_Arm_Threshold))  
            self.horizontalSlider_Arm_Gauss.sliderReleased.connect(lambda: self.img_slider_control(self.horizontalSlider_Arm_Gauss))  
            self.horizontalSlider_Arm_Sharpen.sliderReleased.connect(lambda: self.img_slider_control(self.horizontalSlider_Arm_Sharpen))  
            self.horizontalSlider_Arm_Pen_Height.sliderReleased.connect(lambda: self.img_slider_control(self.horizontalSlider_Arm_Pen_Height))
        else:
            self.horizontalSlider_Arm_Threshold.valueChanged.connect(lambda: self.img_slider_control(self.horizontalSlider_Arm_Threshold)) 
            self.horizontalSlider_Arm_Gauss.valueChanged.connect(lambda: self.img_slider_control(self.horizontalSlider_Arm_Gauss)) 
            self.horizontalSlider_Arm_Sharpen.valueChanged.connect(lambda: self.img_slider_control(self.horizontalSlider_Arm_Sharpen))
            self.horizontalSlider_Arm_Pen_Height.valueChanged.connect(lambda: self.img_slider_control(self.horizontalSlider_Arm_Pen_Height)) 
        self.pushButton_Arm_Servo_Turn_On.clicked.connect(lambda: self.control_servo_angle(self.pushButton_Arm_Servo_Turn_On)) 
        self.pushButton_Arm_Servo_Turn_Off.clicked.connect(lambda: self.control_servo_angle(self.pushButton_Arm_Servo_Turn_Off)) 
        self.pushButton_Arm_Parameter_UI.clicked.connect(self.configure_parameter_ui)  
        self.pushButton_Arm_Led_UI.clicked.connect(self.configure_led_ui) 

    @staticmethod
    def map(value, fromLow, fromHigh, toLow, toHigh, num):
        return round(((toHigh - toLow) * (value - fromLow) / (fromHigh - fromLow) + toLow), num)

    @staticmethod
    def constrain(value, range_min, range_max):
        if value > range_max:
            value = range_max
        if value < range_min:
            value = range_min
        return value

    def record_command(self, cmd):
        self.record_last_command = cmd

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

    def ui_arm_show_label_axis(self, axis):
        self.label_Arm_Axis_X_Value.setText(str(axis[0]))  
        self.label_Arm_Axis_Y_Value.setText(str(axis[1]))  
        self.label_Arm_Axis_Z_Value.setText(str(axis[2]))  

    def ui_arm_show_record_area(self):
        self.textEdit_Arm_Record_Area.clear()
        cmd = self.record_area_data_queue.gets()
        for i in range(self.record_area_data_queue.len()):
            self.textEdit_Arm_Record_Area.append(cmd[i])

    def save_ip_address(self):
        self.record.write_remote_ip(self.lineEdit_Arm_IP_Address.text())

    def process_message(self):
        while True:
            if not self.client.connect_flag:
                self.client.disconnect()
                print("Disconnected the remote ip.")
                self.ui_arm_btn_connect.emit("Connect")
                break
            if self.client.data_queue.empty() is not True:
                try:
                    buf = self.client.data_queue.get()
                    self.message_parser.parser(buf)
                    if self.message_parser.commandArray[0] == self.cmd.CUSTOM_ACTION:
                        if self.message_parser.commandArray[1] == self.cmd.ARM_QUERY:
                            if self.gcode_command.len() > 0:
                                self.arm_command_count = self.message_parser.intParameter[1]
                                self.send_g_code_state = True
                            elif self.gcode_command.len() == 0:
                                self.arm_command_count = 0
                                self.send_g_code_state = False
                                cmd = self.cmd.CUSTOM_ACTION + str('12') + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_QUERY + str('0')
                                self.threading_cmd.emit(cmd)
                        else:
                            print(self.message_parser.inputCommandArray)
                    else:
                        print(self.message_parser.inputCommandArray)
                        self.message_parser.clearParameters()
                except:
                    pass
            else:
                pass

    def btn_connect_remote_ip(self):
        if self.pushButton_Arm_Connect.text() == "Connect":  
            self.client.ip = self.lineEdit_Arm_IP_Address.text()
            if self.client.connect(self.client.ip):  
                print("Connected the remote ip.")
                self.read_cmd_handling = threading.Thread(target=self.client.receive_messages)  
                self.read_cmd_handling.start()
                self.message_handling = threading.Thread(target=self.process_message) 
                self.message_handling.start() 
                self.pushButton_Arm_Connect.setText("Disconnect") 
            else:  
                print("Failed to connect the remote ip.")
                self.pushButton_Arm_Connect.setText("Connect")  
        elif self.pushButton_Arm_Connect.text() == "Disconnect": 
            try:
                messageThread.stop_thread(self.read_cmd_handling)  
                messageThread.stop_thread(self.message_handling)
                if self.configurationWindow != None:
                    self.configurationWindow.close()
                if self.ledWindow != None:
                    self.ledWindow.close()
            except:
                pass
            self.client.disconnect() 
            print("Disconnected the remote ip.")
            self.pushButton_Arm_Connect.setText("Connect")  
            self.pushButton_Arm_Load_Relax.setText("Load Motor")

    def ui_arm_show_btn_connect_content(self, content):
        if self.configurationWindow != None:
            self.configurationWindow.close()
        if self.ledWindow != None:
            self.ledWindow.close()
        self.pushButton_Arm_Load_Relax.setText("Load Motor")
        self.pushButton_Arm_Connect.setText(content)

    def btn_stop_arm(self):
        if self.client.connect_flag:
            self.client_busy = True
            cmd = self.cmd.CUSTOM_ACTION + str("13") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_STOP + str("1")
            self.threading_cmd.emit(cmd)
            self.client_busy = False
            if self.configurationWindow != None:
                self.configurationWindow.close()
            if self.ledWindow != None:
                self.ledWindow.close()
            self.pushButton_Arm_Load_Relax.setText("Load Motor")
        else:
            print("Connect the remote IP address first.")

    def btn_move_to_zero_point(self):
        cmd = self.cmd.CUSTOM_ACTION + str("10") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_SENSOR_POINT + str("1")
        self.threading_cmd.emit(cmd)

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

    def btn_move_to_position_point(self):
        if self.client.connect_flag:
            if self.pushButton_Arm_Load_Relax.text() == "Relax Motor":
                self.client_busy = True
                if self.record_last_command == "S8 E0": 
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

    def btn_move_to_above_home_point(self):
        if self.client.connect_flag:
            if self.pushButton_Arm_Load_Relax.text() == "Relax Motor":
                self.client_busy = True
                if self.record_last_command == "S8 E0": 
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
            self.folder_path = self.filePath.getFilePath("./record/*")  
            print(self.folder_path)
            if self.folder_path is not None:
                if self.folder_path.split(".")[1] == "txt":  
                    fb = open(self.folder_path, "r") 
                    self.record_area_data_queue.clear()  
                    line = fb.readline()
                    while line:  
                        txt_command = line.split("\n")[0]  
                        self.record_area_data_queue.put(txt_command)  
                        line = fb.readline()  
                    self.ui_arm_show_record_area() 
                    fb.close() 
            else:
                print("Cancel the instructions in the import file.")

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

    def send_Image_command(self):
        if not self.gcode_command.empty():
            if self.client.connect_flag:
                self.client_busy = True
                cmd = self.cmd.CUSTOM_ACTION + str("12") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_QUERY + str("1")
                self.threading_cmd.emit(cmd)
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

    def set_img_action(self, index):
        if index.objectName() == "pushButton_Arm_Import_Picture": 
            try:
                self.folder_path = self.filePath.getFilePath("./picture/*")
                if self.folder_path is not None:
                    print(self.folder_path)
                    white_image = self.white_image.copy() 
                    self.img_flag = 1
                    img = cv2.imdecode(np.fromfile(self.folder_path.encode('utf-8'), dtype=np.uint8), cv2.IMREAD_COLOR)
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  
                    img_h, img_w = img.shape[:2]
                    label_h = self.label_videl_size[1]
                    label_w = self.label_videl_size[0]
                    if img_h <= label_h and img_w <= label_w: 
                        picture_center = ((label_h - img_h) // 2, (label_w - img_w) // 2)  
                        white_image[picture_center[0]:picture_center[0] + img_h, picture_center[1]:picture_center[1] + img_w] = img
                    elif img_h > label_h or img_w > label_w: 
                        scale = min((label_h-2) / img_h, (label_w-2) / img_w)
                        new_img_h = int(scale * img_h)
                        new_img_w = int(scale * img_w)
                        resized_img = cv2.resize(img, (new_img_w, new_img_h), interpolation=cv2.INTER_AREA)
                        picture_center = ((label_h - new_img_h) // 2, (label_w - new_img_w) // 2)
                        white_image[picture_center[0]:picture_center[0] + new_img_h, picture_center[1]:picture_center[1] + new_img_w] = resized_img
                    img = white_image.copy()
                    self.raw_img = img.copy()  
                    img = QImage(img.data.tobytes(), img.shape[1], img.shape[0], QImage.Format_RGB888)  
                    self.label_Arm_Video.setPixmap(QPixmap.fromImage(img)) 
                    self.original_label_img = self.raw_img.copy()
                else:
                    print("Folder path is None.")
            except:
                self.img_flag = 0
                print("Load picture failed.")
                self.axis_paint_function = False  
                img = QImage(self.white_image.data.tobytes(), self.white_image.shape[1], self.white_image.shape[0], QImage.Format_RGB888) 
                self.label_Arm_Video.setPixmap(QPixmap.fromImage(img)) 
                self.original_label_img = self.white_image.copy()
        elif index.objectName() == "pushButton_Arm_Gray_Picture": 
            try:
                if len(self.raw_img):
                    self.img_flag = 2
                    self.gray_img = cv2.cvtColor(self.raw_img, cv2.COLOR_BGR2GRAY)  
                    img = QImage(self.gray_img.data.tobytes(), self.gray_img.shape[1], self.gray_img.shape[0], QImage.Format_Indexed8) 
                    self.label_Arm_Video.setPixmap(QPixmap.fromImage(img))  
                    self.original_label_img = self.gray_img.copy()
            except:
                print("Show gary picture failed.")
        elif index.objectName() == "pushButton_Arm_Binaryzation_Picture":  
            try:
                if len(self.gray_img):
                    self.img_flag = 3
                    img = self.gray_img.copy() 
                    ret, binary = cv2.threshold(img, self.threshold_value, 255, cv2.THRESH_BINARY)  
                    img = cv2.GaussianBlur(binary, (self.gauss_value, self.gauss_value), 0, 0)  
                    kernel = np.array([[0, -1, 0], [-1, self.sharpen_value, -1], [0, -1, 0]], np.float32)  
                    img = cv2.filter2D(img, -1, kernel=kernel) 
                    self.binary_img = img.copy()  
                    img = QImage(img.data.tobytes(), img.shape[1], img.shape[0], QImage.Format_Indexed8)  
                    self.label_Arm_Video.setPixmap(QPixmap.fromImage(img))
                    self.original_label_img = self.binary_img.copy()
            except:
                print("Show binaryzation picture failed.")
        elif index.objectName() == "pushButton_Arm_Contour_Picture":
            try:
                if len(self.binary_img):
                    self.img_flag = 4
                    img = self.binary_img.copy() 
                    self.contours_data = None  
                    self.hierarchy_data = None 
                    #self.contours_data, self.hierarchy_data = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
                    self.contours_data, self.hierarchy_data = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                    img1 = self.raw_img.copy()
                    img1 = np.zeros(shape=img.shape, dtype=np.uint8)  
                    img1 += 255  
                    cv2.drawContours(img1, self.contours_data, -1, (0, 0, 0), 1)  
                    self.contour_img = img1.copy()  
                    img1 = QImage(img1.data.tobytes(), img1.shape[1], img1.shape[0], QImage.Format_Indexed8)  
                    self.label_Arm_Video.setPixmap(QPixmap.fromImage(img1))
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
                                if j == 0: 
                                    gcode_change_command = self.cmd.MOVE_ACTION + str("0") + self.cmd.DECOLLATOR_CHAR \
                                        + self.cmd.AXIS_X_ACTION + str(self.last_axis_point[0]) + self.cmd.DECOLLATOR_CHAR \
                                        + self.cmd.AXIS_Y_ACTION + str(self.last_axis_point[1]) + self.cmd.DECOLLATOR_CHAR \
                                        + self.cmd.AXIS_Z_ACTION + str(round(z_height, 1))
                                    self.gcode_command.put(gcode_change_command)
                                    x = self.map(buf[0], 0, self.label_videl_size[0], self.axis_map_x[0], self.axis_map_x[1], 1)
                                    y = self.map(buf[1], 0, self.label_videl_size[1], self.axis_map_y[0], self.axis_map_y[1], 1)
                                    gcode_change_command = self.cmd.MOVE_ACTION + str("0") + self.cmd.DECOLLATOR_CHAR \
                                        + self.cmd.AXIS_X_ACTION + str(x) + self.cmd.DECOLLATOR_CHAR \
                                        + self.cmd.AXIS_Y_ACTION + str(y) + self.cmd.DECOLLATOR_CHAR \
                                        + self.cmd.AXIS_Z_ACTION + str(round(z_height, 1))
                                    self.gcode_command.put(gcode_change_command)
                                    gcode_change_command = self.cmd.MOVE_ACTION + str("0") + self.cmd.DECOLLATOR_CHAR \
                                        + self.cmd.AXIS_X_ACTION + str(x) + self.cmd.DECOLLATOR_CHAR \
                                        + self.cmd.AXIS_Y_ACTION + str(y) + self.cmd.DECOLLATOR_CHAR \
                                        + self.cmd.AXIS_Z_ACTION + str(z_axis)
                                    self.gcode_command.put(gcode_change_command)
                                    track_last_point_command = [x, y]
                                    self.last_axis_point = [x, y]
                                else:  
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
                        gcode_change_command = self.cmd.MOVE_ACTION + str("0") + self.cmd.DECOLLATOR_CHAR \
                            + self.cmd.AXIS_X_ACTION + str(self.last_axis_point[0]) + self.cmd.DECOLLATOR_CHAR \
                            + self.cmd.AXIS_Y_ACTION + str(self.last_axis_point[1]) + self.cmd.DECOLLATOR_CHAR \
                            + self.cmd.AXIS_Z_ACTION + str(round(z_height, 1))
                        self.gcode_command.put(gcode_change_command)
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
                    self.gcode_command.clear()  
                    self.textEdit_Arm_Gcode_Area.clear()
                    if self.painter_point.len() > 0:
                        self.current_line_curves = 0
                        buf_point = self.painter_point.gets()
                        for i in range(self.painter_point.len()):
                            # print(buf_point[i])
                            if self.current_line_curves != buf_point[i][2]: 
                                x = self.last_axis_point[0]
                                y = self.last_axis_point[1]
                                gcode_change_command = self.cmd.MOVE_ACTION + str("0") + self.cmd.DECOLLATOR_CHAR \
                                    + self.cmd.AXIS_X_ACTION + str(x) + self.cmd.DECOLLATOR_CHAR \
                                    + self.cmd.AXIS_Y_ACTION + str(y) + self.cmd.DECOLLATOR_CHAR \
                                    + self.cmd.AXIS_Z_ACTION + str(round(z_height, 1))
                                self.gcode_command.put(gcode_change_command)
                                x = self.map(buf_point[i][0][0], 0, self.label_videl_size[0], self.axis_map_x[0], self.axis_map_x[1], 1)
                                y = self.map(buf_point[i][0][1], 0, self.label_videl_size[1], self.axis_map_y[0], self.axis_map_y[1], 1)
                                gcode_change_command = self.cmd.MOVE_ACTION + str("0") + self.cmd.DECOLLATOR_CHAR \
                                    + self.cmd.AXIS_X_ACTION + str(x) + self.cmd.DECOLLATOR_CHAR \
                                    + self.cmd.AXIS_Y_ACTION + str(y) + self.cmd.DECOLLATOR_CHAR \
                                    + self.cmd.AXIS_Z_ACTION + str(round(z_height, 1))
                                self.gcode_command.put(gcode_change_command)
                                gcode_change_command = self.cmd.MOVE_ACTION + str("0") + self.cmd.DECOLLATOR_CHAR \
                                    + self.cmd.AXIS_X_ACTION + str(x) + self.cmd.DECOLLATOR_CHAR \
                                    + self.cmd.AXIS_Y_ACTION + str(y) + self.cmd.DECOLLATOR_CHAR \
                                    + self.cmd.AXIS_Z_ACTION + str(z_axis)
                                self.gcode_command.put(gcode_change_command)
                                x = self.map(buf_point[i][1][0], 0, self.label_videl_size[0], self.axis_map_x[0], self.axis_map_x[1], 1)
                                y = self.map(buf_point[i][1][1], 0, self.label_videl_size[1], self.axis_map_y[0], self.axis_map_y[1], 1)
                                gcode_change_command = self.cmd.MOVE_ACTION + str("0") + self.cmd.DECOLLATOR_CHAR \
                                    + self.cmd.AXIS_X_ACTION + str(x) + self.cmd.DECOLLATOR_CHAR \
                                    + self.cmd.AXIS_Y_ACTION + str(y) + self.cmd.DECOLLATOR_CHAR \
                                    + self.cmd.AXIS_Z_ACTION + str(z_axis)
                                self.gcode_command.put(gcode_change_command)
                                self.last_axis_point = [x, y]
                                self.current_line_curves = buf_point[i][2] 
                            else:
                                x = self.map(buf_point[i][1][0], 0, self.label_videl_size[0], self.axis_map_x[0], self.axis_map_x[1], 1)
                                y = self.map(buf_point[i][1][1], 0, self.label_videl_size[1], self.axis_map_y[0], self.axis_map_y[1], 1)
                                gcode_change_command = self.cmd.MOVE_ACTION + str("0") + self.cmd.DECOLLATOR_CHAR \
                                    + self.cmd.AXIS_X_ACTION + str(x) + self.cmd.DECOLLATOR_CHAR \
                                    + self.cmd.AXIS_Y_ACTION + str(y) + self.cmd.DECOLLATOR_CHAR \
                                    + self.cmd.AXIS_Z_ACTION + str(z_axis)
                                self.gcode_command.put(gcode_change_command)
                                self.last_axis_point = [x, y]
                        x = self.last_axis_point[0]
                        y = self.last_axis_point[1]
                        gcode_change_command = self.cmd.MOVE_ACTION + str("0") + self.cmd.DECOLLATOR_CHAR \
                            + self.cmd.AXIS_X_ACTION + str(x) + self.cmd.DECOLLATOR_CHAR \
                            + self.cmd.AXIS_Y_ACTION + str(y) + self.cmd.DECOLLATOR_CHAR \
                            + self.cmd.AXIS_Z_ACTION + str(round(z_height, 1))
                        self.gcode_command.put(gcode_change_command)
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

    def img_slider_control(self, index):
        if index.objectName() == "horizontalSlider_Arm_Threshold": 
            self.threshold_value = index.value()
            self.lineEdit_Arm_Threshold_Value.setText(str(self.threshold_value))  
        elif index.objectName() == "horizontalSlider_Arm_Gauss":
            self.gauss_value = index.value()  
            if self.gauss_value % 2 == 0:  
                self.gauss_value = self.gauss_value + 1  
            self.lineEdit_Arm_Gauss_Value.setText(str(self.gauss_value)) 
            index.setValue(self.gauss_value) 
        elif index.objectName() == "horizontalSlider_Arm_Sharpen":
            self.sharpen_value = index.value() 
            self.lineEdit_Arm_Sharpen_Value.setText(str(self.sharpen_value)) 
        elif index.objectName() == "horizontalSlider_Arm_Pen_Height":
            self.lineEdit_Arm_Pen_Height_Value.setText(str(index.value()))
        if self.img_flag >= 3:
            try:
                img = self.gray_img.copy() 
                ret, binary = cv2.threshold(img, self.threshold_value, 255, cv2.THRESH_BINARY)
                img = cv2.GaussianBlur(binary, (self.gauss_value, self.gauss_value), 0, 0)  
                kernel = np.array([[0, -1, 0], [-1, self.sharpen_value, -1], [0, -1, 0]], np.float32) 
                img = cv2.filter2D(img, -1, kernel=kernel)  
                self.binary_img = img.copy() 
                self.original_label_img = img.copy()
                if self.img_flag == 4:
                    self.contours_data = None 
                    self.hierarchy_data = None 
                    #self.contours_data, self.hierarchy_data = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
                    self.contours_data, self.hierarchy_data = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                    img1 = np.zeros(shape=img.shape, dtype=np.uint8) 
                    img1 += 255  
                    cv2.drawContours(img1, self.contours_data, -1, (0, 0, 0), 1)
                    self.contour_img = img1.copy()  
                    self.original_label_img = img1.copy()
                    img1 = QImage(img1.data.tobytes(), img1.shape[1], img1.shape[0],
                                  QImage.Format_Indexed8)  
                    self.label_Arm_Video.setPixmap(QPixmap.fromImage(img1))  
                else:
                    img = QImage(img.data.tobytes(), img.shape[1], img.shape[0], QImage.Format_Indexed8)  
                    self.label_Arm_Video.setPixmap(QPixmap.fromImage(img))
            except:
                print("Show binaryzation picture failed.")

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

    def updata_label_show(self):
        img = None
        start_point = (self.lastPoint[0], self.lastPoint[1])  
        end_point = (self.currentPoint[0], self.currentPoint[1])  
        if self.painter_line_style == 1:
            if self.isDrawing:
                img = self.original_label_img.copy()
            else:
                img = self.original_label_img  
        else:
            img = self.original_label_img
        if start_point != end_point:
            cv2.line(img, start_point, end_point, (0, 0, 0), 1, cv2.LINE_AA) 
        if self.img_flag <= 1:
            img = QImage(img.data.tobytes(), img.shape[1], img.shape[0], QImage.Format_RGB888) 
        else:
            img = QImage(img.data.tobytes(), img.shape[1], img.shape[0], QImage.Format_Indexed8)  
        self.label_Arm_Video.setPixmap(QPixmap.fromImage(img)) 

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: 
            if self.painter_line_style != 0:
                x = self.constrain(event.pos().x(), 0, self.label_videl_size[0])
                y = self.constrain(event.pos().y(), 0, self.label_videl_size[1])
                self.currentPoint = [x, y]  
                self.lastPoint = self.currentPoint.copy() 
                self.isDrawing = True

    def mouseMoveEvent(self, event):
        if event.buttons() and Qt.LeftButton:  
            if self.painter_line_style != 0:
                x = self.constrain(event.pos().x(), 0, self.label_videl_size[0])
                y = self.constrain(event.pos().y(), 0, self.label_videl_size[1])
                self.currentPoint = [x, y]
                self.updata_label_show()
                if self.painter_line_style == 2:
                    self.painter_point.put([self.lastPoint, self.currentPoint, self.line_curves_count])
                    self.lastPoint = self.currentPoint.copy()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:  
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

    def close_parameter_ui(self, data):
        data = data.split(",")
        if data[3] == "1":
            self.ui_arm_show_label_axis(data[:3])
            self.original_position_axis = data[:3]
            self.pushButton_Arm_Parameter_UI.setEnabled(True)
        elif data[3] == "0":
            self.ui_arm_show_label_axis(data[:3])
            self.original_position_axis = data[:3]

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

    def close_led_ui(self):
        self.pushButton_Arm_Led_UI.setEnabled(True)

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
