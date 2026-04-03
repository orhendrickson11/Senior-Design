import math

def euler_to_quaternion(roll_deg, pitch_deg, yaw_deg):
    # roll  -> X
    # pitch -> Y
    # yaw   -> Z
    #
    # 组合顺序：
    # q = qx(roll) * qy(pitch) * qz(yaw)

    roll = math.radians(roll_deg)
    pitch = math.radians(pitch_deg)
    yaw = math.radians(yaw_deg)

    cr = math.cos(roll / 2.0)
    sr = math.sin(roll / 2.0)

    cp = math.cos(pitch / 2.0)
    sp = math.sin(pitch / 2.0)

    cy = math.cos(yaw / 2.0)
    sy = math.sin(yaw / 2.0)

    # 这是 qx * qy * qz 正确展开后的结果
    x = sr * cp * cy + cr * sp * sy
    y = cr * sp * cy - sr * cp * sy
    z = cr * cp * sy + sr * sp * cy
    w = cr * cp * cy - sr * sp * sy

    return x, y, z, w


# test
x, y, z, w = euler_to_quaternion(89.7, 34.6, -89.7)
print("x =", x)
print("y =", y)
print("z =", z)
print("w =", w)
