"""Generate quote PDFs with reportlab."""
from io import BytesIO
from datetime import date, timedelta

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)
from reportlab.lib.enums import TA_RIGHT, TA_CENTER

from app import config

PRIMARY = colors.HexColor("#1e3a5f")
ACCENT = colors.HexColor("#2563eb")
LIGHT_GRAY = colors.HexColor("#f1f5f9")
MID_GRAY = colors.HexColor("#94a3b8")
TEXT = colors.HexColor("#1e293b")
WHITE = colors.white


def _styles():
    base = getSampleStyleSheet()
    return {
        "company": ParagraphStyle(
            "company",
            fontName="Helvetica-Bold",
            fontSize=14,
            textColor=PRIMARY,
            leading=18,
        ),
        "company_sub": ParagraphStyle(
            "company_sub",
            fontName="Helvetica",
            fontSize=8,
            textColor=MID_GRAY,
            leading=12,
        ),
        "heading": ParagraphStyle(
            "heading",
            fontName="Helvetica-Bold",
            fontSize=22,
            textColor=PRIMARY,
            alignment=TA_RIGHT,
        ),
        "meta_label": ParagraphStyle(
            "meta_label",
            fontName="Helvetica-Bold",
            fontSize=8,
            textColor=MID_GRAY,
            leading=12,
            alignment=TA_RIGHT,
        ),
        "meta_value": ParagraphStyle(
            "meta_value",
            fontName="Helvetica",
            fontSize=9,
            textColor=TEXT,
            leading=12,
            alignment=TA_RIGHT,
        ),
        "customer_label": ParagraphStyle(
            "customer_label",
            fontName="Helvetica-Bold",
            fontSize=8,
            textColor=MID_GRAY,
            leading=12,
        ),
        "customer_value": ParagraphStyle(
            "customer_value",
            fontName="Helvetica",
            fontSize=10,
            textColor=TEXT,
            leading=14,
        ),
        "section_title": ParagraphStyle(
            "section_title",
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=WHITE,
        ),
        "cell": ParagraphStyle(
            "cell",
            fontName="Helvetica",
            fontSize=9,
            textColor=TEXT,
            leading=12,
        ),
        "cell_bold": ParagraphStyle(
            "cell_bold",
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=TEXT,
            leading=12,
        ),
        "total_label": ParagraphStyle(
            "total_label",
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=TEXT,
            alignment=TA_RIGHT,
        ),
        "total_value": ParagraphStyle(
            "total_value",
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=TEXT,
            alignment=TA_RIGHT,
        ),
        "grand_total_label": ParagraphStyle(
            "grand_total_label",
            fontName="Helvetica-Bold",
            fontSize=12,
            textColor=WHITE,
            alignment=TA_RIGHT,
        ),
        "grand_total_value": ParagraphStyle(
            "grand_total_value",
            fontName="Helvetica-Bold",
            fontSize=12,
            textColor=WHITE,
            alignment=TA_RIGHT,
        ),
        "notes": ParagraphStyle(
            "notes",
            fontName="Helvetica",
            fontSize=9,
            textColor=TEXT,
            leading=13,
        ),
        "footer": ParagraphStyle(
            "footer",
            fontName="Helvetica",
            fontSize=8,
            textColor=MID_GRAY,
            alignment=TA_CENTER,
        ),
    }


def _fmt_sek(amount: float) -> str:
    return f"{amount:,.2f} SEK".replace(",", " ")


def generate_quote_pdf(quote) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    s = _styles()
    story = []
    page_w = A4[0] - 40 * mm

    company_lines = [
        Paragraph(config.COMPANY_NAME, s["company"]),
        Paragraph(config.COMPANY_ADDRESS, s["company_sub"]),
    ]
    if config.COMPANY_PHONE:
        company_lines.append(Paragraph(f"Phone: {config.COMPANY_PHONE}", s["company_sub"]))
    if config.COMPANY_EMAIL:
        company_lines.append(Paragraph(config.COMPANY_EMAIL, s["company_sub"]))
    if config.COMPANY_ORG_NUMBER:
        company_lines.append(Paragraph(f"Org no: {config.COMPANY_ORG_NUMBER}", s["company_sub"]))

    valid_until = (
        quote.created_at.date() + timedelta(days=quote.valid_days)
        if quote.created_at
        else date.today() + timedelta(days=quote.valid_days)
    )

    quote_meta = [
        Paragraph("QUOTE", s["heading"]),
        Paragraph(f"No: {quote.quote_number}", s["meta_value"]),
        Paragraph(
            f"Date: {quote.created_at.strftime('%Y-%m-%d') if quote.created_at else date.today().strftime('%Y-%m-%d')}",
            s["meta_value"],
        ),
        Paragraph(f"Valid until: {valid_until.strftime('%Y-%m-%d')}", s["meta_value"]),
    ]

    header_table = Table(
        [[company_lines, quote_meta]],
        colWidths=[page_w * 0.55, page_w * 0.45],
    )
    header_table.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ])
    )
    story.append(header_table)
    story.append(Spacer(1, 6 * mm))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY))
    story.append(Spacer(1, 5 * mm))

    c = quote.customer
    customer_lines = [Paragraph("TO", s["customer_label"])]
    if c.company:
        customer_lines.append(Paragraph(c.company, s["customer_value"]))
    customer_lines.append(Paragraph(c.name, s["customer_value"]))
    if c.address:
        for line in c.address.splitlines():
            if line.strip():
                customer_lines.append(Paragraph(line, s["customer_value"]))
    if c.email:
        customer_lines.append(Paragraph(c.email, s["customer_value"]))
    if c.phone:
        customer_lines.append(Paragraph(c.phone, s["customer_value"]))
    if c.org_number:
        customer_lines.append(Paragraph(f"Org no: {c.org_number}", s["customer_value"]))

    title_lines = [
        Paragraph("SUBJECT", s["customer_label"]),
        Paragraph(quote.title, s["customer_value"]),
    ]
    if quote.description:
        title_lines.append(Spacer(1, 3 * mm))
        for para in quote.description.splitlines():
            if para.strip():
                title_lines.append(Paragraph(para, s["notes"]))

    customer_table = Table(
        [[customer_lines, title_lines]],
        colWidths=[page_w * 0.45, page_w * 0.55],
    )
    customer_table.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ])
    )
    story.append(customer_table)
    story.append(Spacer(1, 6 * mm))

    col_widths = [page_w * 0.45, page_w * 0.10, page_w * 0.10, page_w * 0.17, page_w * 0.18]
    header_row = [
        Paragraph("DESCRIPTION", s["section_title"]),
        Paragraph("QTY", s["section_title"]),
        Paragraph("UNIT", s["section_title"]),
        Paragraph("UNIT PRICE", s["section_title"]),
        Paragraph("AMOUNT", s["section_title"]),
    ]
    rows = [header_row]
    for item in quote.items:
        rows.append([
            Paragraph(item.description, s["cell"]),
            Paragraph(str(int(item.quantity) if item.quantity == int(item.quantity) else item.quantity), s["cell"]),
            Paragraph(item.unit, s["cell"]),
            Paragraph(_fmt_sek(item.unit_price), s["cell"]),
            Paragraph(_fmt_sek(item.total), s["cell_bold"]),
        ])

    items_table = Table(rows, colWidths=col_widths, repeatRows=1)
    items_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("LINEABOVE", (0, 0), (-1, 0), 0, WHITE),
            ("LINEBELOW", (0, -1), (-1, -1), 1, MID_GRAY),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ])
    )
    story.append(items_table)
    story.append(Spacer(1, 4 * mm))

    ex_vat = quote.total_ex_vat
    vat = quote.vat_amount
    incl_vat = quote.total_incl_vat

    summary_rows = [
        ["", "", Paragraph("Subtotal (excl. VAT)", s["total_label"]), Paragraph(_fmt_sek(ex_vat), s["total_value"])],
        ["", "", Paragraph("VAT 25%", s["total_label"]), Paragraph(_fmt_sek(vat), s["total_value"])],
    ]
    summary_table = Table(
        summary_rows,
        colWidths=[page_w * 0.35, page_w * 0.15, page_w * 0.30, page_w * 0.20],
    )
    summary_table.setStyle(
        TableStyle([
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ])
    )
    story.append(summary_table)

    grand_total_rows = [
        [
            "",
            Paragraph("TOTAL (INCL. VAT)", s["grand_total_label"]),
            Paragraph(_fmt_sek(incl_vat), s["grand_total_value"]),
        ]
    ]
    gt_table = Table(
        grand_total_rows,
        colWidths=[page_w * 0.35, page_w * 0.45, page_w * 0.20],
    )
    gt_table.setStyle(
        TableStyle([
            ("BACKGROUND", (1, 0), (-1, -1), PRIMARY),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ])
    )
    story.append(gt_table)
    story.append(Spacer(1, 6 * mm))

    if quote.notes:
        story.append(HRFlowable(width="100%", thickness=0.5, color=MID_GRAY))
        story.append(Spacer(1, 3 * mm))
        story.append(Paragraph("Notes", s["customer_label"]))
        story.append(Spacer(1, 2 * mm))
        for line in quote.notes.splitlines():
            if line.strip():
                story.append(Paragraph(line, s["notes"]))
        story.append(Spacer(1, 4 * mm))

    story.append(HRFlowable(width="100%", thickness=0.5, color=MID_GRAY))
    story.append(Spacer(1, 3 * mm))
    conditions = [
        "Payment terms: Net 30 days",
        f"This quote is valid for {quote.valid_days} days from issue date.",
        "VAT: 25% is added to listed prices.",
    ]
    if config.COMPANY_ORG_NUMBER:
        conditions.append(f"Org no: {config.COMPANY_ORG_NUMBER}")

    story.append(
        Paragraph("  |  ".join(conditions), s["footer"])
    )

    doc.build(story)
    return buffer.getvalue()
