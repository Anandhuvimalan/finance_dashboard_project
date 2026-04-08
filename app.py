import json

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sqlalchemy import MetaData, Table, create_engine

# ── Config ──────────────────────────────────────────────────────────
DB_URL = "postgresql+psycopg2://postgres:bleach%23postgres@localhost:5432/finance"
engine = create_engine(DB_URL)

app = FastAPI(title="SkyFinance Dashboard")
app.mount("/static", StaticFiles(directory="static"), name="static")
tpl = Jinja2Templates(directory="templates")

# ── Plotly Theme (matches CSS dark theme) ───────────────────────────
PLT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#aaa", size=11), margin=dict(l=52, r=24, t=16, b=72),
    legend=dict(font=dict(color="#ccc", size=11)),
    xaxis=dict(
        gridcolor="#1e1e1e",
        tickfont=dict(color="#b8b8b8"),
        title_font=dict(color="#ff8c33"),
        automargin=True,
        showline=False,
        zeroline=False,
    ),
    yaxis=dict(
        gridcolor="#1e1e1e",
        tickfont=dict(color="#b8b8b8"),
        title_font=dict(color="#ff8c33"),
        automargin=True,
        separatethousands=True,
        showline=False,
        zeroline=False,
    ),
)
C = {"orange": "#ff6a00", "green": "#10b981", "red": "#ef4444", "blue": "#3b82f6",
     "purple": "#8b5cf6", "yellow": "#f59e0b", "pink": "#ec4899", "teal": "#14b8a6"}

FORM_CONFIGS = {
    "daily-revenue": {
        "title": "Add Daily Revenue",
        "table": "daily_revenue",
        "fields": [
            {"name": "date", "label": "Date", "type": "date", "required": True},
            {"name": "passenger_mainline", "label": "Passenger Mainline", "type": "number"},
            {"name": "passenger_regional", "label": "Passenger Regional", "type": "number"},
            {"name": "cargo_mail", "label": "Cargo Mail", "type": "number"},
            {"name": "total_revenue", "label": "Total Revenue", "type": "number", "required": True},
            {"name": "load_factor", "label": "Load Factor", "type": "number"},
        ],
    },
    "operating-cost": {
        "title": "Add Operating Cost",
        "table": "daily_operating_cost",
        "fields": [
            {"name": "date", "label": "Date", "type": "date", "required": True},
            {"name": "fuel_oil", "label": "Fuel & Oil", "type": "number"},
            {"name": "salaries_flight_crew", "label": "Flight Crew Salaries", "type": "number"},
            {"name": "salaries_ground_staff", "label": "Ground Staff Salaries", "type": "number"},
            {"name": "maintenance_repair", "label": "Maintenance", "type": "number"},
            {"name": "airport_landing_fees", "label": "Airport Fees", "type": "number"},
            {"name": "total_operating_cost", "label": "Total Operating Cost", "type": "number", "required": True},
            {"name": "casm", "label": "CASM", "type": "number"},
        ],
    },
    "daily-expense": {
        "title": "Add Daily Expense",
        "table": "daily_expense",
        "fields": [
            {"name": "date", "label": "Date", "type": "date", "required": True},
            {"name": "category", "label": "Category", "type": "text", "required": True},
            {"name": "description", "label": "Description", "type": "text"},
            {"name": "amount", "label": "Amount", "type": "number", "required": True},
            {"name": "department", "label": "Department", "type": "text"},
            {"name": "vendor", "label": "Vendor", "type": "text"},
            {"name": "cost_center", "label": "Cost Center", "type": "text"},
            {"name": "approved_by", "label": "Approved By", "type": "text"},
            {"name": "status", "label": "Status", "type": "text"},
        ],
    },
    "ap": {
        "title": "Add Accounts Payable",
        "table": "accounts_payable",
        "fields": [
            {"name": "vendor_name", "label": "Vendor Name", "type": "text", "required": True},
            {"name": "invoice_number", "label": "Invoice Number", "type": "text", "required": True},
            {"name": "invoice_date", "label": "Invoice Date", "type": "date", "required": True},
            {"name": "due_date", "label": "Due Date", "type": "date", "required": True},
            {"name": "amount", "label": "Amount", "type": "number", "required": True},
            {"name": "paid_amount", "label": "Paid Amount", "type": "number"},
            {"name": "balance", "label": "Balance", "type": "number", "required": True},
            {"name": "category", "label": "Category", "type": "text"},
            {"name": "status", "label": "Status", "type": "text"},
        ],
    },
    "ar": {
        "title": "Add Accounts Receivable",
        "table": "accounts_receivable",
        "fields": [
            {"name": "customer_name", "label": "Customer Name", "type": "text", "required": True},
            {"name": "invoice_number", "label": "Invoice Number", "type": "text", "required": True},
            {"name": "invoice_date", "label": "Invoice Date", "type": "date", "required": True},
            {"name": "due_date", "label": "Due Date", "type": "date", "required": True},
            {"name": "amount", "label": "Amount", "type": "number", "required": True},
            {"name": "received_amount", "label": "Received Amount", "type": "number"},
            {"name": "balance", "label": "Balance", "type": "number", "required": True},
            {"name": "category", "label": "Category", "type": "text"},
            {"name": "status", "label": "Status", "type": "text"},
        ],
    },
    "gl": {
        "title": "Add General Ledger Entry",
        "table": "general_ledger",
        "fields": [
            {"name": "entry_date", "label": "Entry Date", "type": "date", "required": True},
            {"name": "posting_date", "label": "Posting Date", "type": "date", "required": True},
            {"name": "account_code", "label": "Account Code", "type": "text", "required": True},
            {"name": "account_name", "label": "Account Name", "type": "text", "required": True},
            {"name": "debit", "label": "Debit", "type": "number"},
            {"name": "credit", "label": "Credit", "type": "number"},
            {"name": "description", "label": "Description", "type": "text"},
            {"name": "journal_type", "label": "Journal Type", "type": "text"},
        ],
    },
    "chart-of-accounts": {
        "title": "Add Chart of Accounts Record",
        "table": "chart_of_accounts",
        "fields": [
            {"name": "account_code", "label": "Account Code", "type": "text", "required": True},
            {"name": "account_name", "label": "Account Name", "type": "text", "required": True},
            {"name": "account_type", "label": "Account Type", "type": "text", "required": True},
            {"name": "sub_type", "label": "Sub Type", "type": "text"},
            {"name": "parent_code", "label": "Parent Code", "type": "text"},
            {"name": "normal_balance", "label": "Normal Balance", "type": "text"},
            {"name": "currency", "label": "Currency", "type": "text"},
            {"name": "is_active", "label": "Is Active", "type": "boolean"},
            {"name": "is_header", "label": "Is Header", "type": "boolean"},
        ],
    },
    "pl": {
        "title": "Add Profit & Loss Record",
        "table": "profit_loss_statement",
        "fields": [
            {"name": "period", "label": "Period", "type": "text", "required": True},
            {"name": "period_start", "label": "Period Start", "type": "date", "required": True},
            {"name": "period_end", "label": "Period End", "type": "date", "required": True},
            {"name": "total_revenue", "label": "Total Revenue", "type": "number", "required": True},
            {"name": "total_expenses", "label": "Total Expenses", "type": "number", "required": True},
            {"name": "operating_income", "label": "Operating Income", "type": "number", "required": True},
            {"name": "pre_tax_income", "label": "Pre-Tax Income", "type": "number", "required": True},
            {"name": "net_income", "label": "Net Income", "type": "number", "required": True},
        ],
    },
    "revenue-recognition": {
        "title": "Add Revenue Recognition Record",
        "table": "revenue_recognition",
        "fields": [
            {"name": "transaction_id", "label": "Transaction ID", "type": "text", "required": True},
            {"name": "booking_date", "label": "Booking Date", "type": "date", "required": True},
            {"name": "service_date", "label": "Service Date", "type": "date", "required": True},
            {"name": "recognition_date", "label": "Recognition Date", "type": "date", "required": True},
            {"name": "flight_number", "label": "Flight Number", "type": "text"},
            {"name": "route", "label": "Route", "type": "text"},
            {"name": "gross_amount", "label": "Gross Amount", "type": "number", "required": True},
            {"name": "recognized_amount", "label": "Recognized Amount", "type": "number"},
            {"name": "deferred_amount", "label": "Deferred Amount", "type": "number"},
            {"name": "recognition_method", "label": "Recognition Method", "type": "text"},
            {"name": "status", "label": "Status", "type": "text"},
        ],
    },
}


# ── Helpers ─────────────────────────────────────────────────────────
def load(table, date_col, year, month):
    df = pd.read_sql_table(table, engine)
    df[date_col] = pd.to_datetime(df[date_col])
    if year:
        df = df[df[date_col].dt.year == year]
    if month:
        df = df[df[date_col].dt.month == month]
    return df.sort_values(date_col).reset_index(drop=True)


def get_filters(year=None):
    dates = pd.Series(dtype="datetime64[ns]")
    for tbl, col in [("daily_revenue","date"),("daily_operating_cost","date"),("daily_profit","date"),
                      ("daily_expense","date"),("accounts_payable","invoice_date"),
                      ("accounts_receivable","invoice_date"),("general_ledger","entry_date"),
                      ("profit_loss_statement","period_start"),("revenue_recognition","recognition_date")]:
        d = pd.read_sql_table(tbl, engine, columns=[col])
        d[col] = pd.to_datetime(d[col])
        dates = pd.concat([dates, d[col]], ignore_index=True)
    dates = dates.dropna()
    years = sorted(int(y) for y in dates.dt.year.unique())
    months = sorted(int(m) for m in (dates[dates.dt.year == year] if year else dates).dt.month.unique())
    return years, months


MONTH_NAMES = ["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

def fmt(v):
    if pd.isna(v) or v is None:
        return "$0.00"
    return f"${float(v):,.2f}"

def num(v):
    if pd.isna(v) or v is None:
        return "0"
    return f"{int(v):,}"

def pct(v, digits=2):
    if pd.isna(v) or v is None:
        return f"{0:.{digits}f}%"
    return f"{float(v):.{digits}f}%"

def yes_no(v):
    return "Yes" if bool(v) else "No"

def date_txt(v):
    if pd.isna(v) or v is None:
        return "-"
    return pd.to_datetime(v).strftime("%Y-%m-%d")

def ctx(request, year, month, **kw):
    """Base template context with filters."""
    years, months = get_filters(year)
    if year and year not in years:
        year = None
        years, months = get_filters(None)
    if month and month not in months:
        month = None
    return {
        "request": request, "years": years, "months": months,
        "month_names": MONTH_NAMES, "sel_year": year, "sel_month": month,
        "form_configs": json.dumps(FORM_CONFIGS), **kw
    }


# ── Chart builders ──────────────────────────────────────────────────
def chart_html(fig):
    fig.update_layout(**PLT)
    return fig.to_html(
        full_html=False,
        include_plotlyjs=False,
        config={"displayModeBar": False, "responsive": True},
        default_height="340px",
        default_width="100%",
    )

def empty_chart(message="No data for the selected filters."):
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(color="#888", size=13),
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return chart_html(fig)


def line_chart(df, x, y, name, color):
    if df.empty:
        return empty_chart()
    x_values = pd.to_datetime(df[x]).dt.strftime("%Y-%m-%d").tolist()
    y_values = pd.to_numeric(df[y], errors="coerce").fillna(0).astype(float).tolist()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_values,
        y=y_values,
        name=name,
        mode="lines+markers",
        line=dict(color=color, width=2.5),
        marker=dict(size=5, color=color, line=dict(color=color, width=1)),
        fill="tozeroy",
        fillcolor=color.replace(")", ",0.12)").replace("rgb", "rgba") if "rgb" in color else f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.12)",
        hovertemplate="%{x|%Y-%m-%d}<br>%{y:$,.2f}<extra>" + name + "</extra>",
    ))
    fig.update_layout(
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#161616",
            bordercolor=color,
            font=dict(color="#f5f5f5", size=12),
            namelength=-1,
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.08,
            xanchor="center",
            x=0.5,
        ),
    )
    fig.update_xaxes(
        title="Date",
        tickformat="%Y-%m-%d",
        tickangle=-25,
        nticks=10,
        rangeslider_visible=False,
        type="date",
    )
    fig.update_yaxes(
        title=f"{name} ($)",
        tickformat="$.3s",
    )
    return chart_html(fig)


def summarize_for_time_chart(df, date_col, value_cols, year, month):
    if df.empty:
        return pd.DataFrame(columns=["bucket", *value_cols]), "Date", "%Y-%m-%d"

    summary = df.copy()
    summary[date_col] = pd.to_datetime(summary[date_col], errors="coerce")
    for col in value_cols:
        summary[col] = pd.to_numeric(summary[col], errors="coerce").fillna(0)

    if month:
        summary["bucket"] = summary[date_col].dt.floor("D")
        tickformat = "%Y-%m-%d"
        axis_title = "Date"
    else:
        summary["bucket"] = summary[date_col].dt.to_period("M").dt.to_timestamp()
        tickformat = "%b %Y"
        axis_title = "Month"

    grouped = summary.groupby("bucket", as_index=False)[value_cols].sum().sort_values("bucket")
    return grouped, axis_title, tickformat


def multi_line(df, x, series):
    fig = go.Figure()
    for name, col, color in series:
        fig.add_trace(go.Scatter(x=df[x], y=df[col], name=name, mode="lines", line=dict(color=color, width=2)))
    return chart_html(fig)


def bar_chart(labels, values, colors=None):
    if not labels:
        return empty_chart()
    clean_labels = [str(label) for label in labels]
    clean_values = [float(v) for v in values]
    fig = go.Figure(go.Bar(x=clean_labels, y=clean_values, marker_color=colors or C["orange"]))
    return chart_html(fig)


def grouped_bar(df, x, series, axis_title="Date", tickformat="%b %Y", barmode="group"):
    if df.empty:
        return empty_chart()
    fig = go.Figure()
    x_values = pd.to_datetime(df[x], errors="coerce").dt.strftime("%Y-%m-%d").tolist()
    if tickformat == "%b %Y":
        x_values = pd.to_datetime(df[x], errors="coerce").dt.strftime("%Y-%m-01").tolist()
    hover_date_format = "%Y-%m-%d" if tickformat == "%Y-%m-%d" else "%b %Y"
    for name, col, color in series:
        y_values = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(float).tolist()
        fig.add_trace(go.Bar(
            x=x_values,
            y=y_values,
            name=name,
            marker_color=color,
            hovertemplate=f"%{{x|{hover_date_format}}}<br>%{{y:$,.2f}}<extra>{name}</extra>",
        ))
    fig.update_layout(
        barmode=barmode,
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#161616",
            bordercolor="#444444",
            font=dict(color="#f5f5f5", size=12),
            namelength=-1,
        ),
    )
    fig.update_xaxes(
        title=axis_title,
        tickformat=tickformat,
        tickangle=-25,
        nticks=12,
        type="date",
        rangeslider_visible=False,
    )
    fig.update_yaxes(
        title="Amount ($)",
        tickformat="$.3s",
    )
    return chart_html(fig)


def horizontal_amount_bar(labels, values, color=None, colors=None, x_title="Amount ($)", show_text=False):
    if not labels:
        return empty_chart()
    clean_labels = [str(label) for label in labels]
    clean_values = [float(v) for v in values]
    marker_color = colors or color or C["orange"]
    fig = go.Figure(go.Bar(
        x=clean_values,
        y=clean_labels,
        orientation="h",
        marker_color=marker_color,
        text=[f"${value:,.0f}" for value in clean_values] if show_text else None,
        textposition="outside" if show_text else None,
        hovertemplate="%{y}<br>%{x:$,.2f}<extra></extra>",
    ))
    fig.update_layout(
        hovermode="y",
        hoverlabel=dict(
            bgcolor="#161616",
            bordercolor=color or "#444444",
            font=dict(color="#f5f5f5", size=12),
            namelength=-1,
        ),
        margin=dict(l=180, r=72, t=16, b=56),
    )
    fig.update_xaxes(title=x_title, tickformat="$.3s")
    fig.update_yaxes(title="")
    return chart_html(fig)


def period_as_of_date(df, year, month, date_col):
    if month and year:
        return (pd.Timestamp(year=year, month=month, day=1) + pd.offsets.MonthEnd(0)).normalize()
    if year:
        return pd.Timestamp(year=year, month=12, day=31)

    if df.empty:
        return pd.Timestamp.today().normalize()

    dates = pd.to_datetime(df[date_col], errors="coerce").dropna()
    if dates.empty:
        return pd.Timestamp.today().normalize()
    return dates.max().normalize()


def combo_time_chart(
    df,
    x,
    bar_series,
    line_series,
    axis_title="Date",
    tickformat="%b %Y",
    left_title="Amount ($)",
    right_title="Amount ($)",
):
    if df.empty:
        return empty_chart()
    x_values = pd.to_datetime(df[x], errors="coerce").dt.strftime("%Y-%m-%d").tolist()
    if tickformat == "%b %Y":
        x_values = pd.to_datetime(df[x], errors="coerce").dt.strftime("%Y-%m-01").tolist()
    hover_date_format = "%Y-%m-%d" if tickformat == "%Y-%m-%d" else "%b %Y"

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    for name, col, color in bar_series:
        y_values = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(float).tolist()
        fig.add_trace(
            go.Bar(
                x=x_values,
                y=y_values,
                name=name,
                marker_color=color,
                hovertemplate=f"%{{x|{hover_date_format}}}<br>%{{y:$,.2f}}<extra>{name}</extra>",
            ),
            secondary_y=False,
        )

    for name, col, color in line_series:
        y_values = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(float).tolist()
        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=y_values,
                name=name,
                mode="lines+markers",
                line=dict(color=color, width=3),
                marker=dict(size=6, color=color, line=dict(color=color, width=1)),
                hovertemplate=f"%{{x|{hover_date_format}}}<br>%{{y:$,.2f}}<extra>{name}</extra>",
            ),
            secondary_y=True,
        )

    fig.update_layout(
        barmode="group",
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#161616",
            bordercolor="#444444",
            font=dict(color="#f5f5f5", size=12),
            namelength=-1,
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.08,
            xanchor="center",
            x=0.5,
        ),
    )
    fig.update_xaxes(
        title=axis_title,
        tickformat=tickformat,
        tickangle=-25,
        nticks=12,
        type="date",
        rangeslider_visible=False,
    )
    fig.update_yaxes(title=left_title, tickformat="$.3s", secondary_y=False)
    fig.update_yaxes(title=right_title, tickformat="$.3s", showgrid=False, secondary_y=True)
    return chart_html(fig)


def pie_chart(labels, values, colors=None):
    if not labels:
        return empty_chart()
    palette = colors or [C["orange"], C["green"], C["blue"], C["red"], C["yellow"], C["purple"], C["pink"], C["teal"]]
    fig = go.Figure(go.Pie(labels=labels, values=values, hole=0.45,
                           marker=dict(colors=palette[:len(labels)]),
                           textinfo="percent", textposition="inside", textfont=dict(color="#ccc", size=11)))
    fig.update_layout(showlegend=True, legend=dict(x=1, y=0.5))
    return chart_html(fig)


def coerce_field(raw_value, field_type):
    if raw_value in (None, ""):
        return None
    if field_type == "number":
        return float(raw_value)
    if field_type == "date":
        return pd.to_datetime(raw_value).date()
    if field_type == "boolean":
        return str(raw_value).lower() in ("true", "1", "yes", "on")
    return str(raw_value).strip()


@app.post("/add-record")
async def add_record(request: Request):
    payload = await request.json()
    form_key = payload.get("form_key")
    config = FORM_CONFIGS.get(form_key)
    if not config:
        raise HTTPException(status_code=400, detail="Unknown form target.")

    row = {}
    for field in config["fields"]:
        name = field["name"]
        value = payload.get(name)
        if field.get("required") and value in (None, ""):
            raise HTTPException(status_code=400, detail=f"{field['label']} is required.")
        coerced = coerce_field(value, field["type"])
        if coerced is not None:
            row[name] = coerced

    try:
        table = Table(config["table"], MetaData(), autoload_with=engine)
        with engine.begin() as conn:
            conn.execute(table.insert().values(**row))
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"ok": True}


# ── ROUTES ──────────────────────────────────────────────────────────

# ── Dashboard ───────────────────────────────────────────────────────
@app.get("/")
def dashboard(request: Request, year: Optional[int] = None, month: Optional[int] = None):
    base = ctx(request, year, month)
    y, m = base["sel_year"], base["sel_month"]

    rev = load("daily_revenue", "date", y, m)
    cost = load("daily_operating_cost", "date", y, m)
    profit = load("daily_profit", "date", y, m)
    expense = load("daily_expense", "date", y, m)
    coa = pd.read_sql_table("chart_of_accounts", engine)

    # KPI cards
    base["cards"] = [
        {"title": "Total Revenue", "value": fmt(rev["total_revenue"].sum())},
        {"title": "Total Operating Cost", "value": fmt(cost["total_operating_cost"].sum())},
        {"title": "Total Net Income", "value": fmt(profit["net_income"].sum())},
    ]

    # Charts
    base["charts"] = [
        {"title": "Revenue Trend", "html": line_chart(rev, "date", "total_revenue", "Revenue", C["orange"])},
        {"title": "Operating Cost Trend", "html": line_chart(cost, "date", "total_operating_cost", "Operating Cost", C["red"])},
        {"title": "Profit Trend", "html": line_chart(profit, "date", "net_income", "Net Income", C["green"])},
    ]

    # Revenue table
    rev_tbl = rev[["date","total_revenue","passenger_mainline","cargo_mail","load_factor"]].fillna(0).copy()
    rev_tbl["date"] = rev_tbl["date"].map(date_txt)
    rev_tbl["total_revenue"] = rev_tbl["total_revenue"].map(fmt)
    rev_tbl["passenger_mainline"] = rev_tbl["passenger_mainline"].map(fmt)
    rev_tbl["cargo_mail"] = rev_tbl["cargo_mail"].map(fmt)
    rev_tbl["load_factor"] = rev_tbl["load_factor"].map(lambda v: pct(v, 1))
    base["table"] = {
        "title": "Revenue Data",
        "headers": ["Date","Total Revenue","Passenger Mainline","Cargo Mail","Load Factor"],
        "rows": rev_tbl.values.tolist()
    }

    # Expense section
    expense["amount"] = expense["amount"].fillna(0)
    expense["status"] = expense["status"].fillna("")
    base["extra_cards"] = [
        {"title": "Total Expense", "value": fmt(expense["amount"].sum())},
        {"title": "Total Records", "value": num(len(expense))},
        {"title": "Approved", "value": num(int((expense["status"].str.lower()=="approved").sum()))},
        {"title": "Pending", "value": num(int((expense["status"].str.lower()=="pending").sum()))},
    ]
    cats = expense.groupby(expense["category"].fillna("Unknown"))["amount"].sum()
    base["extra_charts"] = [
        {"title": "Expense by Category", "html": pie_chart(cats.index.tolist(), cats.values.tolist())},
    ]

    # COA section
    base["coa_cards"] = [
        {"title": "Total Accounts", "value": num(len(coa))},
        {"title": "Active Accounts", "value": num(int(coa["is_active"].sum()))},
        {"title": "Header Accounts", "value": num(int(coa["is_header"].sum()))},
        {"title": "Account Types", "value": num(int(coa["account_type"].dropna().nunique()))},
    ]
    coa_types = coa.groupby(coa["account_type"].fillna("Unknown")).size()
    base["coa_chart"] = {"title": "Accounts by Type", "html": bar_chart(coa_types.index.tolist(), coa_types.values.tolist(),
                          [C["orange"],C["blue"],C["green"],C["red"],C["yellow"],C["purple"],C["pink"]][:len(coa_types)])}

    return tpl.TemplateResponse("app.html", base)


# ── Daily Revenue ───────────────────────────────────────────────────
@app.get("/daily-revenue")
def daily_revenue_page(request: Request, year: Optional[int] = None, month: Optional[int] = None):
    base = ctx(request, year, month, page_title="Daily Revenue", page_subtitle="Track daily revenue performance")
    y, m = base["sel_year"], base["sel_month"]
    df = load("daily_revenue", "date", y, m)

    base["cards"] = [
        {"title": "Total Revenue", "value": fmt(df["total_revenue"].sum())},
        {"title": "Average Daily Revenue", "value": fmt(df["total_revenue"].mean()) if len(df) else "$0.00"},
        {"title": "Top Revenue Day", "value": (df.loc[df["total_revenue"].idxmax(), "date"].strftime("%Y-%m-%d") + " (" + fmt(df["total_revenue"].max()) + ")") if len(df) else "—"},
        {"title": "Average Load Factor", "value": f"{df['load_factor'].mean():.2f}%" if len(df) else "0.00%"},
    ]
    base["charts"] = [{"title": "Revenue Trend", "html": line_chart(df, "date", "total_revenue", "Revenue", C["orange"])}]

    tbl = df[["date","passenger_mainline","passenger_regional","cargo_mail","total_revenue","load_factor"]].fillna(0).copy()
    tbl["date"] = tbl["date"].map(date_txt)
    tbl["passenger_mainline"] = tbl["passenger_mainline"].map(fmt)
    tbl["passenger_regional"] = tbl["passenger_regional"].map(fmt)
    tbl["cargo_mail"] = tbl["cargo_mail"].map(fmt)
    tbl["total_revenue"] = tbl["total_revenue"].map(fmt)
    tbl["load_factor"] = tbl["load_factor"].map(lambda v: pct(v, 1))
    base["table"] = {"title": "Daily Revenue Records", "headers": ["Date","Passenger Mainline","Passenger Regional","Cargo Mail","Total Revenue","Load Factor"], "rows": tbl.values.tolist()}
    return tpl.TemplateResponse("app.html", base)


# ── Operating Cost ──────────────────────────────────────────────────
@app.get("/operating-cost")
def operating_cost_page(request: Request, year: Optional[int] = None, month: Optional[int] = None):
    base = ctx(request, year, month, page_title="Operating Cost", page_subtitle="Monitor daily operating expenses")
    y, m = base["sel_year"], base["sel_month"]
    df = load("daily_operating_cost", "date", y, m)

    base["cards"] = [
        {"title": "Total Operating Cost", "value": fmt(df["total_operating_cost"].sum())},
        {"title": "Average Daily Cost", "value": fmt(df["total_operating_cost"].mean()) if len(df) else "$0.00"},
        {"title": "Highest Cost Day", "value": (df.loc[df["total_operating_cost"].idxmax(), "date"].strftime("%Y-%m-%d") + " (" + fmt(df["total_operating_cost"].max()) + ")") if len(df) else "-"},
        {"title": "Average CASM", "value": f"{df['casm'].fillna(0).mean():.4f}" if len(df) else "0.0000"},
    ]
    base["charts"] = [{"title": "Operating Cost Trend", "html": line_chart(df, "date", "total_operating_cost", "Operating Cost", C["red"])}]

    tbl = df[["date","fuel_oil","salaries_flight_crew","salaries_ground_staff","maintenance_repair","airport_landing_fees","total_operating_cost","casm"]].fillna(0).copy()
    tbl["date"] = tbl["date"].map(date_txt)
    tbl["fuel_oil"] = tbl["fuel_oil"].map(fmt)
    tbl["salaries_flight_crew"] = tbl["salaries_flight_crew"].map(fmt)
    tbl["salaries_ground_staff"] = tbl["salaries_ground_staff"].map(fmt)
    tbl["maintenance_repair"] = tbl["maintenance_repair"].map(fmt)
    tbl["airport_landing_fees"] = tbl["airport_landing_fees"].map(fmt)
    tbl["total_operating_cost"] = tbl["total_operating_cost"].map(fmt)
    tbl["casm"] = tbl["casm"].map(lambda v: f"{float(v):.4f}")
    base["table"] = {"title": "Operating Cost Records", "headers": ["Date","Fuel & Oil","Flight Crew Salaries","Ground Staff Salaries","Maintenance","Airport Fees","Total Operating Cost","CASM"], "rows": tbl.values.tolist()}
    return tpl.TemplateResponse("app.html", base)


# ── Daily Expense ───────────────────────────────────────────────────
@app.get("/daily-expense")
def daily_expense_page(request: Request, year: Optional[int] = None, month: Optional[int] = None):
    base = ctx(request, year, month, page_title="Daily Expense", page_subtitle="Track daily business expenses")
    y, m = base["sel_year"], base["sel_month"]
    df = load("daily_expense", "date", y, m)
    df["amount"] = df["amount"].fillna(0)
    df["status"] = df["status"].fillna("")

    base["cards"] = [
        {"title": "Total Expense", "value": fmt(df["amount"].sum())},
        {"title": "Total Records", "value": num(len(df))},
        {"title": "Approved Count", "value": num(int((df["status"].str.lower()=="approved").sum()))},
        {"title": "Pending Count", "value": num(int((df["status"].str.lower()=="pending").sum()))},
    ]
    cats = df.groupby(df["category"].fillna("Unknown"))["amount"].sum().sort_values(ascending=False)
    base["charts"] = [{"title": "Expense by Category", "html": pie_chart(cats.index.tolist(), cats.values.tolist())}]

    tbl = df[["date","category","description","amount","department","vendor","cost_center","approved_by","status"]].fillna("").copy()
    tbl["date"] = pd.to_datetime(tbl["date"]).map(date_txt)
    tbl["amount"] = pd.to_numeric(tbl["amount"], errors="coerce").fillna(0).map(fmt)
    base["table"] = {"title": "Daily Expense Records", "headers": ["Date","Category","Description","Amount","Department","Vendor","Cost Center","Approved By","Status"], "rows": tbl.values.tolist()}
    return tpl.TemplateResponse("app.html", base)


# ── Accounts Payable ────────────────────────────────────────────────
@app.get("/ap")
def ap_page(request: Request, year: Optional[int] = None, month: Optional[int] = None):
    base = ctx(request, year, month, page_title="Accounts Payable", page_subtitle="Manage vendor invoices and payments")
    y, m = base["sel_year"], base["sel_month"]
    df = load("accounts_payable", "invoice_date", y, m)
    df["due_date"] = pd.to_datetime(df["due_date"], errors="coerce")
    df["balance"] = df["balance"].fillna(0)
    df["paid_amount"] = df["paid_amount"].fillna(0)
    as_of = period_as_of_date(df, y, m, "due_date")
    df["age_days"] = (as_of - df["due_date"]).dt.days

    overdue = int(((df["balance"] > 0) & (df["age_days"] > 0)).sum())
    base["cards"] = [
        {"title": "Total Outstanding", "value": fmt(df["balance"].sum())},
        {"title": "Total Paid", "value": fmt(df["paid_amount"].sum())},
        {"title": "Overdue Invoices", "value": num(overdue)},
        {"title": "Total Invoices", "value": num(len(df))},
    ]

    pos = df[df["balance"] > 0]
    aging = {
        "Current": float(pos[pos["age_days"] <= 0]["balance"].sum()),
        "1-30 Days": float(pos[pos["age_days"].between(1, 30)]["balance"].sum()),
        "31-60 Days": float(pos[pos["age_days"].between(31, 60)]["balance"].sum()),
        "61-90 Days": float(pos[pos["age_days"].between(61, 90)]["balance"].sum()),
        "90+ Days": float(pos[pos["age_days"] > 90]["balance"].sum()),
    }
    aging_labels = list(aging.keys())
    aging_values = list(aging.values())
    base["charts"] = [{"title": f"AP Aging Analysis (As of {as_of.strftime('%Y-%m-%d')})", "html": horizontal_amount_bar(
                        aging_labels,
                        aging_values,
                        colors=[C["green"], C["blue"], C["yellow"], C["orange"], C["red"]],
                        x_title="Outstanding Balance ($)",
                        show_text=True,
                    )}]

    tbl = df[["vendor_name","invoice_number","amount","paid_amount","balance","due_date"]].fillna("").copy()
    tbl["amount"] = pd.to_numeric(tbl["amount"], errors="coerce").fillna(0).map(fmt)
    tbl["paid_amount"] = pd.to_numeric(tbl["paid_amount"], errors="coerce").fillna(0).map(fmt)
    tbl["balance"] = pd.to_numeric(tbl["balance"], errors="coerce").fillna(0).map(fmt)
    tbl["due_date"] = pd.to_datetime(tbl["due_date"]).map(date_txt)
    base["table"] = {"title": "Accounts Payable Invoices", "headers": ["Vendor","Invoice #","Amount","Paid","Balance","Due Date"], "rows": tbl.values.tolist()}
    return tpl.TemplateResponse("app.html", base)


# ── Accounts Receivable ─────────────────────────────────────────────
@app.get("/ar")
def ar_page(request: Request, year: Optional[int] = None, month: Optional[int] = None):
    base = ctx(request, year, month, page_title="Accounts Receivable", page_subtitle="Track customer invoices and collections")
    y, m = base["sel_year"], base["sel_month"]
    df = load("accounts_receivable", "invoice_date", y, m)
    df["balance"] = df["balance"].fillna(0)
    df["received_amount"] = df["received_amount"].fillna(0)
    today = pd.Timestamp.today()

    base["cards"] = [
        {"title": "Total Outstanding", "value": fmt(df["balance"].sum())},
        {"title": "Total Received", "value": fmt(df["received_amount"].sum())},
        {"title": "Overdue Invoices", "value": num(int(((df["balance"] > 0) & (df["due_date"] < today)).sum()))},
        {"title": "Total Invoices", "value": num(len(df))},
    ]
    base["charts"] = []

    tbl = df[["customer_name","invoice_number","amount","received_amount","balance","due_date"]].fillna("").copy()
    tbl["amount"] = pd.to_numeric(tbl["amount"], errors="coerce").fillna(0).map(fmt)
    tbl["received_amount"] = pd.to_numeric(tbl["received_amount"], errors="coerce").fillna(0).map(fmt)
    tbl["balance"] = pd.to_numeric(tbl["balance"], errors="coerce").fillna(0).map(fmt)
    tbl["due_date"] = pd.to_datetime(tbl["due_date"]).map(date_txt)
    base["table"] = {"title": "Accounts Receivable Invoices", "headers": ["Customer","Invoice #","Amount","Received","Balance","Due Date"], "rows": tbl.values.tolist()}
    return tpl.TemplateResponse("app.html", base)


# ── General Ledger ──────────────────────────────────────────────────
@app.get("/gl")
def gl_page(request: Request, year: Optional[int] = None, month: Optional[int] = None):
    base = ctx(request, year, month, page_title="General Ledger", page_subtitle="Complete journal entries and balances")
    y, m = base["sel_year"], base["sel_month"]
    df = load("general_ledger", "entry_date", y, m)
    df["debit"] = df["debit"].fillna(0)
    df["credit"] = df["credit"].fillna(0)
    df["activity"] = df["debit"] + df["credit"]

    base["cards"] = [
        {"title": "Total Debit", "value": fmt(df["debit"].sum())},
        {"title": "Total Credit", "value": fmt(df["credit"].sum())},
        {"title": "Total Entries", "value": num(len(df))},
        {"title": "Net Balance", "value": fmt(df["debit"].sum() - df["credit"].sum())},
    ]
    top_accounts = (
        df.groupby(["account_code", "account_name"], as_index=False)["activity"]
          .sum()
          .sort_values("activity", ascending=False)
          .head(8)
          .sort_values("activity")
    )
    labels = (
        top_accounts["account_code"].astype(str).str.strip()
        + " - "
        + top_accounts["account_name"].astype(str).str.strip()
    ).tolist()
    base["charts"] = [{"title": "Top Ledger Accounts by Activity", "html": horizontal_amount_bar(
                        labels,
                        top_accounts["activity"].tolist(),
                        C["blue"],
                    )}]

    tbl = df[["entry_date","posting_date","account_code","account_name","debit","credit","is_reconciled"]].fillna("").copy()
    tbl["entry_date"] = pd.to_datetime(tbl["entry_date"]).map(date_txt)
    tbl["posting_date"] = pd.to_datetime(tbl["posting_date"]).map(date_txt)
    tbl["debit"] = pd.to_numeric(tbl["debit"], errors="coerce").fillna(0).map(fmt)
    tbl["credit"] = pd.to_numeric(tbl["credit"], errors="coerce").fillna(0).map(fmt)
    tbl["is_reconciled"] = tbl["is_reconciled"].map(yes_no)
    base["table"] = {"title": "General Ledger Records", "headers": ["Entry Date","Posting Date","Account Code","Account Name","Debit","Credit","Reconciled"], "rows": tbl.values.tolist()}
    return tpl.TemplateResponse("app.html", base)


# ── Chart of Accounts ───────────────────────────────────────────────
@app.get("/chart-of-accounts")
def coa_page(request: Request, year: Optional[int] = None, month: Optional[int] = None):
    base = ctx(request, year, month, page_title="Chart of Accounts", page_subtitle="Account structure and classifications")
    df = pd.read_sql_table("chart_of_accounts", engine)

    base["cards"] = [
        {"title": "Total Accounts", "value": num(len(df))},
        {"title": "Active Accounts", "value": num(int(df["is_active"].sum()))},
        {"title": "Header Accounts", "value": num(int(df["is_header"].sum()))},
        {"title": "Unique Account Types", "value": num(int(df["account_type"].dropna().nunique()))},
    ]
    types = df.groupby(df["account_type"].fillna("Unknown")).size()
    base["charts"] = [{"title": "Accounts by Type", "html": bar_chart(types.index.tolist(), types.values.tolist(),
                        [C["orange"],C["blue"],C["green"],C["red"],C["yellow"],C["purple"],C["pink"]][:len(types)])}]

    tbl = df[["account_code","account_name","account_type","sub_type","parent_code","normal_balance","is_active","is_header","currency"]].fillna("").copy()
    tbl["is_active"] = tbl["is_active"].map(yes_no)
    tbl["is_header"] = tbl["is_header"].map(yes_no)
    base["table"] = {"title": "Chart of Accounts Records", "headers": ["Account Code","Account Name","Account Type","Sub Type","Parent Code","Normal Balance","Active","Header","Currency"], "rows": tbl.values.tolist()}
    return tpl.TemplateResponse("app.html", base)


# ── Profit & Loss ───────────────────────────────────────────────────
@app.get("/pl")
def pl_page(request: Request, year: Optional[int] = None, month: Optional[int] = None):
    base = ctx(request, year, month, page_title="Profit & Loss", page_subtitle="Income statement and performance")
    y, m = base["sel_year"], base["sel_month"]
    df = load("profit_loss_statement", "period_start", y, m)

    base["cards"] = [
        {"title": "Total Revenue", "value": fmt(df["total_revenue"].sum())},
        {"title": "Total Expenses", "value": fmt(df["total_expenses"].sum())},
        {"title": "Total Net Income", "value": fmt(df["net_income"].sum())},
        {"title": "Total Periods", "value": num(len(df))},
    ]
    grouped, axis_title, tickformat = summarize_for_time_chart(
        df, "period_start", ["total_revenue", "total_expenses", "net_income"], y, m
    )
    base["charts"] = [{"title": "Revenue, Expenses & Net Income", "html": combo_time_chart(
                        grouped, "bucket",
                        [("Revenue","total_revenue",C["green"]), ("Expenses","total_expenses",C["red"])],
                        [("Net Income","net_income",C["orange"])],
                        axis_title=axis_title,
                        tickformat=tickformat,
                        left_title="Revenue / Expenses ($)",
                        right_title="Net Income ($)",
                    )}] if len(df) else []

    tbl = df[["period","period_start","period_end","total_revenue","total_expenses","operating_income","pre_tax_income","net_income"]].fillna(0).copy()
    tbl["period_start"] = tbl["period_start"].map(date_txt)
    tbl["period_end"] = tbl["period_end"].map(date_txt)
    tbl["total_revenue"] = tbl["total_revenue"].map(fmt)
    tbl["total_expenses"] = tbl["total_expenses"].map(fmt)
    tbl["operating_income"] = tbl["operating_income"].map(fmt)
    tbl["pre_tax_income"] = tbl["pre_tax_income"].map(fmt)
    tbl["net_income"] = tbl["net_income"].map(fmt)
    base["table"] = {"title": "Profit & Loss Records", "headers": ["Period","Period Start","Period End","Total Revenue","Total Expenses","Operating Income","Pre-Tax Income","Net Income"], "rows": tbl.values.tolist()}
    return tpl.TemplateResponse("app.html", base)


# ── Revenue Recognition ─────────────────────────────────────────────
@app.get("/revenue-recognition")
def rr_page(request: Request, year: Optional[int] = None, month: Optional[int] = None):
    base = ctx(request, year, month, page_title="Revenue Recognition", page_subtitle="Track recognized vs deferred revenues")
    y, m = base["sel_year"], base["sel_month"]
    df = load("revenue_recognition", "recognition_date", y, m)
    df["recognized_amount"] = df["recognized_amount"].fillna(0)
    df["deferred_amount"] = df["deferred_amount"].fillna(0)

    base["cards"] = [
        {"title": "Total Gross Amount", "value": fmt(df["gross_amount"].sum())},
        {"title": "Total Recognized", "value": fmt(df["recognized_amount"].sum())},
        {"title": "Total Deferred", "value": fmt(df["deferred_amount"].sum())},
        {"title": "Total Transactions", "value": num(len(df))},
    ]
    grouped, axis_title, tickformat = summarize_for_time_chart(
        df, "recognition_date", ["recognized_amount", "deferred_amount"], y, m
    )
    base["charts"] = [{"title": "Recognized vs Deferred Revenue", "html": grouped_bar(
                        grouped, "bucket",
                        [("Recognized","recognized_amount",C["green"]), ("Deferred","deferred_amount",C["red"])],
                        axis_title=axis_title,
                        tickformat=tickformat,
                        barmode="stack",
                    )}]

    tbl = df[["booking_date","service_date","recognition_date","flight_number","route","gross_amount","recognized_amount","deferred_amount","recognition_method","status"]].fillna("").copy()
    tbl["booking_date"] = pd.to_datetime(tbl["booking_date"]).map(date_txt)
    tbl["service_date"] = pd.to_datetime(tbl["service_date"]).map(date_txt)
    tbl["recognition_date"] = pd.to_datetime(tbl["recognition_date"]).map(date_txt)
    tbl["gross_amount"] = pd.to_numeric(tbl["gross_amount"], errors="coerce").fillna(0).map(fmt)
    tbl["recognized_amount"] = pd.to_numeric(tbl["recognized_amount"], errors="coerce").fillna(0).map(fmt)
    tbl["deferred_amount"] = pd.to_numeric(tbl["deferred_amount"], errors="coerce").fillna(0).map(fmt)
    base["table"] = {"title": "Recognition Records", "headers": ["Booking","Service","Recognition","Flight","Route","Gross","Recognized","Deferred","Method","Status"], "rows": tbl.values.tolist()}
    return tpl.TemplateResponse("app.html", base)
