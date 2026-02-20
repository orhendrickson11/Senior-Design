# robot movement w/ python trigger

import serial
import time
from standardbots import models, StandardBotsRobot

# Configure the serial connection 
arduino = serial.Serial(port='COM5', baudrate=9600, timeout=1)

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
        1: ( 500, 360, 0),
            11: ( 500, 330, 0),
            12: ( 470, 360, 0),
            13: ( 500, 390, 0),
            14: ( 530, 360, 0),
        2: ( 250, 740, 0),
            21: ( 500, 710, 0),
            22: ( 470, 740, 0),
            23: ( 500, 770, 0),
            23: ( 530, 740, 0),
        3: ( 700, 360, 0),
            31: (700, 330, 0),
            32: (670, 360, 0),
            33: (700, 390, 0),
            34: (730, 360, 0),
        4: ( 700, 740, 0),
            41: (700, 710, 0),
            42: (670, 740, 0),
            43: (700, 770, 0),
            44: (730, 740, 0),
        # Points will locate in the range of all positive x and y
        # Updated!
    }

    # Order：1 11 12 13 14, 2 21 22 23 24, 3 31 32 33 34, 4 41 42 43 44
    sequence = [1,11,12,13,14,
                2,21,22,23,24,
                3,31,32,33,34,
                4,41,42,43,44]
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
    
    
