import math
import serial
import time
from standardbots import models, StandardBotsRobot

# ================= Robot Connection =================
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

# ==================== Arduino Connection ===============
arduino = serial.Serial('COM5', 9600)  

def write_read(x):
    # Send data to Arduino, encoding it into bytes
    arduino.write(bytes(x, 'utf-8'))
    time.sleep(0.1)
    # Read the response from Arduino, decode it, and strip whitespace
    response = arduino.readline().decode().strip()
    return response

def speak_to_arduino1():
    time.sleep(2) # Wait for Arduino to initialize after connection
    print("Connected to Arduino")
    # Send '1' once
    num = "1" 
    value = write_read(num)
   # print(f"Arduino responded: {value}")

    #arduino.close() # Close the serial connection

def speak_to_arduino2():
    time.sleep(2) # Wait for Arduino to initialize after connection
    print("Connected to Arduino")
    # Send '1' once
    num = "2" 
    value = write_read(num)
    print(f"Arduino responded: {value}")

    #arduino.close() # Close the serial connection


# ================= Global States =================
# Current orientation 
CURRENT_ORIENTATION = models.Quaternion(1.0, 0.0, -1.0, 0.0)


# ================= Quaternion Utilities =================
def quaternion_multiply(q1, q2):
    '''
    Multiply two quaternions (q1 ⊗ q2)
    Used for LOCAL rotation (tool frame)
    '''
    return models.Quaternion(
        x=q1.w*q2.x + q1.x*q2.w + q1.y*q2.z - q1.z*q2.y,
        y=q1.w*q2.y - q1.x*q2.z + q1.y*q2.w + q1.z*q2.x,
        z=q1.w*q2.z + q1.x*q2.y - q1.y*q2.x + q1.z*q2.w,
        w=q1.w*q2.w - q1.x*q2.x - q1.y*q2.y - q1.z*q2.z
    )


def quaternion_from_axis_angle(axis, angle_rad):
    s = math.sin(angle_rad / 2.0)
    return models.Quaternion(
        x=axis[0] * s,
        y=axis[1] * s,
        z=axis[2] * s,
        w=math.cos(angle_rad / 2.0)
    )

    '''
    Create quaternion from axis-angle (axis must be normalized)
    Axis is a unit vector

    Ex:
    Rotate the tool 90° around the Z-axis:
        axis = (0, 0, 1)
        angle = π/2

    Get:
        s = sin(π/4) = 0.707
        w = cos(π/4) = 0.707

    Output (Quaternions):
        q = (0, 0, 0.707, 0.707)
        
    '''

# ================= Oritation Generation (Head Down + Self-Rotation) =================
'''
    Initial: Roll = 0°, Pitch = 90°, Yaw = 0°
    Positive rotation angles are determined by the right-hand rule:
        Grasp the shaft with your right hand.
        Point your thumb in the positive direction of the shaft (pointing the ground).
        The direction in which your four fingers curl corresponds to the positive direction of rotation.
'''
def get_downward_drill_orientation(spin_deg):
    q_base = quaternion_from_axis_angle((0, 1, 0), math.radians(90))
    q_spin = quaternion_from_axis_angle((1, 0, 0), math.radians(spin_deg))
    return quaternion_multiply(q_base, q_spin)


# ================= Move Function=================
def move_tooltip_xyz(x_m, y_m, z_m):
    """
     Move tooltip using IK (position + fixed orientation)
    """

    global CURRENT_SPIN_DEG

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

# This function let the tooltip move to a traget point with a defined rotation angle
def move_with_agnle(target_point, spin_deg):
    """
    target_point: (x, y, z_work)
    safe_point:   (x, y, z_safe)  
    """

    global CURRENT_SPIN_DEG

    target_x, target_y, target_z = target_point

    # --- Step 1: set orientation ---
    CURRENT_SPIN_DEG = spin_deg
    # print(f"[WEAVE] Spin = {spin_deg}")

    # --- Step 2: move to target ---
    # print(f"[WEAVE] Move to target ({target_x}, {target_y}, {target_z})")
    move_tooltip_xyz(target_x, target_y, target_z)
    

# ---- Testing New orientation ----
# This two functions are used to cover more orientations (Are not used in our current process)
# Only need to adjust the unit vector below:
# q_base = quaternion_from_axis_angle((0, 1, 0), math.radians(90))
'''
def move_tooltip(x_m, y_m, z_m):
    
    global CURRENT_SPIN_DEG

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
                quaternion=get_orientation(CURRENT_SPIN_DEG), # NEW UPDATES HERE
            ),
        ),
    )
    q = get_downward_drill_orientation(CURRENT_SPIN_DEG)
    print("spin =", CURRENT_SPIN_DEG, "-> q =", q)

    sdk.movement.position.set_arm_position(body=body).ok()

def get_orientation(spin_deg):
    q_base = quaternion_from_axis_angle((0, 1, 0), math.radians(90))
    q_spin = quaternion_from_axis_angle((1, 0, 0), math.radians(90))
    return quaternion_multiply(q_base, q_spin)
'''


# ================= Nail Motion =================
def wound_nail(nail_point, dx=30, dy=30, delta_deg=0):
    """
    Execute cross pattern around a nail, then rotate joint6
    """

    x, y, z = nail_point

    C = (x,      y,      z)
    R = (x - dx, y,      z)
    D = (x,      y + dy, z)
    L = (x + dx, y,      z)
    U = (x,      y - dy, z)

    # ---- Step 2: IK Motion ----
    move_tooltip_xyz(*U)
    move_tooltip_xyz(*L)
    move_tooltip_xyz(*D)
    move_tooltip_xyz(*R)
    move_tooltip_xyz(*U)
    move_tooltip_xyz(*L)
    move_tooltip_xyz(*D)

# Same as wound_nail(), but this function only loop once
def wound_nail_less_loop(nail_point, dx=30, dy=30, delta_deg=0):
    """
    Execute cross pattern around a nail, then rotate joint6
    """

    x, y, z = nail_point

    C = (x,      y,      z)
    R = (x - dx, y,      z)
    D = (x,      y + dy, z)
    L = (x + dx, y,      z)
    U = (x,      y - dy, z)

    # ---- Step 2: IK Motion (joint6 allowed to drift) ----
    move_tooltip_xyz(*U)
    move_tooltip_xyz(*L)
    move_tooltip_xyz(*D)
    move_tooltip_xyz(*R)
    move_tooltip_xyz(*U)





# ================= Weave =================
def weave(target_point, safe_point, spin_deg):
    """
    target_point: (x, y, z_work)
    safe_point:   (x, y, z_safe)  
    """

    global CURRENT_SPIN_DEG

    target_x, target_y, target_z = target_point
    safe_x, safe_y, safe_z = safe_point

    # --- Step 1: set orientation ---
    CURRENT_SPIN_DEG = spin_deg
    # print(f"[WEAVE] Spin = {spin_deg}")

    # --- Step 2: move to safe point ---
    # print(f"[WEAVE] Move to safe ({safe_x}, {safe_y}, {safe_z})\n")
    move_tooltip_xyz(safe_x, safe_y, safe_z)

    # --- Step 3: move down to target ---
    # print(f"[WEAVE] Move to target ({target_x}, {target_y}, {target_z})")
    move_tooltip_xyz(target_x, target_y, target_z)

    # --- Step 4: Motor Rotation:
    speak_to_arduino1()

    # --- Step 5: move back to safe point ---
    # print(f"[WEAVE] Move to safe ({safe_x}, {safe_y}, {safe_z})\n")
    move_tooltip_xyz(safe_x, safe_y, safe_z)


# ================= Main =================
with sdk.connection():
    # Outer circuit
    move_tooltip_xyz(185, 465, 85)
    wound_nail((185, 465, 85))
    move_tooltip_xyz(285, 311, 75)
    move_tooltip_xyz(725, 311, 75)
    move_tooltip_xyz(735, 635, 85)
    move_tooltip_xyz(405, 890, 75)
    move_tooltip_xyz(85, 855, 75)
    move_tooltip_xyz(85, 455, 65)
    wound_nail((185, 465, 75))
    wound_nail_less_loop((330, 465, 80))
    
    #Inner loop
    move_tooltip_xyz(565, 385, 85)
    move_tooltip_xyz(565, 685, 75)
    move_tooltip_xyz(285, 785, 74)
    move_tooltip_xyz(205, 655, 77)
    move_tooltip_xyz(205, 445, 82)
    wound_nail_less_loop((330, 465, 85))
    
    #Weaving
    weave((380, 486, 55), (380, 486, 105), 205)
    weave((500, 410, 55), (500, 410, 105), 180)
    weave((480, 530, 55), (480, 530, 105), 150)
    weave((606, 500, 55), (606, 500, 105), 115)
    weave((520, 630, 55), (520, 630, 105), 90)    
    weave((495, 780, 55), (495, 780, 105), 60)    
    weave((415, 720, 55), (415, 720, 105), 25)
    weave((345, 805, 40), (345, 805, 105), 0)
    weave((325, 685, 40), (325, 685, 105), 330)
    weave((191, 585, 40), (191, 585, 105), 290)
    weave((295, 575, 50), (295, 575, 105), 260)
    weave((265, 450, 30), (265, 450, 105), 240)
    wound_nail_less_loop((490, 480, 76))
    
    #Ending
    move_with_agnle((380, 480, 205), 0)
    move_with_agnle((75, 480, 205), 0)
    move_with_agnle((75, 480, -7), 0)
    move_with_agnle((60, 710, -7), 0)
    speak_to_arduino2()
    move_with_agnle((115, 730, -7), 0)

    



    
    
    
    






