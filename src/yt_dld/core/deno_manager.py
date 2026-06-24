import os
import platform
import shutil
import sys


def _get_bundled_dir():
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def _platform_dir():
    system = platform.system().lower()
    if system == "darwin":
        return "deno-macos"
    elif system == "windows":
        return "deno-windows"
    else:
        return "deno-linux"


def find_deno():
    bundled = os.path.join(_get_bundled_dir(), "bin", _platform_dir())
    deno_path = os.path.join(bundled, "deno")

    if platform.system() == "Windows":
        deno_path += ".exe"

    if os.path.isfile(deno_path):
        return deno_path

    return shutil.which("deno")
