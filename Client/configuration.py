import sys

from PyQt5.QtGui import *
from PyQt5 import QtWidgets,QtCore
from PyQt5.QtCore import Qt
from command import Command
from ui.ui_parameter import Ui_Parameter
from messageRecord import MessageRecord

class Configuration(QtWidgets.QWidget, Ui_Parameter):
    # 定义一个信号通道，用来接受配置界面返回来的ip地址
    position_axis_channel = QtCore.pyqtSignal(str)
    send_cmd_channel = QtCore.pyqtSignal(str)

    #def __init__(self, client):
    def __init__(self):
        super(Configuration, self).__init__()
        self.setupUi(self)
        self.setFixedSize(713, 483)

        # 添加界面的logo
        self.setWindowIcon(QIcon('./picture/Freenove.ico'))  # 添加窗口logo
        #self.client = client
        self.cmd = Command()
        self.record = MessageRecord()
        self.z_original_height_value = 75     # 夹具末端z值
        self.lineEdit_Parameter_Axis = [[self.lineEdit_Parameter_Axis_X_0, self.lineEdit_Parameter_Axis_Y_0, self.lineEdit_Parameter_Axis_Z_0],
                                        [self.lineEdit_Parameter_Axis_X_1, self.lineEdit_Parameter_Axis_Y_1, self.lineEdit_Parameter_Axis_Z_1],
                                        [self.lineEdit_Parameter_Axis_X_2, self.lineEdit_Parameter_Axis_Y_2, self.lineEdit_Parameter_Axis_Z_2],
                                        [self.lineEdit_Parameter_Axis_X_3, self.lineEdit_Parameter_Axis_Y_3, self.lineEdit_Parameter_Axis_Z_3],
                                        [self.lineEdit_Parameter_Axis_X_4, self.lineEdit_Parameter_Axis_Y_4, self.lineEdit_Parameter_Axis_Z_4]]

        self.position_axis = [0.0, 200.0, self.z_original_height_value]      #中心点高度
        self.original_axis = [[0.0, 200.0, self.z_original_height_value],
                              [-100.0, 200.0, self.z_original_height_value],
                              [100.0, 200.0, self.z_original_height_value],
                              [0.0, 150.0, self.z_original_height_value],
                              [0.0, 250.0, self.z_original_height_value]]
        self.calibrated_axis = [[0.0, 0.0, 0.0],
                                [0.0, 0.0, 0.0],
                                [0.0, 0.0, 0.0],
                                [0.0, 0.0, 0.0],
                                [0.0, 0.0, 0.0]]
        self.radioButton_axis_flag = 0         # 记录当前选择哪一个checkbox
        self.load_configuration_ui()           # 加载参数，消耗了1秒
        self.set_radioButton_color(0)          # 设置Point 0行显黄色
        self.connect()                         # 信号与槽函数，消耗了1秒多

    # 加载界面参数
    def load_configuration_ui(self):
        value = self.record.read_ground_height()                                         # 获取机械臂转轴高度
        self.lineEdit_Parameter_Axis_Height.setText(str(value))                               # 显示机械臂转轴高度
        self.horizontalSlider_Parameter_Axis_Height.setValue(round(float(value)*10))     # 设置转轴高度滑条
        value = self.record.read_clamp_length()                                          # 获取夹具长度
        self.lineEdit_Parameter_Clamp_Length.setText(str(value))                              # 显示夹具长度
        self.horizontalSlider_Parameter_Clamp_Length.setValue(round(float(value)*10))    # 设置夹具长度
        value = self.record.read_clamp_height()                                          # 获取夹具高度
        self.lineEdit_Parameter_Clamp_Height.setText(str(value))                              # 显示夹具高度
        self.horizontalSlider_Parameter_Clamp_Height.setValue(round(float(value)*10))    # 设置夹具高度
        value = self.record.read_pen_height()                                            # 获取笔具高度
        self.lineEdit_Parameter_Pen_Height.setText(str(value))                                 # 显示笔具高度
        self.horizontalSlider_Parameter_Pen_Height.setValue(round(float(value)*10))      # 设置笔具滑条
        axis = [self.record.read_axis_point_1(), self.record.read_axis_point_2(), self.record.read_axis_point_3(), self.record.read_axis_point_4(), self.record.read_axis_point_5()]
        for i in range(5):
            for j in range(3):
                self.calibrated_axis[i][j] = float(axis[i][j])                                 # 将从本地文件中读取到的数据更新给self.calibrated_axis
                self.lineEdit_Parameter_Axis[i][j].setText(str(self.calibrated_axis[i][j]))    # 将从本地文件中读取到的数据加载到显示框中

        frequency = self.record.read_a4988_frequency()                                         # 获取机械臂频率
        self.lineEdit_Parameter_Arm_Frequency.setText(str(frequency))                          # 显示机械臂频率
        self.horizontalSlider_Parameter_Arm_Frequency.setValue(int(frequency)//50)             # 设置机械臂频率滑条

        self.position_axis = [float(self.record.read_position_point()[i]) for i in range(3)]   # 获取校准点数据
        self.label_Parameter_Default_Position_X.setText("X:" + str(self.position_axis[0]))
        self.label_Parameter_Default_Position_Y.setText("Y:" + str(self.position_axis[1]))
        self.label_Parameter_Default_Position_Z.setText("Z:" + str(self.position_axis[2]))

        for i in range(5):
            self.original_axis[i][2] = float(self.position_axis[2])                       # 更新每个校准坐标的z轴数据

    # 保存界面参数
    def save_configuration_ui(self):
        x = self.label_Parameter_Default_Position_X.text().split(":")[1]
        y = self.label_Parameter_Default_Position_Y.text().split(":")[1]
        z = self.label_Parameter_Default_Position_Z.text().split(":")[1]
        self.record.write_position_point(x, y, z)
        self.record.write_axis_point_1(self.lineEdit_Parameter_Axis_X_0.text(), self.lineEdit_Parameter_Axis_Y_0.text(), self.lineEdit_Parameter_Axis_Z_0.text())
        self.record.write_axis_point_2(self.lineEdit_Parameter_Axis_X_1.text(), self.lineEdit_Parameter_Axis_Y_1.text(), self.lineEdit_Parameter_Axis_Z_1.text())
        self.record.write_axis_point_3(self.lineEdit_Parameter_Axis_X_2.text(), self.lineEdit_Parameter_Axis_Y_2.text(), self.lineEdit_Parameter_Axis_Z_2.text())
        self.record.write_axis_point_4(self.lineEdit_Parameter_Axis_X_3.text(), self.lineEdit_Parameter_Axis_Y_3.text(), self.lineEdit_Parameter_Axis_Z_3.text())
        self.record.write_axis_point_5(self.lineEdit_Parameter_Axis_X_4.text(), self.lineEdit_Parameter_Axis_Y_4.text(), self.lineEdit_Parameter_Axis_Z_4.text())
        self.record.write_pen_height(self.lineEdit_Parameter_Pen_Height.text())
        self.record.write_a4988_frequency(self.lineEdit_Parameter_Arm_Frequency.text())
        self.record.write_ground_height(self.lineEdit_Parameter_Axis_Height.text())
        self.record.write_clamp_length(self.lineEdit_Parameter_Clamp_Length.text())
        self.record.write_clamp_height(self.lineEdit_Parameter_Clamp_Height.text())

    # 控件信号与槽函数
    def connect(self):
        #第一组框
        self.pushButton_Parameter_Adjust_Zero.clicked.connect(lambda: self.set_first_groupbox(self.pushButton_Parameter_Adjust_Zero))
        self.pushButton_Parameter_Zero_Point.clicked.connect(lambda: self.set_first_groupbox(self.pushButton_Parameter_Zero_Point))
        self.pushButton_Parameter_Default_Parameter.clicked.connect(lambda: self.set_first_groupbox(self.pushButton_Parameter_Default_Parameter))
        self.pushButton_Parameter_Default_Position.clicked.connect(lambda: self.set_first_groupbox(self.pushButton_Parameter_Default_Position))
        self.pushButton_Parameter_Default_Position.clicked.connect(lambda: self.update_main_default_position)
        #第二组框
        self.horizontalSlider_Parameter_Axis_Height.valueChanged.connect(lambda: self.set_second_groupbox(self.horizontalSlider_Parameter_Axis_Height))
        self.pushButton_Parameter_Axis_Height_Subtract.clicked.connect(lambda: self.set_second_groupbox(self.pushButton_Parameter_Axis_Height_Subtract))
        self.pushButton_Parameter_Axis_Height_Add.clicked.connect(lambda: self.set_second_groupbox(self.pushButton_Parameter_Axis_Height_Add))
        self.horizontalSlider_Parameter_Clamp_Length.valueChanged.connect(lambda: self.set_second_groupbox(self.horizontalSlider_Parameter_Clamp_Length))
        self.pushButton_Parameter_Clamp_Length_Subtract.clicked.connect(lambda: self.set_second_groupbox(self.pushButton_Parameter_Clamp_Length_Subtract))
        self.pushButton_Parameter_Clamp_Length_Add.clicked.connect(lambda: self.set_second_groupbox(self.pushButton_Parameter_Clamp_Length_Add))
        self.horizontalSlider_Parameter_Clamp_Height.valueChanged.connect(lambda: self.set_second_groupbox(self.horizontalSlider_Parameter_Clamp_Height))
        self.pushButton_Parameter_Clamp_Height_Subtract.clicked.connect(lambda: self.set_second_groupbox(self.pushButton_Parameter_Clamp_Height_Subtract))
        self.pushButton_Parameter_Clamp_Height_Add.clicked.connect(lambda: self.set_second_groupbox(self.pushButton_Parameter_Clamp_Height_Add))
        self.horizontalSlider_Parameter_Pen_Height.valueChanged.connect(lambda: self.set_second_groupbox(self.horizontalSlider_Parameter_Pen_Height))
        self.pushButton_Parameter_Pen_Height_Subtract.clicked.connect(lambda: self.set_second_groupbox(self.pushButton_Parameter_Pen_Height_Subtract))
        self.pushButton_Parameter_Pen_Height_Add.clicked.connect(lambda: self.set_second_groupbox(self.pushButton_Parameter_Pen_Height_Add))
        #第三组框
        self.radioButton_Parameter_Point_0.clicked.connect(lambda: self.select_third_checkbox(self.radioButton_Parameter_Point_0))
        self.radioButton_Parameter_Point_1.clicked.connect(lambda: self.select_third_checkbox(self.radioButton_Parameter_Point_1))
        self.radioButton_Parameter_Point_2.clicked.connect(lambda: self.select_third_checkbox(self.radioButton_Parameter_Point_2))
        self.radioButton_Parameter_Point_3.clicked.connect(lambda: self.select_third_checkbox(self.radioButton_Parameter_Point_3))
        self.radioButton_Parameter_Point_4.clicked.connect(lambda: self.select_third_checkbox(self.radioButton_Parameter_Point_4))
        self.radioButton_Parameter_Point_0.clicked.connect(lambda: self.set_third_groupbox(self.radioButton_Parameter_Point_0))
        self.radioButton_Parameter_Point_1.clicked.connect(lambda: self.set_third_groupbox(self.radioButton_Parameter_Point_1))
        self.radioButton_Parameter_Point_2.clicked.connect(lambda: self.set_third_groupbox(self.radioButton_Parameter_Point_2))
        self.radioButton_Parameter_Point_3.clicked.connect(lambda: self.set_third_groupbox(self.radioButton_Parameter_Point_3))
        self.radioButton_Parameter_Point_4.clicked.connect(lambda: self.set_third_groupbox(self.radioButton_Parameter_Point_4))
        self.pushButton_Parameter_Axis_X_Subtract.clicked.connect(lambda: self.set_third_groupbox(self.pushButton_Parameter_Axis_X_Subtract))
        self.pushButton_Parameter_Axis_Y_Subtract.clicked.connect(lambda: self.set_third_groupbox(self.pushButton_Parameter_Axis_Y_Subtract))
        self.pushButton_Parameter_Axis_Z_Subtract.clicked.connect(lambda: self.set_third_groupbox(self.pushButton_Parameter_Axis_Z_Subtract))
        self.pushButton_Parameter_Axis_X_Add.clicked.connect(lambda: self.set_third_groupbox(self.pushButton_Parameter_Axis_X_Add))
        self.pushButton_Parameter_Axis_Y_Add.clicked.connect(lambda: self.set_third_groupbox(self.pushButton_Parameter_Axis_Y_Add))
        self.pushButton_Parameter_Axis_Z_Add.clicked.connect(lambda: self.set_third_groupbox(self.pushButton_Parameter_Axis_Z_Add))
        self.pushButton_Parameter_Axis_Save.clicked.connect(lambda: self.set_third_groupbox(self.pushButton_Parameter_Axis_Save))
        #第四组框
        self.horizontalSlider_Parameter_Arm_Frequency.valueChanged.connect(lambda: self.set_fourth_groupbox(self.horizontalSlider_Parameter_Arm_Frequency))
        #self.horizontalSlider_Parameter_Arm_Frequency.sliderReleased.connect(lambda: self.set_fourth_groupbox(self.horizontalSlider_Parameter_Arm_Frequency))
        self.pushButton_Parameter_Arm_Frequency_Subtract.clicked.connect(lambda: self.set_fourth_groupbox(self.pushButton_Parameter_Arm_Frequency_Subtract))
        self.pushButton_Parameter_Arm_Frequency_Add.clicked.connect(lambda: self.set_fourth_groupbox(self.pushButton_Parameter_Arm_Frequency_Add))
    # 第一组框参数配置
    def set_first_groupbox(self, index):
        if index.objectName() == "pushButton_Parameter_Adjust_Zero":
            command = self.cmd.CUSTOM_ACTION + str("10") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_SENSOR_POINT + str("0")
            self.send_cmd(command)
        elif index.objectName() == "pushButton_Parameter_Zero_Point":
            command = self.cmd.CUSTOM_ACTION + str("10") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_SENSOR_POINT + str("1")
            self.send_cmd(command)
        elif index.objectName() == "pushButton_Parameter_Default_Parameter":
            for i in range(5):
                for j in range(3):
                    self.calibrated_axis[i][j] = 0.0
                    self.lineEdit_Parameter_Axis[i][j].setText(str(self.calibrated_axis[i][j]))
            self.lineEdit_Parameter_Axis_Height.setText(str("0.0"))
            self.horizontalSlider_Parameter_Axis_Height.setValue(0)
            self.lineEdit_Parameter_Clamp_Length.setText(str("15.0"))
            self.horizontalSlider_Parameter_Clamp_Length.setValue(230)
            self.lineEdit_Parameter_Clamp_Height.setText(str("45.0"))
            self.horizontalSlider_Parameter_Clamp_Height.setValue(450)
            self.lineEdit_Parameter_Pen_Height.setText(str("0.0"))
            self.horizontalSlider_Parameter_Pen_Height.setValue(0)
            self.lineEdit_Parameter_Arm_Frequency.setText(str("1000"))
            self.horizontalSlider_Parameter_Arm_Frequency.setValue(20)
            self.record.write_json_default_parameter()
        elif index.objectName() == "pushButton_Parameter_Default_Position":
            command = self.cmd.CUSTOM_ACTION + str("3") + self.cmd.DECOLLATOR_CHAR + self.cmd.GROUND_HEIGHT + self.lineEdit_Parameter_Axis_Height.text()
            self.send_cmd(command)
            command = self.cmd.CUSTOM_ACTION + str("4") + self.cmd.DECOLLATOR_CHAR + self.cmd.CLAMP_LENGTH + self.lineEdit_Parameter_Clamp_Length.text()
            self.send_cmd(command)
            command = self.cmd.CUSTOM_ACTION + str("5") + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.AXIS_X_ACTION + str(self.position_axis[0]) + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.AXIS_Y_ACTION + str(self.position_axis[1]) + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.AXIS_Z_ACTION + str(self.position_axis[2])
            self.send_cmd(command)
            self.record.write_position_point(self.position_axis[0], self.position_axis[1], self.position_axis[2])

    # 第二组框参数配置
    def set_second_groupbox(self, index):
        if index.objectName() == "horizontalSlider_Parameter_Axis_Height":
            show_axis_height = round(self.horizontalSlider_Parameter_Axis_Height.value() * 0.1, 1)       #获取滑条值
            self.lineEdit_Parameter_Axis_Height.setText(str(show_axis_height))                           #显示滑条值
            self.record.write_ground_height(str(show_axis_height))                                         #写入本地
        elif index.objectName() == "pushButton_Parameter_Axis_Height_Subtract":
            value = self.horizontalSlider_Parameter_Axis_Height.value() - 1
            if value < 0:
                value = 0
            elif value > 1000:
                value = 1000
            self.horizontalSlider_Parameter_Axis_Height.setValue(value)
            show_axis_height = round(value * 0.1, 1)
            self.lineEdit_Parameter_Axis_Height.setText(str(show_axis_height))
            self.record.write_ground_height(str(show_axis_height))
        elif index.objectName() == "pushButton_Parameter_Axis_Height_Add":
            value = self.horizontalSlider_Parameter_Axis_Height.value() + 1
            if value < 0:
                value = 0
            elif value > 1000:
                value = 1000
            self.horizontalSlider_Parameter_Axis_Height.setValue(value)
            show_axis_height = round(value * 0.1, 1)
            self.lineEdit_Parameter_Axis_Height.setText(str(show_axis_height))
            self.record.write_ground_height(str(show_axis_height))

        elif index.objectName() == "horizontalSlider_Parameter_Clamp_Length":
            show_clamp_length = round(self.horizontalSlider_Parameter_Clamp_Length.value() * 0.1, 1)       #获取滑条值
            self.lineEdit_Parameter_Clamp_Length.setText(str(show_clamp_length))                           #显示滑条值
            self.record.write_clamp_length(str(show_clamp_length))                                         #写入本地

        elif index.objectName() == "pushButton_Parameter_Clamp_Length_Subtract":
            value = self.horizontalSlider_Parameter_Clamp_Length.value() - 1
            if value < 0:
                value = 0
            elif value > 1000:
                value = 1000
            self.horizontalSlider_Parameter_Clamp_Length.setValue(value)
            show_clamp_length = round(value * 0.1, 1)
            self.lineEdit_Parameter_Clamp_Length.setText(str(show_clamp_length))
            self.record.write_clamp_length(str(show_clamp_length))
        elif index.objectName() == "pushButton_Parameter_Clamp_Length_Add":
                value = self.horizontalSlider_Parameter_Clamp_Length.value() + 1
                if value < 0:
                    value = 0
                elif value > 1000:
                    value = 1000
                self.horizontalSlider_Parameter_Clamp_Length.setValue(value)
                show_clamp_length = round(value * 0.1, 1)
                self.lineEdit_Parameter_Clamp_Length.setText(str(show_clamp_length))
                self.record.write_clamp_length(str(show_clamp_length))

        elif index.objectName() == "horizontalSlider_Parameter_Clamp_Height":
            show_clamp_height = round(self.horizontalSlider_Parameter_Clamp_Height.value() * 0.1, 1)       #获取滑条值
            self.lineEdit_Parameter_Clamp_Height.setText(str(show_clamp_height))                           #显示滑条值
            self.record.write_clamp_height(str(show_clamp_height))
            self.z_original_height_value = float(self.lineEdit_Parameter_Clamp_Height.text()) + float(self.lineEdit_Parameter_Pen_Height.text())
            self.position_axis[2] = round(self.z_original_height_value, 1)
            self.label_Parameter_Default_Position_Z.setText("Z:" + str(self.position_axis[2]))
            for i in range(5):
                self.original_axis[i][2] = round(self.z_original_height_value, 1)
        elif index.objectName() == "pushButton_Parameter_Clamp_Height_Subtract":
            value = self.horizontalSlider_Parameter_Clamp_Height.value() - 1
            if value < 0:
                value = 0
            elif value > 1000:
                value = 1000
            self.horizontalSlider_Parameter_Clamp_Height.setValue(value)
            show_clamp_height = round(value * 0.1, 1)
            self.lineEdit_Parameter_Clamp_Height.setText(str(show_clamp_height))
            self.record.write_clamp_height(str(show_clamp_height))
            self.z_original_height_value = float(self.lineEdit_Parameter_Clamp_Height.text()) + float(self.lineEdit_Parameter_Pen_Height.text())
            self.position_axis[2] = round(self.z_original_height_value, 1)
            self.label_Parameter_Default_Position_Z.setText("Z:" + str(self.position_axis[2]))
            for i in range(5):
                self.original_axis[i][2] = round(self.z_original_height_value, 1)
        elif index.objectName() == "pushButton_Parameter_Clamp_Height_Add":
            value = self.horizontalSlider_Parameter_Clamp_Height.value() + 1
            if value < 0:
                value = 0
            elif value > 1000:
                value = 1000
            self.horizontalSlider_Parameter_Clamp_Height.setValue(value)
            show_clamp_height = round(value * 0.1, 1)
            self.lineEdit_Parameter_Clamp_Height.setText(str(show_clamp_height))
            self.record.write_clamp_height(str(show_clamp_height))
            self.z_original_height_value = float(self.lineEdit_Parameter_Clamp_Height.text()) + float(self.lineEdit_Parameter_Pen_Height.text())
            self.position_axis[2] = round(self.z_original_height_value, 1)
            self.label_Parameter_Default_Position_Z.setText("Z:" + str(self.position_axis[2]))
            for i in range(5):
                self.original_axis[i][2] = round(self.z_original_height_value, 1)
        elif index.objectName() == "horizontalSlider_Parameter_Pen_Height":
            show_pen_height = round(self.horizontalSlider_Parameter_Pen_Height.value() * 0.1, 1)
            self.lineEdit_Parameter_Pen_Height.setText(str(show_pen_height))
            self.record.write_pen_height(str(show_pen_height))
            self.z_original_height_value = float(self.lineEdit_Parameter_Clamp_Height.text()) + float(self.lineEdit_Parameter_Pen_Height.text())
            self.position_axis[2] = round(self.z_original_height_value, 1)
            self.label_Parameter_Default_Position_Z.setText("Z:" + str(self.position_axis[2]))
            for i in range(5):
                self.original_axis[i][2] = round(self.z_original_height_value, 1)
        elif index.objectName() == "pushButton_Parameter_Pen_Height_Subtract":
            value = self.horizontalSlider_Parameter_Pen_Height.value() - 1
            if value < 0:
                value = 0
            elif value > 1200:
                value = 1200
            self.horizontalSlider_Parameter_Pen_Height.setValue(value)
            show_pen_height = round(value * 0.1, 1)
            self.lineEdit_Parameter_Pen_Height.setText(str(show_pen_height))
            self.record.write_pen_height(str(show_pen_height))
            self.z_original_height_value = float(self.lineEdit_Parameter_Clamp_Height.text()) + float(self.lineEdit_Parameter_Pen_Height.text())
            self.position_axis[2] = round(self.z_original_height_value, 1)
            self.label_Parameter_Default_Position_Z.setText("Z:" + str(self.position_axis[2]))
            for i in range(5):
                self.original_axis[i][2] = round(self.z_original_height_value, 1)
        elif index.objectName() == "pushButton_Parameter_Pen_Height_Add":
            value = self.horizontalSlider_Parameter_Pen_Height.value() + 1
            if value < 0:
                value = 0
            elif value > 1200:
                value = 1200
            self.horizontalSlider_Parameter_Pen_Height.setValue(value)
            show_pen_height = round(value * 0.1, 1)
            self.lineEdit_Parameter_Pen_Height.setText(str(show_pen_height))
            self.record.write_pen_height(str(show_pen_height))
            self.z_original_height_value = float(self.lineEdit_Parameter_Clamp_Height.text()) + float(self.lineEdit_Parameter_Pen_Height.text())
            self.position_axis[2] = round(self.z_original_height_value, 1)
            self.label_Parameter_Default_Position_Z.setText("Z:" + str(self.position_axis[2]))
            for i in range(5):
                self.original_axis[i][2] = round(self.z_original_height_value, 1)

    # 设置调参框的颜色
    def set_radioButton_color(self, index):
        radioButton_sheet = "QLineEdit{\n" \
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
        for i in range(5):
            for j in range(3):
                self.lineEdit_Parameter_Axis[i][j].setStyleSheet(radioButton_sheet)
        if index == 1:
            for j in range(3):
                self.lineEdit_Parameter_Axis[0][j].setStyleSheet("background-color: rgb(255, 238, 0);")
        elif index == 2:
            for j in range(3):
                self.lineEdit_Parameter_Axis[1][j].setStyleSheet("background-color: rgb(255, 238, 0);")
        elif index == 3:
            for j in range(3):
                self.lineEdit_Parameter_Axis[2][j].setStyleSheet("background-color: rgb(255, 238, 0);")
        elif index == 4:
            for j in range(3):
                self.lineEdit_Parameter_Axis[3][j].setStyleSheet("background-color: rgb(255, 238, 0);")
        elif index == 5:
            for j in range(3):
                self.lineEdit_Parameter_Axis[4][j].setStyleSheet("background-color: rgb(255, 238, 0);")
        elif index == 0:
            pass
    # 设置checkbox，由第三组框的checkbox触发
    def select_third_checkbox(self, index):
        radio_state = index.isChecked()
        self.radioButton_Parameter_Point_0.setChecked(False)
        self.radioButton_Parameter_Point_1.setChecked(False)
        self.radioButton_Parameter_Point_2.setChecked(False)
        self.radioButton_Parameter_Point_3.setChecked(False)
        self.radioButton_Parameter_Point_4.setChecked(False)
        if index.objectName() == "radioButton_Parameter_Point_0":
            if radio_state == True:
                self.set_radioButton_color(1)
                index.setChecked(True)
            else:
                self.set_radioButton_color(0)
        elif index.objectName() == "radioButton_Parameter_Point_1":
            if radio_state == True:
                self.set_radioButton_color(2)
                index.setChecked(True)
            else:
                self.set_radioButton_color(0)
        elif index.objectName() == "radioButton_Parameter_Point_2":
            if radio_state == True:
                self.set_radioButton_color(3)
                index.setChecked(True)
            else:
                self.set_radioButton_color(0)
        elif index.objectName() == "radioButton_Parameter_Point_3":
            if radio_state == True:
                self.set_radioButton_color(4)
                index.setChecked(True)
            else:
                self.set_radioButton_color(0)
        elif index.objectName() == "radioButton_Parameter_Point_4":
            if radio_state == True:
                self.set_radioButton_color(5)
                index.setChecked(True)
            else:
                self.set_radioButton_color(0)
    # 发送校准命令
    def send_calibrated_command(self, index):
        if index == 0:
            command = self.cmd.CUSTOM_ACTION + str("11") + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.ARM_CALIBRATION_POINT + str("0") + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.AXIS_X_ACTION + str(self.calibrated_axis[self.radioButton_axis_flag][0] + self.original_axis[0][0]) + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.AXIS_Y_ACTION + str(self.calibrated_axis[self.radioButton_axis_flag][1] + self.original_axis[0][1]) + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.AXIS_Z_ACTION + str(self.calibrated_axis[self.radioButton_axis_flag][2] + self.original_axis[0][2])
            if self.radioButton_Parameter_Point_0.isChecked()==True:
                self.send_cmd(command)
        elif index == 1:
            command = self.cmd.CUSTOM_ACTION + str("11") + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.ARM_CALIBRATION_POINT + str("1") + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.AXIS_X_ACTION + str(self.calibrated_axis[self.radioButton_axis_flag][0] + self.original_axis[1][0]) + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.AXIS_Y_ACTION + str(self.calibrated_axis[self.radioButton_axis_flag][1] + self.original_axis[1][1]) + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.AXIS_Z_ACTION + str(self.calibrated_axis[self.radioButton_axis_flag][2] + self.original_axis[1][2])
            if self.radioButton_Parameter_Point_1.isChecked() == True:
                self.send_cmd(command)
        elif index == 2:
            command = self.cmd.CUSTOM_ACTION + str("11") + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.ARM_CALIBRATION_POINT + str("2") + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.AXIS_X_ACTION + str(self.calibrated_axis[self.radioButton_axis_flag][0] + self.original_axis[2][0]) + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.AXIS_Y_ACTION + str(self.calibrated_axis[self.radioButton_axis_flag][1] + self.original_axis[2][1]) + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.AXIS_Z_ACTION + str(self.calibrated_axis[self.radioButton_axis_flag][2] + self.original_axis[2][2])
            if self.radioButton_Parameter_Point_2.isChecked() == True:
                self.send_cmd(command)
        elif index == 3:
            command = self.cmd.CUSTOM_ACTION + str("11") + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.ARM_CALIBRATION_POINT + str("3") + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.AXIS_X_ACTION + str(self.calibrated_axis[self.radioButton_axis_flag][0] + self.original_axis[3][0]) + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.AXIS_Y_ACTION + str(self.calibrated_axis[self.radioButton_axis_flag][1] + self.original_axis[3][1]) + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.AXIS_Z_ACTION + str(self.calibrated_axis[self.radioButton_axis_flag][2] + self.original_axis[3][2])
            if self.radioButton_Parameter_Point_3.isChecked() == True:
                self.send_cmd(command)
        elif index == 4:
            command = self.cmd.CUSTOM_ACTION + str("11") + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.ARM_CALIBRATION_POINT + str("4") + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.AXIS_X_ACTION + str(self.calibrated_axis[self.radioButton_axis_flag][0] + self.original_axis[4][0]) + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.AXIS_Y_ACTION + str(self.calibrated_axis[self.radioButton_axis_flag][1] + self.original_axis[4][1]) + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.AXIS_Z_ACTION + str(self.calibrated_axis[self.radioButton_axis_flag][2] + self.original_axis[4][2])
            if self.radioButton_Parameter_Point_4.isChecked() == True:
                self.send_cmd(command)

        elif index == 5:
            command = self.cmd.CUSTOM_ACTION + str("11") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_CALIBRATION_START + str("0")
            if self.radioButton_Parameter_Point_0.isChecked()==True:
                self.send_cmd(command)
        elif index == 6:
            command = self.cmd.CUSTOM_ACTION + str("11") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_CALIBRATION_START + str("1")
            if self.radioButton_Parameter_Point_1.isChecked()==True:
                self.send_cmd(command)
        elif index == 7:
            command = self.cmd.CUSTOM_ACTION + str("11") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_CALIBRATION_START + str("2")
            if self.radioButton_Parameter_Point_2.isChecked()==True:
                self.send_cmd(command)
        elif index == 8:
            command = self.cmd.CUSTOM_ACTION + str("11") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_CALIBRATION_START + str("3")
            if self.radioButton_Parameter_Point_3.isChecked()==True:
                self.send_cmd(command)
        elif index == 9:
            command = self.cmd.CUSTOM_ACTION + str("11") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_CALIBRATION_START + str("4")
            if self.radioButton_Parameter_Point_4.isChecked()==True:
                self.send_cmd(command)

        elif index == 10:
            command = self.cmd.CUSTOM_ACTION + str("11") + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.ARM_CALIBRATION_END + str("0") + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.AXIS_X_ACTION + str(self.calibrated_axis[self.radioButton_axis_flag][0] + self.original_axis[0][0]) + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.AXIS_Y_ACTION + str(self.calibrated_axis[self.radioButton_axis_flag][1] + self.original_axis[0][1]) + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.AXIS_Z_ACTION + str(self.calibrated_axis[self.radioButton_axis_flag][2] + self.original_axis[0][2])
            if self.radioButton_Parameter_Point_0.isChecked()==True:
                self.send_cmd(command)
        elif index == 11:
            command = self.cmd.CUSTOM_ACTION + str("11") + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.ARM_CALIBRATION_END + str("1") + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.AXIS_X_ACTION + str(self.calibrated_axis[self.radioButton_axis_flag][0] + self.original_axis[1][0]) + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.AXIS_Y_ACTION + str(self.calibrated_axis[self.radioButton_axis_flag][1] + self.original_axis[1][1]) + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.AXIS_Z_ACTION + str(self.calibrated_axis[self.radioButton_axis_flag][2] + self.original_axis[1][2])
            if self.radioButton_Parameter_Point_1.isChecked()==True:
                self.send_cmd(command)
        elif index == 12:
            command = self.cmd.CUSTOM_ACTION + str("11") + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.ARM_CALIBRATION_END + str("2") + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.AXIS_X_ACTION + str(self.calibrated_axis[self.radioButton_axis_flag][0] + self.original_axis[2][0]) + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.AXIS_Y_ACTION + str(self.calibrated_axis[self.radioButton_axis_flag][1] + self.original_axis[2][1]) + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.AXIS_Z_ACTION + str(self.calibrated_axis[self.radioButton_axis_flag][2] + self.original_axis[2][2])
            if self.radioButton_Parameter_Point_2.isChecked()==True:
                self.send_cmd(command)
        elif index == 13:
            command = self.cmd.CUSTOM_ACTION + str("11") + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.ARM_CALIBRATION_END + str("3") + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.AXIS_X_ACTION + str(self.calibrated_axis[self.radioButton_axis_flag][0] + self.original_axis[3][0]) + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.AXIS_Y_ACTION + str(self.calibrated_axis[self.radioButton_axis_flag][1] + self.original_axis[3][1]) + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.AXIS_Z_ACTION + str(self.calibrated_axis[self.radioButton_axis_flag][2] + self.original_axis[3][2])
            if self.radioButton_Parameter_Point_3.isChecked()==True:
                self.send_cmd(command)
        elif index == 14:
            command = self.cmd.CUSTOM_ACTION + str("11") + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.ARM_CALIBRATION_END + str("4") + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.AXIS_X_ACTION + str(self.calibrated_axis[self.radioButton_axis_flag][0] + self.original_axis[4][0]) + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.AXIS_Y_ACTION + str(self.calibrated_axis[self.radioButton_axis_flag][1] + self.original_axis[4][1]) + self.cmd.DECOLLATOR_CHAR \
                      + self.cmd.AXIS_Z_ACTION + str(self.calibrated_axis[self.radioButton_axis_flag][2] + self.original_axis[4][2])
            if self.radioButton_Parameter_Point_4.isChecked()==True:
                self.send_cmd(command)

    # 第三组框参数设置
    def set_third_groupbox(self, index):
        if index.objectName() == "radioButton_Parameter_Point_0":
            if index.isChecked() == True:
                self.radioButton_axis_flag = 0
            else:
                self.radioButton_axis_flag = -1
            self.send_calibrated_command(5)
        elif index.objectName() == "radioButton_Parameter_Point_1":
            if index.isChecked() == True:
                self.radioButton_axis_flag = 1
            else:
                self.radioButton_axis_flag = -1
            self.send_calibrated_command(6)
        elif index.objectName() == "radioButton_Parameter_Point_2":
            if index.isChecked() == True:
                self.radioButton_axis_flag = 2
            else:
                self.radioButton_axis_flag = -1
            self.send_calibrated_command(7)
        elif index.objectName() == "radioButton_Parameter_Point_3":
            if index.isChecked() == True:
                self.radioButton_axis_flag = 3
            else:
                self.radioButton_axis_flag = -1
            self.send_calibrated_command(8)
        elif index.objectName() == "radioButton_Parameter_Point_4":
            if index.isChecked() == True:
                self.radioButton_axis_flag = 4
            else:
                self.radioButton_axis_flag = -1
            self.send_calibrated_command(9)

        elif index.objectName() == "pushButton_Parameter_Axis_X_Subtract":
            if self.radioButton_axis_flag != -1:
                self.calibrated_axis[self.radioButton_axis_flag][0] = round(self.calibrated_axis[self.radioButton_axis_flag][0] - 1, 1)
                self.lineEdit_Parameter_Axis[self.radioButton_axis_flag][0].setText(str(self.calibrated_axis[self.radioButton_axis_flag][0]))
                self.send_calibrated_command(self.radioButton_axis_flag)
        elif index.objectName() == "pushButton_Parameter_Axis_Y_Subtract":
            if self.radioButton_axis_flag != -1:
                self.calibrated_axis[self.radioButton_axis_flag][1] = round(self.calibrated_axis[self.radioButton_axis_flag][1] - 1, 1)
                self.lineEdit_Parameter_Axis[self.radioButton_axis_flag][1].setText(str(self.calibrated_axis[self.radioButton_axis_flag][1]))
                self.send_calibrated_command(self.radioButton_axis_flag)
        elif index.objectName() == "pushButton_Parameter_Axis_Z_Subtract":
            if self.radioButton_axis_flag != -1:
                self.calibrated_axis[self.radioButton_axis_flag][2] = round(self.calibrated_axis[self.radioButton_axis_flag][2] - 1, 1)
                self.lineEdit_Parameter_Axis[self.radioButton_axis_flag][2].setText(str(self.calibrated_axis[self.radioButton_axis_flag][2]))
                self.send_calibrated_command(self.radioButton_axis_flag)
        elif index.objectName() == "pushButton_Parameter_Axis_X_Add":
            if self.radioButton_axis_flag != -1:
                self.calibrated_axis[self.radioButton_axis_flag][0] = round(self.calibrated_axis[self.radioButton_axis_flag][0] + 1, 1)
                self.lineEdit_Parameter_Axis[self.radioButton_axis_flag][0].setText(str(self.calibrated_axis[self.radioButton_axis_flag][0]))
                self.send_calibrated_command(self.radioButton_axis_flag)
        elif index.objectName() == "pushButton_Parameter_Axis_Y_Add":
            if self.radioButton_axis_flag != -1:
                self.calibrated_axis[self.radioButton_axis_flag][1] = round(self.calibrated_axis[self.radioButton_axis_flag][1] + 1, 1)
                self.lineEdit_Parameter_Axis[self.radioButton_axis_flag][1].setText(str(self.calibrated_axis[self.radioButton_axis_flag][1]))
                self.send_calibrated_command(self.radioButton_axis_flag)
        elif index.objectName() == "pushButton_Parameter_Axis_Z_Add":
            if self.radioButton_axis_flag != -1:
                self.calibrated_axis[self.radioButton_axis_flag][2] = round(self.calibrated_axis[self.radioButton_axis_flag][2] + 1, 1)
                self.lineEdit_Parameter_Axis[self.radioButton_axis_flag][2].setText(str(self.calibrated_axis[self.radioButton_axis_flag][2]))
                self.send_calibrated_command(self.radioButton_axis_flag)

        elif index.objectName() == "pushButton_Parameter_Axis_Save":
            if self.radioButton_axis_flag == 0:
                self.send_calibrated_command(10)
                self.radioButton_Parameter_Point_0.setChecked(False)
            elif self.radioButton_axis_flag == 1:
                self.send_calibrated_command(11)
                self.radioButton_Parameter_Point_1.setChecked(False)
            elif self.radioButton_axis_flag == 2:
                self.send_calibrated_command(12)
                self.radioButton_Parameter_Point_2.setChecked(False)
            elif self.radioButton_axis_flag == 3:
                self.send_calibrated_command(13)
                self.radioButton_Parameter_Point_3.setChecked(False)
            elif self.radioButton_axis_flag == 4:
                self.send_calibrated_command(14)
                self.radioButton_Parameter_Point_4.setChecked(False)
            else:
                pass
            self.radioButton_axis_flag = -1
            self.set_radioButton_color(0)

    # 第四组框参数设置
    def set_fourth_groupbox(self, index):
        if index.objectName() == "horizontalSlider_Parameter_Arm_Frequency":
            data = self.horizontalSlider_Parameter_Arm_Frequency.value() * 50
            self.lineEdit_Parameter_Arm_Frequency.setText(str(data))
            command = self.cmd.CUSTOM_ACTION + str("6") + self.cmd.DECOLLATOR_CHAR + self.cmd.ARM_FREQUENCY + str(data)
            self.send_cmd(command)
        elif index.objectName() == "pushButton_Parameter_Arm_Frequency_Subtract":
            data = self.horizontalSlider_Parameter_Arm_Frequency.value() - 1
            if data < 1:
                data = 1
            self.horizontalSlider_Parameter_Arm_Frequency.setValue(data)
            self.lineEdit_Parameter_Arm_Frequency.setText(str(data * 50))
        elif index.objectName() == "pushButton_Parameter_Arm_Frequency_Add":
            data = self.horizontalSlider_Parameter_Arm_Frequency.value() + 1
            if data > 320:
                data = 320
            self.horizontalSlider_Parameter_Arm_Frequency.setValue(data)
            self.lineEdit_Parameter_Arm_Frequency.setText(str(data * 50))

    #将指令通过信号通道发送出去
    def send_cmd(self, cmd):
        self.send_cmd_channel.emit(cmd)

    #将坐标更新到主界面
    def update_main_default_position(self):
        axis = [str(self.position_axis[0]), str(self.position_axis[1]), str(self.position_axis[2]), str("0")]
        coordinate_str = f"{axis[0]},{axis[1]},{axis[2]},{axis[3]}"
        self.position_axis_channel.emit(coordinate_str)

    # 窗口关闭事件
    def closeEvent(self, event):
        self.save_configuration_ui()
        axis = [str(self.position_axis[0]), str(self.position_axis[1]), str(self.position_axis[2]), str("1")]
        coordinate_str = f"{axis[0]},{axis[1]},{axis[2]},{axis[3]}"
        self.position_axis_channel.emit(coordinate_str)
        event.accept()

def print_cmd(cmd):
    print("cmd:" + cmd)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #s.connect(("192.168.1.80", 5000))
    #calibrationWindow = Configuration(s)

    calibrationWindow = Configuration()
    calibrationWindow.setWindowModality(Qt.ApplicationModal)
    calibrationWindow.show()
    calibrationWindow.send_cmd_channel.connect(print_cmd)
    sys.exit(app.exec_())
