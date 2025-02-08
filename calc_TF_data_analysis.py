# calc_TF_data_analysis.py

import numpy as np
import pandas as pd
import control as ct
from statistics import mean
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

data = pd.read_csv("data.csv")
step_magnitude = 0.6  # duty cycle of step input

# Finds the start and end indices of step response
def find_bump_indices(data, threshold):
    indices = []
    in_bump = False
    for i in range(len(data)):  
        if abs(data[i]) > threshold:  # check for values above threshold in deg/s
            if not in_bump:
                start_index = i
                in_bump = True
        elif in_bump:
            end_index = i
            indices.append([start_index-20, end_index+20])  # add some padding
            in_bump = False
    return indices

# Calculate final value of step response
def calc_final_value(data, threshold):
    for i in range(len(data)):
        if abs(data[i]) > threshold:  # check for values above threshold in deg/s
            final_value_index = i
    final_value = mean(data[final_value_index-5:final_value_index])  # calculate final value based on mean
    return final_value

# Calculate time constant of step response (time of intersection at 63% final value)
def calc_time_constant(time, velocity, final_value):
    x = np.linspace(time[0], time[-1], 1000)  # times to interpolate with
    y = np.interp(x, time, velocity)  # interpolate velocities
    difference = np.abs(y - (0.63*final_value))  # calculate difference between velocity and 63% of final value
    approx_index = np.argmin(difference)  # find index with least difference
    approx_time = x[approx_index]  # calculate the time constant
    return approx_time

# Calcualte start time (t=0) of step response
def calc_step_start(time, velocity):
    for i in range(len(data)):
        if abs(velocity[i]) > 1:  # check for values below 1 deg/s
            return time[i-1]
        
def generate_step(time, transfer_function):
    time = np.linspace(time[0], time[-1], 1000)  # times to input through
    x, y = ct.step_response(transfer_function, time) # uhh...
    return x, y
    
yaw_indices = find_bump_indices(data['yaw_velocity'], 20)
pitch_indices = find_bump_indices(data['pitch_velocity'], 20)

# Subplot for Position vs. Time
plt.figure(figsize=(10, 5))
plt.subplot(2, 1, 1)
plt.plot(data['time'], data['yaw'], marker='.', label='Yaw')
plt.plot(data['time'], data['pitch'], marker='.', label='Pitch')
plt.title("Position vs. Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Position (degrees)")
plt.grid(True)
plt.legend()

# Subplot for Angular Velocity
plt.subplot(2, 1, 2)
plt.plot(data['time'], data['yaw_velocity'], marker='.', label='Yaw')
plt.plot(data['time'], data['pitch_velocity'], marker='.', label='Ptich')
plt.title("Angular Velocity vs. Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Angular Velocity (degrees/sec)")
plt.grid(True)
plt.legend()
plt.tight_layout()

# Subplots for transfer function calculation
plt.figure(figsize=(10, 5))
plt.subplot(2, 2, 1)
time = data['time'][yaw_indices[0][0]:yaw_indices[0][1]].tolist()
yaw_velocity = data['yaw_velocity'][yaw_indices[0][0]:yaw_indices[0][1]].tolist()
final_value = calc_final_value(yaw_velocity, 20)
SSG = final_value / step_magnitude
tau_time = calc_time_constant(time, yaw_velocity, final_value)
start_time = calc_step_start(time, yaw_velocity)
plt.plot(time, yaw_velocity, marker='.')
plt.axhline(final_value, color='red', linestyle='-')
plt.axhline(0.63*final_value, color='magenta', linestyle='-')
plt.axvline(tau_time, color='lime', linestyle='-')
plt.axvline(start_time, color='black', linestyle='-')
plt.title("Yaw Velocity vs. Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Velocity (degrees/second)")
plt.grid(True)

plt.subplot(2, 2, 2)
time = data['time'][yaw_indices[1][0]:yaw_indices[1][1]].tolist()
yaw_velocity = data['yaw_velocity'][yaw_indices[1][0]:yaw_indices[1][1]].tolist()
final_value = calc_final_value(yaw_velocity, 20)
SSG = final_value / step_magnitude
tau_time = calc_time_constant(time, yaw_velocity, final_value)
start_time = calc_step_start(time, yaw_velocity)
plt.plot(time, yaw_velocity, marker='.')
plt.axhline(final_value, color='red', linestyle='-')
plt.axhline(0.63*final_value, color='magenta', linestyle='-')
plt.axvline(tau_time, color='lime', linestyle='-')
plt.axvline(start_time, color='black', linestyle='-')
plt.title("Yaw Velocity vs. Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Velocity (degrees/second)")
plt.grid(True)

plt.subplot(2, 2, 3)
time = data['time'][pitch_indices[0][0]:pitch_indices[0][1]].tolist()
pitch_velocity = data['pitch_velocity'][pitch_indices[0][0]:pitch_indices[0][1]].tolist()
final_value = calc_final_value(pitch_velocity, 20)
SSG = final_value / step_magnitude
tau_time = calc_time_constant(time, pitch_velocity, final_value)
start_time = calc_step_start(time, pitch_velocity)
plt.plot(time, pitch_velocity, marker='.')
plt.axhline(final_value, color='red', linestyle='-')
plt.axhline(0.63*final_value, color='magenta', linestyle='-')
plt.axvline(tau_time, color='lime', linestyle='-')
plt.axvline(start_time, color='black', linestyle='-')
plt.title("Pitch Velocity vs. Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Velocity (degrees/second)")
plt.grid(True)

plt.subplot(2, 2, 4)
time = data['time'][pitch_indices[1][0]:pitch_indices[1][1]].tolist()
pitch_velocity = data['pitch_velocity'][pitch_indices[1][0]:pitch_indices[1][1]].tolist()
final_value = calc_final_value(pitch_velocity, 20)
SSG = final_value / step_magnitude
tau_time = calc_time_constant(time, pitch_velocity, final_value)
start_time = calc_step_start(time, pitch_velocity)
plt.plot(time, pitch_velocity, marker='.')
plt.axhline(y=final_value, color='red', linestyle='-')
plt.axhline(y=(0.63*final_value), color='magenta', linestyle='-')
plt.axvline(x=tau_time, color='lime', linestyle='-')
plt.axvline(start_time, color='black', linestyle='-')
plt.title("Pitch Velocity vs. Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Velocity (degrees/second)")
plt.grid(True)
plt.tight_layout()

# Large plot for transfer function calculation
plt.figure(figsize=(10, 5))
time = data['time'][yaw_indices[0][0]:yaw_indices[0][1]].tolist()
yaw_velocity = data['yaw_velocity'][yaw_indices[0][0]:yaw_indices[0][1]].tolist()
final_value = calc_final_value(yaw_velocity, 20)
SSG = final_value / step_magnitude
tau_time = calc_time_constant(time, yaw_velocity, final_value)
start_time = calc_step_start(time, yaw_velocity)
plt.plot(time, yaw_velocity, marker='.')
plt.axhline(final_value, color='red', linestyle='-', label=r'$F_v$')
plt.axhline(0.63*final_value, color='magenta', linestyle='-', label=r'63% $F_v$')
plt.axvline(tau_time, color='lime', linestyle='-', label=r'$\tau$')
plt.axvline(start_time, color='black', linestyle='-', label=r'$t=0$')
plt.title("Yaw Velocity vs. Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Velocity (degrees/second)")
plt.legend()
plt.grid(True)
plt.tight_layout()

# Subplots for transfer function comparison
plt.figure(figsize=(10, 5))
plt.subplot(2, 2, 1)
time = data['time'][yaw_indices[0][0]:yaw_indices[0][1]].tolist()
yaw_velocity = data['yaw_velocity'][yaw_indices[0][0]:yaw_indices[0][1]].tolist()
final_value = calc_final_value(yaw_velocity, 20)
tau_time = calc_time_constant(time, yaw_velocity, final_value)
start_time = calc_step_start(time, yaw_velocity)
SSG = final_value / step_magnitude
tau = tau_time - start_time
a = 1 / tau
b = SSG * a
num = a  # numerator coefficient a
den = [1, b]  # denominator coefficients (s + b)
# sys = ct.TransferFunction(num, den)
# x, y = generate_step(time, sys)
# print(x)
# print(y)
plt.plot(time, yaw_velocity, marker='.')
# plt.plot(x, y)
plt.title("Yaw Velocity vs. Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Velocity (degrees/second)")
plt.grid(True)

plt.subplot(2, 2, 2)
time = data['time'][yaw_indices[1][0]:yaw_indices[1][1]].tolist()
yaw_velocity = data['yaw_velocity'][yaw_indices[1][0]:yaw_indices[1][1]].tolist()
final_value = calc_final_value(yaw_velocity, 20)
tau_time = calc_time_constant(time, yaw_velocity, final_value)
start_time = calc_step_start(time, yaw_velocity)
SSG = final_value / step_magnitude
tau = tau_time - start_time
plt.plot(time, yaw_velocity, marker='.')
plt.title("Yaw Velocity vs. Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Velocity (degrees/second)")
plt.grid(True)

plt.subplot(2, 2, 3)
time = data['time'][pitch_indices[0][0]:pitch_indices[0][1]].tolist()
pitch_velocity = data['pitch_velocity'][pitch_indices[0][0]:pitch_indices[0][1]].tolist()
final_value = calc_final_value(pitch_velocity, 20)
tau_time = calc_time_constant(time, pitch_velocity, final_value)
start_time = calc_step_start(time, pitch_velocity)
plt.plot(time, pitch_velocity, marker='.')
SSG = final_value / step_magnitude
tau = tau_time - start_time
plt.title("Pitch Velocity vs. Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Velocity (degrees/second)")
plt.grid(True)

plt.subplot(2, 2, 4)
time = data['time'][pitch_indices[1][0]:pitch_indices[1][1]].tolist()
pitch_velocity = data['pitch_velocity'][pitch_indices[1][0]:pitch_indices[1][1]].tolist()
final_value = calc_final_value(pitch_velocity, 20)
SSG = final_value / step_magnitude
tau_time = calc_time_constant(time, pitch_velocity, final_value)
start_time = calc_step_start(time, pitch_velocity)
plt.plot(time, pitch_velocity, marker='.')
SSG = final_value / step_magnitude
tau = tau_time - start_time
plt.title("Pitch Velocity vs. Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Velocity (degrees/second)")
plt.grid(True)
plt.tight_layout()

# Display plots
plt.show()