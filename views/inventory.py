from database.main import Database
import sqlite3
from datetime import datetime

db = Database()


def handle_inventory():
    while True:
        print("\nInventory Management:")
        print("1. Add new item")
        print("2. Update item")
        print("3. Delete item")
        print("4. Search item")
        print("5. Return to main menu")

        view_inventory()
        choice = input("\nEnter your choice (1-5): ")

        if choice == '1':
            add_item()
        elif choice == '2':
            update_item()
        elif choice == '3':
            delete_item()
        elif choice == '4':
            search_item()
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")


def view_inventory():
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM inventory')
    items = cursor.fetchall()

    if not items:
        print("\nInventory is empty.")
    else:
        print("\nCurrent Inventory:")
        print("ID  |  Name  |  Quantity  |  Price  |  Location  |  Last Updated")
        print("-" * 75)
        for item in items:
            print(
                f"{item[0]:3} | {item[1]:6} | {item[2]:9} | ${item[3]:6.2f} | {item[4]:9} | {item[6]}")

    conn.close()


def add_item():
    print("\nAdd New Item:")
    try:
        name = input("Enter item name: ")
        quantity = int(input("Enter quantity: "))
        price = float(input("Enter price: $"))
        location = input("Enter storage location: ")
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        conn = db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO inventory (name, quantity, price, location, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, quantity, price, location, current_time, current_time))

        conn.commit()
        conn.close()
        print("\nItem added successfully!")

    except ValueError:
        print("Invalid input. Please enter numeric values for quantity and price.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")


def update_item():
    view_inventory()
    try:
        item_id = int(input("\nEnter item ID to update: "))

        conn = db.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM inventory WHERE id = ?', (item_id,))
        item = cursor.fetchone()

        if item:
            print("\nUpdate Item (press Enter to skip):")
            name = input(f"Enter new name [{item[1]}]: ") or item[1]
            quantity_str = input(f"Enter new quantity [{item[2]}]: ")
            quantity = int(quantity_str) if quantity_str else item[2]
            price_str = input(f"Enter new price [{item[3]}]: ")
            price = float(price_str) if price_str else item[3]
            location = input(f"Enter new location [{item[4]}]: ") or item[4]
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute('''
                UPDATE inventory 
                SET name = ?, quantity = ?, price = ?, location = ?, updated_at = ?
                WHERE id = ?
            ''', (name, quantity, price, location, current_time, item_id))

            conn.commit()
            print("\nItem updated successfully!")
        else:
            print("\nItem not found.")

        conn.close()

    except ValueError:
        print("Invalid input. Please enter valid values.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")


def delete_item():
    view_inventory()
    try:
        item_id = int(input("\nEnter item ID to delete: "))

        conn = db.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM inventory WHERE id = ?', (item_id,))
        if cursor.fetchone():
            confirm = input(
                "Are you sure you want to delete this item? (y/n): ")
            if confirm.lower() == 'y':
                cursor.execute(
                    'DELETE FROM inventory WHERE id = ?', (item_id,))
                conn.commit()
                print("\nItem deleted successfully!")
            else:
                print("\nDeletion cancelled.")
        else:
            print("\nItem not found.")

        conn.close()

    except ValueError:
        print("Invalid input. Please enter a valid item ID.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")


def search_item():
    search_term = input("\nEnter item name to search: ")

    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM inventory WHERE name LIKE ?',
                   (f'%{search_term}%',))
    items = cursor.fetchall()

    if items:
        print("\nSearch Results:")
        print("ID  |  Name  |  Quantity  |  Price  |  Location  |  Last Updated")
        print("-" * 75)
        for item in items:
            print(
                f"{item[0]:3} | {item[1]:6} | {item[2]:9} | ${item[3]:6.2f} | {item[4]:9} | {item[6]}")
    else:
        print("\nNo items found.")

    conn.close()
