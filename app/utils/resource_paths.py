import os
import sys


def get_base_path():
    if hasattr(sys, "_MEIPASS"):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_assets_dir():
    base = get_base_path()
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(base, "app", "assets")
    return os.path.join(base, "assets")
