import streamlit as st

from modules import compliance
from modules import gst_tracker

from utils.theme import (
    inject_theme,
    section_header
)


# ─────────────────────────────────────────
# MAIN PAGE
# ─────────────────────────────────────────
def show():

    inject_theme()

    # -------------------------------------
    # PAGE HEADER
    # -------------------------------------
    section_header(
        "Compliance Center",
        "Monitor regulatory obligations and GST compliance from a unified workspace."
    )

    # -------------------------------------
    # TABS
    # -------------------------------------
    tab1, tab2 = st.tabs(
        [
            "Deadlines & Obligations",
            "GST & Tax Tracker"
        ]
    )

    # -------------------------------------
    # TAB 1
    # -------------------------------------
    with tab1:

        compliance.show()

    # -------------------------------------
    # TAB 2
    # -------------------------------------
    with tab2:

        gst_tracker.show()
