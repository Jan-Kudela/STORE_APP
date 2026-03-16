
from database.db import Session
from database.models import Product

def decrease_stock(product_id, qty):
    session = Session()
    product = session.get(Product, product_id)
    if not product:
        return
    product.stock -= qty
    if product.stock < 0:
        product.stock = 0
    session.commit()
