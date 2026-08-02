"""Data-quality dashboard page."""

from typing import Any

import pandas as pd
import streamlit as st

from src.ui.components import (
    render_kpi_cards,
    render_page_header,
)
from src.validator import validate_audit_data

VALIDATION_FIELDS = {
    "Duplicate reference numbers": "duplicate_reference_numbers",
    "Missing reference numbers": "missing_reference_numbers",
    "Missing findings": "missing_findings",
    "Missing due dates": "missing_due_dates",
    "Missing root causes": "missing_root_causes",
    "Missing corrective actions": "missing_corrective_actions",
    "Missing preventive actions": "missing_preventive_actions",
    "Invalid severity values": "invalid_severity_values",
}


def _get_validation_results(
    dataframe: pd.DataFrame,
) -> dict[str, Any]:
    """Return stored validation results or recalculate them."""

    validation_results = st.session_state.get("validation_results")

    if isinstance(validation_results, dict):
        return validation_results

    return validate_audit_data(dataframe)


def _count_total_issues(
    validation_results: dict[str, Any],
) -> int:
    """Count all record-level validation issues."""

    return sum(
        int(
            validation_results.get(
                field_name,
                0,
            )
        )
        for field_name in VALIDATION_FIELDS.values()
    )


def _build_validation_summary(
    validation_results: dict[str, Any],
) -> pd.DataFrame:
    """Build a table summarising validation checks."""

    rows = []

    for label, field_name in VALIDATION_FIELDS.items():
        affected_records = int(
            validation_results.get(
                field_name,
                0,
            )
        )

        rows.append(
            {
                "Validation check": label,
                "Records affected": affected_records,
                "Status": ("Passed" if affected_records == 0 else "Requires attention"),
            }
        )

    missing_columns = validation_results.get(
        "missing_required_columns",
        [],
    )

    rows.append(
        {
            "Validation check": "Missing required columns",
            "Records affected": len(missing_columns),
            "Status": ("Passed" if not missing_columns else "Requires attention"),
        }
    )

    return pd.DataFrame(rows)


def _build_missing_value_summary(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Build a column-level missing-value summary."""

    rows = []

    total_records = len(dataframe)

    for column in dataframe.columns:
        series = dataframe[column]

        missing_count = int(series.isna().sum())

        if pd.api.types.is_string_dtype(series) or series.dtype == object:
            blank_count = int(
                series.astype("string").str.strip().eq("").fillna(False).sum()
            )
        else:
            blank_count = 0

        total_missing = missing_count + blank_count

        percentage = (
            round(
                total_missing / total_records * 100,
                2,
            )
            if total_records > 0
            else 0.0
        )

        rows.append(
            {
                "Column": column,
                "Missing values": missing_count,
                "Blank values": blank_count,
                "Total incomplete": total_missing,
                "Incomplete percentage": percentage,
            }
        )

    return (
        pd.DataFrame(rows)
        .sort_values(
            by=[
                "Total incomplete",
                "Column",
            ],
            ascending=[
                False,
                True,
            ],
        )
        .reset_index(drop=True)
    )


def _render_quality_kpis(
    dataframe: pd.DataFrame,
    validation_results: dict[str, Any],
) -> None:
    """Display high-level data-quality KPI cards."""

    validation_passed = bool(
        validation_results.get(
            "validation_passed",
            False,
        )
    )

    missing_columns = validation_results.get(
        "missing_required_columns",
        [],
    )

    kpis: list[
        tuple[
            str,
            int | float | str,
            str | None,
        ]
    ] = [
        (
            "Rows Loaded",
            len(dataframe),
            "Total records in the cleaned dataset.",
        ),
        (
            "Validation Status",
            ("Passed" if validation_passed else "Attention"),
            "Overall result from the project validation rules.",
        ),
        (
            "Total Issues",
            _count_total_issues(validation_results),
            "Combined count of record-level validation issues.",
        ),
        (
            "Missing Required Columns",
            len(missing_columns),
            "Required columns absent from the cleaned dataset.",
        ),
        (
            "Duplicate References",
            int(
                validation_results.get(
                    "duplicate_reference_numbers",
                    0,
                )
            ),
            "Records sharing duplicated audit reference numbers.",
        ),
        (
            "Missing Due Dates",
            int(
                validation_results.get(
                    "missing_due_dates",
                    0,
                )
            ),
            "Records without a valid response due date.",
        ),
        (
            "Invalid Severities",
            int(
                validation_results.get(
                    "invalid_severity_values",
                    0,
                )
            ),
            "Records using invalid severity values.",
        ),
    ]

    render_kpi_cards(
        kpis,
        columns_per_row=4,
    )


def _render_validation_status(
    validation_results: dict[str, Any],
) -> None:
    """Display the overall validation result."""

    validation_passed = bool(
        validation_results.get(
            "validation_passed",
            False,
        )
    )

    if validation_passed:
        st.success(
            "Validation passed. No issues were identified by the "
            "current validation rules."
        )
    else:
        st.warning(
            "Validation requires attention. Review the detailed "
            "checks and affected records below."
        )

    missing_columns = validation_results.get(
        "missing_required_columns",
        [],
    )

    if missing_columns:
        st.error("The dataset is missing required columns:")

        for column in missing_columns:
            st.markdown(f"- `{column}`")


def _render_validation_tables(
    dataframe: pd.DataFrame,
    validation_results: dict[str, Any],
) -> None:
    """Display validation and missing-value tables."""

    st.subheader("Validation Summary")

    validation_summary = _build_validation_summary(validation_results)

    st.dataframe(
        validation_summary,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Missing-Value Summary")

    missing_summary = _build_missing_value_summary(dataframe)

    st.dataframe(
        missing_summary,
        use_container_width=True,
        hide_index=True,
    )


def _render_exception_records(
    dataframe: pd.DataFrame,
    validation_results: dict[str, Any],
) -> None:
    """Display records affected by selected validation issues."""

    st.subheader("Exception Records")

    invalid_severity_records = validation_results.get(
        "invalid_severity_records",
        [],
    )

    invalid_tab, duplicate_tab, missing_date_tab = st.tabs(
        [
            "Invalid Severities",
            "Duplicate References",
            "Missing Due Dates",
        ]
    )

    with invalid_tab:
        if invalid_severity_records:
            st.dataframe(
                pd.DataFrame(invalid_severity_records),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.success("No invalid severity records identified.")

    with duplicate_tab:
        required_column = "audit_reference_no"

        if required_column not in dataframe.columns:
            st.info("Audit-reference data is unavailable.")
        else:
            duplicate_mask = dataframe[required_column].duplicated(keep=False)

            duplicate_records = dataframe.loc[duplicate_mask]

            if duplicate_records.empty:
                st.success("No duplicate audit references identified.")
            else:
                st.dataframe(
                    duplicate_records,
                    use_container_width=True,
                    hide_index=True,
                )

    with missing_date_tab:
        required_column = "response_due_date"

        if required_column not in dataframe.columns:
            st.info("Response-due-date data is unavailable.")
        else:
            missing_date_records = dataframe.loc[dataframe[required_column].isna()]

            if missing_date_records.empty:
                st.success("No missing response due dates identified.")
            else:
                st.dataframe(
                    missing_date_records,
                    use_container_width=True,
                    hide_index=True,
                )


def _render_downloads(
    dataframe: pd.DataFrame,
    validation_results: dict[str, Any],
) -> None:
    """Display validation-report download controls."""

    st.subheader("Download Data-Quality Reports")

    validation_summary = _build_validation_summary(validation_results)

    missing_summary = _build_missing_value_summary(dataframe)

    first_column, second_column = st.columns(2)

    with first_column:
        st.download_button(
            label="Download validation summary",
            data=validation_summary.to_csv(index=False).encode("utf-8"),
            file_name=("audit_validation_summary.csv"),
            mime="text/csv",
        )

    with second_column:
        st.download_button(
            label="Download missing-value summary",
            data=missing_summary.to_csv(index=False).encode("utf-8"),
            file_name=("audit_missing_value_summary.csv"),
            mime="text/csv",
        )


def render(description: str) -> None:
    """Render the Data Quality page."""

    render_page_header(
        "Data Quality",
        description,
    )

    cleaned_dataframe = st.session_state.get("cleaned_dataframe")

    if not isinstance(
        cleaned_dataframe,
        pd.DataFrame,
    ):
        st.warning("Upload and validate an audit register before viewing Data Quality.")
        return

    try:
        validation_results = _get_validation_results(cleaned_dataframe)
    except (
        KeyError,
        TypeError,
        ValueError,
    ) as error:
        st.error("The data-quality dashboard could not be generated.")

        with st.expander("Technical details"):
            st.code(str(error))

        return

    _render_quality_kpis(
        cleaned_dataframe,
        validation_results,
    )

    st.divider()
    _render_validation_status(validation_results)

    st.divider()
    _render_validation_tables(
        cleaned_dataframe,
        validation_results,
    )

    st.divider()
    _render_exception_records(
        cleaned_dataframe,
        validation_results,
    )

    st.divider()
    _render_downloads(
        cleaned_dataframe,
        validation_results,
    )

    st.caption(
        "The dashboard reports issues identified by the current "
        "validation rules. A passed result does not replace detailed "
        "audit or engineering review of the underlying content."
    )
