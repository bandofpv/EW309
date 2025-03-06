# fire_one_ball.py

from fire import Fire
import time

testing = Fire()

# NOTE: THIS SCRIPT ASSUMES SPIN UP BEFORE HAND

while True:
    testing.fire_balls()
    print(testing.read_current())
    time.sleep(0.1)
    
    if testing.ball_shot():
        testing.motor2.duty_u16(0)
        break

testing.motor1.duty_u16(0)
testing.motor2.duty_u16(0)
time.sleep(1)
