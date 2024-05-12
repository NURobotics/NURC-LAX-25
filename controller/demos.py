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

controller.initialization()
print("Initialization Complete!")

# Set initial controller gains
controller.set_motor_modes(MMODE=0) # Closed loop count position
#controller.set_pid_params(kp=20,ki=0,kd=0)
#controller.set_kinematics_params(accel=100,decel=100,max_v=40) # Conservative 


# Input an inital point prolly just the middle of the goal
# P = controller.bottom_right_poss / 2

# print(P)
# Open loop testing scheme
while(True):
	#while (controller.safety_protocol(P)):
	controller.read_enc_values()
	if not controller.safety_protocol(controller.convert_enc_counts_to_posn(controller.M1_abscntr,controller.M2_abscntr)):
		print(f"End effector is outside of safety region! Recorded position: {controller.convert_enc_counts_to_posn(controller.M1_abscntr,controller.M2_abscntr)}")

	print(f'Encoder vals: [{controller.M1_abscntr,controller.M2_abscntr}')


	# Update P


