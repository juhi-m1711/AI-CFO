import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.theme import (
    inject_theme,
    section_header,
    kpi_card,
    style_plotly_fig,
    alert_box
)


# ─────────────────────────────────────────
# MAIN PAGE
# ─────────────────────────────────────────
def show():

    inject_theme()

    fin = st.session_state.get(
        "financial_intelligence"
    )

    if fin is None:

        alert_box(
            "Financial intelligence data not loaded.",
            "warning"
        )
        return

    df = fin.copy()

    # -----------------------------------
    # CLEANING
    # -----------------------------------
    for col in [
        "Profit_Margin",
        "YoY_Growth",
        "Forecast_Accuracy"
    ]:

        if col in df.columns:

            df[col] = pd.to_numeric(
                df[col]
                .astype(str)
                .str.replace("%", "")
                .str.strip(),
                errors="coerce"
            )

    df["Period_dt"] = pd.to_datetime(
        df["Period"],
        format="%b-%Y",
        errors="coerce"
    )

    df["Month"] = (
        df["Period_dt"]
        .dt.strftime("%b %Y")
    )

    # -----------------------------------
    # HERO
    # -----------------------------------
    st.markdown(
        """
        <div style="
        background:
        linear-gradient(
        135deg,
        #2563EB,
        #1D4ED8);

        color:white;
        padding:32px;
        border-radius:18px;
        margin-bottom:24px;">

        <h1 style="
        color:white;
        margin:0;
        font-size:30px;
        font-weight:800;">

        Analytics Center

        </h1>

        <p style="
        margin-top:10px;
        opacity:.92;
        font-size:14px;">

        Explore trends, profitability and
        operational performance.

        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    # -----------------------------------
    # KPI VALUES
    # -----------------------------------
    total_rev = df["Revenue"].sum()

    total_profit = df["Net_Profit"].sum()

    avg_margin = df["Profit_Margin"].mean()

    avg_growth = df["YoY_Growth"].mean()

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        kpi_card(
            "Total Revenue",
            f"₹{total_rev/1e6:.2f}M",
            "Across all periods",
            "payments"
        )

    with c2:

        kpi_card(
            "Net Profit",
            f"₹{total_profit/1e6:.2f}M",
            "Total profitability",
            "trending_up"
        )

    with c3:

        kpi_card(
            "Average Margin",
            f"{avg_margin:.1f}%",
            "Profitability ratio",
            "percent"
        )

    with c4:

        kpi_card(
            "YoY Growth",
            f"{avg_growth:.1f}%",
            "Average growth rate",
            "analytics"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------
    # REVENUE AND PROFIT TRENDS
    # ------------------------------------------------
    ch1, ch2 = st.columns(2)

    # -----------------------------------
    # REVENUE TREND
    # -----------------------------------
    with ch1:

        section_header(
            "Revenue Trend",
            "Monthly revenue performance"
        )

        fig_rev = go.Figure()

        fig_rev.add_trace(
            go.Scatter(
                x=df["Month"],
                y=df["Revenue"],
                mode="lines+markers",
                line=dict(
                    color="#2563EB",
                    width=3
                ),
                fill="tozeroy",
                fillcolor="rgba(37,99,235,.08)",
                name="Revenue"
            )
        )

        fig_rev = style_plotly_fig(
            fig_rev,
            320
        )

        st.plotly_chart(
            fig_rev,
            use_container_width=True
        )

    # -----------------------------------
    # NET PROFIT TREND
    # -----------------------------------
    with ch2:

        section_header(
            "Net Profit Trend",
            "Monthly profit evolution"
        )

        fig_profit = go.Figure()

        fig_profit.add_trace(
            go.Scatter(
                x=df["Month"],
                y=df["Net_Profit"],
                mode="lines+markers",
                line=dict(
                    color="#10B981",
                    width=3
                ),
                fill="tozeroy",
                fillcolor="rgba(16,185,129,.08)",
                name="Net Profit"
            )
        )

        fig_profit = style_plotly_fig(
            fig_profit,
            320
        )

        st.plotly_chart(
            fig_profit,
            use_container_width=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------
    # CASH FLOW + MARGIN TRENDS
    # ------------------------------------------------
    ch3, ch4 = st.columns(2)

    # -----------------------------------
    # CASH FLOW
    # -----------------------------------
    with ch3:

        section_header(
            "Cash Flow Trend",
            "Monthly cash movement"
        )

        fig_cf = go.Figure()

        fig_cf.add_trace(
            go.Bar(
                x=df["Month"],
                y=df["Cash_Flow"],
                marker_color="#60A5FA",
                name="Cash Flow"
            )
        )

        fig_cf = style_plotly_fig(
            fig_cf,
            320
        )

        st.plotly_chart(
            fig_cf,
            use_container_width=True
        )

    # -----------------------------------
    # PROFIT MARGIN
    # -----------------------------------
    with ch4:

        section_header(
            "Profit Margin Trend",
            "Margin consistency across periods"
        )

        fig_margin = go.Figure()

        fig_margin.add_trace(
            go.Scatter(
                x=df["Month"],
                y=df["Profit_Margin"],
                mode="lines+markers",
                line=dict(
                    color="#F59E0B",
                    width=3
                ),
                name="Margin"
            )
        )

        fig_margin = style_plotly_fig(
            fig_margin,
            320
        )

        fig_margin.update_layout(
            yaxis=dict(
                ticksuffix="%"
            )
        )

        st.plotly_chart(
            fig_margin,
            use_container_width=True
        )

    st.markdown("<br>", unsafe_allow_html=True)


    # ------------------------------------------------
    # REVENUE VS EXPENSES
    # ------------------------------------------------
    section_header(
        "Revenue vs Expenses",
        "Income compared with operating costs"
    )

    expenses = (
        df["Operating_Expenses"]
        + df["COGS"]
    )

    fig_rexp = go.Figure()

    fig_rexp.add_trace(
        go.Bar(
            x=df["Month"],
            y=df["Revenue"],
            name="Revenue",
            marker_color="#2563EB"
        )
    )

    fig_rexp.add_trace(
        go.Bar(
            x=df["Month"],
            y=expenses,
            name="Expenses",
            marker_color="#EF4444"
        )
    )

    fig_rexp.update_layout(
        barmode="group"
    )

    fig_rexp = style_plotly_fig(
        fig_rexp,
        350
    )

    st.plotly_chart(
        fig_rexp,
        use_container_width=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------
    # EBITDA + BURN RATE
    # ------------------------------------------------
    c1, c2 = st.columns(2)

    # -----------------------------------
    # EBITDA
    # -----------------------------------
    with c1:

        section_header(
            "EBITDA Trend",
            "Operating profitability over time"
        )

        fig_ebitda = go.Figure()

        fig_ebitda.add_trace(
            go.Scatter(
                x=df["Month"],
                y=df["EBITDA"],
                mode="lines+markers",
                line=dict(
                    color="#10B981",
                    width=3
                ),
                fill="tozeroy",
                fillcolor="rgba(16,185,129,.08)"
            )
        )

        fig_ebitda = style_plotly_fig(
            fig_ebitda,
            320
        )

        st.plotly_chart(
            fig_ebitda,
            use_container_width=True
        )

    # -----------------------------------
    # BURN RATE
    # -----------------------------------
    with c2:

        section_header(
            "Burn Rate Analysis",
            "Monthly operating cash consumption"
        )

        fig_burn = go.Figure()

        fig_burn.add_trace(
            go.Bar(
                x=df["Month"],
                y=df["Burn_Rate"],
                marker_color="#F59E0B"
            )
        )

        fig_burn = style_plotly_fig(
            fig_burn,
            320
        )

        st.plotly_chart(
            fig_burn,
            use_container_width=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------
    # AI ANALYTICS INSIGHTS
    # ------------------------------------------------
    section_header(
        "AI Analytics Insights",
        "Automated business performance observations"
    )

    best_month = (
        df.loc[
            df["Revenue"].idxmax(),
            "Month"
        ]
    )

    worst_month = (
        df.loc[
            df["Revenue"].idxmin(),
            "Month"
        ]
    )

    highest_margin = (
        df["Profit_Margin"]
        .max()
    )

    avg_burn = (
        df["Burn_Rate"]
        .mean()
    )

    i1, i2, i3 = st.columns(3)

    with i1:

        kpi_card(
            "Best Revenue Month",
            best_month,
            "Highest revenue recorded",
            "trending_up"
        )

    with i2:

        kpi_card(
            "Weakest Revenue Month",
            worst_month,
            "Lowest revenue recorded",
            "trending_down"
        )

    with i3:

        kpi_card(
            "Average Burn Rate",
            f"₹{avg_burn/1e3:.0f}K",
            f"Peak margin {highest_margin:.1f}%",
            "local_fire_department"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------
    # HEALTH ALERT
    # ------------------------------------------------
    if avg_margin >= 20:

        alert_box(
            "Profitability remains strong across periods.",
            "success"
        )

    elif avg_margin >= 10:

        alert_box(
            "Margins are moderate. Monitor expenses closely.",
            "warning"
        )

    else:

        alert_box(
            "Profit margins are low and require attention.",
            "error"
        )

    # ------------------------------------------------
    # SESSION SUMMARY
    # ------------------------------------------------
    st.session_state["analytics_summary"] = (
        f"Total revenue ₹{total_rev/1e6:.2f}M, "
        f"net profit ₹{total_profit/1e6:.2f}M, "
        f"average margin {avg_margin:.1f}%, "
        f"best month {best_month}, "
        f"worst month {worst_month}."
    )
