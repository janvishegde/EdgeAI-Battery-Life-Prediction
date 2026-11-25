
#pragma once
#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

struct FeatCfg {
  int fs = 16000, win = 480, hop = 320, nfft = 512, mels = 40, mfcc = 0;
};

class FeaturePipeline {
 public:
  FeatCfg c;
  bool ok = false;

  bool begin(const FeatCfg &cfg) {
    end();
    c = cfg;
    if (c.nfft < 16 || c.nfft > 2048 || (c.nfft & (c.nfft - 1)) || c.win > c.nfft || c.win < 2 ||
        c.hop < 1 || c.mels < 1 || c.mels > 128 || c.mfcc < 0 || c.mfcc > c.mels) return false;
    nb = c.nfft / 2 + 1;
    tw_re = alloc(c.nfft / 2);
    tw_im = alloc(c.nfft / 2);
    window = alloc(c.win); re = alloc(c.nfft); im = alloc(c.nfft); pw = alloc(nb);
    melw = alloc((size_t)c.mels * nb); melv = alloc(c.mels);

    if (c.mfcc) dct = alloc((size_t)c.mfcc * c.mels);
    if (!tw_re || !tw_im || !window || !re || !im || !pw || !melw || !melv || (c.mfcc && !dct)) {
      end();
      return false;
    }

    for (int n = 0; n < c.win; n++) window[n] = 0.5f - 0.5f * cosf(2.0f * (float)M_PI * n / (c.win - 1));
    for (int k = 0; k < c.nfft / 2; k++) {
      float angle = 2.0f * (float)M_PI * k / c.nfft;
      tw_re[k] = cosf(angle);
      tw_im[k] = -sinf(angle);
    }

    // HTK mel filterbank
    auto hz2mel = [](double f) { return 2595.0 * log10(1.0 + f / 700.0); };
    auto mel2hz = [](double m) { return 700.0 * (pow(10.0, m / 2595.0) - 1.0); };
    double m0 = hz2mel(20.0), m1 = hz2mel(c.fs / 2.0);
    double *edge = (double *)malloc(sizeof(double) * (c.mels + 2));
    if (!edge) { end(); return false; }

    for (int i = 0; i < c.mels + 2; i++) edge[i] = mel2hz(m0 + (m1 - m0) * i / (c.mels + 1));
    for (int m = 0; m < c.mels; m++)
      for (int k = 0; k < nb; k++) {
        double f = (double)k * c.fs / c.nfft, lo = edge[m], ce = edge[m + 1], hi = edge[m + 2], w = 0;
        if (f > lo && f <= ce) w = (f - lo) / (ce - lo);
        else if (f > ce && f < hi) w = (hi - f) / (hi - ce);
        melw[(size_t)m * nb + k] = (float)w;
      }
    free(edge);

    for (int q = 0; q < c.mfcc; q++)
      for (int m = 0; m < c.mels; m++)
        dct[(size_t)q * c.mels + m] = (float)((q == 0 ? sqrt(1.0 / c.mels) : sqrt(2.0 / c.mels)) *
                                              cos(M_PI * q * (2 * m + 1) / (2.0 * c.mels)));
    ok = true;
    return true;
  }

  int outSize() const { return c.mfcc ? c.mfcc : c.mels; }

  // frame: c.win float samples (already dequantised). out: outSize() floats.
  void compute(const float *frame, float *out) {
    for (int n = 0; n < c.win; n++) { re[n] = frame[n] * window[n]; im[n] = 0; }
    for (int n = c.win; n < c.nfft; n++) { re[n] = 0; im[n] = 0; }
    fft();
    for (int k = 0; k < nb; k++) pw[k] = (re[k] * re[k] + im[k] * im[k]) / c.nfft;
    for (int m = 0; m < c.mels; m++) {
      const float *w = melw + (size_t)m * nb; float s = 0;
      for (int k = 0; k < nb; k++) s += w[k] * pw[k];
      melv[m] = 10.0f * log10f(s > 1e-10f ? s : 1e-10f);
    }
    if (!c.mfcc) { memcpy(out, melv, sizeof(float) * c.mels); return; }
    for (int q = 0; q < c.mfcc; q++) {
      const float *d = dct + (size_t)q * c.mels; float s = 0;
      for (int m = 0; m < c.mels; m++) s += d[m] * melv[m];
      out[q] = s;
    }
  }

  void end() {
    float **ps[] = {&tw_re, &tw_im, &window, &re, &im, &pw, &melw, &melv, &dct};
    for (auto p : ps) { free(*p); *p = nullptr; }
    ok = false;
  }

  ~FeaturePipeline() { end(); }

 private:
  int nb = 0;
  float *tw_re = nullptr;
  float *tw_im = nullptr;
  float *window = nullptr, *re = nullptr, *im = nullptr, *pw = nullptr, *melw = nullptr,
        *melv = nullptr, *dct = nullptr;

  static float *alloc(size_t n) { return (float *)malloc(sizeof(float) * n); }

  // Fast radix-2 FFT
  void fft() {
    int j = 0;

    // Bit reversal
    for (int i = 1; i < c.nfft; i++) {
      int bit = c.nfft >> 1;

      while (j & bit) {
        j ^= bit;
        bit >>= 1;
      }

      j ^= bit;

      if (i < j) {
        float temp = re[i];
        re[i] = re[j];
        re[j] = temp;

        temp = im[i];
        im[i] = im[j];
        im[j] = temp;
      }
    }

    // Butterfly calculations
    for (int len = 2; len <= c.nfft; len <<= 1) {
      int half = len / 2;
      int step = c.nfft / len;

      for (int i = 0; i < c.nfft; i += len) {
        for (int k = 0; k < half; k++) {
          int tw = k * step;

          float wr = tw_re[tw];
          float wi = tw_im[tw];

          int even = i + k;
          int odd = even + half;

          float vr = re[odd];
          float vi = im[odd];

          float tr = wr * vr - wi * vi;
          float ti = wr * vi + wi * vr;

          float ur = re[even];
          float ui = im[even];

          re[even] = ur + tr;
          im[even] = ui + ti;

          re[odd] = ur - tr;
          im[odd] = ui - ti;
        }
      }
    }
  }

  // The discrete Fourier transform, straight from the formula:
  //   X[k] = sum over n of x[n] * (cos(2*pi*k*n/N) - j*sin(2*pi*k*n/N))
  // Only the first nfft/2+1 outputs are needed (the rest mirror them).
  void dft() {
    static float xr[2048];
    memcpy(xr, re, sizeof(float) * c.nfft);
    for (int k = 0; k < nb; k++) {
      float sr = 0, si = 0;
      for (int n = 0; n < c.win; n++) {          // samples past win are zero padding
        float a = 2.0f * (float)M_PI * k * n / c.nfft;
        sr += xr[n] * cosf(a);
        si -= xr[n] * sinf(a);
      }
      re[k] = sr; im[k] = si;
    }
  }
};
