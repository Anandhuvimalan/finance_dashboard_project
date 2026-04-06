from sqlalchemy import Column, Integer, String, Date, Numeric, Boolean, Text, TIMESTAMP
from app.database import Base


class ChartOfAccounts(Base):
    __tablename__ = "chart_of_accounts"

    id = Column(Integer, primary_key=True, index=True)
    account_code = Column(String(20), unique=True, nullable=False)
    account_name = Column(String(100), nullable=False)
    account_type = Column(String(50), nullable=False)
    sub_type = Column(String(50))
    parent_code = Column(String(20))
    description = Column(Text)
    normal_balance = Column(String(10))
    is_active = Column(Boolean, default=True)
    is_header = Column(Boolean, default=False)
    currency = Column(String(10), default="USD")
    created_at = Column(TIMESTAMP)


class DailyRevenue(Base):
    __tablename__ = "daily_revenue"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    passenger_mainline = Column(Numeric(14, 2), default=0)
    passenger_regional = Column(Numeric(14, 2), default=0)
    cargo_mail = Column(Numeric(14, 2), default=0)
    ancillary_bags = Column(Numeric(14, 2), default=0)
    ancillary_seats = Column(Numeric(14, 2), default=0)
    ancillary_wifi = Column(Numeric(14, 2), default=0)
    ancillary_other = Column(Numeric(14, 2), default=0)
    loyalty_program = Column(Numeric(14, 2), default=0)
    contract_carrier = Column(Numeric(14, 2), default=0)
    total_revenue = Column(Numeric(14, 2), nullable=False)
    load_factor = Column(Numeric(6, 2))
    rasm = Column(Numeric(10, 4))
    asm = Column(Numeric(14, 2))
    rpm = Column(Numeric(14, 2))
    created_at = Column(TIMESTAMP)


class DailyOperatingCost(Base):
    __tablename__ = "daily_operating_cost"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    fuel_oil = Column(Numeric(14, 2), default=0)
    salaries_flight_crew = Column(Numeric(14, 2), default=0)
    salaries_ground_staff = Column(Numeric(14, 2), default=0)
    maintenance_repair = Column(Numeric(14, 2), default=0)
    airport_landing_fees = Column(Numeric(14, 2), default=0)
    aircraft_lease_rent = Column(Numeric(14, 2), default=0)
    distribution_sales = Column(Numeric(14, 2), default=0)
    catering_inflight = Column(Numeric(14, 2), default=0)
    insurance_safety = Column(Numeric(14, 2), default=0)
    depreciation_amort = Column(Numeric(14, 2), default=0)
    other_operating = Column(Numeric(14, 2), default=0)
    total_operating_cost = Column(Numeric(14, 2), nullable=False)
    casm = Column(Numeric(10, 4))
    created_at = Column(TIMESTAMP)


class DailyProfit(Base):
    __tablename__ = "daily_profit"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    total_revenue = Column(Numeric(14, 2), nullable=False)
    total_operating_cost = Column(Numeric(14, 2), nullable=False)
    gross_profit = Column(Numeric(14, 2), nullable=False)
    non_operating_income = Column(Numeric(14, 2), default=0)
    non_operating_expense = Column(Numeric(14, 2), default=0)
    pre_tax_income = Column(Numeric(14, 2), nullable=False)
    tax_provision = Column(Numeric(14, 2), default=0)
    net_income = Column(Numeric(14, 2), nullable=False)
    operating_margin = Column(Numeric(8, 4))
    net_margin = Column(Numeric(8, 4))
    ebitda = Column(Numeric(14, 2))
    created_at = Column(TIMESTAMP)


class AccountsPayable(Base):
    __tablename__ = "accounts_payable"

    id = Column(Integer, primary_key=True, index=True)
    vendor_name = Column(String(100), nullable=False)
    vendor_code = Column(String(30))
    invoice_number = Column(String(50), unique=True, nullable=False)
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    amount = Column(Numeric(14, 2), nullable=False)
    paid_amount = Column(Numeric(14, 2), default=0)
    balance = Column(Numeric(14, 2), nullable=False)
    category = Column(String(50))
    payment_terms = Column(String(50))
    status = Column(String(30))
    currency = Column(String(10), default="USD")
    description = Column(Text)
    created_at = Column(TIMESTAMP)
    
class AccountsReceivable(Base):
    __tablename__ = "accounts_receivable"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(100), nullable=False)
    customer_code = Column(String(30))
    invoice_number = Column(String(50), unique=True, nullable=False)
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    amount = Column(Numeric(14, 2), nullable=False)
    received_amount = Column(Numeric(14, 2), default=0)
    balance = Column(Numeric(14, 2), nullable=False)
    category = Column(String(50))
    payment_terms = Column(String(50))
    status = Column(String(30))
    currency = Column(String(10), default="USD")
    description = Column(Text)
    created_at = Column(TIMESTAMP)    
    
class DailyExpense(Base):
    __tablename__ = "daily_expense"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    category = Column(String(50), nullable=False)
    subcategory = Column(String(50))
    description = Column(Text)
    amount = Column(Numeric(14, 2), nullable=False)
    department = Column(String(50))
    vendor = Column(String(100))
    cost_center = Column(String(50))
    approved_by = Column(String(100))
    status = Column(String(30))
    created_at = Column(TIMESTAMP)    
    
class GeneralLedger(Base):
    __tablename__ = "general_ledger"

    id = Column(Integer, primary_key=True, index=True)
    entry_date = Column(Date, nullable=False)
    posting_date = Column(Date, nullable=False)
    account_code = Column(String(20), nullable=False)
    account_name = Column(String(100), nullable=False)
    debit = Column(Numeric(14, 2), default=0)
    credit = Column(Numeric(14, 2), default=0)
    description = Column(Text)
    reference = Column(String(50))
    journal_type = Column(String(50))
    department = Column(String(50))
    cost_center = Column(String(50))
    fiscal_period = Column(String(20))
    is_reconciled = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP)    
    
class ProfitLossStatement(Base):
    __tablename__ = "profit_loss_statement"

    id = Column(Integer, primary_key=True, index=True)
    period = Column(String(20), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    passenger_revenue = Column(Numeric(14, 2), default=0)
    cargo_revenue = Column(Numeric(14, 2), default=0)
    ancillary_revenue = Column(Numeric(14, 2), default=0)
    loyalty_revenue = Column(Numeric(14, 2), default=0)
    other_revenue = Column(Numeric(14, 2), default=0)
    total_revenue = Column(Numeric(14, 2), nullable=False)
    fuel_expense = Column(Numeric(14, 2), default=0)
    labor_expense = Column(Numeric(14, 2), default=0)
    maintenance_expense = Column(Numeric(14, 2), default=0)
    airport_expense = Column(Numeric(14, 2), default=0)
    lease_expense = Column(Numeric(14, 2), default=0)
    distribution_expense = Column(Numeric(14, 2), default=0)
    catering_expense = Column(Numeric(14, 2), default=0)
    insurance_expense = Column(Numeric(14, 2), default=0)
    depreciation_expense = Column(Numeric(14, 2), default=0)
    other_expense = Column(Numeric(14, 2), default=0)
    total_expenses = Column(Numeric(14, 2), nullable=False)
    operating_income = Column(Numeric(14, 2), nullable=False)
    interest_expense = Column(Numeric(14, 2), default=0)
    interest_income = Column(Numeric(14, 2), default=0)
    fuel_hedging_gain_loss = Column(Numeric(14, 2), default=0)
    pre_tax_income = Column(Numeric(14, 2), nullable=False)
    income_tax = Column(Numeric(14, 2), default=0)
    net_income = Column(Numeric(14, 2), nullable=False)
    created_at = Column(TIMESTAMP)    

class RevenueRecognition(Base):
    __tablename__ = "revenue_recognition"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(50))
    transaction_type = Column(String(50))
    booking_date = Column(Date)
    service_date = Column(Date)
    recognition_date = Column(Date)
    gross_amount = Column(Numeric(14, 2))
    recognized_amount = Column(Numeric(14, 2))
    deferred_amount = Column(Numeric(14, 2))
    recognition_method = Column(String(50))
    performance_obligation = Column(String(100))
    status = Column(String(30))
    flight_number = Column(String(20))
    route = Column(String(50))
    notes = Column(Text)
    created_at = Column(TIMESTAMP)