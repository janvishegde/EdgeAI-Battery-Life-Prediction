import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("data/team_06_train.csv")

print(df.shape)
print(df.columns)

bad_battery = df["battery_v"] == 0
bad_temp = df["temp_c"] == -127
bad_wifi = df["wifi_rssi_dbm"] == 0

print("Battery glitches:", bad_battery.sum())
print("Temperature glitches:", bad_temp.sum())
print("Wi-Fi glitches:", bad_wifi.sum())
print("Total unique affected rows:", (bad_battery | bad_temp | bad_wifi).sum())

df.hist(figsize=(15, 10), bins=30)
plt.tight_layout()
plt.savefig("histograms.png")

plt.figure()
plt.scatter(df["battery_v"], df["days_left"])
plt.xlabel("battery_v")
plt.ylabel("days_left")
plt.title("Battery Voltage vs Battery Life")
plt.savefig("battery_vs_days.png")

plt.tight_layout()
plt.savefig("battery_vs_days.png")

plt.figure()
plt.scatter(df["temp_c"], df["days_left"])
plt.xlabel("temp_c")
plt.ylabel("days_left")
plt.title("Temperature vs Battery Life")
plt.tight_layout()
plt.savefig("temp_vs_days.png")

plt.figure()
plt.scatter(df["rings_per_day"], df["days_left"])
plt.xlabel("rings_per_day")
plt.ylabel("days_left")
plt.title("Daily Ring Usage vs Battery Life")
plt.tight_layout()
plt.savefig("rings_vs_days.png")

plt.figure()
plt.scatter(df["wifi_rssi_dbm"], df["days_left"])
plt.xlabel("wifi_rssi_dbm")
plt.ylabel("days_left")
plt.title("Wi-Fi Signal vs Battery Life")
plt.tight_layout()
plt.savefig("wifi_vs_days.png")

plt.figure()
plt.scatter(df["age_months"], df["days_left"])
plt.xlabel("age_months")
plt.ylabel("days_left")
plt.title("Device Age vs Battery Life")
plt.tight_layout()
plt.savefig("age_vs_days.png")

df_clean = df[~(bad_battery | bad_temp | bad_wifi)]

print("Original rows:", len(df))
print("Clean rows:", len(df_clean))
print("Removed rows:", len(df) - len(df_clean))

y = df_clean["days_left"].to_numpy()

mean_prediction = y.mean()
mean_mae = (abs(y - mean_prediction)).mean()

print("Mean baseline MAE:", mean_mae)

X = df_clean[["battery_v", "temp_c", "rings_per_day", "wifi_rssi_dbm", "age_months"]].to_numpy()
y = df_clean["days_left"].to_numpy()

X_bias = np.column_stack((X, np.ones(len(X))))

weights = np.linalg.lstsq(X_bias, y, rcond=None)[0]

predictions = X_bias @ weights
linear_mae = np.mean(np.abs(y - predictions))

print("Linear regression MAE:", linear_mae)