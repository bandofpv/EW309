# fire.py

import time
import math
from machine import Pin, PWM, I2C

class Fire:
    def __init__(self, sampling_rate):
        
        self.sampling_time = 1/sampling_rate
        self.INA260_ADDRESS = 0x40
        self.INA260_CURRENT_REGISTER = 0x01
        self.ina260_i2c = I2C(0, scl=Pin(1), sda=Pin(0))
        self.previous_current = 0
        self.current = 0
        self.in_shot = False
        self.shot_count = 0
        self.slope = 0

        self.motor1 = Pin(15, Pin.OUT)  # counter rotating wheel motor
        self.motor2 = Pin(14, Pin.OUT)  # feed belt motor
        
        # Wait for counter rotating wheel motor to spin all the way up
        while self.read_current() > 2000 or self.read_current() < 1000:
            self.motor1.value(1)  # spin up wheel motor
            self.motor2.value(0)  # stop feed belt motor
            time.sleep(self.sampling_time)
        
        print("READY TO FIRE!!!")

    def read_current(self):
        """Read current from INA260."""
        try:
            data = self.ina260_i2c.readfrom_mem(self.INA260_ADDRESS, self.INA260_CURRENT_REGISTER, 2)
            raw_current = int.from_bytes(data, 'big')
            if raw_current & 0x8000:
                raw_current -= 1 << 16
            self.previous_current = self.current
            self.current = raw_current * 1.25  # Convert to mA
            return self.current
        except OSError:
            print("Error reading INA260.")
            return math.nan  # Return nan if read fails
        
    def spin_up(self):
        self.motor1.value(1)

    def count_shots(self):
        self.read_current()
        self.slope = (self.current - self.previous_current) / self.sampling_time  # caluclate slope
        
        # Count shots if above threshold and detected a peak
        if self.previous_current > 0 and self.slope > 20000:
            if not self.in_shot:
                self.in_shot = True
        else:
            if self.in_shot:
                self.shot_count += 1
            self.in_shot = False
        
    def fire_balls(self):
        self.motor2.value(1)  # power up feed belt
        self.count_shots()