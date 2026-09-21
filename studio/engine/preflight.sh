# preflight.sh — sourced by the entry scripts. Fails with an actionable message
# instead of a Python traceback when the interpreter running these scripts is not
# the one pip installed into (the usual macOS system-vs-Homebrew split).
_missing=""
for mod in numpy imageio_ffmpeg; do
  python3 -c "import $mod" 2>/dev/null || _missing="$_missing $mod"
done
if [ -n "$_missing" ]; then
  cat >&2 <<MSG

  Missing Python modules for $(command -v python3):$_missing

  pip most likely installed them into a different interpreter. A virtual
  environment removes the mismatch entirely:

      cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
      python3 -m venv .venv
      source .venv/bin/activate
      python3 -m pip install numpy imageio-ffmpeg Pillow

  Then run this script again. Pillow is only needed for thumbnails.

MSG
  exit 1
fi
unset _missing
