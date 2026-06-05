import pandas as pd
import numpy as np


# ─────────────────────────────────────────
# PREPROCESS TRANSACTIONS
# ─────────────────────────────────────────
def preprocess_transactions(df):
    """
    Cleans and prepares transaction data.

    What it does:
    1. Fixes date column to proper datetime format
    2. Makes sure amount is a number
    3. Standardizes text columns (lowercase, strip spaces)
    4. Removes duplicate transactions
    5. Removes rows where amount is missing
    6. Adds helper columns used by modules

    Input:  raw DataFrame from load_transactions()
    Output: clean DataFrame ready for dashboard, fraud detection
    """
    if df is None:
        return None

    df = df.copy()

    # 1. Fix date format
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # 2. Make sure amount is numeric, force errors to NaN
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

    # 3. Standardize text columns
    df['category'] = df['category'].str.strip().str.title()
    df['type']     = df['type'].str.strip().str.lower()

    # 4. Remove duplicates based on txn_id
    df = df.drop_duplicates(subset='txn_id', keep='first')

    # 5. Remove rows with missing amount or date
    df = df.dropna(subset=['amount', 'date'])

    # 6. Add helper columns
    # year-month string (used for grouping in charts)
    df['month'] = df['date'].dt.to_period('M').astype(str)

    # separate columns for revenue and expense
    df['revenue'] = df['amount'].where(df['type'] == 'credit', 0)
    df['expense'] = df['amount'].where(df['type'] == 'debit', 0)

    # day of week (used in fraud detection — 3AM transactions)
    df['day_of_week'] = df['date'].dt.day_name()
    df['hour']        = df['date'].dt.hour

    # Reset index cleanly
    df = df.reset_index(drop=True)

    return df


# ─────────────────────────────────────────
# PREPROCESS GST DATA
# ─────────────────────────────────────────
def preprocess_gst(df):
    """
    Cleans and prepares GST invoice data.

    What it does:
    1. Fixes date column
    2. Calculates GST amount from rate + taxable amount
    3. Calculates total invoice amount
    4. Adds overdue flag
    5. Calculates compliance score

    Input:  raw DataFrame from load_gst_data()
    Output: clean DataFrame ready for GST tracker
    """
    if df is None:
        return None

    df = df.copy()

    # 1. Fix date
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # 2. Calculate GST amount
    # GST amount = taxable_amount × (gst_rate / 100)
    df['gst_amount'] = (
        df['taxable_amount'] * df['gst_rate'] / 100
    ).round(2)

    # 3. Total invoice amount = taxable + gst
    df['total_amount'] = df['taxable_amount'] + df['gst_amount']

    # 4. Standardize filing_status
    df['filing_status'] = df['filing_status'].str.strip().str.lower()

    # 5. Add numeric score per invoice
    # filed = 1, pending = 0, overdue = -1
    status_score = {'filed': 1, 'pending': 0, 'overdue': -1}
    df['status_score'] = df['filing_status'].map(status_score).fillna(0)

    # 6. Month column for grouping
    df['month'] = df['date'].dt.to_period('M').astype(str)

    df = df.reset_index(drop=True)

    return df


# ─────────────────────────────────────────
# PREPROCESS FINANCIAL DATA
# ─────────────────────────────────────────
def preprocess_financial(df):
    """
    Cleans monthly P&L data for dashboard + forecasting.

    What it does:
    1. Fixes month column to datetime
    2. Ensures all number columns are numeric
    3. Calculates profit margin if missing
    4. Adds month labels for charts

    Input:  raw DataFrame from load_financial_data()
    Output: clean DataFrame ready for dashboard + Prophet
    """
    if df is None:
        return None

    df = df.copy()

    # 1. Parse month column
    df['month'] = pd.to_datetime(df['month'], errors='coerce')

    # 2. Make sure number columns are numeric
    num_cols = [
        'revenue', 'total_expense', 'profit',
        'cash_flow', 'accounts_receivable', 'accounts_payable'
    ]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # 3. Recalculate profit margin (in case of rounding errors)
    df['profit_margin_pct'] = (
        (df['profit'] / df['revenue']) * 100
    ).round(2)

    # 4. Add display-friendly month label (Jan 2024, Feb 2024...)
    df['month_label'] = df['month'].dt.strftime('%b %Y')

    # 5. Prepare Prophet-ready columns
    # Prophet needs exactly 'ds' (date) and 'y' (value)
    df['ds'] = df['month']
    df['y']  = df['revenue']

    df = df.reset_index(drop=True)

    return df


# ─────────────────────────────────────────
# PREPROCESS PAYROLL DATA
# ─────────────────────────────────────────
def preprocess_payroll(df):
    """
    Cleans payroll data for payroll module + AI assistant.

    What it does:
    1. Fixes month column
    2. Ensures salary columns are numeric
    3. Calculates total cost to company (CTC)
    4. Adds department-level summary

    Input:  raw DataFrame from load_payroll_data()
    Output: clean DataFrame ready for payroll analysis
    """
    if df is None:
        return None

    df = df.copy()

    # 1. Parse month
    df['month'] = pd.to_datetime(df['month'], errors='coerce')

    # 2. Numeric salary columns
    salary_cols = [
        'basic_salary', 'hra', 'allowances', 'gross_salary',
        'pf_employee', 'pf_employer', 'esi', 'tds', 'net_salary'
    ]
    for col in salary_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # 3. Total Cost to Company (CTC)
    # CTC = gross salary + employer PF contribution
    df['ctc'] = df['gross_salary'] + df['pf_employer']

    # 4. Standardize text
    df['department']     = df['department'].str.strip()
    df['payment_status'] = df['payment_status'].str.strip().str.lower()

    # 5. Month label
    df['month_label'] = df['month'].dt.strftime('%b %Y')

    df = df.reset_index(drop=True)

    return df


# ─────────────────────────────────────────
# PREPROCESS ALL — master function
# (called after load_all_data in app.py)
# ─────────────────────────────────────────
def preprocess_all(session):
    """
    Runs all preprocessors on session_state data.
    Updates session_state with clean versions.

    Call this right after load_all_data().

    Usage in app.py:
        from utils.data_loader   import load_all_data
        from utils.preprocessor  import preprocess_all

        load_all_data()
        preprocess_all(st.session_state)
    """
    session['transactions']   = preprocess_transactions(
                                    session.get('transactions'))
    session['gst_data']       = preprocess_gst(
                                    session.get('gst_data'))
    session['financial_data'] = preprocess_financial(
                                    session.get('financial_data'))
    session['payroll_data']   = preprocess_payroll(
                                    session.get('payroll_data'))


# ─────────────────────────────────────────
# HELPER: Get summary stats for AI assistant
# ─────────────────────────────────────────
def get_summary_for_ai(session):
    """
    Builds a short text summary of all data.
    This is injected into the Gemini API system prompt
    so the AI assistant can answer personalized questions.

    Returns: string summary
    """
    summary = []

    # Financial summary
    fin = session.get('financial_data')
    if fin is not None and not fin.empty:
        latest        = fin.iloc[-1]
        total_revenue = fin['revenue'].sum()
        total_expense = fin['total_expense'].sum()
        avg_margin    = fin['profit_margin_pct'].mean()
        summary.append(
            f"Financial overview (12 months): "
            f"Total revenue ₹{total_revenue:,.0f}, "
            f"Total expenses ₹{total_expense:,.0f}, "
            f"Average profit margin {avg_margin:.1f}%. "
            f"Latest month: ₹{latest['revenue']:,.0f} revenue, "
            f"₹{latest['profit']:,.0f} profit."
        )

    # GST summary
    gst = session.get('gst_data')
    if gst is not None and not gst.empty:
        total    = len(gst)
        filed    = (gst['filing_status'] == 'filed').sum()
        pending  = (gst['filing_status'] == 'pending').sum()
        overdue  = (gst['filing_status'] == 'overdue').sum()
        score    = round((filed / total) * 100, 1)
        summary.append(
            f"GST compliance: {total} invoices total — "
            f"{filed} filed, {pending} pending, {overdue} overdue. "
            f"Compliance score: {score}%."
        )

    # Fraud summary
    txn = session.get('transactions')
    if txn is not None and not txn.empty:
        total_txn = len(txn)
        summary.append(
            f"Transactions: {total_txn} total records loaded."
        )

    # Payroll summary
    pay = session.get('payroll_data')
    if pay is not None and not pay.empty:
        employees  = pay['emp_id'].nunique()
        total_cost = pay['ctc'].sum()
        summary.append(
            f"Payroll: {employees} employees, "
            f"total annual CTC ₹{total_cost:,.0f}."
        )

    return " | ".join(summary) if summary else "No data loaded."