"""
NEPSE Analysis Platform
Data Upload Center
"""

import streamlit as st

from components.theme import initialize_theme

initialize_theme(
    title="Data Upload Center | NEPSE Analysis Platform",
    icon="📥",
)

from services.data_upload_service import (
    get_database_coverage,
    get_uploaded_dates,
    find_missing_weekdays,
    read_uploaded_file,
    prepare_daily_dataframe,
    prepare_floorsheet_dataframe,
    upload_daily_data,
    upload_floorsheet_data,
)


st.title("📥 Data Upload Center")

st.caption(
    "Upload and validate NEPSE Daily Market Data and Floorsheet Data "
    "before they enter the analytics database."
)

st.divider()


# ============================================================
# DATABASE COVERAGE
# ============================================================

st.header("Database Coverage Status")

try:

    coverage = get_database_coverage()

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Daily Latest Date",
            str(
                coverage["daily_max_date"]
                if coverage["daily_max_date"]
                else "No Data"
            ),
        )

    with col2:

        st.metric(
            "Daily Records",
            f"{coverage['daily_rows']:,}",
        )

    with col3:

        st.metric(
            "Floorsheet Latest Date",
            str(
                coverage["floorsheet_max_date"]
                if coverage["floorsheet_max_date"]
                else "No Data"
            ),
        )

    with col4:

        st.metric(
            "Floorsheet Records",
            f"{coverage['floorsheet_rows']:,}",
        )


    # --------------------------------------------------------
    # MISSING DATE CHECK
    # --------------------------------------------------------

    daily_dates = get_uploaded_dates("daily")
    floorsheet_dates = get_uploaded_dates("floorsheet")

    all_dates = sorted(
        set(daily_dates) | set(floorsheet_dates)
    )

    if all_dates:

        start_date = min(all_dates)
        end_date = max(all_dates)

        missing_daily = find_missing_weekdays(
            start_date,
            end_date,
            daily_dates,
        )

        missing_floorsheet = find_missing_weekdays(
            start_date,
            end_date,
            floorsheet_dates,
        )

        if missing_daily:

            st.warning(
                f"⚠️ Daily table may be missing "
                f"{len(missing_daily)} weekday(s)."
            )

            st.write(
                ", ".join(
                    str(d)
                    for d in missing_daily[-20:]
                )
            )

        else:

            st.success(
                "✓ No missing weekdays detected in Daily data."
            )

        if missing_floorsheet:

            st.warning(
                f"⚠️ Floorsheet table may be missing "
                f"{len(missing_floorsheet)} weekday(s)."
            )

            st.write(
                ", ".join(
                    str(d)
                    for d in missing_floorsheet[-20:]
                )
            )

        else:

            st.success(
                "✓ No missing weekdays detected in Floorsheet data."
            )


except Exception as exc:

    st.error(
        f"Coverage analysis error: {exc}"
    )


st.divider()


# ============================================================
# UPLOAD SECTION
# ============================================================

st.header("Upload Market Data")

tab1, tab2 = st.tabs(
    [
        "📈 Daily Market Data",
        "📋 Floorsheet Data",
    ]
)


# ============================================================
# DAILY UPLOAD
# ============================================================

with tab1:

    st.subheader("Upload Daily Market Data")

    st.info(
        "Upload the NEPSE daily market data file. "
        "Supported formats: CSV and XLSX."
    )

    daily_date = st.date_input(
        "Trading Date",
        key="daily_date",
    )

    daily_file = st.file_uploader(
        "Select Daily Market Data File",
        type=["csv", "xlsx"],
        key="daily_file",
    )

    if daily_file is not None:

        try:

            raw_daily = read_uploaded_file(
                daily_file
            )

            st.write(
                f"Rows detected: {len(raw_daily):,}"
            )

            st.dataframe(
                raw_daily.head(10),
                use_container_width=True,
            )

            if st.button(
                "Validate Daily Data",
                type="secondary",
            ):

                prepared_daily = (
                    prepare_daily_dataframe(
                        raw_daily,
                        daily_date,
                    )
                )

                st.success(
                    f"Validation successful. "
                    f"{len(prepared_daily):,} records ready."
                )

                st.dataframe(
                    prepared_daily.head(10),
                    use_container_width=True,
                )


            if st.button(
                "Upload Daily Data to Database",
                type="primary",
            ):

                prepared_daily = (
                    prepare_daily_dataframe(
                        raw_daily,
                        daily_date,
                    )
                )

                rows_uploaded = (
                    upload_daily_data(
                        prepared_daily
                    )
                )

                st.success(
                    f"✓ Successfully uploaded "
                    f"{rows_uploaded:,} Daily records "
                    f"for {daily_date}."
                )

                st.rerun()


        except Exception as exc:

            st.error(
                f"Daily upload error: {exc}"
            )


# ============================================================
# FLOORSHEET UPLOAD
# ============================================================

with tab2:

    st.subheader("Upload Floorsheet Data")

    st.info(
        "Upload the NEPSE Floorsheet file. "
        "Supported formats: CSV and XLSX."
    )

    floorsheet_date = st.date_input(
        "Trading Date",
        key="floorsheet_date",
    )

    floorsheet_file = st.file_uploader(
        "Select Floorsheet File",
        type=["csv", "xlsx"],
        key="floorsheet_file",
    )

    if floorsheet_file is not None:

        try:

            raw_floorsheet = read_uploaded_file(
                floorsheet_file
            )

            st.write(
                f"Rows detected: "
                f"{len(raw_floorsheet):,}"
            )

            st.dataframe(
                raw_floorsheet.head(10),
                use_container_width=True,
            )

            if st.button(
                "Validate Floorsheet Data",
                type="secondary",
            ):

                prepared_floorsheet = (
                    prepare_floorsheet_dataframe(
                        raw_floorsheet,
                        floorsheet_date,
                    )
                )

                st.success(
                    f"Validation successful. "
                    f"{len(prepared_floorsheet):,} "
                    f"records ready."
                )

                st.dataframe(
                    prepared_floorsheet.head(10),
                    use_container_width=True,
                )


            if st.button(
                "Upload Floorsheet to Database",
                type="primary",
            ):

                prepared_floorsheet = (
                    prepare_floorsheet_dataframe(
                        raw_floorsheet,
                        floorsheet_date,
                    )
                )

                rows_uploaded = (
                    upload_floorsheet_data(
                        prepared_floorsheet
                    )
                )

                st.success(
                    f"✓ Successfully uploaded "
                    f"{rows_uploaded:,} Floorsheet records "
                    f"for {floorsheet_date}."
                )

                st.rerun()


        except Exception as exc:

            st.error(
                f"Floorsheet upload error: {exc}"
            )


st.divider()

st.caption(
    "Data integrity policy: existing records for the selected date "
    "are replaced during upload to prevent duplicate data."
)
