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
  ./lasttrain.sh desktop-install
  ./lasttrain.sh desktop-remove

With no command, install dependencies, build the app and initialize its profile.
EOF
}

desktop_exec_quote() {
  python3 -c 'import sys; s=sys.argv[1]; special=chr(92)+chr(34)+chr(96)+chr(36); print(chr(34)+"".join(chr(92)+c if c in special else c for c in s)+chr(34))' "$1"
}

desktop_install() {
  local python="$ROOT/back/.venv/bin/python"
  [[ -x "$python" ]] || { echo 'Run ./lasttrain.sh install before adding the application shortcut.' >&2; exit 1; }

  local xdg_data="${XDG_DATA_HOME:-$HOME/.local/share}"
  [[ "$xdg_data" == /* ]] || { echo 'XDG_DATA_HOME must be an absolute path.' >&2; exit 1; }
  local applications="$xdg_data/applications"
  local icons="$xdg_data/icons/hicolor/scalable/apps"
  local desktop_file="$applications/lasttrain.desktop"
  local icon_file="$icons/lasttrain.svg"
  mkdir -p "$applications" "$icons"
  install -m 0644 "$ROOT/assets/lasttrain.svg" "$icon_file"

  local temp_file="$desktop_file.tmp.$$"
  {
    printf '[Desktop Entry]\n'
    printf 'Version=1.0\n'
    printf 'Type=Application\n'
    printf 'Name=Last Train\n'
    printf 'Comment=Focus, rest, and reflect along the railway\n'
    printf 'Exec=%s start\n' "$(desktop_exec_quote "$ROOT/lasttrain.sh")"
    printf 'Icon=%s\n' "$icon_file"
    printf 'Terminal=false\n'
    printf 'StartupNotify=true\n'
    printf 'Categories=Office;Utility;\n'
  } > "$temp_file"
  chmod 0644 "$temp_file"
  mv -f -- "$temp_file" "$desktop_file"
  printf 'Application shortcut installed: %s\n' "$desktop_file"
  printf 'You can now launch Last Train from your applications menu.\n'
}

desktop_remove() {
  local xdg_data="${XDG_DATA_HOME:-$HOME/.local/share}"
  [[ "$xdg_data" == /* ]] || { echo 'XDG_DATA_HOME must be an absolute path.' >&2; exit 1; }
  rm -f -- "$xdg_data/applications/lasttrain.desktop" \
    "$xdg_data/icons/hicolor/scalable/apps/lasttrain.svg"
  printf 'Last Train application shortcut removed. Your profile and project files were kept.\n'
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
  desktop-install) desktop_install ;;
  desktop-remove) desktop_remove ;;
  start|stop|backup|restore|doctor)
    python="$ROOT/back/.venv/bin/python"
    [[ -x "$python" ]] || { echo 'Run ./lasttrain.sh install first.' >&2; exit 1; }
    exec "$python" "$ROOT/back/launcher.py" "$command_name" "$@"
    ;;
  -h|--help|help) usage ;;
  *) usage >&2; exit 2 ;;
esac
