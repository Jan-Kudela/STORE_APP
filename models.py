from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Customer(Base):

    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    ico = Column(String)
    dic = Column(String)
    address = Column(String)

    invoices = relationship("Invoice", back_populates="customer")


class Product(Base):

    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)
    stock = Column(Integer)
    ean = Column(String)


class Invoice(Base):

    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))

    customer = relationship("Customer", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice")


class InvoiceItem(Base):

    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    product_name = Column(String)
    quantity = Column(Integer)
    price = Column(Float)

    invoice = relationship("Invoice", back_populates="items")