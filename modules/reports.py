import streamlit as st
import pandas as pd

from utils.theme import (
    inject_theme,
    section_header,
    kpi_card,
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

    gst = st.session_state.get(
        "gst_data"
    )

    fraud = st.session_state.get(
        "ml_fraud_result"
    )

    comp = st.session_state.get(
        "compliance_data"
    )

    if fin is None:

        alert_box(
            "Financial data not loaded.",
            "warning"
        )
        return

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

        Reports Center

        </h1>

        <p style="
        margin-top:10px;
        opacity:.92;
        font-size:14px;">

        Executive reporting and
        consolidated business insights.

        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    # -----------------------------------
    # KPI VALUES
    # -----------------------------------
    total_rev = fin["Revenue"].sum()

    total_profit = fin["Net_Profit"].sum()

    total_gst = (
        gst["Total_GST"].sum()
        if gst is not None
        else 0
    )

    total_penalty = (
        comp["Penalty_Risk"].sum()
        if (
            comp is not None
            and "Penalty_Risk"
            in comp.columns
        )
        else 0
    )

    fraud_count = (
        fraud["ml_is_fraud"]
        .sum()
        if (
            fraud is not None
            and "ml_is_fraud"
            in fraud.columns
        )
        else 0
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        kpi_card(
            "Revenue",
            f"₹{total_rev/1e6:.2f}M",
            "Business turnover",
            "payments"
        )

    with c2:

        kpi_card(
            "Profit",
            f"₹{total_profit/1e6:.2f}M",
            "Net profitability",
            "trending_up"
        )

    with c3:

        kpi_card(
            "GST Collected",
            f"₹{total_gst/1e6:.2f}M",
            "Tax liability",
            "receipt_long"
        )

    with c4:

        kpi_card(
            "Fraud Cases",
            str(int(fraud_count)),
            "Flagged anomalies",
            "warning"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------
    # FINANCIAL SNAPSHOT
    # ------------------------------------------------
    section_header(
        "Financial Snapshot",
        "High-level financial performance"
    )

    latest_rev = fin["Revenue"].iloc[-1]
    latest_profit = fin["Net_Profit"].iloc[-1]
    latest_cash = fin["Cash_Flow"].iloc[-1]
    avg_margin = fin["Profit_Margin"].mean()

    f1, f2, f3, f4 = st.columns(4)

    with f1:

        kpi_card(
            "Latest Revenue",
            f"₹{latest_rev/1e6:.2f}M",
            "Current period",
            "payments"
        )

    with f2:

        kpi_card(
            "Latest Profit",
            f"₹{latest_profit/1e6:.2f}M",
            "Current period",
            "trending_up"
        )

    with f3:

        kpi_card(
            "Cash Flow",
            f"₹{latest_cash/1e6:.2f}M",
            "Current period",
            "account_balance_wallet"
        )

    with f4:

        kpi_card(
            "Avg Margin",
            f"{avg_margin:.1f}%",
            "Profitability",
            "percent"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------
    # COMPLIANCE SNAPSHOT
    # ------------------------------------------------
    if comp is not None:

        section_header(
            "Compliance Snapshot",
            "Regulatory status overview"
        )

        compliant = (
            comp["Status"] == "Compliant"
        ).sum()

        pending = (
            comp["Status"] == "Pending"
        ).sum()

        at_risk = (
            comp["Status"] == "At Risk"
        ).sum()

        critical = (
            comp["Priority"] == "Critical"
        ).sum()

        c1, c2, c3, c4 = st.columns(4)

        with c1:

            kpi_card(
                "Compliant",
                str(compliant),
                "Completed obligations",
                "check_circle"
            )

        with c2:

            kpi_card(
                "Pending",
                str(pending),
                "Awaiting action",
                "schedule"
            )

        with c3:

            kpi_card(
                "At Risk",
                str(at_risk),
                "Near deadline",
                "warning"
            )

        with c4:

            kpi_card(
                "Critical",
                str(critical),
                "High priority",
                "dangerous"
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------
    # GST SNAPSHOT
    # ------------------------------------------------
    if gst is not None:

        section_header(
            "GST Snapshot",
            "Tax compliance indicators"
        )

        filed = (
            gst["Status"]
            == "Filed On Time"
        ).sum()

        late = (
            gst["Status"]
            == "Late Filing"
        ).sum()

        missed = (
            gst["Status"]
            == "Missed"
        ).sum()

        avg_score = pd.to_numeric(
            gst["Compliance_Score"]
            .astype(str)
            .str.replace("%", ""),
            errors="coerce"
        ).mean()

        g1, g2, g3, g4 = st.columns(4)

        with g1:

            kpi_card(
                "Filed On Time",
                str(filed),
                "Successful filings",
                "check_circle"
            )

        with g2:

            kpi_card(
                "Late Filings",
                str(late),
                "Delayed filings",
                "warning"
            )

        with g3:

            kpi_card(
                "Missed",
                str(missed),
                "Not submitted",
                "dangerous"
            )

        with g4:

            kpi_card(
                "Compliance Score",
                f"{avg_score:.1f}%",
                "Average score",
                "analytics"
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------
    # FRAUD SNAPSHOT
    # ------------------------------------------------
    if fraud is not None:

        section_header(
            "Fraud Snapshot",
            "AI anomaly detection summary"
        )

        flagged = (
            fraud["ml_is_fraud"]
            == True
        ).sum()

        safe = (
            fraud["ml_is_fraud"]
            == False
        ).sum()

        avg_risk = (
            fraud.loc[
                fraud["ml_is_fraud"],
                "ml_risk_score"
            ].mean()
        )

        r1, r2, r3 = st.columns(3)

        with r1:

            kpi_card(
                "Safe Transactions",
                str(int(safe)),
                "Normal transactions",
                "check_circle"
            )

        with r2:

            kpi_card(
                "Flagged Transactions",
                str(int(flagged)),
                "Suspicious records",
                "warning"
            )

        with r3:

            kpi_card(
                "Average Risk",
                f"{avg_risk:.1f}%",
                "Anomaly severity",
                "security"
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------
    # AI EXECUTIVE SUMMARY
    # ------------------------------------------------
    section_header(
        "AI Executive Summary",
        "Business highlights generated automatically"
    )

    ai1, ai2, ai3 = st.columns(3)

    with ai1:

        kpi_card(
            "Revenue Position",
            f"₹{total_rev/1e6:.2f}M",
            "Strong financial base",
            "trending_up"
        )

    with ai2:

        kpi_card(
            "Compliance Exposure",
            f"₹{total_penalty/1e6:.2f}M",
            "Potential penalty risk",
            "gavel"
        )

    with ai3:

        kpi_card(
            "Fraud Exposure",
            str(int(fraud_count)),
            "Flagged anomalies",
            "security"
        )

    st.markdown("<br>", unsafe_allow_html=True)


    # ------------------------------------------------
    # REPORT DATA EXPORT
    # ------------------------------------------------
    section_header(
        "Export Reports",
        "Download consolidated business data"
    )

    exp1, exp2, exp3 = st.columns(3)

    # -----------------------------------
    # FINANCIAL EXPORT
    # -----------------------------------
    with exp1:

        fin_csv = (
            fin
            .to_csv(index=False)
            .encode("utf-8")
        )

        st.download_button(
            "Export Financial Report",
            data=fin_csv,
            file_name="financial_report.csv",
            mime="text/csv",
            use_container_width=True
        )

    # -----------------------------------
    # COMPLIANCE EXPORT
    # -----------------------------------
    with exp2:

        if comp is not None:

            comp_csv = (
                comp
                .to_csv(index=False)
                .encode("utf-8")
            )

            st.download_button(
                "Export Compliance Report",
                data=comp_csv,
                file_name="compliance_report.csv",
                mime="text/csv",
                use_container_width=True
            )

    # -----------------------------------
    # GST EXPORT
    # -----------------------------------
    with exp3:

        if gst is not None:

            gst_csv = (
                gst
                .to_csv(index=False)
                .encode("utf-8")
            )

            st.download_button(
                "Export GST Report",
                data=gst_csv,
                file_name="gst_report.csv",
                mime="text/csv",
                use_container_width=True
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------
    # REPORT PREVIEW TABLES
    # ------------------------------------------------
    section_header(
        "Report Preview",
        "Latest records from each module"
    )

    tab1, tab2, tab3 = st.tabs(
        [
            "Finance",
            "Compliance",
            "GST"
        ]
    )

    with tab1:

        st.dataframe(
            fin.tail(10),
            use_container_width=True,
            hide_index=True
        )

    with tab2:

        if comp is not None:

            st.dataframe(
                comp.tail(10),
                use_container_width=True,
                hide_index=True
            )

    with tab3:

        if gst is not None:

            st.dataframe(
                gst.tail(10),
                use_container_width=True,
                hide_index=True
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------
    # BUSINESS HEALTH
    # ------------------------------------------------
    section_header(
        "Business Health Assessment",
        "AI-generated health indicators"
    )

    margin = fin["Profit_Margin"].mean()

    if margin >= 20:

        alert_box(
            "Business profitability remains strong with healthy margins.",
            "success"
        )

    elif margin >= 10:

        alert_box(
            "Profitability is moderate. Monitor operational expenses.",
            "warning"
        )

    else:

        alert_box(
            "Profit margins are under pressure and require attention.",
            "error"
        )

    if fraud_count > 0:

        alert_box(
            f"{int(fraud_count)} suspicious transactions have been detected.",
            "warning"
        )

    else:

        alert_box(
            "No fraud anomalies detected.",
            "success"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------
    # AI REPORT SUMMARY
    # ------------------------------------------------
    section_header(
        "AI Report Summary",
        "Executive summary for management"
    )

    summary = f"""
Total revenue reached ₹{total_rev/1e6:.2f}M with
net profit of ₹{total_profit/1e6:.2f}M.

GST collections amounted to ₹{total_gst/1e6:.2f}M.

Potential compliance exposure stands at
₹{total_penalty/1e6:.2f}M.

AI Fraud Detection flagged {int(fraud_count)}
suspicious transactions.

Overall business performance remains
{'strong' if avg_margin >= 20 else 'stable' if avg_margin >= 10 else 'under pressure'}.
"""

    st.info(summary)

    # ------------------------------------------------
    # SESSION SUMMARY
    # ------------------------------------------------
    st.session_state["reports_summary"] = summary

