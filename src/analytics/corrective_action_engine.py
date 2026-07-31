"""Analytics engine for aviation MRO corrective-action data."""

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
from src.models.corrective_action_analysis import (
    CorrectiveActionAnalysis,
)


CORRECTIVE_ACTION_COLUMN = "corrective_action"
DEFAULT_DATE_COLUMN = "response_due_date"
UNSPECIFIED_LABEL = "Unspecified"


def generate_corrective_action_analysis(
    dataframe: pd.DataFrame,
    *,
    date_column: str = DEFAULT_DATE_COLUMN,
) -> CorrectiveActionAnalysis:
    """
    Generate current and time-based corrective-action analytics.

    The current dataset uses ``response_due_date`` for time grouping.
    A future ``audit_finding_date`` column should be preferred for
    true finding-occurrence trends.
    """

    validate_required_columns(
        dataframe,
        {
            CORRECTIVE_ACTION_COLUMN,
            date_column,
        },
        "corrective-action analysis",
    )

    total_findings = int(
        len(dataframe)
    )

    corrective_action_series = (
        standardise_text_series(
            dataframe[
                CORRECTIVE_ACTION_COLUMN
            ],
            unspecified_label=UNSPECIFIED_LABEL,
        )
    )

    unspecified_findings = int(
        corrective_action_series
        .eq(UNSPECIFIED_LABEL)
        .sum()
    )

    specified_findings = (
        total_findings
        - unspecified_findings
    )

    specified_series = (
        corrective_action_series[
            corrective_action_series.ne(
                UNSPECIFIED_LABEL
            )
        ]
    )

    unique_corrective_actions = int(
        specified_series.nunique()
    )

    pareto_dataframe = dataframe.copy()

    pareto_dataframe[
        CORRECTIVE_ACTION_COLUMN
    ] = corrective_action_series

    pareto_result = generate_pareto(
        pareto_dataframe,
        CORRECTIVE_ACTION_COLUMN,
        include_missing=True,
        missing_label=UNSPECIFIED_LABEL,
    )

    if pareto_result.table.empty:
        top_corrective_action = None
        top_corrective_action_frequency = 0
        top_corrective_action_percentage = 0.0
    else:
        top_row = pareto_result.table.iloc[0]

        top_corrective_action = str(
            top_row["category"]
        )

        top_corrective_action_frequency = int(
            top_row["frequency"]
        )

        top_corrective_action_percentage = float(
            top_row["percentage"]
        )

    monthly_trend = generate_long_trend_table(
        dataframe,
        category_column=CORRECTIVE_ACTION_COLUMN,
        category_output_column="corrective_action",
        date_column=date_column,
        period_frequency="M",
        unspecified_label=UNSPECIFIED_LABEL,
    )

    quarterly_trend = generate_long_trend_table(
        dataframe,
        category_column=CORRECTIVE_ACTION_COLUMN,
        category_output_column="corrective_action",
        date_column=date_column,
        period_frequency="Q",
        unspecified_label=UNSPECIFIED_LABEL,
    )

    yearly_trend = generate_long_trend_table(
        dataframe,
        category_column=CORRECTIVE_ACTION_COLUMN,
        category_output_column="corrective_action",
        date_column=date_column,
        period_frequency="Y",
        unspecified_label=UNSPECIFIED_LABEL,
    )

    monthly_wide_trend = (
        generate_wide_trend_table(
            monthly_trend,
            category_column="corrective_action",
        )
    )

    quarterly_wide_trend = (
        generate_wide_trend_table(
            quarterly_trend,
            category_column="corrective_action",
        )
    )

    yearly_wide_trend = (
        generate_wide_trend_table(
            yearly_trend,
            category_column="corrective_action",
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

    return CorrectiveActionAnalysis(
        date_column=date_column,

        total_findings=total_findings,
        specified_findings=specified_findings,
        unspecified_findings=unspecified_findings,
        unique_corrective_actions=(
            unique_corrective_actions
        ),

        top_corrective_action=(
            top_corrective_action
        ),
        top_corrective_action_frequency=(
            top_corrective_action_frequency
        ),
        top_corrective_action_percentage=(
            top_corrective_action_percentage
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