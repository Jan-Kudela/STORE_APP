from reportlab.pdfgen import canvas


def create_invoice_pdf():

    c = canvas.Canvas("invoice.pdf")

    c.drawString(100, 800, "FAKTURA")

    c.drawString(100, 760, "Zákazník: Testovací zákazník")

    c.drawString(100, 720, "Produkt A - 2 ks - 500 Kč")

    c.drawString(100, 680, "Celkem: 1000 Kč")

    c.save()