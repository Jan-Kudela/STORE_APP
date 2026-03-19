# ui/products_view.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QMessageBox,
    QTableWidget, QTableWidgetItem, QComboBox, QLabel, QAbstractItemView,
    QHBoxLayout,QHeaderView,QFrame
)
from database.db import Session
from database.models import Product

class ProductsView(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        # --- filtr ---
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filtrovat produkty podle názvu, EAN nebo výrobce")
        self.filter_input.textChanged.connect(self.load_products)  # filtr live při psaní

        # --- vstupy ---
        self.name = QLineEdit()
        self.name.setPlaceholderText("Název produktu")
        self.name.textChanged.connect(self.check_name)
        self.name.textChanged.connect(self.live_update_prices)

        self.manufacturer = QLineEdit()
        self.manufacturer.setPlaceholderText("Výrobce")
        

        self.supplier = QLineEdit()
        self.supplier.setPlaceholderText("Dodavatel")
        

        self.purchase = QLineEdit()
        self.purchase.setPlaceholderText("Nákup bez DPH")
        self.purchase.textChanged.connect(self.live_update_prices)

        self.sale_vat = QLineEdit()
        self.sale_vat.setPlaceholderText("Prodej s DPH")
        self.sale_vat.textChanged.connect(self.live_update_prices)

        self.vat = QComboBox()
        self.vat.addItems(["21%","15%","12%","0%"])
        self.vat.setCurrentText("21%")
        self.vat.currentTextChanged.connect(self.live_update_prices)

        self.stock = QLineEdit()
        self.stock.setPlaceholderText("Sklad")
        self.stock.textChanged.connect(self.live_update_prices)

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

        # live náhled
        self.preview_frame = QFrame()
        self.preview_frame.setFrameShape(QFrame.StyledPanel)
        self.preview_frame.setStyleSheet("""
            QFrame {
                background-color: #eaf4fb;
                border: 1px solid #90cae8;
                border-radius: 6px;
                padding: 4px;
            }
        """)

        preview_layout = QHBoxLayout()
        preview_layout.setContentsMargins(8, 6, 8, 6)
        preview_layout.setSpacing(16)

        self.lbl_name        = QLabel("Název: —")
        self.lbl_purchase    = QLabel("Nákup bez DPH: —")
        self.lbl_purchase_vat= QLabel("Nákup s DPH: —")
        self.lbl_sale        = QLabel("Prodej bez DPH: —")
        self.lbl_sale_vat    = QLabel("Prodej s DPH: —")
        self.lbl_margin_kc   = QLabel("Marže: —")
        self.lbl_margin_pct  = QLabel("Marže %: —")
        self.lbl_vat         = QLabel("DPH: —")
        self.lbl_stock       = QLabel("Sklad: —")

        for lbl in [self.lbl_name, self.lbl_purchase, self.lbl_purchase_vat,
                    self.lbl_sale, self.lbl_sale_vat, self.lbl_margin_kc,
                    self.lbl_margin_pct, self.lbl_vat, self.lbl_stock]:
            lbl.setStyleSheet("color: #1a5276; font-size: 12px;")
            preview_layout.addWidget(lbl)

        preview_layout.addStretch()
        self.preview_frame.setLayout(preview_layout)


        # --- tabulka ---
        self.table = QTableWidget()
        self.table.setColumnCount(12)
        self.table.setHorizontalHeaderLabels([
            "ID","Produkt","Výrobce","Dodavatel","DPH",
            "Nákup bez DPH","Nákup s DPH",
            "Prodej bez DPH","Prodej s DPH",
            "Marže Kč","Marže %","Sklad"
        ])

        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setSortingEnabled(True)

        self.table.doubleClicked.connect(self.edit_product)

        # width of colums in table
        header = self.table.horizontalHeader()
        for col in range(0, 12):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)


        # line with TAX
        self.vat_row = QHBoxLayout()
        label = (QLabel("DPH:"))
        label.setFixedWidth(25)
        self.vat_row.addWidget(label)
        self.vat_row.addWidget(self.vat)
        self.vat_row.addStretch()

        # --- layout ---
        layout.addWidget(QLabel("Filtr produktů:"))
        layout.addWidget(self.filter_input)
        layout.addWidget(self.name)
        layout.addWidget(self.manufacturer)
        layout.addWidget(self.supplier)
        layout.addWidget(self.purchase)
        layout.addWidget(self.sale_vat)
        layout.addLayout(self.vat_row)
        layout.addWidget(self.stock)
        layout.addWidget(self.ean)
        layout.addWidget(self.preview_frame)
        layout.addWidget(self.table)
      

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
        self.manufacturer.clear()
        self.supplier.clear()
        self.purchase.clear()
        self.sale_vat.clear()
        self.stock.clear()
        self.ean.clear()

        self.vat.setCurrentText("21%")

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
        self.manufacturer.setText(product.manufacturer)
        self.supplier.setText(product.supplier)
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
            vat = int(self.vat.currentText().strip("%"))
        except:
            vat = 21

        sale = round(sale_vat / (1 + vat / 100), 2)
        purchase_vat = round(purchase * (1 + vat / 100), 2)
        margin_kc = round(sale - purchase, 2)
        margin_percent = round((margin_kc / purchase * 100) if purchase else 0, 2)

        # uložíme pro add_product
        self.purchase_vat   = purchase_vat
        self.sale_price     = sale
        self.sale_vat_calc  = sale_vat
        self.margin_kc      = margin_kc
        self.margin_percent = margin_percent

        # aktualizace karty
        name = self.name.text() or "—"
        stock = self.stock.text() or "0"

        # barva marže — zelená / oranžová / červená
        if margin_kc > 0:
            color = "#1e8449"
        elif margin_kc == 0:
            color = "#b7950b"
        else:
            color = "#c0392b"

        self.lbl_name.setText(f"<b>{name}</b>")
        self.lbl_vat.setText(f"DPH: {vat} %")
        self.lbl_purchase.setText(f"Nákup bez DPH: {purchase} Kč")
        self.lbl_purchase_vat.setText(f"Nákup s DPH: {purchase_vat} Kč")
        self.lbl_sale.setText(f"Prodej bez DPH: {sale} Kč")
        self.lbl_sale_vat.setText(f"Prodej s DPH: {sale_vat} Kč")
        self.lbl_margin_kc.setText(f"<span style='color:{color}'><b>Marže: {margin_kc} Kč</b></span>")
        self.lbl_margin_pct.setText(f"<span style='color:{color}'><b>{margin_percent} %</b></span>")
        self.lbl_stock.setText(f"Sklad: {stock} ks")

    # --- načtení produktů z DB s filtrem ---
    def load_products(self):
        session = Session()
        filter_text = self.filter_input.text().strip()

        query = session.query(Product)

        if filter_text:

            query = query.filter(
                (Product.name.ilike(f"%{filter_text}%")) |
                (Product.ean.ilike(f"%{filter_text}%"))  |
                (Product.manufacturer.ilike(f"%{filter_text}%"))
            )

        products = query.order_by(Product.name).all()

        self.table.setRowCount(len(products))
        for r,p in enumerate(products):
            self.table.setItem(r,0,QTableWidgetItem(str(p.id)))
            self.table.setItem(r,1,QTableWidgetItem(p.name))
            self.table.setItem(r,2,QTableWidgetItem(p.manufacturer or ""))
            self.table.setItem(r,3,QTableWidgetItem(p.supplier or ""))
            self.table.setItem(r,4,QTableWidgetItem(str(p.vat)))
            self.table.setItem(r,5,QTableWidgetItem(str(p.purchase_price)))
            self.table.setItem(r,6,QTableWidgetItem(str(p.purchase_price_vat)))
            self.table.setItem(r,7,QTableWidgetItem(str(p.sale_price)))
            self.table.setItem(r,8,QTableWidgetItem(str(p.sale_price_vat)))
            self.table.setItem(r,9,QTableWidgetItem(str(p.margin_kc)))
            self.table.setItem(r,10,QTableWidgetItem(str(p.margin_percent) + " %"))
            self.table.setItem(r,11,QTableWidgetItem(str(p.stock)))

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

        vat_str =(self.vat.currentText()) 
        vat = float(vat_str.strip("%"))
        sale = round(sale_vat / (1 + vat/100), 2)

        if hasattr(self, "editing_product_id"):

            product = session.query(Product).get(self.editing_product_id)

            product.name = self.name.text()
            product.manufacturer = self.manufacturer.text()
            product.supplier = self.supplier.text()
            product.purchase_price = purchase
            product.sale_price = sale
            product.vat = vat
            product.stock = int(self.stock.text() or 0)
            product.ean = self.ean.text()

            del self.editing_product_id

        else:

            product = Product(
                name=self.name.text(),
                manufacturer=self.manufacturer.text(),
                supplier=self.supplier.text(),
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
        self.manufacturer.clear()
        self.supplier.clear()
        self.purchase.clear()
        self.sale_vat.clear()
        self.stock.clear()
        self.ean.clear()
        self.vat.setCurrentText("21")


    def check_name(self):
        from database.db import Session
        from database.models import Product

        name = self.name.text().strip()

        if not name:
            self.name.setStyleSheet("")
            return

        session = Session()
        exists = session.query(Product).filter(Product.name == name).first()

        if exists:
            # červené pole = existuje
            self.name.setStyleSheet("background-color: #ffcccc;")
        else:
            # OK stav
            self.name.setStyleSheet("")
        
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