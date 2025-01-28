from motor import Motor
import ttyacm

tty = ttyacm.open(1)

yaw_motor = Motor(9, 10)
pitch_motor = Motor(12, 13)

const_speed = 0.0

while True:  
    data = tty.readline()
    print(data)
    if data == "UP":
        print("UP")
        pitch_motor.move(const_speed)
    elif data == "DOWN":
        print("DOWN")
        pitch_motor.move(-const_speed)
    elif data == "RIGHT":
        print("RIGHT")
        yaw_motor.move(const_speed)
    elif data == "LEFT":
        print("LEFT")
        yaw_motor.move(-const_speed)
    elif data == "SPACE":
        print("SPACE")
        pitch_motor.move(0)
        yaw_motor.move(0)