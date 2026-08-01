import pandas as pd
import pytest

from src.analytics.pareto_engine import generate_pareto


def create_test_dataframe() -> pd.DataFrame:
    """Create sample categorical data for Pareto testing."""

    return pd.DataFrame(
        {
            "human_factor": [
                "Communication",
                "Attention lapse",
                "Communication",
                "Knowledge gap",
                "Communication",
                "Attention lapse",
            ]
        }
    )


def test_pareto_frequency_and_sorting() -> None:
    dataframe = create_test_dataframe()

    result = generate_pareto(
        dataframe,
        "human_factor",
    )

    assert result.total_records == 6

    assert result.categories == [
        "Communication",
        "Attention lapse",
        "Knowledge gap",
    ]

    assert result.frequencies == [3, 2, 1]


def test_pareto_percentages() -> None:
    dataframe = create_test_dataframe()

    result = generate_pareto(
        dataframe,
        "human_factor",
    )

    assert result.percentages == [
        50.0,
        33.33,
        16.67,
    ]

    assert result.cumulative_percentages == [
        50.0,
        83.33,
        100.0,
    ]


def test_pareto_top_category_properties() -> None:
    dataframe = create_test_dataframe()

    result = generate_pareto(
        dataframe,
        "human_factor",
    )

    assert result.top_category == "Communication"
    assert result.top_category_frequency == 3


def test_missing_values_are_excluded_by_default() -> None:
    dataframe = pd.DataFrame(
        {
            "human_factor": [
                "Communication",
                None,
                "",
            ]
        }
    )

    result = generate_pareto(
        dataframe,
        "human_factor",
    )

    assert result.total_records == 1
    assert result.categories == ["Communication"]


def test_missing_values_can_be_included() -> None:
    dataframe = pd.DataFrame(
        {
            "human_factor": [
                "Communication",
                None,
                "",
            ]
        }
    )

    result = generate_pareto(
        dataframe,
        "human_factor",
        include_missing=True,
    )

    assert result.total_records == 3
    assert "Not specified" in result.categories


def test_empty_column_returns_empty_result() -> None:
    dataframe = pd.DataFrame(
        {
            "human_factor": [
                None,
                None,
            ]
        }
    )

    result = generate_pareto(
        dataframe,
        "human_factor",
    )

    assert result.total_records == 0
    assert result.table.empty
    assert result.top_category is None
    assert result.top_category_frequency == 0


def test_missing_column_raises_error() -> None:
    dataframe = create_test_dataframe()

    with pytest.raises(
        KeyError,
        match="does not exist",
    ):
        generate_pareto(
            dataframe,
            "department",
        )
