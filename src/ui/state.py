"""Streamlit session-state management."""

from typing import Any

import pandas as pd
import streamlit as st

DEFAULT_SESSION_STATE: dict[str, Any] = {
    "uploaded_file_name": None,
    "raw_dataframe": None,
    "cleaned_dataframe": None,
    "validation_results": None,
    "processing_error": None,
    "active_filters": {},
    "word_report_bytes": None,
    "excel_report_bytes": None,
    "report_as_of_date": None,
    "report_source_file_name": None,
}


def initialize_session_state() -> None:
    """Initialize application session-state values."""

    for key, default_value in DEFAULT_SESSION_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def clear_data_state() -> None:
    """Clear uploaded and processed audit data from session state."""

    for key in (
        "uploaded_file_name",
        "raw_dataframe",
        "cleaned_dataframe",
        "validation_results",
        "processing_error",
        "word_report_bytes",
        "excel_report_bytes",
        "report_as_of_date",
        "report_source_file_name",
    ):
        st.session_state[key] = DEFAULT_SESSION_STATE[key]


def store_processed_data(
    *,
    file_name: str,
    raw_dataframe: pd.DataFrame,
    cleaned_dataframe: pd.DataFrame,
    validation_results: dict[str, Any],
) -> None:
    """Store processed audit data in Streamlit session state."""

    st.session_state["uploaded_file_name"] = file_name
    st.session_state["raw_dataframe"] = raw_dataframe
    st.session_state["cleaned_dataframe"] = cleaned_dataframe
    st.session_state["validation_results"] = validation_results
    st.session_state["processing_error"] = None


def store_processing_error(
    error_message: str,
) -> None:
    """Store an upload or processing error."""

    st.session_state["processing_error"] = error_message
    st.session_state["raw_dataframe"] = None
    st.session_state["cleaned_dataframe"] = None
    st.session_state["validation_results"] = None


def has_loaded_data() -> bool:
    """Return whether cleaned audit data is available."""

    return st.session_state.get("cleaned_dataframe") is not None


def validation_passed() -> bool:
    """Return whether the current dataset passed validation."""

    validation_results = st.session_state.get("validation_results")

    if not isinstance(validation_results, dict):
        return False

    return bool(
        validation_results.get(
            "validation_passed",
            False,
        )
    )
