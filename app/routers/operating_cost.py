from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import Optional

from app.database import get_db
from app.models import DailyOperatingCost
from app.schemas import OperatingCostCreate

router = APIRouter(prefix="/api/operating-cost", tags=["Operating Cost"])

def apply_filters(query, model, year, month):
    if year:
        query = query.filter(extract('year', model.date) == year)
    if month:
        query = query.filter(extract('month', model.date) == month)
    return query

@router.get("/")
def get_operating_cost(
    db: Session = Depends(get_db),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None)
):
    query = db.query(DailyOperatingCost)
    query = apply_filters(query, DailyOperatingCost, year, month)
    rows = query.order_by(DailyOperatingCost.date).all()

    return [
        {
            "id": row.id,
            "date": str(row.date),
            "fuel_oil": float(row.fuel_oil or 0),
            "salaries_flight_crew": float(row.salaries_flight_crew or 0),
            "salaries_ground_staff": float(row.salaries_ground_staff or 0),
            "maintenance_repair": float(row.maintenance_repair or 0),
            "airport_landing_fees": float(row.airport_landing_fees or 0),
            "total_operating_cost": float(row.total_operating_cost or 0),
            "casm": float(row.casm or 0)
        }
        for row in rows
    ]

@router.get("/summary")
def get_operating_cost_summary(
    db: Session = Depends(get_db),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None)
):
    query_sum = db.query(func.sum(DailyOperatingCost.total_operating_cost))
    query_sum = apply_filters(query_sum, DailyOperatingCost, year, month)
    total = query_sum.scalar() or 0

    query_latest = db.query(DailyOperatingCost).order_by(DailyOperatingCost.date.desc())
    query_latest = apply_filters(query_latest, DailyOperatingCost, year, month)
    latest = query_latest.first()

    return {
        "total_operating_cost_sum": float(total),
        "latest_day_operating_cost": float(latest.total_operating_cost) if latest else 0
    }

@router.post("/")
def create_operating_cost(data: OperatingCostCreate, db: Session = Depends(get_db)):
    new_entry = DailyOperatingCost(**data.dict())
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return {"message": "Operating cost record added", "id": new_entry.id}