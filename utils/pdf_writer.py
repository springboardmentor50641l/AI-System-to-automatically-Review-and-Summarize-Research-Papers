from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import textwrap
import os


def save_text_as_pdf(text: str, output_path: str):
    """
    Converts long text into a properly formatted PDF.
    """

    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    x_margin = 1 * inch
    y_margin = height - 1 * inch
    max_width = width - 2 * inch

    text_object = c.beginText(x_margin, y_margin)
    text_object.setFont("Times-Roman", 11)

    for line in text.split("\n"):
        wrapped_lines = textwrap.wrap(line, 95)
        if not wrapped_lines:
            text_object.textLine("")
        for wrap in wrapped_lines:
            if text_object.getY() < 1 * inch:
                c.drawText(text_object)
                c.showPage()
                text_object = c.beginText(x_margin, height - 1 * inch)
                text_object.setFont("Times-Roman", 11)
            text_object.textLine(wrap)

    c.drawText(text_object)
    c.save()
