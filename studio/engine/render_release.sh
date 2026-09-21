#!/usr/bin/env bash
# render_release.sh — render every video in a release spec, plus its thumbnail.
#
#   ./engine/render_release.sh releases/batch-01.json
#
# Run engine/fetch_assets.sh first: the photo-mode entries need the stills.
# Expect roughly 25 min per 3-hour video and 45 min per 8-hour one on one core;
# the whole batch is an overnight job.
set -euo pipefail
SPEC=${1:?usage: render_release.sh releases/batch-01.json}
HERE="$(cd "$(dirname "$0")/.." && pwd)"
cd "$HERE"
export FFMPEG="${FFMPEG:-$(python3 -c 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())')}"

python3 - "$SPEC" <<'PY' > /tmp/_release_cmds.sh
import json, sys
spec = json.load(open(sys.argv[1], encoding="utf-8"))
for v in spec["videos"]:
    print(f'echo "=== {v["slug"]} ==="')
    print(v["render"]); print(v["thumb"])
PY
bash -e /tmp/_release_cmds.sh
echo "all done -> out/"
