"""
Add Company
Dashboard administration page for adding companies to the master company table.
"""

import streamlit as st

from components.theme import initialize_theme
from queries.company_admin import (
    add_company,
    company_symbol_exists,
    get_recent_companies,
)
from utils.validators import (
    is_valid_email,
    is_valid_symbol,
    is_valid_website,
    normalize_symbol,
)


initialize_theme(
    title="Add Company",
    icon="➕",
)


st.title("➕ Add Company")

st.markdown(
    """
Add a new company to the NEPSE company master.

The company record will be stored in:

`public.company_name`
"""
)


# ================================================================
# COMPANY ENTRY FORM
# ================================================================

with st.form(
    "add_company_form",
    clear_on_submit=True,
):

    st.subheader("Company Information")

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input(
            "Company Name *",
            placeholder="e.g. Nepal Investment Mega Bank Limited",
        )

        symbol = st.text_input(
            "Symbol *",
            placeholder="e.g. NIMB",
        )

        status = st.selectbox(
            "Status *",
            options=[
                "Active",
                "Inactive",
                "Suspended",
                "Delisted",
            ],
        )

        sector = st.text_input(
            "Sector *",
            placeholder="e.g. Commercial Banks",
        )

    with col2:

        instrument = st.selectbox(
            "Instrument *",
            options=[
                "Equity",
                "Promoter Equity",
                "Debenture",
                "Mutual Fund",
                "Bond",
                "Other",
            ],
        )

        email = st.text_input(
            "Email",
            placeholder="e.g. info@company.com",
        )

        website = st.text_input(
            "Website",
            placeholder="https://www.company.com",
        )

    submitted = st.form_submit_button(
        "➕ Add Company",
        use_container_width=True,
    )


# ================================================================
# FORM PROCESSING
# ================================================================

if submitted:

    normalized_symbol = normalize_symbol(symbol)

    errors = []

    if not name.strip():
        errors.append(
            "Company name is required."
        )

    if not normalized_symbol:
        errors.append(
            "Company symbol is required."
        )

    elif not is_valid_symbol(
        normalized_symbol
    ):
        errors.append(
            "Invalid symbol format."
        )

    if not sector.strip():
        errors.append(
            "Sector is required."
        )

    if not is_valid_email(email):
        errors.append(
            "Invalid email address."
        )

    if not is_valid_website(website):
        errors.append(
            "Website must start with http:// or https://"
        )

    if not errors:

        if company_symbol_exists(
            normalized_symbol
        ):
            errors.append(
                f"Company symbol '{normalized_symbol}' already exists."
            )

    if errors:

        for error in errors:
            st.error(error)

    else:

        try:

            add_company(
                name=name,
                symbol=normalized_symbol,
                status=status,
                sector=sector,
                instrument=instrument,
                email=email,
                website=website,
            )

            st.success(
                f"Company '{normalized_symbol}' added successfully."
            )

        except ValueError as exc:

            st.error(str(exc))

        except Exception as exc:

            st.error(
                "Unable to add company."
            )

            st.exception(exc)


# ================================================================
# EXISTING COMPANY RECORDS
# ================================================================

st.divider()

st.subheader("Company Master Records")

recent_df = get_recent_companies(
    limit=50
)

if recent_df.empty:

    st.info(
        "No company records found."
    )

else:

    st.dataframe(
        recent_df,
        use_container_width=True,
        hide_index=True,
    )
