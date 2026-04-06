from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routers import (
    revenue,
    operating_cost,
    profit,
    accounts_payable,
    accounts_receivable,
    daily_expense,
    general_ledger,
    chart_of_accounts,
    profit_loss,
    revenue_recognition
)

app = FastAPI(title="Finance Dashboard")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(revenue.router)
app.include_router(operating_cost.router)
app.include_router(profit.router)
app.include_router(accounts_payable.router)
app.include_router(accounts_receivable.router)
app.include_router(daily_expense.router)
app.include_router(general_ledger.router)
app.include_router(chart_of_accounts.router)
app.include_router(profit_loss.router)
app.include_router(revenue_recognition.router)


@app.get("/")
def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/ap")
def accounts_payable_page(request: Request):
    return templates.TemplateResponse("accounts_payable.html", {"request": request})


@app.get("/ar")
def accounts_receivable_page(request: Request):
    return templates.TemplateResponse("accounts_receivable.html", {"request": request})


@app.get("/gl")
def general_ledger_page(request: Request):
    return templates.TemplateResponse("general_ledger.html", {"request": request})


@app.get("/pl")
def profit_loss_page(request: Request):
    return templates.TemplateResponse("profit_loss.html", {"request": request})


@app.get("/daily-revenue")
def daily_revenue_page(request: Request):
    return templates.TemplateResponse("daily_revenue.html", {"request": request})


@app.get("/operating-cost")
def operating_cost_page(request: Request):
    return templates.TemplateResponse("operating_cost.html", {"request": request})


@app.get("/daily-expense")
def daily_expense_page(request: Request):
    return templates.TemplateResponse("daily_expense.html", {"request": request})


@app.get("/chart-of-accounts")
def chart_of_accounts_page(request: Request):
    return templates.TemplateResponse("chart_of_accounts.html", {"request": request})

@app.get("/revenue-recognition")
def revenue_recognition_page(request: Request):
    return templates.TemplateResponse("revenue_recognition.html", {"request": request})