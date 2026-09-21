#!/usr/bin/env bash
# photoloop.sh — build a mathematically seamless video loop from 3 still images.
#
#   ./photoloop.sh a.png b.png c.png out/seg.mp4 [scene_s] [xfade_s] [W] [H] [FPS] [ZOOM]
#
# Construction (see ../global-sleep-brand/04-longform-and-seo.md, seamless loops):
# the chain is A_body -> B -> C -> A_head, where A_body is scene A starting X
# seconds into its zoom and A_head is the first X seconds of that same zoom. The
# final crossfade therefore lands on exactly the frame the segment opened with,
# so the segment can be stream-copied back to back for hours with no seam.
#
#   loop length = 3 * (scene_s - xfade_s)
#
# Nothing here is time-varying except the zoom, and the zoom is continuous across
# the wrap by construction. A brightness "breath" was deliberately left out: it
# would not line up at the wrap point and would show as a step every loop.
set -euo pipefail

A=$1; B=$2; C=$3; OUT=$4
S=${5:-40}; X=${6:-6}; W=${7:-1920}; H=${8:-1080}; FPS=${9:-24}; ZOOM=${10:-0.04}

FF="${FFMPEG:-$(python3 -c 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())')}"
N=$((S * FPS))            # frames in a full scene zoom
NX=$((X * FPS))           # frames in one crossfade
NB=$((N - NX))            # frames in A_body / B / C
SS=$((W * 2)); SH=$((H * 2))          # supersample keeps the slow zoom smooth
mkdir -p "$(dirname "$OUT")"

# $1 input index, $2 output frame count, $3 zoom offset in frames
scene () {
  echo "[$1:v]scale=${SS}:${SH}:force_original_aspect_ratio=increase,crop=${SS}:${SH},\
zoompan=z='1+${ZOOM}*($3+on)/${N}':d=$2:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=${W}x${H}:fps=${FPS},\
eq=saturation=0.94,format=yuv420p,setsar=1,fps=${FPS}"
}

OFF1=$((S - 2 * X)); OFF2=$((2 * S - 3 * X)); OFF3=$((3 * S - 4 * X))

"$FF" -y -hide_banner -loglevel "${FFLOG:-error}" \
  -i "$A" -i "$B" -i "$C" -i "$A" \
  -filter_complex "\
$(scene 0 "$NB" "$NX")[abody]; \
$(scene 1 "$N" 0)[b0]; \
$(scene 2 "$N" 0)[c0]; \
$(scene 3 "$NX" 0)[ahead]; \
[abody][b0]xfade=transition=fade:duration=${X}:offset=${OFF1}[s1]; \
[s1][c0]xfade=transition=fade:duration=${X}:offset=${OFF2}[s2]; \
[s2][ahead]xfade=transition=fade:duration=${X}:offset=${OFF3}[v]" \
  -map "[v]" -c:v libx264 -crf 23 -preset medium -tune stillimage \
  -g $((FPS * 2)) -pix_fmt yuv420p -movflags +faststart "$OUT"

"$FF" -hide_banner -i "$OUT" 2>&1 | grep -E "Duration|Stream" || true
echo "expected loop length: $((3 * (S - X)))s"
