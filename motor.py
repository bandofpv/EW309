from machine import Pin, PWM

class Motor:
    def __init__(self, IN1, IN2=16):
        # Assign Pin Values
        self.IN1 = IN1
        self.IN2 = IN2
        
        # Forward Motor Pin (IN1)
        self.motor1 = PWM(Pin(self.IN1))  # set motor pin
        self.motor1.freq(1000) # set frequency to 1KHz
        self.motor1.duty_u16(0)  # 0-65535 for duty cycle range 0-100
        
        # Backward Motor Pin (IN2)
        self.motor2 = PWM(Pin(self.IN2))  # set motor pin
        self.motor2.freq(1000) # set frequency to 1KHz
        self.motor2.duty_u16(0)  # 0-65535 for duty cycle range 0-100
        
    # Move the motor given speed (-1.0 to 1.0)
    def move(self, speed):
        if speed > 0:
            self.motor1.duty_u16(int(speed * 65535))
            self.motor2.duty_u16(0)
        elif speed < 0:
            self.motor1.duty_u16(0)
            self.motor2.duty_u16(int(-speed * 65535))
        else:
            self.motor1.duty_u16(65535)
            self.motor2.duty_u16(65535)