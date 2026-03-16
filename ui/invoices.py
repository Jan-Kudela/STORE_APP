from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel

from services.invoice_service import create_invoice_pdf


class InvoicesWidget(QWidget):

    def __init__(self):

        super().__init__()

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Generování faktury"))

        btn = QPushButton("Vytvořit testovací fakturu")

        btn.clicked.connect(self.create_invoice)

        layout.addWidget(btn)

        self.setLayout(layout)

    def create_invoice(self):

        create_invoice_pdf()