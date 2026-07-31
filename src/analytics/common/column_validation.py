"""Shared required-column validation utilities."""

from collections.abc import Iterable

import pandas as pd


def validate_required_columns(
    dataframe: pd.DataFrame,
    required_columns: Iterable[str],
    context: str,
) -> None:
    """Validate that a DataFrame contains all required columns.

    Args:
        dataframe:
            DataFrame whose columns will be validated.
        required_columns:
            Column names required by the calling component.
        context:
            Description used in the error message, such as
            ``"human-factor analysis"`` or ``"KPI"``.

    Raises:
        TypeError:
            If ``dataframe`` is not a pandas DataFrame.
        ValueError:
            If ``context`` is empty.
        KeyError:
            If one or more required columns are missing.
    """

    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError(
            "dataframe must be a pandas DataFrame."
        )

    cleaned_context = str(context).strip()

    if not cleaned_context:
        raise ValueError(
            "context must not be empty."
        )

    required_column_set = set(required_columns)
    missing_columns = (
        required_column_set
        - set(dataframe.columns)
    )

    if missing_columns:
        missing_text = ", ".join(
            sorted(
                str(column)
                for column in missing_columns
            )
        )

        raise KeyError(
            f"Required {cleaned_context} column(s) missing: "
            f"{missing_text}"
        )
