import numpy as np
from team_audio import clip_list, get_clip

def mel_filterbank(fs, nfft, mels):
    hz2mel = lambda f: 2595 * np.log10(1 + f / 700)
    mel2hz = lambda m: 700 * (10 ** (m / 2595) - 1)
    edges = mel2hz(np.linspace(hz2mel(20), hz2mel(fs / 2), mels + 2))
    f = np.arange(nfft // 2 + 1) * fs / nfft
    W = np.zeros((mels, len(f)))
    for m in range(mels):
        lo, ce, hi = edges[m], edges[m + 1], edges[m + 2]
        up = (f - lo) / (ce - lo)
        down = (hi - f) / (hi - ce)
        W[m] = np.maximum(0, np.minimum(up, down))   # triangle
    return W

def features(x, fs=16000, win=480, hop=320, nfft=512, mels=40, mfcc=0):
    W = mel_filterbank(fs, nfft, mels)
    n_frames = (len(x) - win) // hop + 1
    out = np.zeros((n_frames, mels))

    for k in range(n_frames):
        frame = x[k*hop : k*hop + win] * np.hanning(win)
        spec = np.abs(np.fft.rfft(frame, nfft)) ** 2 / nfft
        logmel = 10 * np.log10(np.maximum(W @ spec, 1e-10))

        if mfcc:
            n = np.arange(mels)
            c = np.arange(mfcc)[:, None]
            dct = np.cos(np.pi / mels * (n + 0.5) * c)
            dct[0] *= 1 / np.sqrt(mels)
            dct[1:] *= np.sqrt(2 / mels)
            out[k, :mfcc] = dct @ logmel
        else:
            out[k] = logmel

    if mfcc:
        return out[:, :mfcc]

    return out
if __name__ == "__main__":
    cid, label = clip_list(6)[0]
    x = get_clip(6, cid, fs=16000, antialias=True)
    print(label, features(x).shape)