import math
import serial
import time
from standardbots import models, StandardBotsRobot

# ==================== Arduino Connection ===============
# arduino = serial.Serial('COM3', 9600)  

def write_read(x):
    # Send data to Arduino, encoding it into bytes
    arduino.write(bytes(x, 'utf-8'))
    time.sleep(0.1)
    # Read the response from Arduino, decode it, and strip whitespace
    response = arduino.readline().decode().strip()
    return response

def speak_to_arduino():
    time.sleep(2) # Wait for Arduino to initialize after connection
    print("Connected to Arduino")
    # Send '1' once
    num = "1" 
    value = write_read(num)
    print(f"Arduino responded: {value}")

    arduino.close() # Close the serial connection


# ================= Robot Connection =================
# Set up robot connection over ethernet
# Set up robot connection over ethernet
sdk = StandardBotsRobot(
    url='http://192.168.110.5:3000',
    # ⬆ used at lab
    # url = 'https://lobsimn1.sb.app',
    # ⬆ connect to local simulator
    token='oetrwf0e-yyquw-8eopsk-z8egwu6g',
    # ⬆ used at lab
    # token = '4k4m-5luub4f4-1n203z6-46hxtg',
    # ⬆ connect to simulator
    robot_kind=StandardBotsRobot.RobotKind.Live,
)

# ================= Global States =================
ORIENTATION_SNAPSHOT =  models.Quaternion(1.0, 0.0, -1.0, 0.0)

# Current orientation (used for true task-space control)
CURRENT_ORIENTATION = models.Quaternion(1.0, 0.0, -1.0, 0.0)

# spin control 
CURRENT_SPIN_DEG = 0.0


# ================= Quaternion Utilities =================
def quaternion_multiply(q1, q2):
    """
    Multiply two quaternions (q1 ⊗ q2)
    Used for LOCAL rotation (tool frame)
    """
    return models.Quaternion(
        x=q1.w*q2.x + q1.x*q2.w + q1.y*q2.z - q1.z*q2.y,
        y=q1.w*q2.y - q1.x*q2.z + q1.y*q2.w + q1.z*q2.x,
        z=q1.w*q2.z + q1.x*q2.y - q1.y*q2.x + q1.z*q2.w,
        w=q1.w*q2.w - q1.x*q2.x - q1.y*q2.y - q1.z*q2.z
    )


def quaternion_from_axis_angle(axis, angle_rad):
    """
    Create quaternion from axis-angle (axis must be normalized)
    """
    s = math.sin(angle_rad / 2.0)
    return models.Quaternion(
        x=axis[0] * s,
        y=axis[1] * s,
        z=axis[2] * s,
        w=math.cos(angle_rad / 2.0)
    )


# ================= Oritation Generation =================
def get_downward_drill_orientation(spin_deg):
    q_base = quaternion_from_axis_angle((0, 1, 0), math.radians(90))
    q_spin = quaternion_from_axis_angle((1, 0, 0), math.radians(spin_deg))
    return quaternion_multiply(q_base, q_spin)


# ================= Snapshot Function =================
def begin_segment_snapshot_orientation():
    """
    Save current tooltip orientation (task-space only)
    """

    global ORIENTATION_SNAPSHOT
    global CURRENT_ORIENTATION

    resp = sdk.movement.position.get_arm_position()
    arm = getattr(resp, "parsed", None) or getattr(resp, "data", None) or resp

    ori = arm.tooltip_position.orientation
    q = ori.quaternion
    ORIENTATION_SNAPSHOT = models.Quaternion(x=q.x, y=q.y, z=q.z, w=q.w)

    CURRENT_ORIENTATION = models.Quaternion(x=q.x, y=q.y, z=q.z, w=q.w)

    print("[Snapshot] Orientation captured")


# ================= Move Function =================
def move_tooltip_xyz(x_m, y_m, z_m):
    """
    Move tooltip using IK (position + fixed orientation)
    """

    body = models.ArmPositionUpdateRequest(
        kind=models.ArmPositionUpdateRequestKindEnum.TooltipPosition,
        tooltip_position=models.PositionAndOrientation(
            position=models.Position(
                x=float(x_m),
                y=float(y_m),
                z=float(z_m),
                unit_kind=models.LinearUnitKind.Millimeters,
            ),
            orientation=models.Orientation(
                kind=models.OrientationKindEnum.Quaternion,
                quaternion=get_downward_drill_orientation(CURRENT_SPIN_DEG),
            ),
        ),
    )

    q = get_downward_drill_orientation(CURRENT_SPIN_DEG)
    print("spin =", CURRENT_SPIN_DEG, "-> q =", q)

    sdk.movement.position.set_arm_position(body=body).ok()


# ================= Nail Motion =================
def wound_nail(nail_point, dx=30, dy=30, delta_deg=0):
    """
    Execute cross pattern around a nail
    """

    begin_segment_snapshot_orientation()

    x, y, z = nail_point

    C = (x,      y,      z)
    L = (x - dx, y,      z)
    D = (x,      y + dy, z)
    R = (x + dx, y,      z)
    U = (x,      y - dy, z)

    move_tooltip_xyz(*U)
    move_tooltip_xyz(*L)
    move_tooltip_xyz(*D)
    move_tooltip_xyz(*R)
    move_tooltip_xyz(*U)
    move_tooltip_xyz(*L)
    move_tooltip_xyz(*D)
    move_tooltip_xyz(*R)
    move_tooltip_xyz(*U)
    move_tooltip_xyz(*L)
    move_tooltip_xyz(*D)


# ================= Main =================
with sdk.connection():

    # Wound the 1st nail
    wound_nail((100, 350, -15))
    #Outer loop
    move_tooltip_xyz(200, 196, -15)
    move_tooltip_xyz(700, 196, -15)
    move_tooltip_xyz(700, 540, -15)
    move_tooltip_xyz(600, 680, -15)
    move_tooltip_xyz(0, 740, -15)
    move_tooltip_xyz(0, 340, -15)

    # Wound the 1st nail again
    wound_nail((100, 350, -25))    
    
    #Inner loop
    move_tooltip_xyz(0, 270, -15)
    move_tooltip_xyz(480, 270, -15)
    move_tooltip_xyz(480, 570, -15)
    move_tooltip_xyz(200, 690, -15)
    move_tooltip_xyz(120, 540, -15)
    move_tooltip_xyz(120, 330, -15)
    move_tooltip_xyz(320, 330, -0)

    '''
    Orientation is controled by
    ABSOLUTE POSITION
    Not relevent position--- BE CAREFUL
    '''

    #this will initiate a wind  
    # speak_to_arduino()  
