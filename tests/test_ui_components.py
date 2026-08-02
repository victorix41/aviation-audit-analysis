"""Tests for reusable Streamlit UI components."""

from unittest.mock import MagicMock, patch

import pytest

from src.ui.components import render_kpi_cards


def test_render_kpi_cards_creates_expected_columns() -> None:
    first_column = MagicMock()
    second_column = MagicMock()

    with patch(
        "src.ui.components.st.columns",
        return_value=[
            first_column,
            second_column,
        ],
    ) as columns_mock:
        render_kpi_cards(
            [
                (
                    "Total Findings",
                    100,
                    "Total number of findings.",
                ),
                (
                    "Major Findings",
                    18,
                    None,
                ),
            ],
            columns_per_row=4,
        )

    columns_mock.assert_called_once_with(2)

    first_column.metric.assert_called_once_with(
        label="Total Findings",
        value=100,
        help="Total number of findings.",
    )

    second_column.metric.assert_called_once_with(
        label="Major Findings",
        value=18,
        help=None,
    )


def test_render_kpi_cards_wraps_to_multiple_rows() -> None:
    first_row_columns = [
        MagicMock(),
        MagicMock(),
    ]

    second_row_columns = [
        MagicMock(),
    ]

    with patch(
        "src.ui.components.st.columns",
        side_effect=[
            first_row_columns,
            second_row_columns,
        ],
    ) as columns_mock:
        render_kpi_cards(
            [
                ("Metric 1", 1, None),
                ("Metric 2", 2, None),
                ("Metric 3", 3, None),
            ],
            columns_per_row=2,
        )

    assert columns_mock.call_count == 2

    columns_mock.assert_any_call(2)
    columns_mock.assert_any_call(1)


def test_render_kpi_cards_rejects_invalid_column_count() -> None:
    with pytest.raises(
        ValueError,
        match="columns_per_row must be at least 1",
    ):
        render_kpi_cards(
            [],
            columns_per_row=0,
        )


def test_render_kpi_cards_handles_empty_metrics() -> None:
    with patch("src.ui.components.st.columns") as columns_mock:
        render_kpi_cards([])

    columns_mock.assert_not_called()
