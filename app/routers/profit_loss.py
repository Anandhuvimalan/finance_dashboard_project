from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import extract
from typing import Optional

from app.database import get_db
from app.models import ProfitLossStatement
from app.schemas import ProfitLossCreate

router = APIRouter(prefix="/api/profit-loss", tags=["Profit & Loss"])

def apply_filters(query, model, year, month):
    if year:
        query = query.filter(extract('year', model.period_start) == year)
    if month:
        query = query.filter(extract('month', model.period_start) == month)
    return query

@router.get("/")
def get_profit_loss(
    db: Session = Depends(get_db),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None)
):
    query = db.query(ProfitLossStatement)
    query = apply_filters(query, ProfitLossStatement, year, month)
    rows = query.order_by(ProfitLossStatement.period_start).all()

    return [
        {
            "id": row.id,
            "period": row.period or "—",
            "period_start": str(row.period_start),
            "period_end": str(row.period_end),
            "total_revenue": float(row.total_revenue or 0),
            "total_expenses": float(row.total_expenses or 0),
            "operating_income": float(row.operating_income or 0),
            "pre_tax_income": float(row.pre_tax_income or 0),
            "net_income": float(row.net_income or 0)
        }
        for row in rows
    ]

@router.get("/summary")
def get_profit_loss_summary(
    db: Session = Depends(get_db),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None)
):
    query = db.query(ProfitLossStatement)
    query = apply_filters(query, ProfitLossStatement, year, month)
    rows = query.all()

    total_revenue = sum(float(row.total_revenue or 0) for row in rows)
    total_expenses = sum(float(row.total_expenses or 0) for row in rows)
    total_net_income = sum(float(row.net_income or 0) for row in rows)
    total_periods = len(rows)

    return {
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "total_net_income": total_net_income,
        "total_periods": total_periods
    }

@router.get("/chart-summary")
def get_profit_loss_chart_summary(
    db: Session = Depends(get_db),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None)
):
    query = db.query(ProfitLossStatement)
    query = apply_filters(query, ProfitLossStatement, year, month)
    rows = query.order_by(ProfitLossStatement.period_start).all()

    return [
        {
            "period": row.period or "—",
            "revenue": float(row.total_revenue or 0),
            "expenses": float(row.total_expenses or 0),
            "net_income": float(row.net_income or 0)
        }
        for row in rows
    ]

@router.post("/")
def create_profit_loss(data: ProfitLossCreate, db: Session = Depends(get_db)):
    new_entry = ProfitLossStatement(**data.dict())
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry