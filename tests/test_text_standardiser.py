"""Tests for the shared text-standardisation utility."""

import pandas as pd
import pytest

from src.analytics.common.text_standardiser import (
    standardise_text_series,
)


def test_standardises_case_and_whitespace() -> None:
    series = pd.Series(
        [
            "  KNOWLEDGE   GAP  ",
            "time PRESSURE",
        ]
    )

    result = standardise_text_series(series)

    assert result.tolist() == [
        "Knowledge gap",
        "Time pressure",
    ]


def test_replaces_missing_and_blank_values() -> None:
    series = pd.Series(
        [
            None,
            "",
            "   ",
            pd.NA,
        ]
    )

    result = standardise_text_series(series)

    assert result.tolist() == [
        "Unspecified",
        "Unspecified",
        "Unspecified",
        "Unspecified",
    ]


def test_supports_custom_unspecified_label() -> None:
    series = pd.Series(
        [
            None,
            "",
            "Training issue",
        ]
    )

    result = standardise_text_series(
        series,
        unspecified_label="Not provided",
    )

    assert result.tolist() == [
        "Not provided",
        "Not provided",
        "Training issue",
    ]


def test_can_preserve_original_case() -> None:
    series = pd.Series(
        [
            "  MRO   Procedure  ",
        ]
    )

    result = standardise_text_series(
        series,
        sentence_case=False,
    )

    assert result.tolist() == [
        "MRO Procedure",
    ]


def test_can_preserve_internal_whitespace() -> None:
    series = pd.Series(
        [
            "Knowledge   gap",
        ]
    )

    result = standardise_text_series(
        series,
        collapse_whitespace=False,
    )

    assert result.tolist() == [
        "Knowledge   gap",
    ]


def test_non_series_input_raises_type_error() -> None:
    with pytest.raises(
        TypeError,
        match="pandas Series",
    ):
        standardise_text_series(
            ["Knowledge gap"]  # type: ignore[arg-type]
        )


def test_blank_unspecified_label_raises_error() -> None:
    series = pd.Series(
        [
            None,
        ]
    )

    with pytest.raises(
        ValueError,
        match="must not be blank",
    ):
        standardise_text_series(
            series,
            unspecified_label="   ",
        )
