# shoot_pico.py

import ttyacm
import _thread
from fire import Fire
import time

tty = ttyacm.open(1)  # open serial DATA port
sampling_rate = 60

fire_system = Fire(sampling_rate)

# Decode serial data
def read_serial():
    global data
    while True:
        data = tty.readline().strip()
    
# Start the reading serial on seperate thread
_thread.start_new_thread(read_serial, ())
  
# Wait for user to start sending keyboard commands
data = False
print("Waiting for keyboard input...")    
while not data:
    time.sleep(0.5)
    
# Move motor based on serial keyboard signals
fire = False
while True:
    tty.print(f"{fire_system.current}, {fire_system.shot_count}, {fire_system.slope}")
    print(f"Current: {fire_system.current} Shot Count: {fire_system.shot_count} Slope: {fire_system.slope}")
    
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
            pass
        elif data == "QUIT":  # stop motors and break
            fire_system.motor1.duty_u16(0)
            fire_system.motor2.duty_u16(0)
            break
        elif data == "ENTER":  # PID Control
            fire = True
        data = None  # reset data variable

    if fire:
        fire_system.fire_balls()
    
    if fire_system.shot_count == 4:
        fire_system.motor1.duty_u16(0)
        fire_system.motor2.duty_u16(0)

    time.sleep(1/sampling_rate)  # control loop rate