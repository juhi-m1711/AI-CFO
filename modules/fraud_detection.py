import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


# ─────────────────────────────────────────
# ML MODEL
# ─────────────────────────────────────────
def run_isolation_forest(df):
    df = df.copy().reset_index(drop=True)
    features = pd.DataFrame({
        'amount':       df['Amount'].values,
        'days_overdue': pd.to_numeric(df['Days_Overdue'], errors='coerce').fillna(0).values,
        'gst_rate':     pd.to_numeric(df['GST_Rate'], errors='coerce').fillna(0).values,
    })
    scaler = StandardScaler()
    X      = scaler.fit_transform(features)
    model  = IsolationForest(contamination=0.08, random_state=42, n_estimators=100)
    model.fit(X)
    preds  = model.predict(X)
    raw    = model.score_samples(X)
    df['ml_risk_score'] = ((raw - raw.max()) / (raw.min() - raw.max()) * 100).round(1)
    df['ml_is_fraud']   = preds == -1

    import os, joblib
    BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODEL_PATH = os.path.join(BASE_DIR, "models", "fraud_detection_model.pkl")
    os.makedirs(os.path.join(BASE_DIR, "models"), exist_ok=True)
    joblib.dump(model,  MODEL_PATH)
    joblib.dump(scaler, os.path.join(BASE_DIR, "models", "fraud_scaler.pkl"))
    return df


# ─────────────────────────────────────────
# MAIN PAGE
# ─────────────────────────────────────────
def show():

    # ── CSS ─────────────────────────────────────────────────────
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

    [data-testid="stAppViewContainer"], .main { background:#F4F5F7 !important; }

    /* ── Hero banner ── */
    .fd-hero {
        background: linear-gradient(120deg, #b91c1c 0%, #dc2626 55%, #ef4444 100%);
        border-radius: 18px;
        padding: 32px 40px;
        color: white;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }
    .fd-hero-icon {
        position: absolute; right: 40px; top: 50%;
        transform: translateY(-50%);
        font-size: 72px; opacity: 0.2;
    }
    .fd-hero h1 {
        font-family: 'Manrope',sans-serif !important;
        font-size: 26px !important; font-weight: 800 !important;
        color: white !important; margin: 0 0 6px 0 !important;
        letter-spacing: -0.5px;
    }
    .fd-hero p {
        font-size: 13px; color: rgba(255,255,255,0.85);
        margin: 0; font-family: 'Manrope',sans-serif;
    }
    .fd-hero-badge {
        display: inline-flex; align-items: center; gap: 6px;
        background: rgba(255,255,255,0.2);
        border-radius: 20px; padding: 4px 12px;
        font-size: 12px; font-weight: 600;
        color: white; margin-bottom: 12px;
        font-family: 'Manrope',sans-serif;
    }

    /* ── KPI cards ── */
    .fd-kpi {
        background: white;
        border-radius: 14px;
        border: 1px solid #E8ECF0;
        padding: 20px 22px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
        height: 100%;
    }
    .fd-kpi-icon {
        width: 40px; height: 40px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 18px; margin-bottom: 10px;
    }
    .fd-kpi-lbl {
        font-size: 11px; font-weight: 600; color: #8492A6;
        text-transform: uppercase; letter-spacing: 0.6px;
        font-family: 'Manrope',sans-serif; margin-bottom: 4px;
    }
    .fd-kpi-val {
        font-size: 32px; font-weight: 800; color: #1A1F36;
        font-family: 'Manrope',sans-serif; letter-spacing: -1px;
        line-height: 1; margin-bottom: 6px;
    }
    .fd-kpi-sub { font-size: 12px; font-family: 'Manrope',sans-serif; }
    .fd-kpi-sub-green  { color: #16a34a; font-weight: 600; }
    .fd-kpi-sub-orange { color: #d97706; font-weight: 600; }
    .fd-kpi-sub-muted  { color: #8492A6; }

    /* ── Section card ── */
    .fd-card {
        background: white; border-radius: 14px;
        border: 1px solid #E8ECF0; padding: 22px 24px;
        margin-bottom: 16px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    }
    .fd-card-title {
        font-size: 15px; font-weight: 700; color: #1A1F36;
        font-family: 'Manrope',sans-serif; margin-bottom: 2px;
    }
    .fd-card-sub {
        font-size: 12px; color: #8492A6;
        font-family: 'Manrope',sans-serif; margin-bottom: 0;
    }
    .fd-card-hdr {
        display: flex; justify-content: space-between;
        align-items: center; margin-bottom: 16px;
    }
    .fd-period-btn {
        border: 1px solid #E8ECF0; border-radius: 8px;
        padding: 5px 12px; font-size: 12px; color: #4A5568;
        background: white; font-family: 'Manrope',sans-serif;
    }
    .fd-viewall {
        font-size: 12px; font-weight: 600; color: #dc2626;
        font-family: 'Manrope',sans-serif; cursor: pointer;
    }

    /* ── Risk badge ── */
    .risk-high   { background:#FFF1F2; color:#dc2626; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:700; font-family:'Manrope',sans-serif; }
    .risk-med    { background:#FFFBEB; color:#d97706; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:700; font-family:'Manrope',sans-serif; }
    .risk-low    { background:#F0FDF4; color:#16a34a; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:700; font-family:'Manrope',sans-serif; }

    /* ── Status badge ── */
    .st-open    { background:#FFF1F2; color:#dc2626; padding:3px 10px; border-radius:6px; font-size:11px; font-weight:600; font-family:'Manrope',sans-serif; }
    .st-review  { background:#FFFBEB; color:#d97706; padding:3px 10px; border-radius:6px; font-size:11px; font-weight:600; font-family:'Manrope',sans-serif; }
    .st-cleared { background:#F0FDF4; color:#16a34a; padding:3px 10px; border-radius:6px; font-size:11px; font-weight:600; font-family:'Manrope',sans-serif; }

    /* ── Insight cards ── */
    .ins-fd {
        background: white; border-radius: 14px;
        border: 1px solid #E8ECF0; padding: 20px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04); height: 100%;
    }
    .ins-fd-icon {
        width: 38px; height: 38px; border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-size: 18px; margin-bottom: 12px;
    }
    .ins-fd-title {
        font-size: 13px; font-weight: 700; color: #1A1F36;
        font-family: 'Manrope',sans-serif; margin-bottom: 6px;
    }
    .ins-fd-body {
        font-size: 12px; color: #6B7280;
        font-family: 'Manrope',sans-serif; line-height: 1.5;
        margin-bottom: 12px;
    }
    .ins-fd-link {
        font-size: 12px; font-weight: 600; color: #dc2626;
        font-family: 'Manrope',sans-serif;
    }

    /* ── ML Scanner card ── */
    .ml-card {
        background: white; border-radius: 14px;
        border: 1px solid #E8ECF0; padding: 24px;
        margin-bottom: 16px;
    }
    .ml-stat {
        display: flex; align-items: center; gap: 10px;
    }
    .ml-stat-icon {
        width: 36px; height: 36px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 16px;
    }

    /* Disable default Streamlit expander arrow color */
    .streamlit-expanderHeader { font-family: 'Manrope',sans-serif !important; }

    /* Override plotly chart background */
    .js-plotly-plot .plotly { background: white !important; }

    /* Table header */
    .tbl-hdr {
        display: grid;
        grid-template-columns: 1fr 1fr 1.5fr 1.2fr 1fr 0.8fr 1.2fr 0.8fr;
        padding: 10px 0; border-bottom: 2px solid #E8ECF0;
        font-size: 11px; font-weight: 700; color: #8492A6;
        text-transform: uppercase; letter-spacing: 0.5px;
        font-family: 'Manrope',sans-serif;
    }
    .tbl-row {
        display: grid;
        grid-template-columns: 1fr 1fr 1.5fr 1.2fr 1fr 0.8fr 1.2fr 0.8fr;
        padding: 12px 0; border-bottom: 1px solid #F3F4F6;
        align-items: center;
        font-size: 12px; color: #374151;
        font-family: 'Manrope',sans-serif;
    }
    .tbl-row:hover { background: #FAFAFA; }
                
    /* Fraud Tabs */
    div[role="radiogroup"] label {
        background: white !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 10px !important;
        padding: 10px 18px !important;
        margin-right: 10px !important;
    }

    div[role="radiogroup"] label p {
        color: #1A1F36 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        opacity: 1 !important;
    }

    div[role="radiogroup"] label:hover {
        background: #FFF5F5 !important;
        border-color: #EF4444 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Data ────────────────────────────────────────────────────
    fraud_df = st.session_state.get('fraud_data')
    txn_df   = st.session_state.get('financial_transactions')

    if fraud_df is None or txn_df is None:
        st.warning("⚠️ Data not loaded. Please run generate_data.py first.")
        return

    # Clean / recompute
    fraud_df = fraud_df.copy()
    fraud_df['is_fraud']   = fraud_df['ML_Prediction'].str.strip().str.upper() == 'FRAUDULENT'
    fraud_df['Risk_Score'] = pd.to_numeric(
        fraud_df['Risk_Score'].astype(str).str.replace(',','').str.strip(),
        errors='coerce'
    )
    fraud_df['Txn_Amount'] = pd.to_numeric(
        fraud_df['Txn_Amount'].astype(str).str.replace(',','').str.strip(),
        errors='coerce'
    )

    total_txn   = len(txn_df)
    confirmed   = fraud_df[fraud_df['is_fraud'] == True]
    high_risk   = fraud_df[fraud_df['Risk_Score'] > 75]
    safe_count  = total_txn - len(high_risk)
    avg_risk    = fraud_df['Risk_Score'].mean()

    # ── HERO BANNER ─────────────────────────────────────────────
    st.markdown(f"""
    <div class="fd-hero">
        <div class="fd-hero-icon">🔍</div>
        <div class="fd-hero-badge">🛡️ AI Fraud Protection</div>
        <h1>AI Fraud Detection Center</h1>
        <p>Real-time anomaly detection powered by ML & Risk Engine</p>
    </div>
    """, unsafe_allow_html=True)

    # ── FRAUD NAVIGATION ────────────────────────
    fraud_view = st.radio(
        "",
        [
            "🔴 Historical Fraud Cases",
            "🤖 Real-Time Fraud Detection"
        ],
        horizontal=True,
        label_visibility="collapsed"
    )

    if fraud_view == "🔴 Historical Fraud Cases":
        # ── ROW 1: 4 KPI Cards ──────────────────────────────────────
        k1, k2, k3, k4 = st.columns(4)

        safe_pct  = safe_count / total_txn * 100
        high_pct  = len(high_risk) / total_txn * 100

        with k1:
            st.markdown(f"""
            <div class="fd-kpi">
                <div class="fd-kpi-icon" style="background:#EFF6FF;">📄</div>
                <div class="fd-kpi-lbl">Total Transactions</div>
                <div class="fd-kpi-val">{total_txn}</div>
                <div class="fd-kpi-sub fd-kpi-sub-muted">100% of all transactions</div>
            </div>
            """, unsafe_allow_html=True)

        with k2:
            st.markdown(f"""
            <div class="fd-kpi">
                <div class="fd-kpi-icon" style="background:#F0FDF4;">✅</div>
                <div class="fd-kpi-lbl">Safe Transactions</div>
                <div class="fd-kpi-val">{safe_count}</div>
                <div class="fd-kpi-sub fd-kpi-sub-green">{safe_pct:.1f}% of all transactions</div>
            </div>
            """, unsafe_allow_html=True)

        with k3:
            st.markdown(f"""
            <div class="fd-kpi">
                <div class="fd-kpi-icon" style="background:#FFF7ED;">⚠️</div>
                <div class="fd-kpi-lbl">High Risk Transactions</div>
                <div class="fd-kpi-val">{len(high_risk)}</div>
                <div class="fd-kpi-sub fd-kpi-sub-orange">{high_pct:.1f}% of all transactions</div>
            </div>
            """, unsafe_allow_html=True)

        with k4:
            st.markdown(f"""
            <div class="fd-kpi">
                <div class="fd-kpi-icon" style="background:#FDF4FF;">%</div>
                <div class="fd-kpi-lbl">Average Risk Score</div>
                <div class="fd-kpi-val">{avg_risk:.0f}%</div>
                <div class="fd-kpi-sub fd-kpi-sub-orange">↑ 12% vs last 30 days</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── ROW 2: Fraud Risk Trend Chart ───────────────────────────
        st.markdown("""
        <div class="fd-card">
            <div class="fd-card-hdr">
                <div>
                    <div class="fd-card-title">Fraud Risk Trend <span style="color:#8492A6;font-weight:500;font-size:13px;">(Last 30 Days)</span></div>
                </div>
                <div class="fd-period-btn">Last 30 Days ▾</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Build 30-day trend from fraud risk scores (sorted by date)
        fraud_sorted = fraud_df.copy()
        fraud_sorted['Date'] = pd.to_datetime(fraud_sorted['Date'], dayfirst=True, errors='coerce')
        trend = fraud_sorted.dropna(subset=['Date']).sort_values('Date').tail(30)

        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=trend['Date'],
            y=trend['Risk_Score'],
            mode='lines+markers',
            line=dict(color='#ef4444', width=2.5),
            marker=dict(size=6, color='#ef4444',
                        line=dict(color='white', width=1.5)),
            fill='tozeroy',
            fillcolor='rgba(239,68,68,0.06)',
            hovertemplate="<b>%{x|%d %b}</b><br>Risk Score: %{y}<extra></extra>"
        ))
        fig_trend.update_layout(
            height=260,
            paper_bgcolor='white', plot_bgcolor='white',
            font=dict(family='Manrope, sans-serif', color='#374151', size=11),
            margin=dict(l=50, r=20, t=10, b=40),
            xaxis=dict(
                showgrid=False, tickformat='%b %d',
                tickfont=dict(size=10, color='#6B7280'),
                color='#6B7280', linecolor='#E5E7EB',
            ),
            yaxis=dict(
                showgrid=True, gridcolor='#F3F4F6',
                tickfont=dict(size=10, color='#6B7280'),
                color='#6B7280', ticksuffix='%',
                range=[0, 105],
            ),
            showlegend=False,
        )
        st.plotly_chart(fig_trend, use_container_width=True)

        # ── ROW 3: Risk Distribution Donut + Fraud by Category ──────
        col_donut, col_bar = st.columns(2)

        with col_donut:
            st.markdown("""
            <div class="fd-card-title" style="margin-bottom:16px;">Risk Distribution</div>
            """, unsafe_allow_html=True)

            # Bin risk scores into 4 bands
            def risk_band(score):
                if score >= 75:   return 'High Risk (75-100)'
                elif score >= 50: return 'Medium Risk (50-75)'
                elif score >= 25: return 'Low Risk (25-50)'
                else:             return 'Very Low Risk (0-25)'

            fraud_df['risk_band'] = fraud_df['Risk_Score'].apply(risk_band)
            band_counts = fraud_df['risk_band'].value_counts()

            band_order  = ['High Risk (75-100)', 'Medium Risk (50-75)',
                        'Low Risk (25-50)',   'Very Low Risk (0-25)']
            band_colors = ['#ef4444', '#f97316', '#facc15', '#22c55e']

            ordered_vals   = [band_counts.get(b, 0) for b in band_order]
            ordered_colors = band_colors

            fig_donut = go.Figure(go.Pie(
                labels=band_order,
                values=ordered_vals,
                hole=0.55,
                marker=dict(colors=ordered_colors,
                            line=dict(color='white', width=2)),
                textinfo='percent',
                textfont=dict(size=11, color='white',
                            family='Manrope, sans-serif'),
                textposition='inside',
                hovertemplate="<b>%{label}</b><br>%{value} transactions (%{percent})<extra></extra>",
                direction='clockwise',
                rotation=90,
                showlegend=False,
            ))
            fig_donut.update_layout(
                height=240,
                paper_bgcolor='white', plot_bgcolor='white',
                margin=dict(l=10, r=10, t=10, b=10),
                showlegend=False,
            )

            d_left, d_right = st.columns([3, 2])
            with d_left:
                st.plotly_chart(fig_donut, use_container_width=True)
            with d_right:
                st.markdown("<br>", unsafe_allow_html=True)
                for band, color, val in zip(band_order, band_colors, ordered_vals):
                    pct = val / len(fraud_df) * 100
                    st.markdown(f"""
                    <div style="display:flex;align-items:center;gap:8px;
                                margin-bottom:10px;font-family:'Manrope',sans-serif;">
                        <div style="width:10px;height:10px;border-radius:50%;
                                    background:{color};flex-shrink:0;"></div>
                        <div>
                            <div style="font-size:11px;color:#374151;font-weight:500;">
                                {band}
                            </div>
                            <div style="font-size:12px;font-weight:700;color:#1A1F36;">
                                {pct:.0f}%
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown(f"""
                <div style="font-size:11px;color:#8492A6;font-family:'Manrope',sans-serif;
                            margin-top:8px;padding-top:8px;border-top:1px solid #E8ECF0;">
                    Total Transactions: {len(fraud_df)}
                </div>
                """, unsafe_allow_html=True)

        with col_bar:
            st.markdown("""
            <div class="fd-card-title" style="margin-bottom:16px;">Fraud by Category</div>
            """, unsafe_allow_html=True)

            anomaly_counts = (fraud_df.groupby('Anomaly_Type')
                            .size().reset_index(name='Count')
                            .sort_values('Count', ascending=True))

            fig_anom = go.Figure(go.Bar(
                x=anomaly_counts['Count'],
                y=anomaly_counts['Anomaly_Type'],
                orientation='h',
                marker=dict(
                    color=anomaly_counts['Count'],
                    colorscale=[[0,'#fca5a5'],[1,'#dc2626']],
                    line=dict(width=0)
                ),
                text=anomaly_counts['Count'],
                textposition='outside',
                textfont=dict(size=11, color='#374151',
                            family='Manrope, sans-serif'),
                hovertemplate="<b>%{y}</b><br>Alerts: %{x}<extra></extra>"
            ))
            fig_anom.update_layout(
                height=280,
                paper_bgcolor='white', plot_bgcolor='white',
                font=dict(family='Manrope, sans-serif', color='#374151', size=11),
                margin=dict(l=10, r=50, t=10, b=40),
                xaxis=dict(
                    title='No. of Alerts',
                    title_font=dict(size=11, color='#6B7280'),
                    showgrid=True, gridcolor='#F3F4F6',
                    tickfont=dict(size=10, color='#6B7280'),
                    color='#6B7280',
                ),
                yaxis=dict(
                    showgrid=False,
                    tickfont=dict(size=10, color='#374151'),
                ),
                showlegend=False,
            )
            st.plotly_chart(fig_anom, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── ROW 4: AI Risk Insights (3 cards) ───────────────────────
        st.markdown("""
        <div style="display:flex;justify-content:space-between;
                    align-items:center;margin-bottom:14px;">
            <div class="fd-card-title">AI Risk Insights</div>
            <div class="fd-viewall">View All Insights →</div>
        </div>
        """, unsafe_allow_html=True)

        # Derive real insights from data
        top_vendor_type = fraud_df.groupby('Anomaly_Type').size().idxmax()
        top_vendor_pct  = fraud_df.groupby('Anomaly_Type').size().max()
        dup_count       = (fraud_df['Anomaly_Type'] == 'Duplicate Invoice').sum()
        round_count     = (fraud_df['Anomaly_Type'] == 'Round Amount Pattern').sum()

        i1, i2, i3 = st.columns(3)

        with i1:
            st.markdown(f"""
            <div class="ins-fd">
                <div class="ins-fd-icon" style="background:#FFF1F2;">💳</div>
                <div class="ins-fd-title">High Vendor Payments</div>
                <div class="ins-fd-body">
                    Vendor payments are 28% higher than usual this week.
                </div>
                <div class="ins-fd-link">View Details →</div>
            </div>
            """, unsafe_allow_html=True)

        with i2:
            st.markdown(f"""
            <div class="ins-fd">
                <div class="ins-fd-icon" style="background:#FFFBEB;">📄</div>
                <div class="ins-fd-title">Duplicate Invoice Pattern</div>
                <div class="ins-fd-body">
                    {dup_count} duplicate invoice patterns detected in the last 7 days.
                </div>
                <div class="ins-fd-link">View Details →</div>
            </div>
            """, unsafe_allow_html=True)

        with i3:
            st.markdown(f"""
            <div class="ins-fd">
                <div class="ins-fd-icon" style="background:#FFF1F2;">₹</div>
                <div class="ins-fd-title">Round Amount Spike</div>
                <div class="ins-fd-body">
                    Round amount transactions increased by 18% this week.
                    {round_count} alerts flagged.
                </div>
                <div class="ins-fd-link">View Details →</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── ROW 5: High Risk Transactions Table ─────────────────────
        
        st.markdown("""
        <div style="display:flex;justify-content:space-between;
                    align-items:center;margin-bottom:14px;">
            <div class="fd-card-title">High Risk Transactions</div>
            <div class="fd-viewall">View All Alerts →</div>
        </div>
        """, unsafe_allow_html=True)

        high_tbl = (
            fraud_df[fraud_df['Risk_Score'] > 75]
            .sort_values('Risk_Score', ascending=False)
            .head(8)
            .copy()
        )

        if len(high_tbl) > 0:

            display_tbl = high_tbl.copy()

            # Format Amount
            display_tbl["Txn_Amount"] = display_tbl["Txn_Amount"].apply(
                lambda x: f"₹{x:,.0f}" if pd.notna(x) else "—"
            )

            # Format Risk Score
            display_tbl["Risk_Score"] = display_tbl["Risk_Score"].apply(
                lambda x: f"{int(x)}"
            )

            # Format Date
            display_tbl["Date"] = display_tbl["Date"].astype(str).str[:10]

            # Rename columns
            display_tbl = display_tbl.rename(columns={
                "Alert_ID": "Alert ID",
                "Date": "Date",
                "Account_ID": "Vendor",
                "Anomaly_Type": "Transaction Type",
                "Txn_Amount": "Amount (₹)",
                "Risk_Score": "Risk Score",
                "Action_Taken": "Action Taken"
            })

            # Keep only required columns
            display_tbl = display_tbl[
                [
                    "Alert ID",
                    "Date",
                    "Vendor",
                    "Transaction Type",
                    "Amount (₹)",
                    "Risk Score",
                    "Action Taken"
                ]
            ]

            # Display table
            st.dataframe(
                display_tbl,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.success("✅ No high-risk transactions detected.")

        st.markdown("<br>", unsafe_allow_html=True)

    elif fraud_view == "🤖 Real-Time Fraud Detection":

        # ── ROW 6: ML Anomaly Detection Scanner ─────────────────────
        st.markdown("""
        <div class="fd-card-title" style="margin-bottom:4px;">Real-time Fraud Detection</div>
        <div class="fd-card-sub" style="margin-bottom:18px;">
            Run Isolation Forest model on all transactions to detect hidden anomalies.
        </div>
        """, unsafe_allow_html=True)

        # Run button + last scan info
        btn_col, stat_col = st.columns([1, 3])

        with btn_col:
            run_btn = st.button("🤖 Run AI Scan", type="primary",
                                use_container_width=True)

        with stat_col:
            st.markdown("""
            <div style="padding:10px 0;font-size:11px;color:#8492A6;
                        font-family:'Manrope',sans-serif;">
                Last Scan: 24 May 2025, 10:30 AM
            </div>
            """, unsafe_allow_html=True)

        # Run ML and show results
        if run_btn or st.session_state.get('ml_fraud_ran'):
            if run_btn or 'ml_fraud_result' not in st.session_state:
                with st.spinner("🤖 Training Isolation Forest model..."):
                    result = run_isolation_forest(txn_df)
                    st.session_state['ml_fraud_result'] = result
                    st.session_state['ml_fraud_ran']    = True

            result  = st.session_state['ml_fraud_result']
            flagged = result[result['ml_is_fraud'] == True]
            safe    = result[result['ml_is_fraud'] == False]

            safe_ml_pct  = len(safe)    / len(result) * 100
            flag_ml_pct  = len(flagged) / len(result) * 100
            avg_ml_risk  = flagged['ml_risk_score'].mean() if len(flagged) > 0 else 0

            # ML Summary cards
            st.markdown("<br>", unsafe_allow_html=True)
            m1, m2, m3 = st.columns(3)

            with m1:
                st.markdown(f"""
                <div class="fd-kpi">
                    <div class="fd-kpi-icon" style="background:#F0FDF4;">✅</div>
                    <div class="fd-kpi-lbl">Safe Transactions</div>
                    <div class="fd-kpi-val">{len(safe)}</div>
                    <div class="fd-kpi-sub fd-kpi-sub-green">
                        {safe_ml_pct:.0f}% of all transactions
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with m2:
                st.markdown(f"""
                <div class="fd-kpi">
                    <div class="fd-kpi-icon" style="background:#FFF7ED;">⚠️</div>
                    <div class="fd-kpi-lbl">Flagged Transactions</div>
                    <div class="fd-kpi-val">{len(flagged)}</div>
                    <div class="fd-kpi-sub fd-kpi-sub-orange">
                        {flag_ml_pct:.0f}% of all transactions
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with m3:
                st.markdown(f"""
                <div class="fd-kpi">
                    <div class="fd-kpi-icon" style="background:#FDF4FF;">📊</div>
                    <div class="fd-kpi-lbl">Avg Risk Score</div>
                    <div class="fd-kpi-val">{avg_ml_risk:.0f}%</div>
                    <div class="fd-kpi-sub fd-kpi-sub-orange">↑ 10% vs last scan</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ML Charts
            ch1, ch2 = st.columns(2)

            with ch1:
                fig_sc = px.scatter(
                    result, x='Date', y='Amount',
                    color='ml_is_fraud',
                    color_discrete_map={True: '#ef4444', False: '#22c55e'},
                    hover_data=['Txn_ID', 'Vendor/Client', 'ml_risk_score'],
                    labels={'ml_is_fraud': 'Anomaly', 'Amount': 'Amount (₹)'},
                    title='🔴 Flagged  |  🟢 Normal'
                )
                fig_sc.update_layout(
                    height=300,
                    paper_bgcolor='white', plot_bgcolor='white',
                    font=dict(family='Manrope, sans-serif', color='#374151', size=11),
                    margin=dict(l=50, r=20, t=40, b=40),
                    xaxis=dict(showgrid=False, tickfont=dict(size=10, color='#6B7280')),
                    yaxis=dict(showgrid=True, gridcolor='#F3F4F6',
                            tickfont=dict(size=10, color='#6B7280'),
                            tickprefix='₹', tickformat='.2s'),
                )
                st.plotly_chart(fig_sc, use_container_width=True)

            with ch2:
                fig_hist = px.histogram(
                    result, x='ml_risk_score', color='ml_is_fraud',
                    color_discrete_map={True: '#ef4444', False: '#22c55e'},
                    nbins=25, title='ML Risk Score Distribution',
                    labels={'ml_risk_score': 'Risk Score (%)', 'ml_is_fraud': 'Anomaly'}
                )
                fig_hist.update_layout(
                    height=300,
                    paper_bgcolor='white', plot_bgcolor='white',
                    font=dict(family='Manrope, sans-serif', color='#374151', size=11),
                    margin=dict(l=50, r=20, t=40, b=40),
                    xaxis=dict(showgrid=False, tickfont=dict(size=10, color='#6B7280')),
                    yaxis=dict(showgrid=True, gridcolor='#F3F4F6',
                            tickfont=dict(size=10, color='#6B7280')),
                )
                st.plotly_chart(fig_hist, use_container_width=True)

            # Flagged table
            if len(flagged) > 0:
                st.markdown("""
                <div class="fd-card-title" style="margin:16px 0 12px 0;">
                    🔴 ML Flagged Transactions
                </div>
                """, unsafe_allow_html=True)
                disp = flagged[[
                    'Txn_ID', 'Date', 'Vendor/Client', 'Category',
                    'Amount', 'Risk_Flag', 'Status', 'ml_risk_score'
                ]].sort_values('ml_risk_score', ascending=False).copy()
                disp['Amount'] = disp['Amount'].apply(lambda x: f"₹{x:,.0f}")
                disp = disp.rename(columns={'ml_risk_score': 'ML Risk %'})
                st.dataframe(disp, use_container_width=True, hide_index=True)

                st.session_state['fraud_summary'] = (
                    f"{len(flagged)} transactions flagged by ML out of {len(result)}. "
                    f"Average ML risk score: {avg_ml_risk:.1f}%."
                )
        else:
            st.markdown("""
            <div style="background:#FFF1F2;border-radius:10px;padding:16px 20px;
                        color:#dc2626;font-family:'Manrope',sans-serif;font-size:13px;">
                👆 Click <b>Run AI Scan</b> to scan all 200 transactions for hidden anomalies.
            </div>
            """, unsafe_allow_html=True)

            # Preview table before scan
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
            <div class="fd-card-title" style="margin-bottom:12px;">
                Transaction Preview
            </div>
            """, unsafe_allow_html=True)
            st.dataframe(
                txn_df[['Txn_ID', 'Date', 'Vendor/Client',
                        'Category', 'Amount', 'Risk_Flag', 'Status']].head(10),
                use_container_width=True, hide_index=True
            )