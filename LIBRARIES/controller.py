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
        self.start_time = None
        
    def move_to_angle(self, current_angle, desired_angle):
        if not self.start_time:
            print("setting time")
            self.start_time = time.time()
        error = desired_angle - current_angle  # calculate error
        self.previous_errors.append(error)  # add to previous_errors list
        self.integral += error * self.time_step  # euler integration
        
        # Calculate input voltage PI 
        input_voltage = (self.P * error) + (self.I * self.integral)
        
        # Deadzone compensation
        if input_voltage >= 0:
            input_voltage += self.deadzone[0]
        else:
            input_voltage -= self.deadzone[1]
        
        # Cap input voltage at +/- 12 volts
        if input_voltage > 12:
            input_voltage = 12
        elif input_voltage < -12:
            input_voltage = -12

        duty_cycle = input_voltage/12  # calculate duty cycle 
        self.motor.move(duty_cycle)

        print(desired_angle, current_angle, error, input_voltage, duty_cycle)
        if self.reached_target():
            print("REACHED TARGET")
            self.integral = 0  # reset integral
            self.previous_errors = [10, 10]  # reset previous_errors
            self.start_time = None
            return True
        
    def reached_target(self, threshold=0.5729578, timeout=5):
        if (self.previous_errors[-1] > 0 and self.previous_errors[-2] > 0) or \
           (self.previous_errors[-1] < 0 and self.previous_errors[-2] < 0):
            return abs(self.previous_errors[-1] + self.previous_errors[-2])/2 < threshold
        elif abs(self.start_time - time.time()) > timeout:
            return True