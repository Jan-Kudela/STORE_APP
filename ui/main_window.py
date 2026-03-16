from PySide6.QtWidgets import QMainWindow, QTabWidget

from ui.customers import CustomersWidget
from ui.products import ProductsWidget
from ui.invoices import InvoicesWidget


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Skladový systém")

        tabs = QTabWidget()

        tabs.addTab(CustomersWidget(), "Zákazníci")
        tabs.addTab(ProductsWidget(), "Zboží")
        tabs.addTab(InvoicesWidget(), "Faktury")

        self.setCentralWidget(tabs)