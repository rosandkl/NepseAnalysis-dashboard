"""
NEPSE Analysis Platform
Dashboard V2 — Market Overview
"""

import streamlit as st

from components.theme import initialize_theme
from components.ui import empty_state, metric_row, refresh_button, styled_table
from queries.market_overview import (
    get_sector_breakdown,
    get_top_movers,
    get_universe_counts,
)


initialize_theme(
    title="Market Overview",
    icon="📈",
)


st.markdown(
    """
    <div class="dashboard-header">
        <div class="dashboard-title">Market Overview</div>
        <div class="dashboard-subtitle">
            NEPSE universe composition, sector distribution, and daily market movers.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


refresh_button()


st.markdown(
    '<div class="section-title">Market Universe</div>',
    unsafe_allow_html=True,
)

universe_df = get_universe_counts()

if universe_df.empty:
    empty_state("No data in security_master yet.")
else:
    counts = dict(
        zip(
            universe_df["security_class"],
            universe_df["security_count"],
        )
    )

    metric_row(
        [
            ("Public Equities", str(counts.get("PUBLIC_EQUITY", 0))),
            ("Promoter Equities", str(counts.get("PROMOTER_EQUITY", 0))),
            ("Debentures", str(counts.get("DEBENTURE", 0))),
            ("Mutual Funds", str(counts.get("MUTUAL_FUND", 0))),
            ("Total Securities", str(int(universe_df["security_count"].sum()))),
        ]
    )


st.divider()


col1, col2 = st.columns(2)


with col1:

    st.markdown(
        '<div class="section-title">Sector Distribution</div>',
        unsafe_allow_html=True,
    )

    sector_df = get_sector_breakdown("PUBLIC_EQUITY")

    if sector_df.empty:
        empty_state()
    else:
        st.bar_chart(
            sector_df.set_index("sector")["security_count"],
            use_container_width=True,
        )


with col2:

    st.markdown(
        '<div class="section-title">Top Gainers — 1 Day</div>',
        unsafe_allow_html=True,
    )

    gainers_df = get_top_movers("gainers", limit=10)

    if gainers_df.empty:
        empty_state()
    else:
        styled_table(
            gainers_df,
            pct_columns=["return_1d_pct"],
        )


st.divider()


st.markdown(
    '<div class="section-title">Top Losers — 1 Day</div>',
    unsafe_allow_html=True,
)

losers_df = get_top_movers("losers", limit=10)

if losers_df.empty:
    empty_state()
else:
    styled_table(
        losers_df,
        pct_columns=["return_1d_pct"],
    )

