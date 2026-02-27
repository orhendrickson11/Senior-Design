# robot movement w/ python trigger

import serial
import math
import time
from standardbots import models, StandardBotsRobot

# Configure the serial connection 
#arduino = serial.Serial(port='COM9', baudrate=9600, timeout=1)

#----------------------------------------------------------------------------------------

# create function to write to and read from arduino through serial port

'''
def write_read(x):
    # Send data to Arduino, encoding it into bytes
    arduino.write(bytes(x, 'utf-8'))
    time.sleep(0.1)
    # Read the response from Arduino, decode it, and strip whitespace
    response = arduino.readline().decode().strip()
    return response
    '''

#--------------------------------------------------------------------------------------------

# Set up robot connection over ethernet
sdk = StandardBotsRobot(
  url='http://192.168.110.5:3000',
  token='oetrwf0e-yyquw-8eopsk-z8egwu6g',
  robot_kind=StandardBotsRobot.RobotKind.Live,
)

#----------------------------------------------------------------------------------------------

# ============ Arm motion start from here ============

#------------------------------------------------------------------------------------------------
# Default quaternion
# Quaternion: (1, 0, -1, 0) represents direction towards the groud.
Q_IDENTITY = models.Quaternion(1.0, 0.0, -1.0, 0.0)

# Current segment-fixed orientation (snapshot from robot)
ORIENTATION_SNAPSHOT = Q_IDENTITY

#---------------------------------------------------------------------------------------------------


# Read CURRENT tooltip orientation (quaternion) from robot once,
# store it to ORIENTATION_SNAPSHOT for the next motion segment.
def begin_segment_snapshot_orientation():

    global ORIENTATION_SNAPSHOT

    resp = sdk.movement.position.get_arm_position()

    # SDK compatibility: sometimes payload is in .parsed or .data, or directly on resp
    arm = getattr(resp, "parsed", None) or getattr(resp, "data", None) or resp

    ori = arm.tooltip_position.orientation
    q = ori.quaternion
    print("DEGBUG q type:", type(q))
    print("DEBUG q:", q)
    # Copy to avoid reference issues
    ORIENTATION_SNAPSHOT = models.Quaternion(x=q.x, y=q.y, z=q.z, w=q.w)
    

#-----------------------------------------------------------------------------------------------------

# Function to move tooltip to (x,y,z) in millimeters, orientation fixed.
def move_tooltip_xyz(x_m, y_m, z_m):

    Q_IDENTITY = models.Quaternion(1.0, 0.0, -1.0, 0.0)
    body = models.ArmPositionUpdateRequest(
        kind = models.ArmPositionUpdateRequestKindEnum.TooltipPosition,
        tooltip_position = models.PositionAndOrientation(
            position = models.Position(
                x = float(x_m), y = float(y_m), z = float(z_m),
                unit_kind=models.LinearUnitKind.Millimeters,
            ),
            orientation = models.Orientation(
                kind = models.OrientationKindEnum.Quaternion,
                quaternion = (ORIENTATION_SNAPSHOT),
            ),
        ),
    )
    sdk.movement.position.set_arm_position(body=body).ok()

#------------------------------------------------------------------------------------------------------------
# Set Tooltip rotation tip to a certain position

def set_joint_6(x, y, extra_offset=0.0):

    resp = sdk.movement.position.get_arm_position()
    arm = getattr(resp, "parsed", None) or getattr(resp, "data", None) or resp

    joints = list(arm.joint_rotations)  # tuple -> list (for editing)

    delta = math.atan2(y, x) + float(extra_offset)

    # Using absolute value currently：
    joints[5] = delta
    # Accumulated：joints[5] = joints[5] + delta

    if len(joints) != 6:
        raise ValueError(f"Expected 6 joints, got {len(joints)}: {joints}")

    body = models.ArmPositionUpdateRequest(
        kind=models.ArmPositionUpdateRequestKindEnum.JointRotations,
        joint_rotations=[models.ArmJointRotations(joints=tuple(joints))],
    )

    sdk.movement.position.set_arm_position(body=body).ok()

# Input: nail_point = (x_mm, y_mm, z_mm)
# Runs 5 points as a group: C, L, D, R, U  (i.e., 1,12,13,14,11 style)
# Orientation: snapshot ONCE at start; unchanged during these 5 moves.
def wound_nail(nail_point, dx=30, dy=30):
  #  begin_segment_snapshot_orientation()  # snapshot once per call

    x, y, z = nail_point

    C = (x,      y,      z)       # center (nail)
    L = (x - dx, y,      z)       # left  (12)
    D = (x,      y + dy, z)       # down  (13)
    R = (x + dx, y,      z)       # right (14)
    U = (x,      y - dy, z)       # up    (11)

    move_tooltip_xyz(*C)
    move_tooltip_xyz(*L)
    move_tooltip_xyz(*D)
    move_tooltip_xyz(*R)
    move_tooltip_xyz(*U)
    set_joint_6(x,y)


# function to call communication with arduino
#def speak_to_arduino():
   # time.sleep(2) # Wait for Arduino to initialize after connection
   # print("Connected to Arduino")
    # Send '1' once
   # num = "1" 
   # value = write_read(num)
   # print(f"Arduino responded: {value}")

   # arduino.close() # Close the serial connection

# ============Main: 4 nails rectangle ============
with sdk.connection():
    with sdk.connection():
        wound_nail((500, 360, -200))  # nail 1
        wound_nail((500, 740, -200))  # nail 2
        wound_nail((700, 740, -200))  # nail 3
        wound_nail((700, 360, -200))  # nail 4
        wound_nail((600, 570, -200))  # central point

    #speak_to_arduino()
