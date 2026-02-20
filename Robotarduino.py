# Upcoming Tasks:
# T1. Modify the screw-driving order (currently in a Z-shape pattern)
#     Suggested pattern modification:
#     For the subsequent weaving process, we need to start from a fixed point,
#     so consider fixing one screw at the center of the rectangle!!!

# T2. Encapsulate the Wound_nail function
#     Issue:
#     During weaving, if we need to use joint 5 to control the end-effector orientation,
#     we must ensure that the orientation remains unchanged during movement —
#     check the user guide.

# T3. Mathematical modeling:
#     Control the end-effector orientation through joint 5.

# T4. Convert the modeling in T3 into executable code.

# Tips:
# Check the key names, make sure they are all defined
# Jupyter lab cannot access arduino port. So, can only use Commend or python IDLE
#  ---------- Updated on Feb 20th, 2026 ---------- 


# robot movement w/ python trigger

import serial
import time
from standardbots import models, StandardBotsRobot

# Configure the serial connection 
arduino = serial.Serial(port='COM9', baudrate=9600, timeout=1)

# create function to write to and read from arduino through serial port
def write_read(x):
    # Send data to Arduino, encoding it into bytes
    arduino.write(bytes(x, 'utf-8'))
    time.sleep(0.1)
    # Read the response from Arduino, decode it, and strip whitespace
    response = arduino.readline().decode().strip()
    return response

# Set up robot connection over ethernet
sdk = StandardBotsRobot(
  url='http://192.168.110.5:3000',
  token='oetrwf0e-yyquw-8eopsk-z8egwu6g',
  robot_kind=StandardBotsRobot.RobotKind.Live,
)

# fixed orientation of the tooltip
Q_IDENTITY = models.Quaternion(1.0, 0.0, -1.0, 0.0)
# Quaternion: (1, 0, -1, 0) represents direction towards the groud.

# Function to move tooltip to (x,y,z) in millimeters, orientation fixed.
def move_tooltip_xyz(x_m, y_m, z_m):
    body = models.ArmPositionUpdateRequest(
        kind = models.ArmPositionUpdateRequestKindEnum.TooltipPosition,
        tooltip_position = models.PositionAndOrientation(
            position = models.Position(
                x = float(x_m), y = float(y_m), z = float(z_m),
                unit_kind=models.LinearUnitKind.Millimeters,
            ),
            orientation = models.Orientation(
                kind = models.OrientationKindEnum.Quaternion,
                quaternion = Q_IDENTITY,
            ),
        ),
    )
    sdk.movement.position.set_arm_position(body=body).ok()

# Define function trajectory data
def run_Square_Wound_nail_trajectory():
    # Location in mm
    points = {
        1: ( 500, 360, -500),
            11: ( 500, 330, -500),
            12: ( 470, 360, -500),
            13: ( 500, 390, -500),
            14: ( 530, 360, -500),
        2: ( 500, 740, -500),
            21: ( 500, 710, -500),
            22: ( 470, 740, -500),
            23: ( 500, 770, -500),
            24: ( 530, 740, -500),
        3: ( 700, 360, -500),
            31: (700, 330, -500),
            32: (670, 360, -500),
            33: (700, 390, -500),
            34: (730, 360, -500),
        4: ( 700, 740, -500),
            41: (700, 710, -500),
            42: (670, 740, -500),
            43: (700, 770, -500),
            44: (730, 740, -500),
        # Points will locate in the range of all positive x and y
        # Updated!
    }

    # Order：1 11 12 13 14, 
    # 2 21 22 23 24,
    # 3 31 32 33 34,
    # 4 41 42 43 44
    sequence = [1,11,12,13,14,2,21,22,23,24,3,31,32,33,34,4,41,42,43,44]
    for index in sequence:
        x_mm, y_mm, z_mm = points[index]
        
        move_tooltip_xyz(float(x_mm), float(y_mm), float(z_mm))


# function to call communication with arduino
def speak_to_arduino():
    time.sleep(2) # Wait for Arduino to initialize after connection
    print("Connected to Arduino")
    # Send '1' once
    num = "1" 
    value = write_read(num)
    print(f"Arduino responded: {value}")

    arduino.close() # Close the serial connection

        

with sdk.connection():
    run_Square_Wound_nail_trajectory()
    speak_to_arduino()

