"""Tests for shared mathematical analytics utilities."""

import pytest

from src.analytics.common.math_utils import (
    calculate_percentage,
)


def test_calculate_percentage() -> None:
    assert calculate_percentage(1, 4) == 25.0


def test_calculate_percentage_rounds_to_two_places() -> None:
    assert calculate_percentage(1, 6) == 16.67


def test_calculate_percentage_handles_zero_total() -> None:
    assert calculate_percentage(0, 0) == 0.0
    assert calculate_percentage(5, 0) == 0.0


def test_calculate_percentage_supports_custom_precision() -> None:
    assert (
        calculate_percentage(
            1,
            3,
            decimal_places=1,
        )
        == 33.3
    )


def test_calculate_percentage_rejects_negative_precision() -> None:
    with pytest.raises(
        ValueError,
        match="decimal_places must be zero or greater",
    ):
        calculate_percentage(
            1,
            2,
            decimal_places=-1,
        )
