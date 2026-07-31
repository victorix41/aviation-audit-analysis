"""Analytics engine for aviation MRO root-cause data."""

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
from src.models.root_cause_analysis import RootCauseAnalysis


ROOT_CAUSE_COLUMN = "root_cause"
DEFAULT_DATE_COLUMN = "response_due_date"
UNSPECIFIED_LABEL = "Unspecified"


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

    validate_required_columns(
        dataframe,
        {
            ROOT_CAUSE_COLUMN,
            date_column,
        },
        "root-cause analysis",
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

    monthly_trend = generate_long_trend_table(
        dataframe,
        category_column=ROOT_CAUSE_COLUMN,
        category_output_column="root_cause",
        date_column=date_column,
        period_frequency="M",
        unspecified_label=UNSPECIFIED_LABEL,
    )

    quarterly_trend = generate_long_trend_table(
        dataframe,
        category_column=ROOT_CAUSE_COLUMN,
        category_output_column="root_cause",
        date_column=date_column,
        period_frequency="Q",
        unspecified_label=UNSPECIFIED_LABEL,
    )

    yearly_trend = generate_long_trend_table(
        dataframe,
        category_column=ROOT_CAUSE_COLUMN,
        category_output_column="root_cause",
        date_column=date_column,
        period_frequency="Y",
        unspecified_label=UNSPECIFIED_LABEL,
    )

    monthly_wide_trend = (
        generate_wide_trend_table(
            monthly_trend,
            category_column="root_cause",
        )
    )

    quarterly_wide_trend = (
        generate_wide_trend_table(
            quarterly_trend,
            category_column="root_cause",
        )
    )

    yearly_wide_trend = (
        generate_wide_trend_table(
            yearly_trend,
            category_column="root_cause",
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