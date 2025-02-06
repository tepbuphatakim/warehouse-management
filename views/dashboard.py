from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QLabel, QPushButton, QTabWidget, QTableWidget, QTableWidgetItem,
                             QGridLayout, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from database.main import Database
import sqlite3


class DashboardPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Retail Dashboard")
        self.setMinimumSize(1200, 600)
        self.db = Database()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)

        tab_widget.addTab(KeyMetricsPage(self.db), "Key Metrics")
        tab_widget.addTab(SalesAnalysisPage(self.db), "Sales Analysis")
        tab_widget.addTab(InventoryPage(self.db), "Inventory")
        tab_widget.addTab(ReturnsPage(self.db), "Returns")
        tab_widget.addTab(LowStockPage(self.db), "Low Stock")


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


class KeyMetricsPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        layout = QGridLayout(self)

        metrics = self.get_key_metrics()

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

    def get_key_metrics(self):
        metrics = {}
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT SUM(total_amount) FROM sales')
            metrics['total_sales'] = cursor.fetchone()[0] or 0

            cursor.execute('SELECT COUNT(*), SUM(quantity) FROM inventory')
            inventory_data = cursor.fetchone()
            metrics['total_items'] = inventory_data[0] or 0
            metrics['total_stock'] = inventory_data[1] or 0

            cursor.execute('SELECT COUNT(*), SUM(refund_amount) FROM returns')
            returns_data = cursor.fetchone()
            metrics['total_returns'] = returns_data[0] or 0
            metrics['total_refunds'] = returns_data[1] or 0

            cursor.execute(
                'SELECT COUNT(*) FROM inventory WHERE quantity < 10')
            metrics['low_stock'] = cursor.fetchone()[0] or 0

        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()

        return metrics


class SalesAnalysisPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
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
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT 
                    DATE(sale_date) as sale_day,
                    COUNT(*) as num_sales,
                    SUM(total_amount) as total_revenue
                FROM sales
                WHERE sale_date >= DATE('now', '-7 days')
                GROUP BY sale_day
                ORDER BY sale_day
            ''')
            daily_sales = cursor.fetchall()

            table.setRowCount(len(daily_sales))
            for i, row in enumerate(daily_sales):
                table.setItem(i, 0, QTableWidgetItem(str(row[0])))
                table.setItem(i, 1, QTableWidgetItem(str(row[1])))
                table.setItem(i, 2, QTableWidgetItem(f"${row[2]:,.2f}"))

        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()

    def populate_top_items(self, table):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT 
                    i.name,
                    SUM(s.quantity) as total_quantity,
                    SUM(s.total_amount) as total_revenue
                FROM sales s
                JOIN inventory i ON s.item_id = i.id
                GROUP BY i.id
                ORDER BY total_revenue DESC
                LIMIT 5
            ''')
            top_items = cursor.fetchall()

            table.setRowCount(len(top_items))
            for i, row in enumerate(top_items):
                table.setItem(i, 0, QTableWidgetItem(row[0]))
                table.setItem(i, 1, QTableWidgetItem(str(row[1])))
                table.setItem(i, 2, QTableWidgetItem(f"${row[2]:,.2f}"))

        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()


class InventoryPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
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
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT 
                    location,
                    COUNT(*) as item_count,
                    SUM(quantity) as total_quantity,
                    SUM(quantity * price) as total_value
                FROM inventory
                GROUP BY location
            ''')
            location_summary = cursor.fetchall()

            table.setRowCount(len(location_summary))
            for i, row in enumerate(location_summary):
                table.setItem(i, 0, QTableWidgetItem(row[0]))
                table.setItem(i, 1, QTableWidgetItem(str(row[1])))
                table.setItem(i, 2, QTableWidgetItem(str(row[2])))
                table.setItem(i, 3, QTableWidgetItem(f"${row[3]:,.2f}"))

        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()

    def populate_restock_items(self, table):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT name, quantity, location
                FROM inventory
                WHERE quantity < 10
                ORDER BY quantity
            ''')
            restock_items = cursor.fetchall()

            table.setRowCount(len(restock_items))
            for i, row in enumerate(restock_items):
                table.setItem(i, 0, QTableWidgetItem(row[0]))
                table.setItem(i, 1, QTableWidgetItem(str(row[1])))
                table.setItem(i, 2, QTableWidgetItem(row[2]))

        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()


class ReturnsPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
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
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT 
                    DATE(return_date) as return_day,
                    COUNT(*) as num_returns,
                    SUM(refund_amount) as total_refunds
                FROM returns
                WHERE return_date >= DATE('now', '-7 days')
                GROUP BY return_day
                ORDER BY return_day
            ''')
            daily_returns = cursor.fetchall()

            table.setRowCount(len(daily_returns))
            for i, row in enumerate(daily_returns):
                table.setItem(i, 0, QTableWidgetItem(str(row[0])))
                table.setItem(i, 1, QTableWidgetItem(str(row[1])))
                table.setItem(i, 2, QTableWidgetItem(f"${row[2]:,.2f}"))

        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()

    def populate_most_returned(self, table):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT 
                    i.name,
                    COUNT(*) as return_count,
                    SUM(r.refund_amount) as total_refunds
                FROM returns r
                JOIN inventory i ON r.item_id = i.id
                GROUP BY i.id
                ORDER BY return_count DESC
                LIMIT 5
            ''')
            most_returned = cursor.fetchall()

            table.setRowCount(len(most_returned))
            for i, row in enumerate(most_returned):
                table.setItem(i, 0, QTableWidgetItem(row[0]))
                table.setItem(i, 1, QTableWidgetItem(str(row[1])))
                table.setItem(i, 2, QTableWidgetItem(f"${row[2]:,.2f}"))

        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()


class LowStockPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
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
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT 
                    name,
                    quantity,
                    price,
                    location,
                    updated_at
                FROM inventory
                WHERE quantity < 10
                ORDER BY quantity
            ''')
            low_stock_items = cursor.fetchall()

            self.low_stock_table.setRowCount(len(low_stock_items))
            for i, row in enumerate(low_stock_items):
                self.low_stock_table.setItem(i, 0, QTableWidgetItem(row[0]))
                self.low_stock_table.setItem(
                    i, 1, QTableWidgetItem(str(row[1])))
                self.low_stock_table.setItem(
                    i, 2, QTableWidgetItem(f"${row[2]:.2f}"))
                self.low_stock_table.setItem(i, 3, QTableWidgetItem(row[3]))
                self.low_stock_table.setItem(
                    i, 4, QTableWidgetItem(str(row[4])))

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

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            self.low_stock_table.setRowCount(1)
            self.low_stock_table.setSpan(0, 0, 1, 5)
            self.low_stock_table.setItem(0, 0,
                                         QTableWidgetItem(f"Error loading data: {str(e)}"))
        finally:
            conn.close()
