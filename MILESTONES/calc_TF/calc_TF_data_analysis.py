# calc_TF_data_analysis.py

import numpy as np
import pandas as pd
import control as ct
from statistics import mean
import matplotlib.pyplot as plt

data = pd.read_csv("data.csv")
step_magnitude = 0.3 * 12  # duty cycle times voltage

# Finds the start and end indices of step response
def find_step_indices(data, threshold):
    indices = []
    in_bump = False
    for i in range(len(data)):  
        if abs(data[i]) > threshold:  # check for values above threshold in deg/s
            if not in_bump:
                start_index = i
                in_bump = True
        elif in_bump:
            end_index = i
            indices.append([start_index-5, end_index+5])  # add some padding
            in_bump = False
    return indices

# Calculate final value of step response
def calc_final_value(data, threshold):
    for i in range(len(data)):
        if abs(data[i]) > threshold:  # check for values above threshold in deg/s
            final_value_index = i
    final_value = mean(data[final_value_index-4:final_value_index])  # calculate final value based on mean
    return final_value, final_value_index

# Calculate time constant of step response (time of intersection at 63% final value)
def calc_time_constant(time, velocity, final_value):
    x = np.linspace(time[0], time[-3], 1000)  # times to interpolate with (start of bump)
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

# Generate step response
def generate_step(transfer_function, start_time, end_time, magnitude, init_condition=0):
    time = np.linspace(start_time, end_time, 1000)  # times to step through (removing padding)
    x, y = ct.step_response(transfer_function, time, X0=init_condition)  # calculate unit step response
    return x, y*magnitude
    
yaw_indices = find_step_indices(data['yaw_velocity'], 10)
pitch_indices = find_step_indices(data['pitch_velocity'], 10)

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
plt.plot(data['time'], data['pitch_velocity'], marker='.', label='Pitch')
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
final_value, _ = calc_final_value(yaw_velocity, 15)
tau_time = calc_time_constant(time, yaw_velocity, final_value)
start_time = calc_step_start(time, yaw_velocity)
SSG1 = abs(final_value / step_magnitude)  # calculate SSG
tau1 = tau_time - start_time  # calculate time constant
plt.plot(time, yaw_velocity, marker='.')
plt.axhline(final_value, color='red', linestyle='-')
plt.axhline(0.63*final_value, color='magenta', linestyle='-')
plt.axvline(tau_time, color='lime', linestyle='-')
plt.axvline(start_time, color='black', linestyle='-')
plt.title("Yaw Angular Velocity vs. Time (CW)")
plt.xlabel("Time (seconds)")
plt.ylabel("Angular Velocity (deg/s)")
plt.grid(True)
print(f"Final value: {final_value}")

plt.subplot(2, 2, 2)
time = data['time'][yaw_indices[1][0]:yaw_indices[1][1]].tolist()
yaw_velocity = data['yaw_velocity'][yaw_indices[1][0]:yaw_indices[1][1]].tolist()
final_value, _ = calc_final_value(yaw_velocity, 15)
tau_time = calc_time_constant(time, yaw_velocity, final_value)
start_time = calc_step_start(time, yaw_velocity)
SSG2 = abs(final_value / step_magnitude)  # calculate SSG
tau2 = tau_time - start_time  # calculate time constant
plt.plot(time, yaw_velocity, marker='.')
plt.axhline(final_value, color='red', linestyle='-')
plt.axhline(0.63*final_value, color='magenta', linestyle='-')
plt.axvline(tau_time, color='lime', linestyle='-')
plt.axvline(start_time, color='black', linestyle='-')
plt.title("Yaw Angular Velocity vs. Time (CCW)")
plt.xlabel("Time (seconds)")
plt.ylabel("Angular Velocity (deg/s)")
plt.grid(True)
print(f"Final value: {final_value}")

# Calculate yaw transfer function
print("Yaw Time Constant:", mean([tau1, tau2]))
a = 1 / mean([tau1, tau2])  # calulate a coefficient using average tau
b = mean([SSG1, SSG2]) * a  # calulate b coefficient using average SSG
num = b  # numerator coefficient b
den = [1, a, 0]  # denominator coefficients (s^2 + as)
yaw_pos_tf = ct.TransferFunction(num, den)  # position transfer function
print("Yaw Position Transfer Function: ", yaw_pos_tf)
num = b  # numerator coefficient b
den = [1, a]  # denominator coefficients (s + a)
yaw_vel_tf = ct.TransferFunction(num, den)  # velocity transfer function
print("Yaw Velocity Transfer Function: ", yaw_vel_tf)

plt.subplot(2, 2, 3)
time = data['time'][pitch_indices[0][0]:pitch_indices[0][1]].tolist()
pitch_velocity = data['pitch_velocity'][pitch_indices[0][0]:pitch_indices[0][1]].tolist()
final_value, _ = calc_final_value(pitch_velocity, 15)
tau_time = calc_time_constant(time, pitch_velocity, final_value)
start_time = calc_step_start(time, pitch_velocity)
SSG1 = abs(final_value / step_magnitude)  # calculate SSG
tau1 = tau_time - start_time  # calculate time constant
plt.plot(time, pitch_velocity, marker='.')
plt.axhline(final_value, color='red', linestyle='-')
plt.axhline(0.63*final_value, color='magenta', linestyle='-')
plt.axvline(tau_time, color='lime', linestyle='-')
plt.axvline(start_time, color='black', linestyle='-')
plt.title("Pitch Angular Velocity vs. Time (Up)")
plt.xlabel("Time (seconds)")
plt.ylabel("Angular Velocity (deg/s)")
plt.grid(True)
print(f"Final value: {final_value}")

plt.subplot(2, 2, 4)
time = data['time'][pitch_indices[1][0]:pitch_indices[1][1]].tolist()
pitch_velocity = data['pitch_velocity'][pitch_indices[1][0]:pitch_indices[1][1]].tolist()
final_value, _ = calc_final_value(pitch_velocity, 15)
tau_time = calc_time_constant(time, pitch_velocity, final_value)
start_time = calc_step_start(time, pitch_velocity)
SSG2 = abs(final_value / step_magnitude)  # calculate SSG
tau2 = tau_time - start_time  # calculate time constant
plt.plot(time, pitch_velocity, marker='.')
plt.axhline(y=final_value, color='red', linestyle='-')
plt.axhline(y=(0.63*final_value), color='magenta', linestyle='-')
plt.axvline(x=tau_time, color='lime', linestyle='-')
plt.axvline(start_time, color='black', linestyle='-')
plt.title("Pitch Angular Velocity vs. Time (Down)")
plt.xlabel("Time (seconds)")
plt.ylabel("Angular Velocity (deg/s)")
plt.grid(True)
plt.tight_layout()
print(f"Final value: {final_value}")

# Calculate pitch transfer function
print("Pitch Time Constant:", mean([tau1, tau2]))
a = 1 / mean([tau1, tau2])  # calulate a coefficient using average tau
b = mean([SSG1, SSG2]) * a  # calulate b coefficient using average SSG
num = b  # numerator coefficient b
den = [1, a, 0]  # denominator coefficients (s^2 + as)
pitch_pos_tf = ct.TransferFunction(num, den)  # position transfer function
print("Pitch Position Transfer Function: ", pitch_pos_tf)
num = b  # numerator coefficient b
den = [1, a]  # denominator coefficients (s + a)
pitch_vel_tf = ct.TransferFunction(num, den)  # velocity transfer function
print("Pitch Velocity Transfer Function: ", pitch_vel_tf)

# Large plot for transfer function calculation
plt.figure(figsize=(10, 5))
time = data['time'][pitch_indices[1][0]:pitch_indices[1][1]].tolist()
pitch_velocity = data['pitch_velocity'][pitch_indices[1][0]:pitch_indices[1][1]].tolist()
final_value, _ = calc_final_value(pitch_velocity, 15)
SSG = final_value / step_magnitude
tau_time = calc_time_constant(time, pitch_velocity, final_value)
start_time = calc_step_start(time, pitch_velocity)
plt.plot(time, pitch_velocity, marker='.')
plt.axhline(final_value, color='red', linestyle='-', label=r'$F_v$')
plt.axhline(0.63*final_value, color='magenta', linestyle='-', label=r'63% $F_v$')
plt.axvline(tau_time, color='lime', linestyle='-', label=r'$\tau$')
plt.axvline(start_time, color='black', linestyle='-', label=r'$t=0$')
plt.title("Pitch Angular Velocity vs. Time (Down)")
plt.xlabel("Time (seconds)")
plt.ylabel("Angular Velocity (deg/s)")
plt.legend()
plt.grid(True)
plt.tight_layout()

# Subplots for velocity transfer function comparison
plt.figure(figsize=(10, 5))
plt.subplot(2, 2, 1)
time = data['time'][yaw_indices[0][0]:yaw_indices[0][1]].tolist()
yaw_velocity = data['yaw_velocity'][yaw_indices[0][0]:yaw_indices[0][1]].tolist()
_, final_index = calc_final_value(yaw_velocity, 15)
start_time = calc_step_start(time, yaw_velocity)
t, step_response = generate_step(yaw_vel_tf, start_time, time[final_index], step_magnitude)
plt.plot(time, yaw_velocity, marker='.')
plt.plot(t, step_response)
plt.title("Yaw Angular Velocity vs. Time (CW)")
plt.xlabel("Time (seconds)")
plt.ylabel("Angular Velocity (deg/s)")
plt.grid(True)

plt.subplot(2, 2, 2)
time = data['time'][yaw_indices[1][0]:yaw_indices[1][1]].tolist()
yaw_velocity = data['yaw_velocity'][yaw_indices[1][0]:yaw_indices[1][1]].tolist()
_, final_index = calc_final_value(yaw_velocity, 15)
start_time = calc_step_start(time, yaw_velocity)
t, step_response = generate_step(yaw_vel_tf, start_time, time[final_index], -step_magnitude)
plt.plot(time, yaw_velocity, marker='.')
plt.plot(t, step_response)
plt.title("Yaw Angular Velocity vs. Time (CCW)")
plt.xlabel("Time (seconds)")
plt.ylabel("Angular Velocity (deg/s)")
plt.grid(True)

plt.subplot(2, 2, 3)
time = data['time'][pitch_indices[0][0]:pitch_indices[0][1]].tolist()
pitch_velocity = data['pitch_velocity'][pitch_indices[0][0]:pitch_indices[0][1]].tolist()
_, final_index = calc_final_value(pitch_velocity, 15)
start_time = calc_step_start(time, pitch_velocity)
t, step_response = generate_step(pitch_vel_tf, start_time, time[final_index], -step_magnitude)
plt.plot(time, pitch_velocity, marker='.')
plt.plot(t, step_response)
plt.title("Pitch Angular Velocity vs. Time (Up)")
plt.xlabel("Time (seconds)")
plt.ylabel("Angular Velocity (deg/s)")
plt.grid(True)

plt.subplot(2, 2, 4)
time = data['time'][pitch_indices[1][0]:pitch_indices[1][1]].tolist()
pitch_velocity = data['pitch_velocity'][pitch_indices[1][0]:pitch_indices[1][1]].tolist()
_, final_index = calc_final_value(pitch_velocity, 15)
start_time = calc_step_start(time, pitch_velocity)
t, step_response = generate_step(pitch_vel_tf, start_time, time[final_index], step_magnitude)
plt.plot(time, pitch_velocity, marker='.')
plt.plot(t, step_response)
plt.title("Pitch Angular Velocity vs. Time (Down)")
plt.xlabel("Time (seconds)")
plt.ylabel("Angular Velocity (deg/s)")
plt.grid(True)
plt.tight_layout()

# Large plot for velocity transfer function comparison
plt.figure(figsize=(10, 5))
time = data['time'][yaw_indices[0][0]:yaw_indices[0][1]].tolist()
yaw_velocity = data['yaw_velocity'][yaw_indices[0][0]:yaw_indices[0][1]].tolist()
final_value, final_index = calc_final_value(yaw_velocity, 15)
tau_time = calc_time_constant(time, yaw_velocity, final_value)
start_time = calc_step_start(time, yaw_velocity)
t, step_response = generate_step(yaw_vel_tf, start_time, time[final_index], step_magnitude)
plt.plot(time, yaw_velocity, marker='.', label='Experimental Data')
plt.plot(t, step_response, label='Estimated Step Response')
plt.title("Yaw Angular Velocity vs. Time (CW)")
plt.xlabel("Time (seconds)")
plt.ylabel("Angular Velocity (deg/s)")
plt.grid(True)
plt.legend()
plt.tight_layout()

# Subplots for position transfer function comparison
plt.figure(figsize=(10, 5))
plt.subplot(2, 2, 1)
time = data['time'][yaw_indices[0][0]:yaw_indices[0][1]].tolist()
yaw = data['yaw'][yaw_indices[0][0]:yaw_indices[0][1]].tolist()
yaw_velocity = data['yaw_velocity'][yaw_indices[0][0]:yaw_indices[0][1]].tolist()
_, final_index = calc_final_value(yaw_velocity, 15)
start_time = calc_step_start(time, yaw_velocity)
t, step_response = generate_step(yaw_pos_tf, start_time, time[final_index+1], step_magnitude)
plt.plot(time, yaw, marker='.')
plt.plot(t, step_response+yaw[time.index(start_time)])
plt.title("Yaw Position vs. Time (CW)")
plt.xlabel("Time (seconds)")
plt.ylabel("Position (degrees)")
plt.grid(True)

plt.subplot(2, 2, 2)
time = data['time'][yaw_indices[1][0]:yaw_indices[1][1]].tolist()
yaw = data['yaw'][yaw_indices[1][0]:yaw_indices[1][1]].tolist()
yaw_velocity = data['yaw_velocity'][yaw_indices[0][0]:yaw_indices[0][1]].tolist()
_, final_index = calc_final_value(yaw_velocity, 15)
start_time = calc_step_start(time, yaw_velocity)
t, step_response = generate_step(yaw_pos_tf, start_time, time[final_index+1], -step_magnitude)
plt.plot(time, yaw, marker='.')
plt.plot(t, step_response+yaw[time.index(start_time)])
plt.title("Yaw Position vs. Time (CCW)")
plt.xlabel("Time (seconds)")
plt.ylabel("Position (degrees)")
plt.grid(True)

plt.subplot(2, 2, 3)
time = data['time'][pitch_indices[0][0]:pitch_indices[0][1]].tolist()
pitch = data['pitch'][pitch_indices[0][0]:pitch_indices[0][1]].tolist()
pitch_velocity = data['pitch_velocity'][pitch_indices[0][0]:pitch_indices[0][1]].tolist()
_, final_index = calc_final_value(pitch_velocity, 15)
start_time = calc_step_start(time, pitch_velocity)
t, step_response = generate_step(pitch_pos_tf, start_time, time[final_index+1], -step_magnitude)
plt.plot(time, pitch, marker='.')
plt.plot(t, step_response+pitch[time.index(start_time)])
plt.title("Pitch Position vs. Time (Up)")
plt.xlabel("Time (seconds)")
plt.ylabel("Position (degrees)")
plt.grid(True)

plt.subplot(2, 2, 4)
time = data['time'][pitch_indices[1][0]:pitch_indices[1][1]].tolist()
pitch = data['pitch'][pitch_indices[1][0]:pitch_indices[1][1]].tolist()
pitch_velocity = data['pitch_velocity'][pitch_indices[1][0]:pitch_indices[1][1]].tolist()
_, final_index = calc_final_value(pitch_velocity, 15)
start_time = calc_step_start(time, pitch_velocity)
t, step_response = generate_step(pitch_pos_tf, start_time, time[final_index+1], step_magnitude)
plt.plot(time, pitch, marker='.')
plt.plot(t, step_response+pitch[time.index(start_time)])
plt.title("Pitch Position vs. Time (Down)")
plt.xlabel("Time (seconds)")
plt.ylabel("Position (degrees)")
plt.grid(True)
plt.tight_layout()

# Large for position transfer function comparison
plt.figure(figsize=(10, 5))
time = data['time'][yaw_indices[0][0]:yaw_indices[0][1]].tolist()
yaw = data['yaw'][yaw_indices[0][0]:yaw_indices[0][1]].tolist()
yaw_velocity = data['yaw_velocity'][yaw_indices[0][0]:yaw_indices[0][1]].tolist()
_, final_index = calc_final_value(yaw_velocity, 15)
start_time = calc_step_start(time, yaw_velocity)
t, step_response = generate_step(yaw_pos_tf, start_time, time[final_index+1], step_magnitude)
plt.plot(time, yaw, marker='.', label='Experimental Data')
plt.plot(t, step_response+yaw[time.index(start_time)], label='Estimated Step Response')
plt.title("Yaw Position vs. Time (CW)")
plt.xlabel("Time (seconds)")
plt.ylabel("Position (degrees)")
plt.legend()
plt.grid(True)

# Display plots
plt.show()