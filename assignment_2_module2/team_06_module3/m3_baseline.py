import sys
import numpy as np
from board_link import Board
from team_audio import clip_list, get_clip
from m3_features import features

PORT = sys.argv[1] if len(sys.argv) > 1 else "COM9"
SECONDS = 10
TEAM = 6

clips = clip_list(TEAM)[:SECONDS]
x = np.concatenate([get_clip(TEAM, cid, fs=16000, antialias=True) for cid, _ in clips])
q = np.round(x * 32767).astype("<i2")
payload = q.tobytes()
xhat = q.astype(np.float32) / 32767

b = Board(PORT)
r = b.stream(payload, fs=16000, fmt="i16", win=400, hop=160, nfft=512, mels=40,mfcc=              13,feat=True, store="none", speed=1.0)
b.close()

us = r["compute_us"]
lag = r["lag_s"]
print(f"audio seconds        : {r['audio_seconds']:.1f}")
print(f"frames expected/got  : {r['expected_features']} / {len(r['features'])}  (lost {r['lost_features']})")
print(f"compute_us per frame : median {np.median(us):,.0f}   max {us.max():,}")
print(f"frame budget (hop)   : {160 / 16000 * 1e6:,.0f} us")
if len(lag):
    print(f"lag_s                : first {lag[0]:.3f}   last {lag[-1]:.3f}   max {lag.max():.3f}")
print("board summary        :", r["board"])

ref = features(xhat, win=400, hop=160,mfcc=13)
n = min(len(ref), len(r["features"]))
d = np.abs(ref[:n] - r["features"][:n])
print(f"vs NumPy (same samples): mean diff {d.mean():.4f} dB   worst {d.max():.4f} dB   (target < 0.05)")

