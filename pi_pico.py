# pid_pico.py

import time
import ttyacm
import _thread
from bno055 import *
from motor import Motor
from controller import Controller

tty = ttyacm.open(1)  # open serial DATA port
sampling_rate = 10  # Hz

# Define SCL & SDA pins for BNO055 IMU
i2c1 = machine.I2C(1, scl=machine.Pin(3), sda=machine.Pin(2))
imu = BNO055(i2c1)

# Create Motor instances
yaw_motor = Motor(9, 10)
pitch_motor = Motor(12, 13)

# Initialize controllers
yaw_control = Controller(yaw_motor, P=1, I=0.01, sampling_rate=sampling_rate)
pitch_control = Controller(pitch_motor, P=1, I=0.01, sampling_rate=sampling_rate)

const_speed = 0.6  # set motor duty cycle speed

# Decode serial data
def read_serial():
    global data
    while True:
        data = tty.readline().strip()
    
# Wraps angles in degrees to the interval [-180,180]
def wrap2pi(ang):
    while ang > 180.0:
        ang = ang - 360.0
    while ang < -180.0:
        ang = ang + 360.0
    return ang
    
# Start the reading serial on seperate thread
_thread.start_new_thread(read_serial, ())
  
# Wait for user to start sending keyboard commands
data = False
print("Waiting for keyboard input...")    
while not data:
    time.sleep(0.5)
    
# Move motor based on serial keyboard signals
move = False
while True:
    # Read imu data and send through serial port
    yaw, pitch, roll = imu.euler()
    x_omega, y_omega, z_omega = imu.gyro()
    print(f"Yaw: {wrap2pi(yaw)} Pitch: {pitch} Yaw Velocity: {z_omega} Pitch Velocity: {y_omega}")
    tty.print(f"{wrap2pi(yaw)},{pitch},{z_omega},{y_omega}")
    
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
        elif data == "QUIT":  # stop motors and break
            pitch_motor.move(0)
            yaw_motor.move(0)
            break
        elif data == "ENTER":  # PID Control
            move = True        
        data = None  # reset data variable
    
    elif move:
        yaw_control.move_to_angle(wrap2pi(yaw), 30, z_omega)
        pitch_control.move_to_angle(pitch, 30, y_omega)
#         if yaw_control.move_to_angle(wrap2pi(yaw), 30, z_omega):
#             yaw_motor.move(0)
#             move = False
#         if pitch_control.move_to_angle(pitch, 30, y_omega):
#             pitch_motor.move(0)
#             move = False
    time.sleep(1/sampling_rate)  # control loop rate