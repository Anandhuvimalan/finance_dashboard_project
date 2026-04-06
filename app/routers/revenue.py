from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import Optional

from app.database import get_db
from app.models import DailyRevenue
from app.schemas import RevenueCreate

router = APIRouter(prefix="/api/revenue", tags=["Revenue"])

def apply_filters(query, model, year, month):
    if year:
        query = query.filter(extract('year', model.date) == year)
    if month:
        query = query.filter(extract('month', model.date) == month)
    return query

@router.get("/")
def get_revenue(
    db: Session = Depends(get_db),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None)
):
    query = db.query(DailyRevenue)
    query = apply_filters(query, DailyRevenue, year, month)
    rows = query.order_by(DailyRevenue.date).all()

    return [
        {
            "id": row.id,
            "date": str(row.date),
            "total_revenue": float(row.total_revenue or 0),
            "passenger_mainline": float(row.passenger_mainline or 0),
            "passenger_regional": float(row.passenger_regional or 0),
            "cargo_mail": float(row.cargo_mail or 0),
            "load_factor": float(row.load_factor or 0)
        }
        for row in rows
    ]

@router.get("/summary")
def get_revenue_summary(
    db: Session = Depends(get_db),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None)
):
    query_sum = db.query(func.sum(DailyRevenue.total_revenue))
    query_sum = apply_filters(query_sum, DailyRevenue, year, month)
    total = query_sum.scalar() or 0

    query_latest = db.query(DailyRevenue).order_by(DailyRevenue.date.desc())
    query_latest = apply_filters(query_latest, DailyRevenue, year, month)
    latest = query_latest.first()

    return {
        "total_revenue_sum": float(total),
        "latest_day_revenue": float(latest.total_revenue) if latest else 0
    }

@router.post("/")
def create_revenue(data: RevenueCreate, db: Session = Depends(get_db)):
    new_entry = DailyRevenue(**data.dict())
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return {"message": "Revenue record added", "id": new_entry.id}