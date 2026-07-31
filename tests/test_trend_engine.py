"""Tests for the shared trend engine."""

import pandas as pd
import pytest

from src.analytics.common.trend_engine import (
    create_empty_long_trend_table,
    create_empty_wide_trend_table,
    generate_long_trend_table,
    generate_wide_trend_table,
)


def create_test_dataframe() -> pd.DataFrame:
    """Create predictable category and date data."""

    return pd.DataFrame(
        {
            "category": [
                "Knowledge gap",
                " knowledge   gap ",
                "Time pressure",
                "Communication",
                None,
                "",
                "Time pressure",
            ],
            "response_due_date": [
                "2025-12-15",
                "2026-01-10",
                "2026-01-20",
                "2026-02-05",
                "2026-02-15",
                "2026-03-01",
                "invalid-date",
            ],
        }
    )


def test_create_empty_long_trend_table() -> None:
    result = create_empty_long_trend_table(
        "human_factor"
    )

    assert result.empty

    assert result.columns.tolist() == [
        "period",
        "human_factor",
        "frequency",
        "period_total",
        "percentage",
    ]


def test_create_empty_wide_trend_table() -> None:
    result = create_empty_wide_trend_table()

    assert result.empty

    assert result.columns.tolist() == [
        "period",
        "total",
    ]


def test_generate_monthly_long_trend_table() -> None:
    dataframe = create_test_dataframe()

    result = generate_long_trend_table(
        dataframe,
        category_column="category",
        category_output_column="human_factor",
        date_column="response_due_date",
        period_frequency="M",
    )

    assert (
        result["period"]
        .unique()
        .tolist()
        == [
            "2025-12",
            "2026-01",
            "2026-02",
            "2026-03",
        ]
    )

    assert result["frequency"].sum() == 6

    january_rows = result[
        result["period"]
        == "2026-01"
    ]

    assert (
        january_rows["period_total"]
        .unique()
        .tolist()
        == [2]
    )


def test_generate_long_trend_standardises_categories() -> None:
    dataframe = create_test_dataframe()

    result = generate_long_trend_table(
        dataframe,
        category_column="category",
        category_output_column="human_factor",
        date_column="response_due_date",
        period_frequency="M",
    )

    categories = set(
        result["human_factor"]
    )

    assert "Knowledge gap" in categories
    assert "Unspecified" in categories

    assert (
        " knowledge   gap "
        not in categories
    )


def test_generate_quarterly_long_trend_table() -> None:
    dataframe = create_test_dataframe()

    result = generate_long_trend_table(
        dataframe,
        category_column="category",
        category_output_column="category",
        date_column="response_due_date",
        period_frequency="Q",
    )

    assert (
        result["period"]
        .unique()
        .tolist()
        == [
            "2025Q4",
            "2026Q1",
        ]
    )

    q1_rows = result[
        result["period"]
        == "2026Q1"
    ]

    assert (
        q1_rows["period_total"]
        .unique()
        .tolist()
        == [5]
    )


def test_generate_yearly_long_trend_table() -> None:
    dataframe = create_test_dataframe()

    result = generate_long_trend_table(
        dataframe,
        category_column="category",
        category_output_column="category",
        date_column="response_due_date",
        period_frequency="Y",
    )

    assert (
        result["period"]
        .unique()
        .tolist()
        == [
            "2025",
            "2026",
        ]
    )

    year_2026_rows = result[
        result["period"]
        == "2026"
    ]

    assert (
        year_2026_rows["period_total"]
        .unique()
        .tolist()
        == [5]
    )


def test_generate_long_trend_percentages() -> None:
    dataframe = create_test_dataframe()

    result = generate_long_trend_table(
        dataframe,
        category_column="category",
        category_output_column="category",
        date_column="response_due_date",
        period_frequency="M",
    )

    percentage_totals = (
        result
        .groupby("period")[
            "percentage"
        ]
        .sum()
        .round(2)
    )

    assert percentage_totals.tolist() == [
        100.0,
        100.0,
        100.0,
        100.0,
    ]


def test_generate_wide_trend_table() -> None:
    dataframe = create_test_dataframe()

    long_result = generate_long_trend_table(
        dataframe,
        category_column="category",
        category_output_column="human_factor",
        date_column="response_due_date",
        period_frequency="M",
    )

    wide_result = generate_wide_trend_table(
        long_result,
        category_column="human_factor",
    )

    assert "period" in wide_result.columns
    assert "total" in wide_result.columns

    assert (
        wide_result["total"]
        .tolist()
        == [
            1,
            2,
            2,
            1,
        ]
    )

    assert (
        wide_result["total"].sum()
        == 6
    )


def test_empty_source_dataframe_returns_empty_long_table() -> None:
    dataframe = pd.DataFrame(
        {
            "category": pd.Series(
                dtype="string"
            ),
            "response_due_date": pd.Series(
                dtype="datetime64[ns]"
            ),
        }
    )

    result = generate_long_trend_table(
        dataframe,
        category_column="category",
        category_output_column="category",
        date_column="response_due_date",
        period_frequency="M",
    )

    assert result.empty

    assert result.columns.tolist() == [
        "period",
        "category",
        "frequency",
        "period_total",
        "percentage",
    ]


def test_all_invalid_dates_return_empty_long_table() -> None:
    dataframe = pd.DataFrame(
        {
            "category": [
                "Knowledge gap",
                "Time pressure",
            ],
            "response_due_date": [
                "invalid",
                None,
            ],
        }
    )

    result = generate_long_trend_table(
        dataframe,
        category_column="category",
        category_output_column="category",
        date_column="response_due_date",
        period_frequency="M",
    )

    assert result.empty


def test_empty_long_table_returns_empty_wide_table() -> None:
    long_table = (
        create_empty_long_trend_table(
            "category"
        )
    )

    result = generate_wide_trend_table(
        long_table,
        category_column="category",
    )

    assert result.empty

    assert result.columns.tolist() == [
        "period",
        "total",
    ]


def test_missing_source_column_raises_error() -> None:
    dataframe = pd.DataFrame(
        {
            "category": [
                "Knowledge gap",
            ]
        }
    )

    with pytest.raises(
        KeyError,
        match="response_due_date",
    ):
        generate_long_trend_table(
            dataframe,
            category_column="category",
            category_output_column="category",
            date_column="response_due_date",
            period_frequency="M",
        )


def test_invalid_period_frequency_raises_error() -> None:
    dataframe = create_test_dataframe()

    with pytest.raises(
        ValueError,
        match="M, Q, Y",
    ):
        generate_long_trend_table(
            dataframe,
            category_column="category",
            category_output_column="category",
            date_column="response_due_date",
            period_frequency="W",
        )


def test_missing_long_table_column_raises_error() -> None:
    long_table = pd.DataFrame(
        {
            "period": [
                "2026-01",
            ],
            "frequency": [
                1,
            ],
        }
    )

    with pytest.raises(
        KeyError,
        match="category",
    ):
        generate_wide_trend_table(
            long_table,
            category_column="category",
        )


def test_non_dataframe_input_raises_type_error() -> None:
    with pytest.raises(
        TypeError,
        match="pandas DataFrame",
    ):
        generate_long_trend_table(
            [],  # type: ignore[arg-type]
            category_column="category",
            category_output_column="category",
            date_column="response_due_date",
            period_frequency="M",
        )


def test_blank_output_column_raises_error() -> None:
    with pytest.raises(
        ValueError,
        match="must not be blank",
    ):
        create_empty_long_trend_table(
            "   "
        )