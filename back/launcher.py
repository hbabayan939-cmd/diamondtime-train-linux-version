"""One local Waitress server; private data stays outside source files."""
import argparse
import contextlib
import hashlib
import http.client
import json
import os
import socket
import subprocess
import sys
import time
import urllib.request
import uuid
import webbrowser
from pathlib import Path

ROOT = Path(sys._MEIPASS) if getattr(sys, "frozen", False) else Path(__file__).resolve().parent.parent
DATA = Path(os.environ.get("LASTTRAIN_DATA_DIR", ROOT / "data")).resolve()
DATA.mkdir(parents=True, exist_ok=True)
STATE = DATA / "server.json"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")


@contextlib.contextmanager
def lock(name):
    # flock locks are released by the OS if a process exits unexpectedly.
    import fcntl
    identity = hashlib.sha256(str(DATA).encode("utf-8")).hexdigest()[:24]
    lock_path = DATA / f".{identity}-{name}"
    with lock_path.open("a+") as handle:
        operation = fcntl.LOCK_EX
        if name != "launcher.lock":
            operation |= fcntl.LOCK_NB
        if name == "launcher.lock":
            deadline = time.monotonic() + 120
            while True:
                try:
                    fcntl.flock(handle, operation | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    if time.monotonic() >= deadline:
                        raise RuntimeError("Last Train is running or maintenance is in progress. Close the other instance first.")
                    time.sleep(.1)
        else:
            try:
                fcntl.flock(handle, operation)
            except BlockingIOError as exc:
                raise RuntimeError("Last Train is already running or maintenance is in progress.") from exc
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def build_identity():
    if getattr(sys, "frozen", False):
        executable = Path(sys.executable).resolve()
        digest = hashlib.sha256(executable.read_bytes())
        frontend = ROOT / "front" / "dist"
        for asset in sorted(path for path in frontend.rglob("*") if path.is_file()):
            digest.update(asset.relative_to(frontend).as_posix().encode("utf-8"))
            digest.update(asset.read_bytes())
        return digest.hexdigest()
    return "source:" + str(Path(__file__).resolve()).lower()


def compatible_state(state):
    if state.get("build"):
        return state["build"] == build_identity()
    # Historical state had no build marker. Only the exact running executable
    # can be reused or stopped; another extracted version remains incompatible.
    process = owned_process(state)
    if not process:
        return False
    if getattr(sys, "frozen", False):
        executable = Path(sys.executable).resolve()
        return Path(process.exe()).resolve() == executable
    return str(Path(__file__).resolve()) in process.cmdline()


def django_ready():
    import django
    django.setup()


def check_migration_compatibility():
    from django.db import connection, connections
    from django.db.migrations.loader import MigrationLoader
    try:
        loader = MigrationLoader(connection)
        if any(tuple(row) not in loader.disk_migrations for row in loader.applied_migrations):
            raise RuntimeError("Database was created by a newer Last Train version. Update the application; the data was not changed.")
    finally:
        connections.close_all()


def initialize():
    from local_data import create_backup, integrity, snapshot
    target = DATA / "lasttrain.sqlite3"
    legacy = ROOT / "back" / "db.sqlite3"
    if (not target.exists() or target.stat().st_size == 0) and legacy.exists() and not os.environ.get("LASTTRAIN_DATA_DIR"):
        staging = DATA / (uuid.uuid4().hex + ".sqlite3")
        snapshot(legacy, staging)
        staging.replace(target)
        print("Copied existing back/db.sqlite3 safely. Original retained.")
    if target.exists():
        integrity(target)
        print("Pre-migration backup:", create_backup(DATA))
    django_ready()
    # Django can otherwise ignore migration rows belonging to a newer build.
    check_migration_compatibility()
    from django.core.management import call_command
    call_command("migrate", interactive=False)
    from journeys.local import local_context
    from django.contrib.auth import get_user_model
    context = local_context()
    print("Local profile:", context.owner_id)
    if get_user_model().objects.count() > 1:
        print("Multiple legacy profiles preserved. Choose their records in Settings > Stored profiles.")
    integrity(target)
    from django.db import connections
    connections.close_all()
    (DATA / "user-files").mkdir(exist_ok=True)


def validate():
    from local_data import integrity
    if not (DATA / "lasttrain.sqlite3").is_file():
        raise RuntimeError("Database missing. Initialize the profile with the install command for this edition.")
    integrity(DATA / "lasttrain.sqlite3")
    dist = ROOT / "front" / "dist"
    if not (dist / "index.html").is_file() or not list((dist / "assets").glob("*.js")):
        raise RuntimeError("Frontend build missing. Build the frontend with the install command for this edition.")
    required_art = "carriage carriage-detail architecture-lights distant-birds firefly-strip foreground-ground glass-rain glass lamp-light mid-pines near-pines panel-texture paper-texture rain-0 rain-1 rain-2 rain-3 rail-tunnel-v3 valley-afternoon valley-dawn valley-fog valley-morning valley-night valley-sunset valley-twilight water-shimmer window-mask".split()
    for name in required_art:
        if not (dist / "art" / (name + ".png")).is_file():
            raise RuntimeError(f"Missing artwork: {name}. Build the frontend with the install command for this edition.")
    import re
    for reference in re.findall(r'(?:src|href)="(/assets/[^"]+)"', (dist / "index.html").read_text(encoding="utf-8")):
        asset = (dist / reference.lstrip("/")).resolve()
        if not asset.is_relative_to(dist.resolve()) or not asset.is_file():
            raise RuntimeError("A referenced frontend bundle is missing. Build the frontend with the install command for this edition.")
    django_ready()
    check_migration_compatibility()
    from django.core.management import call_command
    call_command("check", verbosity=0)
    from django.db import connection, connections
    from django.db.migrations.executor import MigrationExecutor
    try:
        executor = MigrationExecutor(connection)
        pending = bool(executor.migration_plan(executor.loader.graph.leaf_nodes()))
    finally:
        connections.close_all()
    if pending:
        raise RuntimeError("Database migrations pending. Run ./lasttrain.sh install.")


def owned_process(state):
    import psutil
    try:
        process = psutil.Process(state["pid"])
        command = process.cmdline()
        if abs(process.create_time() - state["created"]) > .01:
            return None
        historical_source = next((arg for arg in command if arg.lower().endswith("launcher.py")), None)
        executable = Path(state.get("executable") or historical_source or process.exe()).resolve()
        if ((executable.suffix.lower() == ".py" and str(executable) not in command)
                or (executable.suffix.lower() != ".py" and Path(process.exe()).resolve() != executable)
                or state["instance"] not in command or "_serve" not in command):
            return None
        return process
    except (psutil.Error, KeyError, ValueError):
        return None


def unverified_live_process(state):
    """A reused or mismatched PID is not permission to use the same profile."""
    import psutil
    try:
        return bool(state and psutil.pid_exists(int(state["pid"])) and not owned_process(state))
    except (KeyError, TypeError, ValueError):
        return False


def read_state():
    try:
        return json.loads(STATE.read_text())
    except (OSError, ValueError):
        return None


def ready(state):
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(f'http://127.0.0.1:{state["port"]}/api/health/', timeout=1) as response:
            return json.load(response).get("instance") == state["instance"]
    except (OSError, ValueError, http.client.HTTPException):
        return False


def start(no_browser=False):
    state = read_state()
    existing = bool(state and owned_process(state))
    if not existing and unverified_live_process(state):
        raise RuntimeError("This profile points to a living but unverified process. No new server was started.")
    if existing:
        if not compatible_state(state):
            raise RuntimeError("Another Last Train build is running with this profile. Stop it using its matching launcher before starting this version.")
        if not ready(state):
            raise RuntimeError("Owned server exists but is not ready. Inspect data/server.log or run ./lasttrain.sh stop.")
    else:
        validate()
        # Reserve a candidate; Waitress handles the final bind. Readiness verifies identity.
        requested = int(os.environ.get("LASTTRAIN_PORT", "8765"))
        port = None
        for candidate in range(requested, min(requested + 30, 65536)):
            with socket.socket() as probe:
                try:
                    probe.bind(("127.0.0.1", candidate))
                    port = candidate
                    break
                except OSError:
                    continue
        if port is None:
            raise RuntimeError("No free local port. Set LASTTRAIN_PORT to another port.")
        token = uuid.uuid4().hex
        command = ([sys.executable] if getattr(sys, "frozen", False)
                   else [sys.executable, str(Path(__file__).resolve())])
        with (DATA / "server.log").open("a", encoding="utf-8") as log:
            options = {"cwd": ROOT, "stdin": subprocess.DEVNULL, "stdout": log, "stderr": log}
            process = subprocess.Popen([*command, "_serve", "--port", str(port), "--instance", token], **options)
        import psutil
        state = {"pid": process.pid, "created": psutil.Process(process.pid).create_time(), "port": port, "instance": token,
                 "executable": str(Path(sys.executable if getattr(sys, "frozen", False) else __file__).resolve()),
                 "build": build_identity()}
        STATE.write_text(json.dumps(state), encoding="utf-8")
        deadline = time.monotonic() + 30
        while not ready(state):
            if process.poll() is not None or time.monotonic() >= deadline:
                raise RuntimeError("Server did not become ready. Read data/server.log; run ./lasttrain.sh stop before retrying.")
            time.sleep(.2)
    url = f'http://127.0.0.1:{state["port"]}/'
    print("Last Train ready:", url)
    print("Data:", DATA)
    if not no_browser and (not existing or not os.environ.get("LASTTRAIN_PORTABLE")):
        if not webbrowser.open(url):
            print("Browser did not open automatically. Open the URL above manually.")
    return url


def stop():
    state = read_state()
    process = owned_process(state) if state else None
    if not process and unverified_live_process(state):
        raise RuntimeError("The recorded process is alive but its identity cannot be verified. Nothing was stopped or removed.")
    if process and not compatible_state(state):
        raise RuntimeError("This launcher belongs to a different build. Use that installation's launcher to stop it.")
    if process:
        request_shutdown(state, process)
        print("Stopped the owned Last Train server.")
    else:
        print("No owned Last Train server running; stale state ignored.")
    STATE.unlink(missing_ok=True)


def request_shutdown(state, process):
    """Signal only the verified owner and wait for its actual process exit."""
    (DATA / "stop.request").write_text(state["instance"], encoding="ascii")
    started = time.monotonic()
    try:
        process.wait(timeout=25)
    except Exception as exc:
        phase = "no shutdown status from the previous build"
        try:
            status = json.loads((DATA / "stop.status").read_text(encoding="utf-8"))
            if status.get("instance") == state["instance"]:
                phase = status.get("phase", phase)
        except (OSError, ValueError):
            pass
        # The request may already be in progress. Removing it here would not
        # cancel the old process and could mislead another launcher.
        raise RuntimeError(
            f"The owned Last Train process has not exited after {time.monotonic() - started:.1f}s "
            f"(shutdown phase: {phase}). The new version was not started."
        ) from exc


def serve_portable(application, port, instance):
    """Drain active work, then close every Waitress socket, including idle tabs."""
    from threading import Thread
    from waitress import create_server, wasyncore
    from django.db import connections

    server = create_server(application, host="127.0.0.1", port=port,
                           threads=4, max_request_body_size=101*1024*1024)
    worker = Thread(target=server.run, daemon=True)
    worker.start()
    request = DATA / "stop.request"
    status_path = DATA / "stop.status"
    started = time.monotonic()

    def phase(name):
        elapsed = time.monotonic() - started
        print(f"shutdown +{elapsed:.3f}s: {name}", flush=True)
        status_path.write_text(json.dumps({"instance": instance, "phase": name,
                                           "elapsed": round(elapsed, 3)}), encoding="utf-8")

    try:
        while worker.is_alive():
            if request.is_file() and request.read_text(encoding="ascii") == instance:
                phase("request received")
                break
            time.sleep(.2)
    finally:
        phase("closing listener")
        # BaseWSGIServer.close() also closes Waitress's wake-up trigger.
        # Active handlers still need that trigger to finish their responses.
        wasyncore.dispatcher.close(server)
        dispatcher = server.task_dispatcher
        deadline = time.monotonic() + 20
        while True:
            with dispatcher.lock:
                busy = bool(dispatcher.queue or dispatcher.active_count)
            if not busy:
                break
            if time.monotonic() >= deadline:
                phase("waiting for active request to finish safely")
                deadline = time.monotonic() + 20
            time.sleep(.1)
        phase("draining Waitress workers")
        dispatcher.shutdown(cancel_pending=False, timeout=20)
        with dispatcher.lock:
            while dispatcher.threads:
                phase("waiting for active request to finish")
                dispatcher.thread_exit_cv.wait(timeout=1)
        phase("closing HTTP channels")
        wasyncore.close_all(server._map)
        worker.join(timeout=5)
        if worker.is_alive():
            raise RuntimeError("Waitress event loop did not exit after its sockets closed")
        phase("closing SQLite connections")
        connections.close_all()
        request.unlink(missing_ok=True)
        phase("server cleanup complete")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["init", "start", "stop", "doctor", "backup", "restore", "_serve"])
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--port", type=int)
    parser.add_argument("--instance")
    parser.add_argument("--file")
    args = parser.parse_args()
    if args.command == "_serve":
        with lock("server.lock"):
            os.environ["LASTTRAIN_INSTANCE"] = args.instance
            from config.wsgi import application
            serve_portable(application, args.port, args.instance)
        return
    with lock("launcher.lock"):
        if args.command == "start":
            start(args.no_browser)
        elif args.command == "stop":
            stop()
        elif args.command == "backup":
            from local_data import create_backup
            print("Backup:", create_backup(DATA))
        elif args.command == "doctor":
            validate()
            print("Database, migrations and built assets OK. Data:", DATA)
        else:
            with lock("server.lock"):
                if args.command == "init":
                    initialize()
                else:
                    django_ready()
                    source = args.file or input("Full path to backup ZIP: ").strip().strip('"')
                    print("Restore replaces the current database. A safety backup will be kept.")
                    if input("Type RESTORE to confirm: ") != "RESTORE":
                        print("Restore cancelled.")
                        return
                    from local_data import restore_backup
                    print("Safety backup:", restore_backup(DATA, source))
                    initialize()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Last Train: {exc}", file=sys.stderr)
        sys.exit(1)
