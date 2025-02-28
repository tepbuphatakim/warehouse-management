from database.main import Database


class SaleDAO:
    def __init__(self):
        self.db = Database()

    def get_all_sales(self):
        query = """
        SELECT s.id, i.name, s.quantity, s.unit_price, s.total_amount, s.sale_date
        FROM sales s
        JOIN inventory i ON s.item_id = i.id
        ORDER BY s.sale_date DESC
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def search_sales_by_date(self, date):
        query = """
        SELECT s.id, i.name, s.quantity, s.unit_price, s.total_amount, s.sale_date
        FROM sales s
        JOIN inventory i ON s.item_id = i.id
        WHERE DATE(s.sale_date) = ?
        ORDER BY s.sale_date DESC
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, (date,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def search_sales_by_item_name(self, item_name):
        query = """
        SELECT s.id, i.name, s.quantity, s.unit_price, s.total_amount, s.sale_date
        FROM sales s
        JOIN inventory i ON s.item_id = i.id
        WHERE i.name LIKE ?
        ORDER BY s.sale_date DESC
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, (f'%{item_name}%',))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def get_available_items(self):
        query = "SELECT id, name, quantity, price FROM inventory WHERE quantity > 0"
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def record_sale(self, item_id, quantity, unit_price):
        total_amount = quantity * unit_price
        sale_query = """
        INSERT INTO sales (item_id, quantity, unit_price, total_amount, sale_date)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """
        inventory_query = """
        UPDATE inventory 
        SET quantity = quantity - ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """
        conn = self.db.get_connection()
        try:
            conn.execute(sale_query, (item_id, quantity, unit_price, total_amount))
            conn.execute(inventory_query, (quantity, item_id))
            conn.commit()
            return True
        finally:
            conn.close()

    def generate_report(self, date, report_type):
        query = """
        SELECT 
            i.name,
            SUM(s.quantity) as total_quantity,
            SUM(s.total_amount) as total_sales
        FROM sales s
        JOIN inventory i ON s.item_id = i.id
        WHERE {} = ?
        GROUP BY i.name
        """
        
        if report_type == "Daily Report":
            date_filter = "DATE(s.sale_date)"
        else:
            date_filter = "strftime('%Y-%m', s.sale_date)"
            date = date[:7]
            
        query = query.format(date_filter)
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, (date,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
