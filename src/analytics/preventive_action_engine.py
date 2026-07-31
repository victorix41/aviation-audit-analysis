"""Analytics engine for aviation MRO preventive-action data."""

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
    generate_wide_trend_table,
)
from src.analytics.pareto_engine import generate_pareto
from src.models.preventive_action_analysis import (
    PreventiveActionAnalysis,
)


PREVENTIVE_ACTION_COLUMN = "preventive_action"
DEFAULT_DATE_COLUMN = "response_due_date"
UNSPECIFIED_LABEL = "Unspecified"


def generate_preventive_action_analysis(
    dataframe: pd.DataFrame,
    *,
    date_column: str = DEFAULT_DATE_COLUMN,
) -> PreventiveActionAnalysis:
    """
    Generate current and time-based preventive-action analytics.

    The current dataset uses ``response_due_date`` for time grouping.
    This represents the preventive-action due-date workload rather
    than the date on which the original audit finding occurred.
    """

    validate_required_columns(
        dataframe,
        {
            PREVENTIVE_ACTION_COLUMN,
            date_column,
        },
        "preventive-action analysis",
    )

    total_findings = int(
        len(dataframe)
    )

    preventive_action_series = (
        standardise_text_series(
            dataframe[
                PREVENTIVE_ACTION_COLUMN
            ],
            unspecified_label=UNSPECIFIED_LABEL,
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

    monthly_trend = generate_long_trend_table(
        dataframe,
        category_column=PREVENTIVE_ACTION_COLUMN,
        category_output_column="preventive_action",
        date_column=date_column,
        period_frequency="M",
        unspecified_label=UNSPECIFIED_LABEL,
    )

    quarterly_trend = generate_long_trend_table(
        dataframe,
        category_column=PREVENTIVE_ACTION_COLUMN,
        category_output_column="preventive_action",
        date_column=date_column,
        period_frequency="Q",
        unspecified_label=UNSPECIFIED_LABEL,
    )

    yearly_trend = generate_long_trend_table(
        dataframe,
        category_column=PREVENTIVE_ACTION_COLUMN,
        category_output_column="preventive_action",
        date_column=date_column,
        period_frequency="Y",
        unspecified_label=UNSPECIFIED_LABEL,
    )

    monthly_wide_trend = (
        generate_wide_trend_table(
            monthly_trend,
            category_column="preventive_action",
        )
    )

    quarterly_wide_trend = (
        generate_wide_trend_table(
            quarterly_trend,
            category_column="preventive_action",
        )
    )

    yearly_wide_trend = (
        generate_wide_trend_table(
            yearly_trend,
            category_column="preventive_action",
        )
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