from PyQt6.QtWidgets import (QWidget, QVBoxLayout,
                             QLabel, QTableWidget, QTableWidgetItem)
from PyQt6.QtGui import QFont
from dao.dashboard_dao import DashboardDAO


class InventoryPage(QWidget):
    def __init__(self):
        super().__init__()
        self.dashboard_dao = DashboardDAO()
        layout = QVBoxLayout(self)

        location_label = QLabel("Inventory by Location")
        location_label.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        layout.addWidget(location_label)

        location_table = QTableWidget()
        location_table.setColumnCount(4)
        location_table.setHorizontalHeaderLabels(
            ["Location", "Item Count", "Total Quantity", "Total Value"])
        self.populate_location_summary(location_table)
        layout.addWidget(location_table)

        # Restock items table
        restock_label = QLabel("Items Needing Restock (Quantity < 10)")
        restock_label.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        layout.addWidget(restock_label)

        restock_table = QTableWidget()
        restock_table.setColumnCount(3)
        restock_table.setHorizontalHeaderLabels(
            ["Item Name", "Quantity", "Location"])
        self.populate_restock_items(restock_table)
        layout.addWidget(restock_table)

    def populate_location_summary(self, table):
        try:
            location_summary = self.dashboard_dao.get_inventory_by_location()

            table.setRowCount(len(location_summary))
            for i, row in enumerate(location_summary):
                table.setItem(i, 0, QTableWidgetItem(row[0]))
                table.setItem(i, 1, QTableWidgetItem(str(row[1])))
                table.setItem(i, 2, QTableWidgetItem(str(row[2])))
                table.setItem(i, 3, QTableWidgetItem(f"${row[3]:,.2f}"))

        except Exception as e:
            print(f"Error populating location summary: {e}")

    def populate_restock_items(self, table):
        try:
            restock_items = self.dashboard_dao.get_restock_items()

            table.setRowCount(len(restock_items))
            for i, row in enumerate(restock_items):
                table.setItem(i, 0, QTableWidgetItem(row[0]))  # name
                table.setItem(i, 1, QTableWidgetItem(str(row[1])))  # quantity
                table.setItem(i, 2, QTableWidgetItem(row[2]))  # location

        except Exception as e:
            print(f"Error populating restock items: {e}")
