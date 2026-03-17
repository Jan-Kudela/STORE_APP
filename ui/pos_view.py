
from PySide6.QtWidgets import QWidget,QVBoxLayout,QLineEdit,QTableWidget,QTableWidgetItem,QPushButton
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
        self.table.setHorizontalHeaderLabels(["Produkt","Ks","Cena","Celkem"])

        btn = QPushButton("Dokončit prodej")
        btn.clicked.connect(self.finish_sale)

        layout.addWidget(self.barcode)
        layout.addWidget(self.table)
        layout.addWidget(btn)

        self.setLayout(layout)

    def scan(self):

        code = self.barcode.text()

        session = Session()
        product = session.query(Product).filter_by(ean=code).first()

        if not product:
            self.barcode.clear()
            return

        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row,0,QTableWidgetItem(product.name))
        self.table.setItem(row,1,QTableWidgetItem("1"))
        self.table.setItem(row,2,QTableWidgetItem(str(product.price)))
        self.table.setItem(row,3,QTableWidgetItem(str(product.price)))

        decrease_stock(product.id,1)
        self.barcode.clear()

    def finish_sale(self):

        items = []

        for r in range(self.table.rowCount()):

            name = self.table.item(r,0).text()
            qty = int(self.table.item(r,1).text())
            price = float(self.table.item(r,2).text())

            items.append((name,qty,price))

        if items:
            create_invoice_pdf(items)

        self.table.setRowCount(0)
