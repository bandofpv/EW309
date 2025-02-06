# calc_TF_data_analysis.py

import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("data.csv")

def find_bump_indices(data):
    """
    Finds the start and end indices of step response
    """
    indices = []
    in_bump = False
    for i in range(len(data)):
        if abs(data[i]) > 20:  # Check for values above 20 deg/s
            if not in_bump:
                start_index = i
                in_bump = True
        elif in_bump:
            end_index = i
            indices.append([start_index-20, end_index+20])  # add some padding
            in_bump = False
    return indices

yaw_indices = find_bump_indices(data['yaw_velocity'])
pitch_indices = find_bump_indices(data['pitch_velocity'])

# Subplot for Position vs. Time
plt.figure(figsize=(10, 5))  # set figure size 
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

# Subplots for step inputs
plt.figure(figsize=(10, 5))  # set figure size
plt.subplot(2, 2, 1)
plt.plot(data['time'][yaw_indices[0][0]:yaw_indices[0][1]], data['yaw_velocity'][yaw_indices[0][0]:yaw_indices[0][1]], marker='.')
plt.title("Yaw Velocity vs. Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Velocity (degrees/second)")
plt.grid(True)

plt.subplot(2, 2, 2)
plt.plot(data['time'][yaw_indices[1][0]:yaw_indices[1][1]], data['yaw_velocity'][yaw_indices[1][0]:yaw_indices[1][1]], marker='.')
plt.title("Yaw Velocity vs. Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Velocity (degrees/second)")
plt.grid(True)

plt.subplot(2, 2, 3)
plt.plot(data['time'][pitch_indices[0][0]:pitch_indices[0][1]], data['pitch_velocity'][pitch_indices[0][0]:pitch_indices[0][1]], marker='.')
plt.title("Pitch Velocity vs. Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Velocity (degrees/second)")
plt.grid(True)

plt.subplot(2, 2, 4)
plt.plot(data['time'][pitch_indices[1][0]:pitch_indices[1][1]], data['pitch_velocity'][pitch_indices[1][0]:pitch_indices[1][1]], marker='.')
plt.title("Pitch Velocity vs. Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Velocity (degrees/second)")
plt.grid(True)
plt.tight_layout()
plt.show()
