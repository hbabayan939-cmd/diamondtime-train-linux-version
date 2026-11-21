# Linux installation and usage

This guide installs the Linux source edition of Last Train. It applies to this Linux-only fork; the original project is maintained in the [upstream repository](https://github.com/count-rzy/diamondtime-train).

## Requirements

- A supported Linux distribution with a graphical web browser.
- Python 3.12, 3.13 or 3.14.
- Node.js 22 or newer, with npm.
- Git, to clone the repository.
- Internet access during installation to download Python and npm packages.

Check the runtimes before installing:

```sh
python3 --version
node --version
npm --version
git --version
```

`python3 --version` must report 3.12–3.14; `node --version` must report v22 or newer. If your distribution provides an older Node.js, follow the installation instructions at [nodejs.org](https://nodejs.org/en/download/) for your distribution or use a maintained Node.js version manager. Restart the terminal after installing tools so its `PATH` is refreshed.

On Debian or Ubuntu, Python and Git can be installed with:

```sh
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git
```

Install Node.js 22+ using the official instructions for your Linux distribution. The distribution’s default package may be older than the version this project requires.

For Ubuntu or Debian, NodeSource provides Node.js 22 packages. Install `curl`, configure its Node.js 22 repository, install `nodejs`, then verify the version:

```sh
sudo apt install -y curl
curl -fsSL https://deb.nodesource.com/setup_22.x -o /tmp/nodesource_setup.sh
sudo -E bash /tmp/nodesource_setup.sh
sudo apt install -y nodejs
node --version
npm --version
```

The setup command should report `v22` or newer. See the [NodeSource distribution instructions](https://github.com/nodesource/distributions) for supported Linux versions and alternatives.

## Get the project

Clone this fork, then enter its directory:

```sh
git clone https://github.com/hbabayan939-cmd/diamondtime-train-linux-version.git
cd diamondtime-train-linux-version
```

If you downloaded a source archive instead, extract it and open a terminal in the extracted project directory.

## Install and build

Make the helper executable and install the application:

```sh
chmod +x lasttrain.sh
./lasttrain.sh install
```

The installer creates `back/.venv`, installs the Python requirements, installs the frontend packages under `front/node_modules`, builds the frontend, and initializes the local database. It does not require administrator privileges for project dependencies. It may ask for system packages if your Linux installation lacks Python’s `venv` support.

You can also run `./lasttrain.sh` with no argument; it performs the same install action. Re-running the install command builds the frontend again and preserves an existing profile.

## Start and stop the app

Start Last Train:

```sh
./lasttrain.sh start
```

The script prints the local URL and opens it in your default browser. If automatic browser opening is unavailable, copy the printed URL (normally `http://127.0.0.1:8765/`) into a browser on the same computer. The app tries nearby ports if the default port is occupied.

Stop the server when finished:

```sh
./lasttrain.sh stop
```

Closing the browser does not stop the server. The server listens only on the loopback interface and is intended for local use.

## Moving an existing profile

To transfer data from another computer or from the original Last Train project, first create a full ZIP backup using that installation's backup feature. Copy the ZIP to the Linux computer, stop Last Train if it is running, and restore it:

```sh
./lasttrain.sh stop
./lasttrain.sh restore --file /path/to/your-backup.zip
```

The restore command keeps a safety backup and asks you to type `RESTORE` before replacing the current profile. Never copy or replace the SQLite database while the app is running, and do not overwrite an existing profile unless you intend to replace it.

## Backups, restore and diagnostics

Create a ZIP backup:

```sh
./lasttrain.sh backup
```

Backups are stored under the profile’s `backups/` directory. Copy important backups somewhere outside the project directory as well.

Restore a backup while the app is stopped:

```sh
./lasttrain.sh restore --file /absolute/path/to/backup.zip
```

The restore process asks you to type `RESTORE`, creates a safety backup, then validates the archive and database before replacing the profile. Read the prompts carefully; restore replaces the current database. Do not manually copy a database over one that is in use.

Check the installation and built files:

```sh
./lasttrain.sh doctor
```

## Where data is stored

By default, user data is in the project’s `data/` directory:

- `lasttrain.sqlite3` — profile, journeys, diary, settings and related records.
- `user-files/` — imported audio managed by the application.
- `backups/` — ZIP backups.
- `server.log` — local application server output.
- `server.json` — state used by the start/stop helper.

To place the profile outside the checkout, set `LASTTRAIN_DATA_DIR` to an absolute directory. Use the same value for install, start, stop, backup and restore commands:

```sh
export LASTTRAIN_DATA_DIR="$HOME/.local/share/lasttrain"
./lasttrain.sh install
./lasttrain.sh start
```

Add the export to your shell profile if you want it set in every new terminal. If you omit it in a later session, Last Train will use the project’s `data/` folder instead.

## Updating the source checkout

Back up important data and stop the server before updating:

```sh
./lasttrain.sh backup
./lasttrain.sh stop
git pull
./lasttrain.sh install
```

The installer preserves the database and creates a pre-migration backup when initializing an existing profile. Keep independent copies of important data; an update is not a substitute for a backup.

## Troubleshooting

- **The installer says Python or Node is missing or too old:** install the required version, open a new terminal, and check `python3 --version` and `node --version` again.
- **Python reports that `venv` is unavailable:** install your distribution’s Python venv package (on Debian or Ubuntu, `sudo apt install python3-venv`).
- **The page does not open:** wait for the URL from the script, then open it manually in a browser on the same computer.
- **The server does not start:** inspect `data/server.log` (or `$LASTTRAIN_DATA_DIR/server.log` if using a custom profile), then run `./lasttrain.sh doctor`.
- **The default port is busy:** Last Train checks a range of nearby ports. Use the URL printed by the launcher.
- **You closed the browser and the app is still running:** use `./lasttrain.sh stop`.
- **A dependency install is interrupted:** rerun `./lasttrain.sh install` with internet access.

## Limitations

The primary workflow is a source-based Linux setup, not a single-file installer. The project directory must remain available because it contains the application source and frontend build. Installation uses Python and Node.js to prepare the app; normal use runs the local Python server and browser interface.

An optional Linux x86_64 onedir archive can be built from source with `./packaging/build.sh`. It bundles Python and application dependencies but still relies on compatible Linux system libraries and a browser. For a packaged build, extract the ZIP, open a terminal in the extracted folder, run `./LastTrain init` once, then use `./LastTrain start` and `./LastTrain stop`. See [packaging/README.txt](../packaging/README.txt) for details.
