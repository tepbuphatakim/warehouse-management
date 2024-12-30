from database.main import Database
import sqlite3
from datetime import datetime

db = Database()


def handle_sales():
    while True:
        print("\nSales Management:")
        print("1. Record new sale")
        print("2. View sales history")
        print("3. Search sales")
        print("4. Generate sales report")
        print("5. Return to main menu")

        choice = input("\nEnter your choice (1-5): ")

        if choice == '1':
            record_sale()
        elif choice == '2':
            view_sales_history()
        elif choice == '3':
            search_sales()
        elif choice == '4':
            generate_sales_report()
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")


def record_sale():
    print("\nRecord New Sale:")
    try:
        conn = db.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            'SELECT id, name, quantity, price FROM inventory WHERE quantity > 0')
        available_items = cursor.fetchall()

        if not available_items:
            print("No items available in inventory!")
            conn.close()
            return

        print("\nAvailable Items:")
        print("ID  |  Name  |  Quantity  |  Price")
        print("-" * 40)
        for item in available_items:
            print(f"{item[0]:3} | {item[1]:6} | {item[2]:9} | ${item[3]:6.2f}")

        item_id = int(input("\nEnter item ID: "))
        quantity = int(input("Enter quantity sold: "))

        cursor.execute(
            'SELECT quantity, price FROM inventory WHERE id = ?', (item_id,))
        item = cursor.fetchone()

        if not item:
            print("Item not found!")
            conn.close()
            return

        if item[0] < quantity:
            print("Insufficient quantity in inventory!")
            conn.close()
            return

        total_amount = quantity * item[1]
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute('''
            INSERT INTO sales (item_id, quantity, unit_price, total_amount, sale_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (item_id, quantity, item[1], total_amount, current_time))

        cursor.execute('''
            UPDATE inventory 
            SET quantity = quantity - ?,
                updated_at = ?
            WHERE id = ?
        ''', (quantity, current_time, item_id))

        conn.commit()
        print(
            f"\nSale recorded successfully! Total amount: ${total_amount:.2f}")

    except ValueError:
        print("Invalid input. Please enter numeric values.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()


def view_sales_history():
    try:
        conn = db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT s.id, i.name, s.quantity, s.unit_price, s.total_amount, s.sale_date
            FROM sales s
            JOIN inventory i ON s.item_id = i.id
            ORDER BY s.sale_date DESC
        ''')
        sales = cursor.fetchall()

        if not sales:
            print("\nNo sales records found.")
        else:
            print("\nSales History:")
            print("ID  |  Item  |  Quantity  |  Unit Price  |  Total  |  Sale Date")
            print("-" * 80)
            for sale in sales:
                print(
                    f"{sale[0]:3} | {sale[1]:6} | {sale[2]:9} | ${sale[3]:8.2f} | ${sale[4]:6.2f} | {sale[5]}")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()


def search_sales():
    try:
        print("\nSearch Sales:")
        print("1. Search by date")
        print("2. Search by item name")
        choice = input("Enter your choice (1-2): ")

        conn = db.get_connection()
        cursor = conn.cursor()

        if choice == '1':
            date = input("Enter date (YYYY-MM-DD): ")
            cursor.execute('''
                SELECT s.id, i.name, s.quantity, s.unit_price, s.total_amount, s.sale_date
                FROM sales s
                JOIN inventory i ON s.item_id = i.id
                WHERE DATE(s.sale_date) = ?
                ORDER BY s.sale_date DESC
            ''', (date,))
        elif choice == '2':
            item_name = input("Enter item name: ")
            cursor.execute('''
                SELECT s.id, i.name, s.quantity, s.unit_price, s.total_amount, s.sale_date
                FROM sales s
                JOIN inventory i ON s.item_id = i.id
                WHERE i.name LIKE ?
                ORDER BY s.sale_date DESC
            ''', (f'%{item_name}%',))
        else:
            print("Invalid choice!")
            return

        sales = cursor.fetchall()

        if not sales:
            print("\nNo sales records found.")
        else:
            print("\nSearch Results:")
            print("ID  |  Item  |  Quantity  |  Unit Price  |  Total  |  Sale Date")
            print("-" * 80)
            for sale in sales:
                print(
                    f"{sale[0]:3} | {sale[1]:6} | {sale[2]:9} | ${sale[3]:8.2f} | ${sale[4]:6.2f} | {sale[5]}")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()


def generate_sales_report():
    try:
        print("\nGenerate Sales Report:")
        print("1. Daily report")
        print("2. Monthly report")
        choice = input("Enter your choice (1-2): ")

        conn = db.get_connection()
        cursor = conn.cursor()

        if choice == '1':
            date = input("Enter date (YYYY-MM-DD): ")
            cursor.execute('''
                SELECT 
                    i.name,
                    SUM(s.quantity) as total_quantity,
                    SUM(s.total_amount) as total_sales
                FROM sales s
                JOIN inventory i ON s.item_id = i.id
                WHERE DATE(s.sale_date) = ?
                GROUP BY i.name
            ''', (date,))
            print(f"\nDaily Sales Report for {date}")
        elif choice == '2':
            month = input("Enter month (YYYY-MM): ")
            cursor.execute('''
                SELECT 
                    i.name,
                    SUM(s.quantity) as total_quantity,
                    SUM(s.total_amount) as total_sales
                FROM sales s
                JOIN inventory i ON s.item_id = i.id
                WHERE strftime('%Y-%m', s.sale_date) = ?
                GROUP BY i.name
            ''', (month,))
            print(f"\nMonthly Sales Report for {month}")
        else:
            print("Invalid choice!")
            return

        sales = cursor.fetchall()

        if not sales:
            print("\nNo sales data found for the specified period.")
        else:
            print("\nItem  |  Total Quantity  |  Total Sales")
            print("-" * 45)
            total_revenue = 0
            for sale in sales:
                print(f"{sale[0]:6} | {sale[1]:14} | ${sale[2]:10.2f}")
                total_revenue += sale[2]
            print("-" * 45)
            print(f"Total Revenue: ${total_revenue:.2f}")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()
