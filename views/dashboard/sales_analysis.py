from PyQt6.QtWidgets import (QWidget, QVBoxLayout,
                             QLabel, QTableWidget, QTableWidgetItem)
from PyQt6.QtGui import QFont
from dao.dashboard_dao import DashboardDAO

class SalesAnalysisPage(QWidget):
    def __init__(self):
        super().__init__()
        self.dashboard_dao = DashboardDAO()
        layout = QVBoxLayout(self)

        # Daily sales table
        daily_sales_label = QLabel("Daily Sales (Last 7 Days)")
        daily_sales_label.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        layout.addWidget(daily_sales_label)

        daily_sales_table = QTableWidget()
        daily_sales_table.setColumnCount(3)
        daily_sales_table.setHorizontalHeaderLabels(
            ["Date", "Number of Sales", "Total Revenue"])
        self.populate_daily_sales(daily_sales_table)
        layout.addWidget(daily_sales_table)

        # Top items table
        top_items_label = QLabel("Top 5 Selling Items")
        top_items_label.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        layout.addWidget(top_items_label)

        top_items_table = QTableWidget()
        top_items_table.setColumnCount(3)
        top_items_table.setHorizontalHeaderLabels(
            ["Item Name", "Quantity Sold", "Total Revenue"])
        self.populate_top_items(top_items_table)
        layout.addWidget(top_items_table)
        
    def populate_daily_sales(self, table):
        try:
            daily_sales = self.dashboard_dao.get_daily_sales()
            
            table.setRowCount(len(daily_sales))
            for i, row in enumerate(daily_sales):
                table.setItem(i, 0, QTableWidgetItem(str(row[0])))
                table.setItem(i, 1, QTableWidgetItem(str(row[1])))
                table.setItem(i, 2, QTableWidgetItem(f"${row[2]:,.2f}"))

        except Exception as e:
            print(f"Error populating daily sales: {e}")

    def populate_top_items(self, table):
        try:
            top_items = self.dashboard_dao.get_top_selling_items()
            
            table.setRowCount(len(top_items))
            for i, row in enumerate(top_items):
                table.setItem(i, 0, QTableWidgetItem(row[0]))
                table.setItem(i, 1, QTableWidgetItem(str(row[1])))
                table.setItem(i, 2, QTableWidgetItem(f"${row[2]:,.2f}"))

        except Exception as e:
            print(f"Error populating top items: {e}")