from database.db import Session
from database.models import Invoice, InvoiceItem

from database.db import Session
from database.models import Invoice, InvoiceItem


def create_invoice(customer, items):
    """
    customer: instance Customer nebo None (prodej u kasy bez zákazníka)
    items: list slovníků {"name", "qty", "price", "vat"}
    """
    session = Session()

    invoice = Invoice(
        number=generate_invoice_number(session),
        customer_id=customer.id if customer else None,
        total=0,
        vat=0,
        total_with_vat=0
    )

    session.add(invoice)
    session.flush()

    total = 0
    total_vat = 0

    for item in items:

        # cena v položce je s DPH, přepočítáme základ
        vat_rate = item["vat"] / 100
        price_with_vat = item["price"]
        price_without_vat = round(price_with_vat / (1 + vat_rate), 4)
        line_total_without_vat = round(price_without_vat * item["qty"], 2)
        line_vat = round(line_total_without_vat * vat_rate, 2)

        total += line_total_without_vat
        total_vat += line_vat

        db_item = InvoiceItem(
            invoice_id=invoice.id,
            product_name=item["name"],
            quantity=item["qty"],
            price=price_without_vat,
            vat=item["vat"]
        )

        session.add(db_item)

    invoice.total = round(total, 2)
    invoice.vat = round(total_vat, 2)
    invoice.total_with_vat = round(total + total_vat, 2)

    session.commit()
    session.close()

    return invoice


def generate_invoice_number(session):
    """Generuje číslo faktury jako rok + pořadové číslo podle MAX id — nevznikají duplicity po smazání."""
    from sqlalchemy import func
    import datetime

    year = datetime.date.today().year
    max_id = session.query(func.max(Invoice.id)).scalar() or 0
    return f"{year}{max_id + 1:04d}"


def create_invoice_pdf(customer_data, items):
    """
    Stub pro generování PDF faktury.
    customer_data: dict {"name": ..., "address": ...}
    items: list of (name, qty, price)
    Plná implementace bude doplněna později.
    """
    print(f"[create_invoice_pdf] PDF pro zákazníka: {customer_data.get('name', 'N/A')}, položek: {len(items)}")