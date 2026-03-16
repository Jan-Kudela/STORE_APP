
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    ico = Column(String)
    dic = Column(String)
    email = Column(String)
    phone = Column(String)
    address = Column(String)

class Product(Base):

    __tablename__ = "products"

    id = Column(Integer, primary_key=True)

    name = Column(String)

    purchase_price = Column(Float)   # nákup bez DPH
    sale_price = Column(Float)       # prodej bez DPH

    vat = Column(Float)              # např 21

    stock = Column(Integer)

    ean = Column(String)

    # ----- výpočty -----

    @property
    def purchase_price_vat(self):
        return round(self.purchase_price * (1 + self.vat/100),2)

    @property
    def sale_price_vat(self):
        return round(self.sale_price * (1 + self.vat/100),2)

    @property
    def margin_kc(self):
        return round(self.sale_price - self.purchase_price,2)

    @property
    def margin_percent(self):

        if self.purchase_price == 0:
            return 0

        return round((self.margin_kc / self.purchase_price) * 100,2)

class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True)
    number = Column(String)
    items = relationship("InvoiceItem", cascade="all, delete")

class InvoiceItem(Base):
    __tablename__ = "invoice_items"
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    name = Column(String)
    quantity = Column(Integer)
    price = Column(Float)
