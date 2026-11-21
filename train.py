"""
train.py -- STARTER. Clean the data, fit baselines, train the network, save it for the server.

    python train.py --team 7 --hidden 32,32
Writes model/model.pt and model/config.json, which app/main.py loads.

Look for TODO. The training loop is given; the decisions are yours.
"""
import argparse
import json
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch

from app.model import FEATURES, BatteryNet

ap = argparse.ArgumentParser()
ap.add_argument("--team", type=int, required=True)
ap.add_argument("--hidden", default="32,32")
ap.add_argument("--epochs", type=int, default=1500)
a = ap.parse_args()
hidden = tuple(int(h) for h in a.hidden.split(","))

df = pd.read_csv(f"team_{a.team:02d}_train.csv")
# TODO Mission 1: find the sensor glitches (plot every column first!) and write a rule that
# marks them. Say in your report how many you found and why each rule is safe.
bad_battery = df["battery_v"] == 0
bad_temp = df["temp_c"] == -127
bad_wifi = df["wifi_rssi_dbm"] == 0

bad = bad_battery | bad_temp | bad_wifi
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
X_with_bias = np.column_stack([X, np.ones(len(X))])
weights = np.linalg.lstsq(X_with_bias, y, rcond=None)[0]
Xv_with_bias = np.column_stack([Xv, np.ones(len(Xv))])
predictions = Xv_with_bias @ weights
print(f"baseline (linear regression): {mae(predictions, yv):.2f} days")
errors = np.abs(predictions - yv)

worst_indices = np.argsort(errors)[-10:][::-1]

print("\n10 worst predictions:")
for i in worst_indices:
    print(
        f"Actual: {yv[i]:.2f}, "
        f"Predicted: {predictions[i]:.2f}, "
        f"Error: {errors[i]:.2f}"
    )

plt.figure(figsize=(7, 6))

plt.scatter(yv, predictions, alpha=0.5)
minimum = min(yv.min(), predictions.min())
maximum = max(yv.max(), predictions.max())
plt.plot([minimum, maximum], [minimum, maximum], "r--")

plt.xlabel("Actual days_left")
plt.ylabel("Predicted days_left")
plt.title("Linear Regression: Predicted vs Actual")

plt.tight_layout()
plt.savefig("linear_regression_plot.png")
plt.show()

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
            train_mae = mae(net(Xt).numpy(), yt.numpy())
            val_mae = mae(net(Xvt).numpy(), yv)

        print(f"  epoch {ep:4d}  train MAE {train_mae:.2f} days  val MAE {val_mae:.2f} days")

os.makedirs("model", exist_ok=True)
torch.save(net.state_dict(), "model/model.pt")
json.dump(dict(team=a.team, hidden=list(hidden), mu=mu.tolist(), sd=sd.tolist(),
               features=FEATURES, val_mae=round(val_mae, 2)), open("model/config.json", "w"), indent=2)
print("saved model/model.pt and model/config.json")