from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit

from database import Session
from models import Customer


class CustomersWidget(QWidget):

    def __init__(self):

        super().__init__()

        layout = QVBoxLayout()

        self.name = QLineEdit()
        self.name.setPlaceholderText("Jméno")

        self.ico = QLineEdit()
        self.ico.setPlaceholderText("IČO")

        self.add_btn = QPushButton("Přidat zákazníka")
        self.add_btn.clicked.connect(self.add_customer)

        self.table = QTableWidget()

        layout.addWidget(self.name)
        layout.addWidget(self.ico)
        layout.addWidget(self.add_btn)
        layout.addWidget(self.table)

        self.setLayout(layout)

        self.load_data()

    def load_data(self):

        session = Session()

        customers = session.query(Customer).all()

        self.table.setRowCount(len(customers))
        self.table.setColumnCount(2)

        for row, c in enumerate(customers):

            self.table.setItem(row, 0, QTableWidgetItem(c.name))
            self.table.setItem(row, 1, QTableWidgetItem(c.ico))

    def add_customer(self):

        session = Session()

        c = Customer(
            name=self.name.text(),
            ico=self.ico.text()
        )

        session.add(c)
        session.commit()

        self.load_data()