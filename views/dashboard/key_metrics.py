from PyQt6.QtWidgets import (QWidget, QVBoxLayout,
                             QLabel,
                             QGridLayout, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from dao.dashboard_dao import DashboardDAO


class KeyMetricsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.dashboard_dao = DashboardDAO()
        layout = QGridLayout(self)

        metrics = self.dashboard_dao.get_key_metrics()

        layout.addWidget(MetricCard("Total Sales Revenue",
                         f"${metrics['total_sales']:,.2f}"), 0, 0)
        layout.addWidget(MetricCard("Total Inventory Items",
                         str(metrics['total_items'])), 0, 1)
        layout.addWidget(MetricCard("Total Stock Quantity",
                         str(metrics['total_stock'])), 0, 2)
        layout.addWidget(MetricCard(
            "Total Returns", str(metrics['total_returns'])), 1, 0)
        layout.addWidget(MetricCard(
            "Total Refunds", f"${metrics['total_refunds']:,.2f}"), 1, 1)
        layout.addWidget(MetricCard("Low Stock Items",
                         str(metrics['low_stock'])), 1, 2)


class MetricCard(QFrame):
    def __init__(self, title, value, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setStyleSheet(
            "background-color: white; border-radius: 10px; padding: 10px;")

        layout = QVBoxLayout(self)

        title_label = QLabel(title)
        title_label.setFont(QFont('Arial', 10))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        value_label = QLabel(value)
        value_label.setFont(QFont('Arial', 14, QFont.Weight.Bold))
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title_label)
        layout.addWidget(value_label)
