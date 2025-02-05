# calc_TF_pico.py

import time
import ttyacm
import _thread
from bno055 import *
from motor import Motor

tty = ttyacm.open(1)  # open serial DATA port
sampling_rate = 100  # Hz

# Define SCL & SDA pins for BNO055 IMU
i2c1 = machine.I2C(1, scl=machine.Pin(3), sda=machine.Pin(2))
imu = BNO055(i2c1)

# Create Motor instances
yaw_motor = Motor(9, 10)
pitch_motor = Motor(13, 12)

const_speed = 0.6  # set motor duty cycle speed
step_duration = 0.2  # seconds
interval = 1  # seconds between step inputs

# Decode serial data
def read_serial():
    global data
    while True:
        data = tty.readline().strip()
        
def wrap2pi(ang):
    while ang > 180.0:
        ang = ang - 360.0
    while ang < -180.0:
        ang = ang + 360.0
    return ang
    
# Start the reading serial on seperate thread
_thread.start_new_thread(read_serial, ())
  
# Wait for user to start sending keyboard commands
while True:
    if data:
        break
    time.sleep(0.5)  # Sleep for a short time to avoid busy-waiting
    
# Move motor based on serial keyboard signals
while True:
    # Read imu data and send through serial port
    yaw, pitch, roll = imu.euler()
    print(f"Yaw: {wrap2pi(yaw)} Pitch: {pitch}")
    tty.print(f"{wrap2pi(yaw)},{pitch}")
    
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
        elif data = "ENTER":  # step response
            yaw_motor.move(const_speed)
            time.sleep(step_duration)
            yaw_motor.move(0)
            time.sleep(interval)
            yaw_motor.move(-const_speed)
            time.sleep(step_duration)
            yaw_motor.move(0)
            time.sleep(interval)
            pich_motor.move(const_speed)
            time.sleep(sleep_duration)
            pitch_motor.move(0)
            time.sleep(interval)
            pich_motor.move(-const_speed)
            time.sleep(sleep_duration)
            pitch_motor.move(0)
            
        data = None  # reset data variable
        
    time.sleep(1/sampling_rate)  # control loop rate

