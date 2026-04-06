import os
from sqlalchemy import create_engine, MetaData, Table, update, select
from datetime import date

DATABASE_URL = "postgresql+psycopg2://postgres:7025465177%40Pgadmin@localhost:5432/finance_dashboard"
engine = create_engine(DATABASE_URL)
metadata = MetaData()
metadata.reflect(bind=engine)

# Fix Daily Expense Categories and missing fields
if 'daily_expense' in metadata.tables:
    exp = metadata.tables['daily_expense']
    with engine.begin() as conn:
        conn.execute(update(exp).where(exp.c.category == 'Marketing').values(
            department='Sales', vendor='Global Ad Agency', cost_center='MKT-100', approved_by='Jane Doe'
        ))
        conn.execute(update(exp).where(exp.c.amount > 3000).values(category='Maintenance', department='Eng', cost_center='ENG-200', vendor='Parts Inc', status='Paid'))
        conn.execute(update(exp).where(exp.c.amount < 2000).values(category='Operations', department='Ops', cost_center='OPS-300', vendor='Sysco', status='Pending'))

# Fix Accounts Payable vendor names and categories
if 'accounts_payable' in metadata.tables:
    ap = metadata.tables['accounts_payable']
    with engine.begin() as conn:
        conn.execute(update(ap).where(ap.c.vendor == 'Vendor 1 Aviation').values(category='Fuel', vendor='Global Fuels', status='Paid'))
        conn.execute(update(ap).where(ap.c.vendor == 'Vendor 2 Aviation').values(category='Maintenance', vendor='AeroParts Ltd', status='Partial'))
        conn.execute(update(ap).where(ap.c.vendor.like('Vendor%')).values(category='Services', status='Pending'))

# Fix Accounts Receivable
if 'accounts_receivable' in metadata.tables:
    ar = metadata.tables['accounts_receivable']
    with engine.begin() as conn:
        conn.execute(update(ar).where(ar.c.customer == 'Customer 1 Aviation').values(category='Charter', customer='Delta Corp', status='Paid'))
        conn.execute(update(ar).where(ar.c.customer == 'Customer 2 Aviation').values(category='Cargo', customer='FedEx Logistics', status='Partial'))
        conn.execute(update(ar).where(ar.c.customer.like('Customer%')).values(category='Leasing', status='Pending'))

print("Database nulls and dummy strings fixed.")
