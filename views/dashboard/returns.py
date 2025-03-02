from PyQt6.QtWidgets import (QWidget, QVBoxLayout,
                             QLabel, QTableWidget, QTableWidgetItem)
from PyQt6.QtGui import QFont
from dao.dashboard_dao import DashboardDAO

class ReturnsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.dashboard_dao = DashboardDAO()
        layout = QVBoxLayout(self)

        daily_returns_label = QLabel("Daily Returns (Last 7 Days)")
        daily_returns_label.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        layout.addWidget(daily_returns_label)

        daily_returns_table = QTableWidget()
        daily_returns_table.setColumnCount(3)
        daily_returns_table.setHorizontalHeaderLabels(
            ["Date", "Number of Returns", "Total Refunds"])
        self.populate_daily_returns(daily_returns_table)
        layout.addWidget(daily_returns_table)

        most_returned_label = QLabel("Most Returned Items")
        most_returned_label.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        layout.addWidget(most_returned_label)

        most_returned_table = QTableWidget()
        most_returned_table.setColumnCount(3)
        most_returned_table.setHorizontalHeaderLabels(
            ["Item Name", "Return Count", "Total Refunds"])
        self.populate_most_returned(most_returned_table)
        layout.addWidget(most_returned_table)

    def populate_daily_returns(self, table):
        try:
            daily_returns = self.dashboard_dao.get_daily_returns()
            
            table.setRowCount(len(daily_returns))
            for i, row in enumerate(daily_returns):
                table.setItem(i, 0, QTableWidgetItem(str(row[0])))
                table.setItem(i, 1, QTableWidgetItem(str(row[1])))
                table.setItem(i, 2, QTableWidgetItem(f"${row[2]:,.2f}"))

        except Exception as e:
            print(f"Error populating daily returns: {e}")

    def populate_most_returned(self, table):
        try:
            most_returned = self.dashboard_dao.get_most_returned_items()
            
            table.setRowCount(len(most_returned))
            for i, row in enumerate(most_returned):
                table.setItem(i, 0, QTableWidgetItem(row[0]))  # name
                table.setItem(i, 1, QTableWidgetItem(str(row[1])))  # return_count
                table.setItem(i, 2, QTableWidgetItem(f"${row[2]:,.2f}"))  # total_refunds

        except Exception as e:
            print(f"Error populating most returned items: {e}")