# fire.py

import time
import math
from machine import Pin, PWM, I2C

class Fire:
    def __init__(self):
        self.INA260_ADDRESS = 0x40
        self.INA260_CURRENT_REGISTER = 0x01

        self.ina260_i2c = I2C(0, scl=Pin(1), sda=Pin(0))

        # Motor drive
        self.motor1 = PWM(Pin(15))  # set motor pin
        self.motor1.freq(1000)  # set frequency to 1KHz
        self.motor1.duty_u16(0)  # 0-65535 for duty cycle range 0-100

        # Feed belt motor 
        self.motor2 = PWM(Pin(14))  # set motor pin
        self.motor2.freq(1000)  # set frequency to 1KHz
        self.motor2.duty_u16(0)  # 0-65535 for duty cycle range 0-100
        
#         self.motor1.duty_u16(int(1 * 65535))
#         time.sleep(3)

    def read_current(self):
        """Read current from INA260."""
        try:
            data = self.ina260_i2c.readfrom_mem(self.INA260_ADDRESS, self.INA260_CURRENT_REGISTER, 2)
            raw_current = int.from_bytes(data, 'big')
            if raw_current & 0x8000:
                raw_current -= 1 << 16
            current_ma = raw_current * 1.25  # Convert to mA
            return current_ma
        except OSError:
            print("Error reading INA260.")
            return math.nan  # Return nan if read fails
        
    def spin_up(self):
        self.motor1.duty_u16(65535)
        
    def fire_balls(self):
        self.motor2.duty_u16(65535)
        
    def ball_shot(self):
        if self.read_current() > 2000:
            return True
        return False
