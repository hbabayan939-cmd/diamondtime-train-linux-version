"""Linux entry point for the optional PyInstaller onedir build."""
import os
import sys
from pathlib import Path


def main():
    data_root = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    if not data_root.is_absolute():
        raise RuntimeError("XDG_DATA_HOME must be an absolute path.")
    default_data = data_root / "LastTrain" / "data"
    configured_data = Path(os.environ.get("LASTTRAIN_DATA_DIR", default_data))
    if not configured_data.is_absolute():
        raise RuntimeError("LASTTRAIN_DATA_DIR must be an absolute path.")
    configured_data.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("LASTTRAIN_DATA_DIR", str(configured_data.resolve()))

    bundle_root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    sys.path.insert(0, str(bundle_root / "back"))
    from launcher import main as launcher_main
    launcher_main()


if __name__ == "__main__":
    main()
