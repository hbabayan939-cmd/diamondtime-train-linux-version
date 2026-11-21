# Linux onedir build: ./packaging/build.sh
from pathlib import Path
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

root = Path(SPECPATH).parent
sys.path.insert(0, str(root / "back"))
datas = [(str(root / "front" / "dist"), "front/dist")]
datas += collect_data_files("django")
datas += collect_data_files("rest_framework")
datas += collect_data_files("rest_framework_simplejwt",
                            includes=["token_blacklist/migrations/*.py"], include_py_files=True)
hiddenimports = (["launcher", "local_data"] + collect_submodules("config") + collect_submodules("journeys")
                 + collect_submodules("django.db.backends.sqlite3"))
for app in ("django.contrib.auth", "django.contrib.contenttypes", "django.contrib.sessions",
            "rest_framework", "rest_framework_simplejwt.token_blacklist"):
    hiddenimports += collect_submodules(app, filter=lambda name: ".tests" not in name)

a = Analysis(
    [str(root / "packaging" / "linux_launcher.py")],
    pathex=[str(root / "back")],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "pytest", "playwright", "django.contrib.gis",
              "django.contrib.postgres", "psycopg", "psycopg2"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="LastTrain",
          debug=False, bootloader_ignore_signals=False, strip=False, upx=False,
          console=True, disable_windowed_traceback=False)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False,
               name="LastTrain-Linux-x86_64")
