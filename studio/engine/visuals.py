#!/usr/bin/env python3
"""
visuals.py — procedural, perfectly-looping visuals for long-form sleep videos.

Every frame is computed from scratch with numpy; nothing is sampled, downloaded
or model-generated, so the video track carries no third-party rights and needs
no synthetic-content declaration.

The loop is exact: all animation is driven by sin/cos whose periods divide the
loop length, so frame N is identical to frame 0. That means a 120 s segment can
be concatenated with `-c:v copy` for hours with no visible seam and no re-encode.

Writes raw rgb24 frames to stdout:
  python3 visuals.py --mode rainglass --seconds 120 --fps 24 --w 1920 --h 1080 \
    | ffmpeg -f rawvideo -pix_fmt rgb24 -s 1920x1080 -r 24 -i - ... segment.mp4
"""
import argparse, math, sys
import numpy as np

MODES = ["rainglass", "gradient", "black", "ember"]


# ------------------------------------------------------------------ helpers ---
def radial(h, w, cy, cx, r, softness=1.7):
    y = np.arange(h)[:, None] - cy
    x = np.arange(w)[None, :] - cx
    d = np.sqrt(y * y + x * x) / max(r, 1e-6)
    return np.clip(1.0 - d ** softness, 0.0, 1.0)


def vignette(h, w, strength=0.55):
    y = (np.arange(h)[:, None] / h - 0.5) * 2.0
    x = (np.arange(w)[None, :] / w - 0.5) * 2.0
    d = np.sqrt(x * x + y * y) / math.sqrt(2.0)
    return 1.0 - strength * np.clip(d, 0, 1) ** 1.6


def hex_rgb(s):
    s = s.lstrip("#")
    return np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float64) / 255.0


# palette locked to the brand tokens in 02-brand-and-visuals.md
BASE_DEEP = hex_rgb("0B1220")
BASE_MID = hex_rgb("16243A")
WARM_IVORY = hex_rgb("F2EDE4")
MUTED_GOLD = hex_rgb("C9A227")
RAIN_SLATE = hex_rgb("5C7A8A")
EMBER_RUST = hex_rgb("A85B3C")


# -------------------------------------------------------------- backgrounds ---
def build_bokeh_bg(h, w, seed, n_discs=140):
    """Soft out-of-focus city lights behind the glass."""
    rng = np.random.default_rng(seed)
    bg = np.zeros((h, w, 3))
    bg += BASE_DEEP
    # broad gradient: slightly lighter toward the lower centre (street glow)
    gy = (np.arange(h)[:, None] / h)
    bg += (BASE_MID - BASE_DEEP) * (gy ** 2.2)[:, :, None] * 1.15
    for _ in range(n_discs):
        cy = rng.uniform(-0.05, 1.05) * h
        cx = rng.uniform(-0.05, 1.05) * w
        r = rng.uniform(0.012, 0.055) * w
        warm = rng.random() < 0.62
        col = MUTED_GOLD if warm else RAIN_SLATE
        amp = rng.uniform(0.10, 0.50) * (0.6 if not warm else 1.0)
        m = radial(h, w, cy, cx, r, softness=1.35)
        bg += m[:, :, None] * col * amp
    return np.clip(bg, 0, 1).astype(np.float32)


def build_gradient_bg(h, w):
    gy = np.arange(h)[:, None] / h
    top = BASE_DEEP * 0.75
    bot = BASE_MID * 1.05
    return np.clip((top + (bot - top) * (gy ** 1.4))[:, :] * np.ones((1, w, 1)), 0, 1)


# ------------------------------------------------------------ rain droplets ---
class Streaks:
    """Droplets sliding down the glass. Travel time divides the loop exactly."""

    def __init__(self, h, w, fps, loop_frames, seed, count=42):
        rng = np.random.default_rng(seed)
        self.h, self.w = h, w
        self.loop = loop_frames
        self.items = []
        for _ in range(count):
            laps = int(rng.integers(2, 7))          # whole laps per loop -> seamless
            x = int(rng.uniform(0.02, 0.98) * w)
            width = max(1, int(rng.uniform(0.0012, 0.0045) * w))
            length = int(rng.uniform(0.05, 0.22) * h)
            amp = rng.uniform(0.05, 0.20)
            phase = rng.uniform(0, 1)
            self.items.append((laps, x, width, length, amp, phase))
        # sprite: bright rounded head fading into a thin tail
        self.sprites = {}

    def _sprite(self, length, width):
        key = (length, width)
        if key not in self.sprites:
            t = np.linspace(0.0, 1.0, length)[:, None]
            tail = t ** 3.0                          # faint at top, bright at head
            tail[-max(2, length // 14):] *= 2.1  # rounded bright head
            xs = np.linspace(-1.0, 1.0, 2 * width + 1)[None, :]
            prof = np.clip(1.0 - xs ** 2, 0, 1) ** 1.2
            self.sprites[key] = tail * prof
        return self.sprites[key]

    def render(self, frame_idx, out):
        h, w = self.h, self.w
        for laps, x, width, length, amp, phase in self.items:
            p = ((frame_idx / self.loop) * laps + phase) % 1.0
            head = int(p * (h + length)) - length
            spr = self._sprite(length, width)
            y0, y1 = head - length, head
            sy0, sy1 = max(0, y0), min(h, y1)
            if sy1 <= sy0:
                continue
            x0, x1 = max(0, x - width), min(w, x + width + 1)
            sub = spr[sy0 - y0:sy1 - y0, :x1 - x0]
            out[sy0:sy1, x0:x1, :] += sub[:, :, None] * WARM_IVORY * amp


def build_static_drops(h, w, seed, count=420):
    """Stationary beaded droplets clinging to the glass."""
    rng = np.random.default_rng(seed)
    layer = np.zeros((h, w))
    for _ in range(count):
        cy = rng.uniform(0, 1) * h
        cx = rng.uniform(0, 1) * w
        r = rng.uniform(0.0015, 0.006) * w
        layer += radial(h, w, cy, cx, r, softness=2.4) * rng.uniform(0.10, 0.45)
    return np.clip(layer, 0, 1.2).astype(np.float32)


# ------------------------------------------------------------------- render ---
def run(mode, seconds, fps, w, h, seed, out, grain=0.006, progress=True):
    loop_frames = int(round(seconds * fps))
    if loop_frames % 24 != 0:
        loop_frames -= loop_frames % 24              # keep grain cycle periodic
    rng = np.random.default_rng(seed + 5)

    if mode == "rainglass":
        bg = build_bokeh_bg(h, w, seed)
        static = build_static_drops(h, w, seed + 1)
        streaks = Streaks(h, w, fps, loop_frames, seed + 2)
    elif mode == "ember":
        bg = build_bokeh_bg(h, w, seed, n_discs=60) * 0.55
        bg += EMBER_RUST * radial(h, w, h * 0.72, w * 0.5, w * 0.42, 1.2)[:, :, None] * 0.55
        bg = np.clip(bg, 0, 1).astype(np.float32)
        static = build_static_drops(h, w, seed + 1, count=120) * 0.25
        streaks = None
    elif mode == "gradient":
        bg = build_gradient_bg(h, w).astype(np.float32)
        static = None
        streaks = None
    else:                                            # black
        bg = np.zeros((h, w, 3)) + BASE_DEEP * 0.22
        bg += radial(h, w, h * 0.5, w * 0.5, w * 0.55, 1.1)[:, :, None] * BASE_MID * 0.30
        bg = bg.astype(np.float32)
        static = None
        streaks = None

    vig = vignette(h, w, 0.50 if mode != "black" else 0.20)[:, :, None].astype(np.float32)
    grains = [rng.standard_normal((h, w, 1)).astype(np.float32) * grain for _ in range(24)]
    buf = np.empty((h, w, 3), dtype=np.float32)

    # zoom is applied by ffmpeg, not here: resampling every frame in numpy is
    # slower than letting the encoder's scaler do it once per segment.
    for i in range(loop_frames):
        ph = 2.0 * math.pi * i / loop_frames
        # brightness breathing, two harmonics -> never feels like a metronome
        bright = 1.0 + 0.035 * math.sin(ph) + 0.018 * math.sin(2 * ph + 1.1)
        buf[:] = bg * bright
        if static is not None:
            tw = 1.0 + 0.10 * math.sin(2 * ph + 0.4)
            buf += static[:, :, None] * WARM_IVORY * 0.16 * tw
        if streaks is not None:
            streaks.render(i, buf)
        buf *= vig
        buf += grains[i % 24]
        np.clip(buf, 0.0, 1.0, out=buf)
        out.write((buf * 255.0 + 0.5).astype(np.uint8).tobytes())
        if progress and i % (fps * 10) == 0:
            print(f"  video {100.0*i/loop_frames:5.1f}%", file=sys.stderr, flush=True)
    return loop_frames


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", required=True, choices=MODES)
    p.add_argument("--seconds", type=float, default=120.0)
    p.add_argument("--fps", type=int, default=24)
    p.add_argument("--w", type=int, default=1920)
    p.add_argument("--h", type=int, default=1080)
    p.add_argument("--seed", type=int, default=20260921)
    p.add_argument("--grain", type=float, default=0.006)
    a = p.parse_args()
    n = run(a.mode, a.seconds, a.fps, a.w, a.h, a.seed, sys.stdout.buffer, a.grain)
    print(f"frames={n} loop={n/a.fps:.2f}s", file=sys.stderr)


if __name__ == "__main__":
    main()
