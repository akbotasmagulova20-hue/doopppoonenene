#!/usr/bin/env python3
"""
sleepaudio.py — procedural sleep/ambient audio engine.

Synthesises rain, noise, ocean and ambient pads from scratch (numpy DSP only).
Nothing is sampled, trained or downloaded: every sample is computed here, so the
output carries no third-party rights, cannot be matched by Content ID and is not
subject to any generative-model licence.

Streams 16-bit PCM to stdout (or a WAV file) so multi-hour renders stay in RAM.

Usage:
  python3 sleepaudio.py --preset rain_window --hours 3 --out - | ffmpeg -f s16le ...
  python3 sleepaudio.py --preset brown_noise --minutes 2 --out test.wav
"""
import argparse, math, struct, sys
import numpy as np

SR = 48000
BLOCK = 1 << 18          # 262144 samples ~5.46 s
HOP = BLOCK // 2         # 50 % overlap -> Hann windows sum to 1.0


# ----------------------------------------------------------------- spectra ---
def _freqs(n):
    return np.fft.rfftfreq(n, 1.0 / SR)


def _tilt(f, exponent, f0=20.0):
    """1/f^exponent tilt, flat below f0 to avoid an infinite DC gain."""
    out = np.empty_like(f)
    lo = f < f0
    out[lo] = 1.0
    out[~lo] = (f[~lo] / f0) ** (-exponent)
    return out


def _band(f, lo, hi, lo_order=2.0, hi_order=2.0):
    """Smooth band-pass shaping curve (no ringing, no phase issues)."""
    hp = 1.0 / np.sqrt(1.0 + (lo / np.maximum(f, 1e-6)) ** (2 * lo_order))
    lp = 1.0 / np.sqrt(1.0 + (np.maximum(f, 1e-6) / hi) ** (2 * hi_order))
    return hp * lp


def spectrum_rain_hiss(f):
    return _tilt(f, 0.55) * _band(f, 420.0, 9500.0, 2.0, 1.6)


def spectrum_rain_body(f):
    return _tilt(f, 1.15) * _band(f, 70.0, 1800.0, 2.0, 1.4)


def spectrum_droplet(f):
    return _tilt(f, 0.2) * _band(f, 1600.0, 7200.0, 3.0, 2.0)


def spectrum_brown(f):
    return _tilt(f, 1.0) * _band(f, 22.0, 9000.0, 2.0, 1.2)


def spectrum_pink(f):
    return _tilt(f, 0.5) * _band(f, 22.0, 13000.0, 2.0, 1.2)


def spectrum_white_soft(f):
    return _band(f, 60.0, 11000.0, 2.0, 1.5)


def spectrum_ocean(f):
    return _tilt(f, 0.85) * _band(f, 55.0, 6500.0, 2.0, 1.5)


def spectrum_crackle(f):
    """Sharp, woody transients of burning wood."""
    return _tilt(f, 0.3) * _band(f, 700.0, 5200.0, 3.0, 1.8)


def spectrum_fire_body(f):
    return _tilt(f, 1.3) * _band(f, 45.0, 900.0, 2.0, 1.5)


def spectrum_wind(f):
    return _tilt(f, 0.9) * _band(f, 90.0, 3400.0, 2.0, 1.6)


def spectrum_stream(f):
    """Water over stones: brighter and busier than rain, with less low body."""
    return _tilt(f, 0.45) * _band(f, 300.0, 7800.0, 2.5, 1.5)


def spectrum_lowbed(f):
    return _tilt(f, 1.4) * _band(f, 18.0, 160.0, 2.0, 2.0)


# ----------------------------------------------------------- noise streamer ---
class ShapedNoise:
    """Endless spectrally-shaped stereo noise via windowed overlap-add.

    Each output sample is new pseudo-random material, so the result never loops:
    there is no repeating cell anywhere in an 8-hour render.
    """

    def __init__(self, spectrum_fn, seed, stereo_decorrelate=0.85):
        self.rng = np.random.default_rng(seed)
        self.curve = spectrum_fn(_freqs(BLOCK)).astype(np.float64)
        self.win = np.hanning(BLOCK + 1)[:BLOCK]
        self.tail = np.zeros((HOP, 2))
        self.decorr = stereo_decorrelate
        # normalise so output sits near unity RMS
        probe = self._raw_block()
        self.gain = 1.0 / (np.sqrt(np.mean(probe ** 2)) + 1e-12)

    def _shape(self, n):
        spec = np.fft.rfft(self.rng.standard_normal(n)) * self.curve
        return np.fft.irfft(spec, n)

    def _raw_block(self):
        left = self._shape(BLOCK)
        # partially independent right channel -> wide but mono-compatible image
        right = self.decorr * self._shape(BLOCK) + (1.0 - self.decorr) * left
        return np.stack([left, right], axis=1)

    def read(self, n):
        """Return n samples of shaped stereo noise."""
        out = np.zeros((n, 2))
        pos = 0
        carry = self.tail
        while pos < n:
            blk = self._raw_block() * self.win[:, None]
            first = blk[:HOP] + carry
            carry = blk[HOP:]
            take = min(HOP, n - pos)
            out[pos:pos + take] = first[:take]
            if take < HOP:                     # stash the unused remainder
                carry = np.concatenate([first[take:], carry])[:HOP] + 0.0
                self.tail = carry
                return out * self.gain
            pos += take
        self.tail = carry
        return out * self.gain


# ---------------------------------------------------------------- modulators ---
class SlowDrift:
    """Smoothed random walk in [-1, 1]; used for wind gusts and wave sets."""

    def __init__(self, seed, period_s=45.0):
        self.rng = np.random.default_rng(seed)
        self.value = 0.0
        self.target = self.rng.uniform(-1, 1)
        self.period = period_s
        self.phase = 0.0

    def read(self, n):
        t = np.arange(n) / SR
        seg = self.period
        out = np.empty(n)
        i = 0
        while i < n:
            take = min(n - i, int(seg * SR))
            a = self.value
            b = self.target
            x = np.linspace(0.0, 1.0, take, endpoint=False)
            out[i:i + take] = a + (b - a) * (0.5 - 0.5 * np.cos(np.pi * x))
            i += take
            if i < n or take == int(seg * SR):
                self.value = b
                self.target = self.rng.uniform(-1, 1)
                seg = self.period * self.rng.uniform(0.6, 1.5)
        return out


def droplet_envelope(n, rng, rate_hz=14.0, decay_s=0.06):
    """Poisson-distributed exponentially decaying impulses -> drops on glass."""
    env = np.zeros(n + int(decay_s * SR) + 1)
    count = rng.poisson(rate_hz * n / SR)
    if count:
        pos = rng.integers(0, n, size=count)
        amp = rng.uniform(0.25, 1.0, size=count) ** 2
        env[pos] = np.maximum(env[pos], amp)
    k = np.exp(-np.arange(int(decay_s * SR)) / (decay_s * SR / 4.0))
    env = fftconv(env, k)[:n]
    m = env.max()
    return env / m if m > 0 else env


def crackle_envelope(n, rng, rate_hz=6.0, decay_s=0.018):
    """Sparse, very fast-decaying impulses — the pops of burning wood."""
    return droplet_envelope(n, rng, rate_hz=rate_hz, decay_s=decay_s)


# --------------------------------------------------------------- ambient pad ---
def fftconv(x, h):
    """FFT convolution. np.convolve is direct and far too slow for 5 s IRs."""
    n = len(x) + len(h) - 1
    N = 1 << int(math.ceil(math.log2(n)))
    y = np.fft.irfft(np.fft.rfft(x, N) * np.fft.rfft(h, N), N)
    return y[:len(x)]


def make_reverb_ir(seconds=5.5, seed=7):
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    decay = np.exp(-t * (6.5 / seconds))
    ir_l = rng.standard_normal(n) * decay
    ir_r = rng.standard_normal(n) * decay
    # dampen the high end of the tail so it sounds like a real hall, not static
    for ir in (ir_l, ir_r):
        f = _freqs(n)
        sp = np.fft.rfft(ir) * _band(f, 60.0, 4200.0, 1.0, 1.0)
        ir[:] = np.fft.irfft(sp, n)
    ir_l[:200] *= np.linspace(0, 1, 200)
    ir_r[:200] *= np.linspace(0, 1, 200)
    ir = np.stack([ir_l, ir_r], axis=1)
    return ir / (np.abs(ir).max() + 1e-12)


# equal temperament, A = 432 Hz by default (see 06-suno-and-frequencies.md:
# used purely as a warmer tuning, with no health claim attached)
def note_hz(semitones_from_a4, a4=432.0):
    return a4 * (2.0 ** (semitones_from_a4 / 12.0))


PAD_CHORDS = {
    # D minor voicings, spread over four octaves, in semitones from A4
    "dmin": [[-19, -12, -7, -3, 0, 5], [-19, -10, -7, -3, 2, 5],
             [-24, -12, -5, -3, 0, 7], [-19, -12, -7, 0, 5, 9]],
    "amin": [[-24, -12, -5, 0, 3, 7], [-24, -10, -5, 0, 3, 10],
             [-29, -12, -5, 3, 7, 12], [-24, -12, -8, 0, 4, 7]],
}


def render_pad_cell(seconds, chord, seed, ir):
    """One self-contained pad cell: additive partials, drift, then convolution."""
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    dry = np.zeros((n, 2))
    for st in chord:
        f0 = note_hz(st)
        for partial, weight in ((1, 1.0), (2, 0.28), (3, 0.11), (4, 0.05)):
            det = rng.uniform(-0.0016, 0.0016)
            f = f0 * partial * (1.0 + det)
            if f > 9000.0:
                continue
            # slow independent amplitude breathing per partial
            lfo_hz = rng.uniform(0.004, 0.021)
            amp = 0.5 + 0.5 * np.sin(2 * np.pi * lfo_hz * t + rng.uniform(0, 6.3))
            vib = 1.0 + 0.0009 * np.sin(2 * np.pi * rng.uniform(0.02, 0.07) * t)
            sig = np.sin(2 * np.pi * f * vib * t + rng.uniform(0, 6.3))
            g = weight / (1.0 + (f / 700.0) ** 1.1)
            pan = rng.uniform(0.25, 0.75)
            dry[:, 0] += sig * amp * g * (1.0 - pan)
            dry[:, 1] += sig * amp * g * pan
    dry *= 1.0 / (np.abs(dry).max() + 1e-12)
    wet = np.empty_like(dry)
    for ch in (0, 1):
        wet[:, ch] = fftconv(dry[:, ch], ir[:, ch])
    wet *= 1.0 / (np.abs(wet).max() + 1e-12)
    out = 0.18 * dry + 0.82 * wet               # mostly reverb: no clear onsets
    # window the cell so cells can be cross-faded without clicks
    fade = int(6.0 * SR)
    ramp = np.linspace(0.0, 1.0, fade)[:, None]
    out[:fade] *= ramp
    out[-fade:] *= ramp[::-1]
    return (out / (np.abs(out).max() + 1e-12)).astype(np.float32)


class PadStream:
    """Cross-fades pre-rendered pad cells in a shuffled, non-repeating order."""

    def __init__(self, key, seed, cell_s=75.0, xfade_s=6.0, n_cells=4):
        self.rng = np.random.default_rng(seed)
        ir = make_reverb_ir(seed=seed + 11)
        chords = PAD_CHORDS[key]
        self.cells = [
            render_pad_cell(cell_s, chords[i % len(chords)], seed + 100 + i, ir)
            for i in range(n_cells)
        ]
        self.xf = int(xfade_s * SR)
        self.buf = np.zeros((0, 2), dtype=np.float32)
        self.prev = -1
        self._extend()

    def _pick(self):
        i = self.rng.integers(0, len(self.cells))
        while i == self.prev and len(self.cells) > 1:
            i = self.rng.integers(0, len(self.cells))
        self.prev = i
        return self.cells[i]

    def _extend(self):
        cell = self._pick()
        if len(self.buf) < self.xf:
            self.buf = np.concatenate([self.buf, cell])
            return
        head = self.buf[-self.xf:] + cell[:self.xf]
        self.buf = np.concatenate([self.buf[:-self.xf], head, cell[self.xf:]])

    def read(self, n):
        while len(self.buf) < n + self.xf:
            self._extend()
        out = self.buf[:n].astype(np.float64)
        self.buf = self.buf[n:]
        return out


# -------------------------------------------------------------------- presets ---
class Layer:
    def __init__(self, source, gain, kind="noise"):
        self.source, self.gain, self.kind = source, gain, kind


def build_preset(name, seed):
    """Return (layers, describe) for a preset. Gains are pre-mastering."""
    L = []
    if name == "rain_window":
        L += [Layer(ShapedNoise(spectrum_rain_hiss, seed + 1), 0.62, "gust"),
              Layer(ShapedNoise(spectrum_rain_body, seed + 2), 0.45, "gust"),
              Layer(ShapedNoise(spectrum_droplet, seed + 3), 0.30, "drop"),
              Layer(ShapedNoise(spectrum_lowbed, seed + 4), 0.22, "flat")]
    elif name == "rain_pad":
        L += [Layer(ShapedNoise(spectrum_rain_hiss, seed + 1), 0.52, "gust"),
              Layer(ShapedNoise(spectrum_rain_body, seed + 2), 0.40, "gust"),
              Layer(ShapedNoise(spectrum_droplet, seed + 3), 0.22, "drop"),
              Layer(ShapedNoise(spectrum_lowbed, seed + 4), 0.20, "flat"),
              Layer(PadStream("dmin", seed + 5), 0.30, "pad")]
    elif name == "brown_noise":
        L += [Layer(ShapedNoise(spectrum_brown, seed + 1, 0.55), 1.00, "flat")]
    elif name == "pink_noise":
        L += [Layer(ShapedNoise(spectrum_pink, seed + 1, 0.55), 1.00, "flat")]
    elif name == "white_noise":
        L += [Layer(ShapedNoise(spectrum_white_soft, seed + 1, 0.55), 1.00, "flat")]
    elif name == "brown_rain":
        L += [Layer(ShapedNoise(spectrum_brown, seed + 1, 0.55), 0.70, "flat"),
              Layer(ShapedNoise(spectrum_rain_hiss, seed + 2), 0.32, "gust")]
    elif name == "fireplace":
        L += [Layer(ShapedNoise(spectrum_fire_body, seed + 1), 0.55, "gust"),
              Layer(ShapedNoise(spectrum_crackle, seed + 2), 0.42, "crackle"),
              Layer(ShapedNoise(spectrum_lowbed, seed + 3), 0.26, "flat")]
    elif name == "wind":
        L += [Layer(ShapedNoise(spectrum_wind, seed + 1), 0.80, "gust"),
              Layer(ShapedNoise(spectrum_lowbed, seed + 2), 0.30, "flat")]
    elif name == "stream":
        L += [Layer(ShapedNoise(spectrum_stream, seed + 1), 0.72, "ripple"),
              Layer(ShapedNoise(spectrum_rain_body, seed + 2), 0.30, "flat"),
              Layer(ShapedNoise(spectrum_lowbed, seed + 3), 0.18, "flat")]
    elif name == "ocean":
        L += [Layer(ShapedNoise(spectrum_ocean, seed + 1), 0.85, "wave"),
              Layer(ShapedNoise(spectrum_lowbed, seed + 2), 0.28, "flat")]
    elif name == "ocean_pad":
        L += [Layer(ShapedNoise(spectrum_ocean, seed + 1), 0.72, "wave"),
              Layer(ShapedNoise(spectrum_lowbed, seed + 2), 0.24, "flat"),
              Layer(PadStream("amin", seed + 3), 0.28, "pad")]
    elif name == "pad_only":
        L += [Layer(PadStream("dmin", seed + 1), 0.95, "pad"),
              Layer(ShapedNoise(spectrum_lowbed, seed + 2), 0.18, "flat")]
    else:
        raise SystemExit(f"unknown preset: {name}")
    return L


PRESETS = ["rain_window", "rain_pad", "brown_noise", "pink_noise", "white_noise",
           "brown_rain", "ocean", "ocean_pad", "pad_only", "fireplace", "wind",
           "stream"]


# --------------------------------------------------------------------- render ---
def render(preset, total_s, seed, out, gain_db=-12.0, decline_db=3.5,
           fade_in_s=20.0, fade_out_s=90.0, progress=True, probe=False):
    layers = build_preset(preset, seed)
    gust = SlowDrift(seed + 901, 55.0)
    wave = SlowDrift(seed + 902, 11.0)
    rng = np.random.default_rng(seed + 903)
    total_n = int(total_s * SR)
    chunk = HOP
    written = 0
    out_gain = 10 ** (gain_db / 20.0)
    if probe:                       # flat render used only to measure loudness
        decline_db, fade_in_s, fade_out_s = 0.0, 0.0, 0.0
    decline_n = min(total_n, int(45 * 60 * SR))

    while written < total_n:
        n = min(chunk, total_n - written)
        t0 = written / SR
        mix = np.zeros((n, 2))
        gust_depth = 0.45 if preset == "wind" else 0.14
        g_env = 1.0 + gust_depth * gust.read(n)
        w_raw = wave.read(n)
        w_env = 0.42 + 0.58 * (0.5 + 0.5 * np.sin(
            2 * np.pi * (t0 + np.arange(n) / SR) / 11.0 + 1.6 * w_raw))
        for lay in layers:
            sig = lay.source.read(n)
            if lay.kind == "gust":
                sig = sig * g_env[:, None]
            elif lay.kind == "wave":
                sig = sig * w_env[:, None]
            elif lay.kind == "drop":
                env = droplet_envelope(n, rng)
                sig = sig * (0.30 + 1.70 * env)[:, None]
            elif lay.kind == "crackle":
                env = crackle_envelope(n, rng)
                sig = sig * (0.06 + 2.60 * env)[:, None]
            elif lay.kind == "ripple":
                # fast, shallow modulation: water moving over stones
                tt = (written + np.arange(n)) / SR
                rip = 1.0 + 0.07 * np.sin(2 * np.pi * 0.7 * tt) \
                          + 0.05 * np.sin(2 * np.pi * 1.9 * tt + 2.1)
                sig = sig * rip[:, None]
            mix += sig * lay.gain

        # slow global decline: the bed quietly recedes as the listener settles
        idx = written + np.arange(n)
        if decline_db:
            d = np.clip(idx / max(decline_n, 1), 0.0, 1.0)
            mix *= (10 ** (-(decline_db * d) / 20.0))[:, None]

        if fade_in_s and written < fade_in_s * SR:        # fade in
            a = np.clip((idx / (fade_in_s * SR)), 0.0, 1.0)
            mix *= (a ** 2)[:, None]
        if fade_out_s:
            tail_start = total_n - fade_out_s * SR
            if written + n > tail_start:                  # fade out
                a = np.clip((total_n - idx) / (fade_out_s * SR), 0.0, 1.0)
                mix *= (a ** 1.5)[:, None]

        # calibrated output gain, then a soft ceiling instead of hard clipping
        mix *= out_gain
        mix = np.tanh(mix * 1.6) / 1.6
        mix = np.clip(mix, -1.0, 1.0)
        out.write((mix * 32767.0).astype("<i2").tobytes())
        written += n
        if progress and written % (SR * 300) < chunk:
            pct = 100.0 * written / total_n
            print(f"  audio {pct:5.1f}%  ({written/SR/60:.1f} min)",
                  file=sys.stderr, flush=True)
    return written


def wav_header(n_samples):
    data = n_samples * 2 * 2
    return (b"RIFF" + struct.pack("<I", 36 + data) + b"WAVEfmt " +
            struct.pack("<IHHIIHH", 16, 1, 2, SR, SR * 4, 4, 16) +
            b"data" + struct.pack("<I", data))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--preset", required=True, choices=PRESETS)
    p.add_argument("--hours", type=float, default=0.0)
    p.add_argument("--minutes", type=float, default=0.0)
    p.add_argument("--seconds", type=float, default=0.0)
    p.add_argument("--seed", type=int, default=20260921)
    p.add_argument("--gain-db", type=float, default=-12.0,
                   help="output gain; set it from a calibration probe")
    p.add_argument("--probe", action="store_true",
                   help="flat render with no fades/decline, for loudness calibration")
    p.add_argument("--decline-db", type=float, default=3.5)
    p.add_argument("--fade-in", type=float, default=20.0)
    p.add_argument("--fade-out", type=float, default=90.0)
    p.add_argument("--out", required=True, help="output .wav path, or - for stdout raw s16le")
    p.add_argument("--list-presets", action="store_true")
    a = p.parse_args()
    total = a.hours * 3600 + a.minutes * 60 + a.seconds
    if total <= 0:
        raise SystemExit("give --hours / --minutes / --seconds")
    n = int(total * SR)
    if a.out == "-":
        render(a.preset, total, a.seed, sys.stdout.buffer, a.gain_db,
               a.decline_db, fade_in_s=min(a.fade_in, total / 4),
               fade_out_s=min(a.fade_out, total / 3), probe=a.probe)
    else:
        with open(a.out, "wb") as f:
            f.write(wav_header(n))
            render(a.preset, total, a.seed, f, a.gain_db, a.decline_db,
                   fade_in_s=min(a.fade_in, total / 4),
                   fade_out_s=min(a.fade_out, total / 3), probe=a.probe)
    print(f"done: {a.preset} {total/60:.1f} min seed={a.seed}", file=sys.stderr)


if __name__ == "__main__":
    main()
