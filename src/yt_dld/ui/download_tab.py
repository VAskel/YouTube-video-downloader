import os

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QFileDialog, QCheckBox, QLabel, QGroupBox, QMessageBox, QStackedWidget,
    QListWidget, QListWidgetItem,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QBrush, QColor

from yt_dld.core.i18n import tr
from yt_dld.core.download_queue import DownloadQueue, DownloadQueueTask, TaskStatus
from yt_dld.core.format_fetcher import FormatFetcher
from yt_dld.core.downloader import DownloadWorker
from yt_dld.ui.format_selector import FormatSelector
from yt_dld.ui.playlist_selector import PlaylistSelector
from yt_dld.ui.progress_widget import ProgressWidget
from yt_dld.ui.error_dialog import ErrorDialog
from yt_dld.ui.settings_dialog import load_settings, get_auth_opts


class DownloadTab(QWidget):
    queue_changed = Signal(int)

    def __init__(self, ffmpeg_path=None, deno_path=None, auth_opts=None, parent=None):
        super().__init__(parent)
        self._ffmpeg_path = ffmpeg_path
        self._deno_path = deno_path
        self._auth_opts = auth_opts or {}
        self._worker = None
        self._playlist_info = None
        self._queue = DownloadQueue()
        self._current_task = None
        self._queue_busy = False
        self._error_dialogs = []
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
        self._stop_btn = QPushButton(tr("stop"))
        self._stop_btn.clicked.connect(self._on_stop)
        self._stop_btn.setEnabled(False)
        self._stop_btn.setStyleSheet("color: #D32F2F;")

        btn_layout.addWidget(self._fetch_btn)
        btn_layout.addWidget(self._cancel_btn)
        btn_layout.addWidget(self._stop_btn)
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

        self._download_btn = QPushButton(tr("add_to_queue"))
        self._download_btn.clicked.connect(self._on_download)
        layout.addWidget(self._download_btn)

        self._queue_group = QGroupBox(tr("queue_title"))
        queue_layout = QVBoxLayout(self._queue_group)
        self._queue_list = QListWidget()
        self._queue_list.setMaximumHeight(100)
        self._queue_list.setAlternatingRowColors(True)
        queue_layout.addWidget(self._queue_list)
        queue_btn_layout = QHBoxLayout()
        self._clear_queue_btn = QPushButton(tr("queue_clear"))
        self._clear_queue_btn.clicked.connect(self._clear_queue)
        queue_btn_layout.addStretch()
        queue_btn_layout.addWidget(self._clear_queue_btn)
        queue_layout.addLayout(queue_btn_layout)
        self._queue_group.setVisible(False)
        layout.addWidget(self._queue_group)

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
            info = FormatFetcher.fetch(url, auth_opts=self._auth_opts)
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

    def _do_download(self):
        url = self._url_input.text().strip()
        output_path = self._path_input.text().strip()
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
            per_video_settings = self._playlist_selector.get_settings()
        else:
            if not url:
                QMessageBox.warning(self, tr("fetch_error_title"), tr("error_no_url"))
                return
            selected_urls = [url]
            per_video_settings = None
            use_subfolder = False

        format_id = self._format_selector.selected_format_id()
        playlist_title = self._playlist_info.get("title") if self._playlist_info else None

        task = DownloadQueueTask(
            url=url,
            output_path=output_path,
            selected_urls=selected_urls,
            per_video_settings=per_video_settings or {},
            format_id=format_id,
            playlist_subfolder=use_subfolder,
            playlist_title=playlist_title,
        )

        task_index = self._queue.add(task)
        self._add_to_queue_list(task, task_index)
        self._queue_group.setVisible(True)
        self.queue_changed.emit(len(self._queue))

        video_count = len(selected_urls)
        self._progress_widget._append_log(
            f"[+] {tr('queue_added') % (task.title, video_count)}"
        )

        self._clear_form()

        if not self._queue_busy:
            self._process_next_task()
        else:
            self._update_queue_display()

    def _clear_form(self):
        self._url_input.clear()
        self._format_selector.clear()
        self._playlist_selector.clear()
        self._playlist_info = None
        self._playlist_cb.setVisible(False)
        self._selector_stack.setCurrentWidget(self._format_selector)

    def _add_to_queue_list(self, task, index):
        title = task.title
        count = task.video_count
        item = QListWidgetItem(f"{title}  ({count} video{'s' if count != 1 else ''})")
        item.setData(Qt.ItemDataRole.UserRole, index)
        item.setForeground(QBrush(QColor("#888")))
        self._queue_list.addItem(item)

    def _update_queue_display(self):
        for i in range(self._queue_list.count()):
            item = self._queue_list.item(i)
            idx = item.data(Qt.ItemDataRole.UserRole)
            if idx is not None and idx < len(self._queue):
                task = self._queue[idx]
                title = task.title
                count = task.video_count
                if task.status == TaskStatus.ACTIVE:
                    item.setText(f"▶ {title}  ({count} videos)")
                    item.setForeground(QBrush(QColor("#4CAF50")))
                elif task.status == TaskStatus.DONE:
                    item.setText(f"✓ {title}  ({count} videos)")
                    item.setForeground(QBrush(QColor("#388E3C")))
                elif task.status == TaskStatus.FAILED:
                    item.setText(f"✕ {title}  ({count} videos)")
                    item.setForeground(QBrush(QColor("#D32F2F")))
                elif task.status == TaskStatus.CANCELLED:
                    item.setText(f"⊘ {title}  ({count} videos)")
                    item.setForeground(QBrush(QColor("#FF9800")))
                else:
                    item.setText(f"{title}  ({count} videos)")
                    item.setForeground(QBrush(QColor("#888")))

    def _process_next_task(self):
        if not self._queue:
            self._queue_busy = False
            self._queue_group.setVisible(False)
            self._reset_buttons()
            self.queue_changed.emit(0)
            return

        self._queue_busy = True
        self._current_task = None

        task = self._queue.next_pending()
        if not task:
            self._queue_busy = False
            self._reset_buttons()
            return

        task.status = TaskStatus.ACTIVE
        self._current_task = task
        self._update_queue_display()

        title = task.title
        self._progress_widget.reset()
        self._progress_widget._append_log(f"[▶] {tr('queue_downloading') % title}")

        self._worker = DownloadWorker(
            url=task.url,
            output_path=task.output_path,
            format_id=task.format_id,
            playlist_subfolder=task.playlist_subfolder,
            ffmpeg_path=self._ffmpeg_path,
            deno_path=self._deno_path,
            selected_urls=task.selected_urls,
            per_video_settings=task.per_video_settings,
            auth_opts=self._auth_opts,
            playlist_title=task.playlist_title,
            auth_rebuilder=self._build_fresh_auth,
        )
        self._worker.progress.connect(self._progress_widget.update_progress)
        self._worker.item_error.connect(self._on_item_error)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.yt_log.connect(self._progress_widget._append_log)

        self._cancel_btn.setEnabled(True)
        self._stop_btn.setEnabled(True)
        self._worker.start()

    def _build_fresh_auth(self):
        settings = load_settings()
        fresh = get_auth_opts(settings)
        return fresh

    def _on_item_error(self, err):
        self._progress_widget._append_log(f"[✕] {err.get('title', '')}: {err.get('error', '')}")

    def _on_cancel(self):
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self._worker.quit()
            self._worker.wait(3000)
            self._progress_widget._append_log("[✕] Cancelled")

        if self._current_task:
            self._current_task.status = TaskStatus.CANCELLED
            self._current_task = None

        self._update_queue_display()
        self._cancel_btn.setEnabled(False)
        self._stop_btn.setEnabled(False)
        self._queue_busy = False
        self._process_next_task()

    def _on_stop(self):
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self._worker.quit()
            self._worker.wait(3000)

        if self._current_task:
            self._current_task.status = TaskStatus.CANCELLED
            self._current_task = None

        self._queue.cancel_pending()

        self._progress_widget._append_log("[⊘] Stopped — queue cleared")
        self._cleanup_queue()
        self._queue_busy = False
        self._reset_buttons()

    def _on_finished(self, url, path, errors=None):
        display_title = self._current_task.title if self._current_task else url
        total = self._current_task.video_count if self._current_task else 0

        if errors:
            self._progress_widget._append_log(
                f"[⚠] {tr('playlist_skip_unavailable') % len(errors)}"
            )
            self._show_error_dialog(errors, total)

        if self._current_task:
            self._current_task.status = TaskStatus.FAILED if errors else TaskStatus.DONE
        self._current_task = None

        self._progress_widget._append_log(f"[✓] {tr('queue_completed') % display_title}")
        self._update_queue_display()

        self._cancel_btn.setEnabled(False)
        self._queue_busy = False
        self._process_next_task()

    def _show_error_dialog(self, errors, total):
        dlg = ErrorDialog(errors, total, self)
        dlg.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self._error_dialogs.append(dlg)
        dlg.finished.connect(lambda _result, dialog=dlg: self._forget_error_dialog(dialog))
        dlg.show()

    def _forget_error_dialog(self, dialog):
        if dialog in self._error_dialogs:
            self._error_dialogs.remove(dialog)

    def _on_error(self, message):
        self._progress_widget._append_log(f"[✕] {message}")
        if self._current_task:
            self._current_task.status = TaskStatus.FAILED
            title = self._current_task.title
            QMessageBox.critical(self, tr("fetch_error_title"), f"{tr('error_download')}: {title}\n{message}")
            self._current_task = None
        self._update_queue_display()
        self._cancel_btn.setEnabled(False)
        self._queue_busy = False
        self._process_next_task()

    def _clear_queue(self):
        pending = self._queue.pending()
        if pending:
            reply = QMessageBox.question(
                self, tr("queue_title"),
                tr("queue_confirm_clear") % len(pending),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.No:
                return

        self._queue.clear()
        self._queue_list.clear()
        self._queue_group.setVisible(False)
        self.queue_changed.emit(0)

    def _cleanup_queue(self):
        self._queue.remove_cancelled()
        self._queue_list.clear()
        for i, t in enumerate(self._queue):
            self._add_to_queue_list(t, i)
        self._update_queue_display()
        self.queue_changed.emit(len(self._queue))
        if not self._queue:
            self._queue_group.setVisible(False)

    def _reset_buttons(self):
        self._fetch_btn.setEnabled(True)
        self._cancel_btn.setEnabled(False)
        self._stop_btn.setEnabled(False)
