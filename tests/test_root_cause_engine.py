"""Tests for the root-cause analytics engine."""

import pandas as pd
import pytest

from src.analytics.root_cause_engine import (
    generate_root_cause_analysis,
)


def create_root_cause_test_data() -> pd.DataFrame:
    """Create predictable root-cause data for testing."""

    return pd.DataFrame(
        {
            "root_cause": [
                "Document control weakness.",
                " document   control weakness. ",
                "Workload prioritisation.",
                "Procedure not consistently followed.",
                "Workload prioritisation.",
                None,
                "",
            ],
            "response_due_date": pd.to_datetime(
                [
                    "2025-12-15",
                    "2026-01-10",
                    "2026-01-20",
                    "2026-02-05",
                    "2026-02-15",
                    "2026-03-01",
                    "2026-04-01",
                ]
            ),
        }
    )


def test_root_cause_counts() -> None:
    dataframe = create_root_cause_test_data()

    result = generate_root_cause_analysis(
        dataframe
    )

    assert result.total_findings == 7
    assert result.specified_findings == 5
    assert result.unspecified_findings == 2
    assert result.unique_root_causes == 3


def test_root_cause_percentages() -> None:
    dataframe = create_root_cause_test_data()

    result = generate_root_cause_analysis(
        dataframe
    )

    assert result.specified_percentage == 71.43
    assert result.unspecified_percentage == 28.57


def test_root_cause_standardisation() -> None:
    dataframe = create_root_cause_test_data()

    result = generate_root_cause_analysis(
        dataframe
    )

    assert set(
        result.pareto.categories
    ) == {
        "Document control weakness.",
        "Workload prioritisation.",
        "Procedure not consistently followed.",
        "Unspecified",
    }


def test_root_cause_pareto() -> None:
    dataframe = create_root_cause_test_data()

    result = generate_root_cause_analysis(
        dataframe
    )

    assert result.pareto.total_records == 7
    assert result.top_root_cause in {
        "Document control weakness.",
        "Workload prioritisation.",
        "Unspecified",
    }

    assert result.top_root_cause_frequency == 2
    assert result.top_root_cause_percentage == 28.57

    assert (
        result.pareto.table.iloc[-1][
            "cumulative_percentage"
        ]
        == 100.0
    )


def test_monthly_root_cause_trend() -> None:
    dataframe = create_root_cause_test_data()

    result = generate_root_cause_analysis(
        dataframe
    )

    assert (
        result.monthly_trend["period"]
        .unique()
        .tolist()
        == [
            "2025-12",
            "2026-01",
            "2026-02",
            "2026-03",
            "2026-04",
        ]
    )

    january_rows = result.monthly_trend[
        result.monthly_trend["period"]
        == "2026-01"
    ]

    assert (
        january_rows["period_total"]
        .unique()
        .tolist()
        == [2]
    )

    assert january_rows["frequency"].sum() == 2


def test_quarterly_root_cause_trend() -> None:
    dataframe = create_root_cause_test_data()

    result = generate_root_cause_analysis(
        dataframe
    )

    assert (
        result.quarterly_trend["period"]
        .unique()
        .tolist()
        == [
            "2025Q4",
            "2026Q1",
            "2026Q2",
        ]
    )

    q1_rows = result.quarterly_trend[
        result.quarterly_trend["period"]
        == "2026Q1"
    ]

    assert (
        q1_rows["period_total"]
        .unique()
        .tolist()
        == [5]
    )


def test_yearly_root_cause_trend() -> None:
    dataframe = create_root_cause_test_data()

    result = generate_root_cause_analysis(
        dataframe
    )

    assert (
        result.yearly_trend["period"]
        .unique()
        .tolist()
        == [
            "2025",
            "2026",
        ]
    )

    year_2026_rows = result.yearly_trend[
        result.yearly_trend["period"]
        == "2026"
    ]

    assert (
        year_2026_rows["period_total"]
        .unique()
        .tolist()
        == [6]
    )


def test_wide_trend_table() -> None:
    dataframe = create_root_cause_test_data()

    result = generate_root_cause_analysis(
        dataframe
    )

    assert "period" in result.monthly_wide_trend.columns
    assert "total" in result.monthly_wide_trend.columns

    assert (
        result.monthly_wide_trend["total"]
        .tolist()
        == [
            1,
            2,
            2,
            1,
            1,
        ]
    )


def test_latest_period_changes() -> None:
    dataframe = create_root_cause_test_data()

    result = generate_root_cause_analysis(
        dataframe
    )

    assert result.latest_month_total_change == 0
    assert (
        result.latest_month_total_change_percentage
        == 0.0
    )

    assert result.latest_quarter_total_change == -4
    assert (
        result.latest_quarter_total_change_percentage
        == -80.0
    )

    assert result.latest_year_total_change == 5
    assert (
        result.latest_year_total_change_percentage
        == 500.0
    )


def test_empty_dataframe() -> None:
    dataframe = pd.DataFrame(
        {
            "root_cause": pd.Series(
                dtype="string"
            ),
            "response_due_date": pd.Series(
                dtype="datetime64[ns]"
            ),
        }
    )

    result = generate_root_cause_analysis(
        dataframe
    )

    assert result.total_findings == 0
    assert result.specified_findings == 0
    assert result.unspecified_findings == 0
    assert result.unique_root_causes == 0

    assert result.top_root_cause is None
    assert result.top_root_cause_frequency == 0
    assert result.top_root_cause_percentage == 0.0

    assert result.monthly_trend.empty
    assert result.monthly_wide_trend.empty
    assert result.has_monthly_comparison is False


def test_missing_required_column_raises_error() -> None:
    dataframe = pd.DataFrame(
        {
            "root_cause": [
                "Workload prioritisation.",
            ]
        }
    )

    with pytest.raises(
        KeyError,
        match="response_due_date",
    ):
        generate_root_cause_analysis(
            dataframe
        )