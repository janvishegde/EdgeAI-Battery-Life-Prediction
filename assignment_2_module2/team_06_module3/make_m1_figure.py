"""make_m1_figure.py -- draws figs/m1_speed_vs_baud.png from the numbers measured on team 6's board (24 Nov 2026)."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLUE, ORANGE, INK, GREY = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e"
fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.4), facecolor="#fcfcfb")
for ax in (a, b):
    ax.set_facecolor("#fcfcfb"); ax.grid(alpha=.25, which="both"); [ax.spines[s].set_visible(False) for s in ("top", "right")]

# ---- A: speed against baud, per port (mean of runs 1-3, speed=0, 16 kHz int16, 320 samples/packet)
baud = np.array([115200, 921600, 2000000])
com = np.array([11584, 89397, 184876])
a.plot(baud, baud / 10, "--", color=GREY, lw=1.5)
a.plot(baud, com, "o-", color=BLUE, lw=2, ms=8)
usb = 190394      # fastest USB setting with zero loss (speed 6x); baud means nothing to this port
a.hlines(usb, baud[0], baud[-1], colors=ORANGE, lw=2)
a.plot([baud[0]], [usb], "s", color=ORANGE, ms=8)
a.set_xscale("log"); a.set_yscale("log")
a.set_xlabel("baud setting (UART only)", color=GREY); a.set_ylabel("bytes per second", color=GREY)
a.set_title("A. Speed against baud, per port", loc="left", color=INK, fontsize=11)
a.annotate("UART limit = baud / 10", (baud[1], baud[1] / 10), xytext=(-6, 16), textcoords="offset points", color=GREY, ha="right", fontsize=9)
a.annotate("COM measured", (baud[0], com[0]), xytext=(10, 12), textcoords="offset points", color=INK, fontsize=9)
a.annotate("USB: about 190,000 B/s with zero loss\n(the baud setting is ignored)", (baud[0], usb), xytext=(6, 8), textcoords="offset points", color=INK, fontsize=9)
for x, y in zip(baud, com):
    a.annotate(f"{y:,}", (x, y), xytext=(0, -16), textcoords="offset points", ha="center", color=INK, fontsize=8)
a.set_ylim(8000, 600000)

# ---- B: USB, speed multiplier against packets lost or damaged (of about 1000 sent per run)
sp = ["1x", "2x", "4x", "6x", "8x", "12x", "16x"]
got = [32497, 64698, 128146, 190394, None, None, None]
bad = [0, 0, 0, 0, 402.5, 303, 363.75]
x = np.arange(len(sp))
cols = [BLUE if v == 0 else ORANGE for v in bad]
b.bar(x, [max(v, 1) for v in bad], color=cols, width=.62)
for i, v in enumerate(bad):
    b.annotate("0 lost" if v == 0 else f"{v:.0f} lost", (i, max(v, 1)), xytext=(0, 4), textcoords="offset points", ha="center", color=INK, fontsize=9)
b.set_xticks(x); b.set_xticklabels(sp)
b.set_xlabel("speed multiplier (1x = real time, 32,650 B/s on the wire)", color=GREY)
b.set_ylabel("packets missing or damaged per run", color=GREY)
b.set_title("B. USB port: where it starts losing data", loc="left", color=INK, fontsize=11)
b.set_ylim(0, 480)
b.annotate("lossless", (1.5, 60), color=BLUE, ha="center", fontsize=9)
plt.tight_layout(); plt.savefig("figs/m1_speed_vs_baud.png", dpi=150); print("ok")
