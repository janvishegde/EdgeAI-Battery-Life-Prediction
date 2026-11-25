"""m2_analysis.py -- Mission 2 without the board: aliasing spectra, SQNR, storage sizes (team 6)."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from team_audio import clip_list, get_clip, _team
from quant import quantise, dequantise, sqnr_db

TEAM = 6
clips = clip_list(TEAM)
sil = [i for i, l in clips if l == "_silence"][0]
word = [i for i, l in clips if l == "on"][0]
room = _team(TEAM)
print("team 6 room:", room)

def spec_db(x, fs):
    w = np.hanning(len(x))
    X = np.fft.rfft(x * w)
    P = np.abs(X) ** 2 / np.sum(w ** 2)
    return np.fft.rfftfreq(len(x), 1 / fs), 10 * np.log10(P + 1e-20)

# ---- aliasing: silence clip at 48k, 8k no filter, 8k with filter
fig, ax = plt.subplots(3, 1, figsize=(8, 8))
for a, (fs, aa, title) in zip(ax, [(48000, False, "48 kHz"), (8000, False, "8 kHz, NO filter"),
                                   (8000, True, "8 kHz, anti-alias filter ON")]):
    x = get_clip(TEAM, sil, fs, aa)
    f, d = spec_db(x, fs)
    a.plot(f, d, lw=0.8); a.set_title(f"silence clip, {title}"); a.set_ylabel("dB"); a.grid(alpha=.3)
    a.set_ylim(-110, 0)
    pk = np.argmax(np.where(f > 200, d, -1e9))   # biggest peak above the 50 Hz hum
    print(f"{title:32s} biggest peak above 200 Hz: {f[pk]:.1f} Hz at {d[pk]:.1f} dB")
    a.annotate(f"{f[pk]:.0f} Hz", (f[pk], d[pk]), xytext=(f[pk] + 150, d[pk] - 3), arrowprops=dict(arrowstyle="->"))
ax[-1].set_xlabel("frequency (Hz)")
plt.tight_layout(); plt.savefig("figs/m2_aliasing.png", dpi=130); plt.close()

whine = room["whine"]
fs = 8000
alias = abs(whine - round(whine / fs) * fs)
print(f"whine {whine:.2f} Hz  ->  alias at 8 kHz = |{whine:.2f} - {round(whine/fs)}*{fs}| = {alias:.2f} Hz")

# ---- SQNR
print("\nSQNR (16 kHz, filter on)")
rows = []
for name, idx in [("word 'on'", word), ("silence", sil)]:
    x = get_clip(TEAM, idx, 16000, True).astype(np.float64)
    print(f"  {name}: peak |x| = {np.max(np.abs(x)):.3f}, rms = {np.sqrt(np.mean(x**2)):.4f}")
    for fmt, S in [("i16", 1.0), ("i8", 1.0), ("i8", 0.5), ("i8", 0.25), ("i8", 0.1)]:
        xh = dequantise(quantise(x, fmt, S), fmt, S)
        clipped = np.mean(np.abs(x) > S) * 100
        s = sqnr_db(x, xh)
        rows.append((name, fmt, S, s, clipped))
        print(f"    {fmt} S={S:<5} SQNR = {s:6.1f} dB   clipped samples = {clipped:.2f}%")

# SQNR over ALL 144 clips for the shortlist, to choose S
print("\nSQNR over all 144 clips (16 kHz, filter on), mean of per-clip dB, and worst clip")
allx = [get_clip(TEAM, i, 16000, True).astype(np.float64) for i, _ in clips]
peak = max(np.max(np.abs(x)) for x in allx)
print(f"largest |sample| in any clip: {peak:.3f}")
for fmt, S in [("i16", 1.0), ("i16", 0.5), ("i8", 1.0), ("i8", 0.5), ("i8", 0.35), ("i8", 0.25), ("i8", 0.1)]:
    s = [sqnr_db(x, dequantise(quantise(x, fmt, S), fmt, S)) for x in allx]
    cl = np.mean([np.mean(np.abs(x) > S) for x in allx]) * 100
    print(f"  {fmt} S={S:<5} mean {np.mean(s):6.1f} dB  worst {np.min(s):6.1f} dB  clipped {cl:.3f}%")

# ---- storage sizes for all 144 clips
print("\nBytes to store 144 clips (144 s of audio)")
for fs in (16000, 8000):
    for fmt, b in (("f32", 4), ("i16", 2), ("i8", 1)):
        n = 144 * fs * b
        print(f"  {fs//1000:2d} kHz {fmt}: {n:>10,} bytes = {n/1e6:.3f} MB")
