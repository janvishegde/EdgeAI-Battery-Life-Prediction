"""m2_storage.py -- Mission 2 board experiments (team 6). Needs the board.

  python m2_storage.py info    --port COM6
  python m2_storage.py sram    --port COM6      # longest recording that fits in internal RAM
  python m2_storage.py psram   --port COM6      # does PSRAM work? what fits? (f32 / i16 / i8 at 16 kHz and 8 kHz)
  python m2_storage.py send    --port COM6      # all 144 clips -> PSRAM -> SAVE to flash -> CRC checks
  (now UNPLUG the board, plug it back in)
  python m2_storage.py check   --port COM6      # CRC and dump from flash vs what was sent; did PSRAM survive?

CHOSEN SETTINGS (edit if the Mission 1 numbers make you change your mind):
"""
import argparse, sys, time, zlib
import numpy as np
from team_audio import clip_list, get_clip
from quant import pack
from m1_pipe import connect

TEAM, FS, FMT, S = 6, 16000, "i16", 1.0
BYTES = {"f32": 4, "i16": 2, "i8": 1}


def all_clips_payload(fs=FS, fmt=FMT, scale=S):
    x = np.concatenate([get_clip(TEAM, i, fs, antialias=True) for i, _ in clip_list(TEAM)])
    return pack(x, fmt, scale)


def try_alloc(b, where, nbytes, fs=FS, fmt=FMT):
    """Ask the board for `nbytes` of storage; the READY line (or the ERR line) tells us the answer."""
    tiny = pack(np.zeros(320, np.float32), fmt, S) if fmt != "f32" else np.zeros(320, "<f4").tobytes()
    try:
        r = b.stream(tiny, fs=fs, fmt=fmt, feat=False, store=where, max_bytes=nbytes, speed=0)
        return True, r["ready"].get("cap")
    except RuntimeError as e:
        return False, str(e)


def hexcrc(d):
    """board_link already turns crc=... into an int; show it as 8 hex digits like Python's zlib.crc32 prints."""
    return {k: (f"{v:08x}" if k == "crc" else v) for k, v in d.items()}


def cmd_info(b):
    for k, v in b.info().items():
        print(f"{k:14s} {v:>12,}" if isinstance(v, int) else f"{k:14s} {v}")


def cmd_sram(b):
    inf = b.info(); print("INFO:", inf)
    largest = inf["heap_largest"]
    print(f"largest free internal block: {largest:,} bytes")
    lo, hi = 0, largest + 4096
    while hi - lo > 64:                                   # binary search on what the board will really give
        mid = (lo + hi) // 2
        ok, _ = try_alloc(b, "sram", mid)
        lo, hi = (mid, hi) if ok else (lo, mid)
    print(f"largest SRAM store the board accepts: {lo:,} bytes")
    for fs, fmt in ((16000, "f32"), (16000, "i16"), (16000, "i8"), (8000, "i16"), (8000, "i8")):
        print(f"  {fs//1000:2d} kHz {fmt}: {lo / (fs * BYTES[fmt]):6.2f} s of audio")
    # prove it: really stream that much and check nothing was dropped
    n = lo // 2 // 2 * 2
    x = np.concatenate([get_clip(TEAM, i, FS, True) for i, _ in clip_list(TEAM)])[: n // 2]
    pl = pack(x, FMT, S)
    r = b.stream(pl, fs=FS, fmt=FMT, feat=False, store="sram", max_bytes=len(pl), speed=0)
    print("stored:", r["board"]["stored"], "of", len(pl), "store_full:", r["board"]["store_full"])
    print("CRC board:", hexcrc(b.crc("sram")), " laptop: %08x" % zlib.crc32(pl))


def cmd_psram(b):
    inf = b.info(); print("INFO:", inf)
    if not inf.get("psram_size"):
        print("psram_size = 0  ->  Tools > PSRAM is not set to 'OPI PSRAM' (N16R8 = 16 MB flash, 8 MB OCTAL PSRAM)")
    for fs, fmt in ((16000, "f32"), (16000, "i16"), (16000, "i8"), (8000, "i16")):
        need = 144 * fs * BYTES[fmt]
        ok, info = try_alloc(b, "psram", need, fs, fmt)
        print(f"  all 144 clips, {fs//1000} kHz {fmt}: need {need:>10,} B -> {'OK cap=' + str(info) if ok else info}")


def cmd_send(b):
    pl = all_clips_payload()
    print(f"payload {len(pl):,} bytes, crc32 {zlib.crc32(pl):08x}")
    r = b.stream(pl, fs=FS, fmt=FMT, scale=S, feat=False, store="psram", max_bytes=len(pl), speed=0)
    print("board summary:", r["board"])
    print("psram CRC:", hexcrc(b.crc("psram")))
    print("save:", hexcrc(b.save()))
    print("flash CRC:", hexcrc(b.crc("flash")))
    print("info:", b.info())
    print("-> now unplug the board, plug it back in, and run:  python m2_storage.py check")


def cmd_check(b):
    pl = all_clips_payload(); mine = zlib.crc32(pl)
    print(f"sent crc32 {mine:08x}, {len(pl):,} bytes")
    print("psram:", hexcrc(b.crc("psram")), " (after a power cut this should be n=0: RAM forgets)")
    c = b.crc("flash"); print("flash:", hexcrc(c))
    back = b.dump("flash")
    print(f"dump: {len(back):,} bytes, crc32 {zlib.crc32(back):08x}, identical to what was sent: {back == pl}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("what", choices=["info", "sram", "psram", "send", "check"])
    ap.add_argument("--port", required=True); ap.add_argument("--baud", type=int, default=921600)
    a = ap.parse_args()
    b = connect(a.port, a.baud)
    {"info": cmd_info, "sram": cmd_sram, "psram": cmd_psram, "send": cmd_send, "check": cmd_check}[a.what](b)
    b.close()
