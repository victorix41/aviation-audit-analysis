"""Tests for cached report-generation services."""

from datetime import date
from unittest.mock import patch

import pandas as pd

from src.reports.cached_reports import (
    generate_cached_excel_report,
    generate_cached_word_report,
)


def create_cleaned_dataframe() -> pd.DataFrame:
    """Create minimal cleaned data for cached-report tests."""

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


def test_generate_cached_word_report() -> None:
    """Return Word bytes from the underlying generator."""

    dataframe = create_cleaned_dataframe()

    generate_cached_word_report.clear()

    with patch(
        "src.reports.cached_reports.generate_management_word_report",
        return_value=b"word-report",
    ) as generator_mock:
        result = generate_cached_word_report(
            dataframe,
            source_file_name="audit.xlsx",
            as_of_date=date(
                2026,
                8,
                2,
            ),
        )

    assert result == b"word-report"
    generator_mock.assert_called_once()


def test_generate_cached_excel_report() -> None:
    """Return Excel bytes from the underlying generator."""

    dataframe = create_cleaned_dataframe()

    generate_cached_excel_report.clear()

    with patch(
        "src.reports.cached_reports.generate_management_excel_report",
        return_value=b"excel-report",
    ) as generator_mock:
        result = generate_cached_excel_report(
            dataframe,
            source_file_name="audit.xlsx",
            as_of_date=date(
                2026,
                8,
                2,
            ),
        )

    assert result == b"excel-report"
    generator_mock.assert_called_once()


def test_word_report_reuses_cached_result() -> None:
    """Avoid regenerating a Word report for identical inputs."""

    dataframe = create_cleaned_dataframe()

    generate_cached_word_report.clear()

    with patch(
        "src.reports.cached_reports.generate_management_word_report",
        return_value=b"word-report",
    ) as generator_mock:
        first_result = generate_cached_word_report(
            dataframe,
            source_file_name="audit.xlsx",
            as_of_date=date(
                2026,
                8,
                2,
            ),
        )

        second_result = generate_cached_word_report(
            dataframe,
            source_file_name="audit.xlsx",
            as_of_date=date(
                2026,
                8,
                2,
            ),
        )

    assert first_result == b"word-report"
    assert second_result == b"word-report"
    generator_mock.assert_called_once()
