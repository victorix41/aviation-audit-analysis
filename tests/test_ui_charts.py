"""Tests for reusable dashboard charts."""

import pandas as pd
import pytest

from src.ui.charts import (
    build_horizontal_pareto_chart,
    build_monthly_workload_chart,
    build_pareto_chart,
)


def create_pareto_table() -> pd.DataFrame:
    """Create predictable Pareto chart data."""

    return pd.DataFrame(
        {
            "category": [
                "Major",
                "Minor",
                "Observation",
            ],
            "frequency": [
                4,
                3,
                2,
            ],
            "percentage": [
                44.44,
                33.33,
                22.22,
            ],
            "cumulative_percentage": [
                44.44,
                77.77,
                100.0,
            ],
        }
    )


def create_monthly_trend() -> pd.DataFrame:
    """Create predictable monthly severity trend data."""

    return pd.DataFrame(
        {
            "period": [
                "2026-01",
                "2026-02",
            ],
            "Observation": [
                1,
                2,
            ],
            "Minor": [
                2,
                1,
            ],
            "Major": [
                1,
                2,
            ],
            "Unspecified": [
                0,
                0,
            ],
            "total": [
                4,
                5,
            ],
        }
    )


def test_build_pareto_chart() -> None:
    chart = build_pareto_chart(
        create_pareto_table(),
        title="Severity Pareto",
    )

    chart_spec = chart.to_dict()

    assert chart_spec["title"] == "Severity Pareto"
    assert len(chart_spec["layer"]) == 2

    frequency_layer = chart_spec["layer"][0]
    percentage_layer = chart_spec["layer"][1]

    assert len(frequency_layer["layer"]) == 2
    assert len(percentage_layer["layer"]) == 4

    frequency_mark_types = [layer["mark"]["type"] for layer in frequency_layer["layer"]]

    percentage_mark_types = [
        layer["mark"]["type"] for layer in percentage_layer["layer"]
    ]

    assert frequency_mark_types == [
        "bar",
        "text",
    ]

    assert percentage_mark_types == [
        "line",
        "text",
        "rule",
        "text",
    ]


def test_build_monthly_workload_chart() -> None:
    chart = build_monthly_workload_chart(
        create_monthly_trend(),
        title="Monthly Workload",
    )

    chart_spec = chart.to_dict()

    assert chart_spec["title"] == "Monthly Workload"
    assert len(chart_spec["layer"]) == 2


def test_pareto_chart_rejects_missing_columns() -> None:
    incomplete_table = pd.DataFrame(
        {
            "category": [
                "Major",
            ]
        }
    )

    with pytest.raises(
        KeyError,
        match="Required Pareto chart column",
    ):
        build_pareto_chart(
            incomplete_table,
            title="Pareto",
        )


def test_workload_chart_rejects_missing_columns() -> None:
    incomplete_table = pd.DataFrame(
        {
            "period": [
                "2026-01",
            ]
        }
    )

    with pytest.raises(
        KeyError,
        match="Required workload chart column",
    ):
        build_monthly_workload_chart(
            incomplete_table,
            title="Workload",
        )


def test_build_horizontal_pareto_chart() -> None:

    chart = build_horizontal_pareto_chart(
        create_pareto_table(),
        title="Root Cause Pareto",
        category_title="Root cause",
    )

    chart_spec = chart.to_dict()

    assert chart_spec["title"] == "Root Cause Pareto"
    assert len(chart_spec["layer"]) == 2

    bar_layer = chart_spec["layer"][0]
    percentage_layer = chart_spec["layer"][1]

    assert len(bar_layer["layer"]) == 2
    assert len(percentage_layer["layer"]) == 3


def test_horizontal_pareto_rejects_invalid_top_n() -> None:

    with pytest.raises(
        ValueError,
        match="top_n must be at least 1",
    ):
        build_horizontal_pareto_chart(
            create_pareto_table(),
            title="Root Cause Pareto",
            category_title="Root cause",
            top_n=0,
        )
