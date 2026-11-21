#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

usage() {
  cat <<'EOF'
Last Train Linux helper

Usage:
  ./lasttrain.sh [install]
  ./lasttrain.sh start [--no-browser]
  ./lasttrain.sh stop
  ./lasttrain.sh backup
  ./lasttrain.sh restore [--file backup.zip]
  ./lasttrain.sh doctor

With no command, install dependencies, build the app and initialize its profile.
EOF
}

install_app() {
  fail() { printf 'Installation failed: %s\n' "$*" >&2; exit 1; }
  command -v python3 >/dev/null || fail 'Python 3.12–3.14 is required.'
  python3 - <<'PY' || fail 'Python 3.12–3.14 is required.'
import sys
raise SystemExit(0 if (3, 12) <= sys.version_info[:2] < (3, 15) else 1)
PY
  command -v node >/dev/null || fail 'Node.js 22 or newer is required.'
  node -e 'if (Number(process.versions.node.split(".")[0]) < 22) process.exit(1)' || fail 'Node.js 22 or newer is required.'
  command -v npm >/dev/null || fail 'npm is required (normally included with Node.js).'

  local venv="$ROOT/back/.venv"
  [[ -x "$venv/bin/python" ]] || python3 -m venv "$venv"
  local python="$venv/bin/python"

  # Stop this installation's owned server before replacing its dependencies.
  local data_dir="${LASTTRAIN_DATA_DIR:-$ROOT/data}"
  if [[ -f "$data_dir/server.json" ]]; then "$python" back/launcher.py stop; fi

  "$python" -m pip install -r back/requirements.txt
  (
    cd front
    npm install --no-audit --no-fund
    npm run build
  )
  "$python" back/launcher.py init
  "$python" back/launcher.py doctor
  printf '\nSetup complete. Start Last Train with ./lasttrain.sh start.\n'
}

command_name="${1:-install}"
if (($#)); then shift; fi
case "$command_name" in
  install|setup) install_app ;;
  start|stop|backup|restore|doctor)
    python="$ROOT/back/.venv/bin/python"
    [[ -x "$python" ]] || { echo 'Run ./lasttrain.sh install first.' >&2; exit 1; }
    exec "$python" "$ROOT/back/launcher.py" "$command_name" "$@"
    ;;
  -h|--help|help) usage ;;
  *) usage >&2; exit 2 ;;
esac
