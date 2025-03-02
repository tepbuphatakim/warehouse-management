from PyQt6.QtWidgets import (QVBoxLayout,
                             QHBoxLayout, QPushButton, QLineEdit, QTableWidget,
                             QTableWidgetItem, QMessageBox, QDialog, QFormLayout, QTextEdit)
from PyQt6.QtCore import Qt


class ProcessReturnDialog(QDialog):
    def __init__(self, return_items_dao, parent=None):
        super().__init__(parent)
        self.return_items_dao = return_items_dao
        self.setWindowTitle("Process New Return")
        self.setMinimumWidth(800)
        self.setup_ui()
        self.load_recent_sales()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(6)
        self.sales_table.setHorizontalHeaderLabels(
            ["Sale ID", "Item", "Quantity", "Unit Price", "Total", "Sale Date"])
        layout.addWidget(self.sales_table)

        form_layout = QFormLayout()
        self.quantity_input = QLineEdit()
        self.reason_input = QTextEdit()
        self.reason_input.setMaximumHeight(100)

        form_layout.addRow("Return Quantity:", self.quantity_input)
        form_layout.addRow("Reason:", self.reason_input)
        layout.addLayout(form_layout)

        button_box = QHBoxLayout()
        process_button = QPushButton("Process Return")
        cancel_button = QPushButton("Cancel")

        process_button.clicked.connect(self.process_return)
        cancel_button.clicked.connect(self.reject)

        button_box.addWidget(process_button)
        button_box.addWidget(cancel_button)
        layout.addLayout(button_box)

        self.setLayout(layout)

    def load_recent_sales(self):
        try:
            sales = self.return_items_dao.get_recent_sales()

            self.sales_table.setRowCount(len(sales))
            for row, sale in enumerate(sales):
                for col, value in enumerate(sale):
                    if isinstance(value, float):
                        value = f"${value:.2f}"
                    cell = QTableWidgetItem(str(value))
                    cell.setFlags(cell.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.sales_table.setItem(row, col, cell)

            self.sales_table.resizeColumnsToContents()

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))

    def process_return(self):
        current_row = self.sales_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(
                self, "Warning", "Please select a sale to process return.")
            return

        try:
            sale_id = int(self.sales_table.item(current_row, 0).text())
            max_quantity = int(self.sales_table.item(current_row, 2).text())
            return_quantity = int(self.quantity_input.text())
            unit_price = float(self.sales_table.item(
                current_row, 3).text().replace('$', ''))
            reason = self.reason_input.toPlainText()

            if return_quantity <= 0 or return_quantity > max_quantity:
                QMessageBox.warning(self, "Error", "Invalid return quantity!")
                return

            refund_amount = return_quantity * unit_price

            self.return_items_dao.process_return(
                sale_id, return_quantity, refund_amount, reason)

            QMessageBox.information(self, "Success",
                                    f"Return processed successfully!\nRefund amount: ${refund_amount:.2f}")
            self.accept()

        except ValueError:
            QMessageBox.warning(
                self, "Error", "Please enter valid numeric values.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
