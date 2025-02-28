from database.main import Database


class InventoryDAO:
    def __init__(self):
        self.db = Database()

    def get_all_items(self):
        query = """
        SELECT id, name, quantity, price, location, updated_at
        FROM inventory
        ORDER BY id DESC
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def add_item(self, name, quantity, price, location):
        query = """
        INSERT INTO inventory (name, quantity, price, location, 
                             created_at, updated_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """
        conn = self.db.get_connection()
        try:
            conn.execute(query, (name, quantity, price, location))
            conn.commit()
        finally:
            conn.close()

    def update_item(self, item_id, name, quantity, price, location):
        query = """
        UPDATE inventory
        SET name = ?, quantity = ?, price = ?, location = ?, 
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """
        conn = self.db.get_connection()
        try:
            conn.execute(query, (name, quantity, price, location, item_id))
            conn.commit()
        finally:
            conn.close()

    def delete_item(self, item_id):
        query = "DELETE FROM inventory WHERE id = ?"
        conn = self.db.get_connection()
        try:
            conn.execute(query, (item_id,))
            conn.commit()
        finally:
            conn.close()

    def search_items(self, search_term):
        query = """
        SELECT id, name, quantity, price, location, updated_at
        FROM inventory
        WHERE name LIKE ? OR location LIKE ?
        ORDER BY id DESC
        """
        search_pattern = f"%{search_term}%"
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, (search_pattern, search_pattern))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
