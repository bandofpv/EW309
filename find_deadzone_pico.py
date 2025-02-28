# find_deadzone_pico.py --> copy of calc_TF_pico.py --> copy of manual_IMU_pico.py

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

const_speed = 0.15  # initial motor duty cycle
duty_cycle = const_speed # set motor duty cycle
increment = 0.01  # how much to increment duty cycle

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
while True:
    if data:
        break
    time.sleep(0.5)  # Sleep for a short time to avoid busy-waiting
    
# Move motor based on serial keyboard signals
while True:    
    # Read imu data and send through serial port
    yaw, pitch, roll = imu.euler()
    x_omega, y_omega, z_omega = imu.gyro()
    print(f"Yaw: {wrap2pi(yaw)} Pitch: {pitch} Yaw Velocity: {z_omega} Pitch Velocity: {y_omega} Duty Cycle: {duty_cycle}")
    tty.print(f"{wrap2pi(yaw)},{pitch},{z_omega},{y_omega},{duty_cycle}")
    
    # Check if serial data was recieved and control motors
    if data:
        print(f"KEYBOARD: {data}")
        if data == "UP":
            const_speed += increment
            duty_cycle = const_speed
            pitch_motor.move(duty_cycle)
        elif data == "DOWN":
            const_speed += increment
            duty_cycle = -const_speed
            pitch_motor.move(duty_cycle)
        elif data == "RIGHT":  # turn yaw motor right
            const_speed += increment
            duty_cycle = const_speed
            yaw_motor.move(duty_cycle)
        elif data == "LEFT":  # turn yaw motor left
            const_speed += increment
            duty_cycle = -const_speed
            yaw_motor.move(duty_cycle) 
        elif data == "SPACE":  # stop motors
            pitch_motor.move(0) 
            yaw_motor.move(0)
            const_speed = 0.15  # reset duty cycle
        elif data == "QUIT":  # stop motors and break
            pitch_motor.move(0)
            yaw_motor.move(0)
            break
        data = None  # reset data variable
        
    time.sleep(1/sampling_rate)  # control loop rate 