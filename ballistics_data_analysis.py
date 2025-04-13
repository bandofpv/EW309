# balistics_data_analysis.py

import math
import numpy as np
import matplotlib.pyplot as plt

target_range = [304.8, 457.2, 609.6]  # cm
x_bias = [-9.75, -7.59, -15.17]  # cm
y_bias = [-26.08, -46.03, -74.35]  # cm
S_p = [3.41, 5.78, 7.26]  # cm
CEP_50 = [4.01, 6.81, 8.55]  # cm

# Fit polynomials (degree 2 for example)
sp_coeffs = np.polyfit(target_range, S_p, deg=2)
x_coeffs = np.polyfit(target_range, x_bias, deg=2)
y_coeffs = np.polyfit(target_range, y_bias, deg=2)
sp_poly = np.poly1d(sp_coeffs)
x_poly = np.poly1d(x_coeffs)
y_poly = np.poly1d(y_coeffs)

# Generate values for plotting the fitted curve
target_range_smooth = np.linspace(min(target_range), max(target_range), 200)

# Compute fitted values
sp_fit = sp_poly(target_range_smooth)
x_fit = x_poly(target_range_smooth)
y_fit = y_poly(target_range_smooth)

# Plot Target Range vs. Precision Error
plt.figure(figsize=(10, 5))
plt.scatter(target_range, S_p, label='Precision Error', color='blue')
plt.plot(target_range_smooth, sp_fit, label='Fitted Curve', color='red')
plt.title("Target Range vs. Precision Error")
plt.xlabel("Target Range (cm)")
plt.ylabel("Precision Error (cm)")
plt.grid(True)
plt.legend()

# Subplot Target Range vs. X-Bias
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.scatter(target_range, x_bias, label='X-Bias', color='blue')
plt.plot(target_range_smooth, x_fit, label='Fitted Curve', color='red')
plt.title("Target Range vs. X-Bias")
plt.xlabel("Target Range (cm)")
plt.ylabel("X-Bias (cm)")
plt.grid(True)
plt.legend()

# Subplot Target Range vs. Y-Bias
plt.subplot(1, 2, 2)
plt.scatter(target_range, y_bias, label='Y-Bias', color='blue')
plt.plot(target_range_smooth, y_fit, label='Fitted Curve', color='red')
plt.title("Target Range vs. Y-Bias")
plt.xlabel("Target Range (cm)")
plt.ylabel("Y-Bias (cm)")
plt.grid(True)
plt.legend()

# Display plot
plt.tight_layout()
plt.show()