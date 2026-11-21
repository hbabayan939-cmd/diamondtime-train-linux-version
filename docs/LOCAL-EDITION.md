# Architecture and development notes

This document describes the local application used by the Linux source fork. For installation and everyday commands, see [Linux installation and usage](LINUX-INSTALLATION.md).

## What runs locally

The production interface is built with React and Vite. Django serves the built frontend, artwork, managed audio and the `/api/` endpoints. Waitress serves Django on `127.0.0.1`; SQLite stores the profile. The browser connects only to the local server during normal use. Vite is used to build the frontend and run development tools.

The source helper, `lasttrain.sh`, creates `back/.venv`, installs backend and frontend dependencies, builds the frontend and initializes the profile. It also delegates start, stop, backup, restore and doctor operations to `back/launcher.py`. An optional PyInstaller onedir build is available through `packaging/build.sh`; the packaged executable uses an XDG data directory by default.

## Local profile and migration behavior

The Django User table and existing migrations are retained for database compatibility. `LocalContext` selects a local owner; no password or cloud account is required. A new profile creates one traveler. Existing users, journeys, diary entries and settings keep their IDs and foreign keys. If an existing database has multiple user profiles, Settings offers **Stored profiles** with record counts. Switching profiles does not merge or delete records.

The default profile directory is the project’s `data/`; `LASTTRAIN_DATA_DIR` can point to another absolute path. On first initialization, if the profile database is missing or empty and the old `back/db.sqlite3` exists, the launcher snapshots it through SQLite's backup API and retains the source file. It does not replace a populated target database. Initialization creates a pre-migration ZIP before applying migrations to an existing profile.

If an older database contains multiple unfinished journeys for the same user, initialization stops and reports the conflict rather than deleting records. Resolve the conflict with a compatible earlier application before retrying. Already-applied migrations are not replayed.

To move a profile between computers or from the original project, create a backup through the app or its backup command, then restore the ZIP on the Linux installation. Avoid copying a live SQLite database or combining databases manually.

## Journey time behavior

UTC timestamps are authoritative. Time continues to pass while the browser is closed, the local process is stopped or the computer sleeps. Paused time does not count. When the app next reads an overdue journey, it reconciles completion to the scheduled arrival time. The browser interpolates snapshots using a monotonic clock and refreshes them periodically and when the page becomes visible. Changing the computer clock can affect arrival timing; there is no external time server.

## Local security model

The server binds to loopback only. Host validation, loopback address validation, same-origin checks and Fetch Metadata checks reject external origins. Django REST Framework enforces CSRF on writes, including the anonymous local workflow. The frontend requests a token from `/api/auth/csrf/`. The app does not enable wildcard CORS. Content Security Policy disallows external scripts, fonts, media and connections. API responses are not cached.

Audio uploads are limited to 100 MB and checked for WAV, MP3, Ogg or FLAC signatures. Files receive managed random names; the browser does not supply filesystem paths. Audio supports byte-range seeking. Ambient train sound is generated locally; third-party songs are not bundled.

This is a personal local application, not a security boundary between Linux user accounts. Anyone who can access the profile files can access that profile's data.

## Fonts, language and audio

DM Sans, Noto Sans (including Cyrillic) and Press Start 2P are bundled from Fontsource packages by Vite. Their SIL Open Font License notices are in `docs/licenses/`; runtime font requests do not go to Google Fonts.

English and Russian translations are maintained in `front/src/locales/` and related source files. SQLite stores the selected language; localStorage caches it for startup. Migrations add language and audio preferences without changing journey or diary content.

`TrainAudioEngine` manages a lazily created Web Audio context, shared noise buffer, scheduled voices and master compressor. The radio uses its own context and bundled tracks. Sound changes with journey state. Browser autoplay restrictions mean audio may require an initial user interaction.

## Process and data safety

Linux `flock` locks serialize launcher operations and prevent two servers from using the same profile concurrently. The server state records the PID, process creation time, launcher path and a random instance token. Readiness checks verify that token. Stop verifies the process identity before requesting graceful shutdown; stale state alone never authorizes terminating an unrelated process. Port conflicts are tried across a 30-port range beginning at 8765.

Backups use SQLite's online backup API and include managed audio referenced by the snapshot. Restore is performed while the app is stopped, requires typing `RESTORE`, validates the ZIP members, size limits, database integrity, foreign keys, migrations and audio, then creates a safety backup before replacement. Backup ZIPs and exported data contain personal information; store them privately.

## Development and checks

Install the project first with `./lasttrain.sh install`. The following checks are run from the repository root unless a directory is noted.

Backend tests and migration checks:

```sh
back/.venv/bin/python back/manage.py test journeys
back/.venv/bin/python back/manage.py makemigrations --check --dry-run
back/.venv/bin/python -m pip check
back/.venv/bin/python scripts/test_shutdown.py
```

Frontend tests and build:

```sh
cd front
npm test
npm run build
npx prettier --check src index.html vite.config.js
```

Browser scenarios use Playwright and the Chrome channel configured in `front/playwright.config.js`. They create disposable profiles, block external browser requests and write artifacts beneath `.local-qa/`. `node scripts/audio-soak.mjs` (from `front/`) exercises sustained audio behavior.

The optional package build uses pinned dependencies from `packaging/requirements-build.txt` in an isolated `packaging/.venv`, and writes `dist/LastTrain-Linux-x86_64.zip`. The Linux source setup currently has no dedicated automated clean-machine installer or launcher integration test. Linux socket-based checks require permission to bind local loopback sockets.

Useful manual checks include a clean Linux installation, non-ASCII project path, suspend/resume, long-running journeys, physical audio output and playback of the user's own supported audio files.
