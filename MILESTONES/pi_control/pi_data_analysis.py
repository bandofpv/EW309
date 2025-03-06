# pi_data_analysis.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("data.csv")
# data = pd.read_csv("data1.csv")

# Manually set values
start_index = 6; end_index = 27; yaw_des = 20; pitch_des = 10  # data.csv
# start_index = 6; end_index = 38;
yaw_des = 40; pitch_des = 20  # data1.csv

sampling_rate = 10  # Hz

# Calculate settling of step response (time of intersection at +/- 2% final value)
def calc_Ts(time, position, final_value):
    x = np.linspace(time[0], time[-1], 1000)  
    y = np.interp(x, time, position)  # interpolate positions
    top_difference = np.abs(y - (1.02*final_value))  # calculate difference between position and +2% of final value
    bottom_difference = np.abs(y - (0.98*final_value))  # calculate difference between position and -2% of final value
    top_approx_index = np.argmin(top_difference)  # find index with least difference
    bottom_approx_index = np.argmin(bottom_difference)  # find index with least difference
    top_approx_time = x[top_approx_index]  # calculate the settling
    bottom_approx_time = x[bottom_approx_index]  # calculate the settling time
    return max(top_approx_time, bottom_approx_time)  # return latest value

time_stamps = np.arange(len(data['yaw'][start_index:end_index])) / sampling_rate  # calculate time stamps for plot

yaw_SSE = yaw_des - np.mean(data['yaw'][end_index-4:end_index])
pitch_SSE = pitch_des - np.mean(data['pitch'][end_index-4:end_index])
yaw_OS = ((data['yaw'].max()-yaw_des) / yaw_des) * 100
pitch_OS = ((data['pitch'].max()-pitch_des) / pitch_des) * 100
yaw_Ts = calc_Ts(time_stamps, data['yaw'][start_index:end_index], data['yaw'][end_index])
pitch_Ts = calc_Ts(time_stamps, data['pitch'][start_index:end_index], data['pitch'][end_index])

print("Yaw SSE:", yaw_SSE)
print("Pitch SSE:", pitch_SSE)
print("Yaw %OS:", yaw_OS)
print("Pitch %OS:", pitch_OS)
print("Yaw Ts:", yaw_Ts)
print("Pitch Ts:", pitch_Ts)

# Subplot for Position vs. Time
plt.figure(figsize=(10, 5))
plt.subplot(2, 1, 1)
plt.plot(time_stamps, data['yaw'][start_index:end_index], marker='.', label='Yaw')
plt.plot(time_stamps, data['pitch'][start_index:end_index], marker='.', label='Pitch')
plt.axhline(data['pitch'][end_index]*1.02)
plt.axhline(data['pitch'][end_index]*0.98)
plt.title("Position vs. Time")
plt.xlabel("Time (sec)")
plt.ylabel("Position (deg)")
plt.grid(True)
plt.legend()

# Subplot for Duty Cycle
plt.subplot(2, 1, 2)
plt.plot(time_stamps, data['yaw_duty_cycle'][start_index:end_index], marker='.', label='Yaw')
plt.plot(time_stamps, data['pitch_duty_cycle'][start_index:end_index], marker='.', label='Pitch')
plt.title("Duty Cycle vs. Time")
plt.xlabel("Time (sec)")
plt.ylabel("Duty Cycle (%)")
plt.grid(True)
plt.legend()

# Display plot
plt.tight_layout()
plt.show()
