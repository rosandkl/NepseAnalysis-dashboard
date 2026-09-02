"""
Database connection layer.

Deliberately generic: nothing here knows about any specific table or view.
New queries never need to touch this file — see queries/ for how to add one.

Design principles carried over from the project manual:
- The dashboard only ever SELECTs. It never modifies public.* raw tables.
- Connects via a read-only DB user (set in .env) wherever possible.
- Uses SQLAlchemy connection pooling so Streamlit reruns don't reopen
  connections constantly.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from config import DEFAULT_CACHE_TTL_SECONDS, load_db_config


@st.cache_resource
def get_engine() -> Engine:
    """
    Create (once, cached across Streamlit reruns) the pooled SQLAlchemy engine.
    st.cache_resource is used instead of a module-level global because it
    survives Streamlit's script-rerun model correctly and is the documented
    pattern for sharing connections/engines across a session.
    """
    cfg = load_db_config()
    return create_engine(
        cfg.sqlalchemy_url,
        pool_size=cfg.pool_size,
        max_overflow=cfg.max_overflow,
        pool_recycle=cfg.pool_recycle_seconds,
        pool_pre_ping=True,  # guards against stale connections after idle periods
    )


@st.cache_data(ttl=DEFAULT_CACHE_TTL_SECONDS)
def run_query(sql: str, params: dict | None = None) -> pd.DataFrame:
    """
    Generic parameterized query runner used by every module in queries/.

    Usage:
        from db import run_query
        df = run_query("SELECT * FROM stock_dashboard.stock_screener WHERE security_class = :cls",
                        {"cls": "PUBLIC_EQUITY"})

    Cached by Streamlit for DEFAULT_CACHE_TTL_SECONDS (config.py) so repeated
    page navigation doesn't re-hit the database every time. Cache key is the
    (sql, params) pair, so different filters naturally get separate cache
    entries.

    Always use :named params (never raw string formatting) to avoid SQL
    injection, even though inputs currently come from trusted UI widgets.
    """
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text(sql), params or {})
        return pd.DataFrame(result.fetchall(), columns=result.keys())


def clear_cache() -> None:
    """Call from a page (e.g. a 'Refresh data' button) to force-refetch."""
    run_query.clear()
