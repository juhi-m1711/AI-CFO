import streamlit as st
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(page_title="AI CFO", page_icon="🔥", layout="wide")

# ── Load all data once on startup ──────────────────────────
if not st.session_state.get('data_loaded'):
    try:
        from utils.data_loader import (
            load_financial_transactions, load_gst_tax_management,
            load_fraud_detection, load_payroll,
            load_financial_intelligence, load_compliance
        )
        st.session_state['financial_transactions'] = load_financial_transactions()
        st.session_state['gst_data']               = load_gst_tax_management()
        st.session_state['fraud_data']             = load_fraud_detection()
        st.session_state['payroll_data']           = load_payroll()
        st.session_state['financial_intelligence'] = load_financial_intelligence()
        st.session_state['compliance_data']        = load_compliance()
        st.session_state['data_loaded']            = True
    except FileNotFoundError as e:
        st.error(f"❌ Data files not found: {e}")
        st.info("👉 Place **AI_Accounting_Platform_Dataset.xlsx** in the `data/` folder and run:\n```\npython data/generate_data.py\n```")
        st.stop()

# ── Sidebar ────────────────────────────────────────────────
st.sidebar.title("🔥 AI CFO")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigate", [
    "🏠 Home",
    "📊 Dashboard",
    "🧾 GST & Tax",
    "🚨 Fraud Detection",
    "📈 Cash Forecast",
    "📋 Compliance",
    "🤖 AI Assistant"
])

st.sidebar.markdown("---")
if st.session_state.get('data_loaded'):
    txn  = st.session_state['financial_transactions']
    gst  = st.session_state['gst_data']
    st.sidebar.success("✅ Data loaded")
    st.sidebar.caption(f"📄 {len(txn)} transactions")
    st.sidebar.caption(f"🧾 {len(gst)} GST records")
st.sidebar.markdown("---")
st.sidebar.caption("Fireblaze Tech League 2025")

# ── Page Routing ───────────────────────────────────────────
if page == "🏠 Home":
    st.title("🔥 Welcome to AI CFO")
    st.subheader("Your Intelligent Finance Partner")
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("📊 **Dashboard**\nRevenue, expenses & profit insights")
        st.info("📋 **Compliance**\nRegulatory deadline tracker")
    with c2:
        st.info("🧾 **GST & Tax**\nCompliance score & filing status")
        st.info("📈 **Cash Forecast**\n24-month revenue prediction")
    with c3:
        st.info("🚨 **Fraud Detection**\nML-powered anomaly detection")
        st.info("🤖 **AI Assistant**\nAsk anything about your finances")
    st.markdown("---")
    st.markdown("👈 **Use the sidebar to navigate.**")

elif page == "📊 Dashboard":
    from modules.dashboard import show
    show()

elif page == "🧾 GST & Tax":
    from modules.gst_tracker import show
    show()

elif page == "🚨 Fraud Detection":
    from modules.fraud_detection import show
    show()

elif page == "📈 Cash Forecast":
    from modules.cash_forecast import show
    show()

elif page == "📋 Compliance":
    from modules.compliance import show
    show()

elif page == "🤖 AI Assistant":
    from modules.ai_assistant import show
    show()