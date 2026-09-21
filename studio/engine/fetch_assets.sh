#!/usr/bin/env bash
# fetch_assets.sh — download the Higgsfield stills listed in assets/MANIFEST.json.
# Run this on your own machine: the session that generated them could not reach
# the CDN itself (egress policy), so the files were never downloaded here.
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
cd "$HERE/assets"
python3 - <<'PY'
import json, os, urllib.request
m = json.load(open("MANIFEST.json", encoding="utf-8"))
base = m["base"].rstrip("/")
for name, path in m["files"].items():
    if os.path.exists(name):
        print("skip", name); continue
    url = f"{base}/{path}"
    print("get ", name)
    urllib.request.urlretrieve(url, name)
print("done ->", os.getcwd())
PY
