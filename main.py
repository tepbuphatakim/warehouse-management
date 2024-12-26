from inventory import handle_inventory

def main():
    while True:
        print("\nWarehouse Management System Menu:")
        print("1. Dashboard")
        print("2. Inventory")
        print("3. Sale management")
        print("4. Return items")
        print("5. Exit")

        choice = input("\nEnter your choice (1-5): ")
        if choice == '1':
            print("Dashboard")
        elif choice == '2':
            handle_inventory()
        elif choice == '3':
            print("Sale management")
        elif choice == '4':
            print("Return items")
        elif choice == '5':
            print("Thank you for using the Warehouse Management System!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
