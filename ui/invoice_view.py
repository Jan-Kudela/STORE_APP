from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QComboBox, QSpinBox
)

from database.db import Session
from database.models import Product, Customer
from services.invoice_service import create_invoice


class InvoiceView(QWidget):

    def __init__(self):

        super().__init__()

        layout = QVBoxLayout()

        # zákazník
        self.customer_combo = QComboBox()
        layout.addWidget(self.customer_combo)

        # produkty
        self.product_combo = QComboBox()
        layout.addWidget(self.product_combo)

        self.qty = QSpinBox()
        self.qty.setValue(1)
        layout.addWidget(self.qty)

        self.btn_add = QPushButton("Přidat položku")
        layout.addWidget(self.btn_add)

        # tabulka položek
        self.table = QTableWidget(0,4)
        self.table.setHorizontalHeaderLabels(["Produkt","Ks","Cena","DPH"])
        layout.addWidget(self.table)

        # vystavení faktury
        self.btn_create = QPushButton("Vystavit fakturu")
        layout.addWidget(self.btn_create)

        #historie faktur
        self.invoice_table = QTableWidget(0,4)
        self.invoice_table.setHorizontalHeaderLabels([
            "Číslo", "Zákazník", "Celkem s DPH", "ID"
        ])

        self.load_invoices()

        self.invoice_table.cellDoubleClicked.connect(self.open_invoice)

        layout.addWidget(self.invoice_table)

        self.setLayout(layout)

        self.items = []

        self.load_data()

        self.btn_add.clicked.connect(self.add_item)
        self.btn_create.clicked.connect(self.create_invoice)

    def load_data(self):

        session = Session()

        for c in session.query(Customer).all():
            self.customer_combo.addItem(c.name, c)

        for p in session.query(Product).all():
            self.product_combo.addItem(p.name, p)

    def add_item(self):

        product = self.product_combo.currentData()

        item = {
            "name": product.name,
            "qty": self.qty.value(),
            "price": product.sale_price_vat,
            "vat": product.vat
        }

        self.items.append(item)

        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row,0,QTableWidgetItem(item["name"]))
        self.table.setItem(row,1,QTableWidgetItem(str(item["qty"])))
        self.table.setItem(row,2,QTableWidgetItem(str(item["price"])))
        self.table.setItem(row,3,QTableWidgetItem(str(item["vat"])))

    def create_invoice(self):

        customer = self.customer_combo.currentData()

        invoice = create_invoice(customer, self.items)

        from services.invoice_service import create_invoice_pdf

        create_invoice_pdf(
            {"name": customer.name, "address": customer.address},
            [(i["name"], i["qty"], i["price"]) for i in self.items]
        )

        print("Faktura vytvořena:", invoice.number)

        self.load_invoices()

    
    def load_invoices(self):

        from database.db import Session
        from database.models import Invoice

        session = Session()

        invoices = session.query(Invoice).all()

        self.invoice_table.setRowCount(0)

        for inv in invoices:

            row = self.invoice_table.rowCount()
            self.invoice_table.insertRow(row)

            self.invoice_table.setItem(row, 0, QTableWidgetItem(inv.number))
            self.invoice_table.setItem(row, 1, QTableWidgetItem(inv.customer.name))
            self.invoice_table.setItem(row, 2, QTableWidgetItem(str(inv.total_with_vat)))
            self.invoice_table.setItem(row, 3, QTableWidgetItem(str(inv.id)))

    
    def open_invoice(self, row, column):

        invoice_id = self.invoice_table.item(row, 3).text()
        pdf_path = f"invoice_{invoice_id}.pdf"

        import os, sys, subprocess

        if not os.path.exists(pdf_path):
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Soubor nenalezen", f"PDF faktura '{pdf_path}' neexistuje.")
            return

        # cross-platform otevření PDF (oprava: os.startfile funguje jen na Windows)
        if sys.platform == "win32":
            os.startfile(pdf_path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", pdf_path])
        else:
            subprocess.Popen(["xdg-open", pdf_path])