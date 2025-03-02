from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QLineEdit, QTableWidget,
                             QTableWidgetItem, QMessageBox, QDialog, QFormLayout,
                             QComboBox, QTabWidget, QDateEdit)
from PyQt6.QtCore import Qt, QDate
import sqlite3
from dao.sale_dao import SaleDAO
from views.sale.record_sale_dialog import RecordSaleDialog
from views.sale.sales_report_dialog import SalesReportDialog

class SaleManagementPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.sale_dao = SaleDAO()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Sales Management System')
        self.setGeometry(100, 100, 800, 600)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.sales_history_tab = QWidget()
        self.setup_sales_history_tab()
        self.tabs.addTab(self.sales_history_tab, "Sales History")

        self.search_tab = QWidget()
        self.setup_search_tab()
        self.tabs.addTab(self.search_tab, "Search Sales")

    def setup_sales_history_tab(self):
        layout = QVBoxLayout()

        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(6)
        self.sales_table.setHorizontalHeaderLabels(
            ["ID", "Item", "Quantity", "Unit Price", "Total", "Sale Date"])
        layout.addWidget(self.sales_table)

        button_layout = QHBoxLayout()
        new_sale_button = QPushButton("Record New Sale")
        refresh_button = QPushButton("Refresh")
        report_button = QPushButton("Generate Report")

        new_sale_button.clicked.connect(self.record_sale)
        refresh_button.clicked.connect(self.refresh_sales_history)
        report_button.clicked.connect(self.generate_report)

        button_layout.addWidget(new_sale_button)
        button_layout.addWidget(refresh_button)
        button_layout.addWidget(report_button)
        layout.addLayout(button_layout)

        self.sales_history_tab.setLayout(layout)
        self.refresh_sales_history()

    def setup_search_tab(self):
        layout = QVBoxLayout()

        search_layout = QHBoxLayout()
        self.search_type = QComboBox()
        self.search_type.addItems(["Date", "Item Name"])
        self.search_input = QLineEdit()
        search_button = QPushButton("Search")

        search_layout.addWidget(QLabel("Search by:"))
        search_layout.addWidget(self.search_type)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)

        layout.addLayout(search_layout)

        self.search_table = QTableWidget()
        self.search_table.setColumnCount(6)
        self.search_table.setHorizontalHeaderLabels(
            ["ID", "Item", "Quantity", "Unit Price", "Total", "Sale Date"])
        layout.addWidget(self.search_table)

        search_button.clicked.connect(self.search_sales)
        self.search_tab.setLayout(layout)

    def refresh_sales_history(self):
        try:
            sales = self.sale_dao.get_all_sales()
            self.sales_table.setRowCount(len(sales))
            for row, sale in enumerate(sales):
                for col, value in enumerate(sale):
                    if isinstance(value, float):
                        value = f"${value:.2f}"
                    cell = QTableWidgetItem(str(value))
                    cell.setFlags(cell.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.sales_table.setItem(row, col, cell)

            self.sales_table.resizeColumnsToContents()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", str(e))

    def record_sale(self):
        dialog = RecordSaleDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_sales_history()

    def generate_report(self):
        dialog = SalesReportDialog(self)
        dialog.exec()

    def search_sales(self):
        try:
            search_term = self.search_input.text()
            if self.search_type.currentText() == "Date":                            
                sales = self.sale_dao.search_sales_by_date(search_term)
            else:  # Item Name
                sales = self.sale_dao.search_sales_by_item_name(search_term)

            self.search_table.setRowCount(len(sales))
            for row, sale in enumerate(sales):
                for col, value in enumerate(sale):
                    if isinstance(value, float):
                        value = f"${value:.2f}"
                    cell = QTableWidgetItem(str(value))
                    cell.setFlags(cell.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.search_table.setItem(row, col, cell)

            self.search_table.resizeColumnsToContents()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", str(e))



