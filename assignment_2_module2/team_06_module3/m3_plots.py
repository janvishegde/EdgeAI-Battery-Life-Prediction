import numpy as np
import matplotlib.pyplot as plt
from team_audio import CLASSES, clip_list, get_clip
from m3_features import features

TEAM = 6
clips = clip_list(TEAM)

fig, axes = plt.subplots(2, 3, figsize=(13, 6), sharex=True, sharey=True)
for ax, cls in zip(axes.ravel(), CLASSES):
    cid = [c for c, lab in clips if lab == cls][0]      # first clip of this class
    x = get_clip(TEAM, cid, fs=16000, antialias=True)
    F = features(x)                                      # (49, 40)
    im = ax.imshow(F.T, origin="lower", aspect="auto", vmin=-60, vmax=40,
                   extent=[0, 1, 0, 40])
    ax.set_title(f"{cls} (clip {cid})")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("mel band")
fig.colorbar(im, ax=axes, label="log-mel (dB)")
fig.savefig("figs/m3_logmel.png", dpi=150)
print("saved figs/m3_logmel.png")
plt.show()