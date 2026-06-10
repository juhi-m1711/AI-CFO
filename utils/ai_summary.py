import pandas as pd
import streamlit as st


# =====================================================
# Load Financial Intelligence Dataset
# =====================================================
@st.cache_data
def load_financial_data():

    try:
        df = pd.read_csv(
            "data/financial_intelligence.csv"
        )

    except:

        df = pd.DataFrame()

    return df


# =====================================================
# Load Transactions Dataset
# =====================================================
@st.cache_data
def load_transaction_data():

    try:
        df = pd.read_csv(
            "data/financial_transactions.csv"
        )

    except:

        df = pd.DataFrame()

    return df


# =====================================================
# Load Compliance Dataset
# =====================================================
@st.cache_data
def load_compliance_data():

    try:
        df = pd.read_csv(
            "data/compliance_tracking.csv"
        )

    except:

        df = pd.DataFrame()

    return df


# =====================================================
# Load GST Dataset
# =====================================================
@st.cache_data
def load_gst_data():

    try:
        df = pd.read_csv(
            "data/gst_tax_management.csv"
        )

    except:

        df = pd.DataFrame()

    return df


# =====================================================
# Financial Summary
# =====================================================
def get_financial_summary():

    summary = {
        "total_revenue": 0,
        "total_expense": 0,
        "net_profit": 0
    }

    df = load_financial_data()

    if df.empty:
        return summary

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns

    if len(numeric_columns) >= 2:

        revenue_col = numeric_columns[0]
        expense_col = numeric_columns[1]

        total_revenue = df[revenue_col].sum()
        total_expense = df[expense_col].sum()

        summary["total_revenue"] = total_revenue
        summary["total_expense"] = total_expense
        summary["net_profit"] = (
            total_revenue - total_expense
        )

    return summary


# =====================================================
# Transaction Summary
# =====================================================
def get_transaction_summary():

    summary = {
        "total_transactions": 0,
        "transaction_amount": 0
    }

    df = load_transaction_data()

    if df.empty:
        return summary

    summary["total_transactions"] = len(df)

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns

    if len(numeric_columns) > 0:

        summary["transaction_amount"] = (
            df[numeric_columns[0]].sum()
        )

    return summary


# =====================================================
# Compliance Summary
# =====================================================
def get_compliance_summary():

    summary = {
        "total_filings": 0,
        "pending_filings": 0,
        "completed_filings": 0
    }

    df = load_compliance_data()

    if df.empty:
        return summary

    summary["total_filings"] = len(df)

    if "Status" in df.columns:

        summary["pending_filings"] = len(
            df[
                df["Status"]
                .astype(str)
                .str.lower()
                .str.contains("pending")
            ]
        )

        summary["completed_filings"] = len(
            df[
                df["Status"]
                .astype(str)
                .str.lower()
                .str.contains("completed")
            ]
        )

    return summary


# =====================================================
# GST Summary
# =====================================================
def get_gst_summary():

    summary = {
        "gst_amount": 0
    }

    df = load_gst_data()

    if df.empty:
        return summary

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns

    if len(numeric_columns) > 0:

        summary["gst_amount"] = (
            df[numeric_columns[0]].sum()
        )

    return summary


# =====================================================
# Fraud Summary
# =====================================================
def get_fraud_summary():

    summary = {
        "fraud_cases": 0
    }

    summary["fraud_cases"] = st.session_state.get(
        "fraud_count",
        0
    )

    return summary


# =====================================================
# Cash Forecast Summary
# =====================================================
def get_forecast_summary():

    summary = {
        "forecast_status":
            "Cash flow forecast available"
    }

    return summary


# =====================================================
# Build AI Context
# =====================================================
def build_business_context():

    financial = get_financial_summary()

    transaction = get_transaction_summary()

    compliance = get_compliance_summary()

    gst = get_gst_summary()

    fraud = get_fraud_summary()

    forecast = get_forecast_summary()

    context = f"""

BUSINESS OVERVIEW

Revenue:
₹{financial['total_revenue']:,.2f}

Expenses:
₹{financial['total_expense']:,.2f}

Net Profit:
₹{financial['net_profit']:,.2f}

Total Transactions:
{transaction['total_transactions']}

Transaction Amount:
₹{transaction['transaction_amount']:,.2f}

Pending Compliance Filings:
{compliance['pending_filings']}

Completed Filings:
{compliance['completed_filings']}

GST Liability:
₹{gst['gst_amount']:,.2f}

Fraud Cases:
{fraud['fraud_cases']}

Forecast:
{forecast['forecast_status']}

"""

    return context