"""
train.py -- STARTER. Clean the data, fit baselines, train the network, save it for the server.

    python train.py --team 7 --hidden 32,32
Writes model/model.pt and model/config.json, which app/main.py loads.

Look for TODO. The training loop is given; the decisions are yours.
"""
import argparse
import json
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import torch

from app.model import FEATURES, BatteryNet

ap = argparse.ArgumentParser()
ap.add_argument("--team", type=int, required=True)
ap.add_argument("--hidden", default="32,32")
ap.add_argument("--epochs", type=int, default=1500)
a = ap.parse_args()
hidden = tuple(int(h) for h in a.hidden.split(","))

df = pd.read_csv(f"data/team_{a.team:02d}_train.csv")
# TODO Mission 1: find the sensor glitches (plot every column first!) and write a rule that
# marks them. Say in your report how many you found and why each rule is safe.
bad_battery = df["battery_v"] == 0
bad_temp = df["temp_c"] == -127
bad_wifi = df["wifi_rssi_dbm"] == 0

bad = bad_battery | bad_temp | bad_wifi

print("Battery glitches:", bad_battery.sum())
print("Temperature glitches:", bad_temp.sum())
print("Wi-Fi glitches:", bad_wifi.sum())
print(f"{len(df)} rows, {bad.sum()} glitch rows dropped")

df = df[~bad]

rng = np.random.default_rng(0)
idx = rng.permutation(len(df)); n_val = len(df) // 5
val, tr = df.iloc[idx[:n_val]], df.iloc[idx[n_val:]]
X, y = tr[FEATURES].to_numpy(np.float32), tr.days_left.to_numpy(np.float32)
Xv, yv = val[FEATURES].to_numpy(np.float32), val.days_left.to_numpy(np.float32)
# TODO Mission 2: normalisation. Why must mu and sd come from the TRAINING rows only?
mu = X.mean(axis=0)
sd = X.std(axis=0)

mae = lambda p, t: float(np.mean(np.abs(p - t)))
print(f"baseline (predict the mean): {mae(np.full_like(yv, y.mean()), yv):.2f} days")
# TODO Mission 1: a straight-line model (linear regression) as the second baseline.
# Use np.linalg.lstsq on [X, 1]. Print its validation MAE the same way as the line above.
X_bias = np.column_stack((X, np.ones(len(X))))
Xv_bias = np.column_stack((Xv, np.ones(len(Xv))))

weights = np.linalg.lstsq(X_bias, y, rcond=None)[0]
linear_predictions = Xv_bias @ weights

print(f"linear regression: {mae(linear_predictions, yv):.2f} days")
plt.figure(figsize=(6, 6))
plt.scatter(yv, linear_predictions, alpha=0.5)

plt.plot([0, 450], [0, 450], "r--")
plt.xlabel("True days_left")
plt.ylabel("Predicted days_left")
plt.title("Linear Regression: Predicted vs True")

plt.savefig("linear_pred_vs_true.png")
plt.close()

torch.manual_seed(0)
net = BatteryNet(hidden)
opt = torch.optim.Adam(net.parameters(), lr=3e-3)
Xt, yt = torch.tensor((X - mu) / sd), torch.tensor(y)
Xvt = torch.tensor((Xv - mu) / sd)
for ep in range(a.epochs):
    perm = torch.randperm(len(Xt))
    for i in range(0, len(Xt), 128):
        b = perm[i:i + 128]
        loss = torch.nn.functional.mse_loss(net(Xt[b]), yt[b])
        opt.zero_grad(); loss.backward(); opt.step()
    if ep % 300 == 0 or ep == a.epochs - 1:
        with torch.no_grad():
            print(f"  epoch {ep:4d}  val MAE {mae(net(Xvt).numpy(), yv):.2f} days")
with torch.no_grad():
    train_mae = mae(net(Xt).numpy(), y)
    val_mae = mae(net(Xvt).numpy(), yv)

print(f"training MAE:   {train_mae:.2f} days")
print(f"validation MAE: {val_mae:.2f} days")
print(f"network {hidden}:            {val_mae:.2f} days")

os.makedirs("model", exist_ok=True)
torch.save(net.state_dict(), "model/model.pt")
json.dump(dict(team=a.team, hidden=list(hidden), mu=mu.tolist(), sd=sd.tolist(),
               features=FEATURES, val_mae=round(val_mae, 2)), open("model/config.json", "w"), indent=2)
print("saved model/model.pt and model/config.json")
