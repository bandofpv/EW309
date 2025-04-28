# ballistics_analysis.py

import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Wedge

# 10 ft
# x = [-6.25, -8, -9.75, -8.75, -4, -10.5, -12.25, -10.5, -11.75, -5.75, -11.75, -11.25, -8, -6, -11.5, -8.25, -10.25, -8.5, -12.5, -9.75, -18.75, -15.75, -8.25, -10.25, -9, -9, -9, -11.5, -6.75, -9]
# y = [-32.5, -29.25, -27.75, -26.5, -25.5, -25.5, -26.25, -22.25, -22, -20.25, -33, -30, -30.25, -29.5, -26.5, -26.5, -25.75, -24, -23.75, -18.25, -17.5, -21, -23.5, -26, -26.5, -26.5, -26.5, -29, -31.25, -29.5]

# 15 ft
# x = [-18, -12.25, -8.75, -7.25, -10.25, -9.75, -7.75, -9.5, -7.25, -5.5, -8, -8, -5, -0.5, -2.5, -2, -6.75, -18.5, -16.75, -13.25, -11, -7.75, -9, -7.75, -6, -6.5, -1.75, -11.25, -6, -5.75]
# y = [-58, -45.75, -38, -34.5, -55, -55.5, -56.25, -48, -49.25, -52, -46, -43, -39, -49.5, -41, -45.25, -47, -41.75, -44.25, -44.25, -43, -35, -48.5, -48, -46, -49.25, -41.75, -50.5, -46.5, -39]

# 20 ft
x = [2.5, -6, -11.75, -13.25, -15.75, -22, -22.75, -20.75, -19, -15, -4.5, -7.5, -15, -14.5, -26, -15.25, -13, -10.75, -28, -18.5, -14.5, -4.5, -8.5, -8.5, -12.5, -17, -17.5, -21.75, -26, -27.5]
y = [-86, -76.25, -72.75, -71.75, -72, -72.75, -73.5, -78.5, -80.25, -84.25, -52.25, -60.75, -64.25, -67.5, -65.5, -74, -75, -76.25, -80.5, -80.5, -83, -80.5, -75.25, -74, -74, -74, -81, -76.5, -77.25, -70.5]

# Calculate Statistics
x_bias = np.mean(x)
y_bias = np.mean(y)
x = [i - x_bias for i in x]  # correct bias
y = [i - y_bias for i in y]  # correct bias
S_x = np.std(x, ddof=1)
S_y = np.std(y, ddof=1)
S_b = math.sqrt(x_bias**2 + y_bias**2)
S_p = 0.5 * (S_x + S_y)
k = math.sqrt(-2*math.log(1-0.5))
CEP_50 = k * S_p
CI_x = 1.96 * (S_x/math.sqrt(len(x)))
CI_y = 1.96 * (S_y/math.sqrt(len(y)))

print("x-bias:", x_bias)
print("y-bias:", y_bias)
print("S_x:", S_x)
print("S_y:", S_y)
print("S_b:", S_b)
print("S_p:", S_p)
print("k:", k)
print("CEP_50:", CEP_50)
print("CI_x:", CI_x)
print("CI_y:", CI_y)

# Calculate the minimum number of shots to hit a 12.7 cm (5 in) target with a 95% of at least one hit
CEP = 12.7/2
k = CEP / S_p
p = 1 - math.exp(-0.5*(k**2))
P_one = 0.95
n = math.log(1-P_one) / math.log(1-p)
print("Number of shots:", math.ceil(n))

# Plot of shot poi and CEP
fig, ax = plt.subplots(figsize=(5, 5))
ax.scatter(x, y, color='blue', zorder=2, label='Shot POI',)
CEP_circle = Circle((0, 0), CEP_50, edgecolor='red', facecolor='none', linewidth=2, zorder=1, label='CEP 50%')
ax.add_patch(CEP_circle)
# disk = Wedge((0, 0), 4.584, 0, 360, width=1.868, facecolor='none', hatch='/', edgecolor='green', zorder=0, label='95% CI')  # 10ft
# disk = Wedge((0, 0), 7.77, 0, 360, width=3.167, facecolor='none', hatch='/', edgecolor='green', zorder=0, label='95% CI')  # 15ft
disk = Wedge((0, 0), 9.76, 0, 360, width=3.978, facecolor='none', hatch='/', edgecolor='green', zorder=0, label='95% CI')  # 20ft
ax.add_patch(disk)
ax.set_title("Ballistics Shot (20 ft)")
ax.set_xlabel("x (cm)")
ax.set_ylabel("y (cm)")
ax.grid(True)
ax.set_xlim(-25, 25)
ax.set_ylim(-25, 25)
ax.legend()

# Display plot
plt.tight_layout()
plt.show()