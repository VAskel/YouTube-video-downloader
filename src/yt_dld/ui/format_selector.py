from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QRadioButton, QButtonGroup,
    QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QLabel,
)
from PySide6.QtCore import Qt

from yt_dld.core.i18n import tr


def _format_size(size_bytes):
    if not size_bytes:
        return "?"
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    if size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


class FormatSelector(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._formats_data = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        top = QHBoxLayout()
        top.addWidget(QLabel(tr("filter_all").capitalize() + ":"))

        self._btn_all = QRadioButton(tr("filter_all"))
        self._btn_video = QRadioButton(tr("filter_video"))
        self._btn_audio = QRadioButton(tr("filter_audio"))
        self._btn_all.setChecked(True)

        self._filter_group = QButtonGroup(self)
        self._filter_group.addButton(self._btn_all, 0)
        self._filter_group.addButton(self._btn_video, 1)
        self._filter_group.addButton(self._btn_audio, 2)

        top.addWidget(self._btn_all)
        top.addWidget(self._btn_video)
        top.addWidget(self._btn_audio)
        top.addStretch()

        self._best_cb = QCheckBox(tr("best_quality"))
        self._best_cb.setChecked(True)
        top.addWidget(self._best_cb)

        layout.addLayout(top)

        self._table = QTableWidget(0, 5)
        self._table.setHorizontalHeaderLabels([
            tr("format_id"), tr("format_resolution"), tr("format_codec"),
            tr("format_size"), tr("format_note"),
        ])
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self._table.verticalHeader().setVisible(False)
        self._table.setAlternatingRowColors(True)
        layout.addWidget(self._table)

        self._filter_group.buttonClicked.connect(self._apply_filter)
        self._best_cb.toggled.connect(self._on_best_toggled)

    def load_formats(self, info):
        self._formats_data = []
        video = info.get("video_formats", [])
        audio = info.get("audio_formats", [])
        for f in video + audio:
            f["_type"] = "video" if f.get("has_video") else "audio"
            self._formats_data.append(f)

        self._apply_filter()

    def clear(self):
        self._table.setRowCount(0)
        self._formats_data = []

    def _apply_filter(self):
        fid = self._filter_group.checkedId()
        self._table.setRowCount(0)

        if fid == 1:
            filtered = [f for f in self._formats_data if f.get("has_video")]
        elif fid == 2:
            filtered = [f for f in self._formats_data if f.get("has_audio") and not f.get("has_video")]
        else:
            filtered = self._formats_data

        for f in filtered:
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(f["id"]))
            self._table.setItem(row, 1, QTableWidgetItem(f.get("resolution", "?")))
            self._table.setItem(row, 2, QTableWidgetItem(f.get("codec", "?") + "/" + f.get("acodec", "?")))
            self._table.setItem(row, 3, QTableWidgetItem(_format_size(f.get("filesize") or f.get("filesize_approx"))))
            self._table.setItem(row, 4, QTableWidgetItem(f.get("format_note", "")))

    def _on_best_toggled(self, checked):
        self._table.setEnabled(not checked)

    def selected_format_id(self):
        if self._best_cb.isChecked():
            return "best"
        row = self._table.currentRow()
        if row >= 0:
            item = self._table.item(row, 0)
            if item:
                return item.text()
        return "best"

    def has_formats(self):
        return len(self._formats_data) > 0
