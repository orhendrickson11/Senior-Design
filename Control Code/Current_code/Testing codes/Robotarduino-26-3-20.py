import math
from standardbots import models, StandardBotsRobot

# ================= Robot Connection =================
# Set up robot connection over ethernet
# Set up robot connection over ethernet
sdk = StandardBotsRobot(
    # url='http://192.168.110.5:3000',
    # ⬆ used at lab
    url = 'https://lobsimn1.sb.app',
    # ⬆ connect to local simulator
    # token='oetrwf0e-yyquw-8eopsk-z8egwu6g',
    # ⬆ used at lab
    token = '4k4m-5luub4f4-1n203z6-46hxtg',
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
    
    --- why using local rotation? ---
    
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
        
    """
    s = math.sin(angle_rad / 2.0)
    return models.Quaternion(
        x=axis[0] * s,
        y=axis[1] * s,
        z=axis[2] * s,
        w=math.cos(angle_rad / 2.0)
    )


# ================= Oritation Generation (Head Down + Self-Rotation) =================
'''
    Initial: Roll = 0°, Pitch = 90°, Yaw = 0°
    Positive rotation angles are determined by the right-hand rule:
        Grasp the shaft with your right hand.
        Point your thumb in the positive direction of the shaft.
        The direction in which your four fingers curl corresponds to the positive direction of rotation.
'''
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

    # ---- Save orientation ----
    ori = arm.tooltip_position.orientation
    q = ori.quaternion
    ORIENTATION_SNAPSHOT = models.Quaternion(x=q.x, y=q.y, z=q.z, w=q.w)

    # Sync current orientation
    CURRENT_ORIENTATION = models.Quaternion(x=q.x, y=q.y, z=q.z, w=q.w)

    print("[Snapshot] Orientation captured")


# ================= Move Function (IK only) =================
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


# ================= Nail Motion =================
def wound_nail(nail_point, dx=30, dy=30, delta_deg=0):
    """
    Execute cross pattern around a nail, then rotate joint6
    """

    # ---- Step 1: Snapshot ----
    begin_segment_snapshot_orientation()

    x, y, z = nail_point

    C = (x,      y,      z)
    L = (x - dx, y,      z)
    D = (x,      y + dy, z)
    R = (x + dx, y,      z)
    U = (x,      y - dy, z)

    # ---- Step 2: IK Motion (joint6 allowed to drift) ----
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
    


# ================= Main =================
with sdk.connection():
    move_tooltip_xyz(200, 196, 50)
    move_tooltip_xyz(200, 396, 100)
    weave((300, 396, 50), (300, 396, 100), 45)
    # These three lines are only used for testing
    '''
    # 
    # Outer circuit
    wound_nail((100, 350, -15))# √
    #刚好在outer外面绕一圈
    move_tooltip_xyz(200, 196, -15)
    move_tooltip_xyz(700, 196, -15)
    move_tooltip_xyz(700, 540, -15)
    move_tooltip_xyz(600, 680, -15)
    move_tooltip_xyz(0, 740, -15)
    move_tooltip_xyz(0, 340, -15)
    
    wound_nail((100, 350, -25))# √
        
    #刚好在inner外面绕一圈
    move_tooltip_xyz(0, 270, -15)
    move_tooltip_xyz(480, 270, -15)
    move_tooltip_xyz(480, 570, -15)
    move_tooltip_xyz(200, 690, -15)
    move_tooltip_xyz(120, 540, -15)
    
    move_tooltip_xyz(120, 330, -15)
    move_tooltip_xyz(320, 330, -0)
    '''
    
    '''
    THIS IS ABSOLUTE POSITION --- BE CAREFUL
    '''
