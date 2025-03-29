# pid_pico.py

import time
import ttyacm
import _thread
from bno055 import *
from motor import Motor
from controller import Controller
from fire import Fire

tty = ttyacm.open(1)  # open serial DATA port
sampling_rate = 60  # Hz

# Define SCL & SDA pins for BNO055 IMU
i2c1 = machine.I2C(1, scl=machine.Pin(3), sda=machine.Pin(2))
imu = BNO055(i2c1)

# Create Motor instances
yaw_motor = Motor(9, 10)
pitch_motor = Motor(13, 12)

# Create Fire System instance
fire_system = Fire(sampling_rate)

# Initialize controllers
yaw_control = Controller(yaw_motor, P=0.8, I=3.3, sampling_rate=sampling_rate, deadzone=[0.2,-0.2])
pitch_control = Controller(pitch_motor, P=0.9, I=3.3, sampling_rate=sampling_rate, deadzone=[0.21,-0.19])

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
    time.sleep(0.1)
    
# Target 1 Variables
yaw1 = 20
pitch1 = 10
target1 = 2
move_yaw1 = False
move_pitch1 = False
shoot1 = False

# Target 2 Variables
yaw2 = -20
pitch2 = -10
target2 = 3
move_yaw2 = False
move_pitch2 = False
shoot2 = False

while True:
    # Read imu data and send through serial port
    yaw, pitch, roll = imu.euler()
    pitch = -pitch
    x_omega, y_omega, z_omega = imu.gyro()
#     print(f"Yaw: {wrap2pi(yaw)} Pitch: {pitch} Yaw Velocity: {z_omega} Pitch Velocity: {y_omega} Yaw Duty Cycle: {yaw_control.duty_cycle} Pitch Duty Cycle: {pitch_control.duty_cycle} Fire System Current: {fire_system.current} Shot Count: {fire_system.shot_count} Slope: {fire_system.slope}")
    tty.print(f"{wrap2pi(yaw)},{pitch},{z_omega},{y_omega},{yaw_control.duty_cycle},{pitch_control.duty_cycle},{fire_system.current},{fire_system.shot_count},{fire_system.slope}")
    
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
            fire_system.motor1.value(0)
            fire_system.motor2.value(0)
            break
        elif data == "ENTER":  # PID Control
            move_yaw1 = True
            move_pitch1 = True
        data = None  # reset data variable

    if move_yaw1:
        if yaw_control.move_to_angle(wrap2pi(yaw), yaw1):
            yaw_motor.move(0)
            move_yaw1 = False
    if move_pitch1:
        if pitch_control.move_to_angle(pitch, pitch1) and not move_yaw1:
            pitch_motor.move(0)
            move_pitch1 = False
            shoot1 = True            
    if shoot1:
        fire_system.fire_balls()
        if fire_system.shot_count == target1:  # shoot only 2 balls then feed belt motor
            fire_system.motor2.value(0)
            shoot1 = False
            move_yaw2 = True
            move_pitch2 = True
            print(f"Yaw Error: {yaw1-wrap2pi(yaw)} Pitch Error: {pitch1-pitch}")
            
    if move_yaw2:
        if yaw_control.move_to_angle(wrap2pi(yaw), yaw2):
            yaw_motor.move(0)
            move_yaw2 = False
    if move_pitch2:
        if pitch_control.move_to_angle(pitch, pitch2) and not move_yaw2:
            pitch_motor.move(0)
            move_pitch2 = False
            shoot2 = True            
    if shoot2:
        fire_system.fire_balls()
        if fire_system.shot_count == target1 + target2:  # shoot only 2 balls then feed belt motor
            pitch_motor.move(0)
            yaw_motor.move(0)
            fire_system.motor1.value(0)
            fire_system.motor2.value(0)
            print(f"Yaw Error: {yaw2-wrap2pi(yaw)} Pitch Error: {pitch2-pitch}")
            break
            
    time.sleep(1/sampling_rate)  # control loop rate

start_loop_time = time.time()

while start_loop_time - time.time() < 5: 
    # Read imu data and send through serial port
    yaw, pitch, roll = imu.euler()
    pitch = -pitch
    x_omega, y_omega, z_omega = imu.gyro()
#     print(f"Yaw: {wrap2pi(yaw)} Pitch: {pitch} Yaw Velocity: {z_omega} Pitch Velocity: {y_omega} Yaw Duty Cycle: {yaw_control.duty_cycle} Pitch Duty Cycle: {pitch_control.duty_cycle} Fire System Current: {fire_system.current} Shot Count: {fire_system.shot_count} Slope: {fire_system.slope}")
    tty.print(f"{wrap2pi(yaw)},{pitch},{z_omega},{y_omega},{yaw_control.duty_cycle},{pitch_control.duty_cycle},{fire_system.current},{fire_system.shot_count},{fire_system.slope}")
    time.sleep(1/sampling_rate)  # control loop rate