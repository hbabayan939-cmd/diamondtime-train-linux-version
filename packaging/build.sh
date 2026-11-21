#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

[[ "$(uname -m)" == "x86_64" ]] || {
  echo 'The current PyInstaller spec produces a Linux x86_64 archive.' >&2
  exit 1
}
command -v python3 >/dev/null || { echo 'Python 3 is required.' >&2; exit 1; }
command -v node >/dev/null || { echo 'Node.js 22+ is required to build the frontend.' >&2; exit 1; }
command -v npm >/dev/null || { echo 'npm is required to build the frontend.' >&2; exit 1; }
python3 - <<'PY' || { echo 'Python 3.12–3.14 is required.' >&2; exit 1; }
import sys
raise SystemExit(0 if (3, 12) <= sys.version_info[:2] < (3, 15) else 1)
PY

# Build only generated artifacts; do not initialize or migrate a personal profile.
node -e 'if (Number(process.versions.node.split(".")[0]) < 22) process.exit(1)' || {
  echo 'Node.js 22 or newer is required.' >&2
  exit 1
}
npm --prefix front install --no-audit --no-fund
npm --prefix front run build

BUILD_VENV="$ROOT/packaging/.venv"
if [[ ! -x "$BUILD_VENV/bin/python" ]]; then python3 -m venv "$BUILD_VENV"; fi
PYTHON="$BUILD_VENV/bin/python"
"$PYTHON" -m pip install -r packaging/requirements-build.txt
"$PYTHON" -m PyInstaller --noconfirm --clean packaging/lasttrain.spec
cp packaging/README.txt dist/LastTrain-Linux-x86_64/README.txt
"$PYTHON" packaging/make_zip.py

printf '\nLinux package created: %s\n' "$ROOT/dist/LastTrain-Linux-x86_64.zip"
