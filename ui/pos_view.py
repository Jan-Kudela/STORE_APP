
from PySide6.QtWidgets import QWidget,QVBoxLayout,QLineEdit,QTableWidget,QTableWidgetItem,QPushButton
from database.db import Session
from database.models import Product
from services.stock_service import decrease_stock
from services.invoice_service import create_invoice

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QTableWidget,
                               QTableWidgetItem, QPushButton, QMessageBox)
from database.db import Session
from database.models import Product
from services.stock_service import decrease_stock
from services.invoice_service import create_invoice

class POSView(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.barcode = QLineEdit()
        self.barcode.setPlaceholderText("Načti EAN kód")
        self.barcode.returnPressed.connect(self.scan)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Produkt", "Ks", "Cena s DPH", "Celkem"])

        btn = QPushButton("Dokončit prodej")
        btn.clicked.connect(self.finish_sale)

        layout.addWidget(self.barcode)
        layout.addWidget(self.table)
        layout.addWidget(btn)

        self.setLayout(layout)

        # interní seznam položek ve správném formátu pro invoice_service
        self._items = []

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

        if product.stock <= 0:
            QMessageBox.warning(self, "Nedostatek zboží", f"Produkt '{product.name}' není na skladě.")
            self.barcode.clear()
            return

        item = {
            "name": product.name,
            "qty": 1,
            "price": product.sale_price_vat,  # oprava: byl product.price (neexistující atribut)
            "vat": product.vat
        }
        self._items.append(item)

        price_vat = product.sale_price_vat
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(product.name))
        self.table.setItem(row, 1, QTableWidgetItem("1"))
        self.table.setItem(row, 2, QTableWidgetItem(str(price_vat)))
        self.table.setItem(row, 3, QTableWidgetItem(str(price_vat)))

        decrease_stock(product.id, 1)
        self.barcode.clear()

    def finish_sale(self):

        if not self._items:
            QMessageBox.information(self, "Kasa", "Košík je prázdný.")
            return

        create_invoice(None, self._items)

        QMessageBox.information(self, "Prodej dokončen", "Prodej byl úspěšně zaznamenán.")

        self._items.clear()
        self.table.setRowCount(0)