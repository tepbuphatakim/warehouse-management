from database.main import Database
import sqlite3
from datetime import datetime

db = Database()


def handle_returns():
    while True:
        print("\nReturns Management:")
        print("1. Process new return")
        print("2. View return history")
        print("3. Search returns")
        print("4. Return to main menu")

        choice = input("\nEnter your choice (1-4): ")

        if choice == '1':
            process_return()
        elif choice == '2':
            view_returns_history()
        elif choice == '3':
            search_returns()
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please try again.")


def process_return():
    try:
        print("\nProcess New Return:")
        conn = db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT s.id, i.name, s.quantity, s.unit_price, s.total_amount, s.sale_date
            FROM sales s
            JOIN inventory i ON s.item_id = i.id
            ORDER BY s.sale_date DESC
            LIMIT 10
        ''')
        recent_sales = cursor.fetchall()

        if not recent_sales:
            print("No sales records found!")
            conn.close()
            return

        print("\nRecent Sales:")
        print("Sale ID  |  Item  |  Quantity  |  Unit Price  |  Total  |  Sale Date")
        print("-" * 80)
        for sale in recent_sales:
            print(
                f"{sale[0]:7} | {sale[1]:6} | {sale[2]:9} | ${sale[3]:8.2f} | ${sale[4]:6.2f} | {sale[5]}")

        sale_id = int(input("\nEnter Sale ID: "))

        cursor.execute('''
            SELECT s.id, s.item_id, i.name, s.quantity, s.unit_price
            FROM sales s
            JOIN inventory i ON s.item_id = i.id
            WHERE s.id = ?
        ''', (sale_id,))
        sale = cursor.fetchone()

        if not sale:
            print("Sale not found!")
            conn.close()
            return

        max_quantity = sale[3]
        print(f"\nMaximum returnable quantity: {max_quantity}")
        return_quantity = int(input("Enter quantity to return: "))

        if return_quantity <= 0 or return_quantity > max_quantity:
            print("Invalid return quantity!")
            conn.close()
            return

        reason = input("Enter reason for return: ")
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Calculate refund amount
        refund_amount = return_quantity * sale[4]

        cursor.execute('''
            INSERT INTO returns (sale_id, item_id, quantity, refund_amount, reason, return_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (sale_id, sale[1], return_quantity, refund_amount, reason, current_time))

        cursor.execute('''
            UPDATE inventory 
            SET quantity = quantity + ?,
                updated_at = ?
            WHERE id = ?
        ''', (return_quantity, current_time, sale[1]))

        conn.commit()
        print(
            f"\nReturn processed successfully! Refund amount: ${refund_amount:.2f}")

    except ValueError:
        print("Invalid input. Please enter numeric values.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()


def view_returns_history():
    try:
        conn = db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT r.id, i.name, r.quantity, r.refund_amount, r.reason, r.return_date
            FROM returns r
            JOIN inventory i ON r.item_id = i.id
            ORDER BY r.return_date DESC
        ''')
        returns = cursor.fetchall()

        if not returns:
            print("\nNo returns history found.")
        else:
            print("\nReturns History:")
            print("ID  |  Item  |  Quantity  |  Refund Amount  |  Reason  |  Return Date")
            print("-" * 85)
            for return_item in returns:
                print(
                    f"{return_item[0]:3} | {return_item[1]:6} | {return_item[2]:9} | ${return_item[3]:12.2f} | {return_item[4][:10]:8} | {return_item[5]}")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()


def search_returns():
    try:
        print("\nSearch Returns:")
        print("1. Search by date")
        print("2. Search by item name")
        choice = input("Enter your choice (1-2): ")

        conn = db.get_connection()
        cursor = conn.cursor()

        if choice == '1':
            date = input("Enter date (YYYY-MM-DD): ")
            cursor.execute('''
                SELECT r.id, i.name, r.quantity, r.refund_amount, r.reason, r.return_date
                FROM returns r
                JOIN inventory i ON r.item_id = i.id
                WHERE DATE(r.return_date) = ?
                ORDER BY r.return_date DESC
            ''', (date,))
        elif choice == '2':
            item_name = input("Enter item name: ")
            cursor.execute('''
                SELECT r.id, i.name, r.quantity, r.refund_amount, r.reason, r.return_date
                FROM returns r
                JOIN inventory i ON r.item_id = i.id
                WHERE i.name LIKE ?
                ORDER BY r.return_date DESC
            ''', (f'%{item_name}%',))
        else:
            print("Invalid choice!")
            return

        returns = cursor.fetchall()

        if not returns:
            print("\nNo returns found.")
        else:
            print("\nSearch Results:")
            print("ID  |  Item  |  Quantity  |  Refund Amount  |  Reason  |  Return Date")
            print("-" * 85)
            for return_item in returns:
                print(
                    f"{return_item[0]:3} | {return_item[1]:6} | {return_item[2]:9} | ${return_item[3]:12.2f} | {return_item[4][:10]:8} | {return_item[5]}")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()
