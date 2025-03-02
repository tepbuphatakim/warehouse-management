from database.main import Database


class DashboardDAO:
    def __init__(self):
        self.db = Database()

    def get_key_metrics(self):
        query = """
        WITH metrics AS (
            SELECT 
                (SELECT SUM(total_amount) FROM sales) as total_sales,
                (SELECT COUNT(*) FROM inventory) as total_items,
                (SELECT SUM(quantity) FROM inventory) as total_stock,
                (SELECT COUNT(*) FROM returns) as total_returns,
                (SELECT SUM(refund_amount) FROM returns) as total_refunds,
                (SELECT COUNT(*) FROM inventory WHERE quantity < 10) as low_stock
        )
        SELECT 
            COALESCE(total_sales, 0) as total_sales,
            COALESCE(total_items, 0) as total_items,
            COALESCE(total_stock, 0) as total_stock,
            COALESCE(total_returns, 0) as total_returns,
            COALESCE(total_refunds, 0) as total_refunds,
            COALESCE(low_stock, 0) as low_stock
        FROM metrics
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            result = cursor.fetchone()
            return {
                'total_sales': result[0],
                'total_items': result[1],
                'total_stock': result[2],
                'total_returns': result[3],
                'total_refunds': result[4],
                'low_stock': result[5]
            }
        finally:
            cursor.close()
            conn.close()

    def get_daily_sales(self):
        query = """
        SELECT 
            DATE(sale_date) as sale_day,
            COUNT(*) as num_sales,
            SUM(total_amount) as total_revenue
        FROM sales
        WHERE sale_date >= DATE('now', '-7 days')
        GROUP BY sale_day
        ORDER BY sale_day
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def get_top_selling_items(self):
        query = """
        SELECT 
            i.name,
            SUM(s.quantity) as total_quantity,
            SUM(s.total_amount) as total_revenue
        FROM sales s
        JOIN inventory i ON s.item_id = i.id
        GROUP BY i.id
        ORDER BY total_revenue DESC
        LIMIT 5
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def get_inventory_by_location(self):
        query = """
        SELECT 
            location,
            COUNT(*) as item_count,
            SUM(quantity) as total_quantity,
            SUM(quantity * price) as total_value
        FROM inventory
        GROUP BY location
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def get_restock_items(self):
        query = """
        SELECT name, quantity, location
        FROM inventory
        WHERE quantity < 10
        ORDER BY quantity
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def get_daily_returns(self):
        query = """
        SELECT 
            DATE(return_date) as return_day,
            COUNT(*) as num_returns,
            SUM(refund_amount) as total_refunds
        FROM returns
        WHERE return_date >= DATE('now', '-7 days')
        GROUP BY return_day
        ORDER BY return_day
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def get_most_returned_items(self):
        query = """
        SELECT 
            i.name,
            COUNT(*) as return_count,
            SUM(r.refund_amount) as total_refunds
        FROM returns r
        JOIN inventory i ON r.item_id = i.id
        GROUP BY i.id
        ORDER BY return_count DESC
        LIMIT 5
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def get_low_stock_items(self):
        query = """
        SELECT 
            name,
            quantity,
            price,
            location,
            updated_at
        FROM inventory
        WHERE quantity < 10
        ORDER BY quantity
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
