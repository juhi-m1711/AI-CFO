"""
gst_tracker.py  —  GST Tax Management Module
AI-CFO Platform
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime


def show():

    from utils.theme import (
        inject_theme,
        section_header,
        kpi_card,
        style_plotly_fig,
        alert_box
    )

    inject_theme()

    # ------------------------------------------------
    # LOAD DATA
    # ------------------------------------------------
    gst = st.session_state.get("gst_data")

    if gst is None:

        alert_box(
            "GST tax management data not loaded.",
            "warning"
        )
        return

    df = gst.copy()

    # ------------------------------------------------
    # NUMERIC COLUMNS
    # ------------------------------------------------
    for col in [
        "CGST",
        "SGST",
        "IGST",
        "Total_GST",
        "Penalty"
    ]:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        ).fillna(0)

    # ------------------------------------------------
    # COMPLIANCE SCORE
    # ------------------------------------------------
    df["Compliance_Score_num"] = pd.to_numeric(
        df["Compliance_Score"]
        .astype(str)
        .str.replace("%", "")
        .str.strip(),
        errors="coerce"
    ).fillna(0)

    # ------------------------------------------------
    # DATES
    # ------------------------------------------------
    df["Due_Date"] = pd.to_datetime(
        df["Due_Date"],
        dayfirst=True,
        errors="coerce"
    )

    df["Filed_Date"] = pd.to_datetime(
        df["Filed_Date"],
        dayfirst=True,
        errors="coerce"
    )

    df["Period_dt"] = pd.to_datetime(
        df["Filing_Period"],
        format="%b-%Y",
        errors="coerce"
    )

    df["Month_Label"] = (
        df["Period_dt"]
        .dt.strftime("%b %Y")
    )

    df["Days_Late"] = (
        (df["Filed_Date"] - df["Due_Date"])
        .dt.days
        .fillna(0)
        .clip(lower=0)
    )

    # ------------------------------------------------
    # KPI VALUES
    # ------------------------------------------------
    total = len(df)

    filed_ot = (
        df["Status"] == "Filed On Time"
    ).sum()

    late = (
        df["Status"] == "Late Filing"
    ).sum()

    missed = (
        df["Status"] == "Missed"
    ).sum()

    pending = (
        df["Status"] == "Pending"
    ).sum()

    total_gst = (
        df["Total_GST"]
        .sum()
    )

    total_pen = (
        df["Penalty"]
        .sum()
    )

    avg_score = (
        df["Compliance_Score_num"]
        .mean()
    )

    compliance_rate = (
        round(
            filed_ot / total * 100,
            1
        )
        if total
        else 0
    )

    # ------------------------------------------------
    # HERO
    # ------------------------------------------------
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

        GST & Tax Management

        </h1>

        <p style="
        margin-top:10px;
        opacity:.92;
        font-size:14px;">

        Track filings, penalties and
        tax exposure across business units.

        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    # ------------------------------------------------
    # KPI SECTION
    # ------------------------------------------------
    section_header(
        "GST Compliance Overview",
        "Performance indicators and filing statistics"
    )

    k1, k2, k3, k4, k5 = st.columns(5)

    with k1:

        kpi_card(
            "Total Filings",
            str(total),
            f"{filed_ot} filed on time",
            "description"
        )

    with k2:

        kpi_card(
            "Filed On Time",
            str(filed_ot),
            f"{compliance_rate:.1f}% compliance rate",
            "check_circle"
        )

    with k3:

        avg_late_days = (
            df.loc[
                df["Days_Late"] > 0,
                "Days_Late"
            ].mean()
        )

        avg_late_str = (
            f"Avg {avg_late_days:.0f} days late"
            if late > 0
            else "No late filings"
        )

        kpi_card(
            "Late Filings",
            str(late),
            avg_late_str,
            "warning"
        )

    with k4:

        kpi_card(
            "Missed / Pending",
            str(missed + pending),
            f"{missed} missed, {pending} pending",
            "dangerous"
        )

    with k5:

        kpi_card(
            "Total Penalties",
            f"₹{total_pen:,.0f}",
            f"{int((df['Penalty'] > 0).sum())} filings affected",
            "payments"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------
    # COMPLIANCE SCORE + STATUS BREAKDOWN
    # ------------------------------------------------
    col_ring, col_status, col_type = st.columns(
        [1.2, 2, 2]
    )

    # -----------------------------------
    # COMPLIANCE SCORE
    # -----------------------------------
    with col_ring:

        section_header(
            "Average Compliance Score",
            f"Based on {total} GST filings"
        )

        if avg_score >= 75:
            score_color = "#10B981"

        elif avg_score >= 50:
            score_color = "#F59E0B"

        else:
            score_color = "#EF4444"

        fig_ring = go.Figure(
            go.Pie(
                values=[
                    avg_score,
                    100 - avg_score
                ],
                hole=0.72,
                marker=dict(
                    colors=[
                        score_color,
                        "#F3F4F6"
                    ],
                    line=dict(width=0)
                ),
                textinfo="none",
                hoverinfo="skip"
            )
        )

        fig_ring.update_layout(
            showlegend=False,
            annotations=[
                dict(
                    text=f"<b>{avg_score:.0f}%</b>",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(
                        size=28,
                        color="#1F2937"
                    )
                )
            ]
        )

        fig_ring = style_plotly_fig(
            fig_ring,
            height=220
        )

        st.plotly_chart(
            fig_ring,
            use_container_width=True
        )

    # -----------------------------------
    # FILING STATUS BREAKDOWN
    # -----------------------------------
    with col_status:

        section_header(
            "Filing Status Breakdown",
            "Distribution by filing status"
        )

        status_counts = (
            df["Status"]
            .value_counts()
        )

        status_colors = {
            "Filed On Time": "#10B981",
            "Late Filing": "#F59E0B",
            "Missed": "#EF4444",
            "Pending": "#2563EB"
        }

        fig_status = go.Figure()

        fig_status.add_trace(
            go.Bar(
                x=status_counts.index,
                y=status_counts.values,
                marker_color=[
                    status_colors.get(
                        x,
                        "#64748B"
                    )
                    for x in status_counts.index
                ],
                text=status_counts.values,
                textposition="outside"
            )
        )

        fig_status = style_plotly_fig(
            fig_status,
            height=220
        )

        fig_status.update_layout(
            showlegend=False
        )

        st.plotly_chart(
            fig_status,
            use_container_width=True
        )

    # -----------------------------------
    # GST COMPONENT BREAKDOWN
    # -----------------------------------
    with col_type:

        section_header(
            "GST Component Breakdown",
            "CGST, SGST and IGST"
        )

        fig_donut = go.Figure(
            go.Pie(
                labels=[
                    "CGST",
                    "SGST",
                    "IGST"
                ],
                values=[
                    df["CGST"].sum(),
                    df["SGST"].sum(),
                    df["IGST"].sum()
                ],
                hole=0.55,
                marker=dict(
                    colors=[
                        "#2563EB",
                        "#60A5FA",
                        "#10B981"
                    ]
                )
            )
        )

        fig_donut = style_plotly_fig(
            fig_donut,
            height=220
        )

        st.plotly_chart(
            fig_donut,
            use_container_width=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------
    # MONTHLY GST COLLECTION TREND
    # ------------------------------------------------
    section_header(
        "Monthly GST Collection Trend",
        "GST collections and penalties over time"
    )

    monthly = (
        df
        .dropna(subset=["Period_dt"])
        .groupby("Period_dt")
        .agg(
            Total_GST=(
                "Total_GST",
                "sum"
            ),
            Penalty=(
                "Penalty",
                "sum"
            )
        )
        .reset_index()
        .sort_values("Period_dt")
    )

    monthly["Month"] = (
        monthly["Period_dt"]
        .dt.strftime("%b %Y")
    )

    fig_trend = go.Figure()

    fig_trend.add_trace(
        go.Bar(
            x=monthly["Month"],
            y=monthly["Total_GST"],
            name="GST Collection",
            marker_color="#2563EB"
        )
    )

    fig_trend.add_trace(
        go.Scatter(
            x=monthly["Month"],
            y=monthly["Penalty"],
            mode="lines+markers",
            name="Penalties",
            line=dict(
                color="#EF4444",
                width=3,
                dash="dot"
            )
        )
    )

    fig_trend = style_plotly_fig(
        fig_trend,
        height=340
    )

    st.plotly_chart(
        fig_trend,
        use_container_width=True
    )

    st.markdown("<br>", unsafe_allow_html=True)


    # ------------------------------------------------
    # BUSINESS ANALYSIS
    # ------------------------------------------------
    c1, c2 = st.columns(2)

    # -----------------------------------
    # COMPLIANCE SCORE BY BUSINESS
    # -----------------------------------
    with c1:

        section_header(
            "Compliance Score by Business",
            "Historical filing performance"
        )

        biz_score = (
            df.groupby("Business_Name")
            .agg(
                avg_score=(
                    "Compliance_Score_num",
                    "mean"
                ),
                filings=(
                    "GSTIN",
                    "count"
                )
            )
            .reset_index()
            .sort_values(
                "avg_score"
            )
        )

        fig_biz = go.Figure()

        fig_biz.add_trace(
            go.Bar(
                x=biz_score["avg_score"],
                y=biz_score["Business_Name"],
                orientation="h",
                marker_color="#2563EB",
                text=[
                    f"{x:.0f}%"
                    for x in biz_score["avg_score"]
                ],
                textposition="outside"
            )
        )

        fig_biz = style_plotly_fig(
            fig_biz,
            height=340
        )

        fig_biz.update_layout(
            xaxis=dict(
                range=[0, 110]
            )
        )

        st.plotly_chart(
            fig_biz,
            use_container_width=True
        )

    # -----------------------------------
    # TOP STATES BY GST COLLECTION
    # -----------------------------------
    with c2:

        section_header(
            "Top States by GST Collection",
            "Highest GST contribution"
        )

        state_gst = (
            df.groupby("State")
            ["Total_GST"]
            .sum()
            .sort_values(
                ascending=False
            )
            .head(10)
            .reset_index()
        )

        fig_state = go.Figure()

        fig_state.add_trace(
            go.Bar(
                x=state_gst["Total_GST"],
                y=state_gst["State"],
                orientation="h",
                marker_color="#60A5FA"
            )
        )

        fig_state = style_plotly_fig(
            fig_state,
            height=340
        )

        fig_state.update_layout(
            yaxis=dict(
                autorange="reversed"
            )
        )

        st.plotly_chart(
            fig_state,
            use_container_width=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------
    # AI GST INSIGHTS
    # ------------------------------------------------
    section_header(
        "AI GST Insights",
        "Automated observations and tax exposure"
    )

    top_defaulter = (
        df[df["Penalty"] > 0]
        .groupby("Business_Name")
        ["Penalty"]
        .sum()
        .idxmax()
        if (df["Penalty"] > 0).any()
        else "N/A"
    )

    top_penalty = (
        df[df["Penalty"] > 0]
        .groupby("Business_Name")
        ["Penalty"]
        .sum()
        .max()
        if (df["Penalty"] > 0).any()
        else 0
    )

    worst_state = (
        df.groupby("State")
        ["Penalty"]
        .sum()
        .idxmax()
    )

    high_igst_biz = (
        df.groupby("Business_Name")
        ["IGST"]
        .sum()
        .idxmax()
    )

    i1, i2, i3 = st.columns(3)

    with i1:

        kpi_card(
            "Highest Penalty Entity",
            top_defaulter,
            f"₹{top_penalty:,.0f} penalties",
            "warning"
        )

    with i2:

        kpi_card(
            "State with Most Penalties",
            worst_state,
            "Highest cumulative penalties",
            "place"
        )

    with i3:

        kpi_card(
            "Highest IGST Exposure",
            high_igst_biz,
            "Heavy inter-state activity",
            "sync"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------
    # GST REGISTER
    # ------------------------------------------------
    section_header(
        "GST Filing Register",
        "Search and inspect historical filings"
    )

    f1, f2, f3, f4 = st.columns([2, 2, 2, 1])

    with f1:

        biz_options = (
            ["All Businesses"]
            + sorted(
                df["Business_Name"]
                .dropna()
                .unique()
                .tolist()
            )
        )

        sel_biz = st.selectbox(
            "Business",
            biz_options
        )

    with f2:

        state_options = (
            ["All States"]
            + sorted(
                df["State"]
                .dropna()
                .unique()
                .tolist()
            )
        )

        sel_state = st.selectbox(
            "State",
            state_options
        )

    with f3:

        status_options = (
            ["All Statuses"]
            + sorted(
                df["Status"]
                .dropna()
                .unique()
                .tolist()
            )
        )

        sel_status = st.selectbox(
            "Status",
            status_options
        )

    with f4:

        st.markdown("<br>", unsafe_allow_html=True)

        penalty_only = st.checkbox(
            "Penalties"
        )

    filt = df.copy()

    if sel_biz != "All Businesses":
        filt = filt[
            filt["Business_Name"]
            == sel_biz
        ]

    if sel_state != "All States":
        filt = filt[
            filt["State"]
            == sel_state
        ]

    if sel_status != "All Statuses":
        filt = filt[
            filt["Status"]
            == sel_status
        ]

    if penalty_only:
        filt = filt[
            filt["Penalty"] > 0
        ]

    st.dataframe(
        filt,
        use_container_width=True,
        hide_index=True
    )

    # ------------------------------------------------
    # EXPORT
    # ------------------------------------------------
    csv_data = (
        filt.to_csv(
            index=False
        )
        .encode("utf-8")
    )

    st.download_button(
        "Export Filtered GST Data",
        data=csv_data,
        file_name="gst_filtered_export.csv",
        mime="text/csv"
    )

