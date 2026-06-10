"""
preprocessor.py  —  cleans loaded dataframes + builds AI summary
"""
import pandas as pd


def get_summary_for_ai(session):
    """
    Builds a short text summary injected into Gemini system prompt
    so AI Assistant answers using real data.
    """
    parts = []

    # Financial Intelligence
    fin = session.get('financial_intelligence')
    if fin is not None and not fin.empty:
        latest = fin.iloc[-1]
        parts.append(
            f"Financials (latest month {latest.get('month_label','')}):"
            f" Revenue ₹{latest['Revenue']:,.0f},"
            f" Net Profit ₹{latest['Net_Profit']:,.0f},"
            f" Profit Margin {latest['Profit_Margin']:.1f}%,"
            f" Cash Flow ₹{latest['Cash_Flow']:,.0f}."
        )

    # GST
    gst = session.get('gst_data')
    if gst is not None and not gst.empty:
        total   = len(gst)
        filed   = (gst['Status'].str.lower() == 'filed').sum()
        pending = (gst['Status'].str.lower() == 'pending').sum()
        overdue = (gst['Status'].str.lower() == 'overdue').sum()
        penalty = gst['Penalty'].sum()
        score   = round((filed / total) * 100, 1)
        parts.append(
            f"GST: {total} filings — {filed} filed, {pending} pending,"
            f" {overdue} overdue. Compliance score {score}%."
            f" Total penalties ₹{penalty:,.0f}."
        )

    # Compliance
    comp = session.get('compliance_data')
    if comp is not None and not comp.empty:
        overdue_comp = (comp['Status'].str.lower() == 'overdue').sum()
        total_penalty_risk = comp['Penalty_Risk'].sum()
        parts.append(
            f"Compliance: {overdue_comp} overdue items,"
            f" total penalty risk ₹{total_penalty_risk:,.0f}."
        )

    # Payroll
    pay = session.get('payroll_data')
    if pay is not None and not pay.empty:
        employees  = pay['Emp_ID'].nunique()
        total_ctc  = pay['CTC'].sum()
        unpaid     = (pay['Payment_Status'].str.lower() == 'pending').sum()
        parts.append(
            f"Payroll: {employees} employees, total CTC ₹{total_ctc:,.0f},"
            f" {unpaid} pending payments."
        )

    return " | ".join(parts) if parts else "No data loaded."