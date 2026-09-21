#!/usr/bin/env bash
# build.sh — render one long-form sleep video end to end.
#
#   ./build.sh --preset rain_window --mode rainglass --hours 3 --out out/rain3h.mp4
#
# The visual is one perfectly-looping segment encoded once and then stream-looped
# with -c:v copy, so a 10-hour render costs the same encoding work as a 90-second
# one. The audio is synthesised continuously for the full duration and never
# repeats.
set -euo pipefail

PRESET=rain_window; MODE=rainglass; HOURS=0; MINUTES=0; OUT=out/video.mp4
LOOP=90; FPS=24; W=1920; H=1080; SEED=20260921; CRF=25; ABR=192k; KEEP=0
TARGET_LUFS=-14; GAIN_DB=
PHOTOS=; SCENE=40; XFADE=6; ZOOM=0.04

while [ $# -gt 0 ]; do
  case "$1" in
    --preset) PRESET=$2; shift 2;;
    --mode)   MODE=$2; shift 2;;
    --hours)  HOURS=$2; shift 2;;
    --minutes) MINUTES=$2; shift 2;;
    --out)    OUT=$2; shift 2;;
    --loop)   LOOP=$2; shift 2;;
    --fps)    FPS=$2; shift 2;;
    --w)      W=$2; shift 2;;
    --h)      H=$2; shift 2;;
    --seed)   SEED=$2; shift 2;;
    --crf)    CRF=$2; shift 2;;
    --keep)   KEEP=1; shift;;
    --lufs)   TARGET_LUFS=$2; shift 2;;
    --gain-db) GAIN_DB=$2; shift 2;;
    --photos) PHOTOS=$2; shift 2;;
    --scene)  SCENE=$2; shift 2;;
    --xfade)  XFADE=$2; shift 2;;
    --zoom)   ZOOM=$2; shift 2;;
    *) echo "unknown option: $1" >&2; exit 2;;
  esac
done

HERE="$(cd "$(dirname "$0")" && pwd)"
. "$(dirname "$0")/preflight.sh"
FF="${FFMPEG:-$(python3 -c 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())')}"
TOTAL=$(python3 -c "print($HOURS*3600 + $MINUTES*60)")
[ "$(python3 -c "print(1 if $TOTAL>0 else 0)")" = 1 ] || { echo "give --hours/--minutes" >&2; exit 2; }
mkdir -p "$(dirname "$OUT")"
TMP="$(mktemp -d)"; [ "$KEEP" = 1 ] || trap 'rm -rf "$TMP"' EXIT

if [ "$MODE" = photo ]; then
  [ -n "$PHOTOS" ] || { echo "--mode photo needs --photos a.png,b.png,c.png" >&2; exit 2; }
  IFS=, read -r P1 P2 P3 <<<"$PHOTOS"
  for f in "$P1" "$P2" "$P3"; do
    [ -f "$f" ] || { echo "missing photo: $f" >&2; exit 2; }
  done
  LOOP=$((3 * (SCENE - XFADE)))
  echo "[1/3] photo loop: ${LOOP}s ${W}x${H}@${FPS} (scene ${SCENE}s, xfade ${XFADE}s)"
  FFMPEG="$FF" "$HERE/photoloop.sh" "$P1" "$P2" "$P3" "$TMP/seg.mp4" \
      "$SCENE" "$XFADE" "$W" "$H" "$FPS" "$ZOOM" >/dev/null
else
  echo "[1/3] visual loop: ${MODE} ${LOOP}s ${W}x${H}@${FPS}"
  python3 "$HERE/visuals.py" --mode "$MODE" --seconds "$LOOP" --fps "$FPS" \
          --w "$W" --h "$H" --seed "$SEED" \
    | "$FF" -y -hide_banner -loglevel error \
        -f rawvideo -pix_fmt rgb24 -s "${W}x${H}" -r "$FPS" -i - \
        -c:v libx264 -crf "$CRF" -preset medium -tune stillimage \
        -g $((FPS*2)) -pix_fmt yuv420p -movflags +faststart "$TMP/seg.mp4"
fi

if [ -z "$GAIN_DB" ]; then
  echo "[2/3] calibrating loudness to ${TARGET_LUFS} LUFS"
  GAIN_DB=$(FFMPEG="$FF" python3 "$HERE/calibrate.py" --preset "$PRESET" \
              --seed "$SEED" --target-lufs "$TARGET_LUFS" | awk '{print $1}')
  echo "      output gain: ${GAIN_DB} dB"
fi
echo "[2/3] audio: ${PRESET} $(python3 -c "print(f'{$TOTAL/3600:.2f}')") h"
python3 "$HERE/sleepaudio.py" --preset "$PRESET" --seconds "$TOTAL" \
        --seed "$SEED" --gain-db "$GAIN_DB" --out "$TMP/audio.wav"

REPEATS=$(python3 -c "import math;print(max(1,math.ceil($TOTAL/$LOOP)))")
echo "[3/3] mux (${REPEATS} loops, video stream-copied)"
"$FF" -y -hide_banner -loglevel error \
    -stream_loop $((REPEATS)) -i "$TMP/seg.mp4" -i "$TMP/audio.wav" \
    -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a "$ABR" -ar 48000 \
    -t "$TOTAL" -movflags +faststart "$OUT"

"$FF" -hide_banner -i "$OUT" 2>&1 | grep -E "Duration|Stream" || true
ls -lh "$OUT"
