# calc_PID_gains.py

import numpy as np
import pandas as pd
import control as ct
import control.matlab as mtlb
from math import log, sqrt, pi, tan
from statistics import mean
import matplotlib.pyplot as plt

# DC Motor Parameters
a = 7.979
b = 44.52

# Design Requirements
req_Ts = 1.5
req_OS = 20

# Calculate Design Point s_d
sigma = 4/req_Ts;
zeta = -log(req_OS/100) / sqrt(pi**2 + log(req_OS/100)**2)
w_n = sigma/zeta
w = w_n*sqrt(1-zeta**2)
s_d = -sigma + w*1j

# Evaluate Plant TF at s_d
G_p = ct.TransferFunction([b], [1, a, 0])
G_p_sd = mtlb.evalfr(G_p, s_d)

# Calculate z_PI
phi_ULG = np.angle(G_p_sd)
phi_PI = -pi - phi_ULG
z_PI = sigma + w/tan(phi_PI + np.angle(s_d))

# Evaluate PI Controller TF at s_d
G_c = ct.TransferFunction([1, z_PI], [1, 0])
G_c_sd = mtlb.evalfr(G_c, s_d)

# Evaluate Gain K
K = abs(1/(G_c_sd*G_p_sd))

print(s_d)
print(G_p)
print(G_p_sd)
print(phi_ULG, phi_PI, z_PI)
print(G_c, G_c_sd)
print(K, K*z_PI)

OLTF = G_c*G_p # blocks in cascade

print(OLTF)

# generate the RL for positive K
rl_plot = ct.root_locus_plot(OLTF)
rl_plot.set_plot_title("Root Locus")

T = ct.feedback(K*OLTF)
t = np.linspace(0, 2, 1000)
x, y = ct.step_response(T, t)
plt.figure(figsize=(10, 5))
plt.plot(x, y)
plt.title("Step Response")
plt.xlabel("Time (seconds)")
plt.ylabel("Position (deg)")
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.show()