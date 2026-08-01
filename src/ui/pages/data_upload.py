"""Data-upload page."""

from typing import Any

import pandas as pd
import streamlit as st

from src.ui.components import render_page_header
from src.ui.data_service import (
    process_uploaded_audit_file,
)
from src.ui.state import (
    clear_data_state,
    store_processed_data,
    store_processing_error,
)


def _render_validation_metrics(
    validation_results: dict[str, Any],
) -> None:
    """Display high-level validation metrics."""

    first_column, second_column, third_column, fourth_column = st.columns(4)

    first_column.metric(
        "Rows loaded",
        int(
            validation_results.get(
                "total_records",
                0,
            )
        ),
    )

    second_column.metric(
        "Duplicate references",
        int(
            validation_results.get(
                "duplicate_reference_numbers",
                0,
            )
        ),
    )

    third_column.metric(
        "Missing due dates",
        int(
            validation_results.get(
                "missing_due_dates",
                0,
            )
        ),
    )

    fourth_column.metric(
        "Invalid severities",
        int(
            validation_results.get(
                "invalid_severity_values",
                0,
            )
        ),
    )


def _render_missing_columns(
    validation_results: dict[str, Any],
) -> None:
    """Display missing required columns."""

    missing_columns = validation_results.get(
        "missing_required_columns",
        [],
    )

    if not missing_columns:
        return

    st.error("The uploaded file is missing required columns.")

    for column in missing_columns:
        st.markdown(f"- `{column}`")


def _render_validation_details(
    validation_results: dict[str, Any],
) -> None:
    """Display detailed validation results."""

    validation_passed = bool(
        validation_results.get(
            "validation_passed",
            False,
        )
    )

    if validation_passed:
        st.success("Validation passed. The cleaned dataset is ready for analysis.")
    else:
        st.warning(
            "Validation requires attention. "
            "Review the issues below before relying on the analysis."
        )

    _render_missing_columns(validation_results)

    issue_fields = {
        "Missing reference numbers": ("missing_reference_numbers"),
        "Missing findings": "missing_findings",
        "Missing due dates": "missing_due_dates",
        "Missing root causes": "missing_root_causes",
        "Missing corrective actions": ("missing_corrective_actions"),
        "Missing preventive actions": ("missing_preventive_actions"),
        "Duplicate reference numbers": ("duplicate_reference_numbers"),
        "Invalid severity values": ("invalid_severity_values"),
    }

    issue_rows = []

    for label, key in issue_fields.items():
        if key not in validation_results:
            continue

        issue_rows.append(
            {
                "Validation check": label,
                "Records affected": int(
                    validation_results.get(
                        key,
                        0,
                    )
                ),
            }
        )

    if issue_rows:
        issue_dataframe = pd.DataFrame(issue_rows)

        st.dataframe(
            issue_dataframe,
            use_container_width=True,
            hide_index=True,
        )

    invalid_records = validation_results.get(
        "invalid_severity_records",
        [],
    )

    if invalid_records:
        with st.expander("Invalid severity records"):
            st.dataframe(
                pd.DataFrame(invalid_records),
                use_container_width=True,
                hide_index=True,
            )


def _render_dataset_previews() -> None:
    """Display raw and cleaned dataset previews."""

    raw_dataframe = st.session_state.get("raw_dataframe")
    cleaned_dataframe = st.session_state.get("cleaned_dataframe")

    if not isinstance(
        raw_dataframe,
        pd.DataFrame,
    ):
        st.info("Upload a file to view the dataset preview.")
        return

    raw_tab, cleaned_tab = st.tabs(
        [
            "Raw data",
            "Cleaned data",
        ]
    )

    with raw_tab:
        st.caption(
            f"{len(raw_dataframe):,} rows × {len(raw_dataframe.columns):,} columns"
        )
        st.dataframe(
            raw_dataframe.head(20),
            use_container_width=True,
            hide_index=True,
        )

    with cleaned_tab:
        if not isinstance(
            cleaned_dataframe,
            pd.DataFrame,
        ):
            st.info("Cleaned data is not available.")
            return

        st.caption(
            f"{len(cleaned_dataframe):,} rows × "
            f"{len(cleaned_dataframe.columns):,} columns"
        )
        st.dataframe(
            cleaned_dataframe.head(20),
            use_container_width=True,
            hide_index=True,
        )


def render(description: str) -> None:
    """Render the data-upload page."""

    render_page_header(
        "Data Upload",
        description,
    )

    uploaded_file = st.file_uploader(
        "Upload an audit register",
        type=[
            "xlsx",
            "xls",
            "csv",
        ],
        help=(
            "Upload an Excel or CSV audit register. "
            "The file will be cleaned and validated automatically."
        ),
    )

    if uploaded_file is None:
        existing_file_name = st.session_state.get("uploaded_file_name")

        if existing_file_name:
            st.success(f"Previously loaded file retained: {existing_file_name}")

            if st.button(
                "Clear loaded audit data",
                type="secondary",
            ):
                clear_data_state()
                st.rerun()

            validation_results = st.session_state.get("validation_results")

            if isinstance(
                validation_results,
                dict,
            ):
                _render_validation_metrics(validation_results)

                st.subheader("Validation details")

                _render_validation_details(validation_results)

            st.subheader("Dataset preview")
            _render_dataset_previews()
            return

        st.info("Select an Excel or CSV audit register to begin.")
        st.subheader("Dataset preview")
        _render_dataset_previews()
        return

    current_file_name = st.session_state.get("uploaded_file_name")

    should_process = (
        uploaded_file.name != current_file_name
        or st.session_state.get("cleaned_dataframe") is None
    )

    if should_process:
        try:
            with st.spinner("Loading, cleaning, and validating the audit register..."):
                result = process_uploaded_audit_file(
                    uploaded_file,
                    file_name=uploaded_file.name,
                )

            store_processed_data(
                file_name=result.file_name,
                raw_dataframe=result.raw_dataframe,
                cleaned_dataframe=result.cleaned_dataframe,
                validation_results=result.validation_results,
            )

            st.rerun()

        except (
            RuntimeError,
            ValueError,
        ) as error:
            store_processing_error(str(error))

    processing_error = st.session_state.get("processing_error")

    if processing_error:
        st.error(processing_error)
        return

    validation_results = st.session_state.get("validation_results")

    first_column, second_column = st.columns(2)

    with first_column:
        st.subheader("File status")
        st.success(f"Loaded: {uploaded_file.name}")

    with second_column:
        st.subheader("Validation status")

        if isinstance(
            validation_results,
            dict,
        ) and validation_results.get("validation_passed"):
            st.success("Passed")
        else:
            st.warning("Requires attention")

    if isinstance(
        validation_results,
        dict,
    ):
        _render_validation_metrics(validation_results)

        st.subheader("Validation details")

        _render_validation_details(validation_results)

    st.subheader("Dataset preview")
    _render_dataset_previews()
