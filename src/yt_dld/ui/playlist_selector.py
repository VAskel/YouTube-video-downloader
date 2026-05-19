from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QLabel,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor

from yt_dld.core.i18n import tr
from yt_dld.ui.video_settings_dialog import VideoSettingsDialog


def _format_duration(secs):
    if secs is None:
        return "-"
    m = int(secs // 60)
    s = int(secs % 60)
    return f"{m}:{s:02d}"


class PlaylistSelector(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._entries = []
        self._settings = {}
        self._locked = False
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        top = QHBoxLayout()

        self._select_all_btn = QPushButton(tr("select_all"))
        self._select_all_btn.clicked.connect(self._select_all)
        top.addWidget(self._select_all_btn)

        self._deselect_all_btn = QPushButton(tr("deselect_all"))
        self._deselect_all_btn.clicked.connect(self._deselect_all)
        top.addWidget(self._deselect_all_btn)

        top.addStretch()

        self._info_label = QLabel("")
        top.addWidget(self._info_label)

        layout.addLayout(top)

        self._table = QTableWidget(0, 5)
        self._table.setHorizontalHeaderLabels([
            "", tr("error_table_index"), tr("error_table_title"), tr("duration"), "⚙",
        ])
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self._table.setColumnWidth(0, 30)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self._table.setColumnWidth(1, 40)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self._table.setColumnWidth(4, 30)
        self._table.verticalHeader().setVisible(False)
        self._table.setAlternatingRowColors(True)

        self._table.cellClicked.connect(self._on_cell_clicked)
        layout.addWidget(self._table)

    def load_entries(self, entries):
        self._entries = entries
        self._settings = {}
        self._table.setRowCount(0)

        available = sum(1 for e in entries if e.get("available"))
        unavailable = sum(1 for e in entries if not e.get("available"))

        self._info_label.setText(
            f"{tr('available_count')}: {available}  |  "
            f"{tr('unavailable_count')}: {unavailable}"
        )

        for entry in entries:
            row = self._table.rowCount()
            self._table.insertRow(row)

            cb_item = QTableWidgetItem("☑" if entry.get("available") else "☐")
            cb_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            cb_item.setCheckState(
                Qt.CheckState.Checked if entry.get("available") else Qt.CheckState.Unchecked
            )
            cb_item.setData(Qt.ItemDataRole.UserRole, entry.get("available", False))
            self._table.setItem(row, 0, cb_item)

            idx_item = QTableWidgetItem(str(entry.get("index", row + 1)))
            idx_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 1, idx_item)

            title = entry.get("title", f"Video #{row + 1}")
            if not entry.get("available"):
                title = f"{title} [{tr('hidden_video')}]"
            title_item = QTableWidgetItem(title)
            self._table.setItem(row, 2, title_item)

            dur = _format_duration(entry.get("duration"))
            dur_item = QTableWidgetItem(dur)
            dur_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 3, dur_item)

            gear_item = QTableWidgetItem("⚙")
            gear_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            gear_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self._table.setItem(row, 4, gear_item)

            if not entry.get("available"):
                gray = QBrush(QColor(160, 160, 160))
                for col in range(5):
                    self._table.item(row, col).setForeground(gray)

    def _on_cell_clicked(self, row, col):
        if col == 0:
            self._toggle_checkbox(row)
        elif col == 4:
            self._open_settings(row)

    def _toggle_checkbox(self, row):
        item = self._table.item(row, 0)
        available = item.data(Qt.ItemDataRole.UserRole)
        if not available:
            item.setCheckState(Qt.CheckState.Unchecked)
            item.setText("☐")
            return
        if item.checkState() == Qt.CheckState.Checked:
            item.setCheckState(Qt.CheckState.Unchecked)
            item.setText("☐")
        else:
            item.setCheckState(Qt.CheckState.Checked)
            item.setText("☑")

    def _open_settings(self, row):
        if self._locked:
            return
        entry = self._entries[row]
        if not entry.get("available"):
            return
        url = entry.get("url")
        if not url:
            return

        current = self._settings.get(url)
        dlg = VideoSettingsDialog(entry["title"], current, self)
        if dlg.exec():
            self._settings[url] = dlg.settings()
            gear_item = self._table.item(row, 4)
            if gear_item:
                gear_item.setText("⚙✓")

    def _select_all(self):
        for row in range(self._table.rowCount()):
            item = self._table.item(row, 0)
            if item.data(Qt.ItemDataRole.UserRole):
                item.setCheckState(Qt.CheckState.Checked)
                item.setText("☑")

    def _deselect_all(self):
        for row in range(self._table.rowCount()):
            item = self._table.item(row, 0)
            item.setCheckState(Qt.CheckState.Unchecked)
            item.setText("☐")

    def selected_urls(self):
        urls = []
        for row in range(self._table.rowCount()):
            item = self._table.item(row, 0)
            if item.checkState() == Qt.CheckState.Checked:
                entry = self._entries[row]
                url = entry.get("url")
                if url:
                    urls.append(url)
        return urls

    def selected_count(self):
        return sum(
            1 for row in range(self._table.rowCount())
            if self._table.item(row, 0).checkState() == Qt.CheckState.Checked
        )

    def get_settings(self):
        return dict(self._settings)

    def lock(self):
        self._locked = True
        self._select_all_btn.setEnabled(False)
        self._deselect_all_btn.setEnabled(False)
        for row in range(self._table.rowCount()):
            item = self._table.item(row, 0)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            gear = self._table.item(row, 4)
            if gear:
                gear.setFlags(Qt.ItemFlag.NoItemFlags)

    def unlock(self):
        self._locked = False
        self._select_all_btn.setEnabled(True)
        self._deselect_all_btn.setEnabled(True)
        for row in range(self._table.rowCount()):
            entry = self._entries[row]
            flags = Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled
            item = self._table.item(row, 0)
            item.setFlags(flags)
            if entry.get("available"):
                gear = self._table.item(row, 4)
                if gear:
                    gear.setFlags(Qt.ItemFlag.ItemIsEnabled)

    def clear(self):
        self._table.setRowCount(0)
        self._entries = []
        self._settings = {}
        self._info_label.setText("")
