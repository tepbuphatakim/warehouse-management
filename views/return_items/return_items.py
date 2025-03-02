from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QLineEdit, QTableWidget,
                             QTableWidgetItem, QMessageBox, QDialog,
                             QComboBox, QTabWidget)
from PyQt6.QtCore import Qt
from dao.return_items_dao import ReturnItemsDAO
from views.return_items.process_return_dialog import ProcessReturnDialog


class ReturnItemsPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.return_items_dao = ReturnItemsDAO()
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
            returns = self.return_items_dao.get_all_returns()
            
            self.returns_table.setRowCount(len(returns))
            for row, return_item in enumerate(returns):
                for col, value in enumerate(return_item):
                    if isinstance(value, float):
                        value = f"${value:.2f}"
                    cell = QTableWidgetItem(str(value))
                    cell.setFlags(cell.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.returns_table.setItem(row, col, cell)

            self.returns_table.resizeColumnsToContents()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def process_return(self):
        dialog = ProcessReturnDialog(self.return_items_dao, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_returns_history()

    def search_returns(self):
        try:
            search_term = self.search_input.text()
            search_type = self.search_type.currentText()
            
            returns = self.return_items_dao.search_returns(search_type, search_term)

            self.search_table.setRowCount(len(returns))
            for row, return_item in enumerate(returns):
                for col, value in enumerate(return_item):
                    if isinstance(value, float):
                        value = f"${value:.2f}"
                    cell = QTableWidgetItem(str(value))
                    cell.setFlags(cell.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.search_table.setItem(row, col, cell)

            self.search_table.resizeColumnsToContents()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
