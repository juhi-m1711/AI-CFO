"""
modules/fraud_detection.py
==========================
[MODIFY] Fraud Anomaly Detection — AI-CFO Finance sub-tab.

Changes from original:
- All inline <style> blocks removed; theme.py tokens used throughout.
- All emojis (13 found: ⚠ 🔍 🛡 🤖 ✅ 📊 🔴 🟢 👆) replaced with Material Icons.
- Both Plotly charts (scatter + histogram) pass through style_plotly_fig().
- Hero banner matches platform-wide danger gradient style.
- Unnecessary radio nav (single-option) removed.
- KPI cards converted to kpi_card() from theme.py.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from utils.theme import (
    section_header, kpi_card, style_plotly_fig, alert_box,
    PRIMARY, PRIMARY_LIGHT, PRIMARY_DARK,
    SUCCESS, SUCCESS_BG,
    WARNING, WARNING_BG,
    DANGER,  DANGER_BG,
    WHITE, BORDER,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    FONT,
)


# ─────────────────────────────────────────────────────────────
# ML MODEL
# ─────────────────────────────────────────────────────────────

def run_isolation_forest(df):
    """
    Train an Isolation Forest on financial transaction features.
    Returns the input df enriched with ml_is_fraud, ml_risk_score, Risk_Flag.
    Also saves model artifacts to models/ directory.
    """
    df = df.copy().reset_index(drop=True)

    features = pd.DataFrame({
        "amount":       df["Amount"],
        "days_overdue": pd.to_numeric(df["Days_Overdue"], errors="coerce").fillna(0),
        "gst_rate":     pd.to_numeric(df["GST_Rate"],     errors="coerce").fillna(0),
        "status":       df["Status"].map({
            "Paid": 0, "Pending": 1, "Partially Paid": 1, "Overdue": 2,
        }).fillna(0),
    })

    scaler = StandardScaler()
    X      = scaler.fit_transform(features)

    model  = IsolationForest(contamination=0.08, random_state=42, n_estimators=100)
    model.fit(X)

    preds = model.predict(X)
    raw   = model.score_samples(X)

    denom = raw.max() - raw.min()
    df["ml_risk_score"] = (
        0 if denom == 0
        else ((raw.max() - raw) / denom * 100).round(1)
    )

    df["ml_is_fraud"] = preds == -1

    def get_risk_label(score):
        if score >= 80:  return "High"
        if score >= 50:  return "Medium"
        return "Low"

    df["Risk_Flag"] = df["ml_risk_score"].apply(get_risk_label)

    # Save model artifacts
    import os, joblib
    BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODEL_DIR  = os.path.join(BASE_DIR, "models")
    os.makedirs(MODEL_DIR, exist_ok=True)
    FEATURES   = ["amount", "days_overdue", "gst_rate", "status"]
    joblib.dump(model,    os.path.join(MODEL_DIR, "fraud_detection_model.pkl"))
    joblib.dump(scaler,   os.path.join(MODEL_DIR, "fraud_scaler.pkl"))
    joblib.dump(FEATURES, os.path.join(MODEL_DIR, "fraud_features.pkl"))

    return df


# ─────────────────────────────────────────────────────────────
# CHART BUILDERS
# ─────────────────────────────────────────────────────────────

def _chart_scatter(result: pd.DataFrame) -> go.Figure:
    """Amount vs Date scatter — red=anomaly, green=normal."""
    flagged = result[result["ml_is_fraud"] == True]
    safe    = result[result["ml_is_fraud"] == False]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=safe["Date"], y=safe["Amount"],
        mode="markers", name="Normal",
        marker=dict(color=SUCCESS, size=5, opacity=0.65,
                    line=dict(color=WHITE, width=0.5)),
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Amount: ₹%{y:,.0f}<br>"
            "<extra>Normal</extra>"
        ),
    ))
    fig.add_trace(go.Scatter(
        x=flagged["Date"], y=flagged["Amount"],
        mode="markers", name="Anomaly",
        marker=dict(color=DANGER, size=7, opacity=0.9,
                    symbol="x",
                    line=dict(color=WHITE, width=0.8)),
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Amount: ₹%{y:,.0f}<br>"
            "<extra>Anomaly</extra>"
        ),
    ))

    style_plotly_fig(fig, height=300)
    fig.update_layout(
        title=dict(
            text="Flagged vs Normal Transactions",
            font=dict(size=13, color=TEXT_PRIMARY, family=FONT),
            x=0, pad=dict(l=4),
        ),
        margin=dict(l=12, r=12, t=36, b=40),
        xaxis=dict(tickformat="%b %Y", tickfont=dict(size=9), tickangle=-30),
        yaxis=dict(tickprefix="₹", tickformat=".2s"),
        legend=dict(orientation="h", x=0, y=-0.28),
    )
    return fig


def _chart_risk_hist(result: pd.DataFrame) -> go.Figure:
    """Histogram of ML risk scores — split by anomaly flag."""
    flagged = result[result["ml_is_fraud"] == True]["ml_risk_score"]
    safe    = result[result["ml_is_fraud"] == False]["ml_risk_score"]

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=safe, name="Normal",
        nbinsx=25,
        marker=dict(color=SUCCESS, opacity=0.75, line=dict(color=WHITE, width=0.5)),
        hovertemplate="Risk Score %{x:.0f}%<br>Count: %{y}<extra>Normal</extra>",
    ))
    fig.add_trace(go.Histogram(
        x=flagged, name="Anomaly",
        nbinsx=25,
        marker=dict(color=DANGER, opacity=0.85, line=dict(color=WHITE, width=0.5)),
        hovertemplate="Risk Score %{x:.0f}%<br>Count: %{y}<extra>Anomaly</extra>",
    ))

    style_plotly_fig(fig, height=300)
    fig.update_layout(
        title=dict(
            text="ML Risk Score Distribution",
            font=dict(size=13, color=TEXT_PRIMARY, family=FONT),
            x=0, pad=dict(l=4),
        ),
        barmode="overlay",
        margin=dict(l=12, r=12, t=36, b=40),
        xaxis=dict(title="Risk Score (%)", tickfont=dict(size=10)),
        yaxis=dict(title="Count",          tickfont=dict(size=10)),
        legend=dict(orientation="h", x=0, y=-0.28),
    )
    return fig


# ─────────────────────────────────────────────────────────────
# MAIN SHOW FUNCTION
# ─────────────────────────────────────────────────────────────

def show():

    # ── Data ─────────────────────────────────────────────────
    txn_df = st.session_state.get("financial_transactions")
    if txn_df is None:
        alert_box("Financial transaction data not loaded.", "error")
        return

    # ── Hero Banner ───────────────────────────────────────────
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#B91C1C,{DANGER});
                border-radius:16px; padding:28px 36px; color:white;
                margin-bottom:24px; position:relative; overflow:hidden;">
        <div style="position:absolute;right:36px;top:50%;transform:translateY(-50%);
                    font-family:'Material Icons';font-size:80px;opacity:0.12;color:white;">
            security
        </div>
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
            <span class="material-icons" style="color:rgba(255,255,255,0.9);font-size:20px;">shield</span>
            <span style="font-size:12px;font-weight:600;font-family:{FONT};
                         background:rgba(255,255,255,0.2);border-radius:20px;
                         padding:3px 12px;">AI Fraud Protection</span>
        </div>
        <div style="font-size:24px;font-weight:800;font-family:{FONT};
                    letter-spacing:-0.5px;margin-bottom:6px;">
            AI Fraud Detection Center
        </div>
        <div style="font-size:13px;opacity:0.88;font-family:{FONT};">
            Real-time anomaly detection powered by Isolation Forest ML model
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Scan control ─────────────────────────────────────────
    section_header(
        "Real-Time Fraud Detection",
        "Run the Isolation Forest model on all transactions to detect hidden anomalies",
    )

    btn_col, stat_col = st.columns([1, 3])
    with btn_col:
        run_btn = st.button(
            "Run AI Scan",
            type="primary",
            use_container_width=True,
        )
    with stat_col:
        st.markdown(f"""
        <div style="padding:10px 0;font-size:12px;color:{TEXT_MUTED};
                    font-family:{FONT};display:flex;align-items:center;gap:8px;">
            <span class="material-icons" style="font-size:15px;color:{TEXT_MUTED};">
                history
            </span>
            Scan all {len(txn_df)} transactions — results stored in session state
            and shown on the Dashboard.
        </div>
        """, unsafe_allow_html=True)

    # ── ML Results ───────────────────────────────────────────
    if run_btn or st.session_state.get("ml_fraud_ran"):

        if run_btn or "ml_fraud_result" not in st.session_state:
            with st.spinner("Training Isolation Forest model on transaction data..."):
                result = run_isolation_forest(txn_df)
                st.session_state["ml_fraud_result"] = result
                st.session_state["ml_fraud_ran"]    = True

        result  = st.session_state["ml_fraud_result"]
        flagged = result[result["ml_is_fraud"] == True]
        safe    = result[result["ml_is_fraud"] == False]

        safe_pct     = len(safe)    / len(result) * 100
        flag_pct     = len(flagged) / len(result) * 100
        avg_risk     = flagged["ml_risk_score"].mean() if len(flagged) > 0 else 0
        high_risk_c  = int((flagged["Risk_Flag"] == "High").sum()) if len(flagged) > 0 else 0

        # ── KPI Row ───────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.markdown(
                kpi_card("Safe Transactions", str(len(safe)),
                         f"{safe_pct:.0f}% of total",
                         "check_circle", " ", "up", SUCCESS),
                unsafe_allow_html=True,
            )
        with m2:
            st.markdown(
                kpi_card("Flagged Transactions", str(len(flagged)),
                         f"{flag_pct:.0f}% of total",
                         "warning", " ", "down" if len(flagged) > 0 else "neutral",
                         DANGER if len(flagged) > 0 else SUCCESS),
                unsafe_allow_html=True,
            )
        with m3:
            st.markdown(
                kpi_card("Avg Risk Score", f"{avg_risk:.0f}%",
                         "Across flagged transactions",
                         "bar_chart", " ", "neutral", WARNING),
                unsafe_allow_html=True,
            )
        with m4:
            st.markdown(
                kpi_card("High-Risk Count", str(high_risk_c),
                         "Risk score >= 80%",
                         "gpp_bad", " ", "down" if high_risk_c > 0 else "neutral",
                         DANGER if high_risk_c > 0 else SUCCESS),
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Charts Row ────────────────────────────────────────
        ch1, ch2 = st.columns(2)
        with ch1:
            st.plotly_chart(_chart_scatter(result), use_container_width=True)
        with ch2:
            st.plotly_chart(_chart_risk_hist(result), use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Risk breakdown bar ────────────────────────────────
        section_header("Risk Level Breakdown", "Distribution of ML risk levels across flagged transactions")
        if len(flagged) > 0:
            risk_counts = flagged["Risk_Flag"].value_counts()
            risk_colors = {"High": DANGER, "Medium": WARNING, "Low": SUCCESS}
            fig_risk = go.Figure(go.Bar(
                x=risk_counts.index,
                y=risk_counts.values,
                marker=dict(
                    color=[risk_colors.get(k, PRIMARY) for k in risk_counts.index],
                    line=dict(color=WHITE, width=1),
                ),
                hovertemplate="<b>%{x}</b><br>%{y} transactions<extra></extra>",
            ))
            style_plotly_fig(fig_risk, height=220, show_legend=False)
            fig_risk.update_layout(margin=dict(l=8, r=8, t=8, b=8))
            st.plotly_chart(fig_risk, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Flagged transactions table ────────────────────────
        if len(flagged) > 0:
            section_header(
                "ML Flagged Transactions",
                f"{len(flagged)} transactions flagged — sorted by risk score descending",
            )
            disp = flagged[[
                "Txn_ID", "Date", "Vendor/Client", "Category",
                "Amount", "Risk_Flag", "Status", "ml_risk_score",
            ]].sort_values("ml_risk_score", ascending=False).copy()
            disp["Amount"] = disp["Amount"].apply(lambda x: f"₹{x:,.0f}")
            disp = disp.rename(columns={"ml_risk_score": "ML Risk %", "Risk_Flag": "Risk Level"})
            st.dataframe(disp, use_container_width=True, hide_index=True)
        else:
            alert_box("No anomalies detected across all transactions.", "success")

        # Store summary for AI Assistant
        st.session_state["fraud_summary"] = (
            f"{len(flagged)} transactions flagged by ML out of {len(result)}. "
            f"Average ML risk score: {avg_risk:.1f}%. "
            f"High-risk transactions: {high_risk_c}."
        )

    else:
        # Pre-scan state
        alert_box(
            "Click <b>Run AI Scan</b> above to scan all transactions "
            "for hidden anomalies using the Isolation Forest ML model.",
            "info",
        )
        st.markdown("<br>", unsafe_allow_html=True)
        section_header("Transaction Preview", "First 10 rows — full scan reveals risk scores")
        st.dataframe(
            txn_df[["Txn_ID", "Date", "Vendor/Client", "Category",
                    "Amount", "Status"]].head(10),
            use_container_width=True,
            hide_index=True,
        )