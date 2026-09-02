"""
Dashboard V2 Theme System
Centralized Streamlit configuration and CSS loading.
"""

from pathlib import Path

import streamlit as st


def load_css():
    """Load the dashboard stylesheet."""

    css_path = (
        Path(__file__).resolve().parent.parent
        / "assets"
        / "styles.css"
    )

    if css_path.exists():

        css = css_path.read_text(
            encoding="utf-8"
        )

        if css.strip():

            st.markdown(
                f"<style>{css}</style>",
                unsafe_allow_html=True,
            )


def initialize_theme(
    title="NEPSE Analysis Platform",
    icon="📊",
):
    """Initialize page configuration and dashboard styling."""

    st.set_page_config(
        page_title=title,
        page_icon=icon,
        layout="wide",
        initial_sidebar_state="expanded",
    )

    load_css()
