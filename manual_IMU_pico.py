import time
import ttyacm
import _thread
from bno055 import *
from motor import Motor

tty = ttyacm.open(1)  # open serial DATA port
sampling_rate = 10  # Hz

# Define SCL & SDA pins for BNO055 IMU
i2c1 = machine.I2C(1, scl=machine.Pin(3), sda=machine.Pin(2))
imu = BNO055(i2c1)

# Create Motor instances
yaw_motor = Motor(9, 10)
pitch_motor = Motor(13, 12)

const_speed = 0.6  # set motor duty cycle speed

# Decode serial data
def read_serial():
    global data
    while True:
        data = tty.readline().strip()
        
# Start the reading serial on seperate thread
_thread.start_new_thread(read_serial, ())
  
# Move motor based on serial keyboard signals
while True:
    # Read imu data and send through serial port
    yaw, pitch, roll = imu.euler()
    print(f"Yaw: {yaw} Pitch: {pitch}")
    tty.print(f"{yaw},{pitch}")
    
    # Check if serial data was recieved and control motors
    if data:
        print(f"KEYBOARD: {data}")
        if data == "UP":
            pitch_motor.move(const_speed)
        elif data == "DOWN":
            pitch_motor.move(-const_speed)
        elif data == "RIGHT":  # turn yaw motor right
            yaw_motor.move(const_speed)
        elif data == "LEFT":  # turn yaw motor left
            yaw_motor.move(-const_speed)
        elif data == "SPACE":  # stop motors
            pitch_motor.move(0)
            yaw_motor.move(0)
        data = None  # reset data variable
        
    time.sleep(1/sampling_rate)  # control loop rate