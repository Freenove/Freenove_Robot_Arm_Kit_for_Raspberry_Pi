# -*- coding: utf-8 -*-
#!/usr/bin/env python

class Command:
    def __init__(self):
        self.MOVE_ACTION =           'G'    
        self.AXIS_X_ACTION =         'X'    
        self.AXIS_Y_ACTION =         'Y'    
        self.AXIS_Z_ACTION =         'Z'   
        self.DELAY_T_ACTION =        'T'    
        self.DECOLLATOR_CHAR =       ' '    

        self.CUSTOM_ACTION =         'S'    
        self.WS2812_MODE =           'M'  
        self.WS2812_RED    =         'R'     
        self.WS2812_GREEN  =         'G'    
        self.WS2812_BLUE   =         'B'  
        self.BUZZER_ACTION =         'D'
        self.GROUND_HEIGHT =         'O'     
        self.CLAMP_LENGTH =          'L'   
        self.ARM_FREQUENCY =         'Q'     
        self.ARM_MSX =               'W'     
        self.ARM_ENABLE =            'E'   
        self.ARM_SERVO_INDEX =       'I'  
        self.ARM_SERVO_ANGLE =       'A'    
        self.ARM_SENSOR_POINT =      'F'    
        self.ARM_CALIBRATION_START = 'C'    
        self.ARM_CALIBRATION_POINT = 'H'    
        self.ARM_CALIBRATION_END   = 'J'     
        self.ARM_QUERY =             'K'    
        self.ARM_STOP =              'N'    

        # G0 X1 Y1 Z1
        # G4 T150

        # S1 M1 R255 G255 B255  
        # S2 D2000/S2 D0 （S2 D0 D2000 D100 D3）
        # S3 O0.0   (mm)
        # S4 L15.0   (mm)
        # S5 X0 Y200 Z45
        # S6 Q1000 (Hz)
        # S7 M5    (1-5)
        # S8 E1    (1/0)
        # S9 I0 A90  (0-0，0-180)
        # S10 F0  

        # S11 C0                
        # S11 H0 X0 Y200 Z45    
        # S11 J0 X0 Y200 Z45   
        # S11 C1                
        # S11 H1 X-100 Y200 Z45 
        # S11 J1 X-100 Y200 Z45 
        # S11 C2               
        # S11 H2 X100 Y200 Z45 
        # S11 J2 X100 Y200 Z45
        # S11 C3                
        # S11 H3 X0 Y150 Z45   
        # S11 J3 X0 Y150 Z45    
        # S11 C4               
        # S11 H4 X0 Y250 Z45    
        # S11 J4 X0 Y250 Z45    

        # S12 K1/S12 K0 
        # S12 Kx 
        # S13 N1 