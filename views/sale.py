from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QLineEdit, QTableWidget,
                             QTableWidgetItem, QMessageBox, QDialog, QFormLayout,
                             QComboBox, QTabWidget, QDateEdit)
from PyQt6.QtCore import Qt, QDate
import sqlite3
from datetime import datetime
from database.main import Database

class SaleManagementPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
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
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT s.id, i.name, s.quantity, s.unit_price, s.total_amount, s.sale_date
                FROM sales s
                JOIN inventory i ON s.item_id = i.id
                ORDER BY s.sale_date DESC
            ''')
            sales = cursor.fetchall()

            self.sales_table.setRowCount(len(sales))
            for row, sale in enumerate(sales):
                for col, value in enumerate(sale):
                    if isinstance(value, float):
                        value = f"${value:.2f}"
                    cell = QTableWidgetItem(str(value))
                    cell.setFlags(cell.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.sales_table.setItem(row, col, cell)

            self.sales_table.resizeColumnsToContents()
            conn.close()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", str(e))

    def record_sale(self):
        dialog = RecordSaleDialog(self.db, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_sales_history()

    def generate_report(self):
        dialog = SalesReportDialog(self.db, self)
        dialog.exec()

    def search_sales(self):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            search_term = self.search_input.text()
            if self.search_type.currentText() == "Date":
                cursor.execute('''
                    SELECT s.id, i.name, s.quantity, s.unit_price, s.total_amount, s.sale_date
                    FROM sales s
                    JOIN inventory i ON s.item_id = i.id
                    WHERE DATE(s.sale_date) = ?
                    ORDER BY s.sale_date DESC
                ''', (search_term,))
            else:  # Item Name
                cursor.execute('''
                    SELECT s.id, i.name, s.quantity, s.unit_price, s.total_amount, s.sale_date
                    FROM sales s
                    JOIN inventory i ON s.item_id = i.id
                    WHERE i.name LIKE ?
                    ORDER BY s.sale_date DESC
                ''', (f'%{search_term}%',))

            sales = cursor.fetchall()

            self.search_table.setRowCount(len(sales))
            for row, sale in enumerate(sales):
                for col, value in enumerate(sale):
                    if isinstance(value, float):
                        value = f"${value:.2f}"
                    cell = QTableWidgetItem(str(value))
                    cell.setFlags(cell.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.search_table.setItem(row, col, cell)

            self.search_table.resizeColumnsToContents()
            conn.close()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", str(e))


class RecordSaleDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
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
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            'SELECT id, name, quantity, price FROM inventory WHERE quantity > 0')
        items = cursor.fetchall()

        self.table.setRowCount(len(items))
        for row, item in enumerate(items):
            for col, value in enumerate(item):
                if isinstance(value, float):
                    value = f"${value:.2f}"
                cell = QTableWidgetItem(str(value))
                cell.setFlags(cell.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, col, cell)

        self.table.resizeColumnsToContents()
        conn.close()

    def record_sale(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(
                self, "Warning", "Please select an item to sell.")
            return

        try:
            item_id = int(self.table.item(current_row, 0).text())
            quantity = int(self.quantity_input.text())
            available = int(self.table.item(current_row, 2).text())
            unit_price = float(self.table.item(
                current_row, 3).text().replace('$', ''))

            if quantity <= 0:
                QMessageBox.warning(
                    self, "Error", "Please enter a valid quantity.")
                return

            if quantity > available:
                QMessageBox.warning(
                    self, "Error", "Insufficient quantity in inventory!")
                return

            total_amount = quantity * unit_price
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            conn = self.db.get_connection()
            cursor = conn.cursor()

            # Record the sale
            cursor.execute('''
                INSERT INTO sales (item_id, quantity, unit_price, total_amount, sale_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (item_id, quantity, unit_price, total_amount, current_time))

            # Update inventory
            cursor.execute('''
                UPDATE inventory 
                SET quantity = quantity - ?,
                    updated_at = ?
                WHERE id = ?
            ''', (quantity, current_time, item_id))

            conn.commit()
            conn.close()

            QMessageBox.information(self, "Success",
                                    f"Sale recorded successfully!\nTotal amount: ${total_amount:.2f}")
            self.accept()

        except ValueError:
            QMessageBox.warning(
                self, "Error", "Please enter valid numeric values.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", str(e))


class SalesReportDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
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
            conn = self.db.get_connection()
            cursor = conn.cursor()

            selected_date = self.date_select.date().toString('yyyy-MM-dd')

            if self.report_type.currentText() == "Daily Report":
                cursor.execute('''
                    SELECT 
                        i.name,
                        SUM(s.quantity) as total_quantity,
                        SUM(s.total_amount) as total_sales
                    FROM sales s
                    JOIN inventory i ON s.item_id = i.id
                    WHERE DATE(s.sale_date) = ?
                    GROUP BY i.name
                ''', (selected_date,))
            else:  # Monthly Report
                cursor.execute('''
                    SELECT 
                        i.name,
                        SUM(s.quantity) as total_quantity,
                        SUM(s.total_amount) as total_sales
                    FROM sales s
                    JOIN inventory i ON s.item_id = i.id
                    WHERE strftime('%Y-%m', s.sale_date) = ?
                    GROUP BY i.name
                ''', (selected_date[:7],))

            sales = cursor.fetchall()

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

            self.total_revenue_label.setText(
                f"Total Revenue: ${total_revenue:.2f}")
            self.table.resizeColumnsToContents()
            conn.close()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", str(e))

