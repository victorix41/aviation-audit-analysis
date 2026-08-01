import pandas as pd

from src.analytics.common.column_validation import (
    validate_required_columns,
)
from src.analytics.common.math_utils import (
    calculate_percentage,
)
from src.analytics.pareto_engine import generate_pareto
from src.models.severity_analysis import SeverityAnalysis

SEVERITY_COLUMN = "severity_level"
DEFAULT_DATE_COLUMN = "response_due_date"

SEVERITY_CATEGORIES = [
    "Observation",
    "Minor",
    "Major",
    "Unspecified",
]


def _prepare_severity_series(
    dataframe: pd.DataFrame,
) -> pd.Series:
    """Standardise severity values for analysis."""

    severity = dataframe[SEVERITY_COLUMN].astype("string").str.strip().str.title()

    recognised_mask = severity.isin(
        [
            "Observation",
            "Minor",
            "Major",
        ]
    )

    return severity.where(
        recognised_mask,
        "Unspecified",
    )


def _generate_trend_table(
    dataframe: pd.DataFrame,
    *,
    date_column: str,
    period_frequency: str,
) -> pd.DataFrame:
    """Generate severity counts grouped by a time period."""

    working_dataframe = dataframe[
        [
            date_column,
            SEVERITY_COLUMN,
        ]
    ].copy()

    working_dataframe[date_column] = pd.to_datetime(
        working_dataframe[date_column],
        errors="coerce",
    )

    working_dataframe = working_dataframe.dropna(subset=[date_column])

    if working_dataframe.empty:
        return pd.DataFrame(
            columns=[
                "period",
                *SEVERITY_CATEGORIES,
                "total",
            ]
        )

    working_dataframe["severity_group"] = _prepare_severity_series(working_dataframe)

    working_dataframe["period"] = (
        working_dataframe[date_column].dt.to_period(period_frequency).astype(str)
    )

    trend_table = (
        working_dataframe.groupby(
            [
                "period",
                "severity_group",
            ],
            observed=True,
        )
        .size()
        .unstack(
            fill_value=0,
        )
        .reindex(
            columns=SEVERITY_CATEGORIES,
            fill_value=0,
        )
        .reset_index()
        .sort_values("period")
        .reset_index(drop=True)
    )

    trend_table.columns.name = None

    trend_table["total"] = trend_table[SEVERITY_CATEGORIES].sum(axis=1)

    for column in [
        *SEVERITY_CATEGORIES,
        "total",
    ]:
        trend_table[column] = trend_table[column].astype(int)

    return trend_table


def _calculate_latest_change(
    trend_table: pd.DataFrame,
    value_column: str,
) -> tuple[int | None, float | None]:
    """Compare the latest period with the preceding period."""

    if len(trend_table) < 2:
        return None, None

    previous_value = int(trend_table.iloc[-2][value_column])

    latest_value = int(trend_table.iloc[-1][value_column])

    absolute_change = latest_value - previous_value

    if previous_value == 0:
        percentage_change = 0.0 if latest_value == 0 else None
    else:
        percentage_change = round(
            absolute_change / previous_value * 100,
            2,
        )

    return (
        absolute_change,
        percentage_change,
    )


def generate_severity_analysis(
    dataframe: pd.DataFrame,
    *,
    date_column: str = DEFAULT_DATE_COLUMN,
) -> SeverityAnalysis:
    """
    Generate current and time-based severity analytics.

    The date column is configurable. The current spreadsheet uses
    response_due_date, but a future audit_finding_date column should
    be preferred for genuine finding-occurrence trends.
    """

    validate_required_columns(
        dataframe,
        {
            SEVERITY_COLUMN,
            date_column,
        },
        "severity analysis",
    )

    total_findings = int(len(dataframe))

    severity_series = _prepare_severity_series(dataframe)

    observation_count = int(severity_series.eq("Observation").sum())

    minor_count = int(severity_series.eq("Minor").sum())

    major_count = int(severity_series.eq("Major").sum())

    unspecified_count = int(severity_series.eq("Unspecified").sum())

    pareto_dataframe = dataframe.copy()

    pareto_dataframe[SEVERITY_COLUMN] = severity_series

    pareto_result = generate_pareto(
        pareto_dataframe,
        SEVERITY_COLUMN,
        include_missing=True,
        missing_label="Unspecified",
    )

    monthly_trend = _generate_trend_table(
        dataframe,
        date_column=date_column,
        period_frequency="M",
    )

    quarterly_trend = _generate_trend_table(
        dataframe,
        date_column=date_column,
        period_frequency="Q",
    )

    yearly_trend = _generate_trend_table(
        dataframe,
        date_column=date_column,
        period_frequency="Y",
    )

    (
        latest_month_total_change,
        latest_month_total_change_percentage,
    ) = _calculate_latest_change(
        monthly_trend,
        "total",
    )

    (
        latest_month_major_change,
        latest_month_major_change_percentage,
    ) = _calculate_latest_change(
        monthly_trend,
        "Major",
    )

    return SeverityAnalysis(
        date_column=date_column,
        total_findings=total_findings,
        observation_count=observation_count,
        minor_count=minor_count,
        major_count=major_count,
        unspecified_count=unspecified_count,
        observation_percentage=(
            calculate_percentage(
                observation_count,
                total_findings,
            )
        ),
        minor_percentage=(
            calculate_percentage(
                minor_count,
                total_findings,
            )
        ),
        major_percentage=(
            calculate_percentage(
                major_count,
                total_findings,
            )
        ),
        unspecified_percentage=(
            calculate_percentage(
                unspecified_count,
                total_findings,
            )
        ),
        pareto=pareto_result,
        monthly_trend=monthly_trend,
        quarterly_trend=quarterly_trend,
        yearly_trend=yearly_trend,
        latest_month_total_change=(latest_month_total_change),
        latest_month_total_change_percentage=(latest_month_total_change_percentage),
        latest_month_major_change=(latest_month_major_change),
        latest_month_major_change_percentage=(latest_month_major_change_percentage),
    )
