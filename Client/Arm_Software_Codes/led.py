import sys
from PyQt5.QtCore import *
import numpy as np
from PyQt5.QtGui import *
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from command import Command
from ui.ui_led import Ui_Led

class ColorDialog(QtWidgets.QColorDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setOptions(self.options() | QtWidgets.QColorDialog.DontUseNativeDialog)
        for children in self.findChildren(QtWidgets.QWidget):
            classname = children.metaObject().className()
            if classname not in ("QColorPicker", "QColorLuminancePicker"):
                children.hide()


class LED(QtWidgets.QWidget, Ui_Led):
    signal_channel = QtCore.pyqtSignal(str)
    send_cmd_channel = QtCore.pyqtSignal(str)

    def __init__(self):
        super(LED, self).__init__()
        self.colordialog = ColorDialog()
        self.setupUi(self)
        self.setFixedSize(408, 275)
        self.setWindowIcon(QIcon('./picture/Freenove.ico'))  
        self.cmd = Command()
        self.led_mode = 0
        self.led_brightness = 255
        self.ws2812_count = 8
        lineEdit_limit_validator = QRegExpValidator(QRegExp('^?([0,1]?\d?\d|2[0-4]\d|25[0-5])$'))  # 0-255
        self.lineEdit_Led_Color_R.setValidator(lineEdit_limit_validator)
        self.lineEdit_Led_Color_G.setValidator(lineEdit_limit_validator)
        self.lineEdit_Led_Color_B.setValidator(lineEdit_limit_validator)
        self.lineEdit_Led_Brightness.setValidator(lineEdit_limit_validator)
        r = int(self.lineEdit_Led_Color_R.text())
        g = int(self.lineEdit_Led_Color_G.text())
        b = int(self.lineEdit_Led_Color_B.text())
        self.color = [r, g, b]
        self.connect()
        self.led_brightness = self.verticalSlider_Led_Brightness.value()
        self.rgb255_brightness_transition()

    def connect(self):
        self.verticalSlider_Led_Brightness.valueChanged.connect(self.Led_Brightnessness_Show)
        self.radioButton_Led_Mode_Off.clicked.connect(lambda: self.Led_Mode_Select(self.radioButton_Led_Mode_Off))
        self.radioButton_Led_Mode_RGB.clicked.connect(lambda: self.Led_Mode_Select(self.radioButton_Led_Mode_RGB))
        self.radioButton_Led_Mode_Following.clicked.connect(lambda: self.Led_Mode_Select(self.radioButton_Led_Mode_Following))
        self.radioButton_Led_Mode_Blink.clicked.connect(lambda: self.Led_Mode_Select(self.radioButton_Led_Mode_Blink))
        self.radioButton_Led_Mode_Breathing.clicked.connect(lambda: self.Led_Mode_Select(self.radioButton_Led_Mode_Breathing))
        self.radioButton_Led_Mode_Rainbow.clicked.connect(lambda: self.Led_Mode_Select(self.radioButton_Led_Mode_Rainbow))
        self.radioButton_Led_Mode_Gradient.clicked.connect(lambda: self.Led_Mode_Select(self.radioButton_Led_Mode_Gradient))
        self.lineEdit_Led_Color_R.textChanged.connect(self.LineEdit_Led_Text_Change)
        self.lineEdit_Led_Color_G.textChanged.connect(self.LineEdit_Led_Text_Change)
        self.lineEdit_Led_Color_B.textChanged.connect(self.LineEdit_Led_Text_Change)
        self.lineEdit_Led_Brightness.textChanged.connect(self.LineEdit_Led_Text_Change)
        self.colordialog.currentColorChanged.connect(self.led_color_disk_show)
        lay = QtWidgets.QVBoxLayout(self.widget_Led_Color_Disk)
        lay.addWidget(self.colordialog, alignment=Qt.AlignCenter)

    def send_cmd(self, cmd):
        self.send_cmd_channel.emit(cmd)

    @staticmethod
    def rgbhex_to_rgb255(rgbhex: str) -> np.array:
        if rgbhex[0] == '#':
            rgbhex = rgbhex[1:]
        r = int(rgbhex[0:2], 16)
        g = int(rgbhex[2:4], 16)
        b = int(rgbhex[4:6], 16)
        return np.array((r, g, b))

    def rgb255_brightness_transition(self):
        r = int(self.led_brightness * self.color[0] / 255)
        g = int(self.led_brightness * self.color[1] / 255)
        b = int(self.led_brightness * self.color[2] / 255)
        label_Led_Color_Disk_Show = 'QLabel {background-color: rgb(' + str(r) + ',' + str(g) + ',' + str(b) + ');}'
        self.label_Led_Color_Disk.setStyleSheet(str(label_Led_Color_Disk_Show))
        self.lineEdit_Led_Color_R.setText(str(r))
        self.lineEdit_Led_Color_G.setText(str(g))
        self.lineEdit_Led_Color_B.setText(str(b))
        return r, g, b

    def led_color_disk_show(self, color):
        self.color = self.rgbhex_to_rgb255(color.name())
        r, g, b = self.rgb255_brightness_transition()
        command = self.cmd.CUSTOM_ACTION + str("1") + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.WS2812_MODE + str(self.led_mode) + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.WS2812_RED + str(r) + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.WS2812_GREEN + str(g) + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.WS2812_BLUE + str(b)
        if (self.led_mode == 0) or (self.led_mode == 5) or (self.led_mode == 6):
            pass
        else:
            self.send_cmd(command)

    def Led_Brightnessness_Show(self):
        self.led_brightness = self.verticalSlider_Led_Brightness.value()
        self.lineEdit_Led_Brightness.setText(str(self.led_brightness))
        r, g, b = self.rgb255_brightness_transition()
        command = self.cmd.CUSTOM_ACTION + str("1") + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.WS2812_MODE + str(self.led_mode) + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.WS2812_RED + str(r) + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.WS2812_GREEN + str(g) + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.WS2812_BLUE + str(b)
        if (self.led_mode == 0) or (self.led_mode == 5) or (self.led_mode == 6):
            pass
        else:
            self.send_cmd(command)

    def Led_Mode_Select(self, parameter):
        if parameter.objectName() == 'radioButton_Led_Mode_Off':
            self.led_mode = 0
            self.radioButton_Led_Mode_RGB.setChecked(False)
            self.radioButton_Led_Mode_Following.setChecked(False)
            self.radioButton_Led_Mode_Blink.setChecked(False)
            self.radioButton_Led_Mode_Breathing.setChecked(False)
            self.radioButton_Led_Mode_Rainbow.setChecked(False)
            self.radioButton_Led_Mode_Gradient.setChecked(False)
        elif parameter.objectName() == 'radioButton_Led_Mode_RGB':
            if self.radioButton_Led_Mode_RGB.isChecked():
                self.led_mode = 1
            elif not self.radioButton_Led_Mode_RGB.isChecked():
                self.led_mode = 0
            self.radioButton_Led_Mode_Off.setChecked(False)
            self.radioButton_Led_Mode_Following.setChecked(False)
            self.radioButton_Led_Mode_Blink.setChecked(False)
            self.radioButton_Led_Mode_Breathing.setChecked(False)
            self.radioButton_Led_Mode_Rainbow.setChecked(False)
            self.radioButton_Led_Mode_Gradient.setChecked(False)
        elif parameter.objectName() == 'radioButton_Led_Mode_Following':
            if self.radioButton_Led_Mode_Following.isChecked():
                self.led_mode = 2
            elif not self.radioButton_Led_Mode_Following.isChecked():
                self.led_mode = 0
            self.radioButton_Led_Mode_Off.setChecked(False)
            self.radioButton_Led_Mode_RGB.setChecked(False)
            self.radioButton_Led_Mode_Blink.setChecked(False)
            self.radioButton_Led_Mode_Breathing.setChecked(False)
            self.radioButton_Led_Mode_Rainbow.setChecked(False)
            self.radioButton_Led_Mode_Gradient.setChecked(False)
        elif parameter.objectName() == 'radioButton_Led_Mode_Blink':
            if self.radioButton_Led_Mode_Blink.isChecked():
                self.led_mode = 3
            elif not self.radioButton_Led_Mode_Blink.isChecked():
                self.led_mode = 0
            self.radioButton_Led_Mode_Off.setChecked(False)
            self.radioButton_Led_Mode_RGB.setChecked(False)
            self.radioButton_Led_Mode_Following.setChecked(False)
            self.radioButton_Led_Mode_Breathing.setChecked(False)
            self.radioButton_Led_Mode_Rainbow.setChecked(False)
            self.radioButton_Led_Mode_Gradient.setChecked(False)
        elif parameter.objectName() == 'radioButton_Led_Mode_Breathing':
            if self.radioButton_Led_Mode_Breathing.isChecked():
                self.led_mode = 4
            elif not self.radioButton_Led_Mode_Breathing.isChecked():
                self.led_mode = 0
            self.radioButton_Led_Mode_Off.setChecked(False)
            self.radioButton_Led_Mode_RGB.setChecked(False)
            self.radioButton_Led_Mode_Following.setChecked(False)
            self.radioButton_Led_Mode_Blink.setChecked(False)
            self.radioButton_Led_Mode_Rainbow.setChecked(False)
            self.radioButton_Led_Mode_Gradient.setChecked(False)
        elif parameter.objectName() == 'radioButton_Led_Mode_Rainbow':
            if self.radioButton_Led_Mode_Rainbow.isChecked():
                self.led_mode = 5
            elif not self.radioButton_Led_Mode_Rainbow.isChecked():
                self.led_mode = 0
            self.radioButton_Led_Mode_Off.setChecked(False)
            self.radioButton_Led_Mode_RGB.setChecked(False)
            self.radioButton_Led_Mode_Following.setChecked(False)
            self.radioButton_Led_Mode_Blink.setChecked(False)
            self.radioButton_Led_Mode_Breathing.setChecked(False)
            self.radioButton_Led_Mode_Gradient.setChecked(False)
        elif parameter.objectName() == 'radioButton_Led_Mode_Gradient':
            if self.radioButton_Led_Mode_Gradient.isChecked():
                self.led_mode = 6
            elif not self.radioButton_Led_Mode_Gradient.isChecked():
                self.led_mode = 0
            self.radioButton_Led_Mode_Off.setChecked(False)
            self.radioButton_Led_Mode_RGB.setChecked(False)
            self.radioButton_Led_Mode_Following.setChecked(False)
            self.radioButton_Led_Mode_Blink.setChecked(False)
            self.radioButton_Led_Mode_Breathing.setChecked(False)
            self.radioButton_Led_Mode_Rainbow.setChecked(False)
        r, g, b = self.rgb255_brightness_transition()
        command = self.cmd.CUSTOM_ACTION + str("1") + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.WS2812_MODE + str(self.led_mode) + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.WS2812_RED + str(r) + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.WS2812_GREEN + str(g) + self.cmd.DECOLLATOR_CHAR \
            + self.cmd.WS2812_BLUE + str(b)
        self.send_cmd(command)

    def LineEdit_Led_Text_Change(self):
        try:
            bright = int(self.lineEdit_Led_Brightness.text())
            r1 = int(self.lineEdit_Led_Color_R.text())
            g1 = int(self.lineEdit_Led_Color_G.text())
            b1 = int(self.lineEdit_Led_Color_B.text())
            r2 = int(bright * r1 / 255)
            g2 = int(bright * g1 / 255)
            b2 = int(bright * b1 / 255)
            label_Led_Color_Disk_Show = 'QLabel {background-color: rgb(' + str(r2) + ',' + str(g2) + ',' + str(b2) + ');}'
            self.label_Led_Color_Disk.setStyleSheet(str(label_Led_Color_Disk_Show))
        except:
            pass

    def Update_Lineedit_Color(self):
        try:
            self.color[0] = int(self.lineEdit_Led_Color_R.text())
            self.color[1] = int(self.lineEdit_Led_Color_G.text())
            self.color[2] = int(self.lineEdit_Led_Color_B.text())
        except:
            pass

    def set_ws2812_count(self, index):
        if index.objectName() == "pushButton_Led_Count_Subtract":
            self.ws2812_count = int(self.lineEdit_Led_Count_Value.text()) - 1
        elif index.objectName() == "pushButton_Led_Count_Add":
            self.ws2812_count = int(self.lineEdit_Led_Count_Value.text()) + 1
        if self.ws2812_count < 1:
            self.ws2812_count = 1
        elif self.ws2812_count > 255:
            self.ws2812_count = 255
        self.lineEdit_Led_Count_Value.setText(str(self.ws2812_count))

    def closeEvent(self, event):
        self.signal_channel.emit("close led ui.")
        event.accept()


def print_cmd(cmd):
    print("cmd:" + cmd)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    led = LED()
    led.setWindowModality(Qt.ApplicationModal)
    led.show()
    led.send_cmd_channel.connect(print_cmd)

    sys.exit(app.exec_())
