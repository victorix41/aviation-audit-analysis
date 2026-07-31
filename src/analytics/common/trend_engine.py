"""Shared trend-generation utilities for analytics engines."""

import pandas as pd

from src.analytics.common.text_standardiser import (
    DEFAULT_UNSPECIFIED_LABEL,
    standardise_text_series,
)


VALID_PERIOD_FREQUENCIES = {
    "M",
    "Q",
    "Y",
}


def create_empty_long_trend_table(
    category_output_column: str,
) -> pd.DataFrame:
    """
    Create an empty long-format trend table.

    Args:
        category_output_column:
            Name of the category column in the returned table.

    Returns:
        Empty DataFrame with the standard long-trend structure.
    """

    cleaned_output_column = (
        str(category_output_column).strip()
    )

    if not cleaned_output_column:
        raise ValueError(
            "category_output_column must not be blank."
        )

    return pd.DataFrame(
        columns=[
            "period",
            cleaned_output_column,
            "frequency",
            "period_total",
            "percentage",
        ]
    )


def create_empty_wide_trend_table() -> pd.DataFrame:
    """
    Create an empty wide-format trend table.

    Returns:
        Empty DataFrame containing period and total columns.
    """

    return pd.DataFrame(
        columns=[
            "period",
            "total",
        ]
    )


def generate_long_trend_table(
    dataframe: pd.DataFrame,
    *,
    category_column: str,
    category_output_column: str,
    date_column: str,
    period_frequency: str,
    unspecified_label: str = DEFAULT_UNSPECIFIED_LABEL,
    standardise_categories: bool = True,
) -> pd.DataFrame:
    """
    Generate category frequencies by month, quarter or year.

    The returned DataFrame uses long format:

    - period
    - category
    - frequency
    - period_total
    - percentage

    Args:
        dataframe:
            Source DataFrame.

        category_column:
            Category column in the source DataFrame.

        category_output_column:
            Category column name in the returned trend table.

        date_column:
            Date column used for period grouping.

        period_frequency:
            Pandas period frequency. Supported values are M, Q and Y.

        unspecified_label:
            Label used for missing or blank categories.

        standardise_categories:
            Whether category text should be cleaned using the shared
            text-standardisation utility.

    Returns:
        Long-format trend DataFrame.

    Raises:
        TypeError:
            If dataframe is not a pandas DataFrame.

        KeyError:
            If a required source column is missing.

        ValueError:
            If a column name is blank or the period frequency is not
            supported.
    """

    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError(
            "dataframe must be a pandas DataFrame."
        )

    cleaned_category_column = (
        str(category_column).strip()
    )

    cleaned_output_column = (
        str(category_output_column).strip()
    )

    cleaned_date_column = (
        str(date_column).strip()
    )

    cleaned_frequency = (
        str(period_frequency).strip().upper()
    )

    if not cleaned_category_column:
        raise ValueError(
            "category_column must not be blank."
        )

    if not cleaned_output_column:
        raise ValueError(
            "category_output_column must not be blank."
        )

    if not cleaned_date_column:
        raise ValueError(
            "date_column must not be blank."
        )

    if cleaned_frequency not in VALID_PERIOD_FREQUENCIES:
        raise ValueError(
            "period_frequency must be one of: M, Q, Y."
        )

    required_columns = {
        cleaned_category_column,
        cleaned_date_column,
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
            "Required trend column(s) missing: "
            f"{missing_text}"
        )

    working_dataframe = dataframe[
        [
            cleaned_date_column,
            cleaned_category_column,
        ]
    ].copy()

    working_dataframe[
        cleaned_date_column
    ] = pd.to_datetime(
        working_dataframe[
            cleaned_date_column
        ],
        errors="coerce",
    )

    working_dataframe = (
        working_dataframe.dropna(
            subset=[
                cleaned_date_column,
            ]
        )
    )

    if working_dataframe.empty:
        return create_empty_long_trend_table(
            cleaned_output_column
        )

    if standardise_categories:
        working_dataframe[
            cleaned_category_column
        ] = standardise_text_series(
            working_dataframe[
                cleaned_category_column
            ],
            unspecified_label=(
                unspecified_label
            ),
        )

    working_dataframe["period"] = (
        working_dataframe[
            cleaned_date_column
        ]
        .dt.to_period(
            cleaned_frequency
        )
        .astype(str)
    )

    trend_table = (
        working_dataframe
        .groupby(
            [
                "period",
                cleaned_category_column,
            ],
            observed=True,
            dropna=False,
        )
        .size()
        .reset_index(
            name="frequency"
        )
        .rename(
            columns={
                cleaned_category_column:
                    cleaned_output_column,
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
        trend_table[
            "frequency"
        ].astype(int)
    )

    return (
        trend_table
        .sort_values(
            by=[
                "period",
                "frequency",
                cleaned_output_column,
            ],
            ascending=[
                True,
                False,
                True,
            ],
        )
        .reset_index(
            drop=True
        )
    )


def generate_wide_trend_table(
    long_trend_table: pd.DataFrame,
    *,
    category_column: str,
) -> pd.DataFrame:
    """
    Convert a long-format trend table into wide format.

    Args:
        long_trend_table:
            Long-format trend table generated by
            ``generate_long_trend_table``.

        category_column:
            Category column in the long-format table.

    Returns:
        Wide-format table containing:

        - one row per period;
        - one column per category;
        - a total column.

    Raises:
        TypeError:
            If long_trend_table is not a pandas DataFrame.

        KeyError:
            If a required long-table column is missing.

        ValueError:
            If category_column is blank.
    """

    if not isinstance(
        long_trend_table,
        pd.DataFrame,
    ):
        raise TypeError(
            "long_trend_table must be a pandas DataFrame."
        )

    cleaned_category_column = (
        str(category_column).strip()
    )

    if not cleaned_category_column:
        raise ValueError(
            "category_column must not be blank."
        )

    if long_trend_table.empty:
        return create_empty_wide_trend_table()

    required_columns = {
        "period",
        cleaned_category_column,
        "frequency",
    }

    missing_columns = (
        required_columns
        - set(long_trend_table.columns)
    )

    if missing_columns:
        missing_text = ", ".join(
            sorted(missing_columns)
        )

        raise KeyError(
            "Required wide-trend column(s) missing: "
            f"{missing_text}"
        )

    wide_table = (
        long_trend_table
        .pivot_table(
            index="period",
            columns=cleaned_category_column,
            values="frequency",
            aggfunc="sum",
            fill_value=0,
        )
        .reset_index()
    )

    wide_table.columns.name = None

    category_columns = [
        column
        for column in wide_table.columns
        if column != "period"
    ]

    for column in category_columns:
        wide_table[column] = (
            wide_table[
                column
            ].astype(int)
        )

    wide_table["total"] = (
        wide_table[
            category_columns
        ]
        .sum(axis=1)
        .astype(int)
    )

    return (
        wide_table
        .sort_values("period")
        .reset_index(
            drop=True
        )
    )