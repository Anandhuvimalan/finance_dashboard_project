# SkyFinance – Airline Financial Dashboard

A full-stack finance management application built with **FastAPI** (backend) and **Vanilla JavaScript + Chart.js** (frontend), using **PostgreSQL** as the database.

## Features

- **Dashboard** – KPI cards showing total revenue, operating costs, net income
- **Daily Revenue** – Track daily revenue with trend charts and data tables
- **Operating Cost** – Monitor fuel, salaries, maintenance and other operating costs
- **Daily Expense** – Track expenses by category with approval status
- **Accounts Payable** – Manage vendor invoices with aging analysis
- **Accounts Receivable** – Track customer invoices and collections
- **General Ledger** – Complete journal entries with debit/credit tracking
- **Chart of Accounts** – Account structure and classifications
- **Profit & Loss** – Income statement with revenue vs expenses trend

## Tech Stack

| Layer     | Technology               |
|-----------|--------------------------|
| Backend   | Python, FastAPI          |
| Frontend  | HTML, CSS, JavaScript    |
| Charts    | Chart.js                 |
| Database  | PostgreSQL               |
| ORM       | SQLAlchemy               |
| Templates | Jinja2                   |

## How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Make sure PostgreSQL is running with the finance_dashboard database

# 3. Start the server
uvicorn app.main:app --reload

# 4. Open browser
http://localhost:8000
```

## Project Structure

```
finance_dashboard_project/
├── app/
│   ├── main.py          # FastAPI app with routes
│   ├── database.py      # PostgreSQL connection
│   ├── models.py        # SQLAlchemy models (8 tables)
│   ├── schemas.py       # Pydantic validation schemas
│   └── routers/         # API routers (one per module)
│       ├── revenue.py
│       ├── operating_cost.py
│       ├── profit.py
│       ├── accounts_payable.py
│       ├── accounts_receivable.py
│       ├── daily_expense.py
│       ├── general_ledger.py
│       ├── chart_of_accounts.py
│       └── profit_loss.py
├── templates/           # Jinja2 HTML templates
├── static/
│   ├── css/style.css    # Dark theme OLED styling
│   └── js/app.js        # Chart.js charts + API calls
├── requirements.txt
└── README.md
```

## Key Features

- **Year/Month Slicers** – Filter all data by year and month globally
- **Add Data Modal** – Add new records from any page via the modal form
- **Live Refresh** – Data updates reflect immediately on the dashboard
- **No Null Values** – All table columns show clean data (dashes for empty)
- **Responsive** – Works on desktop and tablet screens
