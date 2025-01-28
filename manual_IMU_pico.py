
import time
import ttyacm
from bno055 import *
from motor import Motor

tty = ttyacm.open(1)  # open serial DATA port

# Define SCL & SDA pins for BNO055 imu
i2c1 = machine.I2C(1, scl=machine.Pin(3), sda=machine.Pin(2))
imu = BNO055(i2c1)

# Create Motor instances
yaw_motor = Motor(10, 9)
pitch_motor = Motor(13, 12)

const_speed = 0.6  # set motor duty cycle speed

def read_serial():
    global data
    while True:
        data = tty.readline().strip()
        
# Start the reading serial on seperate thread
serial_thread = threading.Thread(target=read_serial, daemon=True)
serial_thread.start()
  
# Move motor based on serial key signals
while True:
    time.sleep(0.1)  # 10 Hz
    yaw, pitch, roll = imu.euler()
    print(f"Yaw: {yaw} Pitch: {pitch}")
    tty.print(yaw)
    tty.print(pitch)
    
    if data:
        print(f"Received: {data}")
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
        data = None  # reset data variable