import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from sqlalchemy import text

from app.database import engine, Base, SessionLocal
from app.models import Customer, Quote
from app.routes import customers, quotes, ai
from app import config

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Quote Generator",
    description="Automated quote generator for small businesses",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="app/templates")

app.include_router(customers.router)
app.include_router(quotes.router)
app.include_router(ai.router)


@app.get("/health")
def health_check():
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        customer_count = db.query(Customer).count()
        quote_count = db.query(Quote).count()
        return {
            "status": "ok",
            "database": "connected",
            "customers": customer_count,
            "quotes": quote_count,
        }
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    db = SessionLocal()
    try:
        customer_count = db.query(Customer).count()
        quote_count = db.query(Quote).count()
        recent_quotes = (
            db.query(Quote).order_by(Quote.created_at.desc()).limit(6).all()
        )
        accepted = db.query(Quote).filter(Quote.status == "accepted").all()
        total_accepted = sum(q.total_incl_vat for q in accepted)
        status_counts = {
            "draft": db.query(Quote).filter(Quote.status == "draft").count(),
            "sent": db.query(Quote).filter(Quote.status == "sent").count(),
            "accepted": db.query(Quote).filter(Quote.status == "accepted").count(),
            "rejected": db.query(Quote).filter(Quote.status == "rejected").count(),
        }
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "request": request,
                "customer_count": customer_count,
                "quote_count": quote_count,
                "recent_quotes": recent_quotes,
                "total_accepted": total_accepted,
                "status_counts": status_counts,
                "company_name": config.COMPANY_NAME,
            },
        )
    finally:
        db.close()
