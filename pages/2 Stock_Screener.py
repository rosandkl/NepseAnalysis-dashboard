"""
NEPSE Analysis Platform
Stock Screener V2
Risk-aware market screening and analysis.
"""

import streamlit as st

from components.theme import initialize_theme
from components.ui import empty_state, styled_table
from queries.screener import (
    MOMENTUM_LEVELS,
    get_momentum_counts,
    get_screener,
    search_symbol,
)


initialize_theme(
    title="Stock Screener | NEPSE Analysis Platform",
    icon="📈",
)


st.title("📈 Stock Screener")

st.markdown(
    """
    <div class="dashboard-subtitle">
        Fact-based stock screening using market performance, momentum,
        volume, trend and risk-awareness indicators.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# MOMENTUM OVERVIEW
# ============================================================

counts_df = get_momentum_counts()

if not counts_df.empty:

    counts = dict(
        zip(
            counts_df["momentum_signal"],
            counts_df["symbol_count"],
        )
    )

    st.markdown("### Market Momentum Overview")

    cols = st.columns(len(MOMENTUM_LEVELS))

    for index, level in enumerate(MOMENTUM_LEVELS):

        with cols[index]:
            st.metric(
                label=level,
                value=counts.get(level, 0),
            )


st.divider()


# ============================================================
# FILTER PANEL
# ============================================================

st.markdown("### Screening Filters")

filter_col1, filter_col2, filter_col3 = st.columns(3)


with filter_col1:

    selected_momentum = st.multiselect(
        "Momentum Signal",
        options=MOMENTUM_LEVELS,
        default=MOMENTUM_LEVELS,
    )


with filter_col2:

    symbol_query = st.text_input(
        "Search Symbol",
        placeholder="e.g. NIMB",
    )


with filter_col3:

    min_return_1d = st.number_input(
        "Minimum 1-Day Return %",
        value=0.0,
        step=0.1,
    )


st.divider()


# ============================================================
# LOAD DATA
# ============================================================

if symbol_query.strip():

    screener_df = search_symbol(
        symbol_query.strip()
    )

else:

    screener_df = get_screener(
        momentum=selected_momentum or None
    )


# ============================================================
# EMPTY STATE
# ============================================================

if screener_df.empty:

    empty_state(
        "No securities found matching the selected criteria."
    )

    st.stop()


# ============================================================
# ADDITIONAL CLIENT-SIDE FILTERS
# ============================================================

if (
    "return_1d_pct" in screener_df.columns
):

    screener_df = screener_df[
        screener_df["return_1d_pct"].fillna(0)
        >= min_return_1d
    ]


# ============================================================
# SUMMARY METRICS
# ============================================================

st.markdown("### Screening Results")

metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)


with metric_col1:

    st.metric(
        "Matching Securities",
        len(screener_df),
    )


with metric_col2:

    if "return_1d_pct" in screener_df.columns:

        avg_return = (
            screener_df["return_1d_pct"]
            .dropna()
            .mean()
        )

        st.metric(
            "Average 1D Return",
            f"{avg_return:.2f}%",
        )

    else:

        st.metric(
            "Average 1D Return",
            "N/A",
        )


with metric_col3:

    if "return_1m_pct" in screener_df.columns:

        positive_month = (
            screener_df["return_1m_pct"]
            .fillna(0)
            > 0
        ).sum()

        st.metric(
            "Positive 1M Trend",
            positive_month,
        )

    else:

        st.metric(
            "Positive 1M Trend",
            "N/A",
        )


with metric_col4:

    if "above_ma50" in screener_df.columns:

        above_ma50 = (
            screener_df["above_ma50"]
            .fillna(False)
            .sum()
        )

        st.metric(
            "Above MA50",
            above_ma50,
        )

    else:

        st.metric(
            "Above MA50",
            "N/A",
        )


st.caption(
    f"{len(screener_df)} securities currently match your criteria."
)


# ============================================================
# RISK-AWARE ANALYSIS
# ============================================================

st.markdown("### Risk & Trend Indicators")

risk_columns = [
    "symbol",
    "company_name",
    "sector",
    "latest_close",
    "return_1d_pct",
    "return_1w_pct",
    "return_1m_pct",
    "return_3m_pct",
    "volume_ratio_20d",
    "distance_from_52week_high_pct",
    "distance_from_52week_low_pct",
    "position_52week_pct",
    "above_ma20",
    "above_ma50",
    "above_ma200",
    "momentum_signal",
]


available_columns = [
    column
    for column in risk_columns
    if column in screener_df.columns
]


display_df = screener_df[
    available_columns
].copy()


# ============================================================
# FACT-BASED RISK FLAGS
# ============================================================

if "distance_from_52week_high_pct" in display_df.columns:

    display_df["risk_flag"] = (
        display_df[
            "distance_from_52week_high_pct"
        ]
        .apply(
            lambda value:
            "Near 52W High"
            if value is not None
            and value > -5
            else ""
        )
    )


# ============================================================
# RESULTS TABLE
# ============================================================

styled_table(
    display_df,
    pct_columns=[
        column
        for column in display_df.columns
        if (
            "return" in column.lower()
            or "pct" in column.lower()
            or "ratio" in column.lower()
        )
    ],
)


# ============================================================
# FACT-BASED DISCLAIMER
# ============================================================

st.divider()

st.info(
    """
    Analysis Framework: Screening results are based on available market data,
    momentum, returns, moving averages, volume activity and 52-week positioning.
    These indicators support research and risk awareness but do not guarantee
    future price performance. Always evaluate liquidity, market conditions,
    company fundamentals and position sizing before making investment decisions.
    """
)
