from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Customer, Quote, QuoteItem
from app.utils.pdf import generate_quote_pdf
from app.utils.email_sender import send_quote_email, EmailError

router = APIRouter(prefix="/quotes", tags=["quotes"])
templates = Jinja2Templates(directory="app/templates")


def _next_quote_number(db: Session) -> str:
    year = date.today().year
    count = db.query(Quote).filter(Quote.quote_number.like(f"OFF-{year}-%")).count()
    return f"OFF-{year}-{count + 1:04d}"


@router.get("", response_class=HTMLResponse)
def list_quotes(
    request: Request,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Quote).order_by(Quote.created_at.desc())
    if status:
        query = query.filter(Quote.status == status)
    quotes = query.all()
    return templates.TemplateResponse(
        request=request,
        name="quotes_list.html",
        context={
            "request": request,
            "quotes": quotes,
            "filter_status": status,
            "msg": request.query_params.get("msg"),
            "error": request.query_params.get("error"),
        },
    )


@router.get("/new", response_class=HTMLResponse)
def new_quote_form(request: Request, db: Session = Depends(get_db)):
    customers = db.query(Customer).order_by(Customer.name).all()
    selected_customer_id = request.query_params.get("customer")
    return templates.TemplateResponse(
        request=request,
        name="quote_form.html",
        context={
            "request": request,
            "quote": None,
            "customers": customers,
            "action": "/quotes",
            "selected_customer_id": int(selected_customer_id) if selected_customer_id and selected_customer_id.isdigit() else None,
        },
    )


@router.post("", response_class=RedirectResponse)
async def create_quote(request: Request, db: Session = Depends(get_db)):
    form = await request.form()

    customer_id = int(form["customer_id"])
    title = str(form["title"]).strip()
    description = str(form.get("description", "")).strip() or None
    valid_days = int(form.get("valid_days", 30))
    notes = str(form.get("notes", "")).strip() or None

    quote = Quote(
        quote_number=_next_quote_number(db),
        customer_id=customer_id,
        title=title,
        description=description,
        valid_days=valid_days,
        notes=notes,
        status="draft",
    )
    db.add(quote)
    db.flush()

    i = 0
    while f"item_description[{i}]" in form:
        desc = str(form[f"item_description[{i}]"]).strip()
        qty_raw = str(form.get(f"item_quantity[{i}]", "1")).replace(",", ".")
        unit = str(form.get(f"item_unit[{i}]", "pcs")).strip()
        price_raw = str(form.get(f"item_unit_price[{i}]", "0")).replace(",", ".")
        if desc:
            item = QuoteItem(
                quote_id=quote.id,
                description=desc,
                quantity=float(qty_raw) if qty_raw else 1.0,
                unit=unit,
                unit_price=float(price_raw) if price_raw else 0.0,
            )
            db.add(item)
        i += 1

    db.commit()
    return RedirectResponse(f"/quotes/{quote.id}?msg=Quote+created", status_code=303)


@router.get("/{quote_id}", response_class=HTMLResponse)
def view_quote(quote_id: int, request: Request, db: Session = Depends(get_db)):
    quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if not quote:
        return RedirectResponse("/quotes?error=Quote+not+found", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="quote_detail.html",
        context={
            "request": request,
            "quote": quote,
            "msg": request.query_params.get("msg"),
            "error": request.query_params.get("error"),
        },
    )


@router.get("/{quote_id}/edit", response_class=HTMLResponse)
def edit_quote_form(quote_id: int, request: Request, db: Session = Depends(get_db)):
    quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if not quote:
        return RedirectResponse("/quotes?error=Quote+not+found", status_code=303)
    customers = db.query(Customer).order_by(Customer.name).all()
    return templates.TemplateResponse(
        request=request,
        name="quote_form.html",
        context={
            "request": request,
            "quote": quote,
            "customers": customers,
            "action": f"/quotes/{quote_id}/edit",
        },
    )


@router.post("/{quote_id}/edit", response_class=RedirectResponse)
async def update_quote(quote_id: int, request: Request, db: Session = Depends(get_db)):
    quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if not quote:
        return RedirectResponse("/quotes?error=Quote+not+found", status_code=303)

    form = await request.form()
    quote.customer_id = int(form["customer_id"])
    quote.title = str(form["title"]).strip()
    quote.description = str(form.get("description", "")).strip() or None
    quote.valid_days = int(form.get("valid_days", 30))
    quote.notes = str(form.get("notes", "")).strip() or None

    for item in list(quote.items):
        db.delete(item)
    db.flush()

    i = 0
    while f"item_description[{i}]" in form:
        desc = str(form[f"item_description[{i}]"]).strip()
        qty_raw = str(form.get(f"item_quantity[{i}]", "1")).replace(",", ".")
        unit = str(form.get(f"item_unit[{i}]", "pcs")).strip()
        price_raw = str(form.get(f"item_unit_price[{i}]", "0")).replace(",", ".")
        if desc:
            item = QuoteItem(
                quote_id=quote.id,
                description=desc,
                quantity=float(qty_raw) if qty_raw else 1.0,
                unit=unit,
                unit_price=float(price_raw) if price_raw else 0.0,
            )
            db.add(item)
        i += 1

    db.commit()
    return RedirectResponse(f"/quotes/{quote_id}?msg=Quote+updated", status_code=303)


@router.get("/{quote_id}/pdf")
def download_pdf(quote_id: int, db: Session = Depends(get_db)):
    quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if not quote:
        return Response("Quote not found", status_code=404)
    pdf_bytes = generate_quote_pdf(quote)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="Quote-{quote.quote_number}.pdf"'
        },
    )


@router.post("/{quote_id}/send-email", response_class=RedirectResponse)
def send_email(quote_id: int, db: Session = Depends(get_db)):
    quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if not quote:
        return RedirectResponse("/quotes?error=Quote+not+found", status_code=303)
    if not quote.customer.email:
        return RedirectResponse(
            f"/quotes/{quote_id}?error=Customer+is+missing+an+email+address", status_code=303
        )
    try:
        pdf_bytes = generate_quote_pdf(quote)
        send_quote_email(
            to_email=quote.customer.email,
            customer_name=quote.customer.name,
            quote_number=quote.quote_number,
            quote_title=quote.title,
            pdf_bytes=pdf_bytes,
        )
        quote.status = "sent"
        db.commit()
        return RedirectResponse(
            f"/quotes/{quote_id}?msg=Quote+sent+to+{quote.customer.email}",
            status_code=303,
        )
    except EmailError as exc:
        error_msg = str(exc).replace(" ", "+")
        return RedirectResponse(
            f"/quotes/{quote_id}?error={error_msg}", status_code=303
        )


@router.post("/{quote_id}/status", response_class=RedirectResponse)
async def update_status(
    quote_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    form = await request.form()
    new_status = str(form.get("status", "draft"))
    allowed = {"draft", "sent", "accepted", "rejected"}
    quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if quote and new_status in allowed:
        quote.status = new_status
        db.commit()
    return RedirectResponse(f"/quotes/{quote_id}?msg=Status+updated", status_code=303)


@router.post("/{quote_id}/delete", response_class=RedirectResponse)
def delete_quote(quote_id: int, db: Session = Depends(get_db)):
    quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if quote:
        db.delete(quote)
        db.commit()
    return RedirectResponse("/quotes?msg=Quote+deleted", status_code=303)
