from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit

from database import Session
from models import Product


class ProductsWidget(QWidget):

    def __init__(self):

        super().__init__()

        layout = QVBoxLayout()

        self.name = QLineEdit()
        self.name.setPlaceholderText("Název")

        self.price = QLineEdit()
        self.price.setPlaceholderText("Cena")

        self.stock = QLineEdit()
        self.stock.setPlaceholderText("Sklad")

        self.add_btn = QPushButton("Přidat zboží")
        self.add_btn.clicked.connect(self.add_product)

        self.table = QTableWidget()

        layout.addWidget(self.name)
        layout.addWidget(self.price)
        layout.addWidget(self.stock)
        layout.addWidget(self.add_btn)
        layout.addWidget(self.table)

        self.setLayout(layout)

        self.load_data()

    def load_data(self):

        session = Session()

        products = session.query(Product).all()

        self.table.setRowCount(len(products))
        self.table.setColumnCount(3)

        for row, p in enumerate(products):

            self.table.setItem(row, 0, QTableWidgetItem(p.name))
            self.table.setItem(row, 1, QTableWidgetItem(str(p.price)))
            self.table.setItem(row, 2, QTableWidgetItem(str(p.stock)))

    def add_product(self):

        session = Session()

        p = Product(
            name=self.name.text(),
            price=float(self.price.text()),
            stock=int(self.stock.text())
        )

        session.add(p)
        session.commit()

        self.load_data()