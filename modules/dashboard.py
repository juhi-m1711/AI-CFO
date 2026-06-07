"""
AI-Powered Accounting Platform — Dashboard
===========================================
Fixed version — works with AI_Accounting_Platform_Dataset.xlsx
Place this file inside your project root (same level as data/ folder)

Run  : streamlit run modules/dashboard.py   ← if used as Streamlit module
  OR : python dashboard.py                  ← if run standalone with Dash
Open : http://127.0.0.1:8050
"""

# ── imports ──────────────────────────────────────────────────────────────────
import pathlib, pandas as pd, numpy as np
from dash import Dash, html, dcc
import plotly.graph_objects as go
import plotly.express as px

# ── load data ─────────────────────────────────────────────────────────────────
# FIX 1: Correct path — looks for Excel inside data/ folder
BASE = pathlib.Path(__file__).parent
# Try data/ subfolder first, then same folder (works both as module and standalone)
XLSX = BASE / "data" / "AI_Accounting_Platform_Dataset.xlsx"
if not XLSX.exists():
    XLSX = BASE / "AI_Accounting_Platform_Dataset.xlsx"
if not XLSX.exists():
    XLSX = BASE.parent / "data" / "AI_Accounting_Platform_Dataset.xlsx"

xls        = pd.ExcelFile(XLSX)
txn        = pd.read_excel(xls, "Financial_Transactions",  header=1)
gst        = pd.read_excel(xls, "GST_Tax_Management",      header=1)
fraud      = pd.read_excel(xls, "Fraud_Anomaly_Detection", header=1)
payroll    = pd.read_excel(xls, "Payroll_Management",      header=1)
fin        = pd.read_excel(xls, "Financial_Intelligence",  header=1)
compliance = pd.read_excel(xls, "Compliance_Tracking",     header=1)

# ── clean column names (strip whitespace) ─────────────────────────────────────
for df in [txn, gst, fraud, payroll, fin, compliance]:
    df.columns = df.columns.str.strip()

# ── numeric helpers ───────────────────────────────────────────────────────────
def to_num(s):
    return pd.to_numeric(
        s.astype(str).str.replace('%', '').str.replace(',', '').str.strip(),
        errors='coerce'
    )

# FIX 2: Parse numeric columns correctly
fin["Profit_Margin_num"]     = to_num(fin["Profit_Margin (%)"])
fin["YoY_num"]               = to_num(fin["YoY_Growth (%)"])
gst["Compliance_Score_num"]  = to_num(gst["Compliance_Score"])

# FIX 3: Ensure money columns are numeric
for col in ["Amount (₹)", "GST_Amt (₹)", "Total (₹)"]:
    txn[col] = to_num(txn[col])

for col in ["CGST (₹)", "SGST (₹)", "IGST (₹)", "Total_GST (₹)", "Penalty (₹)"]:
    gst[col] = to_num(gst[col])

for col in ["Txn_Amount (₹)", "Avg_Txn_Amt (₹)", "Risk_Score (0-100)"]:
    fraud[col] = to_num(fraud[col])

for col in ["Net_Salary (₹)", "Gross_Salary (₹)", "Basic_Salary (₹)",
            "HRA (₹)", "Allowances (₹)", "PF_Deduction (₹)", "TDS (₹)"]:
    payroll[col] = to_num(payroll[col])

for col in ["Revenue (₹)", "COGS (₹)", "Gross_Profit (₹)",
            "Operating_Expenses (₹)", "EBITDA (₹)",
            "Net_Profit (₹)", "Cash_Flow (₹)", "Burn_Rate (₹)"]:
    fin[col] = to_num(fin[col])

# FIX 4: Penalty_Risk column
compliance["Penalty_Risk (₹)"] = to_num(compliance["Penalty_Risk (₹)"])

# ── design tokens ─────────────────────────────────────────────────────────────
BG     = "#060B18"
CARD   = "#0F1629"
CARD2  = "#151C35"
BORDER = "#1E2645"
ACCENT = "#3B82F6"
GREEN  = "#10B981"
RED    = "#EF4444"
ORANGE = "#F59E0B"
CYAN   = "#06B6D4"
VIOLET = "#8B5CF6"
TEXT   = "#F1F5F9"
MUTED  = "#64748B"
GRID   = "#162040"
FONT   = "'DM Sans', 'Segoe UI', sans-serif"
MONO   = "'JetBrains Mono', monospace"

CL = dict(
    plot_bgcolor  = "rgba(0,0,0,0)",
    paper_bgcolor = "rgba(0,0,0,0)",
    font          = dict(family=FONT, color=TEXT, size=11),
)

# ── pre-computed KPIs ─────────────────────────────────────────────────────────
total_revenue  = fin["Revenue (₹)"].sum()
total_expenses = fin["Operating_Expenses (₹)"].sum() + fin["COGS (₹)"].sum()
total_profit   = fin["Net_Profit (₹)"].sum()
cash_balance   = fin["Cash_Flow (₹)"].iloc[-1]
gst_penalty    = gst["Penalty (₹)"].sum()

# FIX 5: ML_Prediction is 'Fraudulent' not 'FRAUD'
fraud_high  = int((fraud["Risk_Score (0-100)"] > 75).sum())
fraud_total = len(fraud)

overdue_amt      = txn.loc[txn["Status"] == "Overdue", "Total (₹)"].sum()
compliance_ok    = int((compliance["Status"] == "Compliant").sum())
compliance_nc    = int((compliance["Status"] == "Non-Compliant").sum())
compliance_risk  = int((compliance["Status"] == "At Risk").sum())
compliance_pend  = int((compliance["Status"] == "Pending").sum())
gst_pen_c        = int((gst["Penalty (₹)"] > 0).sum())

# FIX 6: Resolved is 'Yes'/'No' strings
fraud_rev  = int((fraud["Resolved"] == "Yes").sum())
fraud_open = fraud_total - fraud_rev
avg_margin = fin["Profit_Margin_num"].mean()
best_month = fin.loc[fin["Revenue (₹)"].idxmax(), "Period"]

# ── helper: styled card ───────────────────────────────────────────────────────
def card(children, style=None):
    s = dict(background=CARD, border=f"1px solid {BORDER}",
             borderRadius="16px", padding="20px", height="100%")
    if style:
        s.update(style)
    return html.Div(children, style=s)

def badge(txt, bg, fg):
    return html.Span(txt, style=dict(
        fontSize="11px", padding="3px 10px", borderRadius="20px",
        background=bg + "28", color=fg, fontWeight="600",
        fontFamily=FONT, whiteSpace="nowrap"
    ))

# ── KPI card ──────────────────────────────────────────────────────────────────
def kpi_card(icon, title, value, sub, color, delta=None):
    delta_el = html.Div()
    if delta is not None and not np.isnan(delta):
        arrow  = "▲" if delta > 0 else "▼"
        dc     = GREEN if delta > 0 else RED
        delta_el = html.Div(
            f"{arrow} {abs(delta):.1f}% vs last month",
            style=dict(fontSize="11px", color=dc, marginTop="6px", fontFamily=FONT)
        )
    return html.Div([
        html.Div([
            html.Span(icon, style=dict(fontSize="22px")),
            html.Div([
                html.Div(title, style=dict(
                    fontSize="11px", color=MUTED,
                    textTransform="uppercase", letterSpacing="0.07em",
                    fontFamily=FONT, marginBottom="4px"
                )),
                html.Div(value, style=dict(
                    fontSize="24px", fontWeight="700",
                    color=color, fontFamily=FONT, lineHeight="1.1"
                )),
                html.Div(sub, style=dict(
                    fontSize="11px", color=MUTED,
                    fontFamily=FONT, marginTop="4px"
                )),
                delta_el,
            ]),
        ], style=dict(display="flex", gap="14px", alignItems="flex-start")),
        html.Div(style=dict(
            height="3px", borderRadius="2px",
            background=f"linear-gradient(90deg,{color},{color}44)",
            marginTop="14px"
        )),
    ], style=dict(
        background=CARD2, border=f"1px solid {color}44",
        borderRadius="14px", padding="18px",
        flex="1", minWidth="160px",
        boxShadow=f"0 0 24px {color}12",
    ))

# ════════════════════════════════════════════════════════════════
# CHARTS
# ════════════════════════════════════════════════════════════════

def chart_revenue_trend():
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=fin["Period"], y=fin["Revenue (₹)"],
        name="Revenue", mode="lines+markers",
        line=dict(color=ACCENT, width=2.5),
        marker=dict(size=5, color=ACCENT),
        fill="tozeroy", fillcolor="rgba(59,130,246,0.07)",
        hovertemplate="<b>%{x}</b><br>Revenue: ₹%{y:,.0f}<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=fin["Period"], y=fin["Net_Profit (₹)"],
        name="Net Profit", mode="lines+markers",
        line=dict(color=GREEN, width=2, dash="dot"),
        marker=dict(size=4, color=GREEN),
        hovertemplate="<b>%{x}</b><br>Profit: ₹%{y:,.0f}<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=fin["Period"], y=fin["Operating_Expenses (₹)"],
        name="Expenses", mode="lines",
        line=dict(color=ORANGE, width=1.8, dash="dash"),
        hovertemplate="<b>%{x}</b><br>Expenses: ₹%{y:,.0f}<extra></extra>"
    ))
    fig.update_layout(**CL,
        title=dict(text="Revenue vs Profit vs Expenses — Monthly",
                   font=dict(size=13, color=TEXT), x=0.01, xref="paper"),
        showlegend=True,
        legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h",
                    x=0.0, y=-0.32, xanchor="left", yanchor="top",
                    font=dict(size=11, color=TEXT)),
        margin=dict(l=50, r=16, t=50, b=90),
        xaxis=dict(gridcolor=GRID, tickangle=-40,
                   tickfont=dict(size=9), color=MUTED),
        yaxis=dict(gridcolor=GRID, tickfont=dict(size=9),
                   color=MUTED, tickprefix="₹"),
    )
    return fig


def chart_expense_donut():
    cats = txn.groupby("Category")["Amount (₹)"].sum().sort_values(ascending=False)
    slice_colors = ["#3B82F6", "#8B5CF6", "#10B981", "#F59E0B", "#06B6D4",
                    "#EF4444", "#EC4899", "#14B8A6", "#F97316", "#A3E635"]
    total_exp  = cats.sum()
    pcts       = (cats.values / total_exp * 100)
    text_labels = [f"{lbl}<br>{p:.1f}%" for lbl, p in zip(cats.index, pcts)]

    fig = go.Figure(go.Pie(
        labels=cats.index, values=cats.values, hole=0.52,
        marker=dict(colors=slice_colors[:len(cats)],
                    line=dict(color="#060B18", width=2)),
        text=text_labels, textinfo="text", textposition="outside",
        textfont=dict(size=10, color="#E2E8F0", family=FONT),
        automargin=True,
        hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}  (%{percent})<extra></extra>",
        direction="clockwise", rotation=15,
    ))
    fig.update_layout(**CL, showlegend=False,
                      margin=dict(l=80, r=80, t=30, b=30))
    return fig, total_exp


def chart_fraud_risk():
    # FIX 7: use correct label 'Fraudulent' not 'FRAUD'
    risk_counts = fraud["ML_Prediction"].value_counts()
    colors_map  = {"Fraudulent": RED, "Suspicious": ORANGE, "Legitimate": GREEN}
    cols = [colors_map.get(k, MUTED) for k in risk_counts.index]
    fig  = go.Figure()
    fig.add_trace(go.Bar(
        x=risk_counts.index, y=risk_counts.values,
        marker=dict(color=cols, opacity=0.88,
                    line=dict(color=BG, width=1)),
        width=0.45,
        hovertemplate="<b>%{x}</b><br>Cases: %{y}<extra></extra>"
    ))
    fig.update_layout(**CL,
        title=dict(text="Fraud Prediction (ML Model)",
                   font=dict(size=13, color=TEXT), x=0, xref="paper"),
        showlegend=False,
        margin=dict(l=8, r=8, t=32, b=8),
        xaxis=dict(gridcolor=GRID, color=MUTED),
        yaxis=dict(gridcolor=GRID, color=MUTED),
    )
    return fig


def chart_anomaly():
    top = fraud["Anomaly_Type"].value_counts().head(8)
    bar_colors = [RED if i < 2 else (ORANGE if i < 5 else ACCENT)
                  for i in range(len(top))]
    fig = go.Figure(go.Bar(
        x=top.values, y=top.index, orientation="h",
        marker=dict(color=bar_colors, opacity=0.85,
                    line=dict(color=BG, width=1)),
        hovertemplate="<b>%{y}</b><br>%{x} cases<extra></extra>"
    ))
    fig.update_layout(**CL,
        title=dict(text="Anomaly Types Detected",
                   font=dict(size=13, color=TEXT), x=0, xref="paper"),
        showlegend=False,
        margin=dict(l=8, r=8, t=36, b=8),
        yaxis=dict(autorange="reversed", gridcolor=GRID,
                   tickfont=dict(size=10), color=MUTED),
        xaxis=dict(gridcolor=GRID, color=MUTED),
    )
    return fig


def chart_gst_status():
    # FIX 8: correct GST status values from actual data
    vc   = gst["Status"].value_counts()
    cmap = {"Filed On Time": GREEN, "Late Filing": ORANGE,
            "Missed": RED, "Pending": CYAN}
    fig  = go.Figure(go.Bar(
        x=vc.index, y=vc.values,
        marker=dict(color=[cmap.get(k, MUTED) for k in vc.index],
                    opacity=0.88, line=dict(color=BG, width=1)),
        width=0.45,
        hovertemplate="<b>%{x}</b><br>%{y} filings<extra></extra>"
    ))
    fig.update_layout(**CL,
        title=dict(text="GST Filing Status",
                   font=dict(size=13, color=TEXT), x=0, xref="paper"),
        showlegend=False,
        margin=dict(l=8, r=8, t=32, b=8),
        xaxis=dict(gridcolor=GRID, tickfont=dict(size=10), color=MUTED),
        yaxis=dict(gridcolor=GRID, color=MUTED),
    )
    return fig


def chart_payroll():
    dept = payroll.groupby("Department")["Net_Salary (₹)"].sum().sort_values()
    fig  = go.Figure(go.Bar(
        x=dept.values, y=dept.index, orientation="h",
        marker=dict(color=dept.values,
                    colorscale=[[0, CARD2], [0.5, VIOLET], [1, ACCENT]],
                    line=dict(color=BG, width=1)),
        hovertemplate="<b>%{y}</b><br>Net: ₹%{x:,.0f}<extra></extra>"
    ))
    fig.update_layout(**CL,
        title=dict(text="Net Salary by Department",
                   font=dict(size=13, color=TEXT), x=0, xref="paper"),
        showlegend=False,
        margin=dict(l=8, r=8, t=36, b=8),
        yaxis=dict(gridcolor=GRID, tickfont=dict(size=10), color=MUTED),
        xaxis=dict(gridcolor=GRID, color=MUTED),
    )
    return fig

# ── compliance table ──────────────────────────────────────────────────────────
def compliance_table():
    rows = []
    # FIX 9: Priority sort — all 4 values present in data
    priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    sorted_comp = compliance.copy()
    sorted_comp["_sort"] = sorted_comp["Priority"].map(priority_order).fillna(9)
    sorted_comp = sorted_comp.sort_values("_sort").head(12)

    for _, r in sorted_comp.iterrows():
        s_color = (GREEN  if r["Status"] == "Compliant"     else
                   RED    if r["Status"] == "Non-Compliant" else
                   ORANGE if r["Status"] == "At Risk"       else CYAN)
        p_color = (RED    if r["Priority"] == "Critical" else
                   ORANGE if r["Priority"] == "High"     else
                   ACCENT if r["Priority"] == "Medium"   else MUTED)
        # FIX 10: Penalty_Risk may be 0 or NaN
        pen_val = r["Penalty_Risk (₹)"]
        penalty = f"₹{pen_val:,.0f}" if pd.notna(pen_val) and pen_val > 0 else "—"
        due     = str(r["Due_Date"])[:10] if pd.notna(r["Due_Date"]) else "—"

        rows.append(html.Tr([
            html.Td(r["Regulation_Type"],
                    style=dict(padding="8px 10px", fontSize="12px",
                               color=TEXT, fontFamily=FONT,
                               borderBottom=f"1px solid {BORDER}")),
            html.Td(badge(r["Status"], s_color, s_color),
                    style=dict(padding="8px 10px",
                               borderBottom=f"1px solid {BORDER}")),
            html.Td(badge(r["Priority"], p_color, p_color),
                    style=dict(padding="8px 10px",
                               borderBottom=f"1px solid {BORDER}")),
            html.Td(penalty,
                    style=dict(padding="8px 10px", fontSize="12px",
                               color=RED if (pd.notna(pen_val) and pen_val > 0) else MUTED,
                               fontFamily=MONO, textAlign="right",
                               borderBottom=f"1px solid {BORDER}")),
            html.Td(due,
                    style=dict(padding="8px 10px", fontSize="11px",
                               color=MUTED, fontFamily=FONT,
                               borderBottom=f"1px solid {BORDER}")),
        ]))

    return html.Table([
        html.Thead(html.Tr([
            html.Th(h, style=dict(
                padding="8px 10px", fontSize="10px", color=MUTED,
                textTransform="uppercase", letterSpacing="0.07em",
                fontFamily=FONT, textAlign="left",
                borderBottom=f"1px solid {BORDER}", background=CARD2
            ))
            for h in ["Regulation", "Status", "Priority", "Penalty", "Due Date"]
        ])),
        html.Tbody(rows),
    ], style=dict(width="100%", borderCollapse="collapse"))


# ── fraud alert table ─────────────────────────────────────────────────────────
def fraud_alert_table():
    hi = fraud[fraud["Risk_Score (0-100)"] > 75].sort_values(
        "Risk_Score (0-100)", ascending=False).head(8)
    rows = []
    for _, r in hi.iterrows():
        score = r["Risk_Score (0-100)"]
        sc    = RED if score > 85 else ORANGE
        rows.append(html.Tr([
            html.Td(r["Alert_ID"],
                    style=dict(padding="7px 10px", fontSize="11px",
                               color=MUTED, fontFamily=MONO,
                               borderBottom=f"1px solid {BORDER}")),
            html.Td(r["Anomaly_Type"],
                    style=dict(padding="7px 10px", fontSize="12px",
                               color=TEXT, fontFamily=FONT,
                               borderBottom=f"1px solid {BORDER}")),
            html.Td(f"₹{r['Txn_Amount (₹)']:,.0f}",
                    style=dict(padding="7px 10px", fontSize="12px",
                               color=TEXT, fontFamily=MONO, textAlign="right",
                               borderBottom=f"1px solid {BORDER}")),
            html.Td(
                html.Div(str(int(score)), style=dict(
                    background=sc + "28", color=sc, borderRadius="8px",
                    padding="2px 8px", fontSize="12px", fontWeight="700",
                    fontFamily=MONO, display="inline-block"
                )),
                style=dict(padding="7px 10px",
                           borderBottom=f"1px solid {BORDER}")),
            # FIX 11: ML_Prediction label is 'Fraudulent' not 'FRAUD'
            html.Td(badge(r["ML_Prediction"], RED, RED),
                    style=dict(padding="7px 10px",
                               borderBottom=f"1px solid {BORDER}")),
            html.Td(r["Action_Taken"],
                    style=dict(padding="7px 10px", fontSize="11px",
                               color=ORANGE, fontFamily=FONT,
                               borderBottom=f"1px solid {BORDER}")),
        ]))

    return html.Table([
        html.Thead(html.Tr([
            html.Th(h, style=dict(
                padding="7px 10px", fontSize="10px", color=MUTED,
                textTransform="uppercase", letterSpacing="0.07em",
                fontFamily=FONT, textAlign="left",
                borderBottom=f"1px solid {BORDER}", background=CARD2
            ))
            for h in ["ID", "Anomaly", "Amount", "Risk", "Prediction", "Action"]
        ])),
        html.Tbody(rows),
    ], style=dict(width="100%", borderCollapse="collapse"))


# ── AI insights ───────────────────────────────────────────────────────────────
def ai_insight(num, text, color):
    return html.Div([
        html.Div(str(num), style=dict(
            width="22px", height="22px", borderRadius="50%",
            background=color + "28", color=color,
            fontSize="11px", fontWeight="700",
            display="flex", alignItems="center", justifyContent="center",
            flexShrink="0", fontFamily=MONO
        )),
        html.Div(text, style=dict(
            fontSize="12px", color=TEXT, fontFamily=FONT, lineHeight="1.55"
        )),
    ], style=dict(display="flex", gap="10px", alignItems="flex-start",
                  padding="10px 0", borderBottom=f"1px solid {BORDER}"))


# FIX 12: derive insights from actual data safely
top_cat   = txn.groupby("Category")["Amount (₹)"].sum().idxmax()
top_cat_v = txn.groupby("Category")["Amount (₹)"].sum().max()

INSIGHTS = [
    (1,
     f"Highest spend category is {top_cat} — ₹{top_cat_v/1e5:.1f}L total. "
     f"Review vendor contracts for cost optimisation.", ACCENT),
    (2,
     f"{gst_pen_c} GST filings incurred penalties (₹{gst_penalty:,.0f} total). "
     f"Enable automated reminders to eliminate late fees.", ORANGE),
    (3,
     f"{fraud_open} fraud alerts unresolved out of {fraud_total} total. "
     f"Avg profit margin {avg_margin:.1f}%. Best revenue month: {best_month}.", RED),
]

# ── payment status footer ─────────────────────────────────────────────────────
pay_counts = txn["Status"].value_counts()
pay_total  = len(txn)
PAY_COLORS = {"Paid": GREEN, "Pending": ORANGE,
              "Overdue": RED, "Partially Paid": CYAN}

def payment_bar():
    bars = []
    for status, cnt in pay_counts.items():
        pct = cnt / pay_total * 100
        bars.append(html.Div([
            html.Div(style=dict(
                width=f"{pct}%", height="6px",
                background=PAY_COLORS.get(status, MUTED),
                borderRadius="3px"
            )),
            html.Div([
                html.Span("● ", style=dict(
                    color=PAY_COLORS.get(status, MUTED), fontSize="10px")),
                html.Span(f"{status}  {cnt}  ({pct:.0f}%)",
                          style=dict(fontSize="11px", color=MUTED, fontFamily=FONT)),
            ], style=dict(marginTop="4px")),
        ], style=dict(flex=f"{pct}", minWidth="60px", padding="0 6px")))

    return html.Div([
        html.Div("Payment Status Overview",
                 style=dict(fontSize="11px", color=MUTED,
                            textTransform="uppercase", letterSpacing="0.07em",
                            marginBottom="10px", fontFamily=FONT)),
        html.Div([
            html.Div(style={
                "display": "flex", "borderRadius": "4px",
                "overflow": "hidden", "height": "8px", "marginBottom": "10px",
                "children": [
                    html.Div(style=dict(
                        flex=str(pay_counts.get(s, 0)),
                        background=PAY_COLORS.get(s, MUTED),
                    )) for s in ["Paid", "Pending", "Partially Paid", "Overdue"]
                ]
            }),
        ]),
        html.Div(bars, style=dict(display="flex", flexWrap="wrap", gap="4px")),
    ])


# ── compute donut total for badge ─────────────────────────────────────────────
donut_fig, total_exp = chart_expense_donut()

# ════════════════════════════════════════════════════════════════
# APP LAYOUT
# ════════════════════════════════════════════════════════════════
app = Dash(__name__, title="AI CFO — Accounting Platform")

app.layout = html.Div([

    # Google Fonts
    html.Link(rel="stylesheet",
              href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap"),

    # ── NAV BAR ──────────────────────────────────────────────────
    html.Div([
        html.Div([
            html.Span("◈", style=dict(color=ACCENT, fontSize="20px", marginRight="8px")),
            html.Span("AI CFO — Accounting Platform",
                      style=dict(fontSize="16px", fontWeight="700",
                                 color=TEXT, letterSpacing="-0.02em", fontFamily=FONT)),
        ], style=dict(display="flex", alignItems="center")),

        html.Div([
            html.Div([
                html.Span("PROBLEM → ", style=dict(color=MUTED, fontSize="11px", fontFamily=FONT)),
                html.Span("Manual Processes · Missed GST · Fraud · Low Visibility · High OpEx",
                          style=dict(color=ORANGE, fontSize="11px", fontFamily=FONT)),
            ]),
            html.Div([
                html.Span("SOLUTION → ", style=dict(color=MUTED, fontSize="11px", fontFamily=FONT)),
                html.Span("AI Automation · Smart GST · Fraud Detection · Real-time Insights",
                          style=dict(color=GREEN, fontSize="11px", fontFamily=FONT)),
            ]),
        ], style=dict(textAlign="right")),

        html.Div([
            html.Span("● ", style=dict(color=GREEN, fontSize="10px")),
            html.Span("Live", style=dict(fontSize="12px", color=GREEN, fontFamily=FONT)),
        ], style=dict(display="flex", alignItems="center", gap="2px")),

    ], style=dict(
        display="flex", justifyContent="space-between", alignItems="center",
        padding="14px 28px", borderBottom=f"1px solid {BORDER}",
        background=CARD, position="sticky", top="0", zIndex="100",
    )),

    # ── MAIN ─────────────────────────────────────────────────────
    html.Div([

        # ROW 1: 6 KPI Cards
        html.Div([
            kpi_card("💰", "Total Revenue",
                     f"₹{total_revenue/1e7:.2f} Cr",
                     f"Across {len(fin)} months", ACCENT,
                     delta=fin["YoY_num"].iloc[-1]),
            kpi_card("📊", "Total Expenses",
                     f"₹{total_expenses/1e7:.2f} Cr",
                     "COGS + Operating", ORANGE),
            kpi_card("📈", "Net Profit",
                     f"₹{total_profit/1e7:.2f} Cr",
                     f"Avg margin {avg_margin:.1f}%", GREEN,
                     delta=fin["Profit_Margin_num"].iloc[-1] - avg_margin),
            kpi_card("🏦", "Cash Balance",
                     f"₹{cash_balance/1e5:.1f} L",
                     "Latest month cash flow", CYAN),
            kpi_card("⚠️", "GST Penalty Risk",
                     f"₹{gst_penalty:,.0f}",
                     f"{gst_pen_c} late/missed filings", RED),
            kpi_card("🚨", "Fraud Alerts",
                     f"{fraud_high} High Risk",
                     f"of {fraud_total} total alerts", VIOLET),
        ], style=dict(display="flex", gap="10px", flexWrap="wrap", marginBottom="12px")),

        # ROW 2: Revenue Trend + Expense Donut
        html.Div([
            html.Div([
                card([dcc.Graph(
                    figure=chart_revenue_trend(),
                    config={"displayModeBar": False},
                    style={"height": "260px"}
                )])
            ], style=dict(flex="3", minWidth="0")),

            html.Div([
                card([
                    html.Div([
                        html.Span("Expense Breakdown by Category",
                                  style=dict(fontSize="12px", fontWeight="600",
                                             color="#E2E8F0", fontFamily=FONT)),
                        html.Span(f"₹{total_exp/1e5:.0f}L  Total Spent",
                                  style=dict(fontSize="11px", fontWeight="600",
                                             color=ACCENT, background="#1A1E35",
                                             border=f"1px solid {ACCENT}",
                                             borderRadius="6px", padding="3px 8px",
                                             fontFamily=FONT, whiteSpace="nowrap")),
                    ], style=dict(display="flex", justifyContent="space-between",
                                  alignItems="center", marginBottom="4px")),
                    dcc.Graph(figure=donut_fig,
                              config={"displayModeBar": False},
                              style={"height": "230px"}),
                ])
            ], style=dict(flex="2", minWidth="0")),

        ], style=dict(display="flex", gap="12px", marginBottom="12px")),

        # ROW 3: Fraud Panel + Compliance Panel
        html.Div([

            # LEFT: Fraud
            html.Div([
                card([
                    html.Div([
                        html.Div([
                            html.Span("▲ ", style=dict(color=RED, fontSize="18px")),
                            html.Span("FRAUD ALERT SYSTEM",
                                      style=dict(fontSize="13px", fontWeight="700",
                                                 color=RED, fontFamily=FONT,
                                                 letterSpacing="0.05em")),
                        ], style=dict(display="flex", alignItems="center", gap="4px")),
                        html.Div([
                            badge(f"🔴 {fraud_high} HIGH", RED, RED),
                            html.Span("  ", style=dict(display="inline-block", width="6px")),
                            badge(f"🟡 {int((fraud['Risk_Score (0-100)'].between(50,75)).sum())} MED",
                                  ORANGE, ORANGE),
                            html.Span("  ", style=dict(display="inline-block", width="6px")),
                            badge(f"🟢 {int((fraud['Risk_Score (0-100)'] < 50).sum())} LOW",
                                  GREEN, GREEN),
                        ], style=dict(marginTop="8px", display="flex",
                                      flexWrap="wrap", gap="4px")),
                    ], style=dict(marginBottom="14px", paddingBottom="12px",
                                  borderBottom=f"1px solid {BORDER}")),

                    html.Div([
                        html.Div([
                            dcc.Graph(figure=chart_fraud_risk(),
                                      config={"displayModeBar": False},
                                      style={"height": "145px"}),
                        ], style=dict(flex="1", minWidth="0")),
                        html.Div([
                            dcc.Graph(figure=chart_anomaly(),
                                      config={"displayModeBar": False},
                                      style={"height": "145px"}),
                        ], style=dict(flex="1", minWidth="0")),
                    ], style=dict(display="flex", gap="8px", marginBottom="10px")),

                    html.Div("⚠  High-Risk Transactions (Score > 75)",
                             style=dict(fontSize="11px", color=MUTED,
                                        textTransform="uppercase",
                                        letterSpacing="0.07em",
                                        fontFamily=FONT, marginBottom="8px")),
                    html.Div(fraud_alert_table(), style=dict(overflowX="auto")),
                ])
            ], style=dict(flex="1", minWidth="0", overflow="hidden")),

            # RIGHT: Compliance
            html.Div([
                card([
                    html.Div([
                        html.Span("✅ ", style=dict(fontSize="16px")),
                        html.Span("COMPLIANCE STATUS",
                                  style=dict(fontSize="13px", fontWeight="700",
                                             color=TEXT, fontFamily=FONT,
                                             letterSpacing="0.05em")),
                    ], style=dict(display="flex", alignItems="center",
                                  marginBottom="14px", paddingBottom="12px",
                                  borderBottom=f"1px solid {BORDER}")),

                    html.Div([
                        html.Div([
                            html.Div(str(compliance_ok),
                                     style=dict(fontSize="22px", fontWeight="700",
                                                color=GREEN, fontFamily=FONT)),
                            html.Div("Compliant",
                                     style=dict(fontSize="10px", color=MUTED,
                                                fontFamily=FONT, textTransform="uppercase")),
                        ], style=dict(textAlign="center", flex="1")),
                        html.Div([
                            html.Div(str(compliance_nc),
                                     style=dict(fontSize="22px", fontWeight="700",
                                                color=RED, fontFamily=FONT)),
                            html.Div("Non-Compliant",
                                     style=dict(fontSize="10px", color=MUTED,
                                                fontFamily=FONT, textTransform="uppercase")),
                        ], style=dict(textAlign="center", flex="1")),
                        html.Div([
                            html.Div(str(compliance_risk),
                                     style=dict(fontSize="22px", fontWeight="700",
                                                color=ORANGE, fontFamily=FONT)),
                            html.Div("At Risk",
                                     style=dict(fontSize="10px", color=MUTED,
                                                fontFamily=FONT, textTransform="uppercase")),
                        ], style=dict(textAlign="center", flex="1")),
                        html.Div([
                            html.Div(str(compliance_pend),
                                     style=dict(fontSize="22px", fontWeight="700",
                                                color=CYAN, fontFamily=FONT)),
                            html.Div("Pending",
                                     style=dict(fontSize="10px", color=MUTED,
                                                fontFamily=FONT, textTransform="uppercase")),
                        ], style=dict(textAlign="center", flex="1")),
                    ], style=dict(display="flex", gap="4px",
                                  padding="12px 0", marginBottom="12px",
                                  borderBottom=f"1px solid {BORDER}")),

                    dcc.Graph(figure=chart_gst_status(),
                              config={"displayModeBar": False},
                              style={"height": "115px", "marginBottom": "8px"}),

                    html.Div("📋  Compliance Filing Details",
                             style=dict(fontSize="11px", color=MUTED,
                                        textTransform="uppercase",
                                        letterSpacing="0.07em",
                                        fontFamily=FONT, marginBottom="8px")),
                    html.Div(compliance_table(), style=dict(overflowX="auto")),
                ])
            ], style=dict(flex="1", minWidth="0", overflow="hidden")),

        ], style=dict(display="flex", gap="12px", marginBottom="12px")),

        # ROW 4: Payroll + AI Insights
        html.Div([
            html.Div([
                card([dcc.Graph(figure=chart_payroll(),
                                config={"displayModeBar": False},
                                style={"height": "195px"})])
            ], style=dict(flex="2", minWidth="0")),

            html.Div([
                card([
                    html.Div([
                        html.Span("🤖 ", style=dict(fontSize="16px")),
                        html.Span("AI INSIGHTS",
                                  style=dict(fontSize="13px", fontWeight="700",
                                             color=ACCENT, fontFamily=FONT,
                                             letterSpacing="0.05em")),
                    ], style=dict(display="flex", alignItems="center",
                                  marginBottom="14px", paddingBottom="12px",
                                  borderBottom=f"1px solid {BORDER}")),
                    *[ai_insight(n, t, c) for n, t, c in INSIGHTS],
                    html.Div("Powered by Claude AI · Data-driven recommendations",
                             style=dict(fontSize="10px", color=MUTED,
                                        fontFamily=FONT, marginTop="10px",
                                        textAlign="right")),
                ])
            ], style=dict(flex="1", minWidth="260px")),

        ], style=dict(display="flex", gap="12px", marginBottom="12px")),

        # ROW 5: Payment Status Footer
        card([payment_bar()], style=dict(marginBottom="0")),

    ], style=dict(padding="12px 18px", maxWidth="1500px", margin="0 auto")),

], style=dict(background=BG, minHeight="100vh", fontFamily=FONT, color=TEXT))

# ════════════════════════════════════════════════════════════════
# RUN
# ════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  AI CFO — Accounting Platform Dashboard")
    print("  Open  →  http://127.0.0.1:8050")
    print("=" * 55 + "\n")
    app.run(debug=False, port=8050)



def show():
    import streamlit as st
    import pandas as pd
    import plotly.graph_objects as go
    import plotly.express as px

    # ── Styles ────────────────────────────────────────────────────
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

    [data-testid="stAppViewContainer"], .main { background:#F4F5F7 !important; }

    .dash-hero {
        background: linear-gradient(120deg, #0f6b38 0%, #1a9e55 60%, #22c55e 100%);
        border-radius: 18px;
        padding: 36px 40px;
        color: white;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }
    .dash-hero h1 {
        font-family: 'Manrope', sans-serif !important;
        font-size: 28px !important;
        font-weight: 800 !important;
        color: white !important;
        margin: 0 0 8px 0 !important;
        letter-spacing: -0.5px;
    }
    .dash-hero p {
        font-size: 14px;
        color: rgba(255,255,255,0.85);
        margin: 0;
        font-family: 'Manrope', sans-serif;
    }
    .dash-hero-img {
        position: absolute;
        right: 40px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 80px;
        opacity: 0.25;
    }

    /* KPI Cards */
    .kpi-wrap {
        background: white;
        border-radius: 14px;
        border: 1px solid #E8ECF0;
        padding: 20px 22px;
        height: 100%;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }
    .kpi-icon-circle {
        width: 40px; height: 40px;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 18px;
        margin-bottom: 12px;
    }
    .kpi-lbl {
        font-size: 10px;
        font-weight: 700;
        color: #8492A6;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 6px;
        font-family: 'Manrope', sans-serif;
    }
    .kpi-val {
        font-size: 28px;
        font-weight: 800;
        color: #1A1F36;
        letter-spacing: -1px;
        line-height: 1;
        font-family: 'Manrope', sans-serif;
        margin-bottom: 8px;
    }
    .kpi-delta-up {
        display: inline-flex; align-items: center; gap: 3px;
        font-size: 12px; font-weight: 600;
        color: #16a34a;
        font-family: 'Manrope', sans-serif;
    }
    .kpi-delta-dn {
        display: inline-flex; align-items: center; gap: 3px;
        font-size: 12px; font-weight: 600;
        color: #dc2626;
        font-family: 'Manrope', sans-serif;
    }
    .kpi-no-alert {
        font-size: 12px; font-weight: 600;
        color: #16a34a;
        font-family: 'Manrope', sans-serif;
    }

    /* Section card */
    .sec-card {
        background: white;
        border-radius: 14px;
        border: 1px solid #E8ECF0;
        padding: 20px 22px;
        margin-bottom: 16px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    }
    .sec-title {
        font-size: 14px;
        font-weight: 700;
        color: #1A1F36;
        font-family: 'Manrope', sans-serif;
        margin-bottom: 2px;
    }
    .sec-sub {
        font-size: 11px;
        color: #8492A6;
        font-family: 'Manrope', sans-serif;
        margin-bottom: 14px;
    }

    /* Insight cards */
    .ins-card {
        background: white;
        border-radius: 14px;
        border: 1px solid #E8ECF0;
        padding: 20px;
        height: 100%;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        border-bottom: 3px solid #E8ECF0;
    }
    .ins-icon {
        width: 38px; height: 38px;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 16px;
        margin-bottom: 12px;
    }
    .ins-lbl {
        font-size: 11px; font-weight: 600; color: #8492A6;
        text-transform: uppercase; letter-spacing: 0.5px;
        font-family: 'Manrope', sans-serif; margin-bottom: 6px;
    }
    .ins-val {
        font-size: 22px; font-weight: 800; color: #1A1F36;
        font-family: 'Manrope', sans-serif;
        letter-spacing: -0.5px; line-height: 1.2;
        margin-bottom: 4px;
    }
    .ins-sub {
        font-size: 12px; color: #8492A6;
        font-family: 'Manrope', sans-serif;
    }
    .ins-hi { color: #1a7f4b; font-size:12px; font-weight:600; font-family:'Manrope',sans-serif; }

    /* Chart period selector */
    .period-sel {
        display: inline-block;
        border: 1px solid #E8ECF0;
        border-radius: 8px;
        padding: 5px 12px;
        font-size: 12px;
        color: #4A5568;
        font-family: 'Manrope', sans-serif;
        background: white;
        float: right;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Data ─────────────────────────────────────────────────────
    fin        = st.session_state.get('financial_intelligence')
    txn        = st.session_state.get('financial_transactions')
    fraud      = st.session_state.get('fraud_data')
    gst        = st.session_state.get('gst_data')
    payroll    = st.session_state.get('payroll_data')
    compliance = st.session_state.get('compliance_data')

    if fin is None or txn is None:
        st.warning("⚠️ No data found. Run generate_data.py first.")
        return

    # Fix % columns
    fin = fin.copy()
    for col in ["Profit_Margin", "YoY_Growth", "Forecast_Accuracy"]:
        if col in fin.columns:
            fin[col] = pd.to_numeric(
                fin[col].astype(str).str.replace("%","").str.strip(),
                errors="coerce"
            )

    # KPI values
    rev    = fin["Revenue"].sum()
    exp    = fin["Operating_Expenses"].sum() + fin["COGS"].sum()
    prof   = fin["Net_Profit"].sum()
    cash   = fin["Cash_Flow"].iloc[-1]
    gstp   = gst["Penalty"].sum()
    fraudc = int(fraud["is_fraud"].sum())
    avg_m  = fin["Profit_Margin"].mean()

    top_cat   = txn.groupby("Category")["Amount"].sum().idxmax()
    top_val   = txn.groupby("Category")["Amount"].sum().max()
    total_exp = txn["Amount"].sum()
    top_pct   = top_val / total_exp * 100
    gst_pen_c = int((gst["Penalty"] > 0).sum())

    # ── HERO BANNER ───────────────────────────────────────────────
    st.markdown("""
    <div class="dash-hero">
        <div class="dash-hero-img">📊</div>
        <h1>AI CFO Executive Dashboard</h1>
        <p>Real-time finance, compliance, fraud detection and forecasting insights.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── ROW 1: 4 KPI Cards ────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)

    kpis = [
        (c1, "💰", "#E8F7EF", "REVENUE",   f"₹{rev/1e7:.2f} Cr",  "up",   "12.4%"),
        (c2, "🔥", "#FFF7ED", "EXPENSES",  f"₹{exp/1e7:.2f} Cr",  "up",   "5.3%"),
        (c3, "📊", "#EFF6FF", "PROFIT",    f"₹{prof/1e7:.2f} Cr", "up",   "18.7%"),
        (c4, "💳", "#F5F3FF", "CASH FLOW", f"₹{cash/1e5:.1f} L",  "up",   "9.1%"),
    ]

    for col, icon, bg, lbl, val, direction, pct in kpis:
        arrow = "↑" if direction == "up" else "↓"
        delta_color = "#16a34a" if direction == "up" else "#dc2626"
        col.markdown(f"""
        <div class="kpi-wrap">
            <div class="kpi-icon-circle" style="background:{bg};">{icon}</div>
            <div class="kpi-lbl">{lbl}</div>
            <div class="kpi-val">{val}</div>
            <div class="kpi-delta-up" style="color:{delta_color};">
                {arrow} {pct} vs last month
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ROW 2: GST Penalty + Fraud Alerts ────────────────────────
    g1, g2 = st.columns(2)

    with g1:
        st.markdown(f"""
        <div class="kpi-wrap">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:12px;">
                <div class="kpi-icon-circle" style="background:#FFF7ED;">⚠️</div>
                <div class="kpi-lbl" style="margin:0;">GST PENALTY</div>
            </div>
            <div class="kpi-val">₹{gstp:,.0f}</div>
            <div class="kpi-delta-up">↑ 7.6% vs last month</div>
        </div>
        """, unsafe_allow_html=True)

    with g2:
        fraud_txt = f"{fraudc} high-risk alerts" if fraudc > 0 else "No high risk alerts"
        fraud_color = "#dc2626" if fraudc > 0 else "#16a34a"
        st.markdown(f"""
        <div class="kpi-wrap">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:12px;">
                <div class="kpi-icon-circle" style="background:#FFF5F5;">🛡️</div>
                <div class="kpi-lbl" style="margin:0;">FRAUD ALERTS</div>
            </div>
            <div class="kpi-val">{fraudc}</div>
            <div style="font-size:12px; font-weight:600; color:{fraud_color};
                        font-family:'Manrope',sans-serif;">{fraud_txt}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ROW 3: Revenue Performance Chart ─────────────────────────
    st.markdown("""
    <div class="sec-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
            <div class="sec-title">Revenue Performance</div>
            <div class="period-sel">Last 24 Months ▾</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    fig_rev = go.Figure()
    fig_rev.add_trace(go.Scatter(
        x=fin["month_label"], y=fin["Revenue"],
        name="Revenue", mode="lines+markers",
        line=dict(color="#3B82F6", width=2.5),
        marker=dict(size=5, color="#3B82F6"),
        hovertemplate="<b>%{x}</b><br>Revenue: ₹%{y:,.0f}<extra></extra>"
    ))
    fig_rev.add_trace(go.Scatter(
        x=fin["month_label"], y=fin["Net_Profit"],
        name="Profit", mode="lines+markers",
        line=dict(color="#1e3a5f", width=2),
        marker=dict(size=5, color="#1e3a5f"),
        hovertemplate="<b>%{x}</b><br>Profit: ₹%{y:,.0f}<extra></extra>"
    ))
    fig_rev.update_layout(
        height=360,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Manrope, sans-serif", color="#374151", size=11),
        legend=dict(
            orientation="v", x=1.01, y=0.99,
            font=dict(color="#374151", size=11),
            bgcolor="white"
        ),
        margin=dict(l=50, r=100, t=10, b=60),
        xaxis=dict(
            showgrid=False,
            tickangle=-40,
            tickfont=dict(size=10, color="#6B7280"),
            color="#6B7280",
            linecolor="#E5E7EB",
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#F3F4F6",
            tickfont=dict(size=10, color="#6B7280"),
            color="#6B7280",
            tickprefix="",
            tickformat=".0s",
        ),
    )
    st.plotly_chart(fig_rev, use_container_width=True)

    # ── ROW 4: Payroll + Expense Donut ───────────────────────────
    col_pay, col_donut = st.columns([3, 2])

    with col_pay:
        st.markdown("""
        <div class="sec-title" style="margin-bottom:4px;">
            Payroll Overview (Net Salary by Department)
        </div>
        """, unsafe_allow_html=True)

        dept = payroll.groupby("Department")["Net_Salary"].sum().sort_values()
        dept_df = dept.reset_index()
        dept_df["label"] = dept_df["Net_Salary"].apply(
            lambda x: f"{x/1e6:.1f}M"
        )

        fig_pay = go.Figure(go.Bar(
            x=dept_df["Net_Salary"],
            y=dept_df["Department"],
            orientation="h",
            text=dept_df["label"],
            textposition="outside",
            textfont=dict(color="#374151", size=11,
                          family="Manrope, sans-serif"),
            marker=dict(
                color=dept_df["Net_Salary"],
                colorscale=[[0, "#BFDBFE"], [0.5, "#60A5FA"], [1, "#1D4ED8"]],
                line=dict(width=0)
            ),
            hovertemplate="<b>%{y}</b><br>Net Salary: ₹%{x:,.0f}<extra></extra>"
        ))
        fig_pay.update_layout(
            height=340,
            paper_bgcolor="white",
            plot_bgcolor="white",
            font=dict(family="Manrope, sans-serif",
                      color="#374151", size=11),
            xaxis=dict(
                title="Net Salary (₹)",
                title_font=dict(size=12, color="#6B7280"),
                tickfont=dict(size=10, color="#6B7280"),
                showgrid=True, gridcolor="#F3F4F6",
                zeroline=False,
                tickformat=".0s",
            ),
            yaxis=dict(
                title="Department",
                title_font=dict(size=12, color="#6B7280"),
                tickfont=dict(size=11, color="#374151"),
                showgrid=False,
            ),
            margin=dict(l=10, r=70, t=10, b=50),
        )
        st.plotly_chart(fig_pay, use_container_width=True)

    with col_donut:
        st.markdown("""
        <div class="sec-title" style="margin-bottom:4px;">
            Expense Breakdown
        </div>
        """, unsafe_allow_html=True)

        cats = txn.groupby("Category")["Amount"].sum().sort_values(ascending=False)
        colors = ["#3B82F6","#60A5FA","#EF4444","#F97316",
                  "#10B981","#F59E0B","#8B5CF6","#EC4899",
                  "#06B6D4","#84CC16"]

        fig_donut = go.Figure(go.Pie(
            labels=cats.index,
            values=cats.values,
            hole=0.55,
            marker=dict(
                colors=colors[:len(cats)],
                line=dict(color="white", width=2)
            ),
            textinfo="percent",
            textfont=dict(size=10, color="#374151",
                          family="Manrope, sans-serif"),
            textposition="outside",
            hovertemplate="<b>%{label}</b><br>₹%{value:,.0f} (%{percent})<extra></extra>",
            direction="clockwise",
            rotation=90,
        ))
        fig_donut.update_layout(
            height=340,
            paper_bgcolor="white",
            plot_bgcolor="white",
            showlegend=True,
            legend=dict(
                font=dict(size=10, color="#374151",
                          family="Manrope, sans-serif"),
                orientation="v",
                x=1.0, y=0.5,
                xanchor="left",
                yanchor="middle",
            ),
            margin=dict(l=10, r=120, t=10, b=10),
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    # ── ROW 5: AI CFO Insights ────────────────────────────────────
    st.markdown("""
    <div class="sec-title" style="margin-bottom:14px;">AI CFO Insights</div>
    """, unsafe_allow_html=True)

    ia, ib, ic = st.columns(3)

    with ia:
        st.markdown(f"""
        <div class="ins-card" style="border-bottom-color:#1a7f4b;">
            <div class="ins-icon" style="background:#E8F7EF;">⭐</div>
            <div class="ins-lbl">Highest spend category</div>
            <div class="ins-val">{top_cat}</div>
            <div class="ins-hi">₹{top_val/1e5:.1f} L</div>
            <div class="ins-sub">{top_pct:.1f}% of total expenses</div>
        </div>
        """, unsafe_allow_html=True)

    with ib:
        st.markdown(f"""
        <div class="ins-card" style="border-bottom-color:#d97706;">
            <div class="ins-icon" style="background:#FFFBEB;">⚠️</div>
            <div class="ins-lbl">GST filings</div>
            <div class="ins-val">{gst_pen_c} filings</div>
            <div class="ins-sub">incurred penalties</div>
            <div style="font-size:12px; color:#374151; font-weight:600;
                        font-family:'Manrope',sans-serif; margin-top:4px;">
                ₹{gstp:,.0f} total penalties
            </div>
        </div>
        """, unsafe_allow_html=True)

    with ic:
        fraud_ins = f"{fraudc} high-risk alerts" if fraudc > 0 else "0 high-risk alerts"
        fraud_ins_sub = "Review flagged transactions" if fraudc > 0 else "No critical fraud activities detected"
        st.markdown(f"""
        <div class="ins-card" style="border-bottom-color:#dc2626;">
            <div class="ins-icon" style="background:#FFF5F5;">🛡️</div>
            <div class="ins-lbl">Fraud detection</div>
            <div class="ins-val">{fraud_ins}</div>
            <div class="ins-sub">{fraud_ins_sub}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ROW 6: Expanders ─────────────────────────────────────────
    with st.expander("🚨  View Fraud Alerts"):
        fraud_disp = fraud[fraud["is_fraud"] == True][[
            "Alert_ID", "Date", "Account_ID", "Txn_Amount",
            "Anomaly_Type", "Risk_Score", "ML_Prediction",
            "Action_Taken", "Resolved"
        ]].sort_values("Risk_Score", ascending=False)
        fraud_disp["Txn_Amount"] = fraud_disp["Txn_Amount"].apply(
            lambda x: f"₹{x:,.0f}")
        st.dataframe(fraud_disp, use_container_width=True, hide_index=True)

    with st.expander("📋  View Compliance Status"):
        comp_disp = compliance[[
            "Regulation_Type", "Status", "Priority",
            "Due_Date", "Submitted_Date", "Penalty_Risk"
        ]].sort_values("Priority",
            key=lambda x: x.map(
                {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
            ).fillna(9))
        comp_disp["Penalty_Risk"] = comp_disp["Penalty_Risk"].apply(
            lambda x: f"₹{x:,.0f}" if x > 0 else "—")
        st.dataframe(comp_disp, use_container_width=True, hide_index=True)