"""Tests for shared required-column validation."""

import pandas as pd
import pytest

from src.analytics.common.column_validation import (
    validate_required_columns,
)


def test_validation_passes_when_all_columns_exist():
    dataframe = pd.DataFrame(
        {
            "category": ["A"],
            "date": ["2026-01-01"],
        }
    )

    result = validate_required_columns(
        dataframe,
        {"category", "date"},
        "test analysis",
    )

    assert result is None


def test_validation_allows_additional_columns():
    dataframe = pd.DataFrame(
        {
            "category": ["A"],
            "date": ["2026-01-01"],
            "extra": [123],
        }
    )

    validate_required_columns(
        dataframe,
        {"category", "date"},
        "test analysis",
    )


def test_missing_column_raises_key_error():
    dataframe = pd.DataFrame(
        {
            "category": ["A"],
        }
    )

    with pytest.raises(
        KeyError,
        match=(
            r"Required test analysis column\(s\) "
            r"missing: date"
        ),
    ):
        validate_required_columns(
            dataframe,
            {"category", "date"},
            "test analysis",
        )


def test_multiple_missing_columns_are_sorted():
    dataframe = pd.DataFrame(
        {
            "available": [1],
        }
    )

    with pytest.raises(
        KeyError,
        match=(
            r"Required test analysis column\(s\) "
            r"missing: alpha, zebra"
        ),
    ):
        validate_required_columns(
            dataframe,
            {"zebra", "alpha"},
            "test analysis",
        )


def test_required_columns_can_be_a_list():
    dataframe = pd.DataFrame(
        {
            "category": ["A"],
            "date": ["2026-01-01"],
        }
    )

    validate_required_columns(
        dataframe,
        ["category", "date"],
        "test analysis",
    )


def test_empty_required_columns_pass_validation():
    dataframe = pd.DataFrame(
        {
            "category": ["A"],
        }
    )

    validate_required_columns(
        dataframe,
        set(),
        "test analysis",
    )


def test_non_dataframe_input_raises_type_error():
    with pytest.raises(
        TypeError,
        match="dataframe must be a pandas DataFrame",
    ):
        validate_required_columns(
            {"category": ["A"]},
            {"category"},
            "test analysis",
        )


def test_empty_context_raises_value_error():
    dataframe = pd.DataFrame(
        {
            "category": ["A"],
        }
    )

    with pytest.raises(
        ValueError,
        match="context must not be empty",
    ):
        validate_required_columns(
            dataframe,
            {"category"},
            "   ",
        )
