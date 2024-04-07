# -*- coding: utf-8 -*-
#!/usr/bin/env python

from stepmotor import StepMotor
import math

class Arm:
    def __init__(self):
        self.CLAMP_LENGTH = 0                                                                      
        self.CLAMP_HEIGHT = 0                                                
        self.ORIGINAL_HEIGHT = 90                                            
        self.GROUND_HEIGHT = 0                                               
        self.PEN_HEIGHT = 0                                                 
        self.L1_LENGTH = 150                                                 
        self.L2_LENGTH = 150                                                
        self.pi = 3.14159265                                                 
        self.armDriver = StepMotor()                                         
        self.last_axis = self.angleToCoordinata(self.armDriver.zeroAngle)
        self.currentAngle = self.armDriver.lastAngle.copy()                
        self.armFrequency = 1000                                            
        self.pulse_count_angle = 0
        self.offsetAngle = [0, 0, 0]                                                                             
        self.plane_x_z = [0,0,0,0]                                           
        self.plane_y_z = [0,0,0,0]                                          
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
        self.arm_limit_angle1 = [26, 150]
        self.arm_limit_angle2 = [0, 110]
        self.arm_limit_angle3 = [-12, 98]
    #mapping function
    def map(self, value, fromLow, fromHigh, toLow, toHigh):
        return ((toHigh-toLow)*(value-fromLow) / (fromHigh-fromLow) + toLow)
    #range limiting function
    def constrain(self, value, min, max):
        if value > max:
            value = max
        if value < min:
            value = min
        return value
    #Calculate the maximum drawing radius of the robotic arm
    def calculate_y_value(self, z):
        y_value = [80,220]
        for y in range(50,200,1):
            try:
                axis = [0, 200-y, z]
                angle = self.coordinateToAngle(axis)
                angleA = 180-angle[1]-angle[2]
                if self.arm_limit_angle1[0] < angleA < self.arm_limit_angle1[1]:
                    if self.arm_limit_angle2[0] < angle[1] < self.arm_limit_angle2[1] and self.arm_limit_angle3[0] < angle[2] < self.arm_limit_angle3[1]:
                        pass
                    else:
                        y_value[0] = 200 - y + 1
                        break 
                else:
                     y_value[0] = 200 - y + 1
                     break   
            except:
                pass
        if y_value[0]>100:
            min_value = y_value[0]
        else:
            min_value = 100
        for y in range(min_value,400,1):
            try:
                axis = [0, y, z]
                angle = self.coordinateToAngle(axis)
                angleA = 180-angle[1]-angle[2]
                if self.arm_limit_angle1[0] < angleA < self.arm_limit_angle1[1]:
                    if self.arm_limit_angle2[0] < angle[1] < self.arm_limit_angle2[1] and self.arm_limit_angle3[0] < angle[2] < self.arm_limit_angle3[1]:
                        pass
                    else:
                        y_value[1] = y - 1
                        break 
                else:
                     y_value[1] = y - 1
                     break   
            except:
                pass
        return y_value

    #Determine whether a point is within a line segment formed by two other points
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
    #Given that point P3(x3,y3) is located on the line connected by points P1(x1, y1, z1) and P2*(x2, y2, z2), find the z value of P3
    def calculate_z_coordinate(self, start_axis, end_axis, axis):
        if start_axis[0] == end_axis[0]:
            if start_axis[1] == end_axis[1]:
                return "Error Result"
            else:
                t = (axis[1] - start_axis[1]) / (end_axis[1] - start_axis[1])
        elif start_axis[1] == end_axis[1]:
            t = (axis[0] - start_axis[0]) / (end_axis[0] - start_axis[0])
        else:
            t = (axis[0] - start_axis[0]) / (end_axis[0] - start_axis[0])
        z = start_axis[2] + t * (end_axis[2] - start_axis[2])
        return z
    #Solve equation
    def solve_quadratic(self, a, b, c):
        discriminant = b ** 2 - 4 * a * c
        if discriminant <= 0:
            return "Error Result"
        root1 = (-b + math.sqrt(discriminant)) / (2 * a)
        root2 = (-b - math.sqrt(discriminant)) / (2 * a)
        return root1, root2
    #Calculate the x coordinates of the intersection points according to the slope of the line, the intercept of the line and the radius of the circle
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
    #Calculate the coordinates of the intersection points by the coordinates, the radius of the circle
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
            if x_axis != "Error Result":                                          
                y1 = k_value * x_axis[0] + b_value                                
                y2 = k_value * x_axis[1] + b_value                                 
                if start_axis[0] > end_axis[0]:                                   
                    if x_axis[0] > x_axis[1]:                                      
                        return [x_axis[0], y1], [x_axis[1], y2]                    
                    elif x_axis[0] < x_axis[1]:                                    
                        return [x_axis[1], y2], [x_axis[0], y1]
                elif start_axis[0] < end_axis[0]:                                    
                    if x_axis[0] < x_axis[1]:                                        
                        return [x_axis[0], y1], [x_axis[1], y2]
                    elif x_axis[0] > x_axis[1]:                                      
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
    #Determine whether a point is range of the ball
    def is_point_inside_sphere(self, x, y, z, radius):   
        distance_to_origin = math.sqrt(x**2 + y**2 + (z-self.ORIGINAL_HEIGHT)**2)  
        if distance_to_origin < radius:  
            return 0 
        elif distance_to_origin == radius:  
            return 1 
        else:  
            return 2 
    #Based on the coordinates, radius of the circle, calculate the coordinate positions of the two points intersecting the circle, if the line does not intersect the circle, return [0, 0]
    def calculate_valid_axis(self, start_axis, end_axis, radius):
        axis = self.calculate_axis(start_axis, end_axis, radius)            
        if axis != "Error Result" and axis != "Error X" and axis != "Error Y" and axis != "Error XY":
            if self.point_is_between_line(start_axis, end_axis, axis[0]) and self.point_is_between_line(start_axis, end_axis, axis[1]): 
                z = self.calculate_z_coordinate(start_axis, end_axis, axis[0]) 
                if z != "Error Result":
                    return [1, 2], [axis[0][0], axis[0][1], z], [axis[1][0], axis[1][1], z] 
                else:
                    return [0, 0], [0, 0, 0], [0, 0, 0]
            elif self.point_is_between_line(start_axis, end_axis, axis[0]) and not self.point_is_between_line(start_axis, end_axis, axis[1]):
                z = self.calculate_z_coordinate(start_axis, end_axis, axis[0])
                if round(start_axis[0], 2) != round(axis[0][0], 2) or round(start_axis[1], 2) != round(axis[0][1], 2):
                    return [1, 1], [axis[0][0], axis[0][1], z], [0, 0, 0]
                else:
                    if (round(math.pow(end_axis[0], 2), 2) + round(math.pow(end_axis[1], 2), 2)) > math.pow(radius, 2):   
                        return [1, 1], [end_axis[0], end_axis[1], end_axis[2]], [0, 0, 0]
                    else:                                                                                                 
                        return [1, 0], [0, 0, 0], [0, 0, 0]        
            elif not self.point_is_between_line(start_axis, end_axis, axis[0]) and self.point_is_between_line(start_axis, end_axis, axis[1]):
                z = self.calculate_z_coordinate(start_axis, end_axis, axis[1])
                if round(start_axis[0], 2) != round(axis[1][0], 2) or round(start_axis[1], 2) != round(axis[1][1], 2):
                    return [1, 1], [axis[1][0], axis[1][1], z], [0, 0, 0]
                else:
                    if (round(math.pow(end_axis[0], 2), 2) + round(math.pow(end_axis[1], 2), 2)) > math.pow(radius, 2):   
                        return [1, 1], [end_axis[0], end_axis[1], end_axis[2]], [0, 0, 0]
                    else:                                                                                                
                        return [1, 0], [0, 0, 0], [0, 0, 0]  
            else:
                return [0, 0], [0, 0, 0], [0, 0, 0]
        else:
            #print("Line segments do not intersect the circle, or parallel the x and y axes.")
            return [0, 0], [0, 0, 0], [0, 0, 0]
    #Adjust the z-axis according to the X-axis
    def setPlaneXZ(self, x1, x2, zz1, zz2):
        self.plane_x_z[0] = float(x1)
        self.plane_x_z[1] = float(x2)
        self.plane_x_z[2] = float(zz1)
        self.plane_x_z[3] = float(zz2)
    #Adjust the z-axis according to the Y-axis
    def setPlaneYZ(self, y1, y2, zz1, zz2):
        self.plane_y_z[0] = float(y1)
        self.plane_y_z[1] = float(y2)
        self.plane_y_z[2] = float(zz1)
        self.plane_y_z[3] = float(zz2)
    #Radians are converted to angles
    def radianToAngle(self, radian):
        return radian * (180 / self.pi)
    #Angles are converted to radians
    def angleToRadian(self, angle):     
        return angle * (self.pi / 180)
    #Triangulation: cosA = （b*b+c*c-a*a）/2bc
    def sidesToAngle(self, a, b, c):     
        A = math.pow(a,2)
        B = math.pow(b,2)
        C = math.pow(c,2)
        D = math.fabs(2 * b * c)
        cosA = (B + C - A) / D
        radian = math.acos(cosA)
        return self.radianToAngle(radian)
    #Set the arm clamp length
    def setClampLength(self, length):
        self.CLAMP_LENGTH = length
    #Set the arm clamp height
    def setClampHeight(self, height):
        self.CLAMP_HEIGHT = height 
    #Set the height of the rotating shaft of the mechanical arm from the bottom surface
    def setOriginHeight(self, height):
        self.ORIGINAL_HEIGHT = height
    #Set the height between the bottom of the robot arm and the ground
    def setGroundHeight(self, height):
        self.GROUND_HEIGHT = height
    #Set the height of the pen at the end of the robot arm
    def setPenHeight(self, height):
        self.PEN_HEIGHT = height
    #Set the stepper motor pulse frequency
    def setFrequency(self, frequency):
        self.armFrequency = [frequency for i in range(3)] 
        self.armDriver.setA4988ClkFrequency(self.armFrequency)
    #Set the stepper motor subdivision mode
    def setMsxMode(self, mode):
        self.armDriver.setA4988MsxMode(mode)
    #Set stepper motor enable and disable
    def setArmEnable(self, enable):
        self.armDriver.setA4988Enable(enable)
    #Set the robot arm to calibrate the sensor center position
    def setArmToSensorPoint(self):
        pulse_count = self.armDriver.caliSensorPoint()
        self.last_axis = self.angleToCoordinata(self.armDriver.lastAngle)
        self.pulse_count_angle = 0
        return pulse_count
    #Move the arm to the center of the sensor
    def setArmToSensorPointNoAdjust(self, pulse_count):
        self.armDriver.gotoSensorPoint(pulse_count)
        self.last_axis = self.angleToCoordinata(self.armDriver.lastAngle)
        self.pulse_count_angle = 0
    #Set the stepper motor calibration offset Angle
    def setArmOffseAngle(self, offsetAngle):
        self.offsetAngle = offsetAngle.copy()
    #Convert coordinates to angles
    def coordinateToAngle(self, axis): 
        tanxy = math.atan2(axis[1], axis[0])
        angle0 = self.radianToAngle(tanxy)                                            
        dPlane = math.fabs(math.sqrt(math.pow(axis[0],2) + math.pow(axis[1],2)))      
        d1Plane = dPlane - self.CLAMP_LENGTH                                          
        zHeight = axis[2] - self.ORIGINAL_HEIGHT - self.GROUND_HEIGHT + self.PEN_HEIGHT 
        dHypotenuse = math.sqrt(math.pow(d1Plane,2) + math.pow(zHeight,2))           
        #cosA = （b*b+c*c-a*a）/(2*b*c), a=b, cosA = c / (2b)
        angle1 = self.sidesToAngle(self.L2_LENGTH, self.L1_LENGTH, dHypotenuse)       
        angle2 = self.radianToAngle(math.atan2(math.fabs(zHeight), d1Plane))          
        if zHeight > 0:                                                              
            angle3 = angle1 + angle2
        else:
            angle3 = angle1 - angle2                                                 
        angle4 = 180 - (2 * angle1)                                                   
        angle5 = 180 - (angle3 + angle4)                                             
        angle = [angle0, angle3, angle5]
        return angle
    #Convert angles to coordinates
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
            z = self.ORIGINAL_HEIGHT + self.GROUND_HEIGHT - zHeight - self.PEN_HEIGHT
        else:
            z = self.ORIGINAL_HEIGHT + self.GROUND_HEIGHT + zHeight - self.PEN_HEIGHT
        angle6 = 90 - angle2
        d1Plane = dHypotenuse * math.sin(self.angleToRadian(angle6))
        dPlane = d1Plane + self.CLAMP_LENGTH  
        y = dPlane * math.sin(self.angleToRadian(angle0))
        angle7 = 90 - angle0
        x = dPlane * math.sin(self.angleToRadian(angle7))
        return [x, y, z]
    #Control the robot arm to move to the corresponding coordinates
    def moveStepMotorToTargetAxis(self, axis, mode=0):
        start_axis = self.last_axis.copy()                       
        end_axis = axis.copy()                                   
        self.last_axis = axis.copy()                            
        if self.plane_x_z[0] != 0 and self.plane_x_z[1] != 0:
            x_z = self.map(end_axis[0], self.plane_x_z[0], self.plane_x_z[1], self.plane_x_z[2], self.plane_x_z[3])  
        else:
            x_z = 0
        if self.plane_y_z[0] != 0 and self.plane_y_z[1] != 0:
            y_z = self.map(end_axis[1], self.plane_y_z[0], self.plane_y_z[1], self.plane_y_z[2], self.plane_y_z[3])  
        else:
            y_z = 0
        self.current_z_offset = x_z + y_z                                                  
        calculated = [(end_axis[i] - start_axis[i]) for i in range(3)]                      
        calculated_value = [0, 0, 0]
        calculated_value[0] = calculated[0] + self.current_x_offset - self.last_x_offset      
        calculated_value[1] = calculated[1] + self.current_y_offset - self.last_y_offset      
        calculated_value[2] = calculated[2] + self.current_z_offset - self.last_z_offset      
        fabs_calculated_value = [math.fabs(calculated_value[i]) for i in range(3)]  
        buf_value = fabs_calculated_value.copy()
        buf_value.sort(reverse=True)                                                
        max_value = buf_value[0]                                                   
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
                angle = self.coordinateToAngle(processing_axis[i])                           
                angle1 = [(self.offsetAngle[i] + angle[i]) for i in range(3)]    # Deviation Angle calibration
                self.armDriver.moveStepMotorToTargetAngle(angle1)                 
        self.last_x_offset = self.current_x_offset                                      
        self.last_y_offset = self.current_y_offset                                         
        self.last_z_offset = self.current_z_offset                                        
    
if __name__ == '__main__':
    import os
    import time
    os.system("sudo pigpiod")
    time.sleep(1)
    arm = Arm() 
    arm.setArmEnable(0)
    print(arm.setArmToSensorPoint())
    arm.setArmEnable(1)

   