"""Archive only the finished onedir distribution, never local data."""
import os
import sys
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parent.parent
folder = root / "dist" / "LastTrain-Linux-x86_64"
target = root / "dist" / "LastTrain-Linux-x86_64.zip"
temporary = target.with_suffix(".zip.tmp")
if not (folder / "LastTrain").is_file() or not (folder / "_internal" / "front" / "dist" / "index.html").is_file():
    sys.exit("Portable distribution is incomplete.")
try:
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6,
                         allowZip64=True) as archive:
        for path in sorted(folder.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(folder.parent))
    os.replace(temporary, target)
except BaseException:
    temporary.unlink(missing_ok=True)
    raise
print(target)
