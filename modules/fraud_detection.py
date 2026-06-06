import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


def run_isolation_forest(df):
    """
    Runs Isolation Forest on financial_transactions data
    to find additional anomalies beyond the pre-labeled ones.
    Returns df with added ml_risk_score and ml_is_fraud columns.
    """
    df = df.copy().reset_index(drop=True)

    features = pd.DataFrame({
        'amount':       df['Amount'].values,
        'days_overdue': pd.to_numeric(df['Days_Overdue'], errors='coerce').fillna(0).values,
        'gst_rate':     pd.to_numeric(df['GST_Rate'], errors='coerce').fillna(0).values,
    })

    scaler      = StandardScaler()
    X           = scaler.fit_transform(features)
    model       = IsolationForest(contamination=0.08, random_state=42, n_estimators=100)
    model.fit(X)

    preds       = model.predict(X)
    raw         = model.score_samples(X)
    df['ml_risk_score'] = ((raw - raw.max()) / (raw.min() - raw.max()) * 100).round(1)
    df['ml_is_fraud']   = preds == -1
    return df


def show():
    st.title("🚨 Fraud & Anomaly Detection")
    st.markdown("*AI-powered transaction monitoring using Isolation Forest + pre-labeled risk data*")
    st.markdown("---")

    # ── Get data ──────────────────────────────────────────
    fraud_df = st.session_state.get('fraud_data')         # Fraud_Anomaly_Detection sheet
    txn_df   = st.session_state.get('financial_transactions')  # Financial_Transactions sheet

    if fraud_df is None or txn_df is None:
        st.warning("⚠️ Data not loaded. Please run generate_data.py first.")
        return

    # ── TABS: two views ───────────────────────────────────
    tab1, tab2 = st.tabs(["🔴 Pre-labeled Fraud Alerts", "🤖 ML Anomaly Scanner"])

    # ════════════════════════════════════════════════════
    # TAB 1 — Pre-labeled Fraud Alerts (from Excel sheet)
    # ════════════════════════════════════════════════════
    with tab1:
        st.subheader("Fraud Alerts from Dataset")

        confirmed = fraud_df[fraud_df['is_fraud'] == True]
        suspected = fraud_df[fraud_df['is_fraud'] == False]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Alerts",      len(fraud_df))
        c2.metric("🔴 Confirmed Fraud", len(confirmed))
        c3.metric("🟡 Suspected",       len(suspected))
        c4.metric("Avg Risk Score",     f"{fraud_df['Risk_Score'].mean():.1f}/100")

        st.markdown("---")

        # Risk Score distribution
        col1, col2 = st.columns(2)
        with col1:
            fig = px.histogram(
                fraud_df, x='Risk_Score', color='ML_Prediction',
                nbins=20, title="Risk Score Distribution",
                color_discrete_map={'FRAUD': '#FF4B4B', 'LEGITIMATE': '#00C49A'},
                labels={'Risk_Score': 'Risk Score (0-100)', 'ML_Prediction': 'Prediction'}
            )
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=320)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig2 = px.scatter(
                fraud_df, x='Txn_Amount', y='Risk_Score',
                color='ML_Prediction', hover_data=['Alert_ID', 'Anomaly_Type', 'Action_Taken'],
                title="Transaction Amount vs Risk Score",
                color_discrete_map={'FRAUD': '#FF4B4B', 'LEGITIMATE': '#00C49A'},
                labels={'Txn_Amount': 'Transaction Amount (₹)', 'Risk_Score': 'Risk Score'}
            )
            fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=320)
            st.plotly_chart(fig2, use_container_width=True)

        # Anomaly Type breakdown
        anomaly_counts = fraud_df.groupby('Anomaly_Type').size().reset_index(name='Count')
        fig3 = px.bar(
            anomaly_counts.sort_values('Count', ascending=False),
            x='Anomaly_Type', y='Count', color='Count',
            color_continuous_scale='Reds', title="Fraud by Anomaly Type"
        )
        fig3.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                           height=280, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

        st.markdown("---")
        st.subheader("🔴 Confirmed Fraud Cases")
        if len(confirmed) > 0:
            disp = confirmed[[
                'Alert_ID', 'Date', 'Account_ID', 'Txn_Amount',
                'Anomaly_Type', 'Risk_Score', 'Action_Taken', 'Resolved'
            ]].sort_values('Risk_Score', ascending=False).copy()
            disp['Txn_Amount'] = disp['Txn_Amount'].apply(lambda x: f"₹{x:,.0f}")
            st.dataframe(disp, use_container_width=True, hide_index=True)

            csv = confirmed.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Fraud Cases CSV", csv,
                               'confirmed_fraud.csv', 'text/csv')

    # ════════════════════════════════════════════════════
    # TAB 2 — ML Isolation Forest on transactions
    # ════════════════════════════════════════════════════
    with tab2:
        st.subheader("ML Anomaly Detection on Financial Transactions")
        st.markdown("Runs **Isolation Forest** on the 200 financial transactions to find additional anomalies.")

        run_btn = st.button("🔍 Run ML Detection", type="primary")

        if run_btn or st.session_state.get('ml_fraud_ran'):
            if run_btn or 'ml_fraud_result' not in st.session_state:
                with st.spinner("Training Isolation Forest model..."):
                    result = run_isolation_forest(txn_df)
                    st.session_state['ml_fraud_result'] = result
                    st.session_state['ml_fraud_ran']    = True

            result    = st.session_state['ml_fraud_result']
            flagged   = result[result['ml_is_fraud'] == True]
            safe      = result[result['ml_is_fraud'] == False]

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Transactions", len(result))
            c2.metric("✅ Safe",             len(safe))
            c3.metric("🔴 Flagged",          len(flagged))
            c4.metric("Avg Risk Score",      f"{flagged['ml_risk_score'].mean():.1f}%"
                                             if len(flagged) > 0 else "0%")

            st.markdown("---")

            col1, col2 = st.columns(2)
            with col1:
                fig = px.scatter(
                    result, x='Date', y='Amount',
                    color='ml_is_fraud',
                    color_discrete_map={True: '#FF4B4B', False: '#00C49A'},
                    hover_data=['Txn_ID', 'Vendor/Client', 'ml_risk_score'],
                    title="🔴 Flagged  |  🟢 Normal",
                    labels={'ml_is_fraud': 'Anomaly', 'Amount': 'Amount (₹)'}
                )
                fig.update_layout(plot_bgcolor='rgba(0,0,0,0)',
                                  paper_bgcolor='rgba(0,0,0,0)', height=320)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                fig2 = px.histogram(
                    result, x='ml_risk_score', color='ml_is_fraud',
                    color_discrete_map={True: '#FF4B4B', False: '#00C49A'},
                    nbins=25, title="ML Risk Score Distribution",
                    labels={'ml_risk_score': 'Risk Score (%)', 'ml_is_fraud': 'Anomaly'}
                )
                fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)',
                                   paper_bgcolor='rgba(0,0,0,0)', height=320)
                st.plotly_chart(fig2, use_container_width=True)

            if len(flagged) > 0:
                st.subheader("🔴 Flagged Transactions")
                disp = flagged[[
                    'Txn_ID', 'Date', 'Vendor/Client', 'Category',
                    'Amount', 'Risk_Flag', 'Status', 'ml_risk_score'
                ]].sort_values('ml_risk_score', ascending=False).copy()
                disp['Amount'] = disp['Amount'].apply(lambda x: f"₹{x:,.0f}")
                st.dataframe(disp.rename(columns={'ml_risk_score': 'ML Risk %'}),
                             use_container_width=True, hide_index=True)

                # Store summary for AI assistant
                st.session_state['fraud_summary'] = (
                    f"{len(flagged)} transactions flagged by ML out of {len(result)}. "
                    f"Average ML risk score: {flagged['ml_risk_score'].mean():.1f}%."
                )
        else:
            st.info("👆 Click **Run ML Detection** to scan transactions.")
            st.dataframe(
                txn_df[['Txn_ID', 'Date', 'Vendor/Client', 'Category',
                        'Amount', 'Risk_Flag', 'Status']].head(10),
                use_container_width=True, hide_index=True
            )