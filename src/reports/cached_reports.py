"""Cached report-generation services for the Streamlit application."""

from datetime import date

import pandas as pd
import streamlit as st

from src.reports.excel_report import (
    generate_management_excel_report,
)
from src.reports.word_report import (
    generate_management_word_report,
)


@st.cache_data(
    show_spinner=False,
    max_entries=8,
)
def generate_cached_word_report(
    dataframe: pd.DataFrame,
    *,
    source_file_name: str,
    as_of_date: date,
) -> bytes:
    """
    Generate or retrieve a cached Word management report.

    Streamlit invalidates the cached result when the DataFrame,
    source filename, report date, or function implementation changes.
    """

    return generate_management_word_report(
        dataframe,
        source_file_name=source_file_name,
        as_of_date=as_of_date,
    )


@st.cache_data(
    show_spinner=False,
    max_entries=8,
)
def generate_cached_excel_report(
    dataframe: pd.DataFrame,
    *,
    source_file_name: str,
    as_of_date: date,
) -> bytes:
    """
    Generate or retrieve a cached Excel analytics workbook.

    Streamlit invalidates the cached result when the DataFrame,
    source filename, report date, or function implementation changes.
    """

    return generate_management_excel_report(
        dataframe,
        source_file_name=source_file_name,
        as_of_date=as_of_date,
    )


def clear_report_cache() -> None:
    """Clear cached Word and Excel report files."""

    generate_cached_word_report.clear()
    generate_cached_excel_report.clear()
