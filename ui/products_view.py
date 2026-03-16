# ui/products_view.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox
)
from PySide6.QtCore import Qt
from database.db import Session
from database.models import Product

class ProductsView(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        # --- vstupy ---
        self.name = QLineEdit()
        self.name.setPlaceholderText("Název produktu")

        self.purchase = QLineEdit()
        self.purchase.setPlaceholderText("Nákup bez DPH")
        self.purchase.textChanged.connect(self.live_update_prices)

        self.sale_vat = QLineEdit()
        self.sale_vat.setPlaceholderText("Prodej s DPH")
        self.sale_vat.textChanged.connect(self.live_update_prices)

        self.vat = QComboBox()
        self.vat.addItems(["21", "15", "12", "0"])
        self.vat.setCurrentText("21")
        self.vat.currentTextChanged.connect(self.live_update_prices)

        self.stock = QLineEdit()
        self.stock.setPlaceholderText("Sklad")

        self.ean = QLineEdit()
        self.ean.setPlaceholderText("EAN")

        # --- tlačítko uložit ---
        self.btn_save = QPushButton("Uložit produkt")
        self.btn_save.clicked.connect(self.add_product)

        # --- tabulka ---
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID","Produkt",
            "Nákup bez DPH","Nákup s DPH",
            "Prodej bez DPH","Prodej s DPH",
            "Marže Kč","Marže %","Sklad"
        ])

        # --- layout ---
        layout.addWidget(self.name)
        layout.addWidget(self.purchase)
        layout.addWidget(self.sale_vat)
        layout.addWidget(self.vat)
        layout.addWidget(self.stock)
        layout.addWidget(self.ean)
        layout.addWidget(self.btn_save)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.load_products()

    # --- live update pro nákup/prodej s DPH a marži ---
    def live_update_prices(self):
        try:
            purchase = float(self.purchase.text())
        except:
            purchase = 0
        try:
            sale_vat = float(self.sale_vat.text())
        except:
            sale_vat = 0
        try:
            vat = float(self.vat.currentText())
        except:
            vat = 21

        # --- dopočítat prodej bez DPH ---
        sale = round(sale_vat / (1 + vat/100), 2)
        purchase_vat = round(purchase * (1 + vat/100), 2)
        margin_kc = round(sale - purchase, 2)
        margin_percent = round((margin_kc / purchase * 100) if purchase else 0, 2)

        self.purchase_vat = purchase_vat
        self.sale_price = sale
        self.sale_vat_calc = sale_vat
        self.margin_kc = margin_kc
        self.margin_percent = margin_percent

        # zobrazení live v tabulce prvního řádku (preview)
        if self.table.rowCount() == 0:
            self.table.setRowCount(1)
        self.table.setItem(0,0,QTableWidgetItem("-"))
        self.table.setItem(0,1,QTableWidgetItem(self.name.text()))
        self.table.setItem(0,2,QTableWidgetItem(str(purchase)))
        self.table.setItem(0,3,QTableWidgetItem(str(self.purchase_vat)))
        self.table.setItem(0,4,QTableWidgetItem(str(self.sale_price)))
        self.table.setItem(0,5,QTableWidgetItem(str(self.sale_vat_calc)))
        self.table.setItem(0,6,QTableWidgetItem(str(self.margin_kc)))
        self.table.setItem(0,7,QTableWidgetItem(str(self.margin_percent) + " %"))
        self.table.setItem(0,8,QTableWidgetItem(self.stock.text() or "0"))

    # --- načtení produktů z DB ---
    def load_products(self):
        session = Session()
        products = session.query(Product).all()

        self.table.setRowCount(len(products))
        for r,p in enumerate(products):
            self.table.setItem(r,0,QTableWidgetItem(str(p.id)))
            self.table.setItem(r,1,QTableWidgetItem(p.name))
            self.table.setItem(r,2,QTableWidgetItem(str(p.purchase_price)))
            self.table.setItem(r,3,QTableWidgetItem(str(p.purchase_price_vat)))
            self.table.setItem(r,4,QTableWidgetItem(str(p.sale_price)))
            self.table.setItem(r,5,QTableWidgetItem(str(p.sale_price_vat)))
            self.table.setItem(r,6,QTableWidgetItem(str(p.margin_kc)))
            self.table.setItem(r,7,QTableWidgetItem(str(p.margin_percent) + " %"))
            self.table.setItem(r,8,QTableWidgetItem(str(p.stock)))

    # --- uložit produkt do DB ---
    def add_product(self):
        session = Session()

        try:
            purchase = float(self.purchase.text())
        except:
            purchase = 0
        try:
            sale_vat = float(self.sale_vat.text())
        except:
            sale_vat = 0
        try:
            vat = float(self.vat.currentText())
        except:
            vat = 21

        # dopočítat prodej bez DPH
        sale = round(sale_vat / (1 + vat/100), 2)

        p = Product(
            name=self.name.text(),
            purchase_price=purchase,
            sale_price=sale,
            vat=vat,
            stock=int(self.stock.text() or 0),
            ean=self.ean.text()
        )

        session.add(p)
        session.commit()
        self.load_products()

        # vyčistit vstupy po uložení
        self.name.clear()
        self.purchase.clear()
        self.sale_vat.clear()
        self.vat.setCurrentText("21")
        self.stock.clear()
        self.ean.clear()