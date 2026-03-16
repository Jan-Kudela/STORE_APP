
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QPushButton,QTableWidget,
QTableWidgetItem,QLineEdit,QHBoxLayout,QAbstractItemView)
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

        self.dic = QLineEdit()
        self.dic.setPlaceholderText("DIČ")

        self.address = QLineEdit()
        self.address.setPlaceholderText("Adresa")

        self.phone = QLineEdit()
        self.phone.setPlaceholderText("Telefon")

        self.email = QLineEdit()
        self.email.setPlaceholderText("E-mail")

        self.btn_new = QPushButton("Nový zákazník")
        self.btn_save = QPushButton("Uložit")
        self.btn_edit = QPushButton("Upravit")
        self.btn_delete = QPushButton("Smazat")

        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText(
            "Filtrovat zákazníky podle názvu / IČO / emailu"
        )

        self.filter_input.textChanged.connect(self.load_customers)

        self.btn_new.clicked.connect(self.new_customer)
        self.btn_save.clicked.connect(self.add_customer)
        self.btn_edit.clicked.connect(self.edit_customer)
        self.btn_delete.clicked.connect(self.delete_customer)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID","Jméno","IČO","DIČ","Adresa","Telefon","E-mail"
        ])

        button_layout = QHBoxLayout()

        button_layout.addWidget(self.btn_new)
        button_layout.addWidget(self.btn_save)
        button_layout.addWidget(self.btn_edit)
        button_layout.addWidget(self.btn_delete)

        button_layout.addStretch()

        layout.addLayout(button_layout)
        layout.addWidget(self.name)
        layout.addWidget(self.ico)
        layout.addWidget(self.dic)
        layout.addWidget(self.address)
        layout.addWidget(self.phone)
        layout.addWidget(self.email)
        layout.addWidget(self.filter_input)
        layout.addWidget(self.table)


        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setSortingEnabled(True)

        self.table.doubleClicked.connect(self.edit_customer)

        self.setLayout(layout)
        self.load_customers()

    def load_customers(self):

        session = Session()

        filter_text = self.filter_input.text().strip()

        query = session.query(Customer)

        if filter_text:

            query = query.filter(
                (Customer.name.ilike(f"%{filter_text}%")) |
                (Customer.ico.ilike(f"%{filter_text}%")) |
                (Customer.email.ilike(f"%{filter_text}%"))
            )

        customers = query.order_by(Customer.name).all()

        self.table.setRowCount(len(customers))

        for r,c in enumerate(customers):

            self.table.setItem(r,0,QTableWidgetItem(str(c.id)))
            self.table.setItem(r,1,QTableWidgetItem(c.name or ""))
            self.table.setItem(r,2,QTableWidgetItem(c.ico or ""))
            self.table.setItem(r,3,QTableWidgetItem(c.dic or ""))
            self.table.setItem(r,4,QTableWidgetItem(c.email or ""))
            self.table.setItem(r,5,QTableWidgetItem(c.phone or ""))
            self.table.setItem(r,6,QTableWidgetItem(c.address or ""))

    def new_customer(self):

        self.name.clear()
        self.ico.clear()
        self.dic.clear()
        self.email.clear()
        self.phone.clear()
        self.address.clear()

        if hasattr(self, "editing_customer_id"):
            del self.editing_customer_id

    def edit_customer(self):

        row = self.table.currentRow()

        if row < 0:
            return

        customer_id = int(self.table.item(row,0).text())

        session = Session()
        customer = session.query(Customer).get(customer_id)

        self.name.setText(customer.name)
        self.ico.setText(customer.ico)
        self.dic.setText(customer.dic)
        self.email.setText(customer.email)
        self.phone.setText(customer.phone)
        self.address.setText(customer.address)

        self.editing_customer_id = customer_id


    def add_customer(self):

        session = Session()

        if hasattr(self, "editing_customer_id"):

            customer = session.query(Customer).get(self.editing_customer_id)

            customer.name = self.name.text()
            customer.ico = self.ico.text()
            customer.dic = self.dic.text()
            customer.email = self.email.text()
            customer.phone = self.phone.text()
            customer.address = self.address.text()

            del self.editing_customer_id

        else:

            customer = Customer(
                name=self.name.text(),
                ico=self.ico.text(),
                dic=self.dic.text(),
                email=self.email.text(),
                phone=self.phone.text(),
                address=self.address.text()
            )

            session.add(customer)

        session.commit()
        self.load_customers()

    
    def delete_customer(self):

        row = self.table.currentRow()

        if row < 0:
            return

        customer_id = int(self.table.item(row,0).text())

        session = Session()
        customer = session.query(Customer).get(customer_id)

        session.delete(customer)
        session.commit()

        self.load_customers()

    