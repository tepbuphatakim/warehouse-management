import sys
from PyQt6.QtWidgets import (QMainWindow, QApplication, QWidget,
                             QToolBar, QStatusBar, QLabel, QVBoxLayout,
                             QStackedWidget)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QSize

from views.inventory.inventory import InventoryPage
from views.sale.sale import SaleManagementPage
from views.return_items.return_items import ReturnItemsPage
from views.dashboard.dashboard import DashboardPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Warehouse Management System")
        self.setGeometry(100, 100, 1200, 600)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)

        self.create_pages()
        self.create_main_toolbar()

    def create_main_toolbar(self):
        main_toolbar = QToolBar("Main Toolbar")
        main_toolbar.setIconSize(QSize(32, 32))
        main_toolbar.setMovable(False)  # Lock toolbar position
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, main_toolbar)

        actions = [
            ("Dashboard", "View dashboard and statistics", 0),
            ("Inventory", "Manage inventory items", 1),
            ("Sales", "Process sales and view history", 2),
            ("Returns", "Handle return items", 3),
            ("Exit", "Exit application", -1)
        ]

        for text, tip, index in actions:
            action = QAction(text, self)
            action.setStatusTip(tip)
            if index == -1:  # Exit action
                action.triggered.connect(self.close)
            else:
                action.triggered.connect(lambda x, i=index: self.show_page(i))
            main_toolbar.addAction(action)
            main_toolbar.addSeparator()

    def create_pages(self):
        self.dashboard_page = DashboardPage()
        self.inventory_page = InventoryPage()
        self.sales_page = SaleManagementPage()
        self.returns_page = ReturnItemsPage()

        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.inventory_page)
        self.stacked_widget.addWidget(self.sales_page)
        self.stacked_widget.addWidget(self.returns_page)

    def show_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        page_names = ["Dashboard", "Inventory",
                      "Sale Management", "Return Items"]
        self.status_bar.showMessage(f"Viewing {page_names[index]}", 2000)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
