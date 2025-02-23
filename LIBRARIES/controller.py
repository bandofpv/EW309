# controller.py

class Controller:
    def __init__(self, motor, P, I, sampling_rate, deadzone):
        self.motor = motor
        self.P = P  # proportional gain
        self.I = I  # integral gain
        self.time_step = 1/sampling_rate
        self.integral = 0  # integral of error
        self.deadzone = deadzone  # deadzone threshold
        
    def move_to_angle(self, current_angle, desired_angle, velocity, threshold=1):
        error = desired_angle - current_angle  # calculate error
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
        if abs(error) < threshold and abs(velocity) < threshold:
            self.integral = 0  # reset integral
            return True