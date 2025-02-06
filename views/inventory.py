from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLineEdit, QTableWidget,
                             QTableWidgetItem, QMessageBox, QDialog, QFormLayout)
from PyQt6.QtCore import Qt
import sqlite3
from datetime import datetime
from database.main import Database


class InventoryPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Inventory Management System')
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search items...")
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_items)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        layout.addLayout(search_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Name", "Quantity", "Price", "Location", "Last Updated"])
        layout.addWidget(self.table)

        button_layout = QHBoxLayout()
        add_button = QPushButton("Add Item")
        update_button = QPushButton("Update Item")
        delete_button = QPushButton("Delete Item")
        refresh_button = QPushButton("Refresh")

        add_button.clicked.connect(self.add_item)
        update_button.clicked.connect(self.update_item)
        delete_button.clicked.connect(self.delete_item)
        refresh_button.clicked.connect(self.refresh_table)

        button_layout.addWidget(add_button)
        button_layout.addWidget(update_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(refresh_button)
        layout.addLayout(button_layout)

        # Load initial data
        self.refresh_table()

    def refresh_table(self):
        self.table.setRowCount(0)
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM inventory')
        items = cursor.fetchall()

        for row_num, item in enumerate(items):
            self.table.insertRow(row_num)
            for col_num, value in enumerate(item):
                if col_num < 6:  # Skip created_at column
                    if isinstance(value, float):
                        value = f"${value:.2f}"
                    cell = QTableWidgetItem(str(value))
                    cell.setFlags(cell.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.table.setItem(row_num, col_num, cell)

        conn.close()
        self.table.resizeColumnsToContents()

    def add_item(self):
        dialog = AddItemDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                data = dialog.get_item_data()
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                conn = self.db.get_connection()
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO inventory (name, quantity, price, location, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (data['name'], int(data['quantity']), float(data['price']),
                      data['location'], current_time, current_time))

                conn.commit()
                conn.close()

                self.refresh_table()
                QMessageBox.information(
                    self, "Success", "Item added successfully!")
            except ValueError:
                QMessageBox.warning(
                    self, "Error", "Please enter valid numeric values.")
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", str(e))

    def update_item(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(
                self, "Warning", "Please select an item to update.")
            return

        item_data = {
            'id': self.table.item(current_row, 0).text(),
            'name': self.table.item(current_row, 1).text(),
            'quantity': self.table.item(current_row, 2).text(),
            'price': self.table.item(current_row, 3).text().replace('$', ''),
            'location': self.table.item(current_row, 4).text()
        }

        dialog = UpdateItemDialog(item_data, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                data = dialog.get_item_data()
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                conn = self.db.get_connection()
                cursor = conn.cursor()

                cursor.execute('''
                    UPDATE inventory 
                    SET name = ?, quantity = ?, price = ?, location = ?, updated_at = ?
                    WHERE id = ?
                ''', (data['name'], int(data['quantity']), float(data['price']),
                      data['location'], current_time, item_data['id']))

                conn.commit()
                conn.close()

                self.refresh_table()
                QMessageBox.information(
                    self, "Success", "Item updated successfully!")
            except ValueError:
                QMessageBox.warning(
                    self, "Error", "Please enter valid numeric values.")
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", str(e))

    def delete_item(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(
                self, "Warning", "Please select an item to delete.")
            return

        item_id = self.table.item(current_row, 0).text()
        reply = QMessageBox.question(self, "Confirm Deletion",
                                     "Are you sure you want to delete this item?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()

                cursor.execute(
                    'DELETE FROM inventory WHERE id = ?', (item_id,))
                conn.commit()
                conn.close()

                self.refresh_table()
                QMessageBox.information(
                    self, "Success", "Item deleted successfully!")
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", str(e))

    def search_items(self):
        search_term = self.search_input.text()
        self.table.setRowCount(0)

        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM inventory WHERE name LIKE ?',
                       (f'%{search_term}%',))
        items = cursor.fetchall()

        for row_num, item in enumerate(items):
            self.table.insertRow(row_num)
            for col_num, value in enumerate(item):
                if col_num < 6:  # Skip created_at column
                    if isinstance(value, float):
                        value = f"${value:.2f}"
                    cell = QTableWidgetItem(str(value))
                    cell.setFlags(cell.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.table.setItem(row_num, col_num, cell)

        conn.close()
        self.table.resizeColumnsToContents()


class AddItemDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Item")
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()

        self.name_input = QLineEdit()
        self.quantity_input = QLineEdit()
        self.price_input = QLineEdit()
        self.location_input = QLineEdit()

        layout.addRow("Name:", self.name_input)
        layout.addRow("Quantity:", self.quantity_input)
        layout.addRow("Price ($):", self.price_input)
        layout.addRow("Location:", self.location_input)

        button_box = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")

        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        button_box.addWidget(save_button)
        button_box.addWidget(cancel_button)
        layout.addRow(button_box)

        self.setLayout(layout)

    def get_item_data(self):
        return {
            'name': self.name_input.text(),
            'quantity': self.quantity_input.text(),
            'price': self.price_input.text(),
            'location': self.location_input.text()
        }


class UpdateItemDialog(QDialog):
    def __init__(self, item_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Update Item")
        self.item_data = item_data
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()

        self.name_input = QLineEdit(self.item_data['name'])
        self.quantity_input = QLineEdit(str(self.item_data['quantity']))
        self.price_input = QLineEdit(str(self.item_data['price']))
        self.location_input = QLineEdit(self.item_data['location'])

        layout.addRow("Name:", self.name_input)
        layout.addRow("Quantity:", self.quantity_input)
        layout.addRow("Price ($):", self.price_input)
        layout.addRow("Location:", self.location_input)

        button_box = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")

        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        button_box.addWidget(save_button)
        button_box.addWidget(cancel_button)
        layout.addRow(button_box)

        self.setLayout(layout)

    def get_item_data(self):
        return {
            'name': self.name_input.text(),
            'quantity': self.quantity_input.text(),
            'price': self.price_input.text(),
            'location': self.location_input.text()
        }
