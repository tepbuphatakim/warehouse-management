from datetime import datetime
import sqlite3
from database.main import Database


class ReturnItemsDAO:
    def __init__(self):
        self.db = Database()

    def get_all_returns(self):
        """Fetch all returns ordered by return date"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT r.id, i.name, r.quantity, r.refund_amount, r.reason, r.return_date
                FROM returns r
                JOIN inventory i ON r.item_id = i.id
                ORDER BY r.return_date DESC
            ''')
            returns = cursor.fetchall()
            conn.close()
            return returns

        except sqlite3.Error as e:
            raise Exception(f"Database error: {str(e)}")

    def search_returns(self, search_type, search_term):
        """Search returns by date or item name
        
        Args:
            search_type (str): Type of search ('Date' or 'Item Name')
            search_term (str): The search term to filter by
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            base_query = '''
                SELECT r.id, i.name, r.quantity, r.refund_amount, r.reason, r.return_date
                FROM returns r
                JOIN inventory i ON r.item_id = i.id
            '''

            if search_type == 'Date':
                query = base_query + ' WHERE DATE(r.return_date) = ?'
                cursor.execute(query + ' ORDER BY r.return_date DESC', (search_term,))
            else:  # Item Name
                query = base_query + ' WHERE i.name LIKE ?'
                cursor.execute(query + ' ORDER BY r.return_date DESC', (f'%{search_term}%',))

            returns = cursor.fetchall()
            conn.close()
            return returns

        except sqlite3.Error as e:
            raise Exception(f"Database error: {str(e)}")

    def get_recent_sales(self, limit=10):
        """Fetch recent sales for returns processing"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT s.id, i.name, s.quantity, s.unit_price, s.total_amount, s.sale_date
                FROM sales s
                JOIN inventory i ON s.item_id = i.id
                ORDER BY s.sale_date DESC
                LIMIT ?
            ''', (limit,))
            sales = cursor.fetchall()
            conn.close()
            return sales

        except sqlite3.Error as e:
            raise Exception(f"Database error: {str(e)}")

    def process_return(self, sale_id, return_quantity, refund_amount, reason):
        """Process a return transaction"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Get item_id from sale
            cursor.execute('SELECT item_id FROM sales WHERE id = ?', (sale_id,))
            item_id = cursor.fetchone()[0]

            # Insert return record
            cursor.execute('''
                INSERT INTO returns (sale_id, item_id, quantity, refund_amount, reason, return_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (sale_id, item_id, return_quantity, refund_amount, reason, current_time))

            # Update inventory quantity
            cursor.execute('''
                UPDATE inventory 
                SET quantity = quantity + ?,
                    updated_at = ?
                WHERE id = ?
            ''', (return_quantity, current_time, item_id))

            conn.commit()
            conn.close()
            return True

        except sqlite3.Error as e:
            raise Exception(f"Database error: {str(e)}")
