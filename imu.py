import time
import ttyacm
import machine
from bno055 import *

tty = ttyacm.open(1)  # open serial DATA port

# Define SCL & SDA pins for BNO055 imu
i2c1 = machine.I2C(1, scl=machine.Pin(3), sda=machine.Pin(2))
imu = BNO055(i2c1)

while True:
    time.sleep(0.1)  # 10 Hz
    yaw, pitch, roll = imu.euler()
    print(f"Yaw: {yaw} Pitch: {pitch}")
    tty.print(yaw)
    tty.print(pitch)