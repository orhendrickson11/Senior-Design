# Test python to arduino command

# Python Code
import serial
import time

# Configure the serial connection (replace 'COM3' with your Arduino's port)
arduino = serial.Serial(port='COM5', baudrate=9600, timeout=1)

def write_read(x):
    # Send data to Arduino, encoding it into bytes
    arduino.write(bytes(x, 'utf-8'))
    time.sleep(0.1)
    # Read the response from Arduino, decode it, and strip whitespace
    response = arduino.readline().decode().strip()
    return response

if __name__ == "__main__":
    time.sleep(2) # Wait for Arduino to initialize after connection
    print("Connected to Arduino")
    # Send '1' once
    num = "1" 
    value = write_read(num)
    print(f"Arduino responded: {value}")

    arduino.close() # Close the serial connection
