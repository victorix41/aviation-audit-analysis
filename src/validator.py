from typing import Any

import pandas as pd

from src.config import (
    REQUIRED_COLUMNS,
    VALID_SEVERITY_LEVELS,
)


def validate_required_columns(
    dataframe: pd.DataFrame,
) -> list[str]:
    """Return required columns that are missing."""

    return sorted(
        REQUIRED_COLUMNS - set(dataframe.columns)
    )


def count_blank_values(
    series: pd.Series,
) -> int:
    """Count missing and empty values."""

    missing_mask = series.isna()

    if (
        pd.api.types.is_string_dtype(series)
        or series.dtype == object
    ):
        blank_mask = (
            series.astype("string")
            .str.strip()
            .eq("")
        )

        return int(
            (missing_mask | blank_mask).sum()
        )

    return int(missing_mask.sum())


def validate_audit_data(
    dataframe: pd.DataFrame,
) -> dict[str, Any]:
    """Run data-quality checks."""

    missing_columns = validate_required_columns(
        dataframe
    )

    if missing_columns:
        return {
            "total_records": len(dataframe),
            "missing_required_columns": missing_columns,
            "validation_passed": False,
        }

    invalid_severity_mask = (
        dataframe["severity_level"].notna()
        & ~dataframe["severity_level"].isin(
            VALID_SEVERITY_LEVELS
        )
    )

    results = {
        "total_records": len(dataframe),
        "missing_required_columns": [],
        "duplicate_reference_numbers": int(
            dataframe["audit_reference_no"]
            .duplicated(keep=False)
            .sum()
        ),
        "missing_reference_numbers": (
            count_blank_values(
                dataframe["audit_reference_no"]
            )
        ),
        "missing_findings": (
            count_blank_values(
                dataframe["finding"]
            )
        ),
        "missing_due_dates": int(
            dataframe["response_due_date"]
            .isna()
            .sum()
        ),
        "missing_root_causes": (
            count_blank_values(
                dataframe["root_cause"]
            )
        ),
        "missing_corrective_actions": (
            count_blank_values(
                dataframe["corrective_action"]
            )
        ),
        "missing_preventive_actions": (
            count_blank_values(
                dataframe["preventive_action"]
            )
        ),
        "invalid_severity_values": int(
            invalid_severity_mask.sum()
        ),
        "invalid_severity_records": (
            dataframe.loc[
                invalid_severity_mask,
                [
                    "audit_reference_no",
                    "severity_level",
                ],
            ]
            .to_dict(orient="records")
        ),
    }

    checks = [
        "duplicate_reference_numbers",
        "missing_reference_numbers",
        "missing_findings",
        "missing_due_dates",
        "missing_root_causes",
        "missing_corrective_actions",
        "missing_preventive_actions",
        "invalid_severity_values",
    ]

    results["validation_passed"] = all(
        results[check] == 0
        for check in checks
    )

    return results