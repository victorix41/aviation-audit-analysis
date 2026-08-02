"""Management reports and export page."""

from datetime import date

import pandas as pd
import streamlit as st

from src.reports.cached_reports import (
    generate_cached_excel_report,
    generate_cached_word_report,
)
from src.ui.components import render_page_header


def _clear_generated_reports() -> None:
    """Clear generated report files from session state."""

    st.session_state["word_report_bytes"] = None
    st.session_state["excel_report_bytes"] = None
    st.session_state["report_as_of_date"] = None
    st.session_state["report_source_file_name"] = None


def _reports_match_current_inputs(
    *,
    source_file_name: str,
    as_of_date: date,
) -> bool:
    """Return whether stored reports match the selected inputs."""

    return (
        st.session_state.get("word_report_bytes") is not None
        and st.session_state.get("excel_report_bytes") is not None
        and st.session_state.get("report_source_file_name") == source_file_name
        and st.session_state.get("report_as_of_date") == as_of_date
    )


def _generate_reports(
    dataframe: pd.DataFrame,
    *,
    source_file_name: str,
    as_of_date: date,
) -> None:
    """Generate Word and Excel management reports."""

    word_report_bytes = generate_cached_word_report(
        dataframe,
        source_file_name=source_file_name,
        as_of_date=as_of_date,
    )

    excel_report_bytes = generate_cached_excel_report(
        dataframe,
        source_file_name=source_file_name,
        as_of_date=as_of_date,
    )

    st.session_state["word_report_bytes"] = word_report_bytes
    st.session_state["excel_report_bytes"] = excel_report_bytes
    st.session_state["report_as_of_date"] = as_of_date
    st.session_state["report_source_file_name"] = source_file_name


def _render_report_contents() -> None:
    """Display a summary of the generated report contents."""

    st.subheader("Report Contents")

    first_column, second_column = st.columns(2)

    with first_column:
        st.markdown("#### Word Management Report")
        st.markdown(
            """
- Cover page and report basis
- Executive KPI summary
- Leading human factor and root cause
- Severity Pareto table
- Monthly response workload
- Management observations
- Management considerations
- Method and due-date qualifications
"""
        )

    with second_column:
        st.markdown("#### Excel Analytics Workbook")
        st.markdown(
            """
- Executive Summary
- Severity Analysis
- Human Factors
- Root Causes
- Corrective Actions
- Preventive Actions
- Data Quality
- Cleaned Audit Data
"""
        )


def _render_download_buttons(
    *,
    source_file_name: str,
) -> None:
    """Display Word and Excel download buttons."""

    word_report_bytes = st.session_state.get("word_report_bytes")
    excel_report_bytes = st.session_state.get("excel_report_bytes")

    if not isinstance(word_report_bytes, bytes):
        return

    if not isinstance(excel_report_bytes, bytes):
        return

    source_stem = source_file_name.rsplit(".", maxsplit=1)[0]

    first_column, second_column = st.columns(2)

    with first_column:
        st.download_button(
            label="Download Word management report",
            data=word_report_bytes,
            file_name=(f"{source_stem}_management_report.docx"),
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            use_container_width=True,
        )

    with second_column:
        st.download_button(
            label="Download Excel analytics workbook",
            data=excel_report_bytes,
            file_name=(f"{source_stem}_analytics_workbook.xlsx"),
            mime=("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
            use_container_width=True,
        )


def render(description: str) -> None:
    """Render the Reports page."""

    render_page_header(
        "Reports",
        description,
    )

    cleaned_dataframe = st.session_state.get("cleaned_dataframe")

    if not isinstance(
        cleaned_dataframe,
        pd.DataFrame,
    ):
        st.warning(
            "Upload and validate an audit register before generating "
            "management reports."
        )
        return

    source_file_name = (
        st.session_state.get("uploaded_file_name") or "audit-register.xlsx"
    )

    st.info(f"Source dataset: {source_file_name} ({len(cleaned_dataframe):,} rows)")

    as_of_date = st.date_input(
        "Report as-of date",
        value=date.today(),
        help=(
            "Used to classify response due dates in the executive "
            "summary and management report."
        ),
    )

    stored_as_of_date = st.session_state.get("report_as_of_date")
    stored_source_file_name = st.session_state.get("report_source_file_name")

    if stored_as_of_date is not None and (
        stored_as_of_date != as_of_date or stored_source_file_name != source_file_name
    ):
        _clear_generated_reports()

    _render_report_contents()

    st.divider()

    if _reports_match_current_inputs(
        source_file_name=source_file_name,
        as_of_date=as_of_date,
    ):
        st.success("The management reports are ready for download.")
    else:
        st.info("Select Generate Reports to create the Word and Excel files.")

    if st.button(
        "Generate Reports",
        type="primary",
        use_container_width=True,
    ):
        try:
            with st.spinner("Generating Word and Excel management reports..."):
                _generate_reports(
                    cleaned_dataframe,
                    source_file_name=source_file_name,
                    as_of_date=as_of_date,
                )
        except (
            KeyError,
            TypeError,
            ValueError,
            RuntimeError,
        ) as error:
            _clear_generated_reports()

            st.error("The management reports could not be generated.")

            with st.expander("Technical details"):
                st.code(str(error))
        else:
            st.success("Word and Excel management reports generated successfully.")

    _render_download_buttons(
        source_file_name=source_file_name,
    )

    st.caption(
        "The generated reports are based on the uploaded cleaned dataset "
        "and deterministic analytics. Past-due classifications do not "
        "confirm whether findings remain open because the source dataset "
        "does not currently contain status or closure-date fields."
    )
