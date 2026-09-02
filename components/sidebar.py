"""
Dashboard V2 Sidebar Component
"""

import streamlit as st


def render_sidebar_brand():
    """Render sidebar branding."""

    st.sidebar.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-title">
                NEPSE ANALYSIS
            </div>

            <div class="sidebar-brand-subtitle">
                NEPSE INTELLIGENCE PLATFORM
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_status():
    """Render sidebar footer information."""

    st.sidebar.divider()

    st.sidebar.caption(
        "Market Intelligence & Research"
    )

    st.sidebar.caption(
        "Data-driven analysis • Research support"
    )
