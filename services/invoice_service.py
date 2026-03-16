
from reportlab.pdfgen import canvas

def create_invoice_pdf(items):
    c = canvas.Canvas("invoice.pdf")
    y = 800
    c.drawString(100,y,"FAKTURA")
    y -= 40
    total = 0
    for name,qty,price in items:
        line = f"{name}  {qty} ks  {price} Kč"
        c.drawString(100,y,line)
        y -= 25
        total += qty*price
    y -= 20
    c.drawString(100,y,f"Celkem: {total} Kč")
    c.save()
