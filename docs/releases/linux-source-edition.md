# Linux source edition

This document describes how to install and run the Linux source edition of the Last Train fork. It is an installation guide, not a claim that a packaged Linux release has been published.

## About this edition

The Linux fork adapts the original Last Train project for Linux computers. It keeps the React and Django application and provides `lasttrain.sh` for dependency setup, frontend builds, local launch and shutdown, backups, restore and diagnostics.

## Install

Use Python 3.12–3.14, Node.js 22 or newer, npm and Git. Clone this fork, enter the project folder and install:

```sh
git clone https://github.com/hbabayan939-cmd/diamondtime-train-linux-version.git
cd diamondtime-train-linux-version
chmod +x lasttrain.sh
./lasttrain.sh install
```

For full prerequisite, data-location, backup and troubleshooting instructions, see the [Linux installation guide](../LINUX-INSTALLATION.md).

## Run

```sh
./lasttrain.sh start
```

Open the local URL printed by the command if the browser does not launch. Stop the server with `./lasttrain.sh stop`; closing the browser tab alone leaves it running.

## Data and limitations

The profile is kept in `data/` in the checkout by default. Set `LASTTRAIN_DATA_DIR` to use a different location. Back up personal data before updates. This edition runs from source and requires the project files; it is not currently distributed as a standalone Linux binary or one-file installer.
