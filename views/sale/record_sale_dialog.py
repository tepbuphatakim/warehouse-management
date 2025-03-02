from PyQt6.QtWidgets import (QVBoxLayout,
                             QHBoxLayout, QPushButton, QLineEdit, QTableWidget,
                             QTableWidgetItem, QMessageBox, QDialog, QFormLayout)
from PyQt6.QtCore import Qt
import sqlite3
from dao.sale_dao import SaleDAO

class RecordSaleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sale_dao = SaleDAO()
        self.setWindowTitle("Record New Sale")
        self.setMinimumWidth(600)
        self.setup_ui()
        self.load_available_items()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Name", "Available", "Price"])
        layout.addWidget(self.table)

        form_layout = QFormLayout()
        self.quantity_input = QLineEdit()
        form_layout.addRow("Quantity:", self.quantity_input)
        layout.addLayout(form_layout)

        button_box = QHBoxLayout()
        save_button = QPushButton("Record Sale")
        cancel_button = QPushButton("Cancel")

        save_button.clicked.connect(self.record_sale)
        cancel_button.clicked.connect(self.reject)

        button_box.addWidget(save_button)
        button_box.addWidget(cancel_button)
        layout.addLayout(button_box)

        self.setLayout(layout)

    def load_available_items(self):
        try:
            items = self.sale_dao.get_available_items()
            self.table.setRowCount(len(items))
            for row, item in enumerate(items):
                for col, value in enumerate(item):
                    if isinstance(value, float):
                        value = f"${value:.2f}"
                    cell = QTableWidgetItem(str(value))
                    cell.setFlags(cell.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.table.setItem(row, col, cell)

            self.table.resizeColumnsToContents()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", str(e))

    def record_sale(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select an item to sell.")
            return

        try:
            item_id = int(self.table.item(current_row, 0).text())
            quantity = int(self.quantity_input.text())
            available = int(self.table.item(current_row, 2).text())
            unit_price = float(self.table.item(current_row, 3).text().replace('$', ''))

            if quantity <= 0:
                QMessageBox.warning(self, "Error", "Please enter a valid quantity.")
                return

            if quantity > available:
                QMessageBox.warning(self, "Error", "Insufficient quantity in inventory!")
                return

            if self.sale_dao.record_sale(item_id, quantity, unit_price):
                total_amount = quantity * unit_price
                QMessageBox.information(self, "Success",
                                    f"Sale recorded successfully!\nTotal amount: ${total_amount:.2f}")
                self.accept()

        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter valid numeric values.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", str(e))
