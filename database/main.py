import sqlite3
# from datetime import datetime

class Database:
    def __init__(self, db_name="warehouse.db"):
        self.db_name = db_name
        self.init_database()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Create inventory table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                location TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()
