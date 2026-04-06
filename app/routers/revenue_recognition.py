from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import extract
from typing import Optional

from app.database import get_db
from app.models import RevenueRecognition
from app.schemas import RevenueRecognitionCreate

router = APIRouter(prefix="/api/revenue-recognition", tags=["Revenue Recognition"])

def apply_filters(query, model, year, month):
    if year:
        query = query.filter(extract('year', model.booking_date) == year)
    if month:
        query = query.filter(extract('month', model.booking_date) == month)
    return query

@router.get("/")
def get_revenue_recognition(
    db: Session = Depends(get_db),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None)
):
    query = db.query(RevenueRecognition)
    query = apply_filters(query, RevenueRecognition, year, month)
    rows = query.order_by(RevenueRecognition.booking_date).all()

    return [
        {
            "id": row.id,
            "transaction_id": row.transaction_id or "—",
            "transaction_type": row.transaction_type or "—",
            "booking_date": str(row.booking_date),
            "service_date": str(row.service_date),
            "recognition_date": str(row.recognition_date),
            "gross_amount": float(row.gross_amount or 0),
            "recognized_amount": float(row.recognized_amount or 0),
            "deferred_amount": float(row.deferred_amount or 0),
            "recognition_method": row.recognition_method or "—",
            "performance_obligation": row.performance_obligation or "—",
            "status": row.status or "Pending",
            "flight_number": row.flight_number or "—",
            "route": row.route or "—"
        }
        for row in rows
    ]

@router.get("/summary")
def get_revenue_recognition_summary(
    db: Session = Depends(get_db),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None)
):
    query = db.query(RevenueRecognition)
    query = apply_filters(query, RevenueRecognition, year, month)
    rows = query.all()

    total_gross = sum(float(row.gross_amount or 0) for row in rows)
    total_recognized = sum(float(row.recognized_amount or 0) for row in rows)
    total_deferred = sum(float(row.deferred_amount or 0) for row in rows)
    total_transactions = len(rows)

    return {
        "total_gross": total_gross,
        "total_recognized": total_recognized,
        "total_deferred": total_deferred,
        "total_transactions": total_transactions
    }

@router.get("/chart-summary")
def get_revenue_recognition_chart_summary(
    db: Session = Depends(get_db),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None)
):
    query = db.query(RevenueRecognition)
    query = apply_filters(query, RevenueRecognition, year, month)
    rows = query.order_by(RevenueRecognition.booking_date).all()

    date_map = {}
    for row in rows:
        date_key = str(row.booking_date)
        if date_key not in date_map:
            date_map[date_key] = {"date": date_key, "recognized": 0, "deferred": 0}
        date_map[date_key]["recognized"] += float(row.recognized_amount or 0)
        date_map[date_key]["deferred"] += float(row.deferred_amount or 0)

    result = list(date_map.values())
    result.sort(key=lambda x: x["date"])
    return result

@router.post("/")
def create_revenue_recognition(data: RevenueRecognitionCreate, db: Session = Depends(get_db)):
    new_entry = RevenueRecognition(**data.dict())
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return {"message": "Record added", "id": new_entry.id}
