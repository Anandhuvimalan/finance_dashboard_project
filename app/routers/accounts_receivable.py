from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import extract
from typing import Optional

from app.database import get_db
from app.models import AccountsReceivable
from app.schemas import AccountsReceivableCreate

router = APIRouter(prefix="/api/accounts-receivable", tags=["Accounts Receivable"])

def apply_filters(query, model, year, month):
    if year:
        query = query.filter(extract('year', model.invoice_date) == year)
    if month:
        query = query.filter(extract('month', model.invoice_date) == month)
    return query

@router.get("/")
def get_accounts_receivable(
    db: Session = Depends(get_db),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None)
):
    query = db.query(AccountsReceivable)
    query = apply_filters(query, AccountsReceivable, year, month)
    rows = query.order_by(AccountsReceivable.due_date).all()

    return [
        {
            "id": row.id,
            "customer_name": row.customer_name or "—",
            "customer_code": row.customer_code or "—",
            "invoice_number": row.invoice_number or "—",
            "invoice_date": str(row.invoice_date),
            "due_date": str(row.due_date),
            "amount": float(row.amount or 0),
            "received_amount": float(row.received_amount or 0),
            "balance": float(row.balance or 0),
            "category": row.category or "—",
            "status": row.status or "Pending"
        }
        for row in rows
    ]

@router.get("/summary")
def get_accounts_receivable_summary(
    db: Session = Depends(get_db),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None)
):
    query = db.query(AccountsReceivable)
    query = apply_filters(query, AccountsReceivable, year, month)
    rows = query.all()
    today = date.today()

    total_outstanding = sum(float(row.balance or 0) for row in rows)
    total_received = sum(float(row.received_amount or 0) for row in rows)
    total_invoices = len(rows)
    overdue_count = sum(1 for row in rows if float(row.balance or 0) > 0 and row.due_date < today)

    return {
        "total_outstanding": total_outstanding,
        "total_received": total_received,
        "total_invoices": total_invoices,
        "overdue_count": overdue_count
    }

@router.post("/")
def create_accounts_receivable(data: AccountsReceivableCreate, db: Session = Depends(get_db)):
    new_entry = AccountsReceivable(**data.dict())
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return {"message": "AR record added", "id": new_entry.id}