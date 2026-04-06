from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import extract
from typing import Optional

from app.database import get_db
from app.models import GeneralLedger
from app.schemas import GeneralLedgerCreate

router = APIRouter(prefix="/api/general-ledger", tags=["General Ledger"])

def apply_filters(query, model, year, month):
    if year:
        query = query.filter(extract('year', model.entry_date) == year)
    if month:
        query = query.filter(extract('month', model.entry_date) == month)
    return query

@router.get("/")
def get_general_ledger(
    db: Session = Depends(get_db),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None)
):
    query = db.query(GeneralLedger)
    query = apply_filters(query, GeneralLedger, year, month)
    rows = query.order_by(GeneralLedger.entry_date).all()

    return [
        {
            "id": row.id,
            "entry_date": str(row.entry_date),
            "posting_date": str(row.posting_date),
            "account_code": row.account_code or "—",
            "account_name": row.account_name or "—",
            "debit": float(row.debit or 0),
            "credit": float(row.credit or 0),
            "description": row.description or "—",
            "reference": row.reference or "—",
            "journal_type": row.journal_type or "—",
            "department": row.department or "—",
            "cost_center": row.cost_center or "—",
            "fiscal_period": row.fiscal_period or "—",
            "is_reconciled": bool(row.is_reconciled)
        }
        for row in rows
    ]

@router.get("/summary")
def get_general_ledger_summary(
    db: Session = Depends(get_db),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None)
):
    query = db.query(GeneralLedger)
    query = apply_filters(query, GeneralLedger, year, month)
    rows = query.all()

    total_debit = sum(float(row.debit or 0) for row in rows)
    total_credit = sum(float(row.credit or 0) for row in rows)
    total_entries = len(rows)
    net_balance = total_debit - total_credit

    return {
        "total_debit": total_debit,
        "total_credit": total_credit,
        "total_entries": total_entries,
        "net_balance": net_balance
    }

@router.get("/chart-summary")
def get_general_ledger_chart_summary(
    db: Session = Depends(get_db),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None)
):
    query = db.query(GeneralLedger)
    query = apply_filters(query, GeneralLedger, year, month)
    rows = query.order_by(GeneralLedger.entry_date).all()

    date_map = {}
    for row in rows:
        date_key = str(row.entry_date)
        if date_key not in date_map:
            date_map[date_key] = {"date": date_key, "debit": 0, "credit": 0}
        date_map[date_key]["debit"] += float(row.debit or 0)
        date_map[date_key]["credit"] += float(row.credit or 0)

    result = list(date_map.values())
    result.sort(key=lambda x: x["date"])
    return result

@router.post("/")
def create_general_ledger(data: GeneralLedgerCreate, db: Session = Depends(get_db)):
    new_entry = GeneralLedger(**data.dict())
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return {"message": "GL entry added", "id": new_entry.id}