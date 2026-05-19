import os

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QFileDialog, QCheckBox, QLabel, QGroupBox, QMessageBox, QStackedWidget,
)
from PySide6.QtCore import Qt

from yt_dld.core.i18n import tr
from yt_dld.core.format_fetcher import FormatFetcher
from yt_dld.core.downloader import DownloadWorker
from yt_dld.ui.format_selector import FormatSelector
from yt_dld.ui.playlist_selector import PlaylistSelector
from yt_dld.ui.progress_widget import ProgressWidget
from yt_dld.ui.error_dialog import ErrorDialog


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
        self._cancel_btn = QPushButton(tr("cancel"))
        self._cancel_btn.clicked.connect(self._on_cancel)
        self._cancel_btn.setEnabled(False)

        btn_layout.addWidget(self._fetch_btn)
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

        self._selector_stack = QStackedWidget()

        self._format_selector = FormatSelector()
        self._selector_stack.addWidget(self._format_selector)

        self._playlist_selector = PlaylistSelector()
        self._selector_stack.addWidget(self._playlist_selector)

        layout.addWidget(self._selector_stack, 1)

        self._download_btn = QPushButton(tr("download"))
        self._download_btn.clicked.connect(self._on_download)
        layout.addWidget(self._download_btn)

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
        self._format_selector.clear()
        self._playlist_selector.clear()
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
            self._playlist_selector.load_entries(info["entries"])
            self._selector_stack.setCurrentWidget(self._playlist_selector)
            self._playlist_cb.setVisible(info.get("available_count", 0) > 0)
            self._progress_widget._append_log(
                f"[▶] {tr('playlist_title')}: {info['title']} "
                f"({info.get('available_count', 0)} {tr('available_count').lower()}, "
                f"{info.get('unavailable_count', 0)} {tr('unavailable_count').lower()})"
            )
        else:
            self._format_selector.load_formats(info)
            self._selector_stack.setCurrentWidget(self._format_selector)
            if not self._format_selector.has_formats():
                QMessageBox.information(self, tr("fetch_error_title"), tr("format_not_found"))

        self._fetch_btn.setEnabled(True)

    def _on_download(self):
        try:
            self._do_download()
        except Exception as e:
            QMessageBox.critical(self, tr("fetch_error_title"), f"{tr('error_download')}: {e}")
            self._progress_widget._append_log(f"[✕] {e}")
            self._reset_buttons()

    def _do_download(self):
        url = self._url_input.text().strip()
        output_path = self._path_input.text().strip()
        if not url:
            QMessageBox.warning(self, tr("fetch_error_title"), tr("error_no_url"))
            return
        if not self._playlist_info and not self._format_selector.has_formats():
            QMessageBox.information(self, tr("fetch_error_title"), tr("fetch_first"))
            return
        if not output_path:
            output_path = os.path.expanduser("~/Downloads")
            self._path_input.setText(output_path)

        is_playlist = self._selector_stack.currentWidget() is self._playlist_selector
        use_subfolder = self._playlist_cb.isChecked() and self._playlist_info

        if is_playlist:
            selected_urls = self._playlist_selector.selected_urls()
            if not selected_urls:
                QMessageBox.warning(self, tr("fetch_error_title"), tr("no_videos_selected"))
                return
            selected_urls_for_download = selected_urls
        else:
            selected_urls_for_download = None

        format_id = self._format_selector.selected_format_id()

        self._worker = DownloadWorker(
            url=url,
            output_path=output_path,
            format_id=format_id,
            playlist_subfolder=use_subfolder,
            ffmpeg_path=self._ffmpeg_path,
            selected_urls=selected_urls_for_download,
        )
        self._worker.progress.connect(self._progress_widget.update_progress)
        self._worker.item_error.connect(self._on_item_error)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)

        self._progress_widget.reset()
        self._fetch_btn.setEnabled(False)
        self._cancel_btn.setEnabled(True)
        self._worker.start()

    def _on_item_error(self, err):
        self._progress_widget._append_log(f"[✕] {err.get('title', '')}: {err.get('error', '')}")

    def _on_cancel(self):
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self._worker.quit()
            self._worker.wait(3000)
            self._progress_widget._append_log("[✕] Cancelled")
        self._reset_buttons()

    def _on_finished(self, url, path, errors=None):
        if errors:
            total = self._playlist_selector.selected_count() if self._playlist_info else 0
            if not total:
                total = len(errors)
            self._progress_widget._append_log(
                f"[⚠] {tr('playlist_skip_unavailable') % len(errors)}"
            )
            dlg = ErrorDialog(errors, total, self)
            dlg.exec()

        self._progress_widget._append_log(f"[✓] {tr('status_done')}: {path}")
        self._reset_buttons()

    def _on_error(self, message):
        self._progress_widget._append_log(f"[✕] {message}")
        QMessageBox.critical(self, tr("fetch_error_title"), f"{tr('error_download')}: {message}")
        self._reset_buttons()

    def _reset_buttons(self):
        self._fetch_btn.setEnabled(True)
        self._cancel_btn.setEnabled(False)
