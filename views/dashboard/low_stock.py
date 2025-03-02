from PyQt6.QtWidgets import (QWidget, QVBoxLayout,
                             QLabel, QPushButton, QTableWidget, QTableWidgetItem)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from dao.dashboard_dao import DashboardDAO

class LowStockPage(QWidget):
    def __init__(self):
        super().__init__()
        self.dashboard_dao = DashboardDAO()
        layout = QVBoxLayout(self)

        header_label = QLabel("Low Stock Items Alert")
        header_label.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        layout.addWidget(header_label)

        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_data)
        layout.addWidget(refresh_button)

        self.low_stock_table = QTableWidget()
        self.low_stock_table.setColumnCount(5)
        self.low_stock_table.setHorizontalHeaderLabels([
            "Item Name", "Quantity", "Price", "Location", "Last Updated"
        ])
        layout.addWidget(self.low_stock_table)

        self.refresh_data()

    def refresh_data(self):
        try:
            low_stock_items = self.dashboard_dao.get_low_stock_items()

            self.low_stock_table.setRowCount(len(low_stock_items))
            for i, row in enumerate(low_stock_items):
                self.low_stock_table.setItem(i, 0, QTableWidgetItem(row[0]))  # name
                self.low_stock_table.setItem(i, 1, QTableWidgetItem(str(row[1])))  # quantity
                self.low_stock_table.setItem(i, 2, QTableWidgetItem(f"${row[2]:.2f}"))  # price
                self.low_stock_table.setItem(i, 3, QTableWidgetItem(row[3]))  # location
                self.low_stock_table.setItem(i, 4, QTableWidgetItem(str(row[4])))  # updated_at

                # Highlight critical items (quantity < 5) in red
                if row[1] < 5:
                    for col in range(5):
                        item = self.low_stock_table.item(i, col)
                        item.setBackground(Qt.GlobalColor.red)
                        item.setForeground(Qt.GlobalColor.white)

            # Adjust column widths
            self.low_stock_table.resizeColumnsToContents()

            if len(low_stock_items) == 0:
                self.low_stock_table.setRowCount(1)
                self.low_stock_table.setSpan(0, 0, 1, 5)
                self.low_stock_table.setItem(0, 0,
                                           QTableWidgetItem("No items are currently low in stock"))

        except Exception as e:
            print(f"Database error: {e}")
            self.low_stock_table.setRowCount(1)
            self.low_stock_table.setSpan(0, 0, 1, 5)
            self.low_stock_table.setItem(0, 0,
                                       QTableWidgetItem(f"Error loading data: {str(e)}"))
