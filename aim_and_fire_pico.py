# pid_pico.py

import time
import ttyacm
import _thread
from bno055 import *
from motor import Motor
from controller import Controller
from fire import Fire

tty = ttyacm.open(1)  # open serial DATA port
sampling_rate = 10  # Hz

# Define SCL & SDA pins for BNO055 IMU
i2c1 = machine.I2C(1, scl=machine.Pin(3), sda=machine.Pin(2))
imu = BNO055(i2c1)

# Create Motor instances
yaw_motor = Motor(9, 10)
pitch_motor = Motor(12, 13)

# Initialize controllers
yaw_control = Controller(yaw_motor, P=1.2, I=1.75, sampling_rate=sampling_rate, deadzone=[0.2,-0.2])
pitch_control = Controller(pitch_motor, P=1.1, I=1.9, sampling_rate=sampling_rate, deadzone=[0.21,-0.19])

const_speed = 0.6  # set motor duty cycle speed
duty_cycle = 0 # set motor duty cycle

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
move_yaw = False
move_pitch = False
shoot = False
spin = False

fire_system = Fire()

while True:
    # Read imu data and send through serial port
    yaw, pitch, roll = imu.euler()
    x_omega, y_omega, z_omega = imu.gyro()
    print(f"Yaw: {wrap2pi(yaw)} Pitch: {pitch} Yaw Velocity: {z_omega} Pitch Velocity: {y_omega} Yaw Duty Cycle: {yaw_control.duty_cycle} Pitch Duty Cycle: {pitch_control.duty_cycle} Fire System Current: {fire_system.current}")
    tty.print(f"{wrap2pi(yaw)},{pitch},{z_omega},{y_omega},{yaw_control.duty_cycle},{pitch_control.duty_cycle},{fire_system.current}")
    
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
            fire_system.spin_up()
            pitch_motor.move(0)
            yaw_motor.move(0)
        elif data == "QUIT":  # stop motors and break
            pitch_motor.move(0)
            yaw_motor.move(0)
            break
        elif data == "ENTER":  # PID Control
            shoot = True
            move_yaw = True
            move_pitch = True
        data = None  # reset data variable

    if move_yaw:
        if yaw_control.move_to_angle(wrap2pi(yaw), 20):
            yaw_motor.move(0)
            move_yaw = False
    if move_pitch:
        if pitch_control.move_to_angle(pitch, 10) and not move_yaw:
            pitch_motor.move(0)
            move_pitch = False
            
    if shoot:
        fire_system.fire_balls()
#         if fire_system.ball_shot():
#             shoot = False
        if fire_system.shot_count > 2:
            shoot = False
            
    time.sleep(1/sampling_rate)  # control loop rate
