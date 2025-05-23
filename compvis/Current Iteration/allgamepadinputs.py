# from inputs import get_gamepad
# from inputs import devices



# def main():

#     for device in devices:
#         print(device)

#     """Just print out some event infomation when the gamepad is used."""
#     while True:
#         try:
#             events = get_gamepad()
#             for event in events:
#                 print(event.ev_type, event.code, event.state)
#         except:
#             # print("not found")
#             pass


# if __name__ == "__main__":
#     main()

import time
# import hid
import pygame
import sys
# for device in hid.enumerate():
#    print(f"0x{device['vendor_id']:04x}:0x{device['product_id']:04x} {device['product_string']}")
# sys.exit(0)

pygame.init()
joysticks = []
clock = pygame.time.Clock()
keepPlaying = True


"""
Left joystick:
    horizontal axis is 0, positive is to the right
    vertical axis is 1, positive is down

    

BUttons:
x  2
a 0
b 1
y 3
"""


# for al the connected joysticks
for i in range(0, pygame.joystick.get_count()):
    # create an Joystick object in our list
    joysticks.append(pygame.joystick.Joystick(i))
    # initialize the appended joystick (-1 means last array item)
    joysticks[-1].init()
    # print a statement telling what the name of the controller is
    print("Detected joystick ",joysticks[-1].get_name(),"'")


while keepPlaying:
    # clock.tick(60)

    # print(pygame.key.get_pressed())
    for event in pygame.event.get():
        # The 0 button is the 'a' button, 1 is the 'b' button, 2 is the 'x' button, 3 is the 'y' button
        # if event.button == 0:
        #     print ("A Has Been Pressed")
        if hasattr(event, 'button'):# and event.axis == 2:
            print(event)
            #  print(pygame.key.get_pressed(), '\n\n')

        # print(event)

# from inputs import get_gamepad
# import math
# import threading

# class XboxController(object):
#     MAX_TRIG_VAL = math.pow(2, 8)
#     MAX_JOY_VAL = math.pow(2, 15)

#     def __init__(self):

#         self.LeftJoystickY = 0
#         self.LeftJoystickX = 0
#         self.RightJoystickY = 0
#         self.RightJoystickX = 0
#         self.LeftTrigger = 0
#         self.RightTrigger = 0
#         self.LeftBumper = 0
#         self.RightBumper = 0
#         self.A = 0
#         self.X = 0
#         self.Y = 0
#         self.B = 0
#         self.LeftThumb = 0
#         self.RightThumb = 0
#         self.Back = 0
#         self.Start = 0
#         self.LeftDPad = 0
#         self.RightDPad = 0
#         self.UpDPad = 0
#         self.DownDPad = 0

#         self._monitor_thread = threading.Thread(target=self._monitor_controller, args=())
#         self._monitor_thread.daemon = True
#         self._monitor_thread.start()


#     def read(self): # return the buttons/triggers that you care about in this methode
#         x = self.LeftJoystickX
#         y = self.LeftJoystickY
#         a = self.A
#         b = self.X # b=1, x=2
#         rb = self.RightBumper
#         return [x, y, a, b, rb]


#     def _monitor_controller(self):
#         while True:
#             events = get_gamepad()
#             for event in events:
#                 if event.code == 'ABS_Y':
#                     self.LeftJoystickY = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
#                 elif event.code == 'ABS_X':
#                     self.LeftJoystickX = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
#                 elif event.code == 'ABS_RY':
#                     self.RightJoystickY = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
#                 elif event.code == 'ABS_RX':
#                     self.RightJoystickX = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
#                 elif event.code == 'ABS_Z':
#                     self.LeftTrigger = event.state / XboxController.MAX_TRIG_VAL # normalize between 0 and 1
#                 elif event.code == 'ABS_RZ':
#                     self.RightTrigger = event.state / XboxController.MAX_TRIG_VAL # normalize between 0 and 1
#                 elif event.code == 'BTN_TL':
#                     self.LeftBumper = event.state
#                 elif event.code == 'BTN_TR':
#                     self.RightBumper = event.state
#                 elif event.code == 'BTN_SOUTH':
#                     self.A = event.state
#                 elif event.code == 'BTN_NORTH':
#                     self.Y = event.state #previously switched with X
#                 elif event.code == 'BTN_WEST':
#                     self.X = event.state #previously switched with Y
#                 elif event.code == 'BTN_EAST':
#                     self.B = event.state
#                 elif event.code == 'BTN_THUMBL':
#                     self.LeftThumb = event.state
#                 elif event.code == 'BTN_THUMBR':
#                     self.RightThumb = event.state
#                 elif event.code == 'BTN_SELECT':
#                     self.Back = event.state
#                 elif event.code == 'BTN_START':
#                     self.Start = event.state
#                 elif event.code == 'BTN_TRIGGER_HAPPY1':
#                     self.LeftDPad = event.state
#                 elif event.code == 'BTN_TRIGGER_HAPPY2':
#                     self.RightDPad = event.state
#                 elif event.code == 'BTN_TRIGGER_HAPPY3':
#                     self.UpDPad = event.state
#                 elif event.code == 'BTN_TRIGGER_HAPPY4':
#                     self.DownDPad = event.state




# if __name__ == '__main__':
#     joy = XboxController()
#     while True:
#         print(joy.read())



"""
Also includes open loop control demo

"""



"""
for some reason doesn't really work well with the joystick stuff as a background thread
"""
# class Gamepad:


#     def __init__(self):

#         self.vertical = 0
#         self.horizontal = 0
#         self.enable = False

#         pygame.init()
#         self.joysticks = []

#         # for al the connected joysticks
#         for i in range(0, pygame.joystick.get_count()):
#             # create an Joystick object in our list
#             self.joysticks.append(pygame.joystick.Joystick(i))
#             # initialize the appended joystick (-1 means last array item)
#             self.joysticks[-1].init()
#             # print a statement telling what the name of the controller is


#         self.lock = threading.Lock()
#         self.alive = True
#         self.thread = threading.Thread(target=self.listen)
#         self.thread.daemon = True
#         self.thread.start()

#     def __del__(self):
#         self.alive = False
#         self.thread.join()
            

#     def peek(self):
#         # self.lock.acquire()
#         h, v, e = self.horizontal, self.vertical, self.enable
#         # self.lock.release()

#         return h, v, e
            

#     def listen(self):

#         """
#         Left joystick:
#             horizontal axis is 0, positive is to the right
#             vertical axis is 1, positive is down

#         todo: encoding might be different for each controller
#         todo: maybe have vertical and horizontal on separate joysticks

#         """

#         while self.alive:
#             # self.lock.acquire()
#             # self.vertical = 0
#             # self.horizontal = 0
#             # self.enable = False
#             # self.lock.release()

#             vert, hori, en = 0, 0, False


#             for event in pygame.event.get():

#                 print('EVENT', event)

#                 if hasattr(event, 'axis'):


#                     if event.axis == 0:
#                         hori = float(event.value)
#                         # self.horizontal = event.value
#                         # if abs(self.horizontal) < 0.1:
#                         #     self.horizontal = 0


#                     if event.axis == 1:
#                         vert = -1 * float(event.value)
#                         # self.vertical = -1 * event.value
#                         # if abs(self.vertical) < 0.1:
#                         #     self.vertical = 0

#                     if event.axis == 5:
#                         en = abs(float(event.value))


#                 # # todo: maybe set to a trigger rather than a face button
#                 # if hasattr(event, "button") and event.button == 0:
#                 #     self.enable = True
#                 # else:
#                 #     self.enable = False
#             # self.lock.acquire()
#             self.vertical = vert
#             self.horizontal = hori
#             self.enable = en
#             # self.lock.release()

        


# #! Open loop demo
# # TODO: belts move in a wierd directions