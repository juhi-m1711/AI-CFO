# Import required libraries
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

#-----------------------------------------------
#----FRAUD DETECTION MACHINE LEARNING MODEL-----
#-----------------------------------------------

def run_fraud_detection(df):
    """
    Runs Isolation Forest on transaction data.
    Adds 3 new columns to the dataframe:
      - anomaly_score : raw score (lower = more suspicious)
      - risk_score    : 0–100% risk (higher = more suspicious)
      - is_fraud      : True / False flag
    """
    #-------------------CREATING COPY OF THE DATA-------------------------------------------------
    df = df.copy()

    #--------------------BUILDING FEATURES FOR THE MODEL-------------------------------------------
    # Build features for the model
    # Using amount, type, and category from sample_transactions

    features = pd.DataFrame()
    features['amount'] = df["amount"]

    #--------------------ENCODING CATEGORICAL FEATURES INTO NUMERICAL FEATURES----------------------
    # Encoding category and type column to numerical column for better ML model

    features = pd.get_dummies(
    features,
    columns=['category', 'type'],
    drop_first=True
    )

    #--------------------SCALING TO NORMALIZE----------------------------------------------------
    # Scale features so amount does not dominate

    scaler = StandardScaler()
    X = scaler.fit_transform(features)

    #---------------------CREATE ISOLATION FOREST MODEL-------------------------------------------
    # Train Isolation Forest Model
    # contamination = expected % of fraud in data (5%)
    
    # Build the model
    model = IsolationForest(
        contamination=0.05,
        n_estimators=100,
        random_state=42
    )

    # Train the model 
    model.fit(X)

    #----------------------PREDICTIONS & SCORING----------------------------------------------------
    df['anamoly'] = model.predict(X)   # 1 = Normal | -1 = Fraud
    raw_scores = model.score_samples(X) # more negative = more anamolous

    # Convert raw score to 0–100% risk score
    # Flip so higher % = higher risk
    min_s, max_s        = raw_scores.min(), raw_scores.max()
    df['risk_score']    = ((raw_scores - max_s) / (min_s - max_s) * 100).round(1)
    df['is_fraud']      = df['anomaly'] == -1
 
    return df


#-----------------------------------------------------------------------------------------------------
#--------------------------REASON GENERATOR-----------------------------------------------------------
#-----------------------------------------------------------------------------------------------------

def get_fraud_reason(row, df):
    """
    Gives a human-readable reason why a transaction was flagged.
    """
    reasons =[]

    # Check if amount is unusually high
    mean_amt = df['amount'].mean()
    std_amt = df['amount'].std()

    if row['amount'] > mean_amt + 2 * std_amt:
        reasons.append("Unusually high amount")

    # Check if amount is suspiciously round number
    if row["amount"] % 100000 == 0:
        reasons.append("Suspiciously round number")

    # Check for duplicate amount
    duplicates = df[df['amount'] == row['amount']]
    if len(duplicates) > 2:
        reasons.append("Duplicate amount detected")

    # Check category mismatch (high credit in expense category)
    if row['type'] == 'credit' and row['category'] in ['Rent', 'Tax', 'Utilities']:
        reasons.append("Unusual credit in expense category")

    return ", ".join(reasons) if reasons else 'Statistical Anamoly'


#----------------------------------------------------------------------------------------------
#-----------------------MAIN PAGE FUNCTION (STREAMLIT)-----------------------------------------------------
#----------------------------------------------------------------------------------------------

def show():
    st.title("🚨 Fraud & Anomaly Detection")
    st.markdown("*AI-powered transaction monitoring using Isolation Forest*")
    st.markdown("---")
 
    # ── Get data from session state ──
    df = st.session_state.get('transactions')
 
    if df is None:
        st.warning("⚠️ No transaction data found. Please upload data first.")
        return
 
    # ── TOP SECTION: Info + Run Button ──
    col1, col2 = st.columns([2, 1])
 
    with col1:
        st.markdown("""
        **How it works:**
        - Loads your transaction data
        - Trains an ML model (Isolation Forest) on the spot
        - Flags transactions that look statistically unusual
        - Shows you exactly which ones to investigate
        """)
 
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        run_button = st.button(
            "🔍 Run Fraud Detection",
            use_container_width=True,
            type="primary"
        )
 
    st.markdown("---")
 
    # ── RUN MODEL when button clicked ──
    if run_button or st.session_state.get('fraud_ran'):
 
        # Run only once, store result in session
        if run_button or 'fraud_result' not in st.session_state:
            with st.spinner("🤖 Training model and scanning transactions..."):
                result_df = run_fraud_detection(df)
 
                # Add fraud reasons
                result_df['reason'] = result_df.apply(
                    lambda row: get_fraud_reason(row, result_df)
                    if row['is_fraud'] else "—",
                    axis=1
                )
                st.session_state['fraud_result'] = result_df
                st.session_state['fraud_ran']    = True
 
        result_df = st.session_state['fraud_result']
 
        # Split into fraud and normal
        fraud_df  = result_df[result_df['is_fraud'] == True].copy()
        normal_df = result_df[result_df['is_fraud'] == False].copy()
 
        # ── SUMMARY CARDS ──
        st.subheader("📊 Detection Summary")
        c1, c2, c3, c4 = st.columns(4)
 
        with c1:
            st.metric(
                label="Total Transactions",
                value=f"{len(result_df):,}"
            )
        with c2:
            st.metric(
                label="✅ Safe",
                value=f"{len(normal_df):,}",
                delta=f"{(len(normal_df)/len(result_df)*100):.1f}%"
            )
        with c3:
            st.metric(
                label="🔴 Flagged",
                value=f"{len(fraud_df):,}",
                delta=f"-{(len(fraud_df)/len(result_df)*100):.1f}%",
                delta_color="inverse"
            )
        with c4:
            avg_risk = fraud_df['risk_score'].mean() if len(fraud_df) > 0 else 0
            st.metric(
                label="Avg Risk Score",
                value=f"{avg_risk:.1f}%"
            )
 
        st.markdown("---")
 
        # ── CHARTS ROW ──
        st.subheader("📈 Visual Analysis")
        chart_col1, chart_col2 = st.columns(2)
 
        # Chart 1: Scatter Plot — Amount vs Date
        with chart_col1:
            st.markdown("**Transaction Amount vs Date**")
            fig_scatter = px.scatter(
                result_df,
                x='date',
                y='amount',
                color='is_fraud',
                color_discrete_map={
                    True:  '#FF4B4B',   # red for fraud
                    False: '#00C49A'    # green for normal
                },
                labels={
                    'is_fraud': 'Fraud',
                    'amount':   'Amount (₹)',
                    'date':     'Date'
                },
                hover_data=['txn_id', 'category', 'risk_score'],
                title="🔴 Flagged  |  🟢 Normal"
            )
            fig_scatter.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=True,
                height=350
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
 
        # Chart 2: Risk Score Distribution
        with chart_col2:
            st.markdown("**Risk Score Distribution**")
            fig_hist = px.histogram(
                result_df,
                x='risk_score',
                color='is_fraud',
                color_discrete_map={
                    True:  '#FF4B4B',
                    False: '#00C49A'
                },
                nbins=30,
                labels={
                    'risk_score': 'Risk Score (%)',
                    'is_fraud':   'Fraud'
                },
                title="Distribution of Risk Scores"
            )
            fig_hist.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=350
            )
            st.plotly_chart(fig_hist, use_container_width=True)
 
        # Chart 3: Fraud by Category bar chart
        st.markdown("**Fraud Count by Category**")
        fraud_by_cat = (
            fraud_df.groupby('category')
            .size()
            .reset_index(name='count')
            .sort_values('count', ascending=False)
        )
        fig_bar = px.bar(
            fraud_by_cat,
            x='category',
            y='count',
            color='count',
            color_continuous_scale='Reds',
            labels={'category': 'Category', 'count': 'Flagged Count'},
            title="Which categories have the most anomalies?"
        )
        fig_bar.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=300,
            showlegend=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)
 
        st.markdown("---")
 
        # ── FLAGGED TRANSACTIONS TABLE ──
        st.subheader("🔴 Flagged Transactions — Investigate These")
 
        if len(fraud_df) > 0:
            # Sort by risk score highest first
            fraud_display = fraud_df[[
                'txn_id', 'date', 'category',
                'type', 'amount', 'risk_score', 'reason'
            ]].sort_values('risk_score', ascending=False).copy()
 
            # Format columns
            fraud_display['amount']     = fraud_display['amount'].apply(
                                            lambda x: f"₹{x:,.0f}")
            fraud_display['risk_score'] = fraud_display['risk_score'].apply(
                                            lambda x: f"{x:.1f}%")
            fraud_display['date']       = fraud_display['date'].astype(str)
 
            # Color code risk score column
            st.dataframe(
                fraud_display.rename(columns={
                    'txn_id':     'Transaction ID',
                    'date':       'Date',
                    'category':   'Category',
                    'type':       'Type',
                    'amount':     'Amount',
                    'risk_score': 'Risk Score',
                    'reason':     'Reason Flagged'
                }),
                use_container_width=True,
                hide_index=True
            )
 
            # Download button for flagged transactions
            csv = fraud_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Flagged Transactions CSV",
                data=csv,
                file_name='flagged_transactions.csv',
                mime='text/csv'
            )
 
        else:
            st.success("✅ No fraudulent transactions detected!")
 
        st.markdown("---")
 
        # ── AI INSIGHT BOX ──
        st.subheader("💡 Quick Insights")
        total        = len(result_df)
        fraud_count  = len(fraud_df)
        fraud_pct    = (fraud_count / total * 100)
        top_category = (fraud_by_cat.iloc[0]['category']
                        if len(fraud_by_cat) > 0 else "N/A")
        top_amount   = fraud_df['amount'].max() if len(fraud_df) > 0 else 0
 
        if fraud_pct > 10:
            risk_level = "🔴 High Risk"
            advice     = "Immediate review recommended."
        elif fraud_pct > 5:
            risk_level = "🟡 Medium Risk"
            advice     = "Monitor closely over next 30 days."
        else:
            risk_level = "🟢 Low Risk"
            advice     = "Financials look healthy."
 
        st.info(f"""
        **Fraud Analysis Summary:**
 
        - **{fraud_count}** out of **{total}** transactions flagged ({fraud_pct:.1f}%)
        - Most suspicious category: **{top_category}**
        - Highest flagged amount: **₹{top_amount:,.0f}**
        - Overall risk level: **{risk_level}**
        - Recommendation: {advice}
        """)
 
        # Store fraud summary in session for AI assistant
        st.session_state['fraud_summary'] = (
            f"{fraud_count} transactions flagged out of {total} "
            f"({fraud_pct:.1f}%). Most suspicious category: {top_category}. "
            f"Highest flagged amount: ₹{top_amount:,.0f}. "
            f"Risk level: {risk_level}."
        )
 
    else:
        # Before button is clicked — show placeholder
        st.info("👆 Click **Run Fraud Detection** to scan your transactions.")
 
        # Show sample of raw data so page isn't empty
        st.subheader("📋 Transaction Data Preview")
        st.dataframe(
            df.head(10)[[
                'txn_id', 'date', 'category', 'type', 'amount'
            ]],
            use_container_width=True,
            hide_index=True
        )