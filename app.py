"""
NEPSE Analysis Platform
Dashboard V2 Main Entry Point
"""

import streamlit as st

from config import APP_TITLE
from components.theme import initialize_theme
from components.sidebar import (
    render_sidebar_brand,
    render_sidebar_status,
)


# ------------------------------------------------------------
# PAGE INITIALIZATION
# ------------------------------------------------------------

initialize_theme(
    title=APP_TITLE,
    icon="📊",
)


# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------

render_sidebar_brand()
render_sidebar_status()


# ------------------------------------------------------------
# DASHBOARD HOME
# ------------------------------------------------------------

st.title(APP_TITLE)


st.markdown(
    """
    <div class="dashboard-hero">
        <div class="dashboard-hero-subtitle">
            Professional market intelligence, stock research,
            risk analysis, and evidence-based decision support
            for the Nepal Stock Exchange.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


st.divider()


# ------------------------------------------------------------
# PLATFORM MODULES
# ------------------------------------------------------------

st.markdown("## Platform Modules")


col1, col2, col3 = st.columns(3)


with col1:

    st.markdown("### Market Intelligence")

    st.markdown(
        """
        <div class="module-card-description">
            Market structure, breadth, sector performance,
            momentum, volume activity, and market trends.
        </div>
        """,
        unsafe_allow_html=True,
    )


with col2:

    st.markdown("### Stock Research")

    st.markdown(
        """
        <div class="module-card-description">
            Multi-factor stock screening, company research,
            technical structure, momentum, and ranking analysis.
        </div>
        """,
        unsafe_allow_html=True,
    )


with col3:

    st.markdown("### Risk Intelligence")

    st.markdown(
        """
        <div class="module-card-description">
            Volatility, drawdown, liquidity, market risk,
            and evidence-based trading risk management.
        </div>
        """,
        unsafe_allow_html=True,
    )


st.divider()


# ------------------------------------------------------------
# DEVELOPMENT STATUS
# ------------------------------------------------------------

st.markdown("## Current Development Status")


st.info(
    """
    The NEPSE Analysis Platform is being developed as a
    data-driven research and market intelligence system.

    Current modules include market overview, stock screening,
    and company administration.
    """
)


st.divider()


st.caption(
    "Data is read-only for market analytics. "
    "Company administration is controlled separately."
)
