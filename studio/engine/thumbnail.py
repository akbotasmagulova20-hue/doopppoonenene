#!/usr/bin/env python3
"""
thumbnail.py — build a thumbnail in the channel's fixed layout.

Layout is the one specified in ../global-sleep-brand/02-brand-and-visuals.md:
logo mark top-left, two-word label bottom-left, duration bottom-right, series
accent rule, darkening gradient for legibility. Keeping every thumbnail on the
same grid is what makes the channel recognisable in a feed before the text is
read — which is the CTR lever in this niche.

  python3 thumbnail.py --title "DEEP SLEEP" --duration 8H --accent sleep \
      --bg ../assets/scene_a.png --out ../out/thumb.png

Without --bg it draws a procedural background, so it never blocks on artwork.

Text is drawn with Pillow rather than ffmpeg's drawtext: the portable ffmpeg
build used here is compiled without freetype, so drawtext is unavailable.
"""
import argparse, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import visuals as V

W, H = 1280, 720

ACCENTS = {
    "sleep":  "3A4E7A", "rain":  "5C7A8A", "nature": "4A6350",
    "ember":  "A85B3C", "noise": "2E3440", "focus":  "546A87",
    "gold":   "C9A227",
}
FONT = os.environ.get(
    "THUMB_FONT", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
THIN = " "          # thin space, used for the brand's wide letter tracking


def ffmpeg():
    return os.environ.get("FFMPEG") or subprocess.run(
        [sys.executable, "-c",
         "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())"],
        capture_output=True, text=True, check=True).stdout.strip()


def load_bg(path, ff):
    """Decode an image and cover-fit it to the thumbnail frame."""
    raw = subprocess.run(
        [ff, "-v", "error", "-i", path,
         "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}",
         "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        capture_output=True).stdout
    if len(raw) != W * H * 3:
        raise SystemExit(f"could not decode background: {path}")
    return np.frombuffer(raw, np.uint8).astype(np.float32).reshape(H, W, 3) / 255.0


def logo_mark(size):
    """Crescent moon dipping behind a horizon line, drawn as a single thin stroke."""
    a = np.zeros((size, size), np.float32)
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    cy, cx, r = size * 0.40, size * 0.5, size * 0.26
    hz = size * 0.66                                       # horizon height
    d = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2)
    ring = np.clip(1.0 - np.abs(d - r) / (size * 0.026), 0, 1)
    a = np.maximum(a, ring * (yy < hz))                    # moon, cut at horizon
    # the line runs the full width so the moon reads as setting behind it,
    # not as an open bowl
    horizon = np.clip(1.0 - np.abs(yy - hz) / (size * 0.020), 0, 1)
    a = np.maximum(a, horizon)
    return a


def build_plate(bg, accent, darken=0.30):
    img = bg * (1.0 - darken)

    # gradient scrim: text sits on the bottom third, so darken it further
    gy = np.clip((np.arange(H) - H * 0.52) / (H * 0.48), 0, 1)[:, None, None]
    img *= 1.0 - 0.58 * (gy ** 1.5)

    img *= V.vignette(H, W, 0.38)[:, :, None]

    # series accent: a short rule above the label
    col = V.hex_rgb(ACCENTS[accent]).astype(np.float32)
    y0, y1 = int(H * 0.735), int(H * 0.742)
    x0, x1 = int(W * 0.055), int(W * 0.175)
    img[y0:y1, x0:x1] = col * 1.5

    # logo mark, top-left, held back to 60% so it never competes with the label
    s = int(H * 0.085)
    mark = logo_mark(s)[:, :, None] * V.WARM_IVORY.astype(np.float32) * 0.60
    oy, ox = int(H * 0.06), int(W * 0.055)
    region = img[oy:oy + s, ox:ox + s]
    img[oy:oy + s, ox:ox + s] = np.clip(region + mark, 0, 1)

    return np.clip(img, 0, 1)


def track(text):
    return THIN.join(text)


def legibility(path, ff):
    """Downscale to feed width and report label contrast; 120 px is the real test."""
    raw = subprocess.run(
        [ff, "-v", "error", "-i", path, "-vf", "scale=120:-1",
         "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
        capture_output=True).stdout
    a = np.frombuffer(raw, np.uint8).astype(np.float32).reshape(-1, 120) / 255.0
    band = a[int(a.shape[0] * 0.74):int(a.shape[0] * 0.90)]
    return float(band.max() - band.min())


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--title", required=True, help="one or two words, kept short")
    p.add_argument("--duration", default="", help="e.g. 8H, 3H, 60M")
    p.add_argument("--accent", default="sleep", choices=sorted(ACCENTS))
    p.add_argument("--bg", default="", help="background image; omit for procedural")
    p.add_argument("--seed", type=int, default=20260921)
    p.add_argument("--out", required=True)
    a = p.parse_args()

    if len(a.title.split()) > 2:
        print("warning: more than two words reads as noise at feed size",
              file=sys.stderr)

    ff = ffmpeg()
    if a.bg:
        bg = load_bg(a.bg, ff)
    else:
        bg = V.build_bokeh_bg(H, W, a.seed).astype(np.float32)

    plate = build_plate(bg, a.accent)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)

    im = Image.fromarray((plate * 255 + 0.5).astype(np.uint8), "RGB")
    d = ImageDraw.Draw(im)
    try:
        f_title = ImageFont.truetype(FONT, 66)
        f_dur = ImageFont.truetype(FONT, 46)
    except OSError:
        raise SystemExit(f"font not found: {FONT} (override with THUMB_FONT)")

    ivory = (242, 237, 228)
    d.text((int(W * 0.055), int(H * 0.775)), track(a.title.upper()),
           font=f_title, fill=ivory)
    if a.duration:
        txt = track(a.duration.upper())
        tw = d.textlength(txt, font=f_dur)
        d.text((W - tw - int(W * 0.055), int(H * 0.788)), txt,
               font=f_dur, fill=(242, 237, 228))
    im.save(a.out)

    c = legibility(a.out, ff)
    verdict = "ok" if c > 0.45 else "LOW — raise contrast or move the label"
    print(f"{a.out}  label contrast at 120px: {c:.2f}  ({verdict})")


if __name__ == "__main__":
    main()
