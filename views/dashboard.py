from database.main import Database
import sqlite3

db = Database()


def display_dashboard():
    while True:
        print("\n" + "="*50)
        print(" "*20 + "DASHBOARD")
        print("="*50)
        print("\n1. View Key Metrics")
        print("2. Sales Analysis")
        print("3. Inventory Status")
        print("4. Returns Overview")
        print("5. Low Stock Alert")
        print("6. Return to main menu")

        choice = input("\nEnter your choice (1-6): ")

        if choice == '1':
            display_key_metrics()
        elif choice == '2':
            sales_analysis()
        elif choice == '3':
            inventory_status()
        elif choice == '4':
            returns_overview()
        elif choice == '5':
            low_stock_alert()
        elif choice == '6':
            break
        else:
            print("Invalid choice. Please try again.")

        input("\nPress Enter to continue...")


def display_key_metrics():
    try:
        conn = db.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT SUM(total_amount) FROM sales')
        total_sales = cursor.fetchone()[0] or 0

        cursor.execute('SELECT COUNT(*), SUM(quantity) FROM inventory')
        inventory_data = cursor.fetchone()
        total_items = inventory_data[0] or 0
        total_stock = inventory_data[1] or 0

        cursor.execute('SELECT COUNT(*), SUM(refund_amount) FROM returns')
        returns_data = cursor.fetchone()
        total_returns = returns_data[0] or 0
        total_refunds = returns_data[1] or 0

        cursor.execute('SELECT COUNT(*) FROM inventory WHERE quantity < 10')
        low_stock = cursor.fetchone()[0] or 0

        print("\n" + "="*50)
        print(" "*18 + "KEY METRICS")
        print("="*50)
        print(f"\nTotal Sales Revenue: ${total_sales:,.2f}")
        print(f"Total Inventory Items: {total_items}")
        print(f"Total Stock Quantity: {total_stock}")
        print(f"Total Returns: {total_returns}")
        print(f"Total Refunds: ${total_refunds:,.2f}")
        print(f"Low Stock Items: {low_stock}")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()


def sales_analysis():
    try:
        conn = db.get_connection()
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

        print("\n" + "="*50)
        print(" "*17 + "SALES ANALYSIS")
        print("="*50)

        print("\nDaily Sales (Last 7 Days):")
        print("-" * 60)
        print("Date       | Number of Sales | Total Revenue")
        print("-" * 60)
        for day in daily_sales:
            print(f"{day[0]} | {day[1]:14d} | ${day[2]:12,.2f}")

        print("\nTop 5 Selling Items:")
        print("-" * 60)
        print("Item Name        | Quantity Sold | Total Revenue")
        print("-" * 60)
        for item in top_items:
            print(f"{item[0]:<15} | {item[1]:12d} | ${item[2]:12,.2f}")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()


def inventory_status():
    try:
        conn = db.get_connection()
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

        cursor.execute('''
            SELECT name, quantity, location
            FROM inventory
            WHERE quantity < 10
            ORDER BY quantity
        ''')
        restock_items = cursor.fetchall()

        print("\n" + "="*50)
        print(" "*16 + "INVENTORY STATUS")
        print("="*50)

        print("\nInventory by Location:")
        print("-" * 70)
        print("Location    | Item Count | Total Quantity | Total Value")
        print("-" * 70)
        for loc in location_summary:
            print(
                f"{loc[0]:<11} | {loc[1]:10d} | {loc[2]:14d} | ${loc[3]:11,.2f}")

        print("\nItems Needing Restock (Quantity < 10):")
        print("-" * 50)
        print("Item Name        | Quantity | Location")
        print("-" * 50)
        for item in restock_items:
            print(f"{item[0]:<15} | {item[1]:8d} | {item[2]}")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()


def returns_overview():
    try:
        conn = db.get_connection()
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

        print("\n" + "="*50)
        print(" "*16 + "RETURNS OVERVIEW")
        print("="*50)

        print("\nDaily Returns (Last 7 Days):")
        print("-" * 60)
        print("Date       | Number of Returns | Total Refunds")
        print("-" * 60)
        for day in daily_returns:
            print(f"{day[0]} | {day[1]:16d} | ${day[2]:12,.2f}")

        print("\nMost Returned Items:")
        print("-" * 60)
        print("Item Name        | Return Count | Total Refunds")
        print("-" * 60)
        for item in most_returned:
            print(f"{item[0]:<15} | {item[1]:12d} | ${item[2]:12,.2f}")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()


def low_stock_alert():
    try:
        conn = db.get_connection()
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

        print("\n" + "="*50)
        print(" "*16 + "LOW STOCK ALERT")
        print("="*50)

        if not low_stock_items:
            print("\nNo items are currently low in stock.")
        else:
            print("\nItems with Low Stock (Quantity < 10):")
            print("-" * 85)
            print("Item Name        | Quantity | Price    | Location    | Last Updated")
            print("-" * 85)
            for item in low_stock_items:
                print(
                    f"{item[0]:<15} | {item[1]:8d} | ${item[2]:7.2f} | {item[3]:<10} | {item[4]}")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()
