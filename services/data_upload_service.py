"""
Data Upload Service
====================

Backs pages/4 Data_Upload.py. This module was missing from the project
export, which is why the Data Upload page rendered blank below the
"Database Coverage Status" header (the page's import of this module
failed silently at load time).

IMPORTANT — READ THIS FIRST
----------------------------
1. WRITE ACCESS: db.py / config.py deliberately use a READ-ONLY DB user
   for the rest of the dashboard. Uploading data requires INSERT/DELETE,
   which a read-only user cannot do. This module opens a SEPARATE engine
   for writes so the read-only guarantee for the rest of the app is not
   touched. Add these to your .env:

       DB_WRITE_USER=<a postgres user with INSERT/DELETE on public.daily
                       and public.floorsheet>
       DB_WRITE_PASSWORD=<its password>

   If those aren't set, this module falls back to DB_USER/DB_PASSWORD —
   uploads will simply fail with a permissions error until either (a)
   you add a write-capable user, or (b) you grant INSERT/DELETE on
   public.daily and public.floorsheet to your existing DB_USER.

2. COLUMN NAMES ARE A BEST GUESS. I don't have access to your database,
   so I could not confirm the actual columns of public.daily /
   public.floorsheet beyond the fact that both use `tdate` as the date
   column (found in check_data_counts.py). The mappings below assume
   standard NEPSE export column names. Run this to get the real schema:

       python inspect_upload_tables.py

   Then edit DAILY_COLUMN_MAP / FLOORSHEET_COLUMN_MAP below (and the
   REQUIRED_* tuples) to match exactly. Everything else in this file
   (coverage stats, missing-date detection, file reading, delete+insert
   logic) does not depend on the guess and needs no changes.
"""

from __future__ import annotations

import io
from datetime import date, timedelta

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from config import load_db_config
from db import run_query, clear_cache


# ============================================================
# WRITE ENGINE (separate from the read-only engine in db.py)
# ============================================================

@st.cache_resource
def _get_write_engine() -> Engine:
    import os

    cfg = load_db_config()
    write_user = os.getenv("DB_WRITE_USER", cfg.user)
    write_password = os.getenv("DB_WRITE_PASSWORD", cfg.password)

    url = (
        f"postgresql+psycopg2://{write_user}:{write_password}"
        f"@{cfg.host}:{cfg.port}/{cfg.database}"
    )
    return create_engine(url, pool_pre_ping=True)


# ============================================================
# COLUMN MAPPING — VERIFY AGAINST YOUR ACTUAL SCHEMA
# ============================================================

# Maps normalized (lowercase, stripped, underscored) source-file headers
# -> target DB column name. Add/adjust entries once you know the real
# public.daily / public.floorsheet columns.
DAILY_COLUMN_MAP = {
    "symbol": "symbol",
    "conf": "symbol",  # some NEPSE exports call it "Conf." — adjust as needed
    "open": "open",
    "open_price": "open",
    "high": "high",
    "low": "low",
    "close": "close",
    "close_price": "close",
    "ltp": "close",
    "prev_close": "prev_close",
    "previous_close": "prev_close",
    "vwap": "vwap",
    "volume": "volume",
    "vol": "volume",
    "turnover": "turnover",
    "transactions": "transactions",
    "trans": "transactions",
    "no_of_transactions": "transactions",
}

FLOORSHEET_COLUMN_MAP = {
    "contract_no": "contract_no",
    "contract_number": "contract_no",
    "symbol": "symbol",
    "buyer": "buyer",
    "buyer_broker": "buyer",
    "seller": "seller",
    "seller_broker": "seller",
    "quantity": "quantity",
    "qty": "quantity",
    "rate": "rate",
    "amount": "amount",

}

REQUIRED_DAILY_COLUMNS = ("symbol", "close")
REQUIRED_FLOORSHEET_COLUMNS = ("symbol", "quantity", "rate", "amount")


def _normalize_headers(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [
        str(c).strip().lower().replace(" ", "_").replace(".", "").replace("-", "_")
        for c in df.columns
    ]
    return df


def _apply_column_map(df: pd.DataFrame, column_map: dict) -> pd.DataFrame:
    df = _normalize_headers(df)
    rename = {c: column_map[c] for c in df.columns if c in column_map}
    df = df.rename(columns=rename)
    # Keep only columns we recognize (mapped targets), drop the rest.
    keep = [c for c in df.columns if c in set(column_map.values())]
    return df[keep]


def _coerce_numeric(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    df = df.copy()
    for col in columns:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.strip()
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


# ============================================================
# COVERAGE / MISSING-DATE HELPERS
# ============================================================

def get_database_coverage() -> dict:
    daily = run_query(
        "SELECT MAX(tdate) AS max_date, COUNT(*) AS rows FROM public.daily"
    )
    floorsheet = run_query(
        "SELECT MAX(tdate) AS max_date, COUNT(*) AS rows FROM public.floorsheet"
    )

    return {
        "daily_max_date": daily.loc[0, "max_date"] if not daily.empty else None,
        "daily_rows": int(daily.loc[0, "rows"]) if not daily.empty else 0,
        "floorsheet_max_date": (
            floorsheet.loc[0, "max_date"] if not floorsheet.empty else None
        ),
        "floorsheet_rows": (
            int(floorsheet.loc[0, "rows"]) if not floorsheet.empty else 0
        ),
    }


def get_uploaded_dates(table: str) -> list[date]:
    if table not in ("daily", "floorsheet"):
        raise ValueError(f"Unknown table: {table}")

    df = run_query(f"SELECT DISTINCT tdate FROM public.{table} ORDER BY tdate")
    return [d for d in df["tdate"].tolist()]


def find_missing_weekdays(
    start_date: date, end_date: date, existing_dates: list[date]
) -> list[date]:
    existing = set(existing_dates)
    missing = []
    current = start_date
    while current <= end_date:
        # NEPSE trades Sun-Thu; Fri/Sat are weekend (weekday(): Mon=0 ... Sun=6)
        if current.weekday() not in (4, 5) and current not in existing:
            missing.append(current)
        current += timedelta(days=1)
    return missing


# ============================================================
# FILE READING
# ============================================================

def read_uploaded_file(uploaded_file) -> pd.DataFrame:
    name = uploaded_file.name.lower()
    raw_bytes = uploaded_file.getvalue()

    if name.endswith(".csv"):
        return pd.read_csv(io.BytesIO(raw_bytes))
    elif name.endswith(".xlsx"):
        return pd.read_excel(io.BytesIO(raw_bytes))
    else:
        raise ValueError(f"Unsupported file type: {uploaded_file.name}")


# ============================================================
# VALIDATION / PREPARATION
# ============================================================

def prepare_daily_dataframe(raw_df: pd.DataFrame, trading_date: date) -> pd.DataFrame:
    df = _apply_column_map(raw_df, DAILY_COLUMN_MAP)

    missing_required = [c for c in REQUIRED_DAILY_COLUMNS if c not in df.columns]
    if missing_required:
        raise ValueError(
            f"Missing required column(s) in Daily file: {missing_required}. "
            f"Detected columns after mapping: {list(df.columns)}. "
            f"Check DAILY_COLUMN_MAP in services/data_upload_service.py "
            f"against your file's actual headers."
        )

    numeric_cols = [
        c for c in
        ("open", "high", "low", "close", "prev_close", "vwap", "volume", "turnover", "transactions")
        if c in df.columns
    ]
    df = _coerce_numeric(df, numeric_cols)

    df["tdate"] = trading_date
    df = df.dropna(subset=["symbol"])
    df = df.drop_duplicates(subset=["symbol", "tdate"])

    return df.reset_index(drop=True)


def prepare_floorsheet_dataframe(
    raw_df: pd.DataFrame, trading_date: date
) -> pd.DataFrame:
    df = _apply_column_map(raw_df, FLOORSHEET_COLUMN_MAP)

    missing_required = [c for c in REQUIRED_FLOORSHEET_COLUMNS if c not in df.columns]
    if missing_required:
        raise ValueError(
            f"Missing required column(s) in Floorsheet file: {missing_required}. "
            f"Detected columns after mapping: {list(df.columns)}. "
            f"Check FLOORSHEET_COLUMN_MAP in services/data_upload_service.py "
            f"against your file's actual headers."
        )

    numeric_cols = [c for c in ("quantity", "rate", "amount") if c in df.columns]
    df = _coerce_numeric(df, numeric_cols)

    df["tdate"] = trading_date
    df = df.dropna(subset=["symbol", "quantity", "rate", "amount"])

    return df.reset_index(drop=True)


# ============================================================
# UPLOAD (DELETE existing rows for the date, then INSERT)
# ============================================================

def _replace_date_and_insert(df: pd.DataFrame, table: str, trading_date: date) -> int:
    engine = _get_write_engine()

    with engine.begin() as conn:
        conn.execute(
            text(f"DELETE FROM public.{table} WHERE tdate = :d"),
            {"d": trading_date},
        )
        df.to_sql(
            table,
            con=conn,
            schema="public",
            if_exists="append",
            index=False,
        )

    clear_cache()  # invalidate cached SELECTs so coverage/pages refresh
    return len(df)


def upload_daily_data(prepared_daily: pd.DataFrame) -> int:
    if prepared_daily.empty:
        raise ValueError("No rows to upload.")
    trading_date = prepared_daily["tdate"].iloc[0]
    return _replace_date_and_insert(prepared_daily, "daily", trading_date)


def upload_floorsheet_data(prepared_floorsheet: pd.DataFrame) -> int:
    if prepared_floorsheet.empty:
        raise ValueError("No rows to upload.")
    trading_date = prepared_floorsheet["tdate"].iloc[0]
    return _replace_date_and_insert(prepared_floorsheet, "floorsheet", trading_date)
