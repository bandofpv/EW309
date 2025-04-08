# train_data_analysis.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("results.csv")
# data = pd.read_csv("results1.csv")

# Subplot for mAP_0.5 vs. Epoch
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.plot(data['epoch'], data['metrics/mAP50(B)'], marker='.')
plt.title("mAP_0.5 vs. Epoch")
plt.xlabel("Epoch")
plt.ylabel("mAP_0.5")
plt.grid(True)

# Subplot for mAP_0.5:0.95 vs. Epoch
plt.subplot(1, 2, 2)
plt.plot(data['epoch'], data['metrics/mAP50-95(B)'], marker='.')
plt.title("mAP_0.5:0.95 vs. Epoch")
plt.xlabel("Epoch")
plt.ylabel("mAP_0.5:0.95")
plt.grid(True)

# Display plot
plt.tight_layout()
plt.show()