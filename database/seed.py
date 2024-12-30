from main import Database
from datetime import datetime, timedelta

def seed_database():
    db = Database()
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM returns')
    cursor.execute('DELETE FROM sales')
    cursor.execute('DELETE FROM inventory')

    # Reset auto-increment
    cursor.execute(
        'DELETE FROM sqlite_sequence WHERE name IN ("inventory", "sales", "returns")')

    inventory_data = [
        ('Laptop', 15, 999.99, 'Electronics-A1',
         '2024-01-01 08:00:00', '2024-01-01 08:00:00'),
        ('Smartphone', 25, 599.99, 'Electronics-A2',
         '2024-01-01 08:00:00', '2024-01-01 08:00:00'),
        ('Headphones', 40, 89.99, 'Electronics-B1',
         '2024-01-01 08:00:00', '2024-01-01 08:00:00'),
        ('Monitor', 20, 299.99, 'Electronics-A3',
         '2024-01-01 08:00:00', '2024-01-01 08:00:00'),
        ('Keyboard', 30, 49.99, 'Electronics-B2',
         '2024-01-01 08:00:00', '2024-01-01 08:00:00'),
        ('Mouse', 45, 29.99, 'Electronics-B2',
         '2024-01-01 08:00:00', '2024-01-01 08:00:00'),
        ('Tablet', 18, 449.99, 'Electronics-A2',
         '2024-01-01 08:00:00', '2024-01-01 08:00:00'),
        ('Printer', 12, 199.99, 'Electronics-C1',
         '2024-01-01 08:00:00', '2024-01-01 08:00:00'),
        ('Speaker', 25, 79.99, 'Electronics-B3',
         '2024-01-01 08:00:00', '2024-01-01 08:00:00'),
        ('Camera', 15, 349.99, 'Electronics-C2',
         '2024-01-01 08:00:00', '2024-01-01 08:00:00')
    ]

    cursor.executemany('''
        INSERT INTO inventory (name, quantity, price, location, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', inventory_data)

    base_date = datetime.now() - timedelta(days=30)
    sales_data = [
        (1, 2, 999.99, 1999.98, base_date + timedelta(days=2)),
        (2, 3, 599.99, 1799.97, base_date + timedelta(days=3)),
        (3, 5, 89.99, 449.95, base_date + timedelta(days=5)),
        (4, 2, 299.99, 599.98, base_date + timedelta(days=7)),
        (5, 4, 49.99, 199.96, base_date + timedelta(days=10)),
        (6, 6, 29.99, 179.94, base_date + timedelta(days=12)),
        (7, 1, 449.99, 449.99, base_date + timedelta(days=15)),
        (8, 2, 199.99, 399.98, base_date + timedelta(days=18)),
        (9, 3, 79.99, 239.97, base_date + timedelta(days=20)),
        (10, 2, 349.99, 699.98, base_date + timedelta(days=22))
    ]

    cursor.executemany('''
        INSERT INTO sales (item_id, quantity, unit_price, total_amount, sale_date)
        VALUES (?, ?, ?, ?, ?)
    ''', sales_data)

    returns_data = [
        (1, 1, 1, 999.99, 'Defective product', base_date + timedelta(days=4)),
        (2, 2, 1, 599.99, 'Wrong model', base_date + timedelta(days=5)),
        (3, 3, 2, 179.98, 'Not satisfied', base_date + timedelta(days=7)),
        (4, 4, 1, 299.99, 'Display issues', base_date + timedelta(days=9)),
        (5, 5, 2, 99.98, 'Double order', base_date + timedelta(days=12)),
        (6, 6, 3, 89.97, 'Changed mind', base_date + timedelta(days=14)),
        (7, 7, 1, 449.99, 'Performance issues', base_date + timedelta(days=17)),
        (8, 8, 1, 199.99, 'Compatibility issues', base_date + timedelta(days=20)),
        (9, 9, 2, 159.98, 'Better deal elsewhere', base_date + timedelta(days=22)),
        (10, 10, 1, 349.99, 'Gift return', base_date + timedelta(days=24))
    ]

    cursor.executemany('''
        INSERT INTO returns (sale_id, item_id, quantity, refund_amount, reason, return_date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', returns_data)

    conn.commit()
    conn.close()

    print("Database seeded successfully!")
    print("\nSeed Data Summary:")
    print(f"Inventory Items: {len(inventory_data)}")
    print(f"Sales Records: {len(sales_data)}")
    print(f"Returns Records: {len(returns_data)}")
