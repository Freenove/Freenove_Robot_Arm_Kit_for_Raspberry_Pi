# -*- coding: utf-8 -*-
#!/usr/bin/env python

from stepmotor import StepMotor
import time
import math

class Arm:
    def __init__(self):
        self.CLAMP_LENGTH = 0                                               #机械臂末端夹具长度                      
        self.CLAMP_HEIGHT = 0                                               #机械臂末端夹具高度
        self.ORIGINAL_HEIGHT = 90                                            #机械臂转轴距离机械臂底座的高度
        self.GROUND_HEIGHT = 0                                               #机械臂底座距离地面的高度
        self.PEN_HEIGHT = 0                                                  #设置夹具上笔的高度
        self.L1_LENGTH = 150                                                 #连接机械臂旋转点的大臂长度
        self.L2_LENGTH = 150                                                 #连接机械臂夹具的小臂长度
        self.pi = 3.14159265                                                 #圆周率π
        self.armDriver = StepMotor()                                         #申请一个步进电机对象
        self.last_axis = self.angleToCoordinata(self.armDriver.zeroAngle)
        self.currentAngle = self.armDriver.lastAngle.copy()                  #记录机械臂当前角度位置
        self.armFrequency = 1000                                             #记录机械臂的运行频率   
        self.pulse_count_angle = 0
     
        self.plane_x_x = [0,0,0,0]                                           # 用来调节机械臂平面.x轴随x轴变化微调量
        self.plane_y_x = [0,0,0,0]                                           # 用来调节机械臂平面.x轴随y轴变化微调量
        self.plane_x_y = [0,0,0,0]                                           # 用来调节机械臂平面.y轴随x轴变化微调量
        self.plane_y_y = [0,0,0,0]                                           # 用来调节机械臂平面.y轴随y轴变化微调量
        self.plane_x_z = [0,0,0,0]                                           # 用来调节机械臂平面.z轴随x轴变化微调量
        self.plane_y_z = [0,0,0,0]                                           # 用来调节机械臂平面.z轴随y轴变化微调量
        self.current_x_offset = 0.0
        self.current_y_offset = 0.0
        self.current_z_offset = 0.0
        self.last_x_offset = 0.0
        self.last_y_offset = 0.0
        self.last_z_offset = 0.0
        self.start_axis_quadrant = 1
        self.end_axis_quadrant = 1
        self.point_quadrant_1 = 1
        self.point_quadrant_2 = 1
        
    #数值映射函数，将数据从一个范围映射到另一个范围
    def map(self, value, fromLow, fromHigh, toLow, toHigh):
        return ((toHigh-toLow)*(value-fromLow) / (fromHigh-fromLow) + toLow)
    #数值范围限制函数，将数据限制在一个范围之中
    def constrain(self, value, min, max):
        if value > max:
            value = max
        if value < min:
            value = min
        return value
    
    #判断一个点是否在另外两点所形成的线段内
    def point_is_between_line(self, p1, p2, p3):
        x_state = 0
        y_state = 0
        if p1[0] <= p2[0]:
            if p1[0] <= p3[0] <= p2[0]:
                x_state = 1
            else:
                x_state = 0
        else:
            if p2[0] <= p3[0] <= p1[0]:
                x_state = 1
            else:
                x_state = 0
        if p1[1] <= p2[1]:
            if p1[1] <= p3[1] <= p2[1]:
                y_state = 1
            else:
                y_state = 0
        else:
            if p2[1] <= p3[1] <= p1[1]:
                y_state = 1
            else:
                y_state = 0
        if x_state == 1 and y_state == 1:
            return True
        else:
            return False
    #已知点P3(x3,y3)位于点P1(x1, y1, z1)和点P2*(x2, y2, z2)连接的直线上，求P3的z值
    def calculate_z_coordinate(self, start_axis, end_axis, axis):
        # 检查分母是否为零，以避免除以零的错误
        if start_axis[0] == end_axis[0]:
            if start_axis[1] == end_axis[1]:
                return "Error Result" #上下移动，x,y轴没有发生变化
            else:
                # 使用y坐标来计算t
                t = (axis[1] - start_axis[1]) / (end_axis[1] - start_axis[1])
        elif start_axis[1] == end_axis[1]:
            # 使用x坐标来计算t
            t = (axis[0] - start_axis[0]) / (end_axis[0] - start_axis[0])
        else:
            # 使用任意坐标来计算t
            t = (axis[0] - start_axis[0]) / (end_axis[0] - start_axis[0])
            # 使用t来计算z坐标
        z = start_axis[2] + t * (end_axis[2] - start_axis[2])
        return z
    #求解二元一次方程
    def solve_quadratic(self, a, b, c):
        # 计算判别式
        discriminant = b ** 2 - 4 * a * c
        # 如果判别式小于等于0，方程无实根或者有1个根
        if discriminant <= 0:
            return "Error Result"
        # 方程有两个根
        root1 = (-b + math.sqrt(discriminant)) / (2 * a)
        root2 = (-b - math.sqrt(discriminant)) / (2 * a)
        return root1, root2
    #根据直线斜率，直线截距，圆半径计算相交点x坐标
    def find_intersections(self, k_value, b_value, r_value):
        # y = kx + b
        # x^2 + y^2 = r^2
        # (k^2+1)x^2 + 2kbx + (b^2-r^2) = 0
        # a = k^2+1, b = 2kb, c = b^2-r^2
        a = k_value * k_value + 1
        b = 2 * k_value * b_value
        c = (b_value * b_value) - (r_value * r_value)
        x_axis = self.solve_quadratic(a, b, c)
        return x_axis
    #根据坐标，圆半径，计算相交点坐标
    def calculate_axis(self, start_axis, end_axis, radius):
        # k = (y2 - y1)/(x2 - x1)
        # b = y - k * x
        # x^2 + y^2 = r^2
        x_offset = end_axis[0] - start_axis[0]
        y_offset = end_axis[1] - start_axis[1]
        if x_offset!=0 and y_offset!=0:
            k_value  = y_offset / x_offset
            b_value = start_axis[1] - (k_value * start_axis[0])
            r_value = radius
            x_axis = self.find_intersections(k_value, b_value, r_value)
            if x_axis != "Error Result":                                             #方程有两个解
                y1 = k_value * x_axis[0] + b_value                                   #计算y1值
                y2 = k_value * x_axis[1] + b_value                                   #计算y2值
                if start_axis[0] > end_axis[0]:                                      #如果起始点在终点的右边
                    if x_axis[0] > x_axis[1]:                                        #第一个解在第二个解的右边
                        return [x_axis[0], y1], [x_axis[1], y2]                    
                    elif x_axis[0] < x_axis[1]:                                      #如果第一个解在第二个解的左边
                        return [x_axis[1], y2], [x_axis[0], y1]
                elif start_axis[0] < end_axis[0]:                                    #如果起始点在终点的左边
                    if x_axis[0] < x_axis[1]:                                        #如果第一个解在第二个解的左边
                        return [x_axis[0], y1], [x_axis[1], y2]
                    elif x_axis[0] > x_axis[1]:                                      #第一个解在第二个解的右边
                        return [x_axis[1], y2], [x_axis[0], y1]
            else:
                return "Error Result"
        elif x_offset == 0 and y_offset != 0:
            if math.fabs(start_axis[0]) < radius:
                y = math.sqrt((radius * radius) - (start_axis[0] * start_axis[0]))
                if start_axis[1] > end_axis[1]:
                    return [start_axis[0], y], [start_axis[0], -y]
                elif start_axis[1] < end_axis[1]:
                    return [start_axis[0], -y], [start_axis[0], y]
            else:
                return "Error Y"
        elif x_offset != 0 and y_offset == 0:
            if math.fabs(start_axis[1]) < radius:
                x = math.sqrt((radius * radius) - (start_axis[1] * start_axis[1]))
                if start_axis[0] > end_axis[0]:
                    return [x, start_axis[1]], [-x, start_axis[1]]
                elif start_axis[0] < end_axis[0]:
                    return [-x, start_axis[1]], [x, start_axis[1]]
            else:
                return "Error X"
        else:
            return "Error XY"
    #判断一个点是否在球内
    def is_point_inside_sphere(self, x, y, z, radius):  
        # 计算点到原点的距离  
        distance_to_origin = math.sqrt(x**2 + y**2 + (z-self.ORIGINAL_HEIGHT)**2)  
        # 判断点在球内、球面上还是球外  
        if distance_to_origin < radius:  
            return 0 #点在球内
        elif distance_to_origin == radius:  
            return 1 #点在球面上
        else:  
            return 2 #点在球外
    #根据坐标，圆半径，计算与圆相交的两个点坐标位置，以及他们之间较小的角度，如果直线与圆不相交，则返回[0, 0]
    def calculate_valid_axis(self, start_axis, end_axis, radius):
        axis = self.calculate_axis(start_axis, end_axis, radius)              #得到2个与圆相交的坐标点
        if axis != "Error Result" and axis != "Error X" and axis != "Error Y" and axis != "Error XY":#如果直线与圆相交有解，存在2个相交点
            #如果两个相交点都在首尾线段上
            if self.point_is_between_line(start_axis, end_axis, axis[0]) and self.point_is_between_line(start_axis, end_axis, axis[1]): 
                z = self.calculate_z_coordinate(start_axis, end_axis, axis[0]) #计算第一个相交点的z值，只要不是单纯沿z轴方向上下移动就有解
                if z != "Error Result":
                    return [1, 2], [axis[0][0], axis[0][1], z], [axis[1][0], axis[1][1], z] #有两个相交点，返回2个坐标
                else:
                    return [0, 0], [0, 0, 0], [0, 0, 0]
            #有两个解，但是只有一个解在线段内（起点在圆外，终点在圆上或者圆内）
            elif self.point_is_between_line(start_axis, end_axis, axis[0]) and not self.point_is_between_line(start_axis, end_axis, axis[1]):
                z = self.calculate_z_coordinate(start_axis, end_axis, axis[0])
                #相交点不在起点位置（终点在圆上或者圆内）
                if round(start_axis[0], 2) != round(axis[0][0], 2) or round(start_axis[1], 2) != round(axis[0][1], 2):
                    return [1, 1], [axis[0][0], axis[0][1], z], [0, 0, 0]
                #相交点在起点位置
                else:
                    #如果终点在圆外
                    if (round(math.pow(end_axis[0], 2), 2) + round(math.pow(end_axis[1], 2), 2)) > math.pow(radius, 2):   
                        return [1, 1], [end_axis[0], end_axis[1], end_axis[2]], [0, 0, 0]
                    #如果终点在圆内
                    else:                                                                                                 
                        return [1, 0], [0, 0, 0], [0, 0, 0]        
            #有两个解，但是只有一个解在线段内
            elif not self.point_is_between_line(start_axis, end_axis, axis[0]) and self.point_is_between_line(start_axis, end_axis, axis[1]):
                z = self.calculate_z_coordinate(start_axis, end_axis, axis[1])
                #相交点不在起点位置（终点在圆上或者圆内）
                if round(start_axis[0], 2) != round(axis[1][0], 2) or round(start_axis[1], 2) != round(axis[1][1], 2):
                    return [1, 1], [axis[1][0], axis[1][1], z], [0, 0, 0]
                #如果起点在圆上，判断终点位置，终点在圆外，返回终点坐标，终点在圆内，不执行操作
                else:
                    if (round(math.pow(end_axis[0], 2), 2) + round(math.pow(end_axis[1], 2), 2)) > math.pow(radius, 2):   
                        return [1, 1], [end_axis[0], end_axis[1], end_axis[2]], [0, 0, 0]
                    else:                                                                                                
                        return [1, 0], [0, 0, 0], [0, 0, 0]  
            #没有相交点(有解，但是解不在线段内)
            else:
                return [0, 0], [0, 0, 0], [0, 0, 0]
        else:
            #print("Line segments do not intersect the circle, or parallel the x and y axes.")
            return [0, 0], [0, 0, 0], [0, 0, 0]
    
    #弧度转化为角度
    def radianToAngle(self, radian):
        return radian * (180 / self.pi)
    #角度转化为弧度
    def angleToRadian(self, angle):     
        return angle * (self.pi / 180)
    #三边求角：cosA = （b*b+c*c-a*a）/2bc
    def sidesToAngle(self, a, b, c):     
        A = math.pow(a,2)
        B = math.pow(b,2)
        C = math.pow(c,2)
        D = math.fabs(2 * b * c)
        cosA = (B + C - A) / D
        radian = math.acos(cosA)
        return self.radianToAngle(radian)
    
    #将坐标转化为角度 
    def coordinateToAngle(self, axis): 
        tanxy = math.atan2(axis[1], axis[0])
        angle0 = self.radianToAngle(tanxy)                                            #底部电机转动角度，x轴正方向为0度，y轴处为90度，x轴负方向为180度
        
        dPlane = math.fabs(math.sqrt(math.pow(axis[0],2) + math.pow(axis[1],2)))      #计算目标点在xy平面映射点到原点的距离
        d1Plane = dPlane - self.CLAMP_LENGTH                                          #计算机械臂末端点（除去夹具）在xy平面映射点到原点的距离
        #zHeight = axis[2] - self.ORIGINAL_HEIGHT - self.GROUND_HEIGHT + self.CLAMP_HEIGHT + self.PEN_HEIGHT #以机械臂转轴为原点，坐标z需要减去机械臂距离地面的高度
        zHeight = axis[2] - self.ORIGINAL_HEIGHT - self.GROUND_HEIGHT + self.PEN_HEIGHT #以机械臂转轴为原点，坐标z需要减去机械臂距离地面的高度
        dHypotenuse = math.sqrt(math.pow(d1Plane,2) + math.pow(zHeight,2))            #机械臂转轴到末端点的距离

        #三边求角：cosA = （b*b+c*c-a*a）/2bc*，a=b，即cosA = c / (2b)
        angle1 = self.sidesToAngle(self.L2_LENGTH, self.L1_LENGTH, dHypotenuse)       #机械臂大臂和机械臂转轴与机械臂末端点 的夹角角度
        angle2 = self.radianToAngle(math.atan2(math.fabs(zHeight), d1Plane))          #机械臂转轴在xy平面投影形成的夹角
        if zHeight > 0:                                                               #计算机械臂大臂与xy轴平面的夹角角度
            angle3 = angle1 + angle2
        else:
            angle3 = angle1 - angle2                                                  #左侧电机转动角度，y轴正方向为0度，z轴处为90度，y轴负方向为180度  
        angle4 = 180 - (2 * angle1)                                                   #计算机械臂大臂与机械臂小臂的夹角角度
        angle5 = 180 - (angle3 + angle4)                                              #右侧电机需要转动的角度，y轴正方向为180度，z轴处为90度，y轴负方向为0度
        angle = [angle0, angle3, angle5]
        return angle
    
    #将角度转化为坐标
    def angleToCoordinata(self, angle):   
        angle0 = angle[0]
        angle3 = angle[1]
        angle5 = angle[2]
        angle4 = 180-angle3-angle5
        angle1 = (180-angle4)/2
        if angle1>angle3:
            angle2 = angle1-angle3
        else:
            angle2 = angle3-angle1
        A = math.pow(self.L1_LENGTH,2)
        B = math.pow(self.L2_LENGTH,2)
        C = 2 * self.L1_LENGTH * self.L2_LENGTH * math.cos(self.angleToRadian(angle4))
        dHypotenuse = math.sqrt(A+B-C)
        
        zHeight = dHypotenuse * math.sin(self.angleToRadian(angle2))
        if angle1 > angle3:
            #z = self.ORIGINAL_HEIGHT + self.GROUND_HEIGHT - zHeight - self.CLAMP_HEIGHT - self.PEN_HEIGHT
            z = self.ORIGINAL_HEIGHT + self.GROUND_HEIGHT - zHeight - self.PEN_HEIGHT
        else:
            #z = self.ORIGINAL_HEIGHT + self.GROUND_HEIGHT + zHeight - self.CLAMP_HEIGHT - self.PEN_HEIGHT
            z = self.ORIGINAL_HEIGHT + self.GROUND_HEIGHT + zHeight - self.PEN_HEIGHT

        angle6 = 90 - angle2
        d1Plane = dHypotenuse * math.sin(self.angleToRadian(angle6))
        dPlane = d1Plane + self.CLAMP_LENGTH  
        y = dPlane * math.sin(self.angleToRadian(angle0))
        angle7 = 90 - angle0
        x = dPlane * math.sin(self.angleToRadian(angle7))
        return [x, y, z]
    
    #控制机械臂移动到对应的坐标
    def moveStepMotorToTargetAxis(self, axis, mode=0):
        start_axis = self.last_axis.copy()                        # 开始位置坐标
        end_axis = axis.copy()                                    # 结束位置坐标
        self.last_axis = axis.copy()                              # 更新最后一次移动的坐标点位置
        if self.plane_x_z[0] != 0 and self.plane_x_z[1] != 0:
            x_z = self.map(end_axis[0], self.plane_x_z[0], self.plane_x_z[1], self.plane_x_z[2], self.plane_x_z[3])  # 映射z轴在x轴上的微调量
        else:
            x_z = 0
        if self.plane_y_z[0] != 0 and self.plane_y_z[1] != 0:
            y_z = self.map(end_axis[1], self.plane_y_z[0], self.plane_y_z[1], self.plane_y_z[2], self.plane_y_z[3])  # 映射z轴在y轴上的微调量
        else:
            y_z = 0

        self.current_z_offset = x_z + y_z                                                      #计算z轴偏移值
        calculated = [(end_axis[i] - start_axis[i]) for i in range(3)]                         #计算起始点到目标点的三轴差值
        calculated_value = [0, 0, 0]
        calculated_value[0] = calculated[0] + self.current_x_offset - self.last_x_offset       #计算x轴经过两轮调节后的实际值
        calculated_value[1] = calculated[1] + self.current_y_offset - self.last_y_offset       #计算y轴经过两轮调节后的实际值
        calculated_value[2] = calculated[2] + self.current_z_offset - self.last_z_offset       #计算z轴经过两轮调节后的实际值

        fabs_calculated_value = [math.fabs(calculated_value[i]) for i in range(3)]   #计算绝对值
        buf_value = fabs_calculated_value.copy()
        buf_value.sort(reverse=True)                                                 #列表降序处理
        max_value = buf_value[0]                                                     #获取最大值
        #如果上一次数据和现在的数据相同，则不执行，不同，则进入下面进行计算
        if max_value!=0:
            processing_axis = []
            if mode==0:
                subdivision = 10
                for i in range(int(max_value*subdivision)+1):
                    buf_value[0] = (start_axis[0]+self.last_x_offset) + ((calculated_value[0]/max_value/subdivision)*i)
                    buf_value[1] = (start_axis[1]+self.last_y_offset) + ((calculated_value[1]/max_value/subdivision)*i)
                    buf_value[2] = (start_axis[2]+self.last_z_offset) + ((calculated_value[2]/max_value/subdivision)*i)
                    processing_axis.append(buf_value.copy())
            elif mode == 1:
                buf_value[0] = (start_axis[0]+self.last_x_offset) + (calculated_value[0])
                buf_value[1] = (start_axis[1]+self.last_y_offset) + (calculated_value[1])
                buf_value[2] = (start_axis[2]+self.last_z_offset) + (calculated_value[2])
                processing_axis.append(buf_value.copy())
            elif mode == 2:
                subdivision = 1
                for i in range(int(max_value*subdivision)+1):
                    buf_value[0] = (start_axis[0]+self.last_x_offset) + ((calculated_value[0]/max_value/subdivision)*i)
                    buf_value[1] = (start_axis[1]+self.last_y_offset) + ((calculated_value[1]/max_value/subdivision)*i)
                    buf_value[2] = (start_axis[2]+self.last_z_offset) + ((calculated_value[2]/max_value/subdivision)*i)
                    processing_axis.append(buf_value.copy())
            for i in range(len(processing_axis)):
                angle = self.coordinateToAngle(processing_axis[i])                             #解算坐标点映射到机械臂的角度
                angle1 = [(self.armDriver.offsetAngle[i] + angle[i]) for i in range(3)]
                self.armDriver.moveStepMotorToTargetAngle(angle1)                              #控制机械臂转动到对应的为止
        self.last_x_offset = self.current_x_offset                                             #更新x轴偏移值
        self.last_y_offset = self.current_y_offset                                             #更新y轴偏移值
        self.last_z_offset = self.current_z_offset                                             #更新z轴偏移值
    
    def setPlaneXX(self, x1, x2, xx1, xx2):
        self.plane_x_x[0] = float(x1)
        self.plane_x_x[1] = float(x2)
        self.plane_x_x[2] = float(xx1)
        self.plane_x_x[3] = float(xx2)
    def setPlaneYX(self, y1, y2, xx1, xx2):
        self.plane_y_x[0] = float(y1)
        self.plane_y_x[1] = float(y2)
        self.plane_y_x[2] = float(xx1)
        self.plane_y_x[3] = float(xx2)
    def setPlaneXY(self, x1, x2, yy1, yy2):
        self.plane_x_y[0] = float(x1)
        self.plane_x_y[1] = float(x2)
        self.plane_x_y[2] = float(yy1)
        self.plane_x_y[3] = float(yy2)
    def setPlaneYY(self, y1, y2, yy1, yy2):
        self.plane_y_y[0] = float(y1)
        self.plane_y_y[1] = float(y2)
        self.plane_y_y[2] = float(yy1)
        self.plane_y_y[3] = float(yy2)
    def setPlaneXZ(self, x1, x2, zz1, zz2):
        self.plane_x_z[0] = float(x1)
        self.plane_x_z[1] = float(x2)
        self.plane_x_z[2] = float(zz1)
        self.plane_x_z[3] = float(zz2)
    def setPlaneYZ(self, y1, y2, zz1, zz2):
        self.plane_y_z[0] = float(y1)
        self.plane_y_z[1] = float(y2)
        self.plane_y_z[2] = float(zz1)
        self.plane_y_z[3] = float(zz2)
    def setlastOffsetValue(self, x, y, z):
        self.last_x_offset = x
        self.last_y_offset = y
        self.last_z_offset = z
        
    #设置机械臂夹具长度
    def setClampLength(self, length):
        self.CLAMP_LENGTH = length
        
    #设置机械臂夹具高度
    def setClampHeight(self, height):
        self.CLAMP_HEIGHT = height
        
    #设置机械臂转轴距离底面高度
    def setOriginHeight(self, height):
        self.ORIGINAL_HEIGHT = height

    #设置机械臂底面距离地面高度
    def setGroundHeight(self, height):
        self.GROUND_HEIGHT = height

    #设置机械臂笔端高度
    def setPenHeight(self, height):
        self.PEN_HEIGHT = height
        
    #设置步进电机脉冲频率
    def setFrequency(self, frequency):
        self.armFrequency = [frequency for i in range(3)] 
        self.armDriver.setA4988ClkFrequency(self.armFrequency)
    
    #设置步进电机细分模式
    def setMsxMode(self, mode):
        self.armDriver.setA4988MsxMode(mode)
    
    #设置步进电机使能和失能
    def setArmEnable(self, enable):
        self.armDriver.setA4988Enable(enable)
    
    #设置步进电机调零
    def setArmToZeroPoint(self):
        pulse_count = self.armDriver.gotoZeroPoint()
        self.last_axis = self.angleToCoordinata(self.armDriver.lastAngle)
        self.pulse_count_angle = 0
        return pulse_count
    
    #设置步进电机回零
    def setArmToZeroPointNoAdjust(self, pulse_count):
        self.armDriver.gotoZeroPointNoAdjust(pulse_count)
        self.last_axis = self.angleToCoordinata(self.armDriver.lastAngle)
        self.pulse_count_angle = 0
    
    #设置步进电机校准偏移角度值
    def setArmOffseAngle(self, offsetAngle):
        self.armDriver.setStepMotorOffsetAngle(offsetAngle)
       
if __name__ == '__main__':
    arm = Arm() 
    arm.setArmEnable(0)
    print(arm.setArmToZeroPoint())
    arm.setArmEnable(1)

   