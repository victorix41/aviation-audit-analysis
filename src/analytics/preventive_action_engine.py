"""Analytics engine for aviation MRO preventive-action data."""

import pandas as pd

from src.analytics.pareto_engine import generate_pareto
from src.models.preventive_action_analysis import (
    PreventiveActionAnalysis,
)


PREVENTIVE_ACTION_COLUMN = "preventive_action"
DEFAULT_DATE_COLUMN = "response_due_date"
UNSPECIFIED_LABEL = "Unspecified"


def _standardise_preventive_action_series(
    series: pd.Series,
) -> pd.Series:
    """
    Clean and standardise preventive-action text.

    Processing:
    - converts values to pandas string format;
    - removes leading and trailing spaces;
    - reduces repeated internal whitespace;
    - replaces blank and missing values;
    - applies sentence-style capitalisation.
    """

    cleaned_series = (
        series.astype("string")
        .str.strip()
        .str.replace(
            r"\s+",
            " ",
            regex=True,
        )
    )

    missing_mask = (
        cleaned_series.isna()
        | cleaned_series.eq("")
    )

    cleaned_series = cleaned_series.mask(
        missing_mask,
        UNSPECIFIED_LABEL,
    )

    cleaned_series = (
        cleaned_series
        .str.lower()
        .str.capitalize()
    )

    return cleaned_series


def _empty_long_trend_table() -> pd.DataFrame:
    """Return an empty long-format preventive-action trend table."""

    return pd.DataFrame(
        columns=[
            "period",
            "preventive_action",
            "frequency",
            "period_total",
            "percentage",
        ]
    )


def _empty_wide_trend_table() -> pd.DataFrame:
    """Return an empty wide-format preventive-action trend table."""

    return pd.DataFrame(
        columns=[
            "period",
            "total",
        ]
    )


def _generate_long_trend_table(
    dataframe: pd.DataFrame,
    *,
    date_column: str,
    period_frequency: str,
) -> pd.DataFrame:
    """Generate preventive-action frequencies by time period."""

    working_dataframe = dataframe[
        [
            date_column,
            PREVENTIVE_ACTION_COLUMN,
        ]
    ].copy()

    working_dataframe[date_column] = pd.to_datetime(
        working_dataframe[date_column],
        errors="coerce",
    )

    working_dataframe = working_dataframe.dropna(
        subset=[date_column]
    )

    if working_dataframe.empty:
        return _empty_long_trend_table()

    working_dataframe[PREVENTIVE_ACTION_COLUMN] = (
        _standardise_preventive_action_series(
            working_dataframe[
                PREVENTIVE_ACTION_COLUMN
            ]
        )
    )

    working_dataframe["period"] = (
        working_dataframe[date_column]
        .dt.to_period(period_frequency)
        .astype(str)
    )

    trend_table = (
        working_dataframe
        .groupby(
            [
                "period",
                PREVENTIVE_ACTION_COLUMN,
            ],
            observed=True,
        )
        .size()
        .reset_index(name="frequency")
        .rename(
            columns={
                PREVENTIVE_ACTION_COLUMN:
                    "preventive_action",
            }
        )
    )

    trend_table["period_total"] = (
        trend_table
        .groupby(
            "period",
            observed=True,
        )["frequency"]
        .transform("sum")
        .astype(int)
    )

    trend_table["percentage"] = (
        trend_table["frequency"]
        / trend_table["period_total"]
        * 100
    ).round(2)

    trend_table["frequency"] = (
        trend_table["frequency"].astype(int)
    )

    return (
        trend_table
        .sort_values(
            by=[
                "period",
                "frequency",
                "preventive_action",
            ],
            ascending=[
                True,
                False,
                True,
            ],
        )
        .reset_index(drop=True)
    )


def _generate_wide_trend_table(
    long_trend_table: pd.DataFrame,
) -> pd.DataFrame:
    """Convert a long-format trend table into wide format."""

    if long_trend_table.empty:
        return _empty_wide_trend_table()

    wide_table = (
        long_trend_table
        .pivot_table(
            index="period",
            columns="preventive_action",
            values="frequency",
            aggfunc="sum",
            fill_value=0,
        )
        .reset_index()
    )

    wide_table.columns.name = None

    action_columns = [
        column
        for column in wide_table.columns
        if column != "period"
    ]

    for column in action_columns:
        wide_table[column] = (
            wide_table[column].astype(int)
        )

    wide_table["total"] = (
        wide_table[action_columns]
        .sum(axis=1)
        .astype(int)
    )

    return (
        wide_table
        .sort_values("period")
        .reset_index(drop=True)
    )


def _calculate_latest_period_total_change(
    trend_table: pd.DataFrame,
) -> tuple[int | None, float | None]:
    """Compare totals for the latest two periods."""

    if trend_table.empty:
        return None, None

    period_totals = (
        trend_table[
            [
                "period",
                "period_total",
            ]
        ]
        .drop_duplicates(
            subset=["period"]
        )
        .sort_values("period")
        .reset_index(drop=True)
    )

    if len(period_totals) < 2:
        return None, None

    previous_total = int(
        period_totals.iloc[-2]["period_total"]
    )

    latest_total = int(
        period_totals.iloc[-1]["period_total"]
    )

    absolute_change = (
        latest_total - previous_total
    )

    if previous_total == 0:
        percentage_change = (
            0.0
            if latest_total == 0
            else None
        )
    else:
        percentage_change = round(
            absolute_change
            / previous_total
            * 100,
            2,
        )

    return (
        absolute_change,
        percentage_change,
    )


def generate_preventive_action_analysis(
    dataframe: pd.DataFrame,
    *,
    date_column: str = DEFAULT_DATE_COLUMN,
) -> PreventiveActionAnalysis:
    """
    Generate current and time-based preventive-action analytics.

    The current dataset uses ``response_due_date`` for time grouping.
    This represents the preventive-action due-date workload, rather
    than the date on which the original finding occurred.
    """

    required_columns = {
        PREVENTIVE_ACTION_COLUMN,
        date_column,
    }

    missing_columns = (
        required_columns
        - set(dataframe.columns)
    )

    if missing_columns:
        missing_text = ", ".join(
            sorted(missing_columns)
        )

        raise KeyError(
            "Required preventive-action analysis "
            f"column(s) missing: {missing_text}"
        )

    total_findings = int(
        len(dataframe)
    )

    preventive_action_series = (
        _standardise_preventive_action_series(
            dataframe[
                PREVENTIVE_ACTION_COLUMN
            ]
        )
    )

    unspecified_findings = int(
        preventive_action_series
        .eq(UNSPECIFIED_LABEL)
        .sum()
    )

    specified_findings = (
        total_findings
        - unspecified_findings
    )

    specified_series = (
        preventive_action_series[
            preventive_action_series.ne(
                UNSPECIFIED_LABEL
            )
        ]
    )

    unique_preventive_actions = int(
        specified_series.nunique()
    )

    pareto_dataframe = dataframe.copy()

    pareto_dataframe[
        PREVENTIVE_ACTION_COLUMN
    ] = preventive_action_series

    pareto_result = generate_pareto(
        pareto_dataframe,
        PREVENTIVE_ACTION_COLUMN,
        include_missing=True,
        missing_label=UNSPECIFIED_LABEL,
    )

    if pareto_result.table.empty:
        top_preventive_action = None
        top_preventive_action_frequency = 0
        top_preventive_action_percentage = 0.0
    else:
        top_row = pareto_result.table.iloc[0]

        top_preventive_action = str(
            top_row["category"]
        )

        top_preventive_action_frequency = int(
            top_row["frequency"]
        )

        top_preventive_action_percentage = float(
            top_row["percentage"]
        )

    monthly_trend = _generate_long_trend_table(
        dataframe,
        date_column=date_column,
        period_frequency="M",
    )

    quarterly_trend = _generate_long_trend_table(
        dataframe,
        date_column=date_column,
        period_frequency="Q",
    )

    yearly_trend = _generate_long_trend_table(
        dataframe,
        date_column=date_column,
        period_frequency="Y",
    )

    monthly_wide_trend = (
        _generate_wide_trend_table(
            monthly_trend
        )
    )

    quarterly_wide_trend = (
        _generate_wide_trend_table(
            quarterly_trend
        )
    )

    yearly_wide_trend = (
        _generate_wide_trend_table(
            yearly_trend
        )
    )

    (
        latest_month_total_change,
        latest_month_total_change_percentage,
    ) = _calculate_latest_period_total_change(
        monthly_trend
    )

    (
        latest_quarter_total_change,
        latest_quarter_total_change_percentage,
    ) = _calculate_latest_period_total_change(
        quarterly_trend
    )

    (
        latest_year_total_change,
        latest_year_total_change_percentage,
    ) = _calculate_latest_period_total_change(
        yearly_trend
    )

    return PreventiveActionAnalysis(
        date_column=date_column,

        total_findings=total_findings,
        specified_findings=specified_findings,
        unspecified_findings=unspecified_findings,
        unique_preventive_actions=(
            unique_preventive_actions
        ),

        top_preventive_action=(
            top_preventive_action
        ),
        top_preventive_action_frequency=(
            top_preventive_action_frequency
        ),
        top_preventive_action_percentage=(
            top_preventive_action_percentage
        ),

        pareto=pareto_result,

        monthly_trend=monthly_trend,
        quarterly_trend=quarterly_trend,
        yearly_trend=yearly_trend,

        monthly_wide_trend=monthly_wide_trend,
        quarterly_wide_trend=quarterly_wide_trend,
        yearly_wide_trend=yearly_wide_trend,

        latest_month_total_change=(
            latest_month_total_change
        ),
        latest_month_total_change_percentage=(
            latest_month_total_change_percentage
        ),

        latest_quarter_total_change=(
            latest_quarter_total_change
        ),
        latest_quarter_total_change_percentage=(
            latest_quarter_total_change_percentage
        ),

        latest_year_total_change=(
            latest_year_total_change
        ),
        latest_year_total_change_percentage=(
            latest_year_total_change_percentage
        ),
    )