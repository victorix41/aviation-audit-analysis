from datetime import date

import pandas as pd
import pytest

from src.analytics.kpi_engine import (
    generate_audit_summary,
)


def create_kpi_test_data() -> pd.DataFrame:
    """Create predictable audit data for KPI testing."""

    return pd.DataFrame(
        {
            "severity_level": [
                "Observation",
                "Minor",
                "Minor",
                "Major",
                None,
            ],
            "response_due_date": pd.to_datetime(
                [
                    "2026-07-01",
                    "2026-07-30",
                    "2026-08-15",
                    "2026-09-15",
                    None,
                ]
            ),
        }
    )


def test_summary_counts() -> None:
    dataframe = create_kpi_test_data()

    summary = generate_audit_summary(
        dataframe,
        as_of_date=date(2026, 7, 30),
    )

    assert summary.total_findings == 5
    assert summary.observation_count == 1
    assert summary.minor_count == 2
    assert summary.major_count == 1
    assert summary.unspecified_severity_count == 1
    assert summary.severity_total == 5


def test_summary_percentages() -> None:
    dataframe = create_kpi_test_data()

    summary = generate_audit_summary(
        dataframe,
        as_of_date=date(2026, 7, 30),
    )

    assert summary.observation_percentage == 20.0
    assert summary.minor_percentage == 40.0
    assert summary.major_percentage == 20.0

    assert (
        summary.unspecified_severity_percentage
        == 20.0
    )


def test_due_date_kpis() -> None:
    dataframe = create_kpi_test_data()

    summary = generate_audit_summary(
        dataframe,
        as_of_date=date(2026, 7, 30),
    )

    assert summary.past_due_response_count == 1
    assert summary.due_within_30_days_count == 2
    assert summary.future_due_count == 1
    assert summary.missing_due_date_count == 1


def test_due_date_range() -> None:
    dataframe = create_kpi_test_data()

    summary = generate_audit_summary(
        dataframe,
        as_of_date=date(2026, 7, 30),
    )

    assert summary.earliest_due_date == date(
        2026,
        7,
        1,
    )

    assert summary.latest_due_date == date(
        2026,
        9,
        15,
    )


def test_empty_dataframe_returns_zero_kpis() -> None:
    dataframe = pd.DataFrame(
        {
            "severity_level": pd.Series(
                dtype="string"
            ),
            "response_due_date": pd.Series(
                dtype="datetime64[ns]"
            ),
        }
    )

    summary = generate_audit_summary(
        dataframe,
        as_of_date=date(2026, 7, 30),
    )

    assert summary.total_findings == 0
    assert summary.major_count == 0
    assert summary.major_percentage == 0.0
    assert summary.past_due_response_count == 0
    assert summary.earliest_due_date is None
    assert summary.latest_due_date is None


def test_missing_required_column_raises_error() -> None:
    dataframe = pd.DataFrame(
        {
            "severity_level": [
                "Minor",
            ]
        }
    )

    with pytest.raises(
        KeyError,
        match="response_due_date",
    ):
        generate_audit_summary(
            dataframe,
            as_of_date=date(2026, 7, 30),
        )