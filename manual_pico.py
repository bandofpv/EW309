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
    if data == "UP":
        pitch_motor.move(const_speed)
    elif data == "DOWN":
        pitch_motor.move(-const_speed)
    elif data == "RIGHT":
        yaw_motor.move(const_speed)
    elif data == "LEFT":
        yaw_motor.move(-const_speed)
    elif data == "SPACE":
        pitch_motor.move(0)
        yaw_motor.move(0)