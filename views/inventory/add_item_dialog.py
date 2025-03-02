from PyQt6.QtWidgets import (QHBoxLayout, QPushButton, QLineEdit, QDialog, QFormLayout)

class AddItemDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Item")
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()

        self.name_input = QLineEdit()
        self.quantity_input = QLineEdit()
        self.price_input = QLineEdit()
        self.location_input = QLineEdit()

        layout.addRow("Name:", self.name_input)
        layout.addRow("Quantity:", self.quantity_input)
        layout.addRow("Price ($):", self.price_input)
        layout.addRow("Location:", self.location_input)

        button_box = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")

        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        button_box.addWidget(save_button)
        button_box.addWidget(cancel_button)
        layout.addRow(button_box)

        self.setLayout(layout)

    def get_item_data(self):
        return {
            'name': self.name_input.text(),
            'quantity': self.quantity_input.text(),
            'price': self.price_input.text(),
            'location': self.location_input.text()
        }
