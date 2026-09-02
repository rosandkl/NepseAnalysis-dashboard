"""
Reusable UI components. Add new ones here as pages start repeating patterns
(e.g. a symbol picker, a date-range filter) instead of copy-pasting into
each page.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from db import clear_cache


def metric_row(items: list[tuple[str, str]]) -> None:
    """
    Render a row of st.metric() cards.
    items: list of (label, value) tuples, e.g. [("Total Securities", "364")]
    """
    cols = st.columns(len(items))
    for col, (label, value) in zip(cols, items):
        col.metric(label, value)


def refresh_button(label: str = "🔄 Refresh data") -> None:
    """Drop this at the top of any page to let the user force-bypass the cache."""
    if st.button(label):
        clear_cache()
        st.rerun()


def styled_table(df: pd.DataFrame, pct_columns: list[str] | None = None) -> None:
    """
    Render a DataFrame with percentage columns formatted and conditionally
    colored (green positive, red negative) — the common case across
    returns/screener tables.
    """
    pct_columns = pct_columns or []

    def _color_pct(val):
        if pd.isna(val):
            return ""
        color = "green" if val > 0 else ("red" if val < 0 else "black")
        return f"color: {color}"

    def _format_pct(val):
        if pd.isna(val):
            return ""
        return f"{val:+.2f}%"

    styler = df.style
    if pct_columns:
        # Styler.applymap() was deprecated in pandas 2.1 and removed in
        # pandas 3.0 in favor of Styler.map(); support both so this works
        # across environments with different pandas versions installed.
        if hasattr(styler, "map"):
            styler = styler.map(_color_pct, subset=pct_columns)
        else:
            styler = styler.applymap(_color_pct, subset=pct_columns)
        # Use a formatter function (not a "{:+.2f}%" spec string) so NULLs
        # in the data — e.g. new listings without a full 6M/1Y history yet —
        # render as blank instead of raising on NoneType.__format__.
        styler = styler.format({col: _format_pct for col in pct_columns})

    st.dataframe(styler, use_container_width=True)


def empty_state(message: str = "No data matches the current filters.") -> None:
    st.info(message)