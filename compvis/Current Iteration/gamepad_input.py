import pygame
import threading
import time
from PyRoboteq import RoboteqHandler
from PyRoboteq import roboteq_commands as cmds



"""
core xy 

delta x = 0.5 * (delta a + delta b)
delta y = 0.5 * (delta a - delta b)

2x = a + b
2y = a - b

means 2x - 2y = 2b --> b = x - y
c
2x = a + x - y
a = x + y

"""
def xy_to_ab(x, y):
    return x + y, x - y


def coord_to_command(x, y):
    assert -0.9 <= x <= 0.9, "x must be between -1 and 1"
    assert -0.9 <= y <= 0.9, "y must be between -1 and 1"
    y_top = -120000
    y_bottom = 150000
    x_right = 200000
    x_left = -170000
    xmid = (x_right+x_left)/2
    ymid = (y_top+y_bottom)/2
    delta_X = xmid
    delta_Y = ymid
    if x < 0:
        delta_Y = abs(x) * (x_left-xmid)
    if y > 0:
        delta_X = y * (y_top-ymid)
    if x > 0:
        delta_Y = x * (x_right-xmid)
    if y < 0:
        delta_X = abs(y) * (y_bottom-ymid)
    # print(f"delta x = {delta_X} and delta y = {delta_Y}\n")
    motor1_pos = delta_X + delta_Y
    motor2_pos = delta_X - delta_Y
    coord = [int(motor1_pos), int(motor2_pos)]
    return coord


if __name__ == '__main__':
    


    g_motorController = RoboteqHandler()
    MOTOR2 = "2"
    MOTOR1 = "1"
    

    pygame.init()
    joysticks = []

    # for al the connected joysticks
    for i in range(0, pygame.joystick.get_count()):
        # create an Joystick object in our list
        joysticks.append(pygame.joystick.Joystick(i))
        # initialize the appended joystick (-1 means last array item)
        joysticks[-1].init()
        # print a statement telling what the name of the controller is
        print("Detected joystick ",joysticks[-1].get_name(),"'")



    enable = False

    # connected = True
    connected = False
    for i in range(100):
        connected = g_motorController.connect(F"COM{i}")
        if connected:
            print("Connected to ROBOTEQ\n\n")
            break

    if not connected:
        print("could not connect to roboteq")

    DEAD_ZONE = 0.2

    curr_x = 0
    curr_y = 0

    # change the deceleration rate
    # g_motorController.send_raw_command("!DC 2 200000")
    # g_motorController.send_raw_command("!DC 1 200000")



    while connected:

        vertical, horizontal = 0, 0

        time.sleep(1/120)
        for event in pygame.event.get():

            if hasattr(event, 'button'):

                """
                BUttons:
x  2
a 0
b 1
y 3
                """
                # if event.button == 0


            # print('EVENT', event)
            if hasattr(event, 'axis'):

                # left joystick horizontal is 0




                # right joystick horizontal
                if event.axis == 0:
                    horizontal = float(event.value)
                    if abs(horizontal) < DEAD_ZONE:
                        horizontal = 0
                    

                # left joystick vertical
                if event.axis == 1:
                    vertical = -1 * float(event.value)
                    if abs(vertical) < DEAD_ZONE:
                        vertical = 0
                    

                # right trigger
                if event.axis == 5:
                    print("ENABLE")
                    enable = True
                    g_motorController.send_command(cmds.SET_SPEED, MOTOR1, "3000")
                    g_motorController.send_command(cmds.SET_ACCEL, MOTOR1, "200000") # CHANGED FROM 100K TO 10K
                    g_motorController.send_command(cmds.SET_SPEED, MOTOR2, "3000")
                    g_motorController.send_command(cmds.SET_ACCEL, MOTOR2, "200000")


                # left trigger
                if event.axis == 4:
                    print("DISABLE")
                    enable = False
                    g_motorController.send_command(cmds.SET_SPEED, MOTOR1, "0")
                    g_motorController.send_command(cmds.SET_SPEED, MOTOR2, "0")

        # horizontal, vertical, enable = GAMEPAD.peek()

        a, b = xy_to_ab(horizontal, vertical)

        if enable and (horizontal != 0 or vertical != 0):
            print()
            print("(hori, vert, en)", horizontal, vertical, enable)
            print()


        # MOTOR_SHIFT = 1000
        # mot1pos = g_motorController.read_value(cmds.READ_ABSCNTR, 1)
        # mot2pos = g_motorController.read_value(cmds.READ_ABSCNTR, 2)

        # print("MOtor positions: ", mot1pos, mot2pos)


        # absolute position, no normalization
        # norm = (vertical ** 2 + horizontal ** 2) ** 0.5
        # vertical /= norm if norm != 0 else 1
        # horizontal /= norm if norm != 0 else 1

        


        if enable and (horizontal != 0 or vertical != 0):
            # print(cmds.SET_SPEED, MOTOR1, "5000")
            # print(cmds.SET_ACCEL, MOTOR1, "10000") # CHANGED FROM 100K TO 10K
            # print(cmds.SET_SPEED, MOTOR2, "5000")
            # print(cmds.SET_ACCEL, MOTOR2, "10000")


            # print(cmds.MOT_POS, MOTOR1, f"{a * MOTOR_SHIFT + float(mot1pos[2:])}")
            # print(cmds.MOT_POS, MOTOR2, f"{b * MOTOR_SHIFT + float(mot2pos[2:])}")

            try:

                SCALE = 0.5#1#0.05
                curr_x = curr_x + horizontal * SCALE
                curr_y = curr_y + vertical * SCALE

                # clamp
                curr_x = max(min(curr_x, 0.9), -0.9)
                curr_y = max(min(curr_y, 0.9), -0.9)
                # motpos1, motpos2 = coord_to_command(curr_x, curr_y)



                horizontal = max(min(horizontal, 0.9), -0.9)
                vertical = max(min(vertical, 0.9), -0.9)
                motpos1, motpos2 = coord_to_command(horizontal * SCALE, vertical * SCALE)


                
                g_motorController.send_command(cmds.MOT_POS, MOTOR1, motpos1)
                g_motorController.send_command(cmds.MOT_POS, MOTOR2, motpos2)
            except:
                print()
        else:
            # print(cmds.SET_SPEED, MOTOR1, "0")
            # print(cmds.SET_ACCEL, MOTOR1, "0")
            # print(cmds.SET_SPEED, MOTOR2, "0")
            # print(cmds.SET_ACCEL, MOTOR2, "0")
            # motpos1, motpos2 = coord_to_command(curr_x, curr_y)

            # pos1 = g_motorController.read_value(cmds.READ_ABSCNTR, 1)
            # pos2 = g_motorController.read_value(cmds.READ_ABSCNTR, 2)

            motpos1, motpos2 = coord_to_command(0, 0)
            g_motorController.send_command(cmds.MOT_POS, MOTOR1, motpos1)
            g_motorController.send_command(cmds.MOT_POS, MOTOR2, motpos2)
            # g_motorController.send_command(cmds.MOT_POS, MOTOR1, pos1)
            # g_motorController.send_command(cmds.MOT_POS, MOTOR2, pos2)
            

    print("Ended")
