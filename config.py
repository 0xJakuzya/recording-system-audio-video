import os
import sys
from datetime import datetime

SAMPLE_RATE = 44100
CHANNELS = 1

# When bundled with PyInstaller, use the directory of the exe.
# When running as a script, use the directory of this file.
if getattr(sys, "frozen", False):
    _BASE_DIR = os.path.dirname(sys.executable)
else:
    _BASE_DIR = os.path.dirname(os.path.abspath(__file__))

OUTPUT_DIR = os.path.join(_BASE_DIR, "data")


def next_session_dir() -> tuple[str, str]:
    """
    Create and return (session_dir_path, date_prefix).
    Folder name: session_N_YYYYMMDD_HHMMSS
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    n = 1
    while True:
        name = f"session_{n}_{date_str}"
        path = os.path.join(OUTPUT_DIR, name)
        if not os.path.exists(path):
            os.makedirs(path)
            return path, date_str
        n += 1

COLORS = {
    "BG":     "#0d0d0f",
    "PANEL":  "#131316",
    "ACCENT": "#e63946",
    "DIM":    "#2a2a30",
    "TEXT":   "#e8e8ec",
    "MUTED":  "#555560",
}
