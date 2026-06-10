import streamlit as st

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

    # ------------------------------------------------
    # HERO
    # ------------------------------------------------
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

        Settings Center

        </h1>

        <p style="
        margin-top:10px;
        opacity:.92;
        font-size:14px;">

        Manage company preferences,
        AI configuration and data controls.

        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    # ------------------------------------------------
    # NAVIGATION
    # ------------------------------------------------
    view = st.radio(
        "",
        [
            "Company Profile",
            "AI Settings",
            "Data Management",
            "System"
        ],
        horizontal=True,
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)


    # =====================================================
    # COMPANY PROFILE
    # =====================================================
    if view == "Company Profile":

        section_header(
            "Company Profile",
            "Configure business information and defaults"
        )

        col1, col2 = st.columns(2)

        with col1:

            company_name = st.text_input(
                "Company Name",
                value=st.session_state.get(
                    "company_name",
                    "AI-CFO Demo Pvt Ltd"
                )
            )

            industry = st.selectbox(
                "Industry",
                [
                    "Technology",
                    "Manufacturing",
                    "Retail",
                    "Healthcare",
                    "Finance",
                    "Education",
                    "Other"
                ]
            )

            country = st.selectbox(
                "Country",
                [
                    "India",
                    "United States",
                    "United Kingdom",
                    "Canada",
                    "Australia"
                ]
            )

        with col2:

            currency = st.selectbox(
                "Currency",
                [
                    "INR (₹)",
                    "USD ($)",
                    "EUR (€)",
                    "GBP (£)"
                ]
            )

            financial_year = st.selectbox(
                "Financial Year",
                [
                    "2025-26",
                    "2026-27",
                    "2027-28"
                ]
            )

            tax_regime = st.selectbox(
                "Tax Regime",
                [
                    "GST",
                    "VAT",
                    "Corporate Tax"
                ]
            )

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button(
            "Save Company Settings",
            type="primary"
        ):

            st.session_state[
                "company_name"
            ] = company_name

            st.session_state[
                "industry"
            ] = industry

            st.session_state[
                "country"
            ] = country

            st.session_state[
                "currency"
            ] = currency

            st.session_state[
                "financial_year"
            ] = financial_year

            st.session_state[
                "tax_regime"
            ] = tax_regime

            alert_box(
                "Company settings saved successfully.",
                "success"
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # ------------------------------------------------
        # PROFILE SUMMARY
        # ------------------------------------------------
        p1, p2, p3, p4 = st.columns(4)

        with p1:

            kpi_card(
                "Company",
                st.session_state.get(
                    "company_name",
                    "AI-CFO Demo"
                ),
                "Business entity",
                "business"
            )

        with p2:

            kpi_card(
                "Industry",
                st.session_state.get(
                    "industry",
                    "Technology"
                ),
                "Sector",
                "domain"
            )

        with p3:

            kpi_card(
                "Currency",
                st.session_state.get(
                    "currency",
                    "INR (₹)"
                ),
                "Default currency",
                "payments"
            )

        with p4:

            kpi_card(
                "Financial Year",
                st.session_state.get(
                    "financial_year",
                    "2026-27"
                ),
                "Reporting period",
                "calendar_month"
            )

    # =====================================================
    # AI SETTINGS
    # =====================================================
    elif view == "AI Settings":

        section_header(
            "AI Configuration",
            "Configure AI Assistant and model parameters"
        )

        col1, col2 = st.columns(2)

        with col1:

            api_key = st.text_input(
                "Gemini API Key",
                value=st.session_state.get(
                    "gemini_api_key",
                    ""
                ),
                type="password"
            )

            model_name = st.selectbox(
                "Model",
                [
                    "gemini-2.5-flash",
                    "gemini-2.5-pro"
                ]
            )

        with col2:

            temperature = st.slider(
                "Temperature",
                0.0,
                1.0,
                0.3,
                0.1
            )

            max_tokens = st.slider(
                "Max Tokens",
                256,
                4096,
                2048,
                256
            )

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button(
            "Save AI Settings",
            type="primary"
        ):

            st.session_state[
                "gemini_api_key"
            ] = api_key

            st.session_state[
                "gemini_model"
            ] = model_name

            st.session_state[
                "gemini_temperature"
            ] = temperature

            st.session_state[
                "gemini_max_tokens"
            ] = max_tokens

            alert_box(
                "AI configuration saved successfully.",
                "success"
            )

        st.markdown("<br>", unsafe_allow_html=True)

        a1, a2, a3 = st.columns(3)

        with a1:

            kpi_card(
                "AI Model",
                st.session_state.get(
                    "gemini_model",
                    "gemini-2.5-flash"
                ),
                "Active model",
                "smart_toy"
            )

        with a2:

            kpi_card(
                "Temperature",
                str(
                    st.session_state.get(
                        "gemini_temperature",
                        0.3
                    )
                ),
                "Creativity level",
                "tune"
            )

        with a3:

            kpi_card(
                "Max Tokens",
                str(
                    st.session_state.get(
                        "gemini_max_tokens",
                        2048
                    )
                ),
                "Response length",
                "token"
            )

    # =====================================================
    # DATA MANAGEMENT
    # =====================================================
    elif view == "Data Management":

        section_header(
            "Data Management",
            "Manage uploaded datasets and session data"
        )

        d1, d2, d3 = st.columns(3)

        with d1:

            if st.button(
                "Clear Forecast Cache",
                use_container_width=True
            ):

                st.session_state.pop(
                    "forecast_result",
                    None
                )

                alert_box(
                    "Forecast cache cleared.",
                    "success"
                )

        with d2:

            if st.button(
                "Clear Fraud Results",
                use_container_width=True
            ):

                st.session_state.pop(
                    "ml_fraud_result",
                    None
                )

                alert_box(
                    "Fraud analysis cache cleared.",
                    "success"
                )

        with d3:

            if st.button(
                "Clear AI Summaries",
                use_container_width=True
            ):

                st.session_state.pop(
                    "forecast_summary",
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
                    "AI summaries cleared.",
                    "success"
                )

        st.markdown("<br>", unsafe_allow_html=True)

        k1, k2, k3 = st.columns(3)

        with k1:

            kpi_card(
                "Financial Dataset",
                "Loaded"
                if "financial_intelligence"
                in st.session_state
                else "Missing",
                "Financial records",
                "database"
            )

        with k2:

            kpi_card(
                "Compliance Dataset",
                "Loaded"
                if "compliance_data"
                in st.session_state
                else "Missing",
                "Compliance records",
                "fact_check"
            )

        with k3:

            kpi_card(
                "GST Dataset",
                "Loaded"
                if "gst_data"
                in st.session_state
                else "Missing",
                "GST records",
                "receipt_long"
            )

    # =====================================================
    # SYSTEM
    # =====================================================
    elif view == "System":

        section_header(
            "System Information",
            "Platform diagnostics and version details"
        )

        s1, s2, s3, s4 = st.columns(4)

        with s1:

            kpi_card(
                "Version",
                "1.0",
                "AI-CFO release",
                "verified"
            )

        with s2:

            kpi_card(
                "Theme",
                "Zoho Books",
                "Blue SaaS style",
                "palette"
            )

        with s3:

            kpi_card(
                "Modules",
                "12",
                "Active modules",
                "grid_view"
            )

        with s4:

            kpi_card(
                "Status",
                "Online",
                "Platform healthy",
                "cloud_done"
            )

        st.markdown("<br>", unsafe_allow_html=True)

        alert_box(
            "AI-CFO platform is running normally.",
            "success"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button(
            "Reset Platform Session",
            type="primary"
        ):

            st.session_state.clear()

            st.rerun()
