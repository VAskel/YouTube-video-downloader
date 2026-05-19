from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QLabel, QApplication,
)
from PySide6.QtCore import Qt

from yt_dld.core.i18n import tr


class ErrorDialog(QDialog):
    def __init__(self, errors, total_count=None, parent=None):
        super().__init__(parent)
        self._errors = errors
        self._total_count = total_count or len(errors)
        self.setWindowTitle(tr("error_dialog_title"))
        self.resize(600, 300)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        count_label = QLabel(tr("errors_count") % (len(self._errors), self._total_count))
        count_label.setStyleSheet("font-weight: bold; color: #c0392b;")
        layout.addWidget(count_label)

        self._table = QTableWidget(len(self._errors), 3)
        self._table.setHorizontalHeaderLabels([
            tr("error_table_index"), tr("error_table_title"), tr("error_table_error"),
        ])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self._table.setColumnWidth(0, 40)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)

        for i, err in enumerate(self._errors):
            idx_item = QTableWidgetItem(str(i + 1))
            idx_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(i, 0, idx_item)

            title_item = QTableWidgetItem(err.get("title", ""))
            title_item.setToolTip(err.get("url", ""))
            self._table.setItem(i, 1, title_item)

            error_item = QTableWidgetItem(err.get("error", ""))
            self._table.setItem(i, 2, error_item)

        layout.addWidget(self._table)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        copy_btn = QPushButton(tr("copy_errors"))
        copy_btn.clicked.connect(self._copy)
        btn_layout.addWidget(copy_btn)

        close_btn = QPushButton(tr("close"))
        close_btn.clicked.connect(self.accept)
        close_btn.setDefault(True)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

    def _copy(self):
        lines = []
        for err in self._errors:
            lines.append(f"{err.get('title', '')}: {err.get('error', '')}")
        QApplication.clipboard().setText("\n".join(lines))
