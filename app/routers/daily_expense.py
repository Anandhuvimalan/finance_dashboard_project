from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import Optional

from app.database import get_db
from app.models import DailyExpense
from app.schemas import DailyExpenseCreate

router = APIRouter(prefix="/api/daily-expense", tags=["Daily Expense"])

def apply_filters(query, model, year, month):
    if year:
        query = query.filter(extract('year', model.date) == year)
    if month:
        query = query.filter(extract('month', model.date) == month)
    return query

@router.get("/")
def get_daily_expense(
    db: Session = Depends(get_db),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None)
):
    query = db.query(DailyExpense)
    query = apply_filters(query, DailyExpense, year, month)
    rows = query.order_by(DailyExpense.date).all()

    return [
        {
            "id": row.id,
            "date": str(row.date),
            "category": row.category or "—",
            "subcategory": row.subcategory or "—",
            "description": row.description or "—",
            "amount": float(row.amount or 0),
            "department": row.department or "—",
            "vendor": row.vendor or "—",
            "cost_center": row.cost_center or "—",
            "approved_by": row.approved_by or "—",
            "status": row.status or "Pending"
        }
        for row in rows
    ]

@router.get("/summary")
def get_daily_expense_summary(
    db: Session = Depends(get_db),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None)
):
    query = db.query(DailyExpense)
    query = apply_filters(query, DailyExpense, year, month)
    rows = query.all()

    total_expense = sum(float(row.amount or 0) for row in rows)
    total_records = len(rows)
    approved_count = sum(1 for row in rows if (row.status or "").lower() == "approved")
    pending_count = sum(1 for row in rows if (row.status or "").lower() == "pending")

    return {
        "total_expense": total_expense,
        "total_records": total_records,
        "approved_count": approved_count,
        "pending_count": pending_count
    }

@router.get("/category-summary")
def get_daily_expense_category_summary(
    db: Session = Depends(get_db),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None)
):
    query = db.query(DailyExpense)
    query = apply_filters(query, DailyExpense, year, month)
    rows = query.all()

    category_totals = {}
    for row in rows:
        category = row.category or "Unknown"
        category_totals[category] = category_totals.get(category, 0) + float(row.amount or 0)

    result = [{"category": c, "amount": float(a)} for c, a in category_totals.items()]
    result.sort(key=lambda x: x["amount"], reverse=True)
    return result

@router.post("/")
def create_daily_expense(data: DailyExpenseCreate, db: Session = Depends(get_db)):
    new_entry = DailyExpense(**data.dict())
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return {"message": "Expense record added", "id": new_entry.id}