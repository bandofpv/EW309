# manual_pico.py

from motor import Motor
import ttyacm

tty = ttyacm.open(1)  # open serial DATA port

# Create Motor instances
yaw_motor = Motor(10, 9)
pitch_motor = Motor(13, 12)

const_speed = 0.6  # set motor duty cycle speed
  
# Move motor based on serial key signals
while True:
    data = tty.readline()
    print(data)
    if data == "UP":  # move pitch motor up
        pitch_motor.move(const_speed)
    elif data == "DOWN":  # move pitch motor down
        pitch_motor.move(-const_speed)
    elif data == "RIGHT":  # move yaw motor right
        yaw_motor.move(const_speed)
    elif data == "LEFT":  # move yaw motor left
        yaw_motor.move(-const_speed)
    elif data == "SPACE":  # stop all motors
        pitch_motor.move(0)
        yaw_motor.move(0)