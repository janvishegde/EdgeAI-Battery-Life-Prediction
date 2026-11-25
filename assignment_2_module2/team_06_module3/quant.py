"""quant.py -- Mission 2: quantise, pack and unpack audio for the board (team 6, Pixel).

The README gives the rule:
    q    = clip(round(x / S * (2**(b-1) - 1)), -2**(b-1), 2**(b-1) - 1)
    xhat = q * S / (2**(b-1) - 1)
S is the "full scale": a sample equal to S becomes the biggest code (32767 for int16,
127 for int8). Anything bigger than S is clipped.
"""
import numpy as np

BITS = {"i16": 16, "i8": 8}
DTYPE = {"i16": "<i2", "i8": np.int8, "f32": "<f4"}


def quantise(x, fmt, S=1.0):
    """float samples -> integer codes (int16 or int8). f32 is not quantised."""
    b = BITS[fmt]
    qmax = 2 ** (b - 1) - 1
    q = np.clip(np.round(x / S * qmax), -(2 ** (b - 1)), 2 ** (b - 1) - 1)
    return q.astype(DTYPE[fmt])


def dequantise(q, fmt, S=1.0):
    """integer codes -> float samples (what the board rebuilds from the bytes)."""
    qmax = 2 ** (BITS[fmt] - 1) - 1
    return q.astype(np.float64) * S / qmax


def pack(x, fmt, S=1.0):
    """float samples -> the bytes that go on the wire."""
    if fmt == "f32":
        return np.asarray(x).astype("<f4").tobytes()
    return quantise(x, fmt, S).tobytes()


def unpack(b, fmt, S=1.0):
    """bytes from the wire -> float samples again."""
    if fmt == "f32":
        return np.frombuffer(b, dtype="<f4").astype(np.float64)
    q = np.frombuffer(b, dtype=DTYPE[fmt])
    return dequantise(q, fmt, S)


def sqnr_db(x, xhat):
    """10*log10(signal power / error power)."""
    x = np.asarray(x, np.float64)
    err = x - np.asarray(xhat, np.float64)
    return 10 * np.log10(np.mean(x ** 2) / max(np.mean(err ** 2), 1e-30))


if __name__ == "__main__":
    # self-test: pack -> unpack must give back exactly what quantise -> dequantise gives
    rng = np.random.default_rng(0)
    x = rng.uniform(-1, 1, 1000)
    for fmt in ("i16", "i8"):
        for S in (1.0, 0.5):
            via_bytes = unpack(pack(x, fmt, S), fmt, S)
            direct = dequantise(quantise(x, fmt, S), fmt, S)
            assert np.array_equal(via_bytes, direct)
            assert len(pack(x, fmt, S)) == len(x) * (2 if fmt == "i16" else 1)
    print("quant.py self-test passed")
