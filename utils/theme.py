"""
utils/theme.py
==============
Centralized Design System for AI-CFO Platform
Blue-and-white SaaS theme inspired by Zoho Books, QuickBooks, and Stripe.

Usage:
    from utils.theme import inject_theme, kpi_card, section_header, card, style_plotly_fig, alert_box
"""

import streamlit as st
import plotly.graph_objects as go

# ─────────────────────────────────────────────────────────────
# DESIGN TOKENS
# ─────────────────────────────────────────────────────────────

# Primary palette — blue-and-white SaaS
PRIMARY       = "#2563EB"   # Primary Blue
PRIMARY_LIGHT = "#60A5FA"   # Light Blue
PRIMARY_DARK  = "#1D4ED8"   # Dark Blue
PRIMARY_BG    = "#EFF6FF"   # Faint blue background
WHITE         = "#FFFFFF"
SURFACE       = "#F8FAFC"   # Page background
BORDER        = "#E5E7EB"   # Subtle border
BORDER_DARK   = "#D1D5DB"

# Semantic colors
SUCCESS       = "#10B981"   # Green
SUCCESS_BG    = "#ECFDF5"
WARNING       = "#F59E0B"   # Amber
WARNING_BG    = "#FFFBEB"
DANGER        = "#EF4444"   # Red
DANGER_BG     = "#FEF2F2"
INFO          = "#3B82F6"   # Blue
INFO_BG       = "#EFF6FF"

# Text
TEXT_PRIMARY  = "#111827"
TEXT_SECONDARY= "#6B7280"
TEXT_MUTED    = "#9CA3AF"

# Chart palette — ordered for use in Plotly traces
CHART_PALETTE = [
    PRIMARY,        # #2563EB
    SUCCESS,        # #10B981
    WARNING,        # #F59E0B
    DANGER,         # #EF4444
    PRIMARY_LIGHT,  # #60A5FA
    PRIMARY_DARK,   # #1D4ED8
    "#8B5CF6",      # Violet
    "#06B6D4",      # Cyan
    "#F97316",      # Orange
    "#84CC16",      # Lime
]

# Typography
FONT = "'Manrope', 'Inter', sans-serif"


# ─────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────

_GLOBAL_CSS = f"""
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">

<style>
/* ── Reset & Base ── */
*, *::before, *::after {{ box-sizing: border-box; }}

html, body, [data-testid="stAppViewContainer"] {{
    font-family: {FONT} !important;
    background-color: {SURFACE} !important;
    color: {TEXT_PRIMARY} !important;
}}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header {{ visibility: hidden; }}
[data-testid="stDecoration"] {{ display: none; }}
[data-testid="stToolbar"] {{ display: none; }}

/* ── Main content ── */
.main .block-container {{
    padding-top: 1.2rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100% !important;
}}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background-color: {WHITE} !important;
    border-right: 1px solid {BORDER} !important;
    padding-top: 0 !important;
}}
[data-testid="stSidebar"] > div:first-child {{
    padding-top: 0 !important;
}}

/* Sidebar radio nav */
[data-testid="stSidebar"] .stRadio > div {{ gap: 2px !important; }}

[data-testid="stSidebar"] .stRadio label {{
    display: flex !important;
    align-items: center !important;
    padding: 10px 16px !important;
    border-radius: 8px !important;
    margin: 1px 8px !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
    font-size: 13.5px !important;
    font-weight: 500 !important;
    color: {TEXT_SECONDARY} !important;
    background: transparent !important;
    border: none !important;
}}
[data-testid="stSidebar"] .stRadio label:hover {{
    background: {PRIMARY_BG} !important;
    color: {PRIMARY_DARK} !important;
}}
/* Sidebar menu text */
[data-testid="stSidebar"] .stRadio label p {{
    color: #2563EB !important;
    font-size: 15px !important;
    font-weight: 600 !important;
}}

/* Selected page */
[data-testid="stSidebar"] .stRadio label[data-checked="true"] p {{
    color: #1D4ED8 !important;
    font-weight: 700 !important;
}}
[data-testid="stSidebar"] .stRadio label[data-checked="true"] {{
    background: {PRIMARY_BG} !important;
    color: {PRIMARY} !important;
    font-weight: 600 !important;
}}
[data-testid="stSidebar"] .stRadio > div > label > div:first-child {{
    display: none !important;
}}

/* ── Typography ── */
h1 {{
    font-size: 22px !important; font-weight: 800 !important;
    color: {TEXT_PRIMARY} !important; letter-spacing: -0.5px !important;
}}
h2 {{
    font-size: 17px !important; font-weight: 700 !important;
    color: {TEXT_PRIMARY} !important;
}}
h3 {{
    font-size: 14px !important; font-weight: 700 !important;
    color: {TEXT_PRIMARY} !important;
}}

/* ── Streamlit native metric ── */
[data-testid="metric-container"] {{
    background: {WHITE} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 12px !important;
    padding: 18px 20px !important;
}}
[data-testid="stMetricLabel"] {{
    font-size: 11px !important; font-weight: 600 !important;
    color: {TEXT_MUTED} !important;
    text-transform: uppercase !important; letter-spacing: 0.5px !important;
}}
[data-testid="stMetricValue"] {{
    font-size: 24px !important; font-weight: 800 !important;
    color: {TEXT_PRIMARY} !important; letter-spacing: -0.5px !important;
}}
[data-testid="stMetricDelta"] svg {{ display: none; }}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
    background: transparent !important;
    border-bottom: 2px solid {BORDER} !important;
    gap: 0 !important;
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent !important; border: none !important;
    color: {TEXT_MUTED} !important;
    font-size: 13px !important; font-weight: 600 !important;
    padding: 10px 20px !important;
    border-bottom: 2px solid transparent !important;
    margin-bottom: -2px !important;
    font-family: {FONT} !important;
}}
.stTabs [aria-selected="true"] {{
    color: {PRIMARY} !important;
    border-bottom: 2px solid {PRIMARY} !important;
}}

/* ── Buttons ── */
.stButton > button {{
    background: {PRIMARY} !important;
    color: {WHITE} !important; border: none !important;
    border-radius: 8px !important;
    font-size: 13px !important; font-weight: 600 !important;
    padding: 8px 20px !important;
    font-family: {FONT} !important;
    transition: all 0.15s ease !important;
}}
.stButton > button:hover {{
    background: {PRIMARY_DARK} !important;
    box-shadow: 0 4px 12px rgba(37,99,235,0.3) !important;
}}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {{
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}}

/* ── Selectbox / inputs ── */
.stSelectbox > div > div,
.stTextInput > div > div,
.stNumberInput > div > div {{
    border-radius: 8px !important;
    border-color: {BORDER} !important;
    font-size: 13px !important;
    font-family: {FONT} !important;
}}

/* ── Alerts ── */
.stAlert {{
    border-radius: 10px !important;
    border: none !important;
    font-size: 13px !important;
}}

/* ── Slider ── */
.stSlider > div > div > div > div {{
    background: {PRIMARY} !important;
}}

/* ── Divider ── */
hr {{ border-color: {BORDER} !important; margin: 1rem 0 !important; }}

/* ── Expander ── */
[data-testid="stExpander"] {{
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
}}

/* ── Material Icons alignment helper ── */
.material-icons {{
    vertical-align: middle;
    font-size: 18px !important;
    color: {PRIMARY};
}}

/* ── Sidebar data pills ── */
.data-pill {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 8px 16px; margin: 2px 8px;
    background: {SURFACE}; border-radius: 8px;
    font-size: 12px; color: {TEXT_SECONDARY};
}}
.data-pill span {{ font-weight: 600; color: {PRIMARY}; }}

/* ── Nav section label ── */
.nav-section {{
    font-size: 10px; font-weight: 700;
    color: {TEXT_MUTED}; letter-spacing: 1px;
    text-transform: uppercase;
    padding: 12px 24px 4px 24px;
}}

/* ── Sidebar logo area ── */
.sidebar-logo {{
    background: {WHITE};
    padding: 20px 20px 16px 20px;
    border-bottom: 1px solid {BORDER};
    margin-bottom: 8px;
}}
.sidebar-logo-text {{
    font-size: 18px; font-weight: 800;
    color: {TEXT_PRIMARY}; letter-spacing: -0.5px;
}}
.sidebar-logo-sub {{
    font-size: 11px; color: {TEXT_MUTED};
    margin-top: 2px; font-weight: 500;
}}

/* ── Status badges ── */
.badge-green  {{ background:{SUCCESS_BG}; color:{SUCCESS};  padding:3px 10px; border-radius:20px; font-size:11px; font-weight:600; display:inline-block; }}
.badge-red    {{ background:{DANGER_BG};  color:{DANGER};   padding:3px 10px; border-radius:20px; font-size:11px; font-weight:600; display:inline-block; }}
.badge-amber  {{ background:{WARNING_BG}; color:{WARNING};  padding:3px 10px; border-radius:20px; font-size:11px; font-weight:600; display:inline-block; }}
.badge-blue   {{ background:{INFO_BG};    color:{INFO};     padding:3px 10px; border-radius:20px; font-size:11px; font-weight:600; display:inline-block; }}
</style>
"""


# ─────────────────────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────────────────────

def inject_theme() -> None:
    """
    Inject the global CSS, Google Fonts, and Material Icons CDN into the page.
    Call once at the top of app.py before any page content.
    """
    st.markdown(_GLOBAL_CSS, unsafe_allow_html=True)


def card(html_content: str, style: str = "") -> None:
    """
    Render content inside a premium white card with rounded corners and a soft shadow.

    Args:
        html_content: Raw HTML string to embed inside the card.
        style: Optional additional inline CSS to apply to the card wrapper.
    """
    st.markdown(f"""
    <div style="background:{WHITE}; border:1px solid {BORDER}; border-radius:16px;
                padding:24px; box-shadow:0 1px 6px rgba(0,0,0,0.05); {style}">
        {html_content}
    </div>
    """, unsafe_allow_html=True)


def kpi_card(
    title: str,
    value: str,
    subtext: str = "",
    icon: str = "analytics",
    delta: str = "",
    delta_direction: str = "up",
    accent_color: str = PRIMARY,
) -> str:
    """
    Return an HTML string for a Zoho-style KPI card with a Material Icon.

    Args:
        title:            Metric label (e.g. "Total Revenue").
        value:            Formatted primary value (e.g. "₹24.8L").
        subtext:          Small descriptor line below the value.
        icon:             Material Icons ligature name (e.g. "payments", "warning").
        delta:            Change text (e.g. "+12.4%"). Empty string hides the badge.
        delta_direction:  "up" → green badge, "down" → red badge, "neutral" → blue.
        accent_color:     Left-border accent hex color.

    Returns:
        HTML string — pass directly to st.markdown(..., unsafe_allow_html=True).
    """
    if delta:
        if delta_direction == "up":
            delta_html = f'<span style="background:{SUCCESS_BG};color:{SUCCESS};padding:2px 8px;border-radius:20px;font-size:11px;font-weight:600;display:inline-block;margin-top:8px;">▲ {delta}</span>'
        elif delta_direction == "down":
            delta_html = f'<span style="background:{DANGER_BG};color:{DANGER};padding:2px 8px;border-radius:20px;font-size:11px;font-weight:600;display:inline-block;margin-top:8px;">▼ {delta}</span>'
        else:
            delta_html = f'<span style="background:{INFO_BG};color:{INFO};padding:2px 8px;border-radius:20px;font-size:11px;font-weight:600;display:inline-block;margin-top:8px;">— {delta}</span>'
    else:
        delta_html = ""

    return f"""
    <div style="background:{WHITE}; border:1px solid {BORDER};
                border-left:4px solid {accent_color};
                border-radius:12px; padding:20px 22px;
                box-shadow:0 1px 4px rgba(0,0,0,0.04);
                transition:box-shadow 0.2s ease;">
        <div style="display:flex; align-items:flex-start; gap:14px;">
            <span class="material-icons"
                  style="color:{accent_color}; font-size:22px; margin-top:2px;">{icon}</span>
            <div style="flex:1;">
                <div style="font-size:10px; font-weight:700; color:{TEXT_MUTED};
                            text-transform:uppercase; letter-spacing:0.8px;
                            margin-bottom:6px; font-family:{FONT};">{title}</div>
                <div style="font-size:26px; font-weight:800; color:{TEXT_PRIMARY};
                            line-height:1.1; letter-spacing:-0.5px;
                            font-family:{FONT};">{value}</div>
                <div style="font-size:12px; color:{TEXT_MUTED}; margin-top:5px;
                            font-family:{FONT};">{subtext}</div>
                {delta_html}
            </div>
        </div>
    </div>
    """


def section_header(title: str, subtitle: str = "") -> None:
    """
    Render a standardized section heading with optional subtitle.
    """
    sub_html = f'<div style="font-size:12px;color:{TEXT_MUTED};margin-top:3px;font-family:{FONT};">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
    <div style="margin-bottom:16px;">
        <div style="font-size:15px; font-weight:700; color:{TEXT_PRIMARY};
                    font-family:{FONT}; letter-spacing:-0.2px;">{title}</div>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


def style_plotly_fig(
    fig: go.Figure,
    height: int = 320,
    show_legend: bool = True,
) -> go.Figure:
    """
    Apply the AI-CFO design system to a Plotly figure.
    Standardizes background, font, gridlines, margins, and color palette.

    Args:
        fig:          Any Plotly Figure object.
        height:       Chart height in pixels.
        show_legend:  Whether to display the legend.

    Returns:
        The same fig object, mutated in-place and returned for chaining.
    """
    fig.update_layout(
        height=height,
        paper_bgcolor=WHITE,
        plot_bgcolor=WHITE,
        font=dict(family=FONT, color=TEXT_SECONDARY, size=11),
        showlegend=show_legend,
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=TEXT_SECONDARY, size=11),
            orientation="h",
            x=0, y=-0.25,
            xanchor="left", yanchor="top",
        ),
        margin=dict(l=12, r=12, t=16, b=16),
        xaxis=dict(
            showgrid=False,
            linecolor=BORDER,
            tickfont=dict(size=10, color=TEXT_MUTED),
            color=TEXT_MUTED,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#F3F4F6",
            linecolor=BORDER,
            tickfont=dict(size=10, color=TEXT_MUTED),
            color=TEXT_MUTED,
            zeroline=False,
        ),
        colorway=CHART_PALETTE,
    )
    return fig


def alert_box(text: str, kind: str = "info") -> None:
    """
    Render a styled callout box with a Material Icon. No emojis.

    Args:
        text: Alert message.
        kind: "info" | "success" | "warning" | "error"
    """
    config = {
        "info":    (INFO,    INFO_BG,    "info",          "Info"),
        "success": (SUCCESS, SUCCESS_BG, "check_circle",  "Success"),
        "warning": (WARNING, WARNING_BG, "warning",       "Warning"),
        "error":   (DANGER,  DANGER_BG,  "error",         "Error"),
    }
    color, bg, icon, label = config.get(kind, config["info"])
    st.markdown(f"""
    <div style="background:{bg}; border:1px solid {color}33;
                border-left:4px solid {color};
                border-radius:10px; padding:14px 18px;
                display:flex; align-items:flex-start; gap:12px;
                margin:8px 0;">
        <span class="material-icons" style="color:{color}; font-size:20px; flex-shrink:0;">{icon}</span>
        <div style="font-size:13px; color:{TEXT_PRIMARY}; font-family:{FONT}; line-height:1.6;">{text}</div>
    </div>
    """, unsafe_allow_html=True)