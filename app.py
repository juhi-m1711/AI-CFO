import streamlit as st
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Page config ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI-CFO Platform",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject centralized theme ─────────────────────────────────
from utils.theme import inject_theme, kpi_card, section_header, card, alert_box

inject_theme()

# ── Load all data once ───────────────────────────────────────
if not st.session_state.get("data_loaded"):
    try:
        from utils.data_loader import (
            load_financial_transactions, load_gst_tax_management, load_payroll,
            load_financial_intelligence, load_compliance,
        )
        with st.spinner("Loading financial data..."):
            st.session_state["financial_transactions"] = load_financial_transactions()
            st.session_state["gst_data"]               = load_gst_tax_management()
            st.session_state["payroll_data"]           = load_payroll()
            st.session_state["financial_intelligence"] = load_financial_intelligence()
            st.session_state["compliance_data"]        = load_compliance()
            st.session_state["data_loaded"]            = True
    except Exception as e:
        alert_box(f"Missing data file: {e} — Please check the files inside the data/ folder.", "error")
        st.stop()

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:

    # Logo & Branding
    st.markdown('<div class="sidebar-logo">', unsafe_allow_html=True)
    st.image("assets/logo.png", width=52)
    st.markdown("""
    <div class="sidebar-logo-text">AI-CFO</div>
    <div class="sidebar-logo-sub">Platform for Finance, Compliance &amp; Automation</div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="nav-section">Main Menu</div>', unsafe_allow_html=True)

    page = st.radio("", [
        "Home",
        "Dashboard",
        "Finance",
        "Compliance",
        "Analytics",
        "Reports",
        "AI Assistant",
        "Settings",
    ], label_visibility="collapsed")

    # Icon overlay — Material Icons injected next to each radio label via CSS
    st.markdown("""
    <style>
    /* Map each nav label to a Material Icon using nth-child selectors */
    [data-testid="stSidebar"] .stRadio > div > label:nth-child(1)  p::before { content: "home ";           font-family: 'Material Icons'; color: #2563EB; margin-right: 8px; font-size: 16px; vertical-align: middle; }
    [data-testid="stSidebar"] .stRadio > div > label:nth-child(2)  p::before { content: "dashboard ";      font-family: 'Material Icons'; color: #2563EB; margin-right: 8px; font-size: 16px; vertical-align: middle; }
    [data-testid="stSidebar"] .stRadio > div > label:nth-child(3)  p::before { content: "account_balance_wallet "; font-family: 'Material Icons'; color: #2563EB; margin-right: 8px; font-size: 16px; vertical-align: middle; }
    [data-testid="stSidebar"] .stRadio > div > label:nth-child(4)  p::before { content: "gavel ";           font-family: 'Material Icons'; color: #2563EB; margin-right: 8px; font-size: 16px; vertical-align: middle; }
    [data-testid="stSidebar"] .stRadio > div > label:nth-child(5)  p::before { content: "bar_chart ";       font-family: 'Material Icons'; color: #2563EB; margin-right: 8px; font-size: 16px; vertical-align: middle; }
    [data-testid="stSidebar"] .stRadio > div > label:nth-child(6)  p::before { content: "description ";     font-family: 'Material Icons'; color: #2563EB; margin-right: 8px; font-size: 16px; vertical-align: middle; }
    [data-testid="stSidebar"] .stRadio > div > label:nth-child(7)  p::before { content: "smart_toy ";       font-family: 'Material Icons'; color: #2563EB; margin-right: 8px; font-size: 16px; vertical-align: middle; }
    [data-testid="stSidebar"] .stRadio > div > label:nth-child(8)  p::before { content: "settings ";        font-family: 'Material Icons'; color: #2563EB; margin-right: 8px; font-size: 16px; vertical-align: middle; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Data status pills
    if st.session_state.get("data_loaded"):
        txn = st.session_state["financial_transactions"]
        gst = st.session_state["gst_data"]
        st.markdown('<div class="nav-section">Data Status</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="data-pill">Transactions <span>{len(txn)}</span></div>
        <div class="data-pill">GST Records  <span>{len(gst)}</span></div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"""
    <div style="padding:0 16px; font-size:11px; color:#9CA3AF; line-height:1.8;">
        <span class="material-icons" style="font-size:12px;color:#2563EB;vertical-align:middle;">circle</span>
        Fireblaze Tech League 2025<br>
        AI-Powered Finance Platform
    </div>
    """, unsafe_allow_html=True)


# ── Page Routing ─────────────────────────────────────────────

# ── HOME ──────────────────────────────────────────────────────
if page == "Home":

    # Top bar
    st.markdown("""
    <div style="background:#FFFFFF; border-bottom:1px solid #E5E7EB;
                padding:14px 24px; display:flex; align-items:center;
                justify-content:space-between; margin:-1rem -2rem 1.5rem -2rem;">
        <div style="font-size:17px; font-weight:700; color:#111827;
                    font-family:'Manrope',sans-serif;">
            <span class="material-icons" style="color:#2563EB;vertical-align:middle;margin-right:6px;font-size:20px;">home</span>
            Welcome to AI-CFO
        </div>
        <div style="display:flex; align-items:center; gap:8px;">
            <span style="width:8px;height:8px;border-radius:50%;background:#10B981;display:inline-block;"></span>
            <span style="font-size:12px;font-weight:600;color:#10B981;font-family:'Manrope',sans-serif;">Live Data</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Hero Section
    st.markdown("""
    <div style="background:linear-gradient(135deg,#2563EB,#1D4ED8);
                border-radius:18px; padding:36px 40px; color:white;
                margin-bottom:24px; position:relative; overflow:hidden;">
        <div style="position:absolute;right:40px;top:50%;transform:translateY(-50%);
                    font-size:100px;opacity:0.12;font-family:'Material Icons';">
            account_balance
        </div>
        <div style="font-size:30px;font-weight:800;font-family:'Manrope',sans-serif;
                    letter-spacing:-0.5px;">AI-CFO Platform</div>
        <div style="font-size:14px;opacity:0.9;margin-top:8px;
                    font-family:'Manrope',sans-serif;">
            Finance &nbsp;•&nbsp; Compliance &nbsp;•&nbsp; Automation
        </div>
        <div style="font-size:13px;opacity:0.8;margin-top:12px;
                    font-family:'Manrope',sans-serif;max-width:560px;line-height:1.6;">
            Unified intelligence for financial decisions — real-time dashboards,
            GST compliance, ML-powered fraud detection, cash flow forecasting,
            and a Gemini-powered AI assistant, all in one platform.
        </div>
        <div style="display:flex;gap:10px;margin-top:20px;flex-wrap:wrap;">
            <span style="background:rgba(255,255,255,0.2);border:1px solid rgba(255,255,255,0.35);
                         border-radius:20px;padding:5px 14px;font-size:12px;font-weight:600;
                         font-family:'Manrope',sans-serif;">
                <span style="font-family:'Material Icons';font-size:13px;vertical-align:middle;margin-right:4px;">verified</span>
                Fireblaze Tech League 2025
            </span>
            <span style="background:rgba(255,255,255,0.2);border:1px solid rgba(255,255,255,0.35);
                         border-radius:20px;padding:5px 14px;font-size:12px;font-weight:600;
                         font-family:'Manrope',sans-serif;">
                <span style="font-family:'Material Icons';font-size:13px;vertical-align:middle;margin-right:4px;">psychology</span>
                Powered by Gemini AI
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # KPI Row
    fin  = st.session_state.get("financial_intelligence")
    txn  = st.session_state.get("financial_transactions")
    gst  = st.session_state.get("gst_data")
    comp = st.session_state.get("compliance_data")

    if fin is not None:
        rev    = fin["Revenue"].sum()
        exp    = fin["Operating_Expenses"].sum() + fin["COGS"].sum()
        profit = fin["Net_Profit"].sum()
        margin = fin["Profit_Margin"].mean()

        k1, k2, k3, k4 = st.columns(4)
        cards = [
            (k1, "Revenue",        f"₹{rev/1e7:.2f} Cr",    "Total across all periods", "payments",       "+12.4%", "up",   "#2563EB"),
            (k2, "Expenses",       f"₹{exp/1e7:.2f} Cr",    "COGS + Operating",         "receipt_long",   "+5.3%",  "down", "#F59E0B"),
            (k3, "Net Profit",     f"₹{profit/1e7:.2f} Cr", f"Avg margin {margin:.1f}%","trending_up",    "+18.7%", "up",   "#10B981"),
            (k4, "Compliance",     "98%",                    "Score across all filings", "shield",         "+2%",    "up",   "#8B5CF6"),
        ]
        for col, title, value, sub, icon, delta, direction, color in cards:
            with col:
                st.markdown(
                    kpi_card(title, value, sub, icon, delta, direction, color),
                    unsafe_allow_html=True,
                )

    st.markdown("<br>", unsafe_allow_html=True)

    # AI Insight Banner
    if fin is not None and txn is not None and gst is not None:
        fraudc     = st.session_state.get("fraud_data")
        fraud_line = f"{int(fraudc['is_fraud'].sum())} high-risk alerts detected — review flagged transactions." if fraudc is not None else "No fraud data loaded."
        gst_pen    = gst["Penalty"].sum()
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#1D4ED8,#2563EB);
                    padding:22px 28px; border-radius:14px; color:white; margin-bottom:24px;">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
                <span class="material-icons" style="color:white;font-size:22px;">smart_toy</span>
                <span style="font-size:14px;font-weight:700;font-family:'Manrope',sans-serif;">AI-CFO Insight</span>
            </div>
            <div style="font-size:13px;opacity:0.92;line-height:1.8;font-family:'Manrope',sans-serif;">
                Revenue growth is accelerating — strong margin performance this period.<br>
                GST penalties total ₹{gst_pen:,.0f} — enable automated reminders to eliminate late fees.<br>
                {fraud_line}<br>
                Cash reserves are healthy. No critical anomalies in compliance status.
            </div>
            <div style="margin-top:14px;font-size:12px;font-weight:700;
                        font-family:'Manrope',sans-serif;opacity:0.9;">
                Recommended Action: Review vendor payments above ₹50,000 this week.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Feature Cards
    section_header("Platform Features", "Everything you need to run finance operations intelligently")

    features = [
        ("dashboard",               "#2563EB", "Dashboard",         "Revenue, expenses, profit and payroll insights from live financial data."),
        ("account_balance_wallet",  "#10B981", "Finance",           "Cash flow forecasting with Prophet ML and anomaly detection via Isolation Forest."),
        ("gavel",                   "#F59E0B", "Compliance",        "Regulatory deadline tracker with penalty risk alerts and GST filing status."),
        ("bar_chart",               "#8B5CF6", "Analytics",         "KPI ratios, financial health scores, interactive revenue and expense comparisons."),
        ("description",             "#06B6D4", "Reports",           "Automated P&L, Tax Ledger, and Payroll Summary reports — downloadable as CSV."),
        ("smart_toy",               "#EF4444", "AI Assistant",      "Ask anything about your finances in plain English — powered by Gemini 2.5 Flash."),
    ]

    c1, c2, c3 = st.columns(3)
    cols = [c1, c2, c3, c1, c2, c3]

    for (col, (icon, color, title, desc)) in zip(cols, features):
        with col:
            st.markdown(f"""
            <div style="background:#FFFFFF; border:1px solid #E5E7EB;
                        border-left:4px solid {color};
                        border-radius:12px; padding:20px;
                        margin-bottom:14px;
                        box-shadow:0 1px 4px rgba(0,0,0,0.04);">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
                    <span class="material-icons" style="color:{color};font-size:22px;">{icon}</span>
                    <span style="font-size:14px;font-weight:700;color:#111827;
                                 font-family:'Manrope',sans-serif;">{title}</span>
                </div>
                <div style="font-size:12px;color:#6B7280;
                            font-family:'Manrope',sans-serif;line-height:1.6;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick Actions
    section_header("Quick Actions")
    q1, q2, q3, q4 = st.columns(4)
    with q1:
        if st.button("Open Dashboard", use_container_width=True):
            st.session_state["_nav"] = "Dashboard"
            st.rerun()
    with q2:
        if st.button("Finance & Forecasts", use_container_width=True):
            st.session_state["_nav"] = "Finance"
            st.rerun()
    with q3:
        if st.button("Compliance Review", use_container_width=True):
            st.session_state["_nav"] = "Compliance"
            st.rerun()
    with q4:
        if st.button("Ask AI Assistant", use_container_width=True):
            st.session_state["_nav"] = "AI Assistant"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)


# ── DASHBOARD ─────────────────────────────────────────────────
elif page == "Dashboard":
    from modules.dashboard import show
    show()

# ── FINANCE ───────────────────────────────────────────────────
elif page == "Finance":
    from modules.finance import show
    show()

# ── COMPLIANCE ────────────────────────────────────────────────
elif page == "Compliance":
    from modules.compliance_page import show
    show()

# ── ANALYTICS ─────────────────────────────────────────────────
elif page == "Analytics":
    from modules.analytics import show
    show()

# ── REPORTS ───────────────────────────────────────────────────
elif page == "Reports":
    from modules.reports import show
    show()

# ── AI ASSISTANT ──────────────────────────────────────────────
elif page == "AI Assistant":
    from modules.ai_assistant import show
    show()

# ── SETTINGS ──────────────────────────────────────────────────
elif page == "Settings":
    from modules.settings import show
    show()