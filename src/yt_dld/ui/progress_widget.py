from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QProgressBar, QLabel, QTextEdit, QHBoxLayout,
)
from PySide6.QtCore import Qt

from yt_dld.core.i18n import tr


def _format_speed(bps):
    if bps < 1024:
        return f"{bps:.0f} B/s"
    if bps < 1024 * 1024:
        return f"{bps / 1024:.1f} KB/s"
    return f"{bps / (1024 * 1024):.1f} MB/s"


def _format_eta(seconds):
    if seconds < 60:
        return f"{seconds:.0f}s"
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m}:{s:02d}"


class ProgressWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._last_logged_fn = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        layout.addWidget(self._progress_bar)

        info_layout = QHBoxLayout()
        self._speed_label = QLabel("")
        self._eta_label = QLabel("")
        self._playlist_label = QLabel("")
        info_layout.addWidget(self._speed_label)
        info_layout.addStretch()
        info_layout.addWidget(self._eta_label)
        info_layout.addStretch()
        info_layout.addWidget(self._playlist_label)
        layout.addLayout(info_layout)

        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setMaximumHeight(120)
        self._log.setPlaceholderText(tr("status_ready"))
        layout.addWidget(self._log)

    def update_progress(self, data):
        status = data.get("status", "")
        self._progress_bar.setValue(int(data.get("percent", 0)))

        if status == "downloading":
            speed = data.get("speed", 0)
            eta = data.get("eta", 0)
            fn = data.get("filename", "")

            self._speed_label.setText(f"{tr('speed')}: {_format_speed(speed)}" if speed else "")
            self._eta_label.setText(f"{tr('eta')}: {_format_eta(eta)}" if eta else "")

            playlist_idx = data.get("playlist_index")
            playlist_count = data.get("playlist_count")
            if playlist_idx and playlist_count:
                self._playlist_label.setText(f"{tr('playlist_progress')}: {playlist_idx}/{playlist_count}")
            else:
                self._playlist_label.setText("")

            if fn and fn != self._last_logged_fn:
                self._last_logged_fn = fn
                self._append_log(f"[↓] {fn}")

        elif status == "finished":
            self._progress_bar.setValue(100)
            self._speed_label.setText("")
            self._eta_label.setText("")
            self._playlist_label.setText("")
            fn = data.get("filename", "")
            if fn:
                self._append_log(f"[✓] {fn}")

    def reset(self):
        self._progress_bar.setValue(0)
        self._speed_label.setText("")
        self._eta_label.setText("")
        self._playlist_label.setText("")
        self._last_logged_fn = None

    def _append_log(self, text):
        self._log.append(text)
        scrollbar = self._log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
