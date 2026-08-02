"""Tests for the Data Quality page."""

from unittest.mock import patch

import pandas as pd

from src.ui.pages.data_quality import (
    _build_missing_value_summary,
    _build_validation_summary,
    render,
)


def create_cleaned_dataframe() -> pd.DataFrame:
    """Create cleaned data for page tests."""

    return pd.DataFrame(
        {
            "audit_reference_no": [
                "AF-001",
                "AF-002",
            ],
            "finding": [
                "Finding one",
                "Finding two",
            ],
            "severity_level": [
                "Major",
                "Minor",
            ],
            "response_due_date": pd.to_datetime(
                [
                    "2026-01-10",
                    None,
                ]
            ),
            "root_cause": [
                "Procedure weakness",
                "",
            ],
            "corrective_action": [
                "Revise procedure",
                "Provide training",
            ],
            "preventive_action": [
                "Review programme",
                "Update checklist",
            ],
        }
    )


def test_build_validation_summary() -> None:
    validation_results = {
        "missing_required_columns": [],
        "duplicate_reference_numbers": 0,
        "missing_reference_numbers": 0,
        "missing_findings": 0,
        "missing_due_dates": 1,
        "missing_root_causes": 1,
        "missing_corrective_actions": 0,
        "missing_preventive_actions": 0,
        "invalid_severity_values": 0,
    }

    summary = _build_validation_summary(validation_results)

    assert len(summary) == 9

    missing_due_date_row = summary.loc[
        summary["Validation check"].eq("Missing due dates")
    ].iloc[0]

    assert missing_due_date_row["Records affected"] == 1

    assert missing_due_date_row["Status"] == "Requires attention"


def test_build_missing_value_summary() -> None:
    dataframe = create_cleaned_dataframe()

    summary = _build_missing_value_summary(dataframe)

    due_date_row = summary.loc[summary["Column"].eq("response_due_date")].iloc[0]

    assert due_date_row["Missing values"] == 1
    assert due_date_row["Total incomplete"] == 1


def test_render_warns_when_data_is_missing() -> None:
    with (
        patch(
            "src.ui.pages.data_quality.st.session_state",
            {},
        ),
        patch("src.ui.pages.data_quality.st.warning") as warning_mock,
        patch("src.ui.pages.data_quality.render_page_header"),
    ):
        render("Data-quality description")

    warning_mock.assert_called_once()


def test_render_uses_stored_validation_results() -> None:
    dataframe = create_cleaned_dataframe()

    validation_results = {
        "total_records": 2,
        "missing_required_columns": [],
        "duplicate_reference_numbers": 0,
        "missing_reference_numbers": 0,
        "missing_findings": 0,
        "missing_due_dates": 1,
        "missing_root_causes": 1,
        "missing_corrective_actions": 0,
        "missing_preventive_actions": 0,
        "invalid_severity_values": 0,
        "invalid_severity_records": [],
        "validation_passed": False,
    }

    with (
        patch(
            "src.ui.pages.data_quality.st.session_state",
            {
                "cleaned_dataframe": dataframe,
                "validation_results": validation_results,
            },
        ),
        patch("src.ui.pages.data_quality.render_page_header"),
        patch("src.ui.pages.data_quality._render_quality_kpis") as kpi_mock,
        patch("src.ui.pages.data_quality._render_validation_status"),
        patch("src.ui.pages.data_quality._render_validation_tables"),
        patch("src.ui.pages.data_quality._render_exception_records"),
        patch("src.ui.pages.data_quality._render_downloads"),
        patch("src.ui.pages.data_quality.st.divider"),
        patch("src.ui.pages.data_quality.st.caption"),
    ):
        render("Data-quality description")

    kpi_mock.assert_called_once_with(
        dataframe,
        validation_results,
    )
