from PyRoboteq import roboteq_commands as cmds
from PyRoboteq.roboteq_handler import RoboteqHandler
import sys

NUM_CONTROLLER = 2
controllers = [RoboteqHandler(), RoboteqHandler()]
controller_stat = [False, False]


MAX_RETRIES = 10
for i in range(MAX_RETRIES):
    controller_stat[0] = controllers[0].connect('/dev/ttyACM0') #chnge to actual motor controller in the future
    if controller_stat[0]:
        break


for i in range(MAX_RETRIES):
    controller_stat[1] = controllers[1].connect('/dev/ttyACM0') #chnge to actual motor controller in the future
    if controller_stat[1]:
        break

if not all(controller_stat):
    print("could not connect to motor controller")
    sys.exit(2)


def move_motors_to_world_position(x, y):
    cmd = f"!P 1 {x} _!P 2 {y} "
    # TODO figure out how to translate world coords into motor coords
    # result = controllers[0].request_handler(cmd)


def motor_set_acceleration(acc):
    pass
    # result = controllers[0].request_handler(cmds.SET_ACCEL + f' {acc}')