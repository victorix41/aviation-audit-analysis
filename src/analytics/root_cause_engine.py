"""Analytics engine for aviation MRO root-cause data."""

import pandas as pd

from src.analytics.common.text_standardiser import (
    standardise_text_series,
)
from src.analytics.pareto_engine import generate_pareto
from src.models.root_cause_analysis import RootCauseAnalysis


ROOT_CAUSE_COLUMN = "root_cause"
DEFAULT_DATE_COLUMN = "response_due_date"
UNSPECIFIED_LABEL = "Unspecified"


def _empty_long_trend_table() -> pd.DataFrame:
    """Return an empty long-format trend table."""

    return pd.DataFrame(
        columns=[
            "period",
            "root_cause",
            "frequency",
            "period_total",
            "percentage",
        ]
    )


def _empty_wide_trend_table() -> pd.DataFrame:
    """Return an empty wide-format trend table."""

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
    """Generate a long-format root-cause trend table."""

    working_dataframe = dataframe[
        [
            date_column,
            ROOT_CAUSE_COLUMN,
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

    working_dataframe[ROOT_CAUSE_COLUMN] = (
        standardise_text_series(
            working_dataframe[
                ROOT_CAUSE_COLUMN
            ],
            unspecified_label=UNSPECIFIED_LABEL,
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
                ROOT_CAUSE_COLUMN,
            ],
            observed=True,
        )
        .size()
        .reset_index(name="frequency")
        .rename(
            columns={
                ROOT_CAUSE_COLUMN: "root_cause",
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
                "root_cause",
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
            columns="root_cause",
            values="frequency",
            aggfunc="sum",
            fill_value=0,
        )
        .reset_index()
    )

    wide_table.columns.name = None

    root_cause_columns = [
        column
        for column in wide_table.columns
        if column != "period"
    ]

    for column in root_cause_columns:
        wide_table[column] = (
            wide_table[column].astype(int)
        )

    wide_table["total"] = (
        wide_table[root_cause_columns]
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


def generate_root_cause_analysis(
    dataframe: pd.DataFrame,
    *,
    date_column: str = DEFAULT_DATE_COLUMN,
) -> RootCauseAnalysis:
    """
    Generate current and time-based root-cause analytics.

    The selected date column is used only for time grouping.
    The current dataset uses ``response_due_date``.
    """

    required_columns = {
        ROOT_CAUSE_COLUMN,
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
            "Required root-cause analysis column(s) missing: "
            f"{missing_text}"
        )

    total_findings = int(
        len(dataframe)
    )

    root_cause_series = (
        standardise_text_series(
            dataframe[
                ROOT_CAUSE_COLUMN
            ],
            unspecified_label=UNSPECIFIED_LABEL,
        )
    )

    unspecified_findings = int(
        root_cause_series
        .eq(UNSPECIFIED_LABEL)
        .sum()
    )

    specified_findings = (
        total_findings
        - unspecified_findings
    )

    specified_series = root_cause_series[
        root_cause_series.ne(
            UNSPECIFIED_LABEL
        )
    ]

    unique_root_causes = int(
        specified_series.nunique()
    )

    pareto_dataframe = dataframe.copy()

    pareto_dataframe[
        ROOT_CAUSE_COLUMN
    ] = root_cause_series

    pareto_result = generate_pareto(
        pareto_dataframe,
        ROOT_CAUSE_COLUMN,
        include_missing=True,
        missing_label=UNSPECIFIED_LABEL,
    )

    if pareto_result.table.empty:
        top_root_cause = None
        top_root_cause_frequency = 0
        top_root_cause_percentage = 0.0
    else:
        top_row = pareto_result.table.iloc[0]

        top_root_cause = str(
            top_row["category"]
        )

        top_root_cause_frequency = int(
            top_row["frequency"]
        )

        top_root_cause_percentage = float(
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

    return RootCauseAnalysis(
        date_column=date_column,

        total_findings=total_findings,
        specified_findings=specified_findings,
        unspecified_findings=unspecified_findings,
        unique_root_causes=unique_root_causes,

        top_root_cause=top_root_cause,
        top_root_cause_frequency=(
            top_root_cause_frequency
        ),
        top_root_cause_percentage=(
            top_root_cause_percentage
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