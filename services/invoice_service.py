from database.db import Session
from database.models import Invoice, InvoiceItem

def create_invoice(customer, items):

    session = Session()

    total = 0

    invoice = Invoice(
        number=generate_invoice_number(session),
        customer_id=customer.id,
        total=0,
        vat=0,
        total_with_vat=0
    )

    session.add(invoice)
    session.flush()

    for item in items:

        line_total = item["qty"] * item["price"]
        total += line_total

        db_item = InvoiceItem(
            invoice_id=invoice.id,
            product_name=item["name"],
            quantity=item["qty"],
            price=item["price"],
            vat=item["vat"]
        )

        session.add(db_item)

    vat = total * 0.21
    total_with_vat = total + vat

    invoice.total = total
    invoice.vat = vat
    invoice.total_with_vat = total_with_vat

    session.commit()

    return invoice


def generate_invoice_number(session):
    count = session.query(Invoice).count()
    return f"2026{count+1:04d}"