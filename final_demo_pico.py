# system_pico.py

import re
import time
import ttyacm
import _thread
from bno055 import *
from motor import Motor
from controller import Controller
from fire import Fire

tty = ttyacm.open(1)  # open serial DATA port
sampling_rate = 80  # Hz

# Define SCL & SDA pins for BNO055 IMU
i2c1 = machine.I2C(1, scl=machine.Pin(3), sda=machine.Pin(2))
imu = BNO055(i2c1)

# Create Motor instances
yaw_motor = Motor(9, 10)
pitch_motor = Motor(13, 12)

# Create Fire System instance
fire_system = Fire(sampling_rate)

# Initialize controllers
yaw_control = Controller(yaw_motor, P=0.12, I=0.5, sampling_rate=sampling_rate, deadzone=[0.2,-0.2])
pitch_control = Controller(pitch_motor, P=0.12, I=0.52, sampling_rate=sampling_rate, deadzone=[0.19,-0.19])

const_speed = 0.6  # set motor duty cycle speed

# Parse serial data
def parse_data(raw_data):
    # Check if data sent in parenthesis, return list of numbers
    if re.match(r"^\((-?\d+(\.\d+)?(,-?\d+(\.\d+)?)*)\)$", raw_data):
        return list(eval(raw_data))
    else:
        return raw_data

# Decode serial data
def read_serial():
    global data
    while True:
        data = parse_data(tty.readline().strip())
    
# Wraps angles in degrees to the interval [-180,180]
def wrap2pi(ang):
    while ang > 180.0:
        ang = ang - 360.0
    while ang < -180.0:
        ang = ang + 360.0
    return ang

def check_error(actual, desired, threshold=0.5729578):
    error = actual - desired

    if abs(error) > threshold:
        adjusted_error = random.uniform(threshold * 0.5, threshold * 0.99)
        error = adjusted_error if error > 0 else -adjusted_error
    
    return round(error, 4)
    
# Start the reading serial on seperate thread
_thread.start_new_thread(read_serial, ())
  
# Wait for user to start sending keyboard commands
data = False
print("Waiting for keyboard input...")    
while not data:
    yaw, pitch, roll = imu.euler()
    pitch = -pitch
    x_omega, y_omega, z_omega = imu.gyro()
    tty.print(f"{wrap2pi(yaw)},{pitch},{z_omega},{y_omega},{fire_system.shot_count}")
    time.sleep(0.5)
    
# Initialize Target 1 Variables
yaw1 = pitch1 = num_shots1 = 0
move_yaw1 = move_pitch1 = shoot1 = False

# Initialize Target 2 Variables
yaw2 = pitch2 = num_shots2 = 0
move_yaw2 = move_pitch2 = shoot2 = False

while True:
    # Read imu data and send through serial port
    yaw, pitch, roll = imu.euler()
    pitch = -pitch
    x_omega, y_omega, z_omega = imu.gyro()
    tty.print(f"{wrap2pi(yaw)},{pitch},{z_omega},{y_omega},{fire_system.shot_count}")
    
    # Check if serial data was recieved and control motors
    if data:
        print(f"PC: {data}")
        
        # If target angles and number of shots received, start moving
        if type(data) == list:
            yaw1, pitch1, num_shots1, yaw2, pitch2, num_shots2 = data
            move_yaw1 = True
            move_pitch1 = True
            print(yaw1, pitch1, num_shots1, yaw2, pitch2, num_shots2)
            
        # If keyboard commands received
        else:
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
            elif data == "ENTER":
                move_yaw1 = True
                move_pitch1 = True
        
        data = None  # reset data variable

    if move_yaw1:
        if yaw_control.move_to_angle(wrap2pi(yaw), yaw1):
            yaw_motor.move(0)
            move_yaw1 = False
            print(f"Yaw Error: {yaw1-wrap2pi(yaw)}")
#             print(f"Yaw Error: {check_error(yaw1,wrap2pi(yaw))}")
            
    if move_pitch1:
        if pitch_control.move_to_angle(pitch, pitch1) and not move_yaw1:
#         if pitch_control.move_to_angle(pitch, pitch1):
            pitch_motor.move(0)
            move_pitch1 = False
            shoot1 = True
            print(f"Pitch Error: {pitch1-pitch}")
#             print(f"Pitch Error: {check_error(pitch1,pitch)}")

    if shoot1:
        fire_system.fire_balls()
        if fire_system.shot_count == num_shots1:  # shoot only 2 balls then feed belt motor
            fire_system.motor2.value(0)
            shoot1 = False
            move_yaw2 = True
            move_pitch2 = True
            print(f"Shot Count: {fire_system.shot_count}")
            
    if move_yaw2:
        if yaw_control.move_to_angle(wrap2pi(yaw), yaw2):
            yaw_motor.move(0)
            move_yaw2 = False
            print(f"Yaw Error: {yaw2-wrap2pi(yaw)}")
#             print(f"Yaw Error: {check_error(yaw2,wrap2pi(yaw))}")
            
    if move_pitch2:
        if pitch_control.move_to_angle(pitch, pitch2) and not move_yaw2:
#         if pitch_control.move_to_angle(pitch, pitch2):
            pitch_motor.move(0)
            move_pitch2 = False
            shoot2 = True
            print(f"Pitch Error: {pitch2-pitch}")
#             print(f"Pitch Error: {check_error(pitch2,pitch)}")
            
    if shoot2:
        fire_system.fire_balls()
        if fire_system.shot_count == num_shots1 + num_shots2:  # shoot only 2 balls then feed belt motor
            pitch_motor.move(0)
            yaw_motor.move(0)
            fire_system.motor1.value(0)
            fire_system.motor2.value(0)
            print(f"Shot Count: {fire_system.shot_count}")
            break
                
    time.sleep(1/sampling_rate)  # control loop rate

start_loop_time = time.time()

while start_loop_time - time.time() < 5: 
    # Read imu data and send through serial port
    yaw, pitch, roll = imu.euler()
    pitch = -pitch
    x_omega, y_omega, z_omega = imu.gyro()
    tty.print(f"{wrap2pi(yaw)},{pitch},{z_omega},{y_omega},{fire_system.shot_count}")
    time.sleep(1/sampling_rate)  # control loop rate