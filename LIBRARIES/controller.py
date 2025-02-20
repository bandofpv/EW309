# controller.py

class Controller:
    def __init__(self, motor, P, I, D, sampling_rate):
        self.motor = motor
        self.P = P  # proportional gain
        self.I = I  # integral gain
        self.D = D  # derivative gain
        self.time_step = 1/sampling_rate
        self.previous_error = 0
        self.integral = 0
        
    def move_to_angle(self, current_angle, desired_angle, velocity, threshold=1):
        error = desired_angle - current_angle
        self.integral += error * self.time_step
        derivative = (error - self.previous_error) / self.time_step

        duty_cycle = (self.P * error) + (self.I * self.integral) + (self.D * derivative)
        if duty_cycle > 12:
            duty_cycle = 12
        elif duty_cycle < -12:
            duty_cycle = -12
        self.motor.move(duty_cycle/12)
        self.previous_error = error

        print(desired_angle, current_angle, error, duty_cycle, duty_cycle/12)
        if abs(error) < threshold and abs(velocity) < threshold:
            self.integral = 0  # reset integral
            return True