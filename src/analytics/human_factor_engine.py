"""Analytics engine for aviation MRO human-factor data."""

import pandas as pd

from src.analytics.common.column_validation import (
    validate_required_columns,
)
from src.analytics.common.period_comparison import (
    calculate_latest_period_total_change,
)
from src.analytics.common.text_standardiser import (
    standardise_text_series,
)
from src.analytics.common.trend_engine import (
    generate_long_trend_table,
)
from src.analytics.pareto_engine import generate_pareto
from src.models.human_factor_analysis import HumanFactorAnalysis

HUMAN_FACTOR_COLUMN = "human_factor"
DEFAULT_DATE_COLUMN = "response_due_date"
UNSPECIFIED_LABEL = "Unspecified"


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

    validate_required_columns(
        dataframe,
        {
            HUMAN_FACTOR_COLUMN,
            date_column,
        },
        "human-factor analysis",
    )

    total_findings = int(
        len(dataframe)
    )

    human_factor_series = (
        standardise_text_series(
            dataframe[
                HUMAN_FACTOR_COLUMN
            ],
            unspecified_label=UNSPECIFIED_LABEL,
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

    monthly_trend = generate_long_trend_table(
        dataframe,
        category_column=HUMAN_FACTOR_COLUMN,
        category_output_column=HUMAN_FACTOR_COLUMN,
        date_column=date_column,
        period_frequency="M",
        unspecified_label=UNSPECIFIED_LABEL,
    )

    quarterly_trend = generate_long_trend_table(
        dataframe,
        category_column=HUMAN_FACTOR_COLUMN,
        category_output_column=HUMAN_FACTOR_COLUMN,
        date_column=date_column,
        period_frequency="Q",
        unspecified_label=UNSPECIFIED_LABEL,
    )

    yearly_trend = generate_long_trend_table(
        dataframe,
        category_column=HUMAN_FACTOR_COLUMN,
        category_output_column=HUMAN_FACTOR_COLUMN,
        date_column=date_column,
        period_frequency="Y",
        unspecified_label=UNSPECIFIED_LABEL,
    )

    (
        latest_month_total_change,
        latest_month_total_change_percentage,
    ) = calculate_latest_period_total_change(
        monthly_trend
    )

    (
        latest_quarter_total_change,
        latest_quarter_total_change_percentage,
    ) = calculate_latest_period_total_change(
        quarterly_trend
    )

    (
        latest_year_total_change,
        latest_year_total_change_percentage,
    ) = calculate_latest_period_total_change(
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