import os
import sys
import platform
import shutil


def _get_bundled_dir():
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def _platform_dir():
    system = platform.system().lower()
    if system == "darwin":
        return "ffmpeg-macos"
    elif system == "windows":
        return "ffmpeg-windows"
    else:
        return "ffmpeg-linux"


def find_ffmpeg():
    bundled = os.path.join(_get_bundled_dir(), "bin", _platform_dir())
    ffmpeg_path = os.path.join(bundled, "ffmpeg")
    ffprobe_path = os.path.join(bundled, "ffprobe")

    if platform.system() == "Windows":
        ffmpeg_path += ".exe"
        ffprobe_path += ".exe"

    if not os.path.isfile(ffmpeg_path):
        system_ffmpeg = shutil.which("ffmpeg")
        system_ffprobe = shutil.which("ffprobe")
        if system_ffmpeg and system_ffprobe:
            return system_ffmpeg, system_ffprobe
        return None, None

    return ffmpeg_path, ffprobe_path
