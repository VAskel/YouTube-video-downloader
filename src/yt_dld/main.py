import sys
import os

from PySide6.QtWidgets import QApplication

from yt_dld.core.ffmpeg_manager import find_ffmpeg
from yt_dld.core.i18n import tr, set_language
from yt_dld.ui.main_window import MainWindow
from yt_dld.ui.settings_dialog import load_settings


def main():
    settings = load_settings()
    lang = settings.get("language")
    if lang:
        set_language(lang)

    app = QApplication(sys.argv)
    app.setApplicationName("yt-dld")

    ffmpeg_path, ffprobe_path = find_ffmpeg()

    ffmpeg_override = settings.get("ffmpeg_path", "")
    if ffmpeg_override and os.path.isfile(ffmpeg_override):
        ffmpeg_path = ffmpeg_override

    window = MainWindow(ffmpeg_path=ffmpeg_path)
    window.show()

    return app.exec()
