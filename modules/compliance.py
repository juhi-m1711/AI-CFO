"""
compliance.py  —  AI-CFO Platform
Compliance Tracking module (Streamlit)
Fixed version — reads from session_state, correct column names
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, timedelta



# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
PRIORITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
STATUS_COLORS  = {
    "Compliant":     "#059669",
    "Pending":       "#2563eb",
    "At Risk":       "#d97706",
    "Non-Compliant": "#dc2626",
}

def _plot_cfg(height=300):
    return dict(
        height=height,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            family="Manrope, sans-serif",
            color="#374151",
            size=11
        )
    )

def _days_until(due_date):
    today = pd.Timestamp.today().normalize()
    if pd.isna(due_date):
        return None
    return (due_date - today).days

def _urgency_label(days):
    if days is None:
        return "—"
    if days < 0:
        return f"Overdue by {abs(days)}d"
    elif days == 0:
        return "Due today"
    elif days <= 7:
        return f"Due in {days}d"
    elif days <= 30:
        return f"Due in {days}d"
    return f"{days}d remaining"

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
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
    # DATA
    # ------------------------------------------------
    comp = st.session_state.get("compliance_data")

    if comp is None:

        alert_box(
            "Compliance data not loaded.",
            "warning"
        )
        return

    comp = comp.copy()

    if "Penalty_Risk (₹)" in comp.columns:

        comp.rename(
            columns={
                "Penalty_Risk (₹)":
                "Penalty_Risk"
            },
            inplace=True
        )

    comp["Penalty_Risk"] = pd.to_numeric(
        comp["Penalty_Risk"],
        errors="coerce"
    ).fillna(0)

    comp["Due_Date"] = pd.to_datetime(
        comp["Due_Date"],
        dayfirst=True,
        errors="coerce"
    )

    comp["Submitted_Date"] = pd.to_datetime(
        comp["Submitted_Date"],
        dayfirst=True,
        errors="coerce"
    )

    total = len(comp)

    n_compliant = (
        comp["Status"] == "Compliant"
    ).sum()

    n_pending = (
        comp["Status"] == "Pending"
    ).sum()

    n_at_risk = (
        comp["Status"] == "At Risk"
    ).sum()

    n_non_comp = (
        comp["Status"] == "Non-Compliant"
    ).sum()

    total_risk = comp[
        "Penalty_Risk"
    ].sum()

    critical_cnt = (
        comp["Priority"] == "Critical"
    ).sum()

    compliance_rate = (
        round(
            n_compliant / total * 100,
            1
        )
        if total
        else 0
    )

    comp["_days_until"] = (
        comp["Due_Date"]
        .apply(_days_until)
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

        Compliance Tracking Centre

        </h1>

        <p style="
        margin-top:10px;
        opacity:.92;
        font-size:14px;">

        Monitor regulatory obligations,
        deadlines and penalty exposure.

        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    # ------------------------------------------------
    # NAVIGATION
    # ------------------------------------------------
    view = st.radio(
        "",
        [
            "Overview",
            "All Obligations",
            "Deadline Tracker",
            "Risk Analysis"
        ],
        horizontal=True,
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ===================================================
    # OVERVIEW
    # ===================================================
    if view == "Overview":

        c1, c2, c3, c4, c5 = st.columns(5)

        with c1:

            kpi_card(
                "Compliant",
                str(n_compliant),
                f"{compliance_rate:.1f}% compliance rate",
                "check_circle"
            )

        with c2:

            kpi_card(
                "Pending",
                str(n_pending),
                "Awaiting action",
                "schedule"
            )

        with c3:

            kpi_card(
                "At Risk",
                str(n_at_risk),
                "Near deadline",
                "warning"
            )

        with c4:

            kpi_card(
                "Non-Compliant",
                str(n_non_comp),
                "Immediate attention",
                "dangerous"
            )

        with c5:

            kpi_card(
                "Penalty Risk",
                f"₹{total_risk/1e6:.2f}M",
                f"{critical_cnt} critical items",
                "payments"
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # ------------------------------------------------
        # STATUS DISTRIBUTION
        # ------------------------------------------------
        col1, col2 = st.columns([1, 2])

        with col1:

            section_header(
                "Status Distribution",
                "Across all compliance obligations"
            )

            status_vc = comp["Status"].value_counts()

            fig_pie = go.Figure(
                go.Pie(
                    labels=status_vc.index,
                    values=status_vc.values,
                    hole=0.60,
                    marker=dict(
                        colors=[
                            STATUS_COLORS.get(
                                x,
                                "#64748B"
                            )
                            for x in status_vc.index
                        ]
                    )
                )
            )

            fig_pie = style_plotly_fig(
                fig_pie,
                320
            )

            st.plotly_chart(
                fig_pie,
                use_container_width=True
            )

        # -----------------------------------
        # REGULATION TYPE × STATUS
        # -----------------------------------
        with col2:

            section_header(
                "Regulation Type × Status",
                "Status breakdown by regulation"
            )

            cross = (
                comp.groupby(
                    [
                        "Regulation_Type",
                        "Status"
                    ]
                )
                .size()
                .unstack(fill_value=0)
            )

            fig_cross = go.Figure()

            color_map = {
                "Compliant": "#10B981",
                "Pending": "#2563EB",
                "At Risk": "#F59E0B",
                "Non-Compliant": "#EF4444"
            }

            for col in cross.columns:

                fig_cross.add_trace(
                    go.Bar(
                        name=col,
                        x=cross.index,
                        y=cross[col],
                        marker_color=color_map.get(
                            col,
                            "#64748B"
                        )
                    )
                )

            fig_cross.update_layout(
                barmode="stack"
            )

            fig_cross = style_plotly_fig(
                fig_cross,
                320
            )

            st.plotly_chart(
                fig_cross,
                use_container_width=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # ------------------------------------------------
        # COMPLIANCE BY DEPARTMENT
        # ------------------------------------------------
        d1, d2 = st.columns(2)

        with d1:

            section_header(
                "Compliance by Department",
                "Department-wise distribution"
            )

            dept_status = (
                comp.groupby(
                    [
                        "Department",
                        "Status"
                    ]
                )
                .size()
                .unstack(fill_value=0)
            )

            fig_dept = go.Figure()

            for col in dept_status.columns:

                fig_dept.add_trace(
                    go.Bar(
                        name=col,
                        y=dept_status.index,
                        x=dept_status[col],
                        orientation="h",
                        marker_color=color_map.get(
                            col,
                            "#64748B"
                        )
                    )
                )

            fig_dept.update_layout(
                barmode="stack"
            )

            fig_dept = style_plotly_fig(
                fig_dept,
                320
            )

            st.plotly_chart(
                fig_dept,
                use_container_width=True
            )

        # ------------------------------------------------
        # PENALTY RISK BY REGULATION
        # ------------------------------------------------
        with d2:

            section_header(
                "Penalty Risk by Regulation Type",
                "Penalty exposure analysis"
            )

            reg_risk = (
                comp.groupby(
                    "Regulation_Type"
                )["Penalty_Risk"]
                .sum()
                .sort_values()
            )

            fig_risk = go.Figure()

            fig_risk.add_trace(
                go.Bar(
                    x=reg_risk.values,
                    y=reg_risk.index,
                    orientation="h",
                    marker_color="#2563EB"
                )
            )

            fig_risk = style_plotly_fig(
                fig_risk,
                320
            )

            st.plotly_chart(
                fig_risk,
                use_container_width=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # ------------------------------------------------
        # CRITICAL ALERTS
        # ------------------------------------------------
        critical_items = comp[
            (comp["Priority"] == "Critical")
            &
            (comp["Status"] != "Compliant")
        ]

        if len(critical_items) > 0:

            section_header(
                "Critical Alerts",
                "Items requiring immediate attention"
            )

            for _, row in critical_items.head(5).iterrows():

                alert_box(
                    f"{row['Regulation_Type']} | "
                    f"{row['Applicable_To']} | "
                    f"Penalty Risk ₹{row['Penalty_Risk']:,.0f}",
                    "error"
                )

        # ------------------------------------------------
        # AI INSIGHTS
        # ------------------------------------------------
        st.markdown("<br>", unsafe_allow_html=True)

        section_header(
            "AI Compliance Insights",
            "Automated observations and recommendations"
        )

        riskiest_dept = (
            comp.groupby("Department")
            ["Penalty_Risk"]
            .sum()
            .idxmax()
        )

        riskiest_val = (
            comp.groupby("Department")
            ["Penalty_Risk"]
            .sum()
            .max()
        )

        riskiest_reg = (
            comp.groupby("Regulation_Type")
            ["Penalty_Risk"]
            .sum()
            .idxmax()
        )

        non_comp_df = comp[
            comp["Status"] != "Compliant"
        ]

        owner = (
            non_comp_df.groupby(
                "Responsible_Person"
            )
            .size()
            .idxmax()
            if len(non_comp_df) > 0
            else "N/A"
        )

        i1, i2, i3 = st.columns(3)

        with i1:

            kpi_card(
                "Highest Risk Department",
                riskiest_dept,
                f"₹{riskiest_val:,.0f} exposure",
                "business"
            )

        with i2:

            kpi_card(
                "Riskiest Regulation",
                riskiest_reg,
                "Highest penalty risk",
                "gavel"
            )

        with i3:

            kpi_card(
                "Overloaded Owner",
                owner,
                "Needs workload balancing",
                "person"
            )

    # =====================================================
    # ALL OBLIGATIONS
    # =====================================================
    elif view == "All Obligations":

        section_header(
            "All Compliance Obligations",
            "Inspect and filter all records"
        )

        st.dataframe(
            comp,
            use_container_width=True,
            hide_index=True
        )

    # =====================================================
    # DEADLINE TRACKER
    # =====================================================
    elif view == "Deadline Tracker":

        section_header(
            "Upcoming Deadlines",
            "Overdue and upcoming obligations"
        )

        upcoming = comp[
            comp["Status"] != "Compliant"
        ].copy()

        upcoming = upcoming.sort_values(
            "_days_until"
        )

        st.dataframe(
            upcoming,
            use_container_width=True,
            hide_index=True
        )

    # =====================================================
    # RISK ANALYSIS
    # =====================================================
    elif view == "Risk Analysis":

        section_header(
            "Penalty Risk Analysis",
            "Deep dive into compliance exposure"
        )

        col_tree, col_bubble = st.columns(2)

        # -----------------------------------
        # TREEMAP
        # -----------------------------------
        with col_tree:

            tree_data = comp[
                comp["Penalty_Risk"] > 0
            ]

            fig_tree = px.treemap(
                tree_data,
                path=[
                    "Department",
                    "Regulation_Type"
                ],
                values="Penalty_Risk",
                color="Priority",
                color_discrete_map={
                    "Critical": "#EF4444",
                    "High": "#F59E0B",
                    "Medium": "#2563EB",
                    "Low": "#10B981"
                }
            )

            fig_tree = style_plotly_fig(
                fig_tree,
                360
            )

            st.plotly_chart(
                fig_tree,
                use_container_width=True
            )

        # -----------------------------------
        # BUBBLE CHART
        # -----------------------------------
        with col_bubble:

            bubble = (
                comp.groupby(
                    [
                        "Regulation_Type",
                        "Status"
                    ]
                )
                .agg(
                    Total_Risk=(
                        "Penalty_Risk",
                        "sum"
                    ),
                    Count=(
                        "Compliance_ID",
                        "count"
                    )
                )
                .reset_index()
            )

            bubble = bubble[
                bubble["Total_Risk"] > 0
            ]

            fig_bubble = px.scatter(
                bubble,
                x="Status",
                y="Regulation_Type",
                size="Total_Risk",
                color="Status",
                color_discrete_map={
                    "Compliant": "#10B981",
                    "Pending": "#2563EB",
                    "At Risk": "#F59E0B",
                    "Non-Compliant": "#EF4444"
                }
            )

            fig_bubble = style_plotly_fig(
                fig_bubble,
                360
            )

            st.plotly_chart(
                fig_bubble,
                use_container_width=True
            )

        # -----------------------------------
        # PRIORITY RISK
        # -----------------------------------
        pri_risk = (
            comp.groupby("Priority")
            ["Penalty_Risk"]
            .sum()
            .reindex(
                [
                    "Critical",
                    "High",
                    "Medium",
                    "Low"
                ]
            )
            .fillna(0)
        )

        fig_pri = go.Figure()

        fig_pri.add_trace(
            go.Bar(
                x=pri_risk.index,
                y=pri_risk.values,
                marker_color=[
                    "#EF4444",
                    "#F59E0B",
                    "#2563EB",
                    "#10B981"
                ]
            )
        )

        fig_pri = style_plotly_fig(
            fig_pri,
            300
        )

        st.plotly_chart(
            fig_pri,
            use_container_width=True
        )
