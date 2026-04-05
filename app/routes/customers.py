from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models import Customer

router = APIRouter(prefix="/customers", tags=["customers"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
def list_customers(request: Request, db: Session = Depends(get_db)):
    customers = db.query(Customer).order_by(Customer.name).all()
    return templates.TemplateResponse(
        request=request,
        name="customers_list.html",
        context={
            "request": request,
            "customers": customers,
            "msg": request.query_params.get("msg"),
            "error": request.query_params.get("error"),
        },
    )


@router.get("/new", response_class=HTMLResponse)
def new_customer_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="customer_form.html",
        context={"request": request, "customer": None, "action": "/customers"},
    )


@router.post("", response_class=RedirectResponse)
def create_customer(
    name: str = Form(...),
    company: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    org_number: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    customer = Customer(
        name=name.strip(),
        company=company.strip() if company else None,
        email=email.strip() if email else None,
        phone=phone.strip() if phone else None,
        address=address.strip() if address else None,
        org_number=org_number.strip() if org_number else None,
    )
    db.add(customer)
    db.commit()
    return RedirectResponse("/customers?msg=Customer+created", status_code=303)


@router.get("/{customer_id}/edit", response_class=HTMLResponse)
def edit_customer_form(customer_id: int, request: Request, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return RedirectResponse("/customers?error=Customer+not+found", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="customer_form.html",
        context={
            "request": request,
            "customer": customer,
            "action": f"/customers/{customer_id}/edit",
        },
    )


@router.post("/{customer_id}/edit", response_class=RedirectResponse)
def update_customer(
    customer_id: int,
    name: str = Form(...),
    company: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    org_number: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return RedirectResponse("/customers?error=Customer+not+found", status_code=303)
    customer.name = name.strip()
    customer.company = company.strip() if company else None
    customer.email = email.strip() if email else None
    customer.phone = phone.strip() if phone else None
    customer.address = address.strip() if address else None
    customer.org_number = org_number.strip() if org_number else None
    db.commit()
    return RedirectResponse("/customers?msg=Customer+updated", status_code=303)


@router.post("/{customer_id}/delete", response_class=RedirectResponse)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if customer:
        db.delete(customer)
        db.commit()
    return RedirectResponse("/customers?msg=Customer+deleted", status_code=303)
