import pygame
import threading
import time

"""
Also includes open loop control demo

"""



"""
for some reason doesn't really work well with the joystick stuff as a background thread
"""
class Gamepad:


    def __init__(self):

        self.vertical = 0
        self.horizontal = 0
        self.enable = False

        pygame.init()
        self.joysticks = []

        # for al the connected joysticks
        for i in range(0, pygame.joystick.get_count()):
            # create an Joystick object in our list
            self.joysticks.append(pygame.joystick.Joystick(i))
            # initialize the appended joystick (-1 means last array item)
            self.joysticks[-1].init()
            # print a statement telling what the name of the controller is


        self.lock = threading.Lock()
        self.alive = True
        self.thread = threading.Thread(target=self.listen)
        self.thread.daemon = True
        self.thread.start()

    def __del__(self):
        self.alive = False
        self.thread.join()
            

    def peek(self):
        # self.lock.acquire()
        h, v, e = self.horizontal, self.vertical, self.enable
        # self.lock.release()

        return h, v, e
            

    def listen(self):

        """
        Left joystick:
            horizontal axis is 0, positive is to the right
            vertical axis is 1, positive is down

        todo: encoding might be different for each controller
        todo: maybe have vertical and horizontal on separate joysticks

        """

        while self.alive:
            # self.lock.acquire()
            # self.vertical = 0
            # self.horizontal = 0
            # self.enable = False
            # self.lock.release()

            vert, hori, en = 0, 0, False


            for event in pygame.event.get():

                print('EVENT', event)

                if hasattr(event, 'axis'):


                    if event.axis == 0:
                        hori = float(event.value)
                        # self.horizontal = event.value
                        # if abs(self.horizontal) < 0.1:
                        #     self.horizontal = 0


                    if event.axis == 1:
                        vert = -1 * float(event.value)
                        # self.vertical = -1 * event.value
                        # if abs(self.vertical) < 0.1:
                        #     self.vertical = 0

                    if event.axis == 5:
                        en = abs(float(event.value))


                # # todo: maybe set to a trigger rather than a face button
                # if hasattr(event, "button") and event.button == 0:
                #     self.enable = True
                # else:
                #     self.enable = False
            # self.lock.acquire()
            self.vertical = vert
            self.horizontal = hori
            self.enable = en
            # self.lock.release()

        


#! Open loop demo
# TODO: belts move in a wierd directions


"""
core xy 

delta x = 0.5 * (delta a + delta b)
delta y = 0.5 * (delta a - delta b)

2x = a + b
2y = a - b

means 2x - 2y = 2b --> b = x - y

2x = a + x - y
a = x + y

"""
def xy_to_ab(x, y):
    return x + y, x - y


if __name__ == '__main__':
    from PyRoboteq import RoboteqHandler
    from PyRoboteq import roboteq_commands as cmds

    # for the controlling demo
    # GAMEPAD = Gamepad()
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
            break

    DEAD_ZONE = 0.1

    while connected:

        vert, hori = 0, 0


        for event in pygame.event.get():
            # print('EVENT', event)
            if hasattr(event, 'axis'):

                # left joystick horizontal
                if event.axis == 0:
                    hori = float(event.value)
                    if abs(hori) < DEAD_ZONE:
                        hori = 0
                    

                # left joystick vertical
                if event.axis == 1:
                    vert = -1 * float(event.value)
                    if abs(vert) < DEAD_ZONE:
                        vert = 0
                    

                # right trigger
                if event.axis == 5:

                    enable = True


                # left trigger
                if event.axis == 4:
                    enable = False

        # horizontal, vertical, enable = GAMEPAD.peek()

        a, b = xy_to_ab(hori, vert)

        if enable and hori != 0 and vert != 0:
            print("(hori, vert, en)", hori, vert, enable)
            print('core x y', a, b)


        MOTOR_SHIFT = 1000
        mot1pos = g_motorController.read_value(cmds.READ_ABSCNTR, 1)
        mot2pos = g_motorController.read_value(cmds.READ_ABSCNTR, 2)

        if enable and hori != 0 and vert != 0:
            g_motorController.send_command(cmds.SET_SPEED, MOTOR1, "5000")
            g_motorController.send_command(cmds.SET_ACCEL, MOTOR1, "100000")
            g_motorController.send_command(cmds.SET_SPEED, MOTOR2, "5000")
            g_motorController.send_command(cmds.SET_ACCEL, MOTOR2, "100000")

            # g_motorController.send_command(cmds.SET_SPEED, MOTOR1, f"{a * MOTOR_SPEED}")
            # g_motorController.send_command(cmds.SET_SPEED, MOTOR2, f"{b * MOTOR_SPEED}")

            g_motorController.send_command(cmds.MOT_POS, MOTOR1, f"{a * MOTOR_SHIFT + mot1pos}")
            g_motorController.send_command(cmds.MOT_POS, MOTOR2, f"{b * MOTOR_SHIFT + mot2pos}")
        else:
            g_motorController.send_command(cmds.SET_SPEED, MOTOR1, "0")
            g_motorController.send_command(cmds.SET_ACCEL, MOTOR1, "0")
            g_motorController.send_command(cmds.SET_SPEED, MOTOR2, "0")
            g_motorController.send_command(cmds.SET_ACCEL, MOTOR2, "0")

