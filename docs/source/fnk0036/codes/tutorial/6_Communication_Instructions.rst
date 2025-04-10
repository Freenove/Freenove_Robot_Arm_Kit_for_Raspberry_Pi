##############################################################################
Chapter 6 Communication Instructions
##############################################################################

Formats of Communication Instructions

In the operation of a robotic arm, each command is constructed using a series of command characters and their corresponding parameters. These command characters are delineated by space characters (" ") to distinguish one from another. To signify the conclusion of an instruction, a combination of a carriage return and a line feed ("\r\n") is employed. 

+----------------------------------------+--------------------------+
| Instruction Explanation                | Instructions             |
+========================================+==========================+
| Control the robot arm to return to its | S10 F1\r\n               |
|                                        |                          |
| sensor point.                          |                          |
+----------------------------------------+--------------------------+
| Move the end effector of the robot arm | G0 X0.0 Y200.0 Z75.0\r\n |
|                                        |                          |
| to the coordinates (0, 200, 75).       |                          |
+----------------------------------------+--------------------------+
| Set the RGB light to display in mode 1 | S1 M1 R0 G255 B0\r\n     |
|                                        |                          |
| with the color value (0, 255, 0).      |                          |
+----------------------------------------+--------------------------+

Instructions for Movements
***************************************

The moving instructions consist of two commands, as shown below.

+----------------------------------+--------------------------+
| Instruction Explanations         | Instructions             |
+==================================+==========================+
| Move the robot arm to the target | G0 X0.0 Y200.0 Z75.0\r\n |
|                                  |                          |
| position in 3D space.            |                          |
+----------------------------------+--------------------------+
| Pause the robot arm's movement   | G4 T150\r\n              |
|                                  |                          |
| for x milliseconds.              |                          |
+----------------------------------+--------------------------+

G0 is the instruction to move the robot arm, where XYZ corresponds to the coordinates in the coordinate system.

G4 is used to introduce a delay in the robot arm's operation, with T150 indicating a pause of 150 milliseconds.

Customized Instructions
******************************************

LED Module Instructions
=========================================

S1 indicates the instructions for the LED module. There are 7 modes: OFF, RGB, Following, Blink, Breathing, Rainbow, and Gradient. The last three parameters indicate the red, green and blue color values, ranging from 0 to 255.

+----------------------------------------+----------------------+
| Instruction Explanations               | Instructions         |
+========================================+======================+
| Set the RGB light to display in Mode 1 | S1 M1 R0 G255 B0\r\n |
|                                        |                      |
| with the color green (0,255,0).        |                      |
+----------------------------------------+----------------------+
| Set the RGB light to display in Mode 2 | S1 M2 R255 G0 B0\r\n |
|                                        |                      |
| with the color red (255,0,0).          |                      |
+----------------------------------------+----------------------+
| Set the RGB light to display in Mode 3 | S1 M3 R0 G0 B255\r\n |
|                                        |                      |
| with the color blue (0,0,255).         |                      |
+----------------------------------------+----------------------+
| |Communication00|                                             |
+---------------------------------------------------------------+

.. |Communication00| image:: ../_static/imgs/6_Communication_Instructions/Communication00.png

Buzzer Instructions
======================================

S2 indicates an instruction related to the buzzer. The buzzer used in this robot is a passive buzzer, which operates within a frequency range of 1-4 kHz.

+-------------------------------------------------------+--------------+
| Instruction Explanations                              | Instructions |
+=======================================================+==============+
| Make the buzzer emit a sound at a frequency of 2 kHz. | S2 D2000     |
+-------------------------------------------------------+--------------+
| Turn off the buzzer's sound emission.                 | S2 D0        |
+-------------------------------------------------------+--------------+
| |Communication00|                                                    |
+----------------------------------------------------------------------+

The Ground Clearance Setting Instructions
==================================================

S3 is used to set the height of the robotic arm's base from the ground. This value is set to the height of the padding only when the arm's base is elevated. Typically, when the robotic arm is placed and operates on a horizontal surface, this value is set to 0mm.

+-----------------------------------------------------+--------------+
| Instruction Explanations                            | Instructions |
+=====================================================+==============+
| Set the ground clearance of the robot arm to 0.0mm. | S3 O0.0\r\n  |
+-----------------------------------------------------+--------------+
| |Communication00|                                                  |
+--------------------------------------------------------------------+

End Effector Length Setting Instructions
=================================================

S4 is used to set the length of the end effector of the robot arm. Our robotic arm is equipped with two types of grippers and has different mounting methods. Therefore, it is necessary to configure the gripper's length value according to the actual situation.

+----------------------------------+--------------+
| Instruction Explanations         | Instructions |
+==================================+==============+
| Set the gripper length to 45.0mm | S4 L45.0\r\n |
+----------------------------------+--------------+
| |Communication00|                               |
+-------------------------------------------------+

Home Position Setting Instructions
================================================

S5 is used to set the coordinates of the Home point at the end of the robot arm. XYZ corresponds to the coordinate position in the coordinate system.

+----------------------------------------------------------+--------------------------+
| Instruction Explanations                                 | Instructions             |
+==========================================================+==========================+
| Set the Home position of the robotic arm's end effector. | S5 X0.0 Y200.0 Z75.0\r\n |
+----------------------------------------------------------+--------------------------+
| |Communication00|                                                                   |
+-------------------------------------------------------------------------------------+

Frequency Setting Instructions
===============================================

S6 indicates the instructions for pulse frequency setting. The range of pulse frenqency of this robot arm is 100-16000, and it is set as 1000 by default.

+----------------------------------------+--------------+
| Instruction Explanations               | Instructions |
+========================================+==============+
| 1000Hz Set the pulse frequency for the | S6 Q1000\r\n |
|                                        |              |
| robot arm's stepper motors             |              |
+----------------------------------------+--------------+
| |Communication00|                                     |
+-------------------------------------------------------+

Stepper Motor Microstep Setting Instructions
==============================================

S7 is used to set the microstep resolution of the robotic arm's stepper motor. When the resolution is set to 1, the stepper motor has the maximum torque but the lowest precision. Conversely, when the resolution is set to 5, the stepper motor has the minimum torque but the highest precision. The default resolution is 5.

+--------------------------+--------------+
| Instruction Explanations | Instructions |
+==========================+==============+
| Set the resolution to 5  | S7 W5\r\n    |
+--------------------------+--------------+
| |Communication00|                       |
+-----------------------------------------+

Motor Enable/Diasble Instructions
===============================================

S8 is used to control the power supply to the stepper motor. When powered, the motor generates torque, locking the motor in place. When the power is cut, the motor loses torque, allowing it to rotate freely.

+----------------------------+--------------+
| Instruction Explanations   | Instructions |
+============================+==============+
| Enable the stepper motor.  | S8 E0\r\n    |
+----------------------------+--------------+
| Disable the stepper motor. | S8 E1\r\n    |
+----------------------------+--------------+
| |Communication00|                         |
+-------------------------------------------+

Servo Control Instructions
================================================

S9 is used to control the movement of servos. "Ix" represents the servo index number, which ranges from 0 to 4. "Ax" denotes the angle to which the servo should rotate.

+------------------------------------------+----------------+
| Instruction Explanations                 | Instructions   |
+==========================================+================+
| Control Servo 0 to rotate to 90 degrees  | S9 I0 A90\r\n  |
+------------------------------------------+----------------+
| Control Servo 1 to rotate to 150 degrees | S9 I1 A150\r\n |
+------------------------------------------+----------------+
| |Communication00|                                         |
+-----------------------------------------------------------+

Sensor Calibration Instrutions
================================================

S10 is employed to re-establish the reference coordinate system for the robot arm. Whenever there is an instance of step loss or when a previously disabled motor is reactivated, it is imperative to initiate a sensor calibration command first.

+----------------------------------+--------------+
| Instruction Explanations         | Instructions |
+==================================+==============+
| Recalibrate the sensor center    | S10 F0\r\n   |
|                                  |              |
| position of the robot arm.       |              |
+----------------------------------+--------------+
| Move the robot arm to the center | S10 F1\r\n   |
|                                  |              |
| positon of the sensors.          |              |
+----------------------------------+--------------+
| |Communication00|                               |
+-------------------------------------------------+

Coordinates Calibration Instructions
====================================================

S11 command is designed to assist in calibrating the robotic arm, enhancing its precision and accuracy during operation. There are three calibration commands in total. The robot arm will only perform calibration at a specific point upon receiving a start signal for calibration. If the start signal is not received, the process signal command and the end signal command will have no effect.

This command allows for the calibration of up to five points. The 0th coordinate represents the Home position of the robot arm, while coordinates 1 through 4 correspond to the four points listed on the calibration paper.

+----------------------------------------------+------------------------------+
|           Instruction Explanations           |         Instructions         |
+==============================================+==============================+
| Begin the calibration of the 0th point       | S11 C0\r\n                   |
+----------------------------------------------+------------------------------+
| Control the robot arm to move to the correct | S11 H0 X0.0 Y200.0 Z75.0\r\n |
|                                              |                              |
| positon after calibration                    |                              |
+----------------------------------------------+------------------------------+
| Finish the calibration of the 0th point      | S11 J0 X0.0 Y200.0 Z75.0\r\n |
+----------------------------------------------+------------------------------+
| |Communication00|                                                           |
+-----------------------------------------------------------------------------+

Instructions for Inquring the Motion Command Queue 
====================================================

S12 is utilized to check the number of remaining motion commands that have not yet been executed within the robot arm's control system. 

+-------------------------------------------+------------+
|      Instruction Explanations             |Instructions|
+===========================================+============+
| Start the feedback thread for robot       |S12 K1\r\n  |
|                                           |            |
| arm motion command inquiry.               |            |
+-------------------------------------------+------------+
| Stop the feedback thread for robot        |S11 K0\r\n  |
|                                           |            |
| arm motion command inquiry.               |            |
+-------------------------------------------+------------+
| |Communication00|                                      |
+-------------------------------------------+------------+
| The robotic arm sends a feedback to the   |S12 Kx\r\n  |
|                                           |            |
| App/Software every 0.5 seconds, reporting |            |
|                                           |            |
| the current number of remaining motion    |            |
|                                           |            |
| commands (where 'x' represents the current|            |
|                                           |            |
| number of remaining commands).            |            |
+-------------------------------------------+------------+
| |Communication00|                                      |
+--------------------------------------------------------+

Emergency Stop Insctructions
================================================

S13 is used to shut down the robot arm's threads and motors. It is typically employed in situations where the robotic arm exhibits abnormal motion, such as when it becomes stuck but continues to operate. This scenario can easily lead to damage to the robotic arm. Utilizing this command allows for an emergency stop of the robotic arm and releases the motor torque, thereby protecting the arm from harm.

+-----------------------------+--------------+
| Instruction Explanations    | Instructions |
+-----------------------------+--------------+
| Force shutdown of robot arm | S13 N1\r\n   |
|                             |              |
| threads and motor current   |              |
+-----------------------------+--------------+
| |Communication00|                          |
+--------------------------------------------+