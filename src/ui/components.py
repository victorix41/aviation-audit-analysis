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
