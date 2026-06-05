import pandas as pd
import json
import streamlit as st
import os

# ─────────────────────────────────────────
# PATHS — all data files live here
# ─────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
DATA_DIR  = os.path.join(BASE_DIR, '..', 'data')

TRANSACTIONS_PATH = os.path.join(DATA_DIR, 'sample_transactions.csv')
GST_PATH          = os.path.join(DATA_DIR, 'gst_data.csv')
FINANCIAL_PATH    = os.path.join(DATA_DIR, 'synthetic_financial_data.csv')
PAYROLL_PATH      = os.path.join(DATA_DIR, 'payroll_data.csv')
GST_RULES_PATH    = os.path.join(DATA_DIR, 'gst_rules.json')


# ─────────────────────────────────────────
# LOAD TRANSACTIONS
# ─────────────────────────────────────────
def load_transactions(filepath=None):
    """
    Loads transaction data.
    - If user uploaded a file → use that
    - If no file → use sample data
    Returns: pandas DataFrame
    """
    try:
        path = filepath if filepath else TRANSACTIONS_PATH
        df = pd.read_csv(path)
        return df
    except FileNotFoundError:
        st.error("❌ transactions file not found. Run generate_data.py first.")
        return None
    except Exception as e:
        st.error(f"❌ Error loading transactions: {e}")
        return None


# ─────────────────────────────────────────
# LOAD GST DATA
# ─────────────────────────────────────────
def load_gst_data(filepath=None):
    """
    Loads GST invoice data.
    - If user uploaded a file → use that
    - If no file → use sample data
    Returns: pandas DataFrame
    """
    try:
        path = filepath if filepath else GST_PATH
        df = pd.read_csv(path)
        return df
    except FileNotFoundError:
        st.error("❌ GST data file not found. Run generate_data.py first.")
        return None
    except Exception as e:
        st.error(f"❌ Error loading GST data: {e}")
        return None


# ─────────────────────────────────────────
# LOAD FINANCIAL DATA
# ─────────────────────────────────────────
def load_financial_data(filepath=None):
    """
    Loads monthly P&L financial data.
    Returns: pandas DataFrame
    """
    try:
        path = filepath if filepath else FINANCIAL_PATH
        df = pd.read_csv(path)
        return df
    except FileNotFoundError:
        st.error("❌ Financial data file not found. Run generate_data.py first.")
        return None
    except Exception as e:
        st.error(f"❌ Error loading financial data: {e}")
        return None


# ─────────────────────────────────────────
# LOAD PAYROLL DATA
# ─────────────────────────────────────────
def load_payroll_data(filepath=None):
    """
    Loads payroll data for all employees.
    Returns: pandas DataFrame
    """
    try:
        path = filepath if filepath else PAYROLL_PATH
        df = pd.read_csv(path)
        return df
    except FileNotFoundError:
        st.error("❌ Payroll data file not found. Run generate_data.py first.")
        return None
    except Exception as e:
        st.error(f"❌ Error loading payroll data: {e}")
        return None


# ─────────────────────────────────────────
# LOAD GST RULES
# ─────────────────────────────────────────
def load_gst_rules():
    """
    Loads GST rules from JSON file.
    Returns: Python dictionary
    """
    try:
        with open(GST_RULES_PATH, 'r') as f:
            rules = json.load(f)
        return rules
    except FileNotFoundError:
        st.error("❌ gst_rules.json not found. Run generate_data.py first.")
        return None
    except Exception as e:
        st.error(f"❌ Error loading GST rules: {e}")
        return None


# ─────────────────────────────────────────
# LOAD ALL DATA AT ONCE
# (called once in app.py on startup)
# ─────────────────────────────────────────
def load_all_data(
    txn_file=None,
    gst_file=None,
    fin_file=None,
    payroll_file=None
):
    """
    Master loader — loads all 5 data sources at once.
    Stores everything in st.session_state so
    every module can access it without reloading.

    Args:
        txn_file:     uploaded transactions file (optional)
        gst_file:     uploaded GST file (optional)
        fin_file:     uploaded financial file (optional)
        payroll_file: uploaded payroll file (optional)
    """
    st.session_state['transactions']  = load_transactions(txn_file)
    st.session_state['gst_data']      = load_gst_data(gst_file)
    st.session_state['financial_data']= load_financial_data(fin_file)
    st.session_state['payroll_data']  = load_payroll_data(payroll_file)
    st.session_state['gst_rules']     = load_gst_rules()
    st.session_state['data_loaded']   = True