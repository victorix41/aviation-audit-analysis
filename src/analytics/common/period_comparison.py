"""Shared utilities for comparing analytics periods."""

import pandas as pd


def calculate_latest_period_total_change(
    trend_table: pd.DataFrame,
) -> tuple[int | None, float | None]:
    """
    Compare the totals for the latest two periods.

    The trend table must contain:

    - period
    - period_total

    Returns:
        A tuple containing:

        - absolute change;
        - percentage change.

        ``(None, None)`` is returned when fewer than two periods
        are available.

    Raises:
        TypeError:
            If trend_table is not a pandas DataFrame.

        KeyError:
            If a required column is missing.
    """

    if not isinstance(
        trend_table,
        pd.DataFrame,
    ):
        raise TypeError("trend_table must be a pandas DataFrame.")

    required_columns = {
        "period",
        "period_total",
    }

    missing_columns = required_columns - set(trend_table.columns)

    if missing_columns:
        missing_text = ", ".join(sorted(missing_columns))

        raise KeyError(f"Required period-comparison column(s) missing: {missing_text}")

    if trend_table.empty:
        return None, None

    period_totals = (
        trend_table[
            [
                "period",
                "period_total",
            ]
        ]
        .drop_duplicates(subset=["period"])
        .sort_values("period")
        .reset_index(drop=True)
    )

    if len(period_totals) < 2:
        return None, None

    previous_total = int(period_totals.iloc[-2]["period_total"])

    latest_total = int(period_totals.iloc[-1]["period_total"])

    absolute_change = latest_total - previous_total

    if previous_total == 0:
        percentage_change = 0.0 if latest_total == 0 else None
    else:
        percentage_change = round(
            absolute_change / previous_total * 100,
            2,
        )

    return (
        absolute_change,
        percentage_change,
    )
