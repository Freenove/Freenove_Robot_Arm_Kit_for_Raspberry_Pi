# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_arm.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Arm(object):
    def setupUi(self, Arm):
        Arm.setObjectName("Arm")
        Arm.setWindowModality(QtCore.Qt.WindowModal)
        Arm.setEnabled(True)
        Arm.resize(1074, 617)
        font = QtGui.QFont()
        font.setFamily("3ds")
        Arm.setFont(font)
        Arm.setFocusPolicy(QtCore.Qt.StrongFocus)
        Arm.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        Arm.setLayoutDirection(QtCore.Qt.LeftToRight)
        Arm.setAutoFillBackground(False)
        Arm.setStyleSheet("QWidget{\n"
"background:#484848;\n"
"}\n"
"QAbstractButton{\n"
"border-style:0px;\n"
"border-radius:0px;\n"
"color:#DCDCDC;\n"
"background:qlineargradient(spread:pad,x1:0,y1:0,x2:0,y2:1,stop:0 #858585,stop:1 #383838);\n"
"}\n"
"QAbstractButton:hover{\n"
"color:#000000;\n"
"background-color:#008aff;\n"
"}\n"
"QAbstractButton:pressed{\n"
"color:#DCDCDC;\n"
"border-style:solid;\n"
"border-width:0px 0px 0px 4px;\n"
"border-color:#008aff;\n"
"background-color:#444444;\n"
"}\n"
"QLabel{\n"
"color:#DCDCDC;\n"
"}\n"
"QLabel:focus{\n"
"border:1px solid #00BB9E;\n"
"}\n"
"QLineEdit{\n"
"border:1px solid #242424;\n"
"border-radius:3px;\n"
"background:none;\n"
"selection-background-color:#484848;\n"
"selection-color:#DCDCDC;\n"
"}\n"
"QLineEdit:focus,QLineEdit:hover{\n"
"border:1px solid #242424;\n"
"}\n"
"QLineEdit{\n"
"border:1px solid #242424;\n"
"border-radius:3px;\n"
"background:none;\n"
"selection-background-color:#484848;\n"
"selection-color:#DCDCDC;\n"
"}\n"
"QLineEdit:focus,QLineEdit:hover{\n"
"border:1px solid #242424;\n"
"}\n"
"QLineEdit{\n"
"lineedit-password-character:9679;\n"
"}\n"
"\n"
"QSlider::sub-page:horizontal{\n"
"height:8px;\n"
"border-radius:3px;\n"
"background:#008aff;\n"
"}\n"
"QSlider::groove:vertical,QSlider::sub-page:vertical{\n"
"width:3px;\n"
"border-radius:3px;\n"
"background:#18181a;\n"
"}\n"
"QSlider::add-page:vertical{\n"
"width:8px;\n"
"border-radius:3px;\n"
"background:#008aff;\n"
"}\n"
"QGroupBox::title {\n"
"color:white;\n"
"subcontrol-position: top center;} ")
        Arm.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.label_Arm_Video = QtWidgets.QLabel(Arm)
        self.label_Arm_Video.setEnabled(True)
        self.label_Arm_Video.setGeometry(QtCore.QRect(10, 10, 600, 300))
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.label_Arm_Video.setFont(font)
        self.label_Arm_Video.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.label_Arm_Video.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.label_Arm_Video.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label_Arm_Video.setLineWidth(0)
        self.label_Arm_Video.setMidLineWidth(0)
        self.label_Arm_Video.setText("")
        self.label_Arm_Video.setTextFormat(QtCore.Qt.AutoText)
        self.label_Arm_Video.setScaledContents(True)
        self.label_Arm_Video.setAlignment(QtCore.Qt.AlignCenter)
        self.label_Arm_Video.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse)
        self.label_Arm_Video.setObjectName("label_Arm_Video")
        self.textEdit_Arm_Gcode_Area = QtWidgets.QTextEdit(Arm)
        self.textEdit_Arm_Gcode_Area.setEnabled(True)
        self.textEdit_Arm_Gcode_Area.setGeometry(QtCore.QRect(740, 20, 321, 301))
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.textEdit_Arm_Gcode_Area.setFont(font)
        self.textEdit_Arm_Gcode_Area.setMouseTracking(False)
        self.textEdit_Arm_Gcode_Area.setFocusPolicy(QtCore.Qt.NoFocus)
        self.textEdit_Arm_Gcode_Area.setAutoFillBackground(True)
        self.textEdit_Arm_Gcode_Area.setStyleSheet("color: rgb(255, 255, 255);")
        self.textEdit_Arm_Gcode_Area.setFrameShape(QtWidgets.QFrame.Box)
        self.textEdit_Arm_Gcode_Area.setFrameShadow(QtWidgets.QFrame.Plain)
        self.textEdit_Arm_Gcode_Area.setReadOnly(True)
        self.textEdit_Arm_Gcode_Area.setObjectName("textEdit_Arm_Gcode_Area")
        self.groupBox_Arm_Axis = QtWidgets.QGroupBox(Arm)
        self.groupBox_Arm_Axis.setGeometry(QtCore.QRect(10, 430, 601, 181))
        self.groupBox_Arm_Axis.setMouseTracking(False)
        self.groupBox_Arm_Axis.setTabletTracking(False)
        self.groupBox_Arm_Axis.setAutoFillBackground(False)
        self.groupBox_Arm_Axis.setObjectName("groupBox_Arm_Axis")
        self.pushButton_Arm_Axis_Z_Add = QtWidgets.QPushButton(self.groupBox_Arm_Axis)
        self.pushButton_Arm_Axis_Z_Add.setGeometry(QtCore.QRect(180, 30, 75, 23))
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.pushButton_Arm_Axis_Z_Add.setFont(font)
        self.pushButton_Arm_Axis_Z_Add.setAutoRepeat(True)
        self.pushButton_Arm_Axis_Z_Add.setAutoRepeatDelay(500)
        self.pushButton_Arm_Axis_Z_Add.setObjectName("pushButton_Arm_Axis_Z_Add")
        self.pushButton_Arm_Axis_Y_Subtract = QtWidgets.QPushButton(self.groupBox_Arm_Axis)
        self.pushButton_Arm_Axis_Y_Subtract.setGeometry(QtCore.QRect(100, 110, 75, 23))
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.pushButton_Arm_Axis_Y_Subtract.setFont(font)
        self.pushButton_Arm_Axis_Y_Subtract.setAutoRepeat(True)
        self.pushButton_Arm_Axis_Y_Subtract.setAutoRepeatDelay(500)
        self.pushButton_Arm_Axis_Y_Subtract.setObjectName("pushButton_Arm_Axis_Y_Subtract")
        self.pushButton_Arm_Axis_X_Subtract = QtWidgets.QPushButton(self.groupBox_Arm_Axis)
        self.pushButton_Arm_Axis_X_Subtract.setGeometry(QtCore.QRect(20, 70, 75, 23))
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.pushButton_Arm_Axis_X_Subtract.setFont(font)
        self.pushButton_Arm_Axis_X_Subtract.setAutoRepeat(True)
        self.pushButton_Arm_Axis_X_Subtract.setAutoRepeatDelay(500)
        self.pushButton_Arm_Axis_X_Subtract.setObjectName("pushButton_Arm_Axis_X_Subtract")
        self.pushButton_Arm_Axis_Z_Subtract = QtWidgets.QPushButton(self.groupBox_Arm_Axis)
        self.pushButton_Arm_Axis_Z_Subtract.setGeometry(QtCore.QRect(180, 110, 75, 23))
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.pushButton_Arm_Axis_Z_Subtract.setFont(font)
        self.pushButton_Arm_Axis_Z_Subtract.setAutoRepeat(True)
        self.pushButton_Arm_Axis_Z_Subtract.setAutoRepeatDelay(500)
        self.pushButton_Arm_Axis_Z_Subtract.setObjectName("pushButton_Arm_Axis_Z_Subtract")
        self.pushButton_Arm_Axis_Y_Add = QtWidgets.QPushButton(self.groupBox_Arm_Axis)
        self.pushButton_Arm_Axis_Y_Add.setGeometry(QtCore.QRect(100, 30, 75, 23))
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.pushButton_Arm_Axis_Y_Add.setFont(font)
        self.pushButton_Arm_Axis_Y_Add.setAutoRepeat(True)
        self.pushButton_Arm_Axis_Y_Add.setAutoRepeatDelay(500)
        self.pushButton_Arm_Axis_Y_Add.setObjectName("pushButton_Arm_Axis_Y_Add")
        self.pushButton_Arm_Axis_X_Add = QtWidgets.QPushButton(self.groupBox_Arm_Axis)
        self.pushButton_Arm_Axis_X_Add.setGeometry(QtCore.QRect(180, 70, 75, 23))
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.pushButton_Arm_Axis_X_Add.setFont(font)
        self.pushButton_Arm_Axis_X_Add.setAutoRepeat(True)
        self.pushButton_Arm_Axis_X_Add.setAutoRepeatDelay(500)
        self.pushButton_Arm_Axis_X_Add.setObjectName("pushButton_Arm_Axis_X_Add")
        self.pushButton_Arm_Record_Command = QtWidgets.QPushButton(self.groupBox_Arm_Axis)
        self.pushButton_Arm_Record_Command.setGeometry(QtCore.QRect(290, 30, 91, 22))
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.pushButton_Arm_Record_Command.setFont(font)
        self.pushButton_Arm_Record_Command.setObjectName("pushButton_Arm_Record_Command")
        self.textEdit_Arm_Record_Area = QtWidgets.QTextEdit(self.groupBox_Arm_Axis)
        self.textEdit_Arm_Record_Area.setEnabled(True)
        self.textEdit_Arm_Record_Area.setGeometry(QtCore.QRect(410, 27, 181, 141))
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.textEdit_Arm_Record_Area.setFont(font)
        self.textEdit_Arm_Record_Area.setMouseTracking(False)
        self.textEdit_Arm_Record_Area.setFocusPolicy(QtCore.Qt.NoFocus)
        self.textEdit_Arm_Record_Area.setAutoFillBackground(True)
        self.textEdit_Arm_Record_Area.setStyleSheet("color: rgb(255, 255, 255);")
        self.textEdit_Arm_Record_Area.setFrameShape(QtWidgets.QFrame.Box)
        self.textEdit_Arm_Record_Area.setFrameShadow(QtWidgets.QFrame.Plain)
        self.textEdit_Arm_Record_Area.setReadOnly(True)
        self.textEdit_Arm_Record_Area.setObjectName("textEdit_Arm_Record_Area")
        self.pushButton_Arm_Withdraw_Command = QtWidgets.QPushButton(self.groupBox_Arm_Axis)
        self.pushButton_Arm_Withdraw_Command.setGeometry(QtCore.QRect(290, 60, 91, 22))
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.pushButton_Arm_Withdraw_Command.setFont(font)
        self.pushButton_Arm_Withdraw_Command.setObjectName("pushButton_Arm_Withdraw_Command")
        self.pushButton_Arm_Execute_Record_Command = QtWidgets.QPushButton(self.groupBox_Arm_Axis)
        self.pushButton_Arm_Execute_Record_Command.setGeometry(QtCore.QRect(290, 90, 91, 22))
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.pushButton_Arm_Execute_Record_Command.setFont(font)
        self.pushButton_Arm_Execute_Record_Command.setObjectName("pushButton_Arm_Execute_Record_Command")
        self.pushButton_Arm_Save_Record_Command = QtWidgets.QPushButton(self.groupBox_Arm_Axis)
        self.pushButton_Arm_Save_Record_Command.setGeometry(QtCore.QRect(290, 150, 91, 22))
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.pushButton_Arm_Save_Record_Command.setFont(font)
        self.pushButton_Arm_Save_Record_Command.setObjectName("pushButton_Arm_Save_Record_Command")
        self.pushButton_Arm_Import_Record_Command = QtWidgets.QPushButton(self.groupBox_Arm_Axis)
        self.pushButton_Arm_Import_Record_Command.setGeometry(QtCore.QRect(290, 120, 91, 22))
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.pushButton_Arm_Import_Record_Command.setFont(font)
        self.pushButton_Arm_Import_Record_Command.setObjectName("pushButton_Arm_Import_Record_Command")
        self.pushButton_Arm_Axis_Switched = QtWidgets.QPushButton(self.groupBox_Arm_Axis)
        self.pushButton_Arm_Axis_Switched.setGeometry(QtCore.QRect(100, 70, 75, 23))
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.pushButton_Arm_Axis_Switched.setFont(font)
        self.pushButton_Arm_Axis_Switched.setObjectName("pushButton_Arm_Axis_Switched")
        self.pushButton_Arm_Zero_Point = QtWidgets.QPushButton(self.groupBox_Arm_Axis)
        self.pushButton_Arm_Zero_Point.setGeometry(QtCore.QRect(20, 150, 75, 23))
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.pushButton_Arm_Zero_Point.setFont(font)
        self.pushButton_Arm_Zero_Point.setAutoRepeat(True)
        self.pushButton_Arm_Zero_Point.setAutoRepeatDelay(500)
        self.pushButton_Arm_Zero_Point.setObjectName("pushButton_Arm_Zero_Point")
        self.pushButton_Arm_Position = QtWidgets.QPushButton(self.groupBox_Arm_Axis)
        self.pushButton_Arm_Position.setGeometry(QtCore.QRect(180, 150, 75, 23))
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.pushButton_Arm_Position.setFont(font)
        self.pushButton_Arm_Position.setAutoRepeat(True)
        self.pushButton_Arm_Position.setAutoRepeatDelay(500)
        self.pushButton_Arm_Position.setObjectName("pushButton_Arm_Position")
        self.pushButton_Arm_Home_Up = QtWidgets.QPushButton(self.groupBox_Arm_Axis)
        self.pushButton_Arm_Home_Up.setGeometry(QtCore.QRect(100, 150, 75, 23))
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.pushButton_Arm_Home_Up.setFont(font)
        self.pushButton_Arm_Home_Up.setAutoRepeat(True)
        self.pushButton_Arm_Home_Up.setAutoRepeatDelay(500)
        self.pushButton_Arm_Home_Up.setObjectName("pushButton_Arm_Home_Up")
        self.layoutWidget = QtWidgets.QWidget(Arm)
        self.layoutWidget.setGeometry(QtCore.QRect(630, 380, 431, 181))
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout_Arm_1 = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout_Arm_1.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_Arm_1.setObjectName("gridLayout_Arm_1")
        self.horizontalSlider_Arm_Pen_Height = QtWidgets.QSlider(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.horizontalSlider_Arm_Pen_Height.setFont(font)
        self.horizontalSlider_Arm_Pen_Height.setMinimum(5)
        self.horizontalSlider_Arm_Pen_Height.setMaximum(25)
        self.horizontalSlider_Arm_Pen_Height.setProperty("value", 15)
        self.horizontalSlider_Arm_Pen_Height.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_Arm_Pen_Height.setObjectName("horizontalSlider_Arm_Pen_Height")
        self.gridLayout_Arm_1.addWidget(self.horizontalSlider_Arm_Pen_Height, 3, 1, 1, 1)
        self.lineEdit_Arm_Threshold_Value = QtWidgets.QLineEdit(self.layoutWidget)
        self.lineEdit_Arm_Threshold_Value.setEnabled(True)
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.lineEdit_Arm_Threshold_Value.setFont(font)
        self.lineEdit_Arm_Threshold_Value.setFocusPolicy(QtCore.Qt.NoFocus)
        self.lineEdit_Arm_Threshold_Value.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_Arm_Threshold_Value.setReadOnly(True)
        self.lineEdit_Arm_Threshold_Value.setObjectName("lineEdit_Arm_Threshold_Value")
        self.gridLayout_Arm_1.addWidget(self.lineEdit_Arm_Threshold_Value, 0, 2, 1, 1)
        self.label_Arm_Pen_Up_Height = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.label_Arm_Pen_Up_Height.setFont(font)
        self.label_Arm_Pen_Up_Height.setFocusPolicy(QtCore.Qt.NoFocus)
        self.label_Arm_Pen_Up_Height.setFrameShape(QtWidgets.QFrame.Box)
        self.label_Arm_Pen_Up_Height.setAlignment(QtCore.Qt.AlignCenter)
        self.label_Arm_Pen_Up_Height.setObjectName("label_Arm_Pen_Up_Height")
        self.gridLayout_Arm_1.addWidget(self.label_Arm_Pen_Up_Height, 3, 0, 1, 1)
        self.lineEdit_Arm_Sharpen_Value = QtWidgets.QLineEdit(self.layoutWidget)
        self.lineEdit_Arm_Sharpen_Value.setEnabled(True)
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.lineEdit_Arm_Sharpen_Value.setFont(font)
        self.lineEdit_Arm_Sharpen_Value.setFocusPolicy(QtCore.Qt.NoFocus)
        self.lineEdit_Arm_Sharpen_Value.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_Arm_Sharpen_Value.setReadOnly(True)
        self.lineEdit_Arm_Sharpen_Value.setObjectName("lineEdit_Arm_Sharpen_Value")
        self.gridLayout_Arm_1.addWidget(self.lineEdit_Arm_Sharpen_Value, 2, 2, 1, 1)
        self.lineEdit_Arm_Gauss_Value = QtWidgets.QLineEdit(self.layoutWidget)
        self.lineEdit_Arm_Gauss_Value.setEnabled(True)
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.lineEdit_Arm_Gauss_Value.setFont(font)
        self.lineEdit_Arm_Gauss_Value.setFocusPolicy(QtCore.Qt.NoFocus)
        self.lineEdit_Arm_Gauss_Value.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_Arm_Gauss_Value.setReadOnly(True)
        self.lineEdit_Arm_Gauss_Value.setObjectName("lineEdit_Arm_Gauss_Value")
        self.gridLayout_Arm_1.addWidget(self.lineEdit_Arm_Gauss_Value, 1, 2, 1, 1)
        self.horizontalSlider_Arm_Threshold = QtWidgets.QSlider(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.horizontalSlider_Arm_Threshold.setFont(font)
        self.horizontalSlider_Arm_Threshold.setMaximum(255)
        self.horizontalSlider_Arm_Threshold.setProperty("value", 100)
        self.horizontalSlider_Arm_Threshold.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_Arm_Threshold.setObjectName("horizontalSlider_Arm_Threshold")
        self.gridLayout_Arm_1.addWidget(self.horizontalSlider_Arm_Threshold, 0, 1, 1, 1)
        self.horizontalSlider_Arm_Gauss = QtWidgets.QSlider(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.horizontalSlider_Arm_Gauss.setFont(font)
        self.horizontalSlider_Arm_Gauss.setMinimum(1)
        self.horizontalSlider_Arm_Gauss.setMaximum(9)
        self.horizontalSlider_Arm_Gauss.setSingleStep(2)
        self.horizontalSlider_Arm_Gauss.setPageStep(2)
        self.horizontalSlider_Arm_Gauss.setProperty("value", 3)
        self.horizontalSlider_Arm_Gauss.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_Arm_Gauss.setObjectName("horizontalSlider_Arm_Gauss")
        self.gridLayout_Arm_1.addWidget(self.horizontalSlider_Arm_Gauss, 1, 1, 1, 1)
        self.label_Arm_Threshold = QtWidgets.QLabel(self.layoutWidget)
        self.label_Arm_Threshold.setEnabled(False)
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.label_Arm_Threshold.setFont(font)
        self.label_Arm_Threshold.setFocusPolicy(QtCore.Qt.NoFocus)
        self.label_Arm_Threshold.setFrameShape(QtWidgets.QFrame.Box)
        self.label_Arm_Threshold.setAlignment(QtCore.Qt.AlignCenter)
        self.label_Arm_Threshold.setObjectName("label_Arm_Threshold")
        self.gridLayout_Arm_1.addWidget(self.label_Arm_Threshold, 0, 0, 1, 1)
        self.label_Arm_Gauss = QtWidgets.QLabel(self.layoutWidget)
        self.label_Arm_Gauss.setEnabled(False)
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.label_Arm_Gauss.setFont(font)
        self.label_Arm_Gauss.setFocusPolicy(QtCore.Qt.NoFocus)
        self.label_Arm_Gauss.setFrameShape(QtWidgets.QFrame.Box)
        self.label_Arm_Gauss.setAlignment(QtCore.Qt.AlignCenter)
        self.label_Arm_Gauss.setObjectName("label_Arm_Gauss")
        self.gridLayout_Arm_1.addWidget(self.label_Arm_Gauss, 1, 0, 1, 1)
        self.label_Arm_Sharpen = QtWidgets.QLabel(self.layoutWidget)
        self.label_Arm_Sharpen.setEnabled(False)
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.label_Arm_Sharpen.setFont(font)
        self.label_Arm_Sharpen.setFocusPolicy(QtCore.Qt.NoFocus)
        self.label_Arm_Sharpen.setFrameShape(QtWidgets.QFrame.Box)
        self.label_Arm_Sharpen.setAlignment(QtCore.Qt.AlignCenter)
        self.label_Arm_Sharpen.setObjectName("label_Arm_Sharpen")
        self.gridLayout_Arm_1.addWidget(self.label_Arm_Sharpen, 2, 0, 1, 1)
        self.horizontalSlider_Arm_Sharpen = QtWidgets.QSlider(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.horizontalSlider_Arm_Sharpen.setFont(font)
        self.horizontalSlider_Arm_Sharpen.setMinimum(1)
        self.horizontalSlider_Arm_Sharpen.setMaximum(9)
        self.horizontalSlider_Arm_Sharpen.setSingleStep(2)
        self.horizontalSlider_Arm_Sharpen.setPageStep(2)
        self.horizontalSlider_Arm_Sharpen.setProperty("value", 5)
        self.horizontalSlider_Arm_Sharpen.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_Arm_Sharpen.setObjectName("horizontalSlider_Arm_Sharpen")
        self.gridLayout_Arm_1.addWidget(self.horizontalSlider_Arm_Sharpen, 2, 1, 1, 1)
        self.lineEdit_Arm_Pen_Height_Value = QtWidgets.QLineEdit(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.lineEdit_Arm_Pen_Height_Value.setFont(font)
        self.lineEdit_Arm_Pen_Height_Value.setFocusPolicy(QtCore.Qt.NoFocus)
        self.lineEdit_Arm_Pen_Height_Value.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_Arm_Pen_Height_Value.setReadOnly(True)
        self.lineEdit_Arm_Pen_Height_Value.setObjectName("lineEdit_Arm_Pen_Height_Value")
        self.gridLayout_Arm_1.addWidget(self.lineEdit_Arm_Pen_Height_Value, 3, 2, 1, 1)
        self.gridLayout_Arm_1.setColumnStretch(0, 2)
        self.gridLayout_Arm_1.setColumnStretch(1, 4)
        self.gridLayout_Arm_1.setColumnStretch(2, 1)
        self.pushButton_Arm_Stop_Arm = QtWidgets.QPushButton(Arm)
        self.pushButton_Arm_Stop_Arm.setGeometry(QtCore.QRect(520, 320, 91, 61))
        font = QtGui.QFont()
        font.setFamily("3ds")
        font.setPointSize(12)
        self.pushButton_Arm_Stop_Arm.setFont(font)
        self.pushButton_Arm_Stop_Arm.setObjectName("pushButton_Arm_Stop_Arm")
        self.layoutWidget1 = QtWidgets.QWidget(Arm)
        self.layoutWidget1.setGeometry(QtCore.QRect(10, 393, 601, 31))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.gridLayout_Arm_3 = QtWidgets.QGridLayout(self.layoutWidget1)
        self.gridLayout_Arm_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_Arm_3.setObjectName("gridLayout_Arm_3")
        self.label_Arm_Axis_Y = QtWidgets.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.label_Arm_Axis_Y.setFont(font)
        self.label_Arm_Axis_Y.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_Arm_Axis_Y.setAlignment(QtCore.Qt.AlignCenter)
        self.label_Arm_Axis_Y.setObjectName("label_Arm_Axis_Y")
        self.gridLayout_Arm_3.addWidget(self.label_Arm_Axis_Y, 0, 3, 1, 1)
        self.label_Arm_Axis = QtWidgets.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.label_Arm_Axis.setFont(font)
        self.label_Arm_Axis.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_Arm_Axis.setAlignment(QtCore.Qt.AlignCenter)
        self.label_Arm_Axis.setObjectName("label_Arm_Axis")
        self.gridLayout_Arm_3.addWidget(self.label_Arm_Axis, 0, 0, 1, 1)
        self.label_Arm_Axis_Z = QtWidgets.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.label_Arm_Axis_Z.setFont(font)
        self.label_Arm_Axis_Z.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_Arm_Axis_Z.setAlignment(QtCore.Qt.AlignCenter)
        self.label_Arm_Axis_Z.setObjectName("label_Arm_Axis_Z")
        self.gridLayout_Arm_3.addWidget(self.label_Arm_Axis_Z, 0, 5, 1, 1)
        self.label_Arm_Axis_X = QtWidgets.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.label_Arm_Axis_X.setFont(font)
        self.label_Arm_Axis_X.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_Arm_Axis_X.setAlignment(QtCore.Qt.AlignCenter)
        self.label_Arm_Axis_X.setObjectName("label_Arm_Axis_X")
        self.gridLayout_Arm_3.addWidget(self.label_Arm_Axis_X, 0, 1, 1, 1)
        self.label_Arm_Axis_X_Value = QtWidgets.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.label_Arm_Axis_X_Value.setFont(font)
        self.label_Arm_Axis_X_Value.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_Arm_Axis_X_Value.setAlignment(QtCore.Qt.AlignCenter)
        self.label_Arm_Axis_X_Value.setObjectName("label_Arm_Axis_X_Value")
        self.gridLayout_Arm_3.addWidget(self.label_Arm_Axis_X_Value, 0, 2, 1, 1)
        self.label_Arm_Axis_Y_Value = QtWidgets.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.label_Arm_Axis_Y_Value.setFont(font)
        self.label_Arm_Axis_Y_Value.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_Arm_Axis_Y_Value.setAlignment(QtCore.Qt.AlignCenter)
        self.label_Arm_Axis_Y_Value.setObjectName("label_Arm_Axis_Y_Value")
        self.gridLayout_Arm_3.addWidget(self.label_Arm_Axis_Y_Value, 0, 4, 1, 1)
        self.label_Arm_Axis_Z_Value = QtWidgets.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.label_Arm_Axis_Z_Value.setFont(font)
        self.label_Arm_Axis_Z_Value.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_Arm_Axis_Z_Value.setAlignment(QtCore.Qt.AlignCenter)
        self.label_Arm_Axis_Z_Value.setObjectName("label_Arm_Axis_Z_Value")
        self.gridLayout_Arm_3.addWidget(self.label_Arm_Axis_Z_Value, 0, 6, 1, 1)
        self.pushButton_Arm_Connect = QtWidgets.QPushButton(Arm)
        self.pushButton_Arm_Connect.setGeometry(QtCore.QRect(410, 320, 91, 61))
        font = QtGui.QFont()
        font.setFamily("3ds")
        font.setPointSize(12)
        self.pushButton_Arm_Connect.setFont(font)
        self.pushButton_Arm_Connect.setObjectName("pushButton_Arm_Connect")
        self.splitter_Arm_1 = QtWidgets.QSplitter(Arm)
        self.splitter_Arm_1.setGeometry(QtCore.QRect(630, 20, 101, 91))
        self.splitter_Arm_1.setOrientation(QtCore.Qt.Vertical)
        self.splitter_Arm_1.setObjectName("splitter_Arm_1")
        self.radioButton_Arm_Line_Mode = QtWidgets.QRadioButton(self.splitter_Arm_1)
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.radioButton_Arm_Line_Mode.setFont(font)
        self.radioButton_Arm_Line_Mode.setObjectName("radioButton_Arm_Line_Mode")
        self.radioButton_Arm_Curves_Mode = QtWidgets.QRadioButton(self.splitter_Arm_1)
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.radioButton_Arm_Curves_Mode.setFont(font)
        self.radioButton_Arm_Curves_Mode.setObjectName("radioButton_Arm_Curves_Mode")
        self.radioButton_Arm_Img_Mode = QtWidgets.QRadioButton(self.splitter_Arm_1)
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.radioButton_Arm_Img_Mode.setFont(font)
        self.radioButton_Arm_Img_Mode.setChecked(True)
        self.radioButton_Arm_Img_Mode.setObjectName("radioButton_Arm_Img_Mode")
        self.splitter_Arm_2 = QtWidgets.QSplitter(Arm)
        self.splitter_Arm_2.setGeometry(QtCore.QRect(630, 120, 101, 201))
        self.splitter_Arm_2.setOrientation(QtCore.Qt.Vertical)
        self.splitter_Arm_2.setObjectName("splitter_Arm_2")
        self.pushButton_Arm_Import_Picture = QtWidgets.QPushButton(self.splitter_Arm_2)
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.pushButton_Arm_Import_Picture.setFont(font)
        self.pushButton_Arm_Import_Picture.setStyleSheet("")
        self.pushButton_Arm_Import_Picture.setObjectName("pushButton_Arm_Import_Picture")
        self.pushButton_Arm_Gray_Picture = QtWidgets.QPushButton(self.splitter_Arm_2)
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.pushButton_Arm_Gray_Picture.setFont(font)
        self.pushButton_Arm_Gray_Picture.setStyleSheet("")
        self.pushButton_Arm_Gray_Picture.setObjectName("pushButton_Arm_Gray_Picture")
        self.pushButton_Arm_Binaryzation_Picture = QtWidgets.QPushButton(self.splitter_Arm_2)
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.pushButton_Arm_Binaryzation_Picture.setFont(font)
        self.pushButton_Arm_Binaryzation_Picture.setObjectName("pushButton_Arm_Binaryzation_Picture")
        self.pushButton_Arm_Contour_Picture = QtWidgets.QPushButton(self.splitter_Arm_2)
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.pushButton_Arm_Contour_Picture.setFont(font)
        self.pushButton_Arm_Contour_Picture.setStyleSheet("alternate-background-color: rgb(16, 16, 16);")
        self.pushButton_Arm_Contour_Picture.setObjectName("pushButton_Arm_Contour_Picture")
        self.pushButton_Arm_Clear_All = QtWidgets.QPushButton(self.splitter_Arm_2)
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.pushButton_Arm_Clear_All.setFont(font)
        self.pushButton_Arm_Clear_All.setObjectName("pushButton_Arm_Clear_All")
        self.pushButton_Arm_Change_Gcode = QtWidgets.QPushButton(self.splitter_Arm_2)
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.pushButton_Arm_Change_Gcode.setFont(font)
        self.pushButton_Arm_Change_Gcode.setObjectName("pushButton_Arm_Change_Gcode")
        self.pushButton_Arm_Execute_Gcode = QtWidgets.QPushButton(self.splitter_Arm_2)
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.pushButton_Arm_Execute_Gcode.setFont(font)
        self.pushButton_Arm_Execute_Gcode.setObjectName("pushButton_Arm_Execute_Gcode")
        self.label_Arm_Servo_GPIO = QtWidgets.QLabel(Arm)
        self.label_Arm_Servo_GPIO.setGeometry(QtCore.QRect(630, 570, 91, 29))
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.label_Arm_Servo_GPIO.setFont(font)
        self.label_Arm_Servo_GPIO.setFrameShape(QtWidgets.QFrame.Box)
        self.label_Arm_Servo_GPIO.setAlignment(QtCore.Qt.AlignCenter)
        self.label_Arm_Servo_GPIO.setObjectName("label_Arm_Servo_GPIO")
        self.comboBox_Arm_Servo = QtWidgets.QComboBox(Arm)
        self.comboBox_Arm_Servo.setGeometry(QtCore.QRect(730, 570, 61, 31))
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.comboBox_Arm_Servo.setFont(font)
        self.comboBox_Arm_Servo.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.comboBox_Arm_Servo.setObjectName("comboBox_Arm_Servo")
        self.comboBox_Arm_Servo.addItem("")
        self.comboBox_Arm_Servo.addItem("")
        self.comboBox_Arm_Servo.addItem("")
        self.comboBox_Arm_Servo.addItem("")
        self.comboBox_Arm_Servo.addItem("")
        self.label_Arm_Servo_Angle = QtWidgets.QLabel(Arm)
        self.label_Arm_Servo_Angle.setGeometry(QtCore.QRect(800, 570, 91, 31))
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.label_Arm_Servo_Angle.setFont(font)
        self.label_Arm_Servo_Angle.setFrameShape(QtWidgets.QFrame.Box)
        self.label_Arm_Servo_Angle.setAlignment(QtCore.Qt.AlignCenter)
        self.label_Arm_Servo_Angle.setObjectName("label_Arm_Servo_Angle")
        self.lineEdit_Arm_Servo_Angle_Value = QtWidgets.QLineEdit(Arm)
        self.lineEdit_Arm_Servo_Angle_Value.setEnabled(True)
        self.lineEdit_Arm_Servo_Angle_Value.setGeometry(QtCore.QRect(900, 570, 61, 31))
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.lineEdit_Arm_Servo_Angle_Value.setFont(font)
        self.lineEdit_Arm_Servo_Angle_Value.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.lineEdit_Arm_Servo_Angle_Value.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_Arm_Servo_Angle_Value.setDragEnabled(False)
        self.lineEdit_Arm_Servo_Angle_Value.setReadOnly(False)
        self.lineEdit_Arm_Servo_Angle_Value.setObjectName("lineEdit_Arm_Servo_Angle_Value")
        self.pushButton_Arm_Servo_Turn_Off = QtWidgets.QPushButton(Arm)
        self.pushButton_Arm_Servo_Turn_Off.setGeometry(QtCore.QRect(970, 570, 41, 31))
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.pushButton_Arm_Servo_Turn_Off.setFont(font)
        self.pushButton_Arm_Servo_Turn_Off.setAutoRepeat(True)
        self.pushButton_Arm_Servo_Turn_Off.setAutoExclusive(False)
        self.pushButton_Arm_Servo_Turn_Off.setObjectName("pushButton_Arm_Servo_Turn_Off")
        self.pushButton_Arm_Servo_Turn_On = QtWidgets.QPushButton(Arm)
        self.pushButton_Arm_Servo_Turn_On.setGeometry(QtCore.QRect(1020, 570, 41, 31))
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.pushButton_Arm_Servo_Turn_On.setFont(font)
        self.pushButton_Arm_Servo_Turn_On.setAutoRepeat(True)
        self.pushButton_Arm_Servo_Turn_On.setAutoExclusive(False)
        self.pushButton_Arm_Servo_Turn_On.setObjectName("pushButton_Arm_Servo_Turn_On")
        self.pushButton_Arm_Buzzer = QtWidgets.QPushButton(Arm)
        self.pushButton_Arm_Buzzer.setGeometry(QtCore.QRect(740, 340, 101, 31))
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.pushButton_Arm_Buzzer.setFont(font)
        self.pushButton_Arm_Buzzer.setObjectName("pushButton_Arm_Buzzer")
        self.pushButton_Arm_Load_Relax = QtWidgets.QPushButton(Arm)
        self.pushButton_Arm_Load_Relax.setGeometry(QtCore.QRect(630, 340, 101, 31))
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.pushButton_Arm_Load_Relax.setFont(font)
        self.pushButton_Arm_Load_Relax.setObjectName("pushButton_Arm_Load_Relax")
        self.pushButton_Arm_Led_UI = QtWidgets.QPushButton(Arm)
        self.pushButton_Arm_Led_UI.setGeometry(QtCore.QRect(960, 340, 101, 31))
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.pushButton_Arm_Led_UI.setFont(font)
        self.pushButton_Arm_Led_UI.setObjectName("pushButton_Arm_Led_UI")
        self.pushButton_Arm_Parameter_UI = QtWidgets.QPushButton(Arm)
        self.pushButton_Arm_Parameter_UI.setGeometry(QtCore.QRect(850, 340, 101, 31))
        font = QtGui.QFont()
        font.setFamily("3ds")
        self.pushButton_Arm_Parameter_UI.setFont(font)
        self.pushButton_Arm_Parameter_UI.setObjectName("pushButton_Arm_Parameter_UI")
        self.lineEdit_Arm_IP_Address = QtWidgets.QLineEdit(Arm)
        self.lineEdit_Arm_IP_Address.setGeometry(QtCore.QRect(150, 320, 241, 61))
        font = QtGui.QFont()
        font.setFamily("3ds")
        font.setPointSize(12)
        self.lineEdit_Arm_IP_Address.setFont(font)
        self.lineEdit_Arm_IP_Address.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.lineEdit_Arm_IP_Address.setObjectName("lineEdit_Arm_IP_Address")
        self.label_Arm_IP = QtWidgets.QLabel(Arm)
        self.label_Arm_IP.setGeometry(QtCore.QRect(12, 320, 121, 61))
        font = QtGui.QFont()
        font.setFamily("3ds")
        font.setPointSize(12)
        self.label_Arm_IP.setFont(font)
        self.label_Arm_IP.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_Arm_IP.setAlignment(QtCore.Qt.AlignCenter)
        self.label_Arm_IP.setObjectName("label_Arm_IP")
        self.lineEdit_Arm_IP_Address.raise_()
        self.label_Arm_IP.raise_()
        self.pushButton_Arm_Buzzer.raise_()
        self.pushButton_Arm_Load_Relax.raise_()
        self.pushButton_Arm_Led_UI.raise_()
        self.pushButton_Arm_Parameter_UI.raise_()
        self.splitter_Arm_1.raise_()
        self.splitter_Arm_2.raise_()
        self.label_Arm_Video.raise_()
        self.textEdit_Arm_Gcode_Area.raise_()
        self.groupBox_Arm_Axis.raise_()
        self.layoutWidget.raise_()
        self.pushButton_Arm_Stop_Arm.raise_()
        self.layoutWidget.raise_()
        self.pushButton_Arm_Connect.raise_()
        self.label_Arm_Servo_GPIO.raise_()
        self.comboBox_Arm_Servo.raise_()
        self.label_Arm_Servo_Angle.raise_()
        self.lineEdit_Arm_Servo_Angle_Value.raise_()
        self.pushButton_Arm_Servo_Turn_Off.raise_()
        self.pushButton_Arm_Servo_Turn_On.raise_()

        self.retranslateUi(Arm)
        QtCore.QMetaObject.connectSlotsByName(Arm)

    def retranslateUi(self, Arm):
        _translate = QtCore.QCoreApplication.translate
        Arm.setWindowTitle(_translate("Arm", "Freenove"))
        self.groupBox_Arm_Axis.setTitle(_translate("Arm", "Axis"))
        self.pushButton_Arm_Axis_Z_Add.setText(_translate("Arm", "Z+"))
        self.pushButton_Arm_Axis_Y_Subtract.setText(_translate("Arm", "Y-"))
        self.pushButton_Arm_Axis_X_Subtract.setText(_translate("Arm", "X-"))
        self.pushButton_Arm_Axis_Z_Subtract.setText(_translate("Arm", "Z-"))
        self.pushButton_Arm_Axis_Y_Add.setText(_translate("Arm", "Y+"))
        self.pushButton_Arm_Axis_X_Add.setText(_translate("Arm", "X+"))
        self.pushButton_Arm_Record_Command.setText(_translate("Arm", "Record"))
        self.pushButton_Arm_Withdraw_Command.setText(_translate("Arm", "Undo"))
        self.pushButton_Arm_Execute_Record_Command.setText(_translate("Arm", "Execute"))
        self.pushButton_Arm_Save_Record_Command.setText(_translate("Arm", "Save"))
        self.pushButton_Arm_Import_Record_Command.setText(_translate("Arm", "Import"))
        self.pushButton_Arm_Axis_Switched.setText(_translate("Arm", "Step: X10"))
        self.pushButton_Arm_Zero_Point.setText(_translate("Arm", "Sensor Point"))
        self.pushButton_Arm_Position.setText(_translate("Arm", "Home"))
        self.pushButton_Arm_Home_Up.setText(_translate("Arm", "Home Up"))
        self.lineEdit_Arm_Threshold_Value.setText(_translate("Arm", "100"))
        self.label_Arm_Pen_Up_Height.setText(_translate("Arm", "Pen Up Height"))
        self.lineEdit_Arm_Sharpen_Value.setText(_translate("Arm", "5"))
        self.lineEdit_Arm_Gauss_Value.setText(_translate("Arm", "3"))
        self.label_Arm_Threshold.setText(_translate("Arm", "Threshold"))
        self.label_Arm_Gauss.setText(_translate("Arm", "Gauss"))
        self.label_Arm_Sharpen.setText(_translate("Arm", "Sharpen"))
        self.lineEdit_Arm_Pen_Height_Value.setText(_translate("Arm", "15"))
        self.pushButton_Arm_Stop_Arm.setText(_translate("Arm", " Stop Arm"))
        self.label_Arm_Axis_Y.setText(_translate("Arm", "Y"))
        self.label_Arm_Axis.setText(_translate("Arm", "Axis:"))
        self.label_Arm_Axis_Z.setText(_translate("Arm", "Z"))
        self.label_Arm_Axis_X.setText(_translate("Arm", "X"))
        self.label_Arm_Axis_X_Value.setText(_translate("Arm", "0"))
        self.label_Arm_Axis_Y_Value.setText(_translate("Arm", "200"))
        self.label_Arm_Axis_Z_Value.setText(_translate("Arm", "0"))
        self.pushButton_Arm_Connect.setText(_translate("Arm", "Connect"))
        self.radioButton_Arm_Line_Mode.setText(_translate("Arm", "Line Mode"))
        self.radioButton_Arm_Curves_Mode.setText(_translate("Arm", "Curves Mode"))
        self.radioButton_Arm_Img_Mode.setText(_translate("Arm", "Img Mode"))
        self.pushButton_Arm_Import_Picture.setText(_translate("Arm", "Import"))
        self.pushButton_Arm_Gray_Picture.setText(_translate("Arm", "Gray"))
        self.pushButton_Arm_Binaryzation_Picture.setText(_translate("Arm", "Binary"))
        self.pushButton_Arm_Contour_Picture.setText(_translate("Arm", "Contour"))
        self.pushButton_Arm_Clear_All.setText(_translate("Arm", "Clear"))
        self.pushButton_Arm_Change_Gcode.setText(_translate("Arm", "Change"))
        self.pushButton_Arm_Execute_Gcode.setText(_translate("Arm", "Execute"))
        self.label_Arm_Servo_GPIO.setText(_translate("Arm", "Servo GPIO"))
        self.comboBox_Arm_Servo.setItemText(0, _translate("Arm", "13"))
        self.comboBox_Arm_Servo.setItemText(1, _translate("Arm", "16"))
        self.comboBox_Arm_Servo.setItemText(2, _translate("Arm", "19"))
        self.comboBox_Arm_Servo.setItemText(3, _translate("Arm", "20"))
        self.comboBox_Arm_Servo.setItemText(4, _translate("Arm", "26"))
        self.label_Arm_Servo_Angle.setText(_translate("Arm", "Servo Angle"))
        self.lineEdit_Arm_Servo_Angle_Value.setText(_translate("Arm", "90"))
        self.pushButton_Arm_Servo_Turn_Off.setText(_translate("Arm", "-"))
        self.pushButton_Arm_Servo_Turn_On.setText(_translate("Arm", "+"))
        self.pushButton_Arm_Buzzer.setText(_translate("Arm", "Buzzer"))
        self.pushButton_Arm_Load_Relax.setText(_translate("Arm", "Load Motor"))
        self.pushButton_Arm_Led_UI.setText(_translate("Arm", "LED"))
        self.pushButton_Arm_Parameter_UI.setText(_translate("Arm", "Configuration"))
        self.lineEdit_Arm_IP_Address.setText(_translate("Arm", "192.168.1.80"))
        self.label_Arm_IP.setText(_translate("Arm", "IP:"))
