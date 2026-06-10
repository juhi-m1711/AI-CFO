"""
modules/dashboard.py
====================
AI-CFO Executive Dashboard — Streamlit module.
Redesigned with blue-and-white SaaS theme via utils/theme.py.

Bug fixed  : Task 1 — third insight card (Fraud Detection) no longer has
             empty lines inside the f-string that caused the markdown compiler
             to render raw HTML/Python code as visible text.
Theme      : All KPI cards, charts, and section headers use theme.py tokens.
No emojis  : All emojis replaced with Material Icons.
Charts     : style_plotly_fig() applied to every Plotly figure.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.theme import (
    inject_theme, kpi_card, section_header, card,
    style_plotly_fig, alert_box,
    PRIMARY, PRIMARY_LIGHT, PRIMARY_DARK,
    SUCCESS, SUCCESS_BG,
    WARNING, WARNING_BG,
    DANGER,  DANGER_BG,
    WHITE, BORDER, SURFACE,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    CHART_PALETTE, FONT,
)


# ─────────────────────────────────────────────────────────────
# CHART BUILDERS
# ─────────────────────────────────────────────────────────────

def _chart_revenue(fin: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=fin["month_label"], y=fin["Revenue"],
        name="Revenue", mode="lines+markers",
        line=dict(color=PRIMARY, width=2.5),
        marker=dict(size=5, color=PRIMARY),
        fill="tozeroy", fillcolor="rgba(37,99,235,0.06)",
        hovertemplate="<b>%{x}</b><br>Revenue: ₹%{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=fin["month_label"], y=fin["Net_Profit"],
        name="Net Profit", mode="lines+markers",
        line=dict(color=SUCCESS, width=2, dash="dot"),
        marker=dict(size=4, color=SUCCESS),
        hovertemplate="<b>%{x}</b><br>Net Profit: ₹%{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=fin["month_label"], y=fin["Operating_Expenses"],
        name="Expenses", mode="lines",
        line=dict(color=WARNING, width=1.8, dash="dash"),
        hovertemplate="<b>%{x}</b><br>Expenses: ₹%{y:,.0f}<extra></extra>",
    ))
    style_plotly_fig(fig, height=320)
    fig.update_layout(
        margin=dict(l=12, r=12, t=10, b=50),
        xaxis=dict(tickangle=-40, tickfont=dict(size=9)),
        yaxis=dict(tickformat=".0s", tickprefix="₹"),
        legend=dict(orientation="h", x=0, y=-0.28),
    )
    return fig


def _chart_expense_donut(txn: pd.DataFrame):
    cats = txn.groupby("Category")["Amount"].sum().sort_values(ascending=False)
    total = cats.sum()
    fig = go.Figure(go.Pie(
        labels=cats.index,
        values=cats.values,
        hole=0.55,
        marker=dict(
            colors=CHART_PALETTE[:len(cats)],
            line=dict(color=WHITE, width=2),
        ),
        textinfo="percent",
        textfont=dict(size=10, color=TEXT_SECONDARY, family=FONT),
        textposition="outside",
        hovertemplate="<b>%{label}</b><br>₹%{value:,.0f} (%{percent})<extra></extra>",
        direction="clockwise",
        rotation=90,
    ))
    style_plotly_fig(fig, height=300, show_legend=True)
    fig.update_layout(
        legend=dict(orientation="v", x=1.0, y=0.5,
                    xanchor="left", yanchor="middle",
                    font=dict(size=10)),
        margin=dict(l=10, r=110, t=10, b=10),
    )
    return fig, total


def _chart_payroll(payroll: pd.DataFrame) -> go.Figure:
    dept = payroll.groupby("Department")["Net_Salary"].sum().sort_values()
    labels = [f"₹{v/1e6:.1f}M" for v in dept.values]
    fig = go.Figure(go.Bar(
        x=dept.values,
        y=dept.index,
        orientation="h",
        text=labels,
        textposition="outside",
        textfont=dict(size=10, color=TEXT_SECONDARY, family=FONT),
        marker=dict(
            color=dept.values,
            colorscale=[[0, "#BFDBFE"], [0.5, PRIMARY_LIGHT], [1, PRIMARY_DARK]],
            line=dict(width=0),
        ),
        hovertemplate="<b>%{y}</b><br>Net Salary: ₹%{x:,.0f}<extra></extra>",
    ))
    style_plotly_fig(fig, height=300, show_legend=False)
    fig.update_layout(
        margin=dict(l=10, r=80, t=10, b=40),
        xaxis=dict(tickformat=".0s", title="Net Salary (₹)",
                   title_font=dict(size=11, color=TEXT_MUTED)),
        yaxis=dict(tickfont=dict(size=11, color=TEXT_PRIMARY)),
    )
    return fig


def _chart_fraud_ml(fraud: pd.DataFrame) -> go.Figure:
    """Bar chart of ML prediction category counts."""
    if "ml_fraud_result" in st.session_state:
        df = st.session_state["ml_fraud_result"]
        counts = df["ml_is_fraud"].value_counts()
        labels = ["Anomaly" if k else "Normal" for k in counts.index]
        colors = [DANGER if k else SUCCESS for k in counts.index]
    else:
        labels = ["No ML data"]
        counts_vals = [1]
        colors = [TEXT_MUTED]
        fig = go.Figure(go.Bar(
            x=labels, y=counts_vals,
            marker=dict(color=colors),
        ))
        style_plotly_fig(fig, height=200, show_legend=False)
        return fig

    fig = go.Figure(go.Bar(
        x=labels,
        y=counts.values,
        marker=dict(color=colors, line=dict(color=WHITE, width=1)),
        hovertemplate="<b>%{x}</b><br>Count: %{y}<extra></extra>",
    ))
    style_plotly_fig(fig, height=200, show_legend=False)
    fig.update_layout(margin=dict(l=8, r=8, t=8, b=8))
    return fig


def _chart_payment_status(txn: pd.DataFrame) -> go.Figure:
    vc = txn["Status"].value_counts()
    color_map = {
        "Paid": SUCCESS, "Pending": WARNING,
        "Overdue": DANGER, "Partially Paid": PRIMARY_LIGHT,
    }
    colors = [color_map.get(k, TEXT_MUTED) for k in vc.index]
    fig = go.Figure(go.Bar(
        x=vc.index, y=vc.values,
        marker=dict(color=colors, line=dict(color=WHITE, width=1)),
        hovertemplate="<b>%{x}</b><br>%{y} transactions<extra></extra>",
    ))
    style_plotly_fig(fig, height=220, show_legend=False)
    fig.update_layout(margin=dict(l=8, r=8, t=8, b=8))
    return fig


# ─────────────────────────────────────────────────────────────
# MAIN SHOW FUNCTION
# ─────────────────────────────────────────────────────────────

def show():
    # ── Pull data from session state ──────────────────────────
    fin        = st.session_state.get("financial_intelligence")
    txn        = st.session_state.get("financial_transactions")
    gst        = st.session_state.get("gst_data")
    payroll    = st.session_state.get("payroll_data")
    compliance = st.session_state.get("compliance_data")

    if fin is None or txn is None:
        alert_box("No data found in session state. Please restart the app.", "error")
        return

    # ── Derived KPIs ──────────────────────────────────────────
    fin = fin.copy()
    for col in ["Profit_Margin", "YoY_Growth", "Forecast_Accuracy"]:
        if col in fin.columns:
            fin[col] = pd.to_numeric(
                fin[col].astype(str).str.replace("%", "").str.strip(),
                errors="coerce",
            )

    rev    = fin["Revenue"].sum()
    exp    = fin["Operating_Expenses"].sum() + fin["COGS"].sum()
    profit = fin["Net_Profit"].sum()
    cash   = fin["Cash_Flow"].iloc[-1]
    margin = fin["Profit_Margin"].mean()

    gstp      = gst["Penalty"].sum() if gst is not None else 0
    gst_pen_c = int((gst["Penalty"] > 0).sum()) if gst is not None else 0

    top_cat = txn.groupby("Category")["Amount"].sum().idxmax()
    top_val = txn.groupby("Category")["Amount"].sum().max()
    top_pct = top_val / txn["Amount"].sum() * 100

    # Fraud from ML session state (set by fraud_detection.py after user runs scan)
    if "ml_fraud_result" in st.session_state:
        ml_result = st.session_state["ml_fraud_result"]
        fraudc    = int(ml_result["ml_is_fraud"].sum())
    else:
        fraudc = 0

    # ── Page header ───────────────────────────────────────────
    st.markdown(f"""
    <div style="background:{WHITE}; border-bottom:1px solid {BORDER};
                padding:14px 24px; display:flex; align-items:center;
                justify-content:space-between; margin:-1rem -2rem 1.5rem -2rem;">
        <div style="font-size:17px; font-weight:700; color:{TEXT_PRIMARY}; font-family:{FONT};">
            <span class="material-icons" style="color:{PRIMARY};vertical-align:middle;
                  margin-right:6px;font-size:20px;">dashboard</span>
            Executive Dashboard
        </div>
        <div style="display:flex;align-items:center;gap:8px;">
            <span style="width:8px;height:8px;border-radius:50%;background:{SUCCESS};
                         display:inline-block;"></span>
            <span style="font-size:12px;font-weight:600;color:{SUCCESS};
                         font-family:{FONT};">Live Data</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── ROW 1: KPI Cards ──────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)

    kpis = [
        (k1, "Total Revenue",   f"₹{rev/1e7:.2f} Cr",    f"Across {len(fin)} months",      "payments",       "+12.4%", "up",      PRIMARY),
        (k2, "Total Expenses",  f"₹{exp/1e7:.2f} Cr",    "COGS + Operating",               "receipt_long",   "+5.3%",  "down",    WARNING),
        (k3, "Net Profit",      f"₹{profit/1e7:.2f} Cr", f"Avg margin {margin:.1f}%",      "trending_up",    "+18.7%", "up",      SUCCESS),
        (k4, "Cash Balance",    f"₹{cash/1e5:.1f} L",    "Latest month cash flow",         "account_balance"," ",       "neutral", "#06B6D4"),
    ]
    for col, title, value, sub, icon, delta, direction, color in kpis:
        with col:
            st.markdown(kpi_card(title, value, sub, icon, delta, direction, color),
                        unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ROW 2: GST Penalty + Fraud Alerts ─────────────────────
    g1, g2 = st.columns(2)

    with g1:
        st.markdown(
            kpi_card("GST Penalty Risk", f"₹{gstp:,.0f}",
                     f"{gst_pen_c} late or missed filings",
                     "warning", "+7.6%", "down", WARNING),
            unsafe_allow_html=True,
        )

    with g2:
        fraud_sub   = f"{fraudc} high-risk alerts detected" if fraudc > 0 else "No anomalies detected"
        fraud_dir   = "down" if fraudc > 0 else "up"
        fraud_delta = f"{fraudc} flagged" if fraudc > 0 else "Clean"
        fraud_color = DANGER if fraudc > 0 else SUCCESS
        st.markdown(
            kpi_card("Fraud Alerts", str(fraudc), fraud_sub,
                     "security", fraud_delta, fraud_dir, fraud_color),
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ROW 3: Revenue Performance Chart ──────────────────────
    section_header("Revenue Performance", "Monthly revenue vs net profit vs operating expenses")
    st.plotly_chart(_chart_revenue(fin), use_container_width=True)

    # ── ROW 4: Payroll + Expense Donut ────────────────────────
    col_pay, col_donut = st.columns([3, 2])

    with col_pay:
        section_header("Payroll Overview", "Net salary distributed by department")
        if payroll is not None:
            st.plotly_chart(_chart_payroll(payroll), use_container_width=True)
        else:
            alert_box("Payroll data not loaded.", "warning")

    with col_donut:
        section_header("Expense Breakdown", "Spend distribution across categories")
        donut_fig, total_exp = _chart_expense_donut(txn)
        st.markdown(f"""
        <div style="font-size:12px;color:{TEXT_MUTED};margin-bottom:6px;font-family:{FONT};">
            Total spend: <strong style="color:{PRIMARY};">₹{total_exp/1e5:.0f} L</strong>
        </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(donut_fig, use_container_width=True)

    # ── ROW 5: AI CFO Insights ────────────────────────────────
    section_header("AI-CFO Insights", "Data-driven recommendations for this period")

    ia, ib, ic = st.columns(3)

    with ia:
        st.markdown(f"""
        <div style="background:{WHITE};border:1px solid {BORDER};border-radius:14px;
                    padding:20px;border-bottom:3px solid {SUCCESS};
                    box-shadow:0 1px 4px rgba(0,0,0,0.04);">
            <div style="width:38px;height:38px;border-radius:50%;background:{SUCCESS_BG};
                        display:flex;align-items:center;justify-content:center;margin-bottom:12px;">
                <span class="material-icons" style="color:{SUCCESS};font-size:20px;">star</span>
            </div>
            <div style="font-size:11px;font-weight:600;color:{TEXT_MUTED};text-transform:uppercase;
                        letter-spacing:0.5px;font-family:{FONT};margin-bottom:6px;">Highest Spend Category</div>
            <div style="font-size:22px;font-weight:800;color:{TEXT_PRIMARY};font-family:{FONT};
                        letter-spacing:-0.5px;margin-bottom:4px;">{top_cat}</div>
            <div style="font-size:13px;font-weight:600;color:{SUCCESS};font-family:{FONT};">₹{top_val/1e5:.1f} L</div>
            <div style="font-size:12px;color:{TEXT_MUTED};font-family:{FONT};margin-top:2px;">{top_pct:.1f}% of total expenses</div>
        </div>
        """, unsafe_allow_html=True)

    with ib:
        st.markdown(f"""
        <div style="background:{WHITE};border:1px solid {BORDER};border-radius:14px;
                    padding:20px;border-bottom:3px solid {WARNING};
                    box-shadow:0 1px 4px rgba(0,0,0,0.04);">
            <div style="width:38px;height:38px;border-radius:50%;background:{WARNING_BG};
                        display:flex;align-items:center;justify-content:center;margin-bottom:12px;">
                <span class="material-icons" style="color:{WARNING};font-size:20px;">receipt</span>
            </div>
            <div style="font-size:11px;font-weight:600;color:{TEXT_MUTED};text-transform:uppercase;
                        letter-spacing:0.5px;font-family:{FONT};margin-bottom:6px;">GST Filings</div>
            <div style="font-size:22px;font-weight:800;color:{TEXT_PRIMARY};font-family:{FONT};
                        letter-spacing:-0.5px;margin-bottom:4px;">{gst_pen_c} filings</div>
            <div style="font-size:12px;color:{TEXT_MUTED};font-family:{FONT};">incurred penalties</div>
            <div style="font-size:13px;font-weight:600;color:{TEXT_PRIMARY};font-family:{FONT};margin-top:4px;">₹{gstp:,.0f} total</div>
        </div>
        """, unsafe_allow_html=True)

    # ── TASK 1 BUG FIX ──
    # The third insight card previously had blank lines inside the f-string
    # which caused the markdown parser to exit HTML mode and render the closing
    # </div> tags and Python variables as raw visible text.
    # Fix: the f-string is now a single unbroken block with no empty lines.
    with ic:
        fraud_ins_val = f"{fraudc} high-risk alerts" if fraudc > 0 else "0 high-risk alerts"
        fraud_ins_sub = "Review flagged transactions." if fraudc > 0 else "No critical fraud activity detected."
        fraud_border  = DANGER if fraudc > 0 else SUCCESS
        fraud_bg      = DANGER_BG if fraudc > 0 else SUCCESS_BG
        fraud_icon_c  = DANGER if fraudc > 0 else SUCCESS
        st.markdown(f'<div style="background:{WHITE};border:1px solid {BORDER};border-radius:14px;padding:20px;border-bottom:3px solid {fraud_border};box-shadow:0 1px 4px rgba(0,0,0,0.04);"><div style="width:38px;height:38px;border-radius:50%;background:{fraud_bg};display:flex;align-items:center;justify-content:center;margin-bottom:12px;"><span class="material-icons" style="color:{fraud_icon_c};font-size:20px;">security</span></div><div style="font-size:11px;font-weight:600;color:{TEXT_MUTED};text-transform:uppercase;letter-spacing:0.5px;font-family:{FONT};margin-bottom:6px;">Fraud Detection</div><div style="font-size:22px;font-weight:800;color:{TEXT_PRIMARY};font-family:{FONT};letter-spacing:-0.5px;margin-bottom:4px;">{fraud_ins_val}</div><div style="font-size:12px;color:{TEXT_MUTED};font-family:{FONT};">{fraud_ins_sub}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ROW 6: Payment Status + ML Fraud Summary ──────────────
    col_pay_status, col_fraud_chart = st.columns([3, 2])

    with col_pay_status:
        section_header("Payment Status Overview", "Transaction breakdown by current status")
        st.plotly_chart(_chart_payment_status(txn), use_container_width=True)

    with col_fraud_chart:
        section_header("Fraud ML Model", "Anomaly vs normal transaction split")
        if "ml_fraud_result" in st.session_state:
            st.plotly_chart(_chart_fraud_ml(
                st.session_state["ml_fraud_result"]),
                use_container_width=True,
            )
        else:
            alert_box(
                "Run the Fraud Detection scan in the Finance module to populate ML results here.",
                "info",
            )

    # ── ROW 7: Expandable detail tables ───────────────────────
    with st.expander("View Fraud Alerts — ML flagged transactions"):
        if "ml_fraud_result" in st.session_state:
            ml = st.session_state["ml_fraud_result"]
            flagged = ml[ml["ml_is_fraud"] == True][[
                "Txn_ID", "Date", "Vendor/Client", "Amount",
                "Category", "ml_risk_score", "Risk_Flag", "Status",
            ]].sort_values("ml_risk_score", ascending=False).copy()
            flagged = flagged.rename(columns={
                "ml_risk_score": "ML Risk %",
                "Risk_Flag": "Risk Level",
            })
            flagged["Amount"] = flagged["Amount"].apply(lambda x: f"₹{x:,.0f}")
            st.dataframe(flagged, use_container_width=True, hide_index=True)
        else:
            alert_box("No ML fraud data yet — run a scan from the Finance module first.", "info")

    with st.expander("View Compliance Status — all obligations"):
        if compliance is not None:
            comp_disp = compliance[[
                "Regulation_Type", "Status", "Priority",
                "Due_Date", "Submitted_Date", "Penalty_Risk",
            ]].sort_values(
                "Priority",
                key=lambda x: x.map(
                    {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
                ).fillna(9),
            ).copy()
            comp_disp["Penalty_Risk"] = comp_disp["Penalty_Risk"].apply(
                lambda x: f"₹{x:,.0f}" if x > 0 else "—"
            )
            st.dataframe(comp_disp, use_container_width=True, hide_index=True)
        else:
            alert_box("Compliance data not loaded.", "warning")

    # Footer
    st.markdown(f"""
    <div style="text-align:right;font-size:11px;color:{TEXT_MUTED};
                font-family:{FONT};margin-top:16px;">
        <span class="material-icons" style="font-size:12px;vertical-align:middle;
              color:{PRIMARY};margin-right:4px;">psychology</span>
        AI-CFO Platform — Fireblaze Tech League 2025
    </div>
    """, unsafe_allow_html=True)