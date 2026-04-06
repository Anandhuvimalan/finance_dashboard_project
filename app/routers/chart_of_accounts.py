from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ChartOfAccounts
from app.schemas import ChartOfAccountsCreate

router = APIRouter(prefix="/api/chart-of-accounts", tags=["Chart of Accounts"])


@router.get("/")
def get_chart_of_accounts(db: Session = Depends(get_db)):
    rows = db.query(ChartOfAccounts).order_by(ChartOfAccounts.account_code).all()

    return [
        {
            "id": row.id,
            "account_code": row.account_code or "—",
            "account_name": row.account_name or "—",
            "account_type": row.account_type or "—",
            "sub_type": row.sub_type or "—",
            "parent_code": row.parent_code or "—",
            "description": row.description or "—",
            "normal_balance": row.normal_balance or "—",
            "is_active": bool(row.is_active),
            "is_header": bool(row.is_header),
            "currency": row.currency or "USD"
        }
        for row in rows
    ]


@router.get("/summary")
def get_chart_of_accounts_summary(db: Session = Depends(get_db)):
    rows = db.query(ChartOfAccounts).all()

    total_accounts = len(rows)
    active_accounts = sum(1 for row in rows if row.is_active)
    header_accounts = sum(1 for row in rows if row.is_header)
    unique_account_types = len(
        set((row.account_type or "").strip() for row in rows if row.account_type)
    )

    return {
        "total_accounts": total_accounts,
        "active_accounts": active_accounts,
        "header_accounts": header_accounts,
        "unique_account_types": unique_account_types
    }


@router.get("/type-summary")
def get_chart_of_accounts_type_summary(db: Session = Depends(get_db)):
    rows = db.query(ChartOfAccounts).all()

    type_counts = {}

    for row in rows:
        account_type = row.account_type or "Unknown"
        type_counts[account_type] = type_counts.get(account_type, 0) + 1

    result = [
        {
            "account_type": account_type,
            "count": count
        }
        for account_type, count in type_counts.items()
    ]

    result.sort(key=lambda x: x["count"], reverse=True)
    return result

@router.post("/")
def create_account(data: ChartOfAccountsCreate, db: Session = Depends(get_db)):
    new_entry = ChartOfAccounts(**data.dict())
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return {"message": "Account added", "id": new_entry.id}