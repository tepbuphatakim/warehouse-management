from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget)
from views.dashboard.sales_analysis import SalesAnalysisPage
from views.dashboard.inventory import InventoryPage
from views.dashboard.returns import ReturnsPage
from views.dashboard.low_stock import LowStockPage
from views.dashboard.key_metrics import KeyMetricsPage


class DashboardPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Retail Dashboard")
        self.setMinimumSize(1200, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)

        tab_widget.addTab(KeyMetricsPage(), "Key Metrics")
        tab_widget.addTab(SalesAnalysisPage(), "Sales Analysis")
        tab_widget.addTab(InventoryPage(), "Inventory")
        tab_widget.addTab(ReturnsPage(), "Returns")
        tab_widget.addTab(LowStockPage(), "Low Stock")
