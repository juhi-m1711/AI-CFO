"""
data_loader.py  —  reads every CSV from data/ folder
"""
import pandas as pd
import streamlit as st
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, '..', 'data')

def _path(filename):
    return os.path.join(DATA, filename)

@st.cache_data
def load_financial_transactions():
    df = pd.read_csv(_path('financial_transactions.csv'))
    df['Date']     = pd.to_datetime(df['Date'],     dayfirst=True, errors='coerce')
    df['Due_Date'] = pd.to_datetime(df['Due_Date'], dayfirst=True, errors='coerce')
    df.rename(columns={
        'Amount (₹)':   'Amount',
        'GST_Rate (%)': 'GST_Rate',
        'GST_Amt (₹)':  'GST_Amt',
        'Total (₹)':    'Total'
    }, inplace=True)
    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    return df

@st.cache_data
def load_gst_tax_management():
    df = pd.read_csv(_path('gst_tax_management.csv'))
    df['Due_Date']   = pd.to_datetime(df['Due_Date'],   dayfirst=True, errors='coerce')
    df['Filed_Date'] = pd.to_datetime(df['Filed_Date'], dayfirst=True, errors='coerce')

    for col in ['CGST (₹)', 'SGST (₹)', 'IGST (₹)', 'Total_GST (₹)', 'Penalty (₹)']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    df.rename(columns={
        'CGST (₹)':      'CGST',
        'SGST (₹)':      'SGST',
        'IGST (₹)':      'IGST',
        'Total_GST (₹)': 'Total_GST',
        'Penalty (₹)':   'Penalty'
    }, inplace=True)

    # ── ADD THIS LINE ──
    df["Compliance_Score"] = pd.to_numeric(
        df["Compliance_Score"].astype(str).str.replace("%", "").str.strip(),
        errors="coerce"
    )
    # ──────────────────

    return df


@st.cache_data
def load_payroll():
    df = pd.read_csv(_path('payroll_management.csv'))
    df['Joining_Date'] = pd.to_datetime(df['Joining_Date'], dayfirst=True, errors='coerce')
    df['Month']        = pd.to_datetime(df['Month'], format='%b-%Y', errors='coerce')
    for col in ['Basic_Salary (₹)', 'HRA (₹)', 'Allowances (₹)',
                'Gross_Salary (₹)', 'PF_Deduction (₹)', 'TDS (₹)', 'Net_Salary (₹)']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    df.rename(columns={
        'Basic_Salary (₹)': 'Basic_Salary',
        'HRA (₹)':          'HRA',
        'Allowances (₹)':   'Allowances',
        'Gross_Salary (₹)': 'Gross_Salary',
        'PF_Deduction (₹)': 'PF_Deduction',
        'TDS (₹)':          'TDS',
        'Net_Salary (₹)':   'Net_Salary'
    }, inplace=True)
    df['CTC'] = df['Gross_Salary'] + df['PF_Deduction']
    return df

@st.cache_data
def load_financial_intelligence():
    df = pd.read_csv(_path('financial_intelligence.csv'))
    df['Period'] = pd.to_datetime(df['Period'], format='%b-%Y', errors='coerce')
    for col in ['Revenue (₹)', 'COGS (₹)', 'Gross_Profit (₹)',
                'Operating_Expenses (₹)', 'EBITDA (₹)',
                'Net_Profit (₹)', 'Cash_Flow (₹)', 'Burn_Rate (₹)']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    df.rename(columns={
        'Revenue (₹)':            'Revenue',
        'COGS (₹)':               'COGS',
        'Gross_Profit (₹)':       'Gross_Profit',
        'Operating_Expenses (₹)': 'Operating_Expenses',
        'EBITDA (₹)':             'EBITDA',
        'Net_Profit (₹)':         'Net_Profit',
        'Cash_Flow (₹)':          'Cash_Flow',
        'Burn_Rate (₹)':          'Burn_Rate',
        'Profit_Margin (%)':      'Profit_Margin',
        'YoY_Growth (%)':         'YoY_Growth',
        'Forecast_Accuracy (%)':  'Forecast_Accuracy'
    }, inplace=True)

    # Inside load_financial_intelligence() — add after rename
    df["Profit_Margin"] = pd.to_numeric(
        df["Profit_Margin"].astype(str).str.replace("%", "").str.strip(),
        errors="coerce"
    )
    df["YoY_Growth"] = pd.to_numeric(
        df["YoY_Growth"].astype(str).str.replace("%", "").str.strip(),
        errors="coerce"
    )
    df["Forecast_Accuracy"] = pd.to_numeric(
        df["Forecast_Accuracy"].astype(str).str.replace("%", "").str.strip(),
        errors="coerce"
    )
    
    # Prophet columns
    df['ds'] = df['Period']
    df['y']  = df['Revenue']
    df['month_label'] = df['Period'].dt.strftime('%b %Y')
    return df

@st.cache_data
def load_compliance():
    df = pd.read_csv(_path('compliance_tracking.csv'))

    df['Due_Date'] = pd.to_datetime(
        df['Due_Date'],
        format='%d-%b-%y',
        errors='coerce'
    )

    df['Submitted_Date'] = pd.to_datetime(
        df['Submitted_Date'],
        format='%d-%b-%y',
        errors='coerce'
    )

    df['Penalty_Risk'] = pd.to_numeric(
        df['Penalty_Risk'],
        errors='coerce'
    ).fillna(0)

    return df

def load_all_data():
    """Master loader — fills session_state with all datasets."""
    import streamlit as st
    st.session_state['financial_transactions']  = load_financial_transactions()
    st.session_state['gst_data']                = load_gst_tax_management()
    st.session_state['payroll_data']            = load_payroll()
    st.session_state['financial_intelligence']  = load_financial_intelligence()
    st.session_state['compliance_data']         = load_compliance()
    st.session_state['data_loaded']             = True