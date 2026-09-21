#!/usr/bin/env python3
"""Measure a preset's loudness on a short flat probe and print the output gain
needed to hit a target integrated LUFS. Sleep beds are stationary, so a 90 s
probe predicts an 8-hour render to well within 0.5 LU."""
import argparse, json, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def ffmpeg():
    return os.environ.get("FFMPEG") or subprocess.run(
        [sys.executable, "-c",
         "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())"],
        capture_output=True, text=True, check=True).stdout.strip()


def measure(path, ff):
    out = subprocess.run(
        [ff, "-hide_banner", "-nostats", "-i", path,
         "-af", "loudnorm=print_format=json", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    blob = re.findall(r"\{[^{}]*input_i[^{}]*\}", out, re.S)
    if not blob:
        raise SystemExit("could not parse loudnorm output")
    d = json.loads(blob[-1])
    return float(d["input_i"]), float(d["input_tp"])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--preset", required=True)
    p.add_argument("--seed", type=int, default=20260921)
    p.add_argument("--target-lufs", type=float, default=-14.0)
    p.add_argument("--max-tp", type=float, default=-1.0)
    p.add_argument("--probe-seconds", type=float, default=90.0)
    a = p.parse_args()
    ff = ffmpeg()
    with tempfile.TemporaryDirectory() as td:
        wav = os.path.join(td, "probe.wav")
        subprocess.run([sys.executable, os.path.join(HERE, "sleepaudio.py"),
                        "--preset", a.preset, "--seconds", str(a.probe_seconds),
                        "--seed", str(a.seed), "--gain-db", "0", "--probe",
                        "--out", wav], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        lufs, tp = measure(wav, ff)
    gain = a.target_lufs - lufs
    # keep true peak under the ceiling as well; whichever limit binds, wins
    gain = min(gain, a.max_tp - tp)
    print(f"{gain:.2f}", end="")
    print(f"   # probe {lufs:.1f} LUFS / {tp:.1f} dBTP -> target "
          f"{a.target_lufs} LUFS", file=sys.stderr)


if __name__ == "__main__":
    main()
