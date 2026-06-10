"""
modules/finance.py
==================
[NEW] Finance module — tab wrapper for Cash Forecast, Fraud Detection,
and Payroll Management.

Imported by app.py when the user selects "Finance" from the sidebar.
All three sub-tabs delegate to their own show() functions; payroll data
is rendered here so it no longer clutters the Dashboard.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.theme import (
    section_header, kpi_card, style_plotly_fig, alert_box,
    PRIMARY, PRIMARY_LIGHT, PRIMARY_DARK,
    SUCCESS, SUCCESS_BG,
    WARNING, WARNING_BG,
    DANGER,  DANGER_BG,
    WHITE, BORDER, SURFACE,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    CHART_PALETTE, FONT,
)


# ─────────────────────────────────────────────────────────────
# PAYROLL CHARTS  (moved here from Dashboard)
# ─────────────────────────────────────────────────────────────

def _payroll_dept_bar(payroll: pd.DataFrame) -> go.Figure:
    dept = payroll.groupby("Department")["Net_Salary"].sum().sort_values()
    labels = [f"₹{v/1e6:.1f}M" for v in dept.values]
    fig = go.Figure(go.Bar(
        x=dept.values, y=dept.index, orientation="h",
        text=labels, textposition="outside",
        textfont=dict(size=10, color=TEXT_SECONDARY, family=FONT),
        marker=dict(
            color=dept.values,
            colorscale=[[0, "#BFDBFE"], [0.5, PRIMARY_LIGHT], [1, PRIMARY_DARK]],
            line=dict(width=0),
        ),
        hovertemplate="<b>%{y}</b><br>Net Salary: ₹%{x:,.0f}<extra></extra>",
    ))
    style_plotly_fig(fig, height=320, show_legend=False)
    fig.update_layout(
        margin=dict(l=10, r=90, t=10, b=40),
        xaxis=dict(tickformat=".0s", title="Net Salary (₹)",
                   title_font=dict(size=11, color=TEXT_MUTED)),
        yaxis=dict(tickfont=dict(size=11, color=TEXT_PRIMARY)),
    )
    return fig


def _payroll_monthly_trend(payroll: pd.DataFrame) -> go.Figure:
    monthly = (
        payroll.groupby("Month")["Net_Salary"]
        .sum()
        .reset_index()
        .sort_values("Month")
    )
    monthly["label"] = monthly["Month"].dt.strftime("%b %Y")
    fig = go.Figure(go.Scatter(
        x=monthly["label"], y=monthly["Net_Salary"],
        mode="lines+markers",
        line=dict(color=PRIMARY, width=2.5),
        marker=dict(size=6, color=PRIMARY),
        fill="tozeroy", fillcolor="rgba(37,99,235,0.06)",
        hovertemplate="<b>%{x}</b><br>Net Salary: ₹%{y:,.0f}<extra></extra>",
    ))
    style_plotly_fig(fig, height=260, show_legend=False)
    fig.update_layout(
        margin=dict(l=12, r=12, t=10, b=50),
        xaxis=dict(tickangle=-40, tickfont=dict(size=9)),
        yaxis=dict(tickformat=".0s", tickprefix="₹"),
    )
    return fig


def _payroll_component_donut(payroll: pd.DataFrame) -> go.Figure:
    components = {
        "Basic Salary": payroll["Basic_Salary"].sum(),
        "HRA":          payroll["HRA"].sum(),
        "Allowances":   payroll["Allowances"].sum(),
        "PF Deduction": payroll["PF_Deduction"].sum(),
        "TDS":          payroll["TDS"].sum(),
    }
    labels = list(components.keys())
    values = list(components.values())
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.55,
        marker=dict(
            colors=[PRIMARY, SUCCESS, WARNING, DANGER, "#8B5CF6"],
            line=dict(color=WHITE, width=2),
        ),
        textinfo="percent",
        textfont=dict(size=10, family=FONT),
        textposition="outside",
        hovertemplate="<b>%{label}</b><br>₹%{value:,.0f} (%{percent})<extra></extra>",
    ))
    style_plotly_fig(fig, height=280, show_legend=True)
    fig.update_layout(
        legend=dict(orientation="v", x=1.0, y=0.5,
                    xanchor="left", yanchor="middle",
                    font=dict(size=10)),
        margin=dict(l=10, r=120, t=10, b=10),
    )
    return fig


def _show_payroll():
    """Payroll Management sub-tab."""
    payroll = st.session_state.get("payroll_data")
    if payroll is None:
        alert_box("Payroll data not loaded.", "error")
        return

    # KPIs
    total_gross   = payroll["Gross_Salary"].sum()
    total_net     = payroll["Net_Salary"].sum()
    total_pf      = payroll["PF_Deduction"].sum()
    total_tds     = payroll["TDS"].sum()
    headcount     = payroll["Emp_ID"].nunique()
    avg_net       = total_net / headcount if headcount else 0
    processed_pct = (payroll["Payment_Status"] == "Processed").mean() * 100

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(kpi_card("Total Gross Salary", f"₹{total_gross/1e7:.2f} Cr",
                             "All employees combined", "groups",
                             " ", "neutral", PRIMARY), unsafe_allow_html=True)
    with k2:
        st.markdown(kpi_card("Total Net Salary", f"₹{total_net/1e7:.2f} Cr",
                             "After all deductions", "payments",
                             " ", "neutral", SUCCESS), unsafe_allow_html=True)
    with k3:
        st.markdown(kpi_card("Headcount", str(headcount),
                             f"Avg net ₹{avg_net/1e3:.0f}K/employee", "person",
                             " ", "neutral", "#8B5CF6"), unsafe_allow_html=True)
    with k4:
        st.markdown(kpi_card("Payroll Processed", f"{processed_pct:.0f}%",
                             "Payment status completion", "check_circle",
                             " ", "up" if processed_pct >= 95 else "neutral",
                             SUCCESS if processed_pct >= 95 else WARNING),
                    unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts row 1
    col_dept, col_trend = st.columns([3, 2])
    with col_dept:
        section_header("Net Salary by Department", "Total net pay distributed across teams")
        st.plotly_chart(_payroll_dept_bar(payroll), use_container_width=True)

    with col_trend:
        section_header("Monthly Payroll Trend", "Total net salary disbursed per month")
        st.plotly_chart(_payroll_monthly_trend(payroll), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts row 2
    col_comp, col_pf = st.columns([2, 3])
    with col_comp:
        section_header("Salary Component Breakdown", "Composition of total compensation")
        st.plotly_chart(_payroll_component_donut(payroll), use_container_width=True)

    with col_pf:
        section_header("PF Filing Status", "Employee-wise PF compliance")
        pf_counts = payroll["PF_Filed"].value_counts()
        pf_colors = {"Yes": SUCCESS, "No": DANGER}
        fig_pf = go.Figure(go.Bar(
            x=pf_counts.index,
            y=pf_counts.values,
            marker=dict(
                color=[pf_colors.get(k, TEXT_MUTED) for k in pf_counts.index],
                line=dict(color=WHITE, width=1),
            ),
            hovertemplate="<b>%{x}</b><br>%{y} employees<extra></extra>",
        ))
        style_plotly_fig(fig_pf, height=260, show_legend=False)
        fig_pf.update_layout(margin=dict(l=8, r=8, t=8, b=8))
        st.plotly_chart(fig_pf, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Payroll detail table
    with st.expander("View Full Payroll Register"):
        display_cols = [
            "Emp_ID", "Name", "Department", "Designation",
            "Gross_Salary", "PF_Deduction", "TDS", "Net_Salary",
            "Month", "Payment_Status", "PF_Filed",
        ]
        disp = payroll[display_cols].copy()
        for col in ["Gross_Salary", "PF_Deduction", "TDS", "Net_Salary"]:
            disp[col] = disp[col].apply(lambda x: f"₹{x:,.0f}")
        disp["Month"] = pd.to_datetime(disp["Month"], errors="coerce").dt.strftime("%b %Y")
        st.dataframe(disp, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────
# MAIN SHOW FUNCTION
# ─────────────────────────────────────────────────────────────

def show():
    # Page header
    st.markdown(f"""
    <div style="background:{WHITE}; border-bottom:1px solid {BORDER};
                padding:14px 24px; display:flex; align-items:center;
                justify-content:space-between; margin:-1rem -2rem 1.5rem -2rem;">
        <div style="font-size:17px; font-weight:700; color:{TEXT_PRIMARY}; font-family:{FONT};">
            <span class="material-icons" style="color:{PRIMARY};vertical-align:middle;
                  margin-right:6px;font-size:20px;">account_balance_wallet</span>
            Finance
        </div>
        <div style="display:flex;align-items:center;gap:8px;">
            <span style="width:8px;height:8px;border-radius:50%;background:{SUCCESS};
                         display:inline-block;"></span>
            <span style="font-size:12px;font-weight:600;color:{SUCCESS};
                         font-family:{FONT};">Live Data</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Sub-tab strip
    tab1, tab2, tab3 = st.tabs([
        "Cash Flow Forecast",
        "Fraud Anomaly Detection",
        "Payroll Management",
    ])

    with tab1:
        from modules.cash_forecast import show as show_forecast
        show_forecast()

    with tab2:
        from modules.fraud_detection import show as show_fraud
        show_fraud()

    with tab3:
        _show_payroll()