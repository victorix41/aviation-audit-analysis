import pandas as pd
import pytest

from src.analytics.severity_engine import (
    generate_severity_analysis,
)


def create_severity_test_data() -> pd.DataFrame:
    """Create predictable severity records for testing."""

    return pd.DataFrame(
        {
            "severity_level": [
                "Observation",
                "Minor",
                "Major",
                "Minor",
                "Major",
                None,
            ],
            "response_due_date": pd.to_datetime(
                [
                    "2026-01-10",
                    "2026-01-15",
                    "2026-02-05",
                    "2026-02-10",
                    "2026-02-20",
                    "2026-03-01",
                ]
            ),
        }
    )


def test_current_severity_counts() -> None:
    dataframe = create_severity_test_data()

    result = generate_severity_analysis(
        dataframe
    )

    assert result.total_findings == 6
    assert result.observation_count == 1
    assert result.minor_count == 2
    assert result.major_count == 2
    assert result.unspecified_count == 1
    assert result.severity_total == 6


def test_current_severity_percentages() -> None:
    dataframe = create_severity_test_data()

    result = generate_severity_analysis(
        dataframe
    )

    assert result.observation_percentage == 16.67
    assert result.minor_percentage == 33.33
    assert result.major_percentage == 33.33
    assert result.unspecified_percentage == 16.67


def test_severity_pareto_result() -> None:
    dataframe = create_severity_test_data()

    result = generate_severity_analysis(
        dataframe
    )

    assert result.pareto.total_records == 6
    assert result.pareto.frequencies == [
        2,
        2,
        1,
        1,
    ]

    assert set(
        result.pareto.categories
    ) == {
        "Minor",
        "Major",
        "Observation",
        "Unspecified",
    }


def test_monthly_trend() -> None:
    dataframe = create_severity_test_data()

    result = generate_severity_analysis(
        dataframe
    )

    assert result.monthly_trend[
        "period"
    ].tolist() == [
        "2026-01",
        "2026-02",
        "2026-03",
    ]

    assert result.monthly_trend[
        "total"
    ].tolist() == [
        2,
        3,
        1,
    ]

    assert result.monthly_trend[
        "Major"
    ].tolist() == [
        0,
        2,
        0,
    ]


def test_quarterly_and_yearly_trends() -> None:
    dataframe = create_severity_test_data()

    result = generate_severity_analysis(
        dataframe
    )

    assert len(
        result.quarterly_trend
    ) == 1

    assert int(
        result.quarterly_trend.iloc[0]["total"]
    ) == 6

    assert len(
        result.yearly_trend
    ) == 1

    assert int(
        result.yearly_trend.iloc[0]["total"]
    ) == 6


def test_latest_month_change() -> None:
    dataframe = create_severity_test_data()

    result = generate_severity_analysis(
        dataframe
    )

    assert (
        result.latest_month_total_change
        == -2
    )

    assert (
        result.latest_month_total_change_percentage
        == -66.67
    )

    assert (
        result.latest_month_major_change
        == -2
    )

    assert (
        result.latest_month_major_change_percentage
        == -100.0
    )


def test_single_period_has_no_comparison() -> None:
    dataframe = pd.DataFrame(
        {
            "severity_level": [
                "Minor",
                "Major",
            ],
            "response_due_date": pd.to_datetime(
                [
                    "2026-01-01",
                    "2026-01-15",
                ]
            ),
        }
    )

    result = generate_severity_analysis(
        dataframe
    )

    assert (
        result.latest_month_total_change
        is None
    )

    assert (
        result.latest_month_total_change_percentage
        is None
    )

    assert result.has_monthly_comparison is False


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
        generate_severity_analysis(
            dataframe
        )