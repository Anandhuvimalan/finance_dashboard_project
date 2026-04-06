from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import Optional

from app.database import get_db
from app.models import DailyProfit

router = APIRouter(prefix="/api/profit", tags=["Profit"])

def apply_filters(query, model, year, month):
    if year:
        query = query.filter(extract('year', model.date) == year)
    if month:
        query = query.filter(extract('month', model.date) == month)
    return query

@router.get("/")
def get_profit(
    db: Session = Depends(get_db),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None)
):
    query = db.query(DailyProfit)
    query = apply_filters(query, DailyProfit, year, month)
    rows = query.order_by(DailyProfit.date).all()

    return [
        {
            "id": row.id,
            "date": str(row.date),
            "total_revenue": float(row.total_revenue or 0),
            "total_operating_cost": float(row.total_operating_cost or 0),
            "gross_profit": float(row.gross_profit or 0),
            "pre_tax_income": float(row.pre_tax_income or 0),
            "net_income": float(row.net_income or 0),
            "operating_margin": float(row.operating_margin or 0),
            "net_margin": float(row.net_margin or 0),
            "ebitda": float(row.ebitda or 0)
        }
        for row in rows
    ]

@router.get("/summary")
def get_profit_summary(
    db: Session = Depends(get_db),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None)
):
    query_sum = db.query(func.sum(DailyProfit.net_income))
    query_sum = apply_filters(query_sum, DailyProfit, year, month)
    total_net_income = query_sum.scalar() or 0

    query_latest = db.query(DailyProfit).order_by(DailyProfit.date.desc())
    query_latest = apply_filters(query_latest, DailyProfit, year, month)
    latest = query_latest.first()

    return {
        "total_net_income_sum": float(total_net_income),
        "latest_day_net_income": float(latest.net_income) if latest else 0
    }