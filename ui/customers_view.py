
from PySide6.QtWidgets import QWidget,QVBoxLayout,QPushButton,QTableWidget,QTableWidgetItem,QLineEdit
from database.db import Session
from database.models import Customer

class CustomersView(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.name = QLineEdit()
        self.name.setPlaceholderText("Jméno")

        self.ico = QLineEdit()
        self.ico.setPlaceholderText("IČO")

        self.address = QLineEdit()
        self.address.setPlaceholderText("Adresa")

        btn = QPushButton("Přidat zákazníka")
        btn.clicked.connect(self.add_customer)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID","Jméno","IČO","Adresa"])

        layout.addWidget(self.name)
        layout.addWidget(self.ico)
        layout.addWidget(self.address)
        layout.addWidget(btn)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.load_customers()

    def load_customers(self):

        session = Session()
        customers = session.query(Customer).all()

        self.table.setRowCount(len(customers))

        for r,c in enumerate(customers):
            self.table.setItem(r,0,QTableWidgetItem(str(c.id)))
            self.table.setItem(r,1,QTableWidgetItem(c.name))
            self.table.setItem(r,2,QTableWidgetItem(str(c.ico)))
            self.table.setItem(r,3,QTableWidgetItem(str(c.address)))

    def add_customer(self):

        session = Session()

        c = Customer(
            name=self.name.text(),
            ico=self.ico.text(),
            address=self.address.text()
        )

        session.add(c)
        session.commit()

        self.load_customers()
