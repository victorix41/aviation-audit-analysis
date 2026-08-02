"""Reusable Streamlit interface components."""

from collections.abc import Sequence

import streamlit as st

from src.ui.state import has_loaded_data


def render_page_header(
    title: str,
    description: str,
) -> None:
    """Display a consistent page heading."""

    st.title(title)
    st.caption(description)
    st.divider()


def render_kpi_cards(
    metrics: list[
        tuple[
            str,
            int | float | str,
            str | None,
        ]
    ],
    *,
    columns_per_row: int = 4,
) -> None:
    """
    Render reusable KPI cards using Streamlit metrics.

    Args:
        metrics:
            List of tuples containing:
            - label;
            - value;
            - optional help text.

        columns_per_row:
            Maximum number of KPI cards displayed in one row.
    """

    if columns_per_row < 1:
        raise ValueError("columns_per_row must be at least 1.")

    for start_index in range(
        0,
        len(metrics),
        columns_per_row,
    ):
        row_metrics = metrics[start_index : start_index + columns_per_row]

        # Always use the same number of columns so incomplete
        # final rows align with the rows above.
        columns = st.columns(columns_per_row)

        for column, metric in zip(
            columns,
            row_metrics,
            strict=False,
        ):
            label, value, help_text = metric

            column.metric(
                label=label,
                value=value,
                help=help_text,
            )


def render_planned_sections(
    sections: Sequence[str],
) -> None:
    """Display planned content for an application page."""

    st.info(
        "This page is part of the Phase 8.1 application shell. "
        "Its analytics components will be connected in a later milestone."
    )

    st.subheader("Planned content")

    for section in sections:
        st.markdown(f"- {section}")


def render_sidebar_status() -> None:
    """Display the current data status in the sidebar."""

    st.subheader("Data status")

    if has_loaded_data():
        validation_results = st.session_state.get("validation_results")

        file_name = st.session_state.get("uploaded_file_name")

        if isinstance(
            validation_results,
            dict,
        ) and validation_results.get("validation_passed"):
            st.success("Audit data is ready for analysis.")
        else:
            st.warning("Audit data loaded with validation issues.")

        if file_name:
            st.caption(f"File: {file_name}")

        cleaned_dataframe = st.session_state.get("cleaned_dataframe")

        if cleaned_dataframe is not None:
            st.caption(f"Rows: {len(cleaned_dataframe):,}")

        return

    processing_error = st.session_state.get("processing_error")

    if processing_error:
        st.error("The uploaded file could not be processed.")
        return

    st.info("No audit register loaded.")
