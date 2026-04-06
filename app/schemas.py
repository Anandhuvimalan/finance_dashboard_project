from pydantic import BaseModel
from datetime import date
from typing import Optional
from decimal import Decimal

class RevenueCreate(BaseModel):
    date: date
    passenger_mainline: Decimal = Decimal(0)
    passenger_regional: Decimal = Decimal(0)
    cargo_mail: Decimal = Decimal(0)
    ancillary_bags: Decimal = Decimal(0)
    ancillary_seats: Decimal = Decimal(0)
    ancillary_wifi: Decimal = Decimal(0)
    ancillary_other: Decimal = Decimal(0)
    loyalty_program: Decimal = Decimal(0)
    contract_carrier: Decimal = Decimal(0)
    total_revenue: Decimal
    load_factor: Optional[Decimal] = None

class OperatingCostCreate(BaseModel):
    date: date
    fuel_oil: Decimal = Decimal(0)
    salaries_flight_crew: Decimal = Decimal(0)
    salaries_ground_staff: Decimal = Decimal(0)
    maintenance_repair: Decimal = Decimal(0)
    airport_landing_fees: Decimal = Decimal(0)
    aircraft_lease_rent: Decimal = Decimal(0)
    distribution_sales: Decimal = Decimal(0)
    catering_inflight: Decimal = Decimal(0)
    insurance_safety: Decimal = Decimal(0)
    depreciation_amort: Decimal = Decimal(0)
    other_operating: Decimal = Decimal(0)
    total_operating_cost: Decimal
    casm: Optional[Decimal] = None

class DailyExpenseCreate(BaseModel):
    date: date
    category: str
    subcategory: Optional[str] = None
    description: Optional[str] = None
    amount: Decimal
    department: Optional[str] = None
    vendor: Optional[str] = None
    cost_center: Optional[str] = None
    approved_by: Optional[str] = None
    status: Optional[str] = "Pending"

class AccountsPayableCreate(BaseModel):
    vendor_name: str
    vendor_code: Optional[str] = None
    invoice_number: str
    invoice_date: date
    due_date: date
    amount: Decimal
    paid_amount: Decimal = Decimal(0)
    balance: Decimal
    category: Optional[str] = None
    payment_terms: Optional[str] = None
    status: Optional[str] = "Pending"
    currency: Optional[str] = "USD"
    description: Optional[str] = None

class AccountsReceivableCreate(BaseModel):
    customer_name: str
    customer_code: Optional[str] = None
    invoice_number: str
    invoice_date: date
    due_date: date
    amount: Decimal
    received_amount: Decimal = Decimal(0)
    balance: Decimal
    category: Optional[str] = None
    payment_terms: Optional[str] = None
    status: Optional[str] = "Pending"
    currency: Optional[str] = "USD"
    description: Optional[str] = None

class GeneralLedgerCreate(BaseModel):
    entry_date: date
    posting_date: date
    account_code: str
    account_name: str
    debit: Decimal = Decimal(0)
    credit: Decimal = Decimal(0)
    description: Optional[str] = None
    reference: Optional[str] = None
    journal_type: Optional[str] = None
    department: Optional[str] = None
    cost_center: Optional[str] = None
    fiscal_period: Optional[str] = None

class ChartOfAccountsCreate(BaseModel):
    account_code: str
    account_name: str
    account_type: str
    sub_type: Optional[str] = None
    normal_balance: Optional[str] = None
    is_active: bool = True

class ProfitLossCreate(BaseModel):
    period: str
    period_start: date
    period_end: date
    passenger_revenue: Decimal = Decimal(0)
    cargo_revenue: Decimal = Decimal(0)
    ancillary_revenue: Decimal = Decimal(0)
    loyalty_revenue: Decimal = Decimal(0)
    other_revenue: Decimal = Decimal(0)
    total_revenue: Decimal
    fuel_expense: Decimal = Decimal(0)
    labor_expense: Decimal = Decimal(0)
    maintenance_expense: Decimal = Decimal(0)
    airport_expense: Decimal = Decimal(0)
    lease_expense: Decimal = Decimal(0)
    distribution_expense: Decimal = Decimal(0)
    catering_expense: Decimal = Decimal(0)
    insurance_expense: Decimal = Decimal(0)
    depreciation_expense: Decimal = Decimal(0)
    other_expense: Decimal = Decimal(0)
    total_expenses: Decimal
    operating_income: Decimal
    interest_expense: Decimal = Decimal(0)
    interest_income: Decimal = Decimal(0)
    fuel_hedging_gain_loss: Decimal = Decimal(0)
    pre_tax_income: Decimal
    income_tax: Decimal = Decimal(0)
    net_income: Decimal

class RevenueRecognitionCreate(BaseModel):
    transaction_id: Optional[str] = None
    transaction_type: Optional[str] = None
    booking_date: date
    service_date: date
    recognition_date: date
    gross_amount: Decimal = Decimal(0)
    recognized_amount: Decimal = Decimal(0)
    deferred_amount: Decimal = Decimal(0)
    recognition_method: Optional[str] = None
    performance_obligation: Optional[str] = None
    status: Optional[str] = "Pending"
    flight_number: Optional[str] = None
    route: Optional[str] = None
    notes: Optional[str] = None
