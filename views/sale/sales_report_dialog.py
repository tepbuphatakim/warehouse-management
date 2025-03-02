from PyQt6.QtWidgets import (QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QTableWidget,
                             QTableWidgetItem, QMessageBox, QDialog, QFormLayout,
                             QComboBox, QDateEdit)
from PyQt6.QtCore import Qt, QDate
import sqlite3
from dao.sale_dao import SaleDAO

class SalesReportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sale_dao = SaleDAO()
        self.setWindowTitle("Generate Sales Report")
        self.setMinimumWidth(500)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        form_layout = QFormLayout()
        self.report_type = QComboBox()
        self.report_type.addItems(["Daily Report", "Monthly Report"])
        form_layout.addRow("Report Type:", self.report_type)

        self.date_select = QDateEdit()
        self.date_select.setDate(QDate.currentDate())
        form_layout.addRow("Date:", self.date_select)

        layout.addLayout(form_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(
            ["Item", "Total Quantity", "Total Sales"])
        layout.addWidget(self.table)

        self.total_revenue_label = QLabel()
        layout.addWidget(self.total_revenue_label)

        button_box = QHBoxLayout()
        generate_button = QPushButton("Generate Report")
        close_button = QPushButton("Close")

        generate_button.clicked.connect(self.generate_report)
        close_button.clicked.connect(self.reject)

        button_box.addWidget(generate_button)
        button_box.addWidget(close_button)
        layout.addLayout(button_box)

        self.setLayout(layout)

    def generate_report(self):
        try:
            selected_date = self.date_select.date().toString('yyyy-MM-dd')
            report_type = self.report_type.currentText()
            
            sales = self.sale_dao.generate_report(selected_date, report_type)

            self.table.setRowCount(len(sales))
            total_revenue = 0

            for row, sale in enumerate(sales):
                for col, value in enumerate(sale):
                    if col == 2:  # Total sales column
                        value = f"${value:.2f}"
                        total_revenue += float(sale[2])
                    cell = QTableWidgetItem(str(value))
                    cell.setFlags(cell.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.table.setItem(row, col, cell)

            self.total_revenue_label.setText(f"Total Revenue: ${total_revenue:.2f}")
            self.table.resizeColumnsToContents()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", str(e))

