"""Tests for the Reports page."""

from datetime import date
from unittest.mock import patch

import pandas as pd

from src.ui.pages.reports import (
    _generate_reports,
    _reports_match_current_inputs,
    render,
)


def create_cleaned_dataframe() -> pd.DataFrame:
    """Create complete cleaned data for report-page tests."""

    return pd.DataFrame(
        {
            "audit_reference_no": [
                "AF-001",
            ],
            "finding": [
                "Finding one",
            ],
            "severity_level": [
                "Major",
            ],
            "response_due_date": pd.to_datetime(
                [
                    "2026-01-10",
                ]
            ),
            "immediate_action": [
                "Contain issue",
            ],
            "root_cause": [
                "Procedure weakness",
            ],
            "human_factor": [
                "Knowledge gap",
            ],
            "corrective_action": [
                "Revise procedure",
            ],
            "preventive_action": [
                "Update checklist",
            ],
        }
    )


def test_reports_match_current_inputs() -> None:
    report_date = date(
        2026,
        2,
        1,
    )

    with patch(
        "src.ui.pages.reports.st.session_state",
        {
            "word_report_bytes": b"word",
            "excel_report_bytes": b"excel",
            "report_as_of_date": report_date,
            "report_source_file_name": "audit.xlsx",
        },
    ):
        result = _reports_match_current_inputs(
            source_file_name="audit.xlsx",
            as_of_date=report_date,
        )

    assert result is True


def test_reports_do_not_match_changed_date() -> None:
    with patch(
        "src.ui.pages.reports.st.session_state",
        {
            "word_report_bytes": b"word",
            "excel_report_bytes": b"excel",
            "report_as_of_date": date(
                2026,
                2,
                1,
            ),
            "report_source_file_name": "audit.xlsx",
        },
    ):
        result = _reports_match_current_inputs(
            source_file_name="audit.xlsx",
            as_of_date=date(
                2026,
                3,
                1,
            ),
        )

    assert result is False


def test_generate_reports_stores_report_bytes() -> None:
    dataframe = create_cleaned_dataframe()
    session_state: dict[str, object] = {}

    with (
        patch(
            "src.ui.pages.reports.st.session_state",
            session_state,
        ),
        patch(
            "src.ui.pages.reports.generate_cached_word_report",
            return_value=b"word-report",
        ) as word_mock,
        patch(
            "src.ui.pages.reports.generate_cached_excel_report",
            return_value=b"excel-report",
        ) as excel_mock,
    ):
        _generate_reports(
            dataframe,
            source_file_name="audit.xlsx",
            as_of_date=date(
                2026,
                2,
                1,
            ),
        )

    word_mock.assert_called_once()
    excel_mock.assert_called_once()

    assert session_state["word_report_bytes"] == b"word-report"

    assert session_state["excel_report_bytes"] == b"excel-report"


def test_render_warns_when_data_is_missing() -> None:
    with (
        patch(
            "src.ui.pages.reports.st.session_state",
            {},
        ),
        patch("src.ui.pages.reports.st.warning") as warning_mock,
        patch("src.ui.pages.reports.render_page_header"),
    ):
        render("Reports description")

    warning_mock.assert_called_once()
