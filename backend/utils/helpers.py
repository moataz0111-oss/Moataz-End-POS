# Utility functions
from datetime import datetime, timezone
import uuid
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import os
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent

def generate_id():
    """Generate unique ID"""
    return str(uuid.uuid4())

def get_current_timestamp():
    """Get current UTC timestamp as ISO string"""
    return datetime.now(timezone.utc).isoformat()

def format_price(amount):
    """Format price with Iraqi Dinar"""
    return f"{amount:,.0f} د.ع"

# Register Arabic font for PDF
def register_arabic_font():
    """Register Arabic font for PDF generation"""
    font_path = ROOT_DIR / "fonts" / "NotoSansArabic-Regular.ttf"
    if font_path.exists():
        pdfmetrics.registerFont(TTFont('Arabic', str(font_path)))
        return 'Arabic'
    return 'Helvetica'

def create_pdf_styles():
    """Create PDF styles with Arabic support"""
    styles = getSampleStyleSheet()
    
    # Try to use Arabic font
    font_name = register_arabic_font()
    
    styles.add(ParagraphStyle(
        name='ArabicTitle',
        fontName=font_name,
        fontSize=18,
        leading=22,
        alignment=1,  # Center
        spaceAfter=20
    ))
    
    styles.add(ParagraphStyle(
        name='ArabicNormal',
        fontName=font_name,
        fontSize=10,
        leading=14,
        alignment=2  # Right for Arabic
    ))
    
    styles.add(ParagraphStyle(
        name='ArabicHeader',
        fontName=font_name,
        fontSize=12,
        leading=16,
        alignment=1,
        textColor=colors.white
    ))
    
    return styles

def generate_pdf_report(title, headers, data, totals=None, summary=None):
    """Generate a PDF report with Arabic support"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        rightMargin=1*cm,
        leftMargin=1*cm,
        topMargin=1*cm,
        bottomMargin=1*cm
    )
    
    styles = create_pdf_styles()
    elements = []
    
    # Title
    elements.append(Paragraph(title, styles['ArabicTitle']))
    elements.append(Spacer(1, 20))
    
    # Summary section if provided
    if summary:
        for key, value in summary.items():
            elements.append(Paragraph(f"{key}: {value}", styles['ArabicNormal']))
        elements.append(Spacer(1, 20))
    
    # Table data
    table_data = [headers] + data
    
    # Add totals row if provided
    if totals:
        table_data.append(totals)
    
    # Create table
    col_widths = [doc.width / len(headers)] * len(headers)
    table = Table(table_data, colWidths=col_widths)
    
    # Table style
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
    ])
    
    # Totals row style
    if totals:
        style.add('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E6E6E6'))
        style.add('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')
    
    table.setStyle(style)
    elements.append(table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer
