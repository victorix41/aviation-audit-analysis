import pandas as pd
import pytest

from src.analytics.human_factor_engine import (
    generate_human_factor_analysis,
)


def create_human_factor_test_data() -> pd.DataFrame:
    """Create predictable human-factor records for testing."""

    return pd.DataFrame(
        {
            "human_factor": [
                "Knowledge gap",
                " communication ",
                "Knowledge Gap",
                "Time pressure",
                "Communication",
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


def test_current_human_factor_counts() -> None:
    dataframe = create_human_factor_test_data()

    result = generate_human_factor_analysis(
        dataframe
    )

    assert result.total_findings == 7
    assert result.specified_findings == 5
    assert result.unspecified_findings == 2
    assert result.unique_human_factors == 3


def test_current_human_factor_percentages() -> None:
    dataframe = create_human_factor_test_data()

    result = generate_human_factor_analysis(
        dataframe
    )

    assert result.specified_percentage == 71.43
    assert result.unspecified_percentage == 28.57


def test_human_factor_standardisation() -> None:
    dataframe = create_human_factor_test_data()

    result = generate_human_factor_analysis(
        dataframe
    )

    assert set(
        result.pareto.categories
    ) == {
        "Knowledge gap",
        "Communication",
        "Time pressure",
        "Unspecified",
    }


def test_human_factor_pareto_result() -> None:
    dataframe = create_human_factor_test_data()

    result = generate_human_factor_analysis(
        dataframe
    )

    assert result.pareto.total_records == 7

    assert result.top_factor in {
        "Knowledge gap",
        "Communication",
        "Unspecified",
    }

    assert result.top_factor_frequency == 2
    assert result.top_factor_percentage == 28.57

    assert result.pareto.table.iloc[-1][
        "cumulative_percentage"
    ] == 100.0


def test_monthly_human_factor_trend() -> None:
    dataframe = create_human_factor_test_data()

    result = generate_human_factor_analysis(
        dataframe
    )

    assert result.monthly_trend[
        "period"
    ].unique().tolist() == [
        "2025-12",
        "2026-01",
        "2026-02",
        "2026-03",
        "2026-04",
    ]

    january_rows = result.monthly_trend[
        result.monthly_trend["period"]
        == "2026-01"
    ]

    assert january_rows[
        "period_total"
    ].unique().tolist() == [2]

    assert january_rows[
        "frequency"
    ].sum() == 2


def test_quarterly_human_factor_trend() -> None:
    dataframe = create_human_factor_test_data()

    result = generate_human_factor_analysis(
        dataframe
    )

    periods = result.quarterly_trend[
        "period"
    ].unique().tolist()

    assert periods == [
        "2025Q4",
        "2026Q1",
        "2026Q2",
    ]

    q1_rows = result.quarterly_trend[
        result.quarterly_trend["period"]
        == "2026Q1"
    ]

    assert q1_rows[
        "period_total"
    ].unique().tolist() == [5]


def test_yearly_human_factor_trend() -> None:
    dataframe = create_human_factor_test_data()

    result = generate_human_factor_analysis(
        dataframe
    )

    periods = result.yearly_trend[
        "period"
    ].unique().tolist()

    assert periods == [
        "2025",
        "2026",
    ]

    year_2026_rows = result.yearly_trend[
        result.yearly_trend["period"]
        == "2026"
    ]

    assert year_2026_rows[
        "period_total"
    ].unique().tolist() == [6]


def test_latest_period_changes() -> None:
    dataframe = create_human_factor_test_data()

    result = generate_human_factor_analysis(
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

    assert result.has_monthly_comparison is True
    assert result.has_quarterly_comparison is True
    assert result.has_yearly_comparison is True


def test_empty_dataframe_returns_empty_analysis() -> None:
    dataframe = pd.DataFrame(
        {
            "human_factor": pd.Series(
                dtype="string"
            ),
            "response_due_date": pd.Series(
                dtype="datetime64[ns]"
            ),
        }
    )

    result = generate_human_factor_analysis(
        dataframe
    )

    assert result.total_findings == 0
    assert result.specified_findings == 0
    assert result.unspecified_findings == 0
    assert result.unique_human_factors == 0

    assert result.top_factor is None
    assert result.top_factor_frequency == 0
    assert result.top_factor_percentage == 0.0

    assert result.monthly_trend.empty
    assert result.quarterly_trend.empty
    assert result.yearly_trend.empty

    assert result.has_monthly_comparison is False


def test_missing_required_column_raises_error() -> None:
    dataframe = pd.DataFrame(
        {
            "human_factor": [
                "Knowledge gap",
            ]
        }
    )

    with pytest.raises(
        KeyError,
        match="response_due_date",
    ):
        generate_human_factor_analysis(
            dataframe
        )