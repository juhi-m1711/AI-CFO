import streamlit as st
import google.generativeai as genai

from utils.theme import (
    inject_theme,
    section_header,
    alert_box
)


# ─────────────────────────────────────────
# BUILD BUSINESS CONTEXT
# ─────────────────────────────────────────
def build_context():

    context = []

    if "forecast_summary" in st.session_state:
        context.append(
            "Cash Forecast:\n"
            + st.session_state["forecast_summary"]
        )

    if "fraud_summary" in st.session_state:
        context.append(
            "Fraud Analysis:\n"
            + st.session_state["fraud_summary"]
        )

    if "analytics_summary" in st.session_state:
        context.append(
            "Analytics:\n"
            + st.session_state["analytics_summary"]
        )

    if "reports_summary" in st.session_state:
        context.append(
            "Reports:\n"
            + st.session_state["reports_summary"]
        )

    return "\n\n".join(context)


# ─────────────────────────────────────────
# GEMINI RESPONSE
# ─────────────────────────────────────────
def ask_gemini(question):

    api_key = st.session_state.get(
        "gemini_api_key",
        ""
    )

    if not api_key:

        return (
            "Gemini API key not configured. "
            "Please add it in Settings → AI Settings."
        )

    genai.configure(
        api_key=api_key
    )

    model_name = st.session_state.get(
        "gemini_model",
        "gemini-2.5-flash"
    )

    model = genai.GenerativeModel(
        model_name
    )

    business_context = build_context()

    prompt = f"""
You are an AI CFO assistant.

Use the following business context:

{business_context}

Answer professionally and provide
actionable financial recommendations.

Question:
{question}
"""

    response = model.generate_content(
        prompt
    )

    return response.text

# ─────────────────────────────────────────
# MAIN PAGE
# ─────────────────────────────────────────
def show():

    inject_theme()

    # -----------------------------------
    # CHAT HISTORY
    # -----------------------------------
    if "chat_history" not in st.session_state:

        st.session_state["chat_history"] = []

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

        AI CFO Assistant

        </h1>

        <p style="
        margin-top:10px;
        opacity:.92;
        font-size:14px;">

        Ask questions about your finances,
        compliance, forecasts and risks.

        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    # -----------------------------------
    # SUGGESTED PROMPTS
    # -----------------------------------
    section_header(
        "Suggested Questions",
        "Quick business insights"
    )

    p1, p2 = st.columns(2)

    with p1:

        if st.button(
            "How healthy is my business?",
            use_container_width=True
        ):
            st.session_state["preset_prompt"] = (
                "How healthy is my business?"
            )

        if st.button(
            "Summarize my financial performance",
            use_container_width=True
        ):
            st.session_state["preset_prompt"] = (
                "Summarize my financial performance."
            )

        if st.button(
            "Identify key risks",
            use_container_width=True
        ):
            st.session_state["preset_prompt"] = (
                "Identify the biggest risks in the business."
            )

    with p2:

        if st.button(
            "Analyze cash flow",
            use_container_width=True
        ):
            st.session_state["preset_prompt"] = (
                "Analyze my cash flow."
            )

        if st.button(
            "Review fraud exposure",
            use_container_width=True
        ):
            st.session_state["preset_prompt"] = (
                "Review fraud exposure."
            )

        if st.button(
            "Give strategic recommendations",
            use_container_width=True
        ):
            st.session_state["preset_prompt"] = (
                "Provide strategic recommendations."
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # -----------------------------------
    # CHAT HISTORY DISPLAY
    # -----------------------------------
    section_header(
        "Conversation",
        "Chat with your AI CFO"
    )

    for item in st.session_state["chat_history"]:

        with st.chat_message(item["role"]):

            st.markdown(
                item["content"]
            )

    # -----------------------------------
    # INPUT
    # -----------------------------------
    question = st.chat_input(
        "Ask your AI CFO..."
    )

    if not question:

        question = st.session_state.pop(
            "preset_prompt",
            None
        )

    # -----------------------------------
    # GENERATE RESPONSE
    # -----------------------------------
    if question:

        st.session_state[
            "chat_history"
        ].append(
            {
                "role": "user",
                "content": question
            }
        )

        with st.chat_message("user"):

            st.markdown(
                question
            )

        with st.chat_message("assistant"):

            with st.spinner(
                "Analyzing..."
            ):

                try:

                    answer = ask_gemini(
                        question
                    )

                except Exception as e:

                    answer = (
                        "Error:\n\n"
                        + str(e)
                    )

                st.markdown(
                    answer
                )

        st.session_state[
            "chat_history"
        ].append(
            {
                "role": "assistant",
                "content": answer
            }
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------
    # AI STATUS
    # ------------------------------------------------
    section_header(
        "AI Status",
        "Active intelligence sources"
    )

    forecast_ok = (
        "forecast_summary"
        in st.session_state
    )

    fraud_ok = (
        "fraud_summary"
        in st.session_state
    )

    analytics_ok = (
        "analytics_summary"
        in st.session_state
    )

    reports_ok = (
        "reports_summary"
        in st.session_state
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        alert_box(
            (
                "Forecast context loaded"
                if forecast_ok
                else "Forecast context unavailable"
            ),
            (
                "success"
                if forecast_ok
                else "warning"
            )
        )

    with c2:

        alert_box(
            (
                "Fraud analysis loaded"
                if fraud_ok
                else "Fraud analysis unavailable"
            ),
            (
                "success"
                if fraud_ok
                else "warning"
            )
        )

    with c3:

        alert_box(
            (
                "Analytics context loaded"
                if analytics_ok
                else "Analytics context unavailable"
            ),
            (
                "success"
                if analytics_ok
                else "warning"
            )
        )

    with c4:

        alert_box(
            (
                "Reports summary loaded"
                if reports_ok
                else "Reports summary unavailable"
            ),
            (
                "success"
                if reports_ok
                else "warning"
            )
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------
    # CONTEXT SOURCES
    # ------------------------------------------------
    section_header(
        "Business Context Sources",
        "Information available to the AI CFO"
    )

    sources = []

    if forecast_ok:
        sources.append("Cash Flow Forecast")

    if fraud_ok:
        sources.append("Fraud Detection")

    if analytics_ok:
        sources.append("Analytics Center")

    if reports_ok:
        sources.append("Reports Center")

    if len(sources) == 0:

        alert_box(
            "No summaries have been generated yet. "
            "Run Forecast, Fraud Detection, Analytics and Reports modules first.",
            "warning"
        )

    else:

        st.success(
            "Active Context Sources:\n\n• "
            + "\n• ".join(sources)
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------
    # CHAT CONTROLS
    # ------------------------------------------------
    section_header(
        "Conversation Controls",
        "Manage chat history"
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "Clear Conversation",
            use_container_width=True
        ):

            st.session_state[
                "chat_history"
            ] = []

            st.rerun()

    with col2:

        if st.button(
            "Clear AI Summaries",
            use_container_width=True
        ):

            st.session_state.pop(
                "forecast_summary",
                None
            )

            st.session_state.pop(
                "fraud_summary",
                None
            )

            st.session_state.pop(
                "analytics_summary",
                None
            )

            st.session_state.pop(
                "reports_summary",
                None
            )

            alert_box(
                "AI summaries cleared successfully.",
                "success"
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------
    # SYSTEM MESSAGE
    # ------------------------------------------------
    section_header(
        "AI Assistant Information",
        "About your AI CFO"
    )

    st.info(
        """
AI CFO Assistant uses Google Gemini and combines information from:

• Cash Flow Forecasting

• Fraud Detection

• Analytics Center

• Reports Center

to provide strategic and actionable recommendations.

For best results, run those modules first before asking questions.
"""
    )


