from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QLineEdit, QTableWidget,
                             QTableWidgetItem, QMessageBox, QDialog, QFormLayout,
                             QComboBox, QTabWidget, QTextEdit)
from PyQt6.QtCore import Qt
import sqlite3
from datetime import datetime
from database.main import Database


class ReturnItemsPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Returns Management System')
        self.setGeometry(100, 100, 1000, 600)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.returns_history_tab = QWidget()
        self.setup_returns_history_tab()
        self.tabs.addTab(self.returns_history_tab, "Returns History")

        self.search_tab = QWidget()
        self.setup_search_tab()
        self.tabs.addTab(self.search_tab, "Search Returns")

    def setup_returns_history_tab(self):
        layout = QVBoxLayout()

        self.returns_table = QTableWidget()
        self.returns_table.setColumnCount(6)
        self.returns_table.setHorizontalHeaderLabels(
            ["ID", "Item", "Quantity", "Refund Amount", "Reason", "Return Date"])
        layout.addWidget(self.returns_table)

        button_layout = QHBoxLayout()
        new_return_button = QPushButton("Process New Return")
        refresh_button = QPushButton("Refresh")

        new_return_button.clicked.connect(self.process_return)
        refresh_button.clicked.connect(self.refresh_returns_history)

        button_layout.addWidget(new_return_button)
        button_layout.addWidget(refresh_button)
        layout.addLayout(button_layout)

        self.returns_history_tab.setLayout(layout)
        self.refresh_returns_history()

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
            ["ID", "Item", "Quantity", "Refund Amount", "Reason", "Return Date"])
        layout.addWidget(self.search_table)

        search_button.clicked.connect(self.search_returns)
        self.search_tab.setLayout(layout)

    def refresh_returns_history(self):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT r.id, i.name, r.quantity, r.refund_amount, r.reason, r.return_date
                FROM returns r
                JOIN inventory i ON r.item_id = i.id
                ORDER BY r.return_date DESC
            ''')
            returns = cursor.fetchall()

            self.returns_table.setRowCount(len(returns))
            for row, return_item in enumerate(returns):
                for col, value in enumerate(return_item):
                    if isinstance(value, float):
                        value = f"${value:.2f}"
                    cell = QTableWidgetItem(str(value))
                    cell.setFlags(cell.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.returns_table.setItem(row, col, cell)

            self.returns_table.resizeColumnsToContents()
            conn.close()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", str(e))

    def process_return(self):
        dialog = ProcessReturnDialog(self.db, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_returns_history()

    def search_returns(self):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            search_term = self.search_input.text()
            if self.search_type.currentText() == "Date":
                cursor.execute('''
                    SELECT r.id, i.name, r.quantity, r.refund_amount, r.reason, r.return_date
                    FROM returns r
                    JOIN inventory i ON r.item_id = i.id
                    WHERE DATE(r.return_date) = ?
                    ORDER BY r.return_date DESC
                ''', (search_term,))
            else:  # Item Name
                cursor.execute('''
                    SELECT r.id, i.name, r.quantity, r.refund_amount, r.reason, r.return_date
                    FROM returns r
                    JOIN inventory i ON r.item_id = i.id
                    WHERE i.name LIKE ?
                    ORDER BY r.return_date DESC
                ''', (f'%{search_term}%',))

            returns = cursor.fetchall()

            self.search_table.setRowCount(len(returns))
            for row, return_item in enumerate(returns):
                for col, value in enumerate(return_item):
                    if isinstance(value, float):
                        value = f"${value:.2f}"
                    cell = QTableWidgetItem(str(value))
                    cell.setFlags(cell.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.search_table.setItem(row, col, cell)

            self.search_table.resizeColumnsToContents()
            conn.close()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", str(e))


class ProcessReturnDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
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
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT s.id, i.name, s.quantity, s.unit_price, s.total_amount, s.sale_date
                FROM sales s
                JOIN inventory i ON s.item_id = i.id
                ORDER BY s.sale_date DESC
                LIMIT 10
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
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            conn = self.db.get_connection()
            cursor = conn.cursor()

            # Get item_id
            cursor.execute(
                'SELECT item_id FROM sales WHERE id = ?', (sale_id,))
            item_id = cursor.fetchone()[0]

            # Process return
            cursor.execute('''
                INSERT INTO returns (sale_id, item_id, quantity, refund_amount, reason, return_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (sale_id, item_id, return_quantity, refund_amount, reason, current_time))

            # Update inventory
            cursor.execute('''
                UPDATE inventory 
                SET quantity = quantity + ?,
                    updated_at = ?
                WHERE id = ?
            ''', (return_quantity, current_time, item_id))

            conn.commit()
            conn.close()

            QMessageBox.information(self, "Success",
                                    f"Return processed successfully!\nRefund amount: ${refund_amount:.2f}")
            self.accept()

        except ValueError:
            QMessageBox.warning(
                self, "Error", "Please enter valid numeric values.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", str(e))
