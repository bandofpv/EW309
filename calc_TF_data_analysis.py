# calc_TF_data_analysis.py

import pandas as pd
import matplotlib as plt

data = pd.read_csv("data.csv")

plt.figure(figsize=(12, 6))  # set figure size 

# Subplot for Position vs. Time
plt.plot(data["time"], data["yaw"], marker='.', label='Yaw')
plt.plot(data["time"], data["pitch"], marker='.', label='Pitch')
plt.title("Position vs. Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Position (degrees)")
plt.grid(True)
plt.legend()

start_time = 0  # seconds to start analyzing data
step_duration = 0.2  # seconds
interval = 1  # seconds between step inputs
plot_time = start_time+step_duration+interval/2
time = data["time"]

plt.figure(figsize=(12, 6))  # set figure size 
plt.plot(data.loc[(time > start_time) & (time < plot_time), "time"], data.loc[(time > start_time) & (time < plot_time), "yaw_velocity"], marker='.')
plt.title("Yaw Velocity vs. Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Velocity (degrees/second)")
plt.grid(True)

plt.figure(figsize=(12, 6))  # set figure size 
plt.plot(data.loc[(time > plot_time) & (time < plot_time+step_duration+interval), "time"], data.loc[(time > plot_time) & (time < plot_time+step_duration+interval), "yaw_velocity"], marker='.')
plt.title("Yaw Velocity vs. Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Velocity (degrees/second)")
plt.grid(True)

plt.figure(figsize=(12, 6))  # set figure size 
plt.plot(data.loc[(time > plot_time+step_duration+interval) & (time < plot_time+2*(step_duration+interval)), "time"], data.loc[(time > plot_time+step_duration+interval) & (time < plot_time+2*(step_duration+interval)), "pitch_velocity"], marker='.')
plt.title("Pitch Velocity vs. Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Velocity (degrees/second)")
plt.grid(True)
plt.legend()

plt.figure(figsize=(12, 6))  # set figure size 
plt.plot(data.loc[(time > plot_time+2*(step_duration+interval)) & (time < plot_time+3*(step_duration+interval)), "time"], data.loc[(time > plot_time+2*(step_duration+interval)) & (time < plot_time+3*(step_duration+interval)), "pitch_velocity"], marker='.')
plt.title("Pitch Velocity vs. Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Velocity (degrees/second)")
plt.grid(True)
plt.legend()
plt.legend()