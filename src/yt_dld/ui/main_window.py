import yt_dlp

from PySide6.QtWidgets import QMainWindow, QMessageBox, QStatusBar
from PySide6.QtGui import QAction

from yt_dld.core.i18n import tr
from yt_dld.ui.download_tab import DownloadTab
from yt_dld.ui.settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    def __init__(self, ffmpeg_path=None):
        super().__init__()
        self._ffmpeg_path = ffmpeg_path
        self.setWindowTitle(tr("app_title"))
        self.resize(800, 700)
        self._setup_menu()
        self._setup_ui()
        self._setup_status()

    def _setup_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu(tr("menu_file"))
        settings_action = QAction(tr("settings_tab"), self)
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        file_menu.addSeparator()
        exit_action = QAction(tr("menu_exit"), self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = menubar.addMenu(tr("menu_help"))
        about_action = QAction(tr("menu_about"), self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_ui(self):
        self._download_tab = DownloadTab(ffmpeg_path=self._ffmpeg_path)
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
