
from PyRoboteq.roboteq_handler import RoboteqHandler
from PyRoboteq import roboteq_commands as cmds
import time
import numpy as np

class Controller(RoboteqHandler):
    '''A simple structure to describe the motor controller at a higher level
    than the base capabilities of class RoboteqHandler.

    This class includes:
    - Member data describing current params being read from the Roboteq
    - Functions to handle PID control
    - Functions to convert from real-world space to motor space
    '''

    def __init__(self, exit_on_interrupt = False, debug_mode = False):
        super().__init__(exit_on_interrupt, debug_mode)
        self.pulley_rad = 0.012 #mm; doesn't take into account belt thickness
        self.encoder_cpr = 1250 #counts per revolution
        self.MAGIC_SCALAR = 1.73 #to adjust conversion from encoder counts to real-world posn

        # Goal constants 
        self.goal_height = 1.92 # meters
        self.goal_width = 2.75 # meters
        self.end_effector_height = 0.331 # meters
        self.end_effector_width = 0.466 # meters

        self.safty_factor = 0.95 # percentage of boundary

        self.dwell = 1 # seconds

        

    def read_curr_state(self):
        '''Read all relevant values from the Roboteq at once. Depending on baud rate,
        this may be a time-consuming operation - check later to see if it needs to be 
        optimized.

        Structure of read_value:  command: str = "", parameter = "" (parameter is usually 1 for first value)

        Returns: none; edits member data
        '''
        self.motor_amps   = self.read_value(cmds.READ_MOTOR_AMPS,1)    # Read current motor amperage
        self.battery_amps = self.read_value(cmds.READ_BATTERY_AMPS,1)  # Read battery amps
        self.bl_motor_rpm = self.read_value(cmds.READ_BL_MOTOR_RPM, 1) # Read brushless motor speed in RPM
        self.blrspeed     = self.read_value(cmds.READ_BLRSPEED, 1)     # Read brushless motor speed as 1/100 of max RPM
        self.abscntr      = self.read_value(cmds.READ_ABSCNTR, 1)      # Read encoder counter absolute
        self.blcntr       = self.read_value(cmds.READ_BLCNTR, 1)       # Read absolute brushless counter
        self.peak_amps    = self.read_value(cmds.READ_PEAK_AMPS, 1)    # Read DC/Peak Amps
        self.dreached     = self.read_value(cmds.READ_DREACHED, 1)     # R4ead destination reached
        self.fltflag      = self.read_value(cmds.READ_FLTFLAG, 1)      # Read fault flags
        self.motcmd       = self.read_value(cmds.READ_MOTCMD, 1)       # Read motor command applied
        self.temp         = self.read_value(cmds.READ_TEMP, 1)         # Read controller temperature
        self.volts        = self.read_value(cmds.READ_VOLTS, 1)        # Read voltage measured
    
    def read_enc_values(self):
        # Read value returns a string so must do some string parsing to get the encoder counts as ints
        self.M1_abscntr   = int(self.read_value(cmds.READ_ABSCNTR, 1)[2:])      # Read encoder counter absolute & turn string into int
        self.M2_abscntr   = int(self.read_value(cmds.READ_ABSCNTR, 2)[2:])      # Read encoder counter absolute & turn string into int

    def set_motor_modes(self,MMODE):
        """
        Inputs:
        Inputs int MMODE in  [0,3]

        Sets both roboteq motors to MMODE
        """
        Mdict = {0:"Open Loop",
                 1:"???",
                 2:"???",
                 3:"Closed Loop Absolute Encoder Position Mode"}
        
        print(f'Attempting to set Motor Modes to: {Mdict[MMODE]}')
        self.send_command(cmds.MOTOR_MODE, 1, MMODE)
        self.send_command(cmds.MOTOR_MODE, 2, MMODE)

        # Rest for the dwell time
        time.sleep(self.dwell)

        # Check the modes
        if int(self.read_value(cmds.READ_MMODE,1)[-1]) != MMODE and int(self.read_value(cmds.READ_MMODE,2)[-1]) != MMODE:
            raise Exception(f'Motor 1 Mode: {self.read_value(cmds.READ_MMODE,1)}\tMotor 2 Mode: {self.read_value(cmds.READ_MMODE,2)}')
        else:
            print(f'Motor modes sucessfully set to {Mdict[MMODE]}')

        
    
    def send_position_command(self, P):
        """
        Inputs a position P : [x,y] in the goal frame and sends that position to the motors:
        """
        enc1,enc2 = self.convert_worldspace_to_encoder_cts(P[0],P[1])
        # Send the encoder counts to the roboteq
        self.send_command(cmds.MOT_POS,1,enc1)
        self.send_command(cmds.MOT_POS,2,enc2)
        print("Position Sent!")

    def convert_worldspace_to_encoder_cts(self, delta_x, delta_y):
        '''Documentation
        '''
        delta_x, delta_y = delta_x / self.MAGIC_SCALAR, delta_y / self.MAGIC_SCALAR

        #use corexy principles to find change in motor linear positions.
        #will need to adjust what "m1" and "m2" are defined as later
        delta_m1_lin =  delta_x - delta_y
        delta_m2_lin = -delta_x - delta_y

        #use x = r*theta to find angular change in motor
        delta_m1 = delta_m1_lin / self.pulley_rad
        delta_m2 = delta_m2_lin / self.pulley_rad
        encoder_cts_1 = delta_m1 * self.encoder_cpr
        encoder_cts_2 = delta_m2 * self.encoder_cpr

        return np.array([encoder_cts_1, encoder_cts_2])


    def convert_enc_counts_to_posn(self, enc_count1, enc_count2):
        '''Takes counts of the encoders, and converts them into positions in x 
        and y in the real world. Uses the inverse of the coreXY transform.

        Returns: (x, y) - positions in real world
        '''

        dtheta_1 = enc_count1 / self.encoder_cpr
        dtheta_2 = enc_count2 / self.encoder_cpr

        dM1 = self.pulley_rad * dtheta_1
        dM2 = self.pulley_rad * dtheta_2

        dx = -0.5*(dM2 - dM1)
        dy = -0.5*(dM1 + dM2)
        dx, dy = self.MAGIC_SCALAR * dx, self.MAGIC_SCALAR * dy

        #assume initial position is at 0, so dx = x and dy = y
        return np.array([dx, dy])
        
    def set_pid_params(self, kp, ki, kd):
        '''Sets gains for PID control all at once.'''
        print("Attempting to set PID parameters...")
        self.send_command(cmds.KP,1, kp)
        self.send_command(cmds.KD,1, kd)
        self.send_command(cmds.KI,1, ki)

        self.send_command(cmds.KP, 2, kp)
        self.send_command(cmds.KD, 2, kd)
        self.send_command(cmds.KI, 2, ki)

        # Rest for a sec
        time.sleep(self.dwell)

        if ((int(self.read_value(cmds.READ_KP, 1)[3:]) != kp) or (int(self.read_value(cmds.READ_KP, 2)[3:]) != kp)):
            raise Exception(f'Kp PID Parameter failed!')
        elif((int(self.read_value(cmds.READ_KI, 1)[3:])!=ki) or (int(self.read_value(cmds.READ_KI, 2)[3:])!=ki)):
            raise Exception(f'Ki PID Parameter failed!')
        elif((int(self.read_value(cmds.READ_KD, 1)[3:])!=kd)or(int(self.read_value(cmds.READ_KD, 2)[3:])!=kd)):
            raise Exception(f'Kd PID Parameter failed!')
        else:
            print("PID Parameters Set!")

        

    def set_kinematics_params(self, accel, decel, max_v):
        #accel, decel, max velocity, rpms at max speed
        print("Attempting to set kinematic parameters...")
        self.send_command(cmds.CL_MAX_ACCEL, 1, accel)
        self.send_command(cmds.CL_MAX_DECEL, 1, decel)
        self.send_command(cmds.CL_MAX_VEL, 1, max_v)

        self.send_command(cmds.CL_MAX_ACCEL, 2, accel)
        self.send_command(cmds.CL_MAX_DECEL, 2, decel)
        self.send_command(cmds.CL_MAX_VEL, 2, max_v)

        # Rest for a sec
        time.sleep(self.dwell)

        if ((int(self.read_value(cmds.READ_MVEL,1)[5:])!=max_v) or (int(self.read_value(cmds.READ_MVEL,2)[5:]) != max_v)):
            raise Exception(f'Max velocity not set!')
        elif((int(self.read_value(cmds.READ_MAC,1)[4:])!=accel) or (int(self.read_value(cmds.READ_MAC,2)[4:])!=accel)):
            raise Exception(f'Max acceleration not set!')
        elif((int(self.read_value(cmds.READ_MDEC,1)[5:])!=decel)or(int(self.read_value(cmds.READ_MDEC,2)[5:])!=decel)):
            raise Exception(f'Max deceleration not set!')
        else:
            print("Kinematic Parameters Set!")              

    def read_PID(self):

        self.read_value(cmds.READ_KP, 1)
        self.read_value(cmds.READ_KI, 1)
        self.read_value(cmds.READ_KD, 1)

        self.read_value(cmds.READ_KP, 2)
        self.read_value(cmds.READ_KI, 2)
        self.read_value(cmds.READ_KD, 2)

    def initialization(self):
        # Set the (0,0) position of the goal in the top left corner of the goal
        # Set the motor mode to open loop 
        self.set_motor_modes(MMODE=0)

        # Wait until a button is pressed to set the encoders 0 positions
        user_input = input("Move end effector to the top left position of the gantry as seen from a thrower's perspective.\nPress any key to set position")
        self.send_command(cmds.SET_ENC_COUNTER, 1, 0) #first motor; set encoder to zero
        self.send_command(cmds.SET_ENC_COUNTER, 2, 0) #second motor; set encoder to zero
        time.sleep(self.dwell)
        print(f"Home has been set at {[self.read_value(cmds.READ_ABSCNTR, 1),self.read_value(cmds.READ_ABSCNTR, 2)]}!")

        # Move to the next position and record the encoder counts
        user_input = input("Move end effector to the bottom right of the gantry as seen from the throwers perspective.\nPress any key to set postition")
        self.read_enc_values()
        self.bottom_right_encs = [self.M1_abscntr,self.M2_abscntr]
        self.bottom_right_poss = self.convert_enc_counts_to_posn(self.bottom_right_encs[0],self.bottom_right_encs[1])
        time.sleep(self.dwell)
        print(f'Encoder values set as {self.bottom_right_encs}\nPostion set at {self.bottom_right_poss}')
        print(f'The goal is actually {self.goal_width,self.goal_height} meters. Does this align with above??')
        self.convert_worldspace_to_encoder_cts()

    def calculate_bounds(self):
        """
        Function to compute the acceptable bounds for the system
        From initialization sequence, origin is at the top left of the goal
        Really important to check this as safety protocol depends on this being correct
        """ 
    
        self.horizontal_bounds = [0 + self.bottom_right_poss[0]*(1-self.safty_factor), self.bottom_right_poss[0]-self.bottom_right_poss[0]*(1-self.safty_factor)]
        self.vertical_bounds = [0 + self.bottom_right_poss[1]*(1-self.safty_factor), self.bottom_right_poss[1]-self.bottom_right_poss[1]*(1-self.safty_factor) ]
        print(f'Horizontal bounds: {self.horizontal_bounds}')
        print(f'Vertical Bounds: {self.vertical_bounds}')
        print(f'System bounds set to {self.safty_factor} of full range of motion!')

    def safety_protocol(self,commanded_point):
        # The commanded point (x,y) is run through this function. It will check with the bounds of the goal to ensure that it will not come into contact with the goal frame.
        # The (0,0) position is the top center of the goal frame
        x,y = commanded_point

        in_safe_zone = True
        if (self.horizontal_bounds[0]>x>self.horizontal_bounds[1]):
            in_safe_zone = False
        
        if (self.vertical_bounds[0]>y>self.vertical_bounds[1]):
            in_safe_zone = False

        return in_safe_zone
    
    
    def traverse_the_boundary(self):
        """
        Function will travel along the safety boundary
        """
        
        self.set_motor_modes(MMODE=3) # Ensure motor mode is in closed loop
        self.set_kinematics_params(accel=100,decel=100,max_v=40) # Conservative to start
        self.set_pid_params(kp=2,ki=0,kd=0)
        print("Attempting to traverse the safety boundary")

        self.send_position_command([self.horizontal_bounds[0],self.vertical_bounds[0]])
        time.sleep(10)
        self.send_position_command([self.horizontal_bounds[1],self.vertical_bounds[0]])
        time.sleep(10)
        self.send_position_command([self.horizontal_bounds[1],self.vertical_bounds[1]])
        time.sleep(10)
        self.send_position_command([self.horizontal_bounds[0],self.vertical_bounds[1]])
    #init_coords = (0,0) #change based on actual posns read by encoders
    #deltax, deltay = [coord[i] - init_coords[i] for i in range(len(coord))]
    
    ##use corexy principles to find change in motor linear positions.
    ##will need to adjust what "m1" and "m2" are defined as later
    #delta_m1_lin = delta_y + delta_x
    #delta_m2_lin = delta_y - delta_x

    ##use x = r*theta to find angular change in motor
    #delta_m1 = delta_m1_lin / pulley_rad
    #delta_m2 = delta_m2_lin / pulley_rad

    #return (delta_m1, delta_m2)

    #def gen_array_speed_cmds():
    #    #check if position can be controlled by roboteq before doing this
    #    pass
