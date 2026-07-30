"""Analytics engine for aviation MRO human-factor data."""

import pandas as pd

from src.analytics.pareto_engine import generate_pareto
from src.models.human_factor_analysis import HumanFactorAnalysis


HUMAN_FACTOR_COLUMN = "human_factor"
DEFAULT_DATE_COLUMN = "response_due_date"
UNSPECIFIED_LABEL = "Unspecified"


def _standardise_human_factor_series(
    series: pd.Series,
) -> pd.Series:
    """
    Clean and standardise human-factor category values.

    The function:
    - converts values to pandas string format,
    - removes leading and trailing spaces,
    - replaces missing and blank values with ``Unspecified``,
    - standardises capitalisation.
    """

    cleaned_series = (
        series.astype("string")
        .str.strip()
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


def _empty_trend_table() -> pd.DataFrame:
    """Return an empty trend table with the expected structure."""

    return pd.DataFrame(
        columns=[
            "period",
            "human_factor",
            "frequency",
            "period_total",
            "percentage",
        ]
    )


def _generate_trend_table(
    dataframe: pd.DataFrame,
    *,
    date_column: str,
    period_frequency: str,
) -> pd.DataFrame:
    """
    Generate human-factor frequencies by period.

    The returned table uses long format so that it can later be
    consumed directly by Plotly, Streamlit and reporting modules.
    """

    working_dataframe = dataframe[
        [
            date_column,
            HUMAN_FACTOR_COLUMN,
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
        return _empty_trend_table()

    working_dataframe[HUMAN_FACTOR_COLUMN] = (
        _standardise_human_factor_series(
            working_dataframe[HUMAN_FACTOR_COLUMN]
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
                HUMAN_FACTOR_COLUMN,
            ],
            observed=True,
        )
        .size()
        .reset_index(name="frequency")
        .rename(
            columns={
                HUMAN_FACTOR_COLUMN: "human_factor",
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

    trend_table = (
        trend_table
        .sort_values(
            by=[
                "period",
                "frequency",
                "human_factor",
            ],
            ascending=[
                True,
                False,
                True,
            ],
        )
        .reset_index(drop=True)
    )

    return trend_table


def _calculate_latest_period_total_change(
    trend_table: pd.DataFrame,
) -> tuple[int | None, float | None]:
    """
    Compare totals for the latest two periods.

    Returns:
        A tuple containing:

        - absolute change;
        - percentage change.

        When fewer than two periods are available, both values are
        returned as ``None``.
    """

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


def generate_human_factor_analysis(
    dataframe: pd.DataFrame,
    *,
    date_column: str = DEFAULT_DATE_COLUMN,
) -> HumanFactorAnalysis:
    """
    Generate current and time-based human-factor analytics.

    Args:
        dataframe:
            Cleaned audit dataframe.

        date_column:
            Column used for monthly, quarterly and yearly grouping.

            The current audit register uses ``response_due_date``.
            A future ``audit_finding_date`` column should be used for
            genuine finding-occurrence trend analysis.

    Returns:
        A structured ``HumanFactorAnalysis`` result.

    Raises:
        KeyError:
            If the human-factor column or selected date column is
            missing.
    """

    required_columns = {
        HUMAN_FACTOR_COLUMN,
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
            "Required human-factor analysis column(s) missing: "
            f"{missing_text}"
        )

    total_findings = int(
        len(dataframe)
    )

    human_factor_series = (
        _standardise_human_factor_series(
            dataframe[HUMAN_FACTOR_COLUMN]
        )
    )

    unspecified_findings = int(
        human_factor_series
        .eq(UNSPECIFIED_LABEL)
        .sum()
    )

    specified_findings = (
        total_findings
        - unspecified_findings
    )

    specified_series = human_factor_series[
        human_factor_series.ne(
            UNSPECIFIED_LABEL
        )
    ]

    unique_human_factors = int(
        specified_series.nunique()
    )

    pareto_dataframe = dataframe.copy()

    pareto_dataframe[
        HUMAN_FACTOR_COLUMN
    ] = human_factor_series

    pareto_result = generate_pareto(
        pareto_dataframe,
        HUMAN_FACTOR_COLUMN,
        include_missing=True,
        missing_label=UNSPECIFIED_LABEL,
    )

    # Read top-category information directly from the Pareto table.
    # This avoids depending on a top_frequency property that is not
    # present in the existing ParetoResult model.
    if pareto_result.table.empty:
        top_factor = None
        top_factor_frequency = 0
        top_factor_percentage = 0.0
    else:
        top_row = pareto_result.table.iloc[0]

        top_factor = str(
            top_row["category"]
        )

        top_factor_frequency = int(
            top_row["frequency"]
        )

        top_factor_percentage = float(
            top_row["percentage"]
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

    return HumanFactorAnalysis(
        date_column=date_column,
        total_findings=total_findings,
        specified_findings=specified_findings,
        unspecified_findings=unspecified_findings,
        unique_human_factors=unique_human_factors,

        top_factor=top_factor,
        top_factor_frequency=top_factor_frequency,
        top_factor_percentage=top_factor_percentage,

        pareto=pareto_result,

        monthly_trend=monthly_trend,
        quarterly_trend=quarterly_trend,
        yearly_trend=yearly_trend,

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