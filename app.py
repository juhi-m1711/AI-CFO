import streamlit as st
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Page config ────────────────────────────────────────────
st.set_page_config(
    page_title="AI CFO",
    page_icon="◢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Zoho Books inspired CSS ────────────────────────────────
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

/* ── Global reset ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Manrope', sans-serif !important;
    background-color: #F4F5F7 !important;
    color: #1A1F36 !important;
}

/* ── Hide Streamlit branding ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── Sidebar — Zoho style: white, icon-driven ── */
[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E8ECF0 !important;
    padding-top: 0 !important;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important;
}

/* Sidebar logo area */
.sidebar-logo {
    background: #FFFFFF;
    padding: 20px 20px 16px 20px;
    border-bottom: 1px solid #E8ECF0;
    margin-bottom: 8px;
}

.sidebar-logo-text {
    font-size: 18px;
    font-weight: 800;
    color: #1A1F36;
    letter-spacing: -0.5px;
}

.sidebar-logo-sub {
    font-size: 11px;
    color: #8492A6;
    margin-top: 2px;
    font-weight: 500;
}

/* Sidebar nav radio buttons → Zoho-style menu items */
[data-testid="stSidebar"] .stRadio > div {
    gap: 2px !important;
}

[data-testid="stSidebar"] .stRadio label {
    display: flex !important;
    align-items: center !important;
    padding: 10px 16px !important;
    border-radius: 8px !important;
    margin: 1px 8px !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
    font-size: 13.5px !important;
    font-weight: 500 !important;
    color: #4A5568 !important;
    background: transparent !important;
    border: none !important;
}

[data-testid="stSidebar"] .stRadio label:hover {
    background: #F0FBF4 !important;
    color: #1A7F4B !important;
}

[data-testid="stSidebar"] .stRadio label[data-checked="true"],
[data-testid="stSidebar"] .stRadio input:checked + div {
    background: #E8F7EF !important;
    color: #1A7F4B !important;
    font-weight: 600 !important;
}

/* Hide radio circles */
[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
    font-size: 13.5px !important;
}

[data-testid="stSidebar"] .stRadio > div > label > div:first-child {
    display: none !important;
}

/* Sidebar section header */
.nav-section {
    font-size: 10px;
    font-weight: 700;
    color: #A0AEC0;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 12px 24px 4px 24px;
}

/* Sidebar data pills */
.data-pill {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 16px;
    margin: 2px 8px;
    background: #F8FAFC;
    border-radius: 8px;
    font-size: 12px;
    color: #4A5568;
}

.data-pill span { font-weight: 600; color: #1A7F4B; }

/* ── Top bar ── */
.top-bar {
    background: #FFFFFF;
    border-bottom: 1px solid #E8ECF0;
    padding: 14px 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: -1rem -1rem 1.5rem -1rem;
    position: sticky;
    top: 0;
    z-index: 100;
}

.top-bar-title {
    font-size: 18px;
    font-weight: 700;
    color: #1A1F36;
}

.top-bar-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #E8F7EF;
    color: #1A7F4B;
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}

/* ── KPI Cards — Zoho style ── */
.kpi-card {
    background: #FFFFFF;
    border: 1px solid #E8ECF0;
    border-radius: 12px;
    padding: 20px 22px;
    transition: box-shadow 0.2s ease;
}

.kpi-card:hover {
    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}

.kpi-label {
    font-size: 11px;
    font-weight: 600;
    color: #8492A6;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 8px;
}

.kpi-value {
    font-size: 26px;
    font-weight: 800;
    color: #1A1F36;
    line-height: 1.1;
    letter-spacing: -0.5px;
}

.kpi-sub {
    font-size: 12px;
    color: #8492A6;
    margin-top: 6px;
    font-weight: 500;
}

.kpi-delta-up {
    display: inline-flex;
    align-items: center;
    gap: 3px;
    font-size: 12px;
    font-weight: 600;
    color: #1A7F4B;
    background: #E8F7EF;
    padding: 2px 8px;
    border-radius: 20px;
    margin-top: 8px;
}

.kpi-delta-down {
    display: inline-flex;
    align-items: center;
    gap: 3px;
    font-size: 12px;
    font-weight: 600;
    color: #C53030;
    background: #FFF5F5;
    padding: 2px 8px;
    border-radius: 20px;
    margin-top: 8px;
}

.kpi-icon {
    font-size: 20px;
    margin-bottom: 10px;
    display: block;
}

/* ── Section card ── */
.section-card {
    background: #FFFFFF;
    border: 1px solid #E8ECF0;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
}

.section-title {
    font-size: 14px;
    font-weight: 700;
    color: #1A1F36;
    margin-bottom: 4px;
}

.section-sub {
    font-size: 12px;
    color: #8492A6;
    margin-bottom: 16px;
}

/* ── Status badges ── */
.badge-green  { background:#E8F7EF; color:#1A7F4B; padding:3px 10px; border-radius:20px; font-size:11px; font-weight:600; }
.badge-red    { background:#FFF5F5; color:#C53030; padding:3px 10px; border-radius:20px; font-size:11px; font-weight:600; }
.badge-orange { background:#FFFBEB; color:#B45309; padding:3px 10px; border-radius:20px; font-size:11px; font-weight:600; }
.badge-blue   { background:#EBF8FF; color:#2B6CB0; padding:3px 10px; border-radius:20px; font-size:11px; font-weight:600; }

/* ── Streamlit metric overrides ── */
[data-testid="metric-container"] {
    background: #FFFFFF !important;
    border: 1px solid #E8ECF0 !important;
    border-radius: 12px !important;
    padding: 18px 20px !important;
}

[data-testid="stMetricLabel"] {
    font-size: 11px !important;
    font-weight: 600 !important;
    color: #8492A6 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}

[data-testid="stMetricValue"] {
    font-size: 24px !important;
    font-weight: 800 !important;
    color: #1A1F36 !important;
    letter-spacing: -0.5px !important;
}

[data-testid="stMetricDelta"] svg { display: none; }

/* ── Streamlit tabs → Zoho style ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 2px solid #E8ECF0 !important;
    gap: 0 !important;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    color: #8492A6 !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
    border-bottom: 2px solid transparent !important;
    margin-bottom: -2px !important;
}

.stTabs [aria-selected="true"] {
    color: #1A7F4B !important;
    border-bottom: 2px solid #1A7F4B !important;
}

/* ── Buttons ── */
.stButton > button {
    background: #1A7F4B !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    padding: 8px 20px !important;
    font-family: 'Manrope', sans-serif !important;
    transition: all 0.15s ease !important;
}

.stButton > button:hover {
    background: #166340 !important;
    box-shadow: 0 4px 12px rgba(26,127,75,0.3) !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border: 1px solid #E8ECF0 !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}

/* ── Alerts/info boxes ── */
.stAlert {
    border-radius: 10px !important;
    border: none !important;
    font-size: 13px !important;
}

/* ── Sidebar success/caption ── */
[data-testid="stSidebar"] .stSuccess {
    background: #E8F7EF !important;
    color: #1A7F4B !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 12px !important;
}

[data-testid="stSidebar"] .stCaption {
    color: #8492A6 !important;
    font-size: 11.5px !important;
}

/* ── Divider ── */
hr {
    border-color: #E8ECF0 !important;
    margin: 1rem 0 !important;
}

/* ── Main content padding ── */
.main .block-container {
    padding-top: 1rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100% !important;
}

/* ── Page title style ── */
h1 {
    font-size: 22px !important;
    font-weight: 800 !important;
    color: #1A1F36 !important;
    letter-spacing: -0.5px !important;
}

h2 {
    font-size: 16px !important;
    font-weight: 700 !important;
    color: #1A1F36 !important;
}

h3 {
    font-size: 14px !important;
    font-weight: 700 !important;
    color: #1A1F36 !important;
}

/* ── Selectbox / input ── */
.stSelectbox > div > div,
.stTextInput > div > div {
    border-radius: 8px !important;
    border-color: #E8ECF0 !important;
    font-size: 13px !important;
}

/* ── Spinner ── */
.stSpinner > div {
    border-top-color: #1A7F4B !important;
}


/* ===== Sidebar Visibility Fix ===== */
[data-testid="stSidebar"] .stRadio label p {
    color:#1A1F36 !important;
    opacity:1 !important;
    font-weight:600 !important;
}

[data-testid="stSidebar"] .stRadio input:checked + div p {
    color:#1A7F4B !important;
    font-weight:700 !important;
}

/* ===== Hero Banner ===== */
.hero-banner {
    background: linear-gradient(135deg,#1A7F4B,#22C55E);
    color:white;
    padding:30px;
    border-radius:16px;
    margin-bottom:20px;
}
.hero-title {
    font-size:30px;
    font-weight:800;
}
.hero-sub {
    opacity:0.9;
    margin-top:8px;
}

</style>
""", unsafe_allow_html=True)


# ── Load all data once on startup ──────────────────────────
if not st.session_state.get('data_loaded'):
    try:
        from utils.data_loader import (
            load_financial_transactions, load_gst_tax_management,
            load_fraud_detection, load_payroll,
            load_financial_intelligence, load_compliance
        )
        with st.spinner("Loading financial data..."):
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
with st.sidebar:

    # Logo
    st.markdown("""
    <div class="sidebar-logo">
        <div class="sidebar-logo-text">🛡️ AI CFO</div>
        <div class="sidebar-logo-sub">Intelligent Finance Platform</div>
    </div>
    """, unsafe_allow_html=True)

    # Nav label
    st.markdown('<div class="nav-section">Main Menu</div>', unsafe_allow_html=True)

    page = st.radio("", [
        "🏠︎  Home",
        "◔  Dashboard",
        "🗐  GST & Tax",
        "⚠  Fraud Detection",
        "🗠  Cash Forecast",
        "☰  Compliance",
        "֎  AI Assistant",
    ], label_visibility="collapsed")

    st.markdown("---")

    # Data status pills
    if st.session_state.get('data_loaded'):
        txn = st.session_state['financial_transactions']
        gst = st.session_state['gst_data']
        fra = st.session_state['fraud_data']

        st.markdown('<div class="nav-section">Data Status</div>',
                    unsafe_allow_html=True)

        st.markdown(f"""
        <div class="data-pill">Transactions <span>{len(txn)}</span></div>
        <div class="data-pill">GST Records  <span>{len(gst)}</span></div>
        <div class="data-pill">Fraud Alerts <span>{len(fra)}</span></div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="padding:0 16px; font-size:11px; color:#A0AEC0; line-height:1.6;">
        🔥 Fireblaze Tech League 2025<br>
        AI-Powered Finance Platform
    </div>
    """, unsafe_allow_html=True)


# ── Page Routing ───────────────────────────────────────────
page_key = page.strip()

if "Home" in page_key:

    # Top bar
    st.markdown("""
    <div class="top-bar">
        <div class="top-bar-title">Welcome to AI CFO </div>
        <div class="top-bar-badge">● Live Data</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">AI CFO Platform</div>
        <div class="hero-sub">
            Unified Finance, Compliance, Forecasting & AI-Powered Decision Intelligence.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1,col2,col3,col4 = st.columns(4)
    with col1:
        st.metric("Revenue", "₹24.8L", "+12.4%")
    with col2:
        st.metric("Expenses", "₹11.3L", "-3.2%")
    with col3:
        st.metric("Profit Margin", "54%", "+6.1%")
    with col4:
        st.metric("Compliance Score", "98%", "+2%")

    st.markdown("""
    <div style="background:linear-gradient(135deg,#1A7F4B,#22C55E);
    padding:25px;border-radius:14px;color:white;margin:20px 0;">
    <h3>🤖 AI CFO Insight</h3>
    • Revenue growth is accelerating.<br>
    • Cash reserves are healthy.<br>
    • GST compliance risk is low.<br>
    • No critical fraud anomalies detected.<br><br>
    <b>Recommended Action:</b> Review vendor payments above ₹50,000 this week.
    </div>
    """, unsafe_allow_html=True)

    # Feature cards
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="kpi-card" style="border-left:4px solid #1A7F4B;">
            <span class="kpi-icon">📊</span>
            <div class="section-title">Dashboard</div>
            <div class="kpi-sub">Revenue, expenses & profit insights from your financial data</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="kpi-card" style="border-left:4px solid #2B6CB0;">
            <span class="kpi-icon">📋</span>
            <div class="section-title">Compliance</div>
            <div class="kpi-sub">Regulatory deadline tracker with penalty risk alerts</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="kpi-card" style="border-left:4px solid #B45309;">
            <span class="kpi-icon">🧾</span>
            <div class="section-title">GST & Tax</div>
            <div class="kpi-sub">Compliance score, filing status & penalty management</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="kpi-card" style="border-left:4px solid #6B46C1;">
            <span class="kpi-icon">📈</span>
            <div class="section-title">Cash Forecast</div>
            <div class="kpi-sub">24-month revenue prediction using Prophet ML model</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="kpi-card" style="border-left:4px solid #C53030;">
            <span class="kpi-icon">🚨</span>
            <div class="section-title">Fraud Detection</div>
            <div class="kpi-sub">ML-powered anomaly detection on all transactions</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="kpi-card" style="border-left:4px solid #1A7F4B;">
            <span class="kpi-icon">🤖</span>
            <div class="section-title">AI Assistant</div>
            <div class="kpi-sub">Ask anything about your finances in plain English</div>
        </div>
        """, unsafe_allow_html=True)


    st.markdown("### Quick Actions")
    q1,q2,q3,q4 = st.columns(4)
    with q1:
        st.button("📊 Open Dashboard")
    with q2:
        st.button("🧾 GST Review")
    with q3:
        st.button("🚨 Fraud Scan")
    with q4:
        st.button("🤖 Ask AI")

    st.markdown("### Recent Activity")
    st.markdown("""
    <div class="section-card">
    ✅ GST Return Filed Successfully<br><br>
    📈 Revenue Forecast Updated<br><br>
    🚨 2 High-Risk Transactions Flagged<br><br>
    🤖 AI Assistant Generated Monthly Report
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <p style="color:#8492A6; font-size:13px;">
    👈 Use the sidebar to navigate between features.
    </p>
    """, unsafe_allow_html=True)

elif "Dashboard" in page_key:
    from modules.dashboard import show
    show()

elif "GST" in page_key:
    from modules.gst_tracker import show
    show()

elif "Fraud" in page_key:
    from modules.fraud_detection import show
    show()

elif "Forecast" in page_key:
    from modules.cash_forecast import show
    show()

elif "Compliance" in page_key:
    from modules.compliance import show
    show()

elif "Assistant" in page_key:
    from modules.ai_assistant import show
    show()