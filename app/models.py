from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    company = Column(String(200))
    email = Column(String(200))
    phone = Column(String(50))
    address = Column(Text)
    org_number = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())

    quotes = relationship("Quote", back_populates="customer")


class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    quote_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    title = Column(String(300), nullable=False)
    description = Column(Text)
    status = Column(String(20), default="draft")
    valid_days = Column(Integer, default=30)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    customer = relationship("Customer", back_populates="quotes")
    items = relationship("QuoteItem", back_populates="quote", cascade="all, delete-orphan")

    @property
    def total_ex_vat(self) -> float:
        return sum(item.total for item in self.items)

    @property
    def vat_amount(self) -> float:
        return round(self.total_ex_vat * 0.25, 2)

    @property
    def total_incl_vat(self) -> float:
        return round(self.total_ex_vat * 1.25, 2)

    @property
    def status_label(self) -> str:
        labels = {
            "draft": "Draft",
            "sent": "Sent",
            "accepted": "Accepted",
            "rejected": "Rejected",
        }
        return labels.get(self.status, self.status)

    @property
    def status_color(self) -> str:
        colors = {
            "draft": "gray",
            "sent": "blue",
            "accepted": "green",
            "rejected": "red",
        }
        return colors.get(self.status, "gray")


class QuoteItem(Base):
    __tablename__ = "quote_items"

    id = Column(Integer, primary_key=True, index=True)
    quote_id = Column(Integer, ForeignKey("quotes.id"), nullable=False)
    description = Column(String(500), nullable=False)
    quantity = Column(Float, default=1.0)
    unit = Column(String(50), default="pcs")
    unit_price = Column(Float, nullable=False)

    quote = relationship("Quote", back_populates="items")

    @property
    def total(self) -> float:
        return round(self.quantity * self.unit_price, 2)
