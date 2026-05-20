import yt_dlp

from PySide6.QtWidgets import QMainWindow, QMessageBox, QStatusBar
from PySide6.QtGui import QAction

from yt_dld.core.i18n import tr
from yt_dld.ui.download_tab import DownloadTab
from yt_dld.ui.settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    def __init__(self, ffmpeg_path=None, auth_opts=None):
        super().__init__()
        self._ffmpeg_path = ffmpeg_path
        self._auth_opts = auth_opts or {}
        self.setWindowTitle(tr("app_title"))
        self.resize(800, 700)
        self._setup_menu()
        self._setup_ui()
        self._setup_status()

    def _setup_ui(self):
        self._download_tab = DownloadTab(ffmpeg_path=self._ffmpeg_path, auth_opts=self._auth_opts)
        self.setCentralWidget(self._download_tab)

    def _setup_status(self):
        self._status = QStatusBar()
        self._status.showMessage(f"{tr('status_ready')}  |  yt-dlp {yt_dlp.version.__version__}")
        self.setStatusBar(self._status)

    def _show_about(self):
        QMessageBox.about(self, tr("menu_about"), tr("about_text"))

    def show_settings(self):
        dlg = SettingsDialog(self)
        dlg.exec()
