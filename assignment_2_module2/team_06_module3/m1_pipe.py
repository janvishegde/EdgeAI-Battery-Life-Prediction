"""m1_pipe.py -- Mission 1 measurements (team 6). Run on YOUR laptop with the board plugged in.

  python m1_pipe.py predict                                  # the numbers to write down BEFORE measuring
  python m1_pipe.py com  --port COM5                         # COM port: 115200, 921600, 2000000 baud, speed=0
  python m1_pipe.py usb  --port COM6                         # native USB port, speed=0
  python m1_pipe.py realtime --port COM5 --label com --baud 921600   # can it carry each format at speed=1?
  python m1_pipe.py packets  --port COM6 --label usb          # samples_per_packet = 8, 64, 320, 1024
  python m1_pipe.py sweep --port COM10 --label usb            # fastest speed with ZERO loss (speed=1,2,4,...)
  python m1_pipe.py plot                                     # speed vs baud plot from m1_results.csv

Every run appends rows to m1_results.csv.  Stream rule from the README: feat=False, store="none".
Wire bytes = payload + 13 per packet (2 magic + 1 type + 4 seq + 2 len + 4 crc).
"""
import argparse, csv, math, os, sys, time
import numpy as np
from team_audio import clip_list, get_clip
from quant import pack

TEAM = 6
CSV = "m1_results.csv"
OVERHEAD = 13
BPS = {"f32": 4, "i16": 2, "i8": 1}


def audio(fs, seconds):
    """`seconds` of real team-6 audio (clips joined), at fs, filter on."""
    ids = [i for i, _ in clip_list(TEAM)][:: max(1, 144 // seconds)][:seconds]
    return np.concatenate([get_clip(TEAM, i, fs, antialias=True) for i in ids])


def payload_for(fmt, fs, seconds):
    return pack(audio(fs, seconds), fmt, 1.0)


def predict():
    print("Bytes per second of audio payload (no framing):")
    for fs in (16000, 8000):
        for f in ("f32", "i16", "i8"):
            print(f"  {fs//1000:2d} kHz {f}: {fs*BPS[f]:>6,} B/s")
    print(f"\n115200 baud UART: 10 bits per byte (start+8+stop) -> {115200//10:,} B/s at best, each direction")
    for b in (921600, 2000000):
        print(f"{b:>8} baud UART: {b//10:,} B/s at best")
    print("\nFraming cost, 16 kHz i16 (13 bytes per packet):")
    for spp in (8, 64, 320, 1024):
        pay = spp * 2
        wire = 32000 * (pay + OVERHEAD) / pay
        print(f"  samples_per_packet={spp:5d}: {pay+OVERHEAD:5d} B per packet, overhead {OVERHEAD/(pay+OVERHEAD)*100:5.1f}%, "
              f"wire rate {wire:>8,.0f} B/s, {32000/pay:6.1f} packets/s")
    print("\nFeatures coming back (win 480, hop 320, 40 mel, 16 kHz):")
    fps = 16000 / 320
    fb = 9 + 8 + 4 * 40 + 4
    print(f"  {fps:.0f} frames/s x {fb} B = {fps*fb:,.0f} B/s  (payload only {fps*(8+160):,.0f} B/s)")
    fps8 = 8000 / 160
    print(f"  at 8 kHz with hop 160 (same 20 ms): {fps8:.0f} frames/s x {fb} B = {fps8*fb:,.0f} B/s")


def connect(port, baud=921600):
    """Open the port and wait for the board. The board may still be at an older baud rate from the
    last test (it keeps the rate you set), so try a few rates and move it to `baud` when it answers."""
    from board_link import Board
    tried = []
    for rate in [baud, 921600, 115200, 2000000]:
        if rate in tried:
            continue
        tried.append(rate)
        b = Board(port, rate)
        old = b.ser.timeout
        b.ser.timeout = 1.5                      # do not wait 5 s for every wrong guess
        for _ in range(3):
            try:
                b.ser.reset_input_buffer()
                if b.ping():
                    b.ser.timeout = old
                    if rate != baud:
                        b.set_baud(baud)         # bring the board to the speed we want
                    return b
            except Exception:
                pass
            time.sleep(0.5)
        b.close()
    raise RuntimeError(f"board on {port} does not answer PING (tried {tried}); press RST on the board and try again")


def log(row):
    new = not os.path.exists(CSV)
    with open(CSV, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(row))
        if new:
            w.writeheader()
        w.writerow(row)


def run_one(b, label, baud, fmt, fs, seconds, speed, spp, repeat):
    pl = payload_for(fmt, fs, seconds)
    t = time.perf_counter()
    r = b.stream(pl, fs=fs, fmt=fmt, feat=False, store="none", speed=speed, samples_per_packet=spp)
    wall = time.perf_counter() - t
    pk = r["packets_sent"] + 1                      # +1 for the END frame
    wire = len(pl) + OVERHEAD * pk
    bd = r["board"] or {}
    row = dict(port=label, baud=baud, fmt=fmt, fs=fs, speed=speed, spp=spp, run=repeat, audio_s=r["audio_seconds"],
               payload_B=len(pl), wire_B=wire, wall_s=round(wall, 3), send_s=round(r["send_seconds"], 3),
               wall_Bps=round(wire / wall), board_ms=bd.get("ms"), board_Bps=round(wire / (bd["ms"] / 1000)) if bd.get("ms") else "",
               seq_gaps=bd.get("seq_gaps"), bad_crc=bd.get("bad_crc"), uart_errors=bd.get("uart_errors"),
               samples=bd.get("samples"), why=bd.get("why"))
    log(row)
    lossy = bool(row["seq_gaps"] or row["bad_crc"] or row["why"] != "end")
    if lossy:
        time.sleep(4)                    # the board gives up on a broken stream after 3 s of silence
        try:
            b.ser.reset_input_buffer()
        except Exception:
            pass
    print(f"{label:4s} baud={baud:>8} {fmt} {fs//1000}k spp={spp:<5} speed={speed:<4} run{repeat}: "
          f"{row['wall_Bps']:>9,} B/s (laptop) | board ms={row['board_ms']} gaps={row['seq_gaps']} crc={row['bad_crc']} uart_err={row['uart_errors']}")
    return row


def cmd_speed(a, label, bauds):
    if a.bauds:
        bauds = [int(x) for x in a.bauds.split(",")]
    for baud in bauds:
        b = connect(a.port, 921600)
        if label == "com" and baud != 921600:
            b.set_baud(baud)
        for rep in range(a.repeats):            # run 0 is the warm-up: keep it, but do not trust it
            run_one(b, label, baud, "i16", 16000, a.seconds, 0, 320, rep)
        if label == "com" and baud != 921600:
            b.set_baud(921600)                   # leave the board at its default speed
        b.close()
        time.sleep(0.5)


def cmd_realtime(a):
    b = connect(a.port, 921600)
    if a.label == "com" and a.baud != 921600:
        b.set_baud(a.baud)
    for fs, fmt in [(16000, "f32"), (16000, "i16"), (16000, "i8"), (8000, "i16"), (8000, "i8")]:
        row = run_one(b, a.label, a.baud, fmt, fs, 5, 1.0, 320, 1)
        need = fs * BPS[fmt] * (320 * BPS[fmt] + OVERHEAD) / (320 * BPS[fmt])
        ok = row["send_s"] <= 5 * 1.05 and not row["seq_gaps"] and not row["bad_crc"]
        print(f"   needs {need:,.0f} B/s on the wire; sent 5 s of audio in {row['send_s']} s -> {'CARRIES it' if ok else 'CANNOT keep up'}")
    b.close()


def cmd_sweep(a):
    """Find the fastest speed with NOTHING lost. speed 1 = real time; each step multiplies it."""
    b = connect(a.port, 921600)
    if a.label == "com" and a.baud != 921600:
        b.set_baud(a.baud)
    expected = a.seconds * 16000
    for sp in [float(x) for x in a.speeds.split(",")]:
        oks = []
        for rep in range(a.repeats):
            r = run_one(b, a.label, a.baud, "i16", 16000, a.seconds, sp, 320, rep)
            oks.append(not (r["seq_gaps"] or r["bad_crc"]) and r["samples"] == expected and r["why"] == "end")
        need = 32000 * 653 / 640 * sp
        print(f"   >>> speed={sp}: needs {need:,.0f} B/s on the wire -> {'ZERO LOSS in every run' if all(oks) else 'LOSS in at least one run'}")
    b.close()


def cmd_packets(a):
    b = connect(a.port, 921600)
    if a.label == "com" and a.baud != 921600:
        b.set_baud(a.baud)
    for spp in (8, 64, 320, 1024):
        for rep in range(a.repeats):
            run_one(b, a.label, a.baud, "i16", 16000, a.seconds, 0, spp, rep)
    b.close()


def cmd_plot():
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rows = [r for r in csv.DictReader(open(CSV)) if r["fmt"] == "i16" and r["fs"] == "16000" and r["speed"] == "0" and r["spp"] == "320"]
    plt.figure(figsize=(7, 4.5))
    xs = [115200, 921600, 2000000]
    plt.plot(xs, [x / 10 for x in xs], "k--", label="UART limit (baud/10)")
    for lab, mk in (("com", "o-"), ("usb", "s")):
        pts = {}
        for r in rows:
            if r["port"] == lab and int(r["run"]) > 0:          # skip the warm-up run
                pts.setdefault(int(r["baud"]), []).append(float(r["wall_Bps"]))
        if pts:
            k = sorted(pts)
            plt.plot(k, [np.mean(pts[x]) for x in k], mk, label=f"{lab.upper()} port (measured)")
    plt.xscale("log"); plt.yscale("log"); plt.xlabel("baud setting"); plt.ylabel("bytes per second"); plt.grid(alpha=.3, which="both"); plt.legend()
    plt.title("Mission 1: speed vs baud"); plt.tight_layout(); plt.savefig("figs/m1_speed_vs_baud.png", dpi=130)
    print("wrote figs/m1_speed_vs_baud.png")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["predict", "com", "usb", "realtime", "packets", "sweep", "plot"])
    ap.add_argument("--port"); ap.add_argument("--label", default="com"); ap.add_argument("--baud", type=int, default=921600)
    ap.add_argument("--bauds", default=""); ap.add_argument("--speeds", default="1,2,4,6,8,12,16"); ap.add_argument("--seconds", type=int, default=10); ap.add_argument("--repeats", type=int, default=4)
    a = ap.parse_args()
    if a.what == "predict": predict()
    elif a.what == "plot": cmd_plot()
    else:
        if not a.port: sys.exit("--port is needed (python board_link.py ports)")
        if a.what == "com": cmd_speed(a, "com", [115200, 921600, 2000000])
        elif a.what == "usb": cmd_speed(a, "usb", [921600])
        elif a.what == "realtime": cmd_realtime(a)
        elif a.what == "packets": cmd_packets(a)
        elif a.what == "sweep": cmd_sweep(a)
