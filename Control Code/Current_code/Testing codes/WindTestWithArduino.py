import math
import serial
import time
from standardbots import models, StandardBotsRobot

#=================== Arduino Connection ===============
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

JOINT6_SNAPSHOT = 0.0


# ================= Snapshot Function =================
def begin_segment_snapshot_orientation():
    """
    Save current tooltip orientation AND joint6 angle
    """

    global ORIENTATION_SNAPSHOT
    global JOINT6_SNAPSHOT

    resp = sdk.movement.position.get_arm_position()
    arm = getattr(resp, "parsed", None) or getattr(resp, "data", None) or resp

    # ---- Save orientation ----
    ori = arm.tooltip_position.orientation
    q = ori.quaternion
    ORIENTATION_SNAPSHOT = models.Quaternion(x=q.x, y=q.y, z=q.z, w=q.w)

    # ---- Save joint6 ----
    JOINT6_SNAPSHOT = arm.joint_rotations[5]

    print(f"[Snapshot] Joint6 = {math.degrees(JOINT6_SNAPSHOT):.2f} deg")


# ================= Move Function (IK only) =================
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
                quaternion=models.Quaternion(1.0, 0.0, -1.0, 0.0),
            ),
        ),
    )

    sdk.movement.position.set_arm_position(body=body).ok()


# ================= Joint6 Control =================
def restore_joint_6():
    """
    Restore joint6 to snapshot value (absolute)
    """

    resp = sdk.movement.position.get_arm_position()
    arm = getattr(resp, "parsed", None) or getattr(resp, "data", None) or resp

    joints = list(arm.joint_rotations)
    joints[5] = JOINT6_SNAPSHOT

    body = models.ArmPositionUpdateRequest(
        kind=models.ArmPositionUpdateRequestKindEnum.JointRotations,
        joint_rotations=[models.ArmJointRotations(joints=tuple(joints))],
    )

    sdk.movement.position.set_arm_position(body=body).ok()


def rotate_joint_6(delta_deg):
    """
    Rotate joint6 relative to current value, with debug print
    """

    delta_rad = math.radians(delta_deg)

    # ---- Read current state (BEFORE) ----
    resp = sdk.movement.position.get_arm_position()
    arm = getattr(resp, "parsed", None) or getattr(resp, "data", None) or resp

    joints = list(arm.joint_rotations)

    before_deg = math.degrees(joints[5])
    print(f"[Joint6 BEFORE] {before_deg:.2f} deg")

    # ---- Apply relative rotation ----
    joints[5] += delta_rad

    body = models.ArmPositionUpdateRequest(
        kind=models.ArmPositionUpdateRequestKindEnum.JointRotations,
        joint_rotations=[models.ArmJointRotations(joints=tuple(joints))],
    )

    sdk.movement.position.set_arm_position(body=body).ok()

    # ---- Read again (AFTER) ----
    resp_after = sdk.movement.position.get_arm_position()
    arm_after = getattr(resp_after, "parsed", None) or getattr(resp_after, "data", None) or resp_after

    joints_after = list(arm_after.joint_rotations)

    after_deg = math.degrees(joints_after[5])
    print(f"[Joint6 AFTER ] {after_deg:.2f} deg\n")


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
    move_tooltip_xyz(*C)
    move_tooltip_xyz(*L)
    move_tooltip_xyz(*D)
    move_tooltip_xyz(*R)
    move_tooltip_xyz(*U)

    # ---- Step 3: Restore + Rotate ----
    restore_joint_6()
    rotate_joint_6(delta_deg)


# ================= Main =================
with sdk.connection():
    wound_nail((500, 360, -200), delta_deg=30)
    wound_nail((500, 740, -200), delta_deg=30)
    wound_nail((700, 740, -200), delta_deg=-45)
    wound_nail((700, 360, -200), delta_deg=90)
    wound_nail((600, 570, -200), delta_deg=45)

  #this will initiate a wind  
  #speak_to_arduino()