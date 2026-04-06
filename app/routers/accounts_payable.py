from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import extract
from typing import Optional

from app.database import get_db
from app.models import AccountsPayable
from app.schemas import AccountsPayableCreate

router = APIRouter(prefix="/api/accounts-payable", tags=["Accounts Payable"])

def apply_filters(query, model, year, month):
    if year:
        query = query.filter(extract('year', model.invoice_date) == year)
    if month:
        query = query.filter(extract('month', model.invoice_date) == month)
    return query

@router.get("/")
def get_accounts_payable(
    db: Session = Depends(get_db),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None)
):
    query = db.query(AccountsPayable)
    query = apply_filters(query, AccountsPayable, year, month)
    rows = query.order_by(AccountsPayable.due_date).all()

    return [
        {
            "id": row.id,
            "vendor_name": row.vendor_name or "—",
            "vendor_code": row.vendor_code or "—",
            "invoice_number": row.invoice_number or "—",
            "invoice_date": str(row.invoice_date),
            "due_date": str(row.due_date),
            "amount": float(row.amount or 0),
            "paid_amount": float(row.paid_amount or 0),
            "balance": float(row.balance or 0),
            "category": row.category or "—",
            "payment_terms": row.payment_terms or "—",
            "status": row.status or "Pending",
            "currency": row.currency or "USD",
            "description": row.description or "—"
        }
        for row in rows
    ]

@router.get("/summary")
def get_accounts_payable_summary(
    db: Session = Depends(get_db),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None)
):
    query = db.query(AccountsPayable)
    query = apply_filters(query, AccountsPayable, year, month)
    rows = query.all()
    today = date.today()

    total_outstanding = sum(float(row.balance or 0) for row in rows)
    total_paid = sum(float(row.paid_amount or 0) for row in rows)
    total_invoices = len(rows)
    overdue_count = sum(1 for row in rows if float(row.balance or 0) > 0 and row.due_date < today)

    return {
        "total_outstanding": total_outstanding,
        "total_paid": total_paid,
        "total_invoices": total_invoices,
        "overdue_count": overdue_count
    }

@router.get("/aging")
def get_accounts_payable_aging(
    db: Session = Depends(get_db),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None)
):
    query = db.query(AccountsPayable)
    query = apply_filters(query, AccountsPayable, year, month)
    rows = query.all()
    today = date.today()

    current = 0
    bucket_1_30 = 0
    bucket_31_60 = 0
    bucket_61_90 = 0
    bucket_90_plus = 0

    for row in rows:
        balance = float(row.balance or 0)
        if balance <= 0: continue
        overdue_days = (today - row.due_date).days
        if overdue_days <= 0: current += balance
        elif 1 <= overdue_days <= 30: bucket_1_30 += balance
        elif 31 <= overdue_days <= 60: bucket_31_60 += balance
        elif 61 <= overdue_days <= 90: bucket_61_90 += balance
        else: bucket_90_plus += balance

    return {
        "current": current,
        "days_1_30": bucket_1_30,
        "days_31_60": bucket_31_60,
        "days_61_90": bucket_61_90,
        "days_90_plus": bucket_90_plus
    }

@router.post("/")
def create_accounts_payable(data: AccountsPayableCreate, db: Session = Depends(get_db)):
    new_entry = AccountsPayable(**data.dict())
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return {"message": "AP record added", "id": new_entry.id}