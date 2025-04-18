# controller.py

import time

class Controller:
    def __init__(self, motor, P, I, sampling_rate, deadzone):
        self.motor = motor
        self.P = P  # proportional gain
        self.I = I  # integral gain
        self.time_step = 1/sampling_rate
        self.integral = 0  # integral of error
        self.deadzone = deadzone  # deadzone threshold
        self.previous_errors = [10, 10]
        self.current_error = 10
        self.previous_error = 10
        self.start_time = None
        self.duty_cycle = 0
        
    def move_to_angle(self, current_angle, desired_angle):
        if not self.start_time:
            self.start_time = time.time()
        error = desired_angle - current_angle  # calculate error
        self.current_error = error
        self.integral += error * self.time_step  # euler integration
        
        # Calculate input voltage PI 
        self.duty_cycle = (self.P * error) + (self.I * self.integral)
                
        # Deadzone compensation
        if self.duty_cycle > 0:
            self.duty_cycle += self.deadzone[0]
        else:
            self.duty_cycle -= self.deadzone[1]
        
        # Cap input voltage at +/- 1 volt
        if self.duty_cycle > 1:
            self.duty_cycle = 1
        elif self.duty_cycle < -1:
            self.duty_cycle = -1

        self.motor.move(self.duty_cycle)

        if self.reached_target():
            self.integral = 0  # reset integral
            self.duty_cycle = 0  # reset duty cycle
            self.current_error = 10
            self.previous_error = 10
            self.start_time = None
            return True
        
        self.previous_error = error
        
    def reached_target(self, threshold=0.5729578, slope=3, timeout=5):
        if abs(self.start_time - time.time()) > timeout:
            print("TIMEOUT")
            return True
        
        return abs(self.current_error) < threshold and abs(self.previous_error) < threshold and abs((self.current_error - self.previous_error)/self.time_step) < slope 