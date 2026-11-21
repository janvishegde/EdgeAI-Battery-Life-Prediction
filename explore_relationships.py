
import pandas as pd
import matplotlib.pyplot as plt

# Load our dataset
df = pd.read_csv("team_06_train.csv")

# Input features
features = [
    "battery_v",
    "temp_c",
    "rings_per_day",
    "wifi_rssi_dbm",
    "age_months"
]

# Create a figure containing six plotting areas
fig, axes = plt.subplots(2, 3, figsize=(15, 9))

# Convert the 2D array of axes into a 1D array
axes = axes.flatten()

# Plot each input feature against days_left
for i, feature in enumerate(features):
    axes[i].scatter(
        df[feature],
        df["days_left"],
        alpha=0.5
    )

    axes[i].set_xlabel(feature)
    axes[i].set_ylabel("days_left")
    axes[i].set_title(f"{feature} vs days_left")
    axes[i].grid(True)

# Hide the unused sixth plotting area
axes[5].axis("off")

plt.tight_layout()

# Save the figure
plt.savefig("feature_relationships.png", dpi=150)

print("Saved feature_relationships.png")
