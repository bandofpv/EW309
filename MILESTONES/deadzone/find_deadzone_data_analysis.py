# find_deadzone_data_analysis.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("deadzone_data.csv")
sampling_rate = 10  # Hz

# Finds the start and end indices of step response
def find_peak_indices(data, threshold):
    indices = []
    in_bump = False
    for i in range(len(data)):  
        if abs(data[i]) > threshold:  # check for values above threshold in deg/s
            if not in_bump:
                in_bump = True
        elif in_bump:
            end_index = i-1
            indices.append(end_index)  # add some padding
            in_bump = False
    indices.append(len(data)-1)  # add final index value
    return indices

peaks = find_peak_indices(data['motor_voltage'], 2)
deadzones = data['motor_voltage'].values[peaks] / 12
print("Deadzones:", deadzones)

time_stamps = np.arange(len(data['yaw_velocity'])) / sampling_rate  # calculate time stamps for plot

# Subplot for Angular Velocity vs. Time
plt.figure(figsize=(10, 5))
plt.subplot(2, 1, 1)
plt.plot(time_stamps, data['yaw_velocity'], marker='.', label='Yaw')
plt.plot(time_stamps, data['pitch_velocity'], marker='.', label='Pitch')
plt.title("Angular Velocity vs. Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Angular Velocity (degrees/sec)")
plt.grid(True)
plt.legend()

# Subplot for Motor Voltage
plt.subplot(2, 1, 2)
plt.plot(time_stamps, (data['motor_voltage']/12)*100, marker='.')
plt.title("Duty Cycle vs. Time")
plt.xlabel("Time (sec)")
plt.ylabel("Duty Cycle (%)")
plt.grid(True)

# Display plot
plt.tight_layout()
plt.show()