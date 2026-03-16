# ui/products_view.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QMessageBox,
    QTableWidget, QTableWidgetItem, QComboBox, QLabel, QAbstractItemView,
    QHBoxLayout
)
from database.db import Session
from database.models import Product

class ProductsView(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        # --- filtr ---
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filtrovat produkty podle názvu nebo EAN")
        self.filter_input.textChanged.connect(self.load_products)  # filtr live při psaní

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
        self.vat.addItems(["21","15","12","0"])
        self.vat.setCurrentText("21")
        self.vat.currentTextChanged.connect(self.live_update_prices)

        self.stock = QLineEdit()
        self.stock.setPlaceholderText("Sklad")

        self.ean = QLineEdit()
        self.ean.setPlaceholderText("EAN")

        # --- tlačítka ---
        self.btn_new = QPushButton("Nový produkt")
        self.btn_save = QPushButton("Uložit")
        self.btn_edit = QPushButton("Upravit")
        self.btn_delete = QPushButton("Smazat")

        self.btn_new.clicked.connect(self.new_product)
        self.btn_save.clicked.connect(self.add_product)
        self.btn_edit.clicked.connect(self.edit_product)
        self.btn_delete.clicked.connect(self.delete_product)

        # --- tabulka ---
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID","Produkt",
            "Nákup bez DPH","Nákup s DPH",
            "Prodej bez DPH","Prodej s DPH",
            "Marže Kč","Marže %","Sklad"
        ])

        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setSortingEnabled(True)

        self.table.doubleClicked.connect(self.edit_product)

        # --- layout ---
        layout.addWidget(QLabel("Filtr produktů:"))
        layout.addWidget(self.filter_input)
        layout.addWidget(self.name)
        layout.addWidget(self.purchase)
        layout.addWidget(self.sale_vat)
        layout.addWidget(self.vat)
        layout.addWidget(self.stock)
        layout.addWidget(self.ean)
        #layout.addWidget(self.btn_save)
        layout.addWidget(self.table)
        #layout.addWidget(self.btn_save)
        #layout.addWidget(self.btn_edit)
        #layout.addWidget(self.btn_delete)

        button_layout = QHBoxLayout()

        button_layout.addWidget(self.btn_new)
        button_layout.addWidget(self.btn_save)
        button_layout.addWidget(self.btn_edit)
        button_layout.addWidget(self.btn_delete)

        button_layout.addStretch()

        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.load_products()

    def get_selected_product_id(self):

        row = self.table.currentRow()

        if row < 0:
            return None

        id_item = self.table.item(row,0)

        if not id_item:
            return None

        return int(id_item.text())
    

    def new_product(self):

        self.name.clear()
        self.purchase.clear()
        self.sale_vat.clear()
        self.stock.clear()
        self.ean.clear()

        self.vat.setCurrentText("21")

        self.purchase.setReadOnly(False)
        self.stock.setReadOnly(False)

        if hasattr(self, "editing_product_id"):
            del self.editing_product_id


    def edit_product(self):

        product_id = self.get_selected_product_id()

        if not product_id:
            return

        session = Session()
        product = session.query(Product).get(product_id)

        if not product:
            return

        self.name.setText(product.name)
        self.purchase.setText(str(product.purchase_price))
        self.sale_vat.setText(str(product.sale_price_vat))
        self.stock.setText(str(product.stock))
        self.ean.setText(product.ean)
        self.vat.setCurrentText(str(product.vat))
        
        self.purchase.setReadOnly(True)
        self.stock.setReadOnly(True)

        # uložíme ID pro update
        self.editing_product_id = product_id

    # --- live update cen ---
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

        sale = round(sale_vat / (1 + vat/100), 2)
        purchase_vat = round(purchase * (1 + vat/100), 2)
        margin_kc = round(sale - purchase, 2)
        margin_percent = round((margin_kc / purchase * 100) if purchase else 0, 2)

        self.purchase_vat = purchase_vat
        self.sale_price = sale
        self.sale_vat_calc = sale_vat
        self.margin_kc = margin_kc
        self.margin_percent = margin_percent

        # preview první řádek
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

    # --- načtení produktů z DB s filtrem ---
    def load_products(self):
        session = Session()
        filter_text = self.filter_input.text().strip()

        query = session.query(Product)

        if filter_text:

            query = query.filter(
                (Product.name.ilike(f"%{filter_text}%")) |
                (Product.ean.ilike(f"%{filter_text}%"))
            )

        products = query.order_by(Product.name).all()

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

        if self.table.rowCount() > 0:
            self.table.selectRow(0)


    # --- uložit produkt ---
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

        vat = float(self.vat.currentText())
        sale = round(sale_vat / (1 + vat/100), 2)

        if hasattr(self, "editing_product_id"):

            product = session.query(Product).get(self.editing_product_id)

            product.name = self.name.text()
            product.purchase_price = purchase
            product.sale_price = sale
            product.vat = vat
            product.stock = int(self.stock.text() or 0)
            product.ean = self.ean.text()

            del self.editing_product_id

        else:

            product = Product(
                name=self.name.text(),
                purchase_price=purchase,
                sale_price=sale,
                vat=vat,
                stock=int(self.stock.text() or 0),
                ean=self.ean.text()
            )

            session.add(product)

        session.commit()

        self.load_products()

        self.purchase.setReadOnly(False)
        self.stock.setReadOnly(False)

        self.name.clear()
        self.purchase.clear()
        self.sale_vat.clear()
        self.stock.clear()
        self.ean.clear()
        self.vat.setCurrentText("21")


    
    def delete_product(self):

        product_id = self.get_selected_product_id()

        if not product_id:
            return

        session = Session()
        product = session.query(Product).get(product_id)

        if not product:
            return

        # podmínka: nesmí jít smazat pokud je skladem
        if product.stock > 0:
            QMessageBox.warning(
                self,
                "Nelze smazat produkt",
                "Produkt nelze smazat, protože je stále na skladě."
            )
            return

        session.delete(product)
        session.commit()

        self.load_products()