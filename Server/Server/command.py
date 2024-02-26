# -*- coding: utf-8 -*-
#!/usr/bin/env python

class Command:
    def __init__(self):
        self.MOVE_ACTION =           'G'     # 移动指令
        self.AXIS_X_ACTION =         'X'     # X坐标指令
        self.AXIS_Y_ACTION =         'Y'     # Y坐标指令
        self.AXIS_Z_ACTION =         'Z'     # Z坐标指令
        self.DELAY_T_ACTION =        'T'     # 延时指令
        self.DECOLLATOR_CHAR =       ' '     # 指令分隔符(空格)

        # 自定义指令
        self.CUSTOM_ACTION =         'S'     # 自定义数据指令
        self.WS2812_MODE =           'M'     # 彩灯模式指令
        self.WS2812_RED    =         'R'     # 彩灯红色指令
        self.WS2812_GREEN  =         'G'     # 彩灯绿色指令
        self.WS2812_BLUE   =         'B'     # 彩灯蓝色指令
        self.BUZZER_ACTION =         'D'     # 蜂鸣器指令
        self.GROUND_HEIGHT =         'O'     # 机械臂底面距离地面高度
        self.CLAMP_LENGTH =          'L'     # 机械臂夹具长度设置
        self.ARM_FREQUENCY =         'Q'     # 机械臂步进电机脉冲频率设置
        self.ARM_MSX =               'W'     # 机械臂步进电机细分精度设置
        self.ARM_ENABLE =            'E'     # 机械臂步进电机使能和失能设置
        self.ARM_SERVO_INDEX =       'I'     # 舵机索引号指令
        self.ARM_SERVO_ANGLE =       'A'     # 机械臂舵机控制指令
        self.ARM_SENSOR_POINT =      'F'     # 机械臂传感器校准/回零指令
        self.ARM_CALIBRATION_START = 'C'     # 机械臂校准模式开始（清除上一次该点的校准数据，并移动到该点）
        self.ARM_CALIBRATION_POINT = 'H'     # 机械臂校准模式过程（没收到START，就不进入该模式，收到，则不更新校准数据，在原始坐标的基础上移动到校准后的位置）
        self.ARM_CALIBRATION_END   = 'J'     # 机械臂校准模式结束（收到该信号，保存校准数据，更新校准坐标，结束校准）
        self.ARM_QUERY =             'K'     # 机械臂消息队列查询指令
        self.ARM_STOP =              'N'     # 机械臂紧急急停指令

        # G0 X1 Y1 Z1
        # G4 T150

        # S1 M1 R255 G255 B255  (彩灯指令：模式模式，红色，绿色，蓝色)
        # S2 D2000/S2 D0 （S2 D0 D2000 D100 D3）
        # S3 O0.0   (mm)
        # S4 L15.0   (mm)
        # S5 X0 Y200 Z45
        # S6 Q1000 (Hz)
        # S7 M5    (1-5)
        # S8 E1    (1/0)
        # S9 I0 A90  (0-第0个舵机，0-180)
        # S10 F0   (0-调零校准，1-回零点)

        # S11 C0                (开始校准Home点)
        # S11 H0 X0 Y200 Z45    (校准Home点)
        # S11 J0 X0 Y200 Z45    (保存Home点)
        # S11 C1                (开始校准相对坐标点1)
        # S11 H1 X-100 Y200 Z45 (校准相对坐标点1)
        # S11 J1 X-100 Y200 Z45 (保存相对坐标点1)
        # S11 C2                (开始校准相对坐标点2)
        # S11 H2 X100 Y200 Z45  (校准相对坐标点2)
        # S11 J2 X100 Y200 Z45  (保存相对坐标点2)
        # S11 C3                (开始校准相对坐标点3)
        # S11 H3 X0 Y150 Z45    (校准相对坐标点3)
        # S11 J3 X0 Y150 Z45    (保存相对坐标点3)
        # S11 C4                (开始校准相对坐标点4)
        # S11 H4 X0 Y250 Z45    (校准相对坐标点4)
        # S11 J4 X0 Y250 Z45    (保存相对坐标点4)

        # S12 K1/S12 K0 (上位机发送给下位机：开启计数线程，准备接收指令/关闭计数线程，停止接收指令)
        # S12 Kx (下位机发送给上位机：当前剩余x条指令)
        # S13 N1 (机械臂紧急急停指令)