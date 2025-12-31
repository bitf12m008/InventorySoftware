from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFrame, QGraphicsDropShadowEffect,
    QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from app.models.product_model import ProductModel

class EditProductWindow(QWidget):
    def __init__(self, product_id, on_success=None):
        super().__init__()

        self.on_success = on_success
        self.product_id = product_id

        self.setWindowTitle("Edit Product")
        self.setFixedSize(460, 350)
        self.setStyleSheet("background: #eef1f6;")

        self.setup_ui()
        self.load_product()

    def setup_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(36, 36, 36, 36)
        main.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 18px;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(22)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 70))
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 44, 40, 44)
        card_layout.setSpacing(12)

        title = QLabel("Edit Product")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setMinimumHeight(42)
        title.setStyleSheet("color: #222;")
        card_layout.addWidget(title)

        card_layout.addSpacerItem(QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

        subtitle = QLabel("Update product details")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setMinimumHeight(28)
        subtitle.setStyleSheet("color: #666;")
        card_layout.addWidget(subtitle)

        card_layout.addSpacerItem(QSpacerItem(0, 18, QSizePolicy.Minimum, QSizePolicy.Fixed))

        label = QLabel("Product Name")
        label.setFont(QFont("Segoe UI", 11))
        label.setMinimumHeight(24)
        label.setStyleSheet("color: #444;")
        card_layout.addWidget(label)

        card_layout.addSpacerItem(QSpacerItem(0, 6, QSizePolicy.Minimum, QSizePolicy.Fixed))

        self.name_input = QLineEdit()
        self.name_input.setMinimumHeight(46)
        self.name_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 16px;
                border-radius: 8px;
                font-size: 14px;
                border: 1px solid #c9c9c9;
                background: white;
            }
            QLineEdit:focus {
                border: 1.4px solid #4A90E2;
            }
        """)
        card_layout.addWidget(self.name_input)

        card_layout.addSpacerItem(QSpacerItem(0, 18, QSizePolicy.Minimum, QSizePolicy.Fixed))

        save_btn = QPushButton("Save Changes")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setMinimumHeight(50)
        save_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #4A90E2;
                color: white;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                margin-top: 14px;
            }
            QPushButton:hover {
                background: #3b7ac7;
            }
        """)
        save_btn.clicked.connect(self.save_product)
        card_layout.addWidget(save_btn)

        card_layout.addSpacerItem(QSpacerItem(0, 8, QSizePolicy.Minimum, QSizePolicy.Fixed))

        main.addWidget(card)

    def load_product(self):
        product = ProductModel.get_by_id(self.product_id)

        if not product:
            QMessageBox.critical(self, "Error", "Product not found.")
            self.close()
            return

        self.name_input.setText(product["name"])

    def save_product(self):
        new_name = self.name_input.text().strip()

        if not new_name:
            QMessageBox.warning(self, "Error", "Product name is required.")
            return

        ProductModel.update_name(self.product_id, new_name)
        QMessageBox.information(self, "Success", "Product updated successfully.")
        self.on_success()
        self.close()
