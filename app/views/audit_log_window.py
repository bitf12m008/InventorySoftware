from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QFrame, QGraphicsDropShadowEffect, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from app.models.audit_log_model import AuditLogModel


class AuditLogWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audit Logs")
        self.resize(1200, 620)
        self.setStyleSheet("background: #eef1f6;")
        self.setup_ui()
        self.load_filters()
        self.load_logs()

    def setup_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(24, 24, 24, 24)
        main.setSpacing(16)

        header = self._card()
        h = QHBoxLayout(header)
        h.setContentsMargins(24, 16, 24, 16)
        title = QLabel("Audit Log Viewer")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: #222;")
        h.addWidget(title)
        h.addStretch()
        main.addWidget(header)

        filters = self._card()
        f = QHBoxLayout(filters)
        f.setContentsMargins(20, 14, 20, 14)
        f.setSpacing(12)

        f.addWidget(QLabel("User"))
        self.user_combo = QComboBox()
        self.user_combo.setMinimumWidth(180)
        self.user_combo.setMinimumHeight(36)
        f.addWidget(self.user_combo)

        f.addWidget(QLabel("Action"))
        self.action_combo = QComboBox()
        self.action_combo.setMinimumWidth(190)
        self.action_combo.setMinimumHeight(36)
        f.addWidget(self.action_combo)

        f.addWidget(QLabel("Search"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("details/action/entity")
        self.search_input.setMinimumWidth(260)
        self.search_input.setMinimumHeight(36)
        self.search_input.returnPressed.connect(self.load_logs)
        f.addWidget(self.search_input)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setStyleSheet(self._btn_style("#4A90E2", "#3b7ac7"))
        refresh_btn.clicked.connect(self.load_logs)
        f.addWidget(refresh_btn)

        clear_btn = QPushButton("Clear")
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.setStyleSheet(self._btn_style("#6b7280", "#4b5563"))
        clear_btn.clicked.connect(self.clear_filters)
        f.addWidget(clear_btn)

        f.addStretch()
        main.addWidget(filters)

        table_card = self._card()
        t = QVBoxLayout(table_card)
        t.setContentsMargins(16, 16, 16, 16)

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            "Time", "User", "Action", "Entity",
            "Entity ID", "Shop", "Product", "Details"
        ])
        self.table.setEditTriggers(self.table.NoEditTriggers)
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.setSelectionMode(self.table.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                border: none;
                font-size: 13px;
                alternate-background-color: #f6f8fb;
                selection-background-color: #dbeafe;
                selection-color: #1f2937;
            }
            QHeaderView::section {
                background: #f0f3f8;
                padding: 8px;
                font-weight: bold;
                border: none;
            }
        """)
        t.addWidget(self.table)
        main.addWidget(table_card, stretch=1)

        self.user_combo.setStyleSheet(self._control_style())
        self.action_combo.setStyleSheet(self._control_style())
        self.search_input.setStyleSheet(self._control_style())

    def load_filters(self):
        rows = AuditLogModel.get_logs(limit=1000)
        users = sorted({r["username"] for r in rows if r["username"]})
        actions = sorted({r["action"] for r in rows if r["action"]})

        self.user_combo.clear()
        self.user_combo.addItem("All", "")
        for user in users:
            self.user_combo.addItem(user, user)

        self.action_combo.clear()
        self.action_combo.addItem("All", "")
        for action in actions:
            self.action_combo.addItem(action, action)

    def load_logs(self):
        username = self.user_combo.currentData()
        action = self.action_combo.currentData()
        query = self.search_input.text().strip()
        logs = AuditLogModel.get_logs(
            limit=1000,
            username=username or None,
            action=action or None,
            query=query or None,
        )

        self.table.setRowCount(len(logs))
        for i, row in enumerate(logs):
            self.table.setItem(i, 0, QTableWidgetItem(row["created_at"] or ""))
            self.table.setItem(i, 1, QTableWidgetItem(row["username"] or "-"))
            self.table.setItem(i, 2, QTableWidgetItem(row["action"] or "-"))
            self.table.setItem(i, 3, QTableWidgetItem(row["entity_type"] or "-"))
            self.table.setItem(i, 4, QTableWidgetItem(str(row["entity_id"] or "-")))
            self.table.setItem(i, 5, QTableWidgetItem(str(row["shop_id"] or "-")))
            self.table.setItem(i, 6, QTableWidgetItem(str(row["product_id"] or "-")))
            details_item = QTableWidgetItem(row["details"] or "")
            details_item.setForeground(QColor("#374151"))
            self.table.setItem(i, 7, details_item)

    def clear_filters(self):
        self.user_combo.setCurrentIndex(0)
        self.action_combo.setCurrentIndex(0)
        self.search_input.clear()
        self.load_logs()

    def _card(self):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 14px;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(16)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 60))
        frame.setGraphicsEffect(shadow)
        return frame

    def _control_style(self):
        return """
            QComboBox, QLineEdit {
                padding: 6px 10px;
                border-radius: 8px;
                border: 1px solid #c9c9c9;
                background: white;
                font-size: 13px;
            }
            QComboBox:focus, QLineEdit:focus {
                border: 1.5px solid #4A90E2;
            }
        """

    def _btn_style(self, bg, hover):
        return f"""
            QPushButton {{
                background: {bg};
                color: white;
                padding: 7px 18px;
                border-radius: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {hover};
            }}
        """
