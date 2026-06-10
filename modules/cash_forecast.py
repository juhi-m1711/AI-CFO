"""
modules/cash_forecast.py
========================
[MODIFY] Cash Flow Forecast — AI-CFO Finance sub-tab.

Changes from original:
- All inline <style> blocks removed; theme.py tokens used throughout.
- All emojis replaced with Material Icons.
- Both Plotly charts (Historical Performance, Prophet Forecast) pass
  through style_plotly_fig() for consistent blue-and-white styling.
- Scenario simulator labels use Material Icons instead of emoji HTML entities.
- Hero banner rewritten to match platform-wide gradient style.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.theme import (
    section_header, kpi_card, style_plotly_fig, alert_box,
    PRIMARY, PRIMARY_LIGHT, PRIMARY_DARK,
    SUCCESS, SUCCESS_BG,
    WARNING, WARNING_BG,
    DANGER,  DANGER_BG,
    WHITE, BORDER,
    TEXT_PRIMARY, TEXT_MUTED,
    CHART_PALETTE, FONT,
)


# ─────────────────────────────────────────────────────────────
# PROPHET FORECAST
# ─────────────────────────────────────────────────────────────

def run_prophet(df, periods=12, target_col="Revenue"):
    """
    Run Facebook Prophet on monthly financial data.
    df must have a 'ds' (datetime) column and the target_col.
    Returns (forecast_df, model, error_string_or_None).
    """
    try:
        from prophet import Prophet

        prophet_df = (
            df[["ds", target_col]]
            .rename(columns={target_col: "y"})
            .dropna()
        )
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            changepoint_prior_scale=0.1,
            interval_width=0.80,
        )
        model.fit(prophet_df)
        future   = model.make_future_dataframe(periods=periods, freq="MS")
        forecast = model.predict(future)
        return forecast, model, None

    except ImportError:
        return None, None, "prophet_not_installed"
    except Exception as exc:
        return None, None, str(exc)


# ─────────────────────────────────────────────────────────────
# CHART BUILDERS
# ─────────────────────────────────────────────────────────────

def _chart_historical(fin: pd.DataFrame) -> go.Figure:
    """Revenue, Net Profit, Cash Flow — 24-month historical trend."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=fin["month_label"], y=fin["Revenue"],
        name="Revenue", mode="lines+markers",
        line=dict(color=PRIMARY, width=2.5),
        marker=dict(size=5, color=PRIMARY),
        fill="tozeroy", fillcolor="rgba(37,99,235,0.06)",
        hovertemplate="<b>%{x}</b><br>Revenue: ₹%{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=fin["month_label"], y=fin["Net_Profit"],
        name="Net Profit", mode="lines+markers",
        line=dict(color=SUCCESS, width=2, dash="dot"),
        marker=dict(size=4, color=SUCCESS),
        hovertemplate="<b>%{x}</b><br>Net Profit: ₹%{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=fin["month_label"], y=fin["Cash_Flow"],
        name="Cash Flow", mode="lines+markers",
        line=dict(color=WARNING, width=1.8, dash="dash"),
        marker=dict(size=4, color=WARNING),
        hovertemplate="<b>%{x}</b><br>Cash Flow: ₹%{y:,.0f}<extra></extra>",
    ))

    style_plotly_fig(fig, height=340)
    fig.update_layout(
        margin=dict(l=12, r=12, t=10, b=55),
        xaxis=dict(tickangle=-40, tickfont=dict(size=9)),
        yaxis=dict(tickprefix="₹", tickformat=".2s"),
        legend=dict(orientation="h", x=0, y=-0.28),
    )
    return fig


def _chart_prophet(
    fin: pd.DataFrame,
    forecast: pd.DataFrame,
    target_col: str,
    periods: int,
) -> go.Figure:
    """Prophet forecast chart with confidence band and vertical split line."""
    hist_end = fin["ds"].max()
    fc_only  = forecast[forecast["ds"] > hist_end].head(periods)

    fig = go.Figure()

    # Confidence band
    fig.add_trace(go.Scatter(
        x=pd.concat([fc_only["ds"], fc_only["ds"][::-1]]),
        y=pd.concat([fc_only["yhat_upper"], fc_only["yhat_lower"][::-1]]),
        fill="toself",
        fillcolor="rgba(37,99,235,0.10)",
        line=dict(color="rgba(0,0,0,0)"),
        name="80% Confidence",
        showlegend=True,
        hoverinfo="skip",
    ))

    # Historical actual
    fig.add_trace(go.Scatter(
        x=fin["ds"], y=fin[target_col],
        name="Actual", mode="lines+markers",
        line=dict(color=PRIMARY_DARK, width=2.5),
        marker=dict(size=5, color=PRIMARY_DARK),
        hovertemplate="<b>%{x|%b %Y}</b><br>Actual: ₹%{y:,.0f}<extra></extra>",
    ))

    # Forecast line
    fig.add_trace(go.Scatter(
        x=fc_only["ds"], y=fc_only["yhat"],
        name="Forecast", mode="lines+markers",
        line=dict(color=PRIMARY, width=2.5, dash="dot"),
        marker=dict(size=6, color=PRIMARY, symbol="diamond",
                    line=dict(color=WHITE, width=1.5)),
        hovertemplate="<b>%{x|%b %Y}</b><br>Forecast: ₹%{y:,.0f}<extra></extra>",
    ))

    # Forecast start marker
    fig.add_vline(
        x=hist_end.timestamp() * 1000,
        line_dash="dash", line_color=TEXT_MUTED, line_width=1.5,
        annotation_text="Forecast Start",
        annotation_font=dict(size=10, color=TEXT_MUTED),
        annotation_position="top right",
    )

    style_plotly_fig(fig, height=380)
    fig.update_layout(
        margin=dict(l=12, r=12, t=16, b=55),
        xaxis=dict(tickformat="%b %Y", tickfont=dict(size=10)),
        yaxis=dict(tickprefix="₹", tickformat=".2s"),
        legend=dict(orientation="h", x=0, y=-0.25),
    )
    return fig


# ─────────────────────────────────────────────────────────────
# MAIN SHOW FUNCTION
# ─────────────────────────────────────────────────────────────

def show():

    # ── Data ─────────────────────────────────────────────────
    fin = st.session_state.get("financial_intelligence")
    if fin is None:
        alert_box("Financial intelligence data not loaded.", "error")
        return

    fin = fin.copy()

    # Normalise % columns
    for col in ["Profit_Margin", "YoY_Growth", "Forecast_Accuracy"]:
        if col in fin.columns:
            fin[col] = pd.to_numeric(
                fin[col].astype(str).str.replace("%", "").str.strip(),
                errors="coerce",
            )

    # Ensure datetime column
    if "ds" not in fin.columns:
        fin["ds"] = pd.to_datetime(fin["Period"], format="%b-%Y", errors="coerce")
    fin = fin.dropna(subset=["ds"]).sort_values("ds")
    fin["month_label"] = fin["ds"].dt.strftime("%b %Y")

    # ── Derived KPIs ─────────────────────────────────────────
    latest       = fin.iloc[-1]
    prev         = fin.iloc[-2]
    avg_margin   = fin["Profit_Margin"].mean()
    latest_rev   = latest["Revenue"]
    latest_cf    = latest["Cash_Flow"]
    latest_burn  = latest["Burn_Rate"]
    rev_growth   = (latest["Revenue"]   - prev["Revenue"])   / prev["Revenue"]   * 100
    cf_growth    = (latest["Cash_Flow"] - prev["Cash_Flow"]) / prev["Cash_Flow"] * 100
    best_month   = fin.loc[fin["Revenue"].idxmax(), "month_label"]
    worst_month  = fin.loc[fin["Revenue"].idxmin(), "month_label"]

    # ── Hero Banner ───────────────────────────────────────────
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{PRIMARY},{PRIMARY_DARK});
                border-radius:16px; padding:28px 36px; color:white;
                margin-bottom:24px; position:relative; overflow:hidden;">
        <div style="position:absolute;right:36px;top:50%;transform:translateY(-50%);
                    font-family:'Material Icons';font-size:80px;opacity:0.12;color:white;">
            trending_up
        </div>
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
            <span class="material-icons" style="color:rgba(255,255,255,0.9);font-size:20px;">psychology</span>
            <span style="font-size:12px;font-weight:600;font-family:{FONT};
                         background:rgba(255,255,255,0.2);border-radius:20px;
                         padding:3px 12px;">AI-Powered Forecasting</span>
        </div>
        <div style="font-size:24px;font-weight:800;font-family:{FONT};
                    letter-spacing:-0.5px;margin-bottom:6px;">
            Cash Flow Forecast Center
        </div>
        <div style="font-size:13px;opacity:0.88;font-family:{FONT};">
            24-month revenue forecasting using Facebook Prophet ML model
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── ROW 1: KPI Cards ─────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)

    rev_dir = "up"   if rev_growth > 0 else "down"
    cf_dir  = "up"   if cf_growth  > 0 else "down"

    with k1:
        st.markdown(
            kpi_card("Latest Revenue",
                     f"₹{latest_rev/1e6:.2f}M",
                     f"{'↑' if rev_growth>0 else '↓'} {abs(rev_growth):.1f}% vs last month",
                     "payments",
                     f"{abs(rev_growth):.1f}%", rev_dir, PRIMARY),
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            kpi_card("Latest Cash Flow",
                     f"₹{latest_cf/1e5:.1f}L",
                     f"{'↑' if cf_growth>0 else '↓'} {abs(cf_growth):.1f}% vs last month",
                     "account_balance",
                     f"{abs(cf_growth):.1f}%", cf_dir, "#06B6D4"),
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            kpi_card("Avg Profit Margin",
                     f"{avg_margin:.1f}%",
                     f"Over {len(fin)} months",
                     "bar_chart", " ", "neutral", SUCCESS),
            unsafe_allow_html=True,
        )
    with k4:
        st.markdown(
            kpi_card("Monthly Burn Rate",
                     f"₹{latest_burn/1e3:.0f}K",
                     "Latest month",
                     "local_fire_department", " ", "neutral", WARNING),
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Forecast Configuration ────────────────────────────────
    section_header(
        "Forecast Configuration",
        "Select metric and horizon, then generate the Prophet ML model",
    )

    cfg1, cfg2, cfg3 = st.columns([2, 2, 3])
    with cfg1:
        forecast_periods = st.selectbox(
            "Forecast Period",
            options=[3, 6, 12, 18, 24],
            index=2,
            format_func=lambda x: f"{x} Months",
        )
    with cfg2:
        forecast_target = st.selectbox(
            "Forecast Metric",
            options=["Revenue", "Cash_Flow", "Net_Profit", "EBITDA"],
            format_func=lambda x: x.replace("_", " "),
        )
    with cfg3:
        st.markdown("<br>", unsafe_allow_html=True)
        run_forecast = st.button(
            "Generate Forecast",
            type="primary",
            use_container_width=False,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Historical Performance Chart ──────────────────────────
    section_header(
        "Historical Performance",
        "Revenue, Net Profit and Cash Flow across all recorded months",
    )
    st.plotly_chart(_chart_historical(fin), use_container_width=True)

    # ── Prophet Forecast ─────────────────────────────────────
    if run_forecast or st.session_state.get("forecast_ran"):

        if run_forecast or "forecast_result" not in st.session_state:
            with st.spinner(
                f"Running Prophet model — "
                f"{forecast_periods}-month {forecast_target.replace('_',' ')} forecast..."
            ):
                forecast, model, err = run_prophet(
                    fin, periods=forecast_periods, target_col=forecast_target
                )

            if err == "prophet_not_installed":
                alert_box("Prophet is not installed. Run: pip install prophet", "error")
                return
            elif err:
                alert_box(f"Forecast error: {err}", "error")
                return

            st.session_state["forecast_result"]  = forecast
            st.session_state["forecast_target"]  = forecast_target
            st.session_state["forecast_periods"] = forecast_periods
            st.session_state["forecast_ran"]     = True

        # Restore from session state
        forecast         = st.session_state["forecast_result"]
        forecast_target  = st.session_state.get("forecast_target",  forecast_target)
        forecast_periods = st.session_state.get("forecast_periods", forecast_periods)
        fc_only          = forecast[forecast["ds"] > fin["ds"].max()].head(forecast_periods)

        st.markdown("<br>", unsafe_allow_html=True)
        section_header(
            f"{forecast_periods}-Month {forecast_target.replace('_', ' ')} Forecast",
            "Shaded area represents the 80% confidence interval",
        )
        st.plotly_chart(
            _chart_prophet(fin, forecast, forecast_target, forecast_periods),
            use_container_width=True,
        )

        # ── What-If Scenario Simulator ────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        section_header(
            "What-If Scenario Simulator",
            "Adjust revenue and expense assumptions to see projected impact",
        )

        sl1, sl2 = st.columns(2)
        with sl1:
            rev_adj = st.slider(
                "Revenue Change (%)",
                min_value=-30, max_value=50, value=0, step=5,
                help="Simulate revenue growth or decline",
            )
        with sl2:
            exp_adj = st.slider(
                "Expense Change (%)",
                min_value=-30, max_value=50, value=0, step=5,
                help="Simulate cost reduction or increase",
            )

        base_next_rev = fc_only["yhat"].iloc[0] if len(fc_only) > 0 else latest_rev
        base_expense  = fin["Operating_Expenses"].mean() + fin["COGS"].mean()
        adj_rev       = base_next_rev * (1 + rev_adj / 100)
        adj_exp       = base_expense  * (1 + exp_adj / 100)
        adj_profit    = adj_rev - adj_exp
        adj_margin    = (adj_profit / adj_rev * 100) if adj_rev > 0 else 0

        # Pre-compute all scenario deltas before f-strings
        d_rev  = adj_rev   - base_next_rev
        d_exp  = adj_exp   - base_expense
        c_rev  = SUCCESS if d_rev  >= 0 else DANGER
        c_exp  = DANGER  if d_exp  >= 0 else SUCCESS
        c_pro  = SUCCESS if adj_profit >= 0 else DANGER
        c_mar  = SUCCESS if adj_margin >= avg_margin else DANGER

        sc1, sc2, sc3, sc4 = st.columns(4)
        scenario_cards = [
            (sc1, "Projected Revenue",  f"₹{adj_rev/1e6:.2f}M",    f"{'↑' if d_rev>=0 else '↓'} ₹{abs(d_rev)/1e5:.1f}L vs base", c_rev,  "payments"),
            (sc2, "Projected Expenses", f"₹{adj_exp/1e6:.2f}M",    f"{'↑' if d_exp>=0 else '↓'} ₹{abs(d_exp)/1e5:.1f}L vs base", c_exp,  "receipt_long"),
            (sc3, "Net Profit",         f"₹{adj_profit/1e6:.2f}M", "Scenario projection",                                          c_pro,  "trending_up"),
            (sc4, "Profit Margin",      f"{adj_margin:.1f}%",       f"Avg: {avg_margin:.1f}%",                                      c_mar,  "bar_chart"),
        ]
        for col, title, value, sub, color, icon in scenario_cards:
            with col:
                st.markdown(
                    kpi_card(title, value, sub, icon, "", "neutral", color),
                    unsafe_allow_html=True,
                )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Monthly Forecast Table ────────────────────────────
        section_header(
            "Monthly Forecast Breakdown",
            "Predicted values with confidence range and month-on-month trend",
        )

        fc_table = fc_only.copy()
        fc_table["Month"]    = fc_table["ds"].dt.strftime("%b %Y")
        fc_table["Forecast"] = fc_table["yhat"].round(0)
        fc_table["Lower"]    = fc_table["yhat_lower"].round(0)
        fc_table["Upper"]    = fc_table["yhat_upper"].round(0)
        fc_table["MoM"]      = fc_table["Forecast"].pct_change() * 100
        fc_table["MoM"]      = fc_table["MoM"].fillna(
            (fc_table["Forecast"].iloc[0] - latest_rev) / latest_rev * 100
        )

        rows_html = ""
        for _, row in fc_table.iterrows():
            mom       = row["MoM"]
            mom_c     = SUCCESS if mom >= 0 else DANGER
            mom_bg    = SUCCESS_BG if mom >= 0 else DANGER_BG
            trend_lbl = "Growing" if mom >= 0 else "Declining"
            arrow     = "▲" if mom >= 0 else "▼"
            rows_html += (
                f'<div style="display:grid;grid-template-columns:1.2fr 1fr 1fr 1fr 1fr 1fr;'
                f'padding:12px 0;border-bottom:1px solid #F3F4F6;'
                f'align-items:center;font-size:12px;color:{TEXT_PRIMARY};font-family:{FONT};">'
                f'<div style="font-weight:600;">{row["Month"]}</div>'
                f'<div style="font-weight:700;color:{PRIMARY};">₹{row["Forecast"]/1e6:.2f}M</div>'
                f'<div style="color:{TEXT_MUTED};">₹{row["Lower"]/1e6:.2f}M</div>'
                f'<div style="color:{TEXT_MUTED};">₹{row["Upper"]/1e6:.2f}M</div>'
                f'<div style="color:{mom_c};font-weight:600;">{arrow} {abs(mom):.1f}%</div>'
                f'<div><span style="background:{mom_bg};color:{mom_c};padding:3px 10px;'
                f'border-radius:20px;font-size:11px;font-weight:600;">{trend_lbl}</span></div>'
                f'</div>'
            )

        hdr_style = (
            f"display:grid;grid-template-columns:1.2fr 1fr 1fr 1fr 1fr 1fr;"
            f"padding:10px 0;border-bottom:2px solid {BORDER};"
            f"font-size:11px;font-weight:700;color:{TEXT_MUTED};"
            f"text-transform:uppercase;letter-spacing:0.5px;font-family:{FONT};"
        )
        st.markdown(
            f'<div style="background:{WHITE};border:1px solid {BORDER};'
            f'border-radius:14px;padding:0 24px 8px 24px;'
            f'box-shadow:0 1px 4px rgba(0,0,0,0.04);">'
            f'<div style="{hdr_style}">'
            f'<div>Month</div><div>Forecast</div><div>Lower Bound</div>'
            f'<div>Upper Bound</div><div>MoM Growth</div><div>Trend</div>'
            f'</div>'
            f'{rows_html}'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

    else:
        alert_box(
            "Select your forecast period and metric above, "
            "then click <b>Generate Forecast</b> to run the Prophet ML model.",
            "info",
        )

    # ── AI Insights ───────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    section_header("AI Cash Flow Insights", "Data-driven observations for this period")

    avg_yoy       = fin["YoY_Growth"].mean() if "YoY_Growth" in fin.columns else 0
    avg_burn      = fin["Burn_Rate"].mean()
    runway_months = int(latest_cf / avg_burn) if avg_burn > 0 else 0
    pos_cf_months = int((fin["Cash_Flow"] > 0).sum())
    latest_margin = fin["Profit_Margin"].iloc[-1]
    margin_trend  = "improving" if latest_margin > avg_margin else "declining"
    m_color       = SUCCESS if margin_trend == "improving" else DANGER

    ia, ib, ic = st.columns(3)

    insight_cards = [
        (ia, "Revenue Growth",
         f"₹{fin['Revenue'].max()/1e6:.1f}M",
         f"Best month: {best_month}",
         f"Average YoY growth of {avg_yoy:.1f}% across {len(fin)} months.",
         SUCCESS_BG, SUCCESS, "trending_up"),

        (ib, "Cash Runway",
         f"{runway_months} Months",
         "At current burn rate",
         f"Monthly burn ₹{avg_burn/1e3:.0f}K. "
         f"{pos_cf_months} of {len(fin)} months had positive cash flow.",
         "#EFF6FF", PRIMARY, "account_balance"),

        (ic, "Margin Trend",
         f"{latest_margin:.1f}%",
         f"Margin is {margin_trend}",
         f"Current {latest_margin:.1f}% vs avg {avg_margin:.1f}%. Worst month: {worst_month}.",
         WARNING_BG, m_color, "bar_chart"),
    ]

    for col, title, value, sub, body, bg, color, icon in insight_cards:
        with col:
            st.markdown(f"""
            <div style="background:{WHITE};border:1px solid {BORDER};border-radius:14px;
                        padding:20px;box-shadow:0 1px 4px rgba(0,0,0,0.04);height:100%;">
                <div style="width:38px;height:38px;border-radius:10px;background:{bg};
                            display:flex;align-items:center;justify-content:center;
                            margin-bottom:12px;">
                    <span class="material-icons" style="color:{color};font-size:20px;">{icon}</span>
                </div>
                <div style="font-size:13px;font-weight:700;color:{TEXT_PRIMARY};
                            font-family:{FONT};margin-bottom:6px;">{title}</div>
                <div style="font-size:20px;font-weight:800;color:{TEXT_PRIMARY};
                            font-family:{FONT};letter-spacing:-0.5px;margin-bottom:4px;">{value}</div>
                <div style="font-size:12px;font-weight:600;color:{color};
                            font-family:{FONT};margin-bottom:6px;">{sub}</div>
                <div style="font-size:12px;color:{TEXT_MUTED};
                            font-family:{FONT};line-height:1.6;">{body}</div>
            </div>
            """, unsafe_allow_html=True)

    # Store summary for AI Assistant
    st.session_state["forecast_summary"] = (
        f"Cash flow forecast: Latest revenue ₹{latest_rev/1e6:.2f}M, "
        f"avg margin {avg_margin:.1f}%, "
        f"cash runway {runway_months} months, "
        f"best revenue month {best_month}."
    )