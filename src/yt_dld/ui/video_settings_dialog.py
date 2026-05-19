from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox, QLineEdit,
    QDialogButtonBox, QLabel,
)

from yt_dld.core.i18n import tr


FORMAT_OPTIONS = [
    ("best", "settings_format_best"),
    ("bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best", "settings_format_video_audio"),
    ("bestvideo[ext=mp4]/best", "settings_format_video_only"),
    ("bestaudio[ext=m4a]/best", "settings_format_audio_only"),
]


class VideoSettingsDialog(QDialog):
    def __init__(self, title, current_settings=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{tr('per_video_settings')}: {title[:50]}")
        self.setMinimumWidth(400)
        self._setup_ui()

        if current_settings:
            self._load(current_settings)

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        self._title_label = QLabel()
        self._title_label.setWordWrap(True)
        layout.addWidget(self._title_label)

        form = QFormLayout()

        self._format_combo = QComboBox()
        for value, key in FORMAT_OPTIONS:
            self._format_combo.addItem(tr(key), value)
        form.addRow(tr("settings_format"), self._format_combo)

        self._filename_input = QLineEdit()
        self._filename_input.setPlaceholderText("auto")
        form.addRow(tr("settings_filename"), self._filename_input)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        ok_btn = buttons.button(QDialogButtonBox.StandardButton.Ok)
        ok_btn.setText(tr("settings_apply"))
        cancel_btn = buttons.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_btn.setText(tr("close"))
        layout.addWidget(buttons)

    def _load(self, settings):
        fmt = settings.get("format", "best")
        for i in range(self._format_combo.count()):
            if self._format_combo.itemData(i) == fmt:
                self._format_combo.setCurrentIndex(i)
                break
        self._filename_input.setText(settings.get("filename", ""))

    def settings(self):
        return {
            "format": self._format_combo.currentData(),
            "filename": self._filename_input.text().strip(),
        }
