import numpy as np
from board_link import Board
from team_audio import clip_list, get_clip

PORT = "COM11"
TEAM = 6

clips = clip_list(TEAM)[:10]
x = np.concatenate([
    get_clip(TEAM, cid, fs=16000, antialias=True)
    for cid, _ in clips
])

q = np.round(x * 32767).astype("<i2")
payload = q.tobytes()

for enabled in [False, True]:
    for speed in [5.0]:
        b = Board(PORT)
        r = b.stream(
            payload, fs=16000, fmt="i16",
            win=480, hop=320, nfft=512, mels=40,
            feat=enabled, store="none", speed=speed
        )
        b.close()

        print("\nFeatures:", "ON" if enabled else "OFF")
        print("Speed:", speed)
        print("Frames received:", len(r["features"]))
        print("Lost features:", r["lost_features"])
        print("Board summary:", r["board"])