from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)

from app.models.product_model import ProductModel

class EditProductWindow(QWidget):
    def __init__(self, product_id):
        super().__init__()

        self.product_id = product_id

        self.setWindowTitle("Edit Product")
        self.setMinimumSize(360, 140)

        self.setup_ui()
        self.load_product()

    def setup_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Product Name:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_product)
        layout.addWidget(save_btn)

        self.setLayout(layout)

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
        self.close()
