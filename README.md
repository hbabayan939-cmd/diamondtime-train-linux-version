<div align="center">

# LAST TRAIN — LINUX FORK

### A quieter way to make time feel like a journey.

**In the end… it matters how far the train has traveled.**

This is a Linux-only fork of [Last Train](https://github.com/count-rzy/diamondtime-train), an offline-first focus and reflection app created by **COUNT (count-rzy)**.

[![Linux](https://img.shields.io/badge/platform-Linux-355a4d?style=flat-square)](#linux-installation)
![Local first](https://img.shields.io/badge/data-local--first-355a4d?style=flat-square)
![React](https://img.shields.io/badge/interface-React-263a55?style=flat-square)

<br>

[Install on Linux](#linux-installation) · [What the project does](#what-is-last-train) · [Credits](#credits)

</div>

## What is Last Train?

Last Train turns focused work into a railway journey. Choose a route and duration, and the train moves while you work. Planned breaks become station stops, and finishing a session brings the train to its destination. A pixel-art carriage and changing scenery make time visible, while a diary gives you a place to keep notes about the journey.

The app is designed for personal use on one computer. Its web interface is served locally and its profile is stored on your computer. It does not need a cloud account or an internet connection after installation.

## A look inside

<div align="center">

<img src="docs/media/readme/carriage.png" alt="Last Train's carriage, journey timer and railway scenery" width="100%">

*The carriage: set out, watch the landscape change, and arrive when your session is complete.*

<table>
<tr>
<td width="50%" align="center"><img src="docs/media/readme/railway-atlas.png" alt="Interactive Railway Atlas" width="100%"><br><sub>Follow the route in the Railway Atlas</sub></td>
<td width="50%" align="center"><img src="docs/media/readme/diary.png" alt="Travel diary" width="100%"><br><sub>Keep a travel diary</sub></td>
</tr>
<tr>
<td colspan="2" align="center"><br><img src="docs/media/readme/radio.png" alt="Cabin radio and audio controls" width="72%"><br><sub>Settle in with the cabin radio and train ambience</sub></td>
</tr>
</table>

</div>

## What you can do

- Plan focus sessions with rest stops and review completed journeys.
- Watch the carriage, railway scenery, weather and station events change as a journey progresses.
- Explore the Railway Atlas and view journey statistics.
- Write and search diary entries.
- Listen to the built-in radio, import supported local audio, and adjust generated train ambience.
- Choose English or Russian and adjust display, motion, weather and sound preferences.
- Create a backup ZIP or export journey and diary data from Settings.

## Linux installation

This fork is intended for Linux computers. It currently runs from the project source through the included `lasttrain.sh` script; it is not a prebuilt desktop package. Follow the full [Linux installation and usage guide](docs/LINUX-INSTALLATION.md).

You need Python 3.12–3.14, Node.js 22 or newer, npm, and Git. After installing those prerequisites and cloning this repository, run these commands from the project directory:

```sh
chmod +x lasttrain.sh
./lasttrain.sh install
./lasttrain.sh desktop-install
./lasttrain.sh start
```

Installation downloads Python and JavaScript dependencies and builds the browser interface, so it needs internet access. `desktop-install` adds a Last Train icon to your applications menu. After that, launch it with one click; the app opens at a local address in your web browser. Starting the app later does not need internet access. Stop the background server with:

```sh
./lasttrain.sh stop
```

The same script provides additional commands:

```sh
./lasttrain.sh backup
./lasttrain.sh restore
./lasttrain.sh doctor
./lasttrain.sh desktop-remove
```

`desktop-remove` removes the menu shortcut only. It keeps the project and your profile. If you move the project folder, run `./lasttrain.sh desktop-install` again so the shortcut points to its new location.

## Optional Linux package build

To create an onedir archive for Linux x86_64, install the project requirements and build tools, then run:

```sh
./packaging/build.sh
```

The archive is written to `dist/LastTrain-Linux-x86_64.zip`. It includes the Python runtime and app dependencies, so the target computer does not need Node.js or Python. A browser and compatible Linux system libraries are still required. See [packaging/README.txt](packaging/README.txt) for archive usage and compatibility notes. The source install through `lasttrain.sh` remains the recommended development and setup path.

## Your data

By default, the SQLite database, backups and imported audio are stored in the project’s `data/` directory. Keep that directory safe and include it in your own backup routine. To store the profile elsewhere, set `LASTTRAIN_DATA_DIR` to the same absolute path whenever you use `lasttrain.sh`, for example:

```sh
LASTTRAIN_DATA_DIR="$HOME/.local/share/lasttrain" ./lasttrain.sh install
LASTTRAIN_DATA_DIR="$HOME/.local/share/lasttrain" ./lasttrain.sh start
```

The application binds to `127.0.0.1`, so it is intended to be used from the same computer. Closing the browser tab does not stop the local server; run `./lasttrain.sh stop` when you are finished.

## Project documentation

- [Linux installation, operation and troubleshooting](docs/LINUX-INSTALLATION.md)
- [Architecture, local data and development checks](docs/LOCAL-EDITION.md)
- [Project history and changes](CHANGELOG.md)
- [Credits and project lineage](docs/PROJECT-CREDITS.md)
- [Linux source-edition notes](docs/releases/linux-source-edition.md)
- [Pixel-art direction and asset workflow](front/art/ART_DIRECTION.md)

## Technology

The interface uses React, JavaScript and Vite. The local API and server use Django, Django REST Framework and Waitress. SQLite stores the profile. The Vite build bundles the interface, artwork and fonts for local serving.

## Credits

Last Train was created by **COUNT (count-rzy)**. This Linux fork builds on the original project and preserves its design, features and history.

## From original README.md

**Special thanks to Sonya (Ryuko)** for her contributions, guidance and programming mentorship, and for supporting the creator’s growth as a developer.

See [project credits and lineage](docs/PROJECT-CREDITS.md) and the [original repository](https://github.com/count-rzy/diamondtime-train).

<div align="center">

---

*In the end… it matters how far the train has traveled.*

</div>
