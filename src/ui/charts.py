"""Reusable chart-building functions for the Streamlit dashboard."""

from typing import Any

import altair as alt
import pandas as pd

SEVERITY_ORDER = [
    "Major",
    "Minor",
    "Observation",
    "Unspecified",
]

SEVERITY_COLOURS = [
    "#C62828",
    "#F9A825",
    "#2E7D32",
    "#757575",
]


def _severity_colour_scale() -> alt.Scale:
    """Return the shared severity colour scale."""

    return alt.Scale(
        domain=SEVERITY_ORDER,
        range=SEVERITY_COLOURS,
    )


def build_pareto_chart(
    pareto_table: pd.DataFrame,
    *,
    title: str,
) -> Any:
    """
    Build a Pareto chart with frequency bars and cumulative percentage.

    Expected columns:

    - category
    - frequency
    - percentage
    - cumulative_percentage
    """

    required_columns = {
        "category",
        "frequency",
        "percentage",
        "cumulative_percentage",
    }

    missing_columns = required_columns - set(pareto_table.columns)

    if missing_columns:
        missing_text = ", ".join(sorted(missing_columns))

        raise KeyError(f"Required Pareto chart column(s) missing: {missing_text}")

    chart_data = pareto_table.copy()

    chart_data["category"] = chart_data["category"].astype(str)

    chart_data["frequency"] = pd.to_numeric(
        chart_data["frequency"],
        errors="coerce",
    ).fillna(0)

    chart_data["percentage"] = pd.to_numeric(
        chart_data["percentage"],
        errors="coerce",
    ).fillna(0.0)

    chart_data["cumulative_percentage"] = pd.to_numeric(
        chart_data["cumulative_percentage"],
        errors="coerce",
    ).fillna(0.0)

    chart_data = chart_data.sort_values(
        by=[
            "frequency",
            "category",
        ],
        ascending=[
            False,
            True,
        ],
    ).reset_index(drop=True)

    chart_data["cumulative_percentage"] = chart_data["cumulative_percentage"].clip(
        lower=0,
        upper=100,
    )

    category_order = chart_data["category"].tolist()

    # Left-axis layer: finding-frequency bars.
    frequency_bars = (
        alt.Chart(chart_data)
        .mark_bar(
            cornerRadiusTopLeft=2,
            cornerRadiusTopRight=2,
        )
        .encode(
            x=alt.X(
                "category:N",
                sort=category_order,
                title="Severity category",
                axis=alt.Axis(
                    labelAngle=0,
                    labelPadding=10,
                ),
            ),
            y=alt.Y(
                "frequency:Q",
                title="Number of findings",
                axis=alt.Axis(
                    orient="left",
                    titlePadding=12,
                    tickCount=6,
                ),
            ),
            color=alt.Color(
                "category:N",
                title="Severity",
                scale=_severity_colour_scale(),
                legend=alt.Legend(
                    orient="right",
                    titleFontSize=13,
                    labelFontSize=12,
                ),
            ),
            tooltip=[
                alt.Tooltip(
                    "category:N",
                    title="Severity",
                ),
                alt.Tooltip(
                    "frequency:Q",
                    title="Findings",
                    format=",.0f",
                ),
                alt.Tooltip(
                    "percentage:Q",
                    title="Percentage",
                    format=".2f",
                ),
            ],
        )
    )

    frequency_labels = (
        alt.Chart(chart_data)
        .mark_text(
            dy=-10,
            fontSize=13,
            fontWeight="bold",
            color="#212121",
        )
        .encode(
            x=alt.X(
                "category:N",
                sort=category_order,
            ),
            y=alt.Y(
                "frequency:Q",
            ),
            text=alt.Text(
                "frequency:Q",
                format=",.0f",
            ),
        )
    )

    frequency_layer = alt.layer(
        frequency_bars,
        frequency_labels,
    )

    # Right-axis layer: cumulative-percentage line.
    cumulative_line = (
        alt.Chart(chart_data)
        .mark_line(
            point=alt.OverlayMarkDef(
                filled=True,
                size=90,
            ),
            color="#1565C0",
            strokeWidth=3,
        )
        .encode(
            x=alt.X(
                "category:N",
                sort=category_order,
            ),
            y=alt.Y(
                "cumulative_percentage:Q",
                title="Cumulative percentage",
                scale=alt.Scale(
                    domain=[
                        0,
                        100,
                    ]
                ),
                axis=alt.Axis(
                    orient="right",
                    titlePadding=14,
                    values=[
                        0,
                        20,
                        40,
                        60,
                        80,
                        100,
                    ],
                    labelExpr="datum.value + '%'",
                ),
            ),
            tooltip=[
                alt.Tooltip(
                    "category:N",
                    title="Severity",
                ),
                alt.Tooltip(
                    "cumulative_percentage:Q",
                    title="Cumulative percentage",
                    format=".2f",
                ),
            ],
        )
    )

    cumulative_labels = (
        alt.Chart(chart_data)
        .transform_calculate(
            cumulative_label=("format(datum.cumulative_percentage, '.0f') + '%'")
        )
        .mark_text(
            dy=-16,
            fontSize=13,
            fontWeight="bold",
            color="#1565C0",
        )
        .encode(
            x=alt.X(
                "category:N",
                sort=category_order,
            ),
            y=alt.Y(
                "cumulative_percentage:Q",
                scale=alt.Scale(
                    domain=[
                        0,
                        100,
                    ]
                ),
                axis=None,
            ),
            text=alt.Text(
                "cumulative_label:N",
            ),
        )
    )

    threshold_data = pd.DataFrame(
        {
            "category": [
                category_order[-1],
            ],
            "threshold": [
                80.0,
            ],
            "threshold_label": [
                "80% Pareto line",
            ],
        }
    )

    threshold_line = (
        alt.Chart(threshold_data)
        .mark_rule(
            strokeDash=[
                6,
                4,
            ],
            color="#616161",
            strokeWidth=1.5,
        )
        .encode(
            y=alt.Y(
                "threshold:Q",
                scale=alt.Scale(
                    domain=[
                        0,
                        100,
                    ]
                ),
                axis=None,
            ),
            tooltip=[
                alt.Tooltip(
                    "threshold:Q",
                    title="Pareto reference",
                    format=".0f",
                )
            ],
        )
    )

    threshold_label = (
        alt.Chart(threshold_data)
        .mark_text(
            align="right",
            dx=-5,
            dy=-8,
            color="#616161",
            fontSize=12,
        )
        .encode(
            x=alt.X(
                "category:N",
                sort=category_order,
            ),
            y=alt.Y(
                "threshold:Q",
                scale=alt.Scale(
                    domain=[
                        0,
                        100,
                    ]
                ),
                axis=None,
            ),
            text=alt.Text(
                "threshold_label:N",
            ),
        )
    )

    # These layers share one percentage scale and therefore one right axis.
    percentage_layer = alt.layer(
        cumulative_line,
        cumulative_labels,
        threshold_line,
        threshold_label,
    )

    return (
        alt.layer(
            frequency_layer,
            percentage_layer,
        )
        .resolve_scale(
            y="independent",
        )
        .properties(
            title=title,
            height=380,
        )
        .configure_view(
            stroke=None,
        )
    )


def build_monthly_workload_chart(
    monthly_trend: pd.DataFrame,
    *,
    title: str,
) -> Any:
    """
    Build a monthly response-due-date workload chart.

    Expected columns:

    - period
    - Observation
    - Minor
    - Major
    - Unspecified
    - total
    """

    required_columns = {
        "period",
        "Observation",
        "Minor",
        "Major",
        "Unspecified",
        "total",
    }

    missing_columns = required_columns - set(monthly_trend.columns)

    if missing_columns:
        missing_text = ", ".join(sorted(missing_columns))

        raise KeyError(f"Required workload chart column(s) missing: {missing_text}")

    chart_data = monthly_trend.copy()

    chart_data["total"] = pd.to_numeric(
        chart_data["total"],
        errors="coerce",
    ).fillna(0)

    long_data = chart_data.melt(
        id_vars=[
            "period",
            "total",
        ],
        value_vars=SEVERITY_ORDER,
        var_name="severity",
        value_name="frequency",
    )

    long_data["frequency"] = pd.to_numeric(
        long_data["frequency"],
        errors="coerce",
    ).fillna(0)

    stacked_bars = (
        alt.Chart(long_data)
        .mark_bar()
        .encode(
            x=alt.X(
                "period:N",
                title="Response due month",
                sort=None,
                axis=alt.Axis(
                    labelAngle=-35,
                    labelPadding=8,
                ),
            ),
            y=alt.Y(
                "frequency:Q",
                title="Number of findings",
                stack="zero",
                axis=alt.Axis(
                    titlePadding=12,
                ),
            ),
            color=alt.Color(
                "severity:N",
                title="Severity",
                sort=SEVERITY_ORDER,
                scale=_severity_colour_scale(),
            ),
            tooltip=[
                alt.Tooltip(
                    "period:N",
                    title="Month",
                ),
                alt.Tooltip(
                    "severity:N",
                    title="Severity",
                ),
                alt.Tooltip(
                    "frequency:Q",
                    title="Findings",
                    format=",.0f",
                ),
                alt.Tooltip(
                    "total:Q",
                    title="Monthly total",
                    format=",.0f",
                ),
            ],
        )
    )

    total_line = (
        alt.Chart(chart_data)
        .mark_line(
            point=alt.OverlayMarkDef(
                filled=True,
                size=70,
            ),
            color="#1565C0",
            strokeWidth=3,
        )
        .encode(
            x=alt.X(
                "period:N",
                sort=None,
            ),
            y=alt.Y(
                "total:Q",
                title="Monthly total",
            ),
            tooltip=[
                alt.Tooltip(
                    "period:N",
                    title="Month",
                ),
                alt.Tooltip(
                    "total:Q",
                    title="Monthly total",
                    format=",.0f",
                ),
            ],
        )
    )

    return (
        alt.layer(
            stacked_bars,
            total_line,
        )
        .resolve_scale(
            y="shared",
        )
        .properties(
            title=title,
            height=380,
        )
        .configure_view(
            stroke=None,
        )
    )


def build_horizontal_pareto_chart(
    pareto_table: pd.DataFrame,
    *,
    title: str,
    category_title: str,
    top_n: int | None = None,
) -> Any:
    """
    Build a horizontal Pareto chart sorted by descending frequency.

    Expected columns:

    - category
    - frequency
    - percentage
    - cumulative_percentage

    Args:
        pareto_table:
            Pareto result table.

        title:
            Chart title.

        category_title:
            Label used for the category axis and tooltips.

        top_n:
            Optional maximum number of categories to display.
    """

    required_columns = {
        "category",
        "frequency",
        "percentage",
        "cumulative_percentage",
    }

    missing_columns = required_columns - set(pareto_table.columns)

    if missing_columns:
        missing_text = ", ".join(sorted(missing_columns))

        raise KeyError(
            f"Required horizontal Pareto chart column(s) missing: {missing_text}"
        )

    if top_n is not None and top_n < 1:
        raise ValueError("top_n must be at least 1 when supplied.")

    chart_data = pareto_table.copy()

    chart_data["category"] = chart_data["category"].astype(str)

    chart_data["frequency"] = pd.to_numeric(
        chart_data["frequency"],
        errors="coerce",
    ).fillna(0)

    chart_data["percentage"] = pd.to_numeric(
        chart_data["percentage"],
        errors="coerce",
    ).fillna(0.0)

    chart_data["cumulative_percentage"] = pd.to_numeric(
        chart_data["cumulative_percentage"],
        errors="coerce",
    ).fillna(0.0)

    chart_data = chart_data.sort_values(
        by=[
            "frequency",
            "category",
        ],
        ascending=[
            False,
            True,
        ],
    ).reset_index(drop=True)

    if top_n is not None:
        chart_data = chart_data.head(top_n).copy()

    if chart_data.empty:
        return (
            alt.Chart(chart_data)
            .mark_bar()
            .properties(
                title=title,
                height=120,
            )
        )

    displayed_total = float(chart_data["frequency"].sum())

    if displayed_total > 0:
        chart_data["displayed_cumulative_percentage"] = (
            chart_data["frequency"].cumsum() / displayed_total * 100
        )
    else:
        chart_data["displayed_cumulative_percentage"] = 0.0

    chart_data["displayed_cumulative_percentage"] = chart_data[
        "displayed_cumulative_percentage"
    ].clip(
        lower=0,
        upper=100,
    )

    category_order = chart_data["category"].tolist()

    row_height = 34

    chart_height = max(
        320,
        len(chart_data) * row_height,
    )

    # Blue horizontal frequency bars.
    frequency_bars = (
        alt.Chart(chart_data)
        .mark_bar(
            cornerRadiusEnd=3,
            color="#4C78A8",
        )
        .encode(
            y=alt.Y(
                "category:N",
                sort=category_order,
                title=category_title,
                axis=alt.Axis(
                    labelLimit=340,
                    labelPadding=8,
                    titlePadding=12,
                ),
            ),
            x=alt.X(
                "frequency:Q",
                title="Number of findings",
                axis=alt.Axis(
                    tickMinStep=1,
                    titlePadding=10,
                ),
            ),
            tooltip=[
                alt.Tooltip(
                    "category:N",
                    title=category_title,
                ),
                alt.Tooltip(
                    "frequency:Q",
                    title="Findings",
                    format=",.0f",
                ),
                alt.Tooltip(
                    "percentage:Q",
                    title="Percentage",
                    format=".2f",
                ),
                alt.Tooltip(
                    "cumulative_percentage:Q",
                    title="Overall cumulative percentage",
                    format=".2f",
                ),
            ],
        )
    )

    frequency_labels = (
        alt.Chart(chart_data)
        .mark_text(
            align="left",
            baseline="middle",
            dx=6,
            fontSize=12,
            fontWeight="bold",
            color="#212121",
        )
        .encode(
            y=alt.Y(
                "category:N",
                sort=category_order,
            ),
            x=alt.X(
                "frequency:Q",
            ),
            text=alt.Text(
                "frequency:Q",
                format=",.0f",
            ),
        )
    )

    bar_layer = alt.layer(
        frequency_bars,
        frequency_labels,
    )

    # Orange cumulative-percentage line.
    cumulative_line = (
        alt.Chart(chart_data)
        .mark_line(
            point=alt.OverlayMarkDef(
                filled=True,
                size=75,
            ),
            color="#F28E2B",
            strokeWidth=3,
        )
        .encode(
            y=alt.Y(
                "category:N",
                sort=category_order,
            ),
            x=alt.X(
                "displayed_cumulative_percentage:Q",
                title="Cumulative percentage",
                scale=alt.Scale(
                    domain=[
                        0,
                        100,
                    ]
                ),
                axis=alt.Axis(
                    orient="top",
                    values=[
                        0,
                        20,
                        40,
                        60,
                        80,
                        100,
                    ],
                    labelExpr="datum.value + '%'",
                    titlePadding=10,
                ),
            ),
            tooltip=[
                alt.Tooltip(
                    "category:N",
                    title=category_title,
                ),
                alt.Tooltip(
                    "displayed_cumulative_percentage:Q",
                    title="Displayed cumulative percentage",
                    format=".2f",
                ),
            ],
        )
    )

    cumulative_labels = (
        alt.Chart(chart_data)
        .transform_calculate(
            cumulative_label=(
                "format(datum.displayed_cumulative_percentage, '.0f') + '%'"
            )
        )
        .mark_text(
            align="left",
            baseline="bottom",
            dx=7,
            dy=-5,
            fontSize=11,
            fontWeight="bold",
            color="#F28E2B",
        )
        .encode(
            y=alt.Y(
                "category:N",
                sort=category_order,
            ),
            x=alt.X(
                "displayed_cumulative_percentage:Q",
                scale=alt.Scale(
                    domain=[
                        0,
                        100,
                    ]
                ),
                axis=None,
            ),
            text=alt.Text(
                "cumulative_label:N",
            ),
        )
    )

    threshold_data = pd.DataFrame(
        {
            "threshold": [
                80.0,
            ]
        }
    )

    # Grey 80% Pareto reference line.
    threshold_line = (
        alt.Chart(threshold_data)
        .mark_rule(
            strokeDash=[
                6,
                4,
            ],
            color="#666666",
            strokeWidth=1.5,
        )
        .encode(
            x=alt.X(
                "threshold:Q",
                scale=alt.Scale(
                    domain=[
                        0,
                        100,
                    ]
                ),
                axis=None,
            ),
            tooltip=[
                alt.Tooltip(
                    "threshold:Q",
                    title="Pareto reference",
                    format=".0f",
                )
            ],
        )
    )

    percentage_layer = alt.layer(
        cumulative_line,
        cumulative_labels,
        threshold_line,
    )

    return (
        alt.layer(
            bar_layer,
            percentage_layer,
        )
        .resolve_scale(
            x="independent",
        )
        .properties(
            title=title,
            height=chart_height,
        )
        .configure_view(
            stroke=None,
        )
    )
