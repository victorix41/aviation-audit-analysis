from datetime import date
from typing import Final

import pandas as pd

from src.models.audit_summary import AuditSummary
from src.analytics.common.column_validation import (
    validate_required_columns,
)



from src.analytics.common.math_utils import (
    calculate_percentage,
)

SEVERITY_COLUMN: Final = "severity_level"
DUE_DATE_COLUMN: Final = "response_due_date"


def generate_audit_summary(
    dataframe: pd.DataFrame,
    *,
    as_of_date: date | None = None,
) -> AuditSummary:
    """
    Calculate executive KPIs from cleaned audit findings.

    A response due date earlier than the as-of date is classified as
    past due. This does not prove that the finding remains open because
    the current dataset has no status or closure-date field.
    """

    validate_required_columns(
        dataframe,
        {
            SEVERITY_COLUMN,
            DUE_DATE_COLUMN,
        },
        "KPI",
    )

    effective_date = as_of_date or date.today()
    total_findings = int(len(dataframe))

    severity_series = (
        dataframe[SEVERITY_COLUMN]
        .astype("string")
        .str.strip()
        .str.title()
    )

    observation_count = int(
        severity_series.eq("Observation").sum()
    )

    minor_count = int(
        severity_series.eq("Minor").sum()
    )

    major_count = int(
        severity_series.eq("Major").sum()
    )

    recognised_severity_count = (
        observation_count
        + minor_count
        + major_count
    )

    unspecified_severity_count = (
        total_findings - recognised_severity_count
    )

    due_dates = pd.to_datetime(
        dataframe[DUE_DATE_COLUMN],
        errors="coerce",
    )

    missing_due_date_count = int(
        due_dates.isna().sum()
    )

    effective_timestamp = pd.Timestamp(
        effective_date
    )

    next_30_days_timestamp = (
        effective_timestamp
        + pd.Timedelta(days=30)
    )

    valid_due_dates = due_dates.dropna()

    past_due_response_count = int(
        (valid_due_dates < effective_timestamp).sum()
    )

    due_within_30_days_count = int(
        (
            (valid_due_dates >= effective_timestamp)
            & (
                valid_due_dates
                <= next_30_days_timestamp
            )
        ).sum()
    )

    future_due_count = int(
        (
            valid_due_dates
            > next_30_days_timestamp
        ).sum()
    )

    if valid_due_dates.empty:
        earliest_due_date = None
        latest_due_date = None
    else:
        earliest_due_date = (
            valid_due_dates.min().date()
        )

        latest_due_date = (
            valid_due_dates.max().date()
        )

    return AuditSummary(
        as_of_date=effective_date,
        total_findings=total_findings,

        observation_count=observation_count,
        minor_count=minor_count,
        major_count=major_count,
        unspecified_severity_count=(
            unspecified_severity_count
        ),

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
        unspecified_severity_percentage=(
            calculate_percentage(
                unspecified_severity_count,
                total_findings,
            )
        ),

        past_due_response_count=(
            past_due_response_count
        ),
        due_within_30_days_count=(
            due_within_30_days_count
        ),
        future_due_count=future_due_count,
        missing_due_date_count=(
            missing_due_date_count
        ),

        earliest_due_date=earliest_due_date,
        latest_due_date=latest_due_date,
    )