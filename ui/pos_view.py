from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QTableWidget,
                               QTableWidgetItem, QPushButton, QMessageBox,
                               QHBoxLayout, QLabel, QSpinBox, QHeaderView)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from database.db import Session
from database.models import Product
from services.stock_service import decrease_stock
from services.invoice_service import create_invoice


class POSView(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        # --- EAN ---
        layout.addWidget(QLabel("EAN kód:"))
        self.barcode = QLineEdit()
        self.barcode.setPlaceholderText("Načti nebo zadej EAN kód")
        self.barcode.returnPressed.connect(self.scan)
        layout.addWidget(self.barcode)

        # --- vyhledávání podle názvu ---
        layout.addWidget(QLabel("Vyhledat podle názvu:"))
        self.name_search = QLineEdit()
        self.name_search.setPlaceholderText("Začněte psát název produktu...")
        self.name_search.textChanged.connect(self.update_completer)

        from PySide6.QtWidgets import QCompleter
        from PySide6.QtCore import QStringListModel
        self.completer = QCompleter([])
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        self.completer.activated.connect(self.add_by_name)
        self.name_search.setCompleter(self.completer)
        layout.addWidget(self.name_search)

        # --- počet kusů + tlačítka ---
        controls_layout = QHBoxLayout()

        controls_layout.addWidget(QLabel("Počet kusů:"))
        self.qty_spin = QSpinBox()
        self.qty_spin.setMinimum(1)
        self.qty_spin.setMaximum(9999)
        self.qty_spin.setValue(1)
        self.qty_spin.setFixedWidth(80)
        controls_layout.addWidget(self.qty_spin)

        controls_layout.addWidget(QLabel("Sleva %:"))
        self.discount_spin = QSpinBox()
        self.discount_spin.setMinimum(0)
        self.discount_spin.setMaximum(100)
        self.discount_spin.setValue(0)
        self.discount_spin.setFixedWidth(60)
        controls_layout.addWidget(self.discount_spin)

        self.btn_add_item = QPushButton("Přidat položku")
        self.btn_add_item.clicked.connect(self.add_selected)
        controls_layout.addWidget(self.btn_add_item)

        self.btn_remove_item = QPushButton("Odebrat položku")
        self.btn_remove_item.setStyleSheet("color: #c0392b;")
        self.btn_remove_item.clicked.connect(self.remove_selected)
        controls_layout.addWidget(self.btn_remove_item)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # --- košík ---
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Produkt", "Ks", "Cena s DPH", "Nákup s DPH", "Sleva" "Celkem"
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for col in range(1, 5):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)

        layout.addWidget(self.table)

        layout.addWidget(self.table)

        # --- celková cena ---
        total_layout = QHBoxLayout()
        total_layout.addStretch()
        self.lbl_total = QLabel("Celkem: 0,00 Kč")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.lbl_total.setFont(font)
        self.lbl_total.setStyleSheet("color: #1a5276; padding: 6px;")
        total_layout.addWidget(self.lbl_total)
        layout.addLayout(total_layout)

        # --- tlačítko ---
        btn = QPushButton("Dokončit prodej")
        btn.clicked.connect(self.finish_sale)
        layout.addWidget(btn)

        self.setLayout(layout)
        self._items = []

        self.update_completer()

    def _set_row(self, row, product, qty, discount=0):
        """Pomocná metoda — zapíše řádek do tabulky se zarovnáním na střed."""
        price_vat = product.sale_price_vat
        purchase_vat = product.purchase_price_vat
        discounted_price = round(price_vat * (1- discount / 100), 2)
        celkem = round(discounted_price * qty, 2)

        values = [
            product.name,
            str(qty),
            f"{price_vat:.2f} Kč",
            f"{purchase_vat:.2f} Kč",
            f"{discount} %" if discount > 0 else "-",
            f"{celkem:.2f} Kč"
        ]

        for col, val in enumerate(values):
            item = QTableWidgetItem(val)
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, col, item)

    def _update_total(self):
        total = sum(round(i["price"] * (1 - i["discount"] / 100), 2) * i["qty"] for i in self._items)
        self.lbl_total.setText(f"Celkem: {total:.2f} Kč")

    def scan(self):
        code = self.barcode.text().strip()
        if not code:
            return

        session = Session()
        product = session.query(Product).filter_by(ean=code).first()
        session.close()

        if not product:
            QMessageBox.warning(self, "Produkt nenalezen", f"EAN '{code}' nenalezen v databázi.")
            self.barcode.clear()
            return

        self._selected_product = product
        self.name_search.setText(product.name)
        self.barcode.clear()

    def update_completer(self):
        from PySide6.QtCore import QStringListModel
        session = Session()
        filter_text = self.name_search.text().strip()
        products = session.query(Product).filter(
            Product.name.ilike(f"%{filter_text}%")
        ).order_by(Product.name).all()
        session.close()

        names = [p.name for p in products]
        self.completer.setModel(QStringListModel(names))

    def add_by_name(self, name):
        session = Session()
        product = session.query(Product).filter_by(name=name).first()
        session.close()

        if not product:
            return

        self._selected_product = product

    def _add_to_cart(self, product, qty, discount=0):
        for item in self._items:
            if item["name"] == product.name:
                item["qty"] += qty
                for r in range(self.table.rowCount()):
                    if self.table.item(r, 0).text() == product.name:
                        self._set_row(r, product, item["qty"], item["discount"])
                        break
                decrease_stock(product.id, qty)
                self._update_total()
                return

        item = {
            "name": product.name,
            "qty": qty,
            "price": product.sale_price_vat,
            "vat": product.vat,
            "discount": discount        # <-- nově
        }
        self._items.append(item)

        row = self.table.rowCount()
        self.table.insertRow(row)
        self._set_row(row, product, qty, discount)

        decrease_stock(product.id, qty)
        self._update_total()
    
    def finish_sale(self):
        if not self._items:
            QMessageBox.information(self, "Kasa", "Košík je prázdný.")
            return

        create_invoice(None, self._items)

        QMessageBox.information(self, "Prodej dokončen", "Prodej byl úspěšně zaznamenán.")

        self._items.clear()
        self.table.setRowCount(0)
        self._update_total()

    def add_selected(self):
        if not hasattr(self, "_selected_product") or not self._selected_product:
            QMessageBox.information(self, "Kasa", "Nejprve vyberte produkt podle názvu nebo EAN.")
            return

        product = self._selected_product
        qty = self.qty_spin.value()
        discount = self.discount_spin.value()   # <-- nově

        if product.stock < qty:
            QMessageBox.warning(self, "Nedostatek zboží",
                                f"Na skladě je pouze {product.stock} ks produktu '{product.name}'.")
            return

        self._add_to_cart(product, qty, discount)
        self.name_search.clear()
        self.qty_spin.setValue(1)
        self.discount_spin.setValue(0)          # <-- reset slevy po přidání
        self._selected_product = None

    def remove_selected(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Kasa", "Vyberte položku, kterou chcete odebrat.")
            return

        name = self.table.item(row, 0).text()
        qty = int(self.table.item(row, 1).text())

        # vrátíme zboží na sklad
        session = Session()
        product = session.query(Product).filter_by(name=name).first()
        if product:
            product.stock += qty
            session.commit()
        session.close()

        # odebereme z interního seznamu
        self._items = [i for i in self._items if i["name"] != name]
        self.table.removeRow(row)
        self._update_total()