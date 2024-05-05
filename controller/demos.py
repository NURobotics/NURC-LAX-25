from motor_controller import Controller
from PyRoboteq import roboteq_commands as cmds
from control_gui_helpers import *
#import keyboard
import time
import sys
import os
import numpy as np

#for visual GUI
curr_dir = os.path.dirname(os.getcwd())
new_dir = curr_dir + '\\motor_control\\python_gui\\code'
sys.path.append(new_dir)

#------------------------------------------------#

controller = Controller(debug_mode = False, exit_on_interrupt = False)  # Create the controller object
is_connected = controller.connect("/dev/tty.usbmodemC13E847AFFFF1")

if (not is_connected):
	raise Exception("Error in connection")

#--------------------------#

## Run the initialization script to home the goalie

#controller.initialization()
print("Initialization Complete!")

# Set initial controller gains
controller.set_motor_modes(3)
controller.set_pid_params(kp=20,ki=0,kd=0)
controller.set_kinematics_params(accel=1000,decel=1000,max_v=400)

for i in range(10):
	print("Going to Positon 0")
	controller.send_command(cmds.MOT_POS,1,0)
	controller.send_command(cmds.MOT_POS,2,0)
	time.sleep(2)
	print("Going to Positon 6000")
	controller.send_command(cmds.MOT_POS,1,6000)
	controller.send_command(cmds.MOT_POS,2,6000)
	time.sleep(2)

# Define the limits in real world coordinates in meters
goal_height = 1.92 # meters
goal_width = 2.75 # meters
end_effector_height = 0.331 # meters
end_effector_width = 0.466 # meters

# Input an inital point
P = controller.bottom_right_poss / 2

print(P)
'''
while (controller.safety_protocol(P)):
	print(f'Encoder vals: [{controller.M1_abscntr,controller.M2_abscntr}')


	# Update P


'''