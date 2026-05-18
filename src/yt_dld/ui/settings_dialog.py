import os
import json

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QFileDialog, QComboBox, QDialogButtonBox, QLabel,
)
from PySide6.QtCore import Qt

from yt_dld.core.i18n import tr, set_language, _current_lang


SETTINGS_FILE = os.path.join(os.path.expanduser("~"), ".yt_dld", "settings.json")


def load_settings():
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_settings(settings):
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("settings_tab"))
        self.setMinimumWidth(500)
        self._setup_ui()
        self._load()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()

        self._lang_combo = QComboBox()
        self._lang_combo.addItem("Русский", "ru")
        self._lang_combo.addItem("English", "en")
        form.addRow(tr("settings_language"), self._lang_combo)

        path_layout = QHBoxLayout()
        self._path_input = QLineEdit()
        self._path_input.setText(os.path.expanduser("~/Downloads"))
        path_layout.addWidget(self._path_input)
        browse_btn = QPushButton(tr("browse"))
        browse_btn.clicked.connect(self._browse_path)
        path_layout.addWidget(browse_btn)
        form.addRow(tr("settings_default_path"), path_layout)

        ffmpeg_layout = QHBoxLayout()
        self._ffmpeg_input = QLineEdit()
        self._ffmpeg_input.setPlaceholderText("Auto-detected")
        ffmpeg_layout.addWidget(self._ffmpeg_input)
        browse_ffmpeg = QPushButton(tr("browse"))
        browse_ffmpeg.clicked.connect(self._browse_ffmpeg)
        ffmpeg_layout.addWidget(browse_ffmpeg)
        form.addRow(tr("settings_ffmpeg_path"), ffmpeg_layout)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load(self):
        settings = load_settings()
        lang = settings.get("language", _current_lang)
        idx = self._lang_combo.findData(lang)
        if idx >= 0:
            self._lang_combo.setCurrentIndex(idx)
        path = settings.get("default_path", "")
        if path:
            self._path_input.setText(path)
        ffmpeg_path = settings.get("ffmpeg_path", "")
        if ffmpeg_path:
            self._ffmpeg_input.setText(ffmpeg_path)

    def _save(self):
        lang = self._lang_combo.currentData()
        settings = load_settings()
        settings["language"] = lang
        settings["default_path"] = self._path_input.text()
        settings["ffmpeg_path"] = self._ffmpeg_input.text()
        save_settings(settings)
        set_language(lang)
        self.accept()

    def _browse_path(self):
        path = QFileDialog.getExistingDirectory(self, tr("output_path"), self._path_input.text())
        if path:
            self._path_input.setText(path)

    def _browse_ffmpeg(self):
        path, _ = QFileDialog.getOpenFileName(self, tr("settings_ffmpeg_path"))
        if path:
            self._ffmpeg_input.setText(path)
