
from PySide6.QtWidgets import QMainWindow,QStackedWidget,QToolBar
from PySide6.QtGui import QAction
from ui.products_view import ProductsView
from ui.customers_view import CustomersView
from ui.pos_view import POSView

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Warehouse - DC")

        self.stack = QStackedWidget()

        self.products = ProductsView()
        self.customers = CustomersView()
        self.pos = POSView()

        self.stack.addWidget(self.products)
        self.stack.addWidget(self.customers)
        self.stack.addWidget(self.pos)

        self.setCentralWidget(self.stack)
        self.create_toolbar()

    def create_toolbar(self):

        toolbar = QToolBar()
        self.addToolBar(toolbar)

        btn_products = QAction("Produkty",self)
        btn_customers = QAction("Zákazníci",self)
        btn_pos = QAction("Kasa",self)

        btn_products.triggered.connect(
            lambda:self.stack.setCurrentWidget(self.products)
        )

        btn_customers.triggered.connect(
            lambda:self.stack.setCurrentWidget(self.customers)
        )

        btn_pos.triggered.connect(
            lambda:self.stack.setCurrentWidget(self.pos)
        )

        toolbar.addAction(btn_products)
        toolbar.addAction(btn_customers)
        toolbar.addAction(btn_pos)
