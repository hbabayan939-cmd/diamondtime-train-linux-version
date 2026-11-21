# Changelog

This file records the Linux fork's platform direction alongside history inherited from the original Last Train project. Historical upstream milestones are not Linux fork releases. See the [Linux installation guide](docs/LINUX-INSTALLATION.md) for supported use of this fork.

## Linux fork — source edition

- Set the fork's target platform to Linux.
- Added `lasttrain.sh` as the single Linux command entry point for installation, start, stop, backup, restore and diagnostics.
- Added an optional Linux x86_64 PyInstaller onedir build and ZIP packager.
- Added Linux setup and usage documentation, and documented the original project lineage and contributor credits.
- Added Linux process locking and launcher startup support while retaining the original application architecture.

## Upstream history

### v0.1.0-exp.1 — Last Train v0.1 EXP

The original project published its first experimental packaged edition.

- Added Settings actions for full profile backups and journey/diary exports.
- Improved portable startup, shutdown and instance handoff, including graceful Waitress shutdown that drains active connections.
- Improved compartment layout recovery after leaving fullscreen.
- Documented portable storage, backup-first migration and the original packaged edition.

### v0.3 — Interface and packaged edition stabilization

- Added an onedir packaging workflow and portable launch/stop support to the original project.
- Improved compartment and scenery presentation, fullscreen recovery, production favicon serving and portable process reliability.

### v0.2 — Feature expansion and railway experience

- Added scheduled station breaks, persistent railway routes and an interactive Railway Atlas.
- Added the animated railway scene, scenery events, an immersive carriage and in-scene notebook.
- Improved journey transitions, audio activation, train ambience, diary search and browser lifecycle behavior.

### v0.1 — Initial foundation

- Established the offline local application with a Django API, React/Vite interface and SQLite storage.
- Added Russian and English interface support, journey and diary workflows, and local setup.
- Added locally generated train ambience and checks for setup and sustained audio behavior.
