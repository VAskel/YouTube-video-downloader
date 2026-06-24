import os
import json

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QFileDialog, QComboBox, QDialogButtonBox, QLabel,
    QRadioButton, QButtonGroup, QStackedWidget, QWidget, QGroupBox,
)
from PySide6.QtCore import Qt

from yt_dld.core.i18n import tr, set_language, _current_lang


SETTINGS_FILE = os.path.join(os.path.expanduser("~"), ".yt_dld", "settings.json")

BROWSERS = [
    ("brave", "Brave"),
    ("chrome", "Chrome"),
    ("chromium", "Chromium"),
    ("edge", "Edge"),
    ("firefox", "Firefox"),
    ("opera", "Opera"),
    ("vivaldi", "Vivaldi"),
]

DEFAULT_FRAGMENT_CONCURRENCY = 2


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


def get_auth_opts(settings):
    auth = settings.get("auth", {})
    method = auth.get("method")
    opts = {}
    if method == "browser":
        browser = auth.get("browser") or "chrome"
        opts["cookiesfrombrowser"] = (browser,)
    elif method == "file":
        cookies_file = auth.get("cookies_file") or ""
        if cookies_file and os.path.isfile(cookies_file):
            opts["cookiefile"] = cookies_file
    elif method == "login":
        username = auth.get("username") or ""
        password = auth.get("password") or ""
        if username:
            opts["username"] = username
            opts["password"] = password
    return opts


def get_fragment_concurrency(settings):
    value = settings.get("fragment_concurrency", DEFAULT_FRAGMENT_CONCURRENCY)
    try:
        value = int(value)
    except (TypeError, ValueError):
        return DEFAULT_FRAGMENT_CONCURRENCY
    return value if value in {1, 2, 4} else DEFAULT_FRAGMENT_CONCURRENCY


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("settings_tab"))
        self.setMinimumWidth(520)
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

        self._fragment_combo = QComboBox()
        fragment_options = [
            (tr("fragment_concurrency_reliable"), 1),
            (tr("fragment_concurrency_balanced"), 2),
            (tr("fragment_concurrency_fast"), 4),
        ]
        for label, value in fragment_options:
            self._fragment_combo.addItem(label, value)
        form.addRow(tr("settings_fragment_concurrency"), self._fragment_combo)

        layout.addLayout(form)

        auth_group = QGroupBox(tr("auth_title"))
        auth_layout = QVBoxLayout(auth_group)

        self._auth_none = QRadioButton(tr("auth_none"))
        self._auth_browser = QRadioButton(tr("auth_browser"))
        self._auth_file = QRadioButton(tr("auth_file"))
        self._auth_login = QRadioButton(tr("auth_login"))
        self._auth_none.setChecked(True)

        self._auth_group = QButtonGroup(self)
        self._auth_group.addButton(self._auth_none, 0)
        self._auth_group.addButton(self._auth_browser, 1)
        self._auth_group.addButton(self._auth_file, 2)
        self._auth_group.addButton(self._auth_login, 3)

        auth_layout.addWidget(self._auth_none)
        auth_layout.addWidget(self._auth_browser)
        auth_layout.addWidget(self._auth_file)
        auth_layout.addWidget(self._auth_login)

        self._auth_stack = QStackedWidget()

        empty_w = QWidget()
        self._auth_stack.addWidget(empty_w)

        browser_w = QWidget()
        browser_layout = QHBoxLayout(browser_w)
        browser_layout.setContentsMargins(20, 0, 0, 0)
        browser_layout.addWidget(QLabel(tr("auth_browser_select")))
        self._browser_combo = QComboBox()
        for value, label in BROWSERS:
            self._browser_combo.addItem(label, value)
        browser_layout.addWidget(self._browser_combo)
        browser_layout.addStretch()
        self._auth_stack.addWidget(browser_w)

        file_w = QWidget()
        file_layout = QHBoxLayout(file_w)
        file_layout.setContentsMargins(20, 0, 0, 0)
        file_layout.addWidget(QLabel(tr("auth_cookies_file")))
        self._cookies_input = QLineEdit()
        file_layout.addWidget(self._cookies_input)
        cookies_browse = QPushButton(tr("browse"))
        cookies_browse.clicked.connect(self._browse_cookies)
        file_layout.addWidget(cookies_browse)
        self._auth_stack.addWidget(file_w)

        login_w = QWidget()
        login_form = QFormLayout(login_w)
        login_form.setContentsMargins(20, 0, 0, 0)
        self._username_input = QLineEdit()
        self._password_input = QLineEdit()
        self._password_input.setEchoMode(QLineEdit.EchoMode.Password)
        login_form.addRow(tr("auth_username"), self._username_input)
        login_form.addRow(tr("auth_password"), self._password_input)
        self._auth_stack.addWidget(login_w)

        auth_layout.addWidget(self._auth_stack)

        self._auth_hint = QLabel("")
        self._auth_hint.setStyleSheet("color: #888; font-size: 11px;")
        self._auth_hint.setWordWrap(True)
        auth_layout.addWidget(self._auth_hint)

        self._auth_group.buttonClicked.connect(self._on_auth_changed)
        layout.addWidget(auth_group)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_auth_changed(self, btn):
        self._auth_stack.setCurrentIndex(self._auth_group.id(btn))
        if self._auth_group.checkedId() == 1:
            self._auth_hint.setText(tr("auth_browser_hint"))
        else:
            self._auth_hint.setText("")

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
        fragment_concurrency = get_fragment_concurrency(settings)
        idx = self._fragment_combo.findData(fragment_concurrency)
        if idx >= 0:
            self._fragment_combo.setCurrentIndex(idx)

        auth = settings.get("auth", {})
        method = auth.get("method", "")
        if method == "browser":
            self._auth_browser.setChecked(True)
            self._auth_stack.setCurrentIndex(1)
            browser = auth.get("browser") or "chrome"
            idx = self._browser_combo.findData(browser)
            if idx >= 0:
                self._browser_combo.setCurrentIndex(idx)
        elif method == "file":
            self._auth_file.setChecked(True)
            self._auth_stack.setCurrentIndex(2)
            self._cookies_input.setText(auth.get("cookies_file", ""))
        elif method == "login":
            self._auth_login.setChecked(True)
            self._auth_stack.setCurrentIndex(3)
            self._username_input.setText(auth.get("username", ""))
            self._password_input.setText(auth.get("password", ""))

    def _save(self):
        lang = self._lang_combo.currentData()
        settings = load_settings()
        settings["language"] = lang
        settings["default_path"] = self._path_input.text()
        settings["ffmpeg_path"] = self._ffmpeg_input.text()
        settings["fragment_concurrency"] = self._fragment_combo.currentData()

        auth_id = self._auth_group.checkedId()
        if auth_id == 1:
            settings["auth"] = {
                "method": "browser",
                "browser": self._browser_combo.currentData(),
            }
        elif auth_id == 2:
            settings["auth"] = {
                "method": "file",
                "cookies_file": self._cookies_input.text(),
            }
        elif auth_id == 3:
            settings["auth"] = {
                "method": "login",
                "username": self._username_input.text(),
                "password": self._password_input.text(),
            }
        else:
            settings["auth"] = {"method": ""}

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

    def _browse_cookies(self):
        path, _ = QFileDialog.getOpenFileName(self, tr("auth_cookies_file"))
        if path:
            self._cookies_input.setText(path)
