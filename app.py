import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="AI CFO",
    page_icon="🔥",
    layout="wide"
)

# ─────────────────────────────────────────
# LOAD ALL DATA ON STARTUP
# Runs once when app starts
# Fills session_state so all modules work
# ─────────────────────────────────────────
@st.cache_data
def load_data():
    """
    Reads all CSV files once and caches them.
    @st.cache_data means it won't re-read files
    every time user clicks a page — much faster.
    """
    base = os.path.dirname(os.path.abspath(__file__))
    data = os.path.join(base, 'data')

    transactions   = pd.read_csv(os.path.join(data, 'sample_transactions.csv'))
    gst_data       = pd.read_csv(os.path.join(data, 'gst_data.csv'))
    financial_data = pd.read_csv(os.path.join(data, 'synthetic_financial_data.csv'))
    payroll_data   = pd.read_csv(os.path.join(data, 'payroll_data.csv'))

    # Fix date columns
    transactions['date']   = pd.to_datetime(transactions['date'])
    gst_data['date']       = pd.to_datetime(gst_data['date'])
    financial_data['month']= pd.to_datetime(financial_data['month'])
    payroll_data['month']  = pd.to_datetime(payroll_data['month'])

    # Add helper columns for transactions
    transactions['month']      = transactions['date'].dt.to_period('M').astype(str)
    transactions['revenue']    = transactions['amount'].where(transactions['type'] == 'credit', 0)
    transactions['expense']    = transactions['amount'].where(transactions['type'] == 'debit', 0)

    # Add helper columns for financial data (Prophet needs ds + y)
    financial_data['ds']          = financial_data['month']
    financial_data['y']           = financial_data['revenue']
    financial_data['month_label'] = financial_data['month'].dt.strftime('%b %Y')

    # Add helper columns for GST
    gst_data['gst_amount']   = (gst_data['taxable_amount'] * gst_data['gst_rate'] / 100).round(2)
    gst_data['total_amount'] = gst_data['taxable_amount'] + gst_data['gst_amount']
    gst_data['month']        = gst_data['date'].dt.to_period('M').astype(str)

    # Add helper columns for payroll
    payroll_data['ctc']          = payroll_data['gross_salary'] + payroll_data['pf_employer']
    payroll_data['month_label']  = payroll_data['month'].dt.strftime('%b %Y')

    return transactions, gst_data, financial_data, payroll_data


# ─────────────────────────────────────────
# FILL SESSION STATE ONCE
# ─────────────────────────────────────────
if not st.session_state.get('data_loaded'):
    try:
        txn, gst, fin, pay = load_data()

        st.session_state['transactions']   = txn
        st.session_state['gst_data']       = gst
        st.session_state['financial_data'] = fin
        st.session_state['payroll_data']   = pay
        st.session_state['data_loaded']    = True

    except FileNotFoundError as e:
        st.error(f"❌ Data files not found: {e}")
        st.info("👉 Run this first: `python data/generate_data.py`")
        st.stop()


# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
st.sidebar.title("🔥 AI CFO")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigate", [
    "🏠 Home",
    "📊 Dashboard",
    "🧾 GST Tracker",
    "🚨 Fraud Detection",
    "📈 Cash Forecast",
    "🤖 AI Assistant"
])

st.sidebar.markdown("---")

# Show data status in sidebar
if st.session_state.get('data_loaded'):
    txn_count = len(st.session_state['transactions'])
    gst_count = len(st.session_state['gst_data'])
    st.sidebar.success(f"✅ Data loaded")
    st.sidebar.caption(f"📄 {txn_count} transactions")
    st.sidebar.caption(f"🧾 {gst_count} GST invoices")

st.sidebar.markdown("---")
st.sidebar.caption("Fireblaze Tech League 2025")


# ─────────────────────────────────────────
# PAGE ROUTING
# ─────────────────────────────────────────
if page == "🏠 Home":
    st.title("🔥 Welcome to AI CFO")
    st.subheader("Your Intelligent Finance Partner")
    st.markdown("---")

    st.markdown("""
    ### What can AI CFO do for you?
    """)

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.info("📊 **Dashboard**\nRevenue, expenses & profit insights")
    with c2:
        st.info("🧾 **GST Tracker**\nCompliance score & filing deadlines")
    with c3:
        st.info("🚨 **Fraud Detection**\nML-powered anomaly detection")
    with c4:
        st.info("📈 **Cash Forecast**\n90-day revenue prediction")
    with c5:
        st.info("🤖 **AI Assistant**\nAsk anything about your finances")

    st.markdown("---")
    st.markdown("👈 **Use the sidebar to navigate between features.**")

elif page == "📊 Dashboard":
    from modules.dashboard import show
    show()

elif page == "🧾 GST Tracker":
    from modules.gst_tracker import show
    show()

elif page == "🚨 Fraud Detection":
    from modules.fraud_detection import show
    show()

elif page == "📈 Cash Forecast":
    from modules.cash_forecast import show
    show()

elif page == "🤖 AI Assistant":
    from modules.ai_assistant import show
    show()