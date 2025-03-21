# shoot_data_analysis.py

import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("data.csv")
sampling_rate = 60  # Hz

indices = data['time'] <= 2.6

# Subplot for Slope vs. Time
plt.figure(figsize=(10, 5))
plt.subplot(2, 1, 1)
plt.plot(data['time'][indices], data['current'][indices], marker='.')
plt.title("Current vs. Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Current (milliamps)")
plt.grid(True)

# Subplot for Current vs. Time
plt.subplot(2, 1, 2)
plt.plot(data['time'][indices], data['slope'][indices], marker='.')
plt.title("Slope vs. Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Slope (amps/sec)")
plt.grid(True)

# Display plot
plt.tight_layout()
plt.show()