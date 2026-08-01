"""Tests for shared period-comparison utilities."""

import pandas as pd
import pytest

from src.analytics.common.period_comparison import (
    calculate_latest_period_total_change,
)


def test_calculates_positive_change() -> None:
    trend_table = pd.DataFrame(
        {
            "period": [
                "2026-01",
                "2026-02",
            ],
            "period_total": [
                10,
                15,
            ],
        }
    )

    result = calculate_latest_period_total_change(trend_table)

    assert result == (
        5,
        50.0,
    )


def test_calculates_negative_change() -> None:
    trend_table = pd.DataFrame(
        {
            "period": [
                "2026-01",
                "2026-02",
            ],
            "period_total": [
                20,
                5,
            ],
        }
    )

    result = calculate_latest_period_total_change(trend_table)

    assert result == (
        -15,
        -75.0,
    )


def test_uses_latest_two_sorted_periods() -> None:
    trend_table = pd.DataFrame(
        {
            "period": [
                "2026-03",
                "2026-01",
                "2026-02",
            ],
            "period_total": [
                12,
                5,
                10,
            ],
        }
    )

    result = calculate_latest_period_total_change(trend_table)

    assert result == (
        2,
        20.0,
    )


def test_duplicate_period_rows_are_counted_once() -> None:
    trend_table = pd.DataFrame(
        {
            "period": [
                "2026-01",
                "2026-01",
                "2026-02",
                "2026-02",
            ],
            "period_total": [
                10,
                10,
                15,
                15,
            ],
        }
    )

    result = calculate_latest_period_total_change(trend_table)

    assert result == (
        5,
        50.0,
    )


def test_single_period_returns_none_values() -> None:
    trend_table = pd.DataFrame(
        {
            "period": [
                "2026-01",
            ],
            "period_total": [
                10,
            ],
        }
    )

    result = calculate_latest_period_total_change(trend_table)

    assert result == (
        None,
        None,
    )


def test_empty_table_returns_none_values() -> None:
    trend_table = pd.DataFrame(
        columns=[
            "period",
            "period_total",
        ]
    )

    result = calculate_latest_period_total_change(trend_table)

    assert result == (
        None,
        None,
    )


def test_zero_previous_total_and_zero_latest_total() -> None:
    trend_table = pd.DataFrame(
        {
            "period": [
                "2026-01",
                "2026-02",
            ],
            "period_total": [
                0,
                0,
            ],
        }
    )

    result = calculate_latest_period_total_change(trend_table)

    assert result == (
        0,
        0.0,
    )


def test_zero_previous_total_and_positive_latest_total() -> None:
    trend_table = pd.DataFrame(
        {
            "period": [
                "2026-01",
                "2026-02",
            ],
            "period_total": [
                0,
                5,
            ],
        }
    )

    result = calculate_latest_period_total_change(trend_table)

    assert result == (
        5,
        None,
    )


def test_missing_required_column_raises_error() -> None:
    trend_table = pd.DataFrame(
        {
            "period": [
                "2026-01",
            ],
        }
    )

    with pytest.raises(
        KeyError,
        match="period_total",
    ):
        calculate_latest_period_total_change(trend_table)


def test_non_dataframe_input_raises_error() -> None:
    with pytest.raises(
        TypeError,
        match="pandas DataFrame",
    ):
        calculate_latest_period_total_change([])
