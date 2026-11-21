LAST TRAIN - LINUX x86_64 PORTABLE BUILD

This archive contains the Last Train runtime for Linux x86_64.

1. Extract the complete archive to a folder you can access.
2. Keep the LastTrain executable and _internal directory together.
3. Open a terminal in the extracted LastTrain-Linux-x86_64 folder.
4. Initialize the profile once: ./LastTrain init
5. Start the app: ./LastTrain start
6. Open the local URL printed by the command if your browser does not open.
7. When finished, run: ./LastTrain stop

The target computer does not need Python or Node.js. A web browser is required.
The app listens only on 127.0.0.1. Closing the browser does not stop the server.

User data is stored in XDG_DATA_HOME/LastTrain/data (by default,
~/.local/share/LastTrain/data) and is kept separately from this program folder.
It can also be relocated by setting
LASTTRAIN_DATA_DIR to an absolute path before running the executable. Backups
are created in the data/backups directory. Keep additional backup copies in a
separate safe location.

The archive is built for Linux x86_64. PyInstaller bundles the Python runtime
and application dependencies, but Linux system libraries such as glibc remain
provided by the operating system. Build on a distribution compatible with the
oldest Linux version you intend to support, and verify the archive on the
target distribution.

To create or restore a backup, or to check the profile, use:

  ./LastTrain backup
  ./LastTrain restore --file /path/to/backup.zip
  ./LastTrain doctor

Restore asks you to type RESTORE and makes a safety backup first. Do not replace
the database while Last Train is running.

Original project created by COUnT (count-rzy). Special thanks to Sonya (Ryuko)
for her contributions and programming mentorship. This Linux fork is based on
the original project: https://github.com/count-rzy/diamondtime-train
