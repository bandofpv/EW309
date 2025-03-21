# aim_and_fire_data_analysis.py

import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("data.csv")

# Manually set values
start_index = 3; end_index = 89;

time_stamps = data['time'].iloc[start_index:end_index].reset_index(drop=True)
time_stamps -= time_stamps.iloc[0]
time_stamps = time_stamps.to_numpy()

# Subplot for Position vs. Time
plt.figure(figsize=(10, 5))
plt.subplot(2, 1, 1)
plt.plot(time_stamps, data['yaw'][start_index:end_index], marker='.', label='Yaw')
plt.plot(time_stamps, data['pitch'][start_index:end_index], marker='.', label='Pitch')
plt.title("Position vs. Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Position (degrees)")
plt.grid(True)
plt.legend()

# Subplot for Angular Velocity
plt.subplot(2, 1, 2)
plt.plot(time_stamps, data['yaw_velocity'][start_index:end_index], marker='.', label='Yaw')
plt.plot(time_stamps, data['pitch_velocity'][start_index:end_index], marker='.', label='Pitch')
plt.title("Angular Velocity vs. Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Angular Velocity (degrees/sec)")
plt.grid(True)
plt.legend( )
 
# Display plot
plt.tight_layout()
plt.show()