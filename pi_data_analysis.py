# pi_data_analysis.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("data.csv")
sampling_rate = 10  # Hz

# Manually set values
start_index = 6; end_index = 30  # data.csv

yaw_SSE = 20 - np.mean(data['yaw'][end_index-4:end_index])
pitch_SSE = 10 - np.mean(data['pitch'][end_index-4:end_index])

print("Yaw SSE:", yaw_SSE)
print("Pitch SSE:", pitch_SSE)

time_stamps = np.arange(len(data['yaw'][start_index:end_index])) / sampling_rate  # calculate time stamps for plot

# Subplot for Position vs. Time
plt.figure(figsize=(10, 5))
plt.subplot(2, 1, 1)
plt.plot(time_stamps, data['yaw'][start_index:end_index], marker='.', label='Yaw')
plt.plot(time_stamps, data['pitch'][start_index:end_index], marker='.', label='Pitch')
plt.title("Position vs. Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Angular Velocity (degrees/sec)")
plt.grid(True)
plt.legend()

# Subplot for Duty Cycle
plt.subplot(2, 1, 2)
plt.plot(time_stamps, data['yaw_duty_cycle'][start_index:end_index], marker='.', label='Yaw')
plt.plot(time_stamps, data['pitch_duty_cycle'][start_index:end_index], marker='.', label='Pitch')
plt.title("Duty Cycle vs. Time")
plt.xlabel("Time (sec)")
plt.ylabel("Motor Voltage (V)")
plt.grid(True)
plt.legend()

# Display plot
plt.tight_layout()
plt.show()
