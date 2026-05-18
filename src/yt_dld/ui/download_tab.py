import os

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QFileDialog, QCheckBox, QLabel, QGroupBox, QMessageBox,
)
from PySide6.QtCore import Qt

from yt_dld.core.i18n import tr
from yt_dld.core.format_fetcher import FormatFetcher
from yt_dld.core.downloader import DownloadWorker
from yt_dld.ui.format_selector import FormatSelector
from yt_dld.ui.progress_widget import ProgressWidget


class DownloadTab(QWidget):
    def __init__(self, ffmpeg_path=None, parent=None):
        super().__init__(parent)
        self._ffmpeg_path = ffmpeg_path
        self._worker = None
        self._playlist_info = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel(tr("url_label")))
        self._url_input = QLineEdit()
        self._url_input.setPlaceholderText(tr("url_placeholder"))
        self._url_input.returnPressed.connect(self._on_fetch)
        url_layout.addWidget(self._url_input, 1)
        layout.addLayout(url_layout)

        btn_layout = QHBoxLayout()
        self._fetch_btn = QPushButton(tr("fetch_formats"))
        self._fetch_btn.clicked.connect(self._on_fetch)
        self._download_btn = QPushButton(tr("download"))
        self._download_btn.clicked.connect(self._on_download)
        self._download_btn.setEnabled(False)
        self._cancel_btn = QPushButton(tr("cancel"))
        self._cancel_btn.clicked.connect(self._on_cancel)
        self._cancel_btn.setEnabled(False)

        btn_layout.addWidget(self._fetch_btn)
        btn_layout.addWidget(self._download_btn)
        btn_layout.addWidget(self._cancel_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel(tr("output_path")))
        self._path_input = QLineEdit()
        self._path_input.setText(os.path.expanduser("~/Downloads"))
        path_layout.addWidget(self._path_input, 1)
        self._browse_btn = QPushButton(tr("browse"))
        self._browse_btn.clicked.connect(self._browse_path)
        path_layout.addWidget(self._browse_btn)
        layout.addLayout(path_layout)

        self._playlist_cb = QCheckBox(tr("playlist_subfolder"))
        self._playlist_cb.setVisible(False)
        layout.addWidget(self._playlist_cb)

        format_group = QGroupBox()
        format_group_layout = QVBoxLayout(format_group)
        self._format_selector = FormatSelector()
        format_group_layout.addWidget(self._format_selector)
        layout.addWidget(format_group, 1)

        self._progress_widget = ProgressWidget()
        layout.addWidget(self._progress_widget)

    def _browse_path(self):
        path = QFileDialog.getExistingDirectory(self, tr("output_path"), self._path_input.text())
        if path:
            self._path_input.setText(path)

    def _on_fetch(self):
        url = self._url_input.text().strip()
        if not url:
            QMessageBox.warning(self, tr("fetch_error_title"), tr("error_no_url"))
            return

        self._fetch_btn.setEnabled(False)
        self._download_btn.setEnabled(False)
        self._format_selector.clear()
        self._playlist_info = None
        self._playlist_cb.setVisible(False)

        try:
            info = FormatFetcher.fetch(url)
        except Exception as e:
            QMessageBox.critical(self, tr("fetch_error_title"), f"{tr('error_fetch')}: {e}")
            self._fetch_btn.setEnabled(True)
            return

        if info["type"] == "playlist":
            self._playlist_info = info
            self._playlist_cb.setVisible(info["count"] > 0)
            self._download_btn.setEnabled(info["count"] > 0)
            self._progress_widget._append_log(f"[▶] {tr('playlist_title')}: {info['title']} ({info.get('count', 0)} videos)")
        else:
            self._format_selector.load_formats(info)
            if self._format_selector.has_formats():
                self._download_btn.setEnabled(True)
            else:
                QMessageBox.information(self, tr("fetch_error_title"), tr("format_not_found"))

        self._fetch_btn.setEnabled(True)

    def _on_download(self):
        url = self._url_input.text().strip()
        output_path = self._path_input.text().strip()
        if not url:
            QMessageBox.warning(self, tr("fetch_error_title"), tr("error_no_url"))
            return
        if not output_path:
            output_path = os.path.expanduser("~/Downloads")
            self._path_input.setText(output_path)

        format_id = self._format_selector.selected_format_id()
        use_subfolder = self._playlist_cb.isChecked() if self._playlist_info else False

        self._worker = DownloadWorker(
            url=url,
            output_path=output_path,
            format_id=format_id,
            playlist_subfolder=use_subfolder,
            ffmpeg_path=self._ffmpeg_path,
        )
        self._worker.progress.connect(self._progress_widget.update_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)

        self._progress_widget.reset()
        self._fetch_btn.setEnabled(False)
        self._download_btn.setEnabled(False)
        self._cancel_btn.setEnabled(True)
        self._worker.start()

    def _on_cancel(self):
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self._worker.quit()
            self._worker.wait(3000)
            self._progress_widget._append_log("[✕] Cancelled")
        self._reset_buttons()

    def _on_finished(self, url, path):
        self._progress_widget._append_log(f"[✓] {tr('status_done')}: {path}")
        self._reset_buttons()

    def _on_error(self, message):
        self._progress_widget._append_log(f"[✕] {message}")
        QMessageBox.critical(self, tr("fetch_error_title"), f"{tr('error_download')}: {message}")
        self._reset_buttons()

    def _reset_buttons(self):
        self._fetch_btn.setEnabled(True)
        self._download_btn.setEnabled(True)
        self._cancel_btn.setEnabled(False)
