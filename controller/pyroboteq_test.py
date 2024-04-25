
from PyRoboteq import RoboteqHandler
from PyRoboteq import roboteq_commands as cmds

#sample roboteq commands
controller = RoboteqHandler(debug_mode = True, exit_on_interrupt = False)  # Create the controller object
is_connected = controller.connect("/dev/tty.usbmodemC13E847AFFFF1") # connect to the controller (COM9 is an example for windows)

if (not is_connected):
    raise Exception("Error in connection")

if __name__ == "__main__":
    controller.send_command(cmds.MOTOR_MODE,2,0)
    while True:
        #controller.dual_motor_control(100, 100) # Send command to the controller
        controller.send_command(cmds.DUAL_DRIVE,100,100)
    

 
    #controller.send_command(cmds.REL_EM_STOP) # send this command to release it
        #controller.send_command(cmds.SET_SPEED, 1, 200) # send 'set speed' command to channel 1 (first argument) with the value of up to 1000 RPM (second argument)