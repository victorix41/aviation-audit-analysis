import pandas as pd

from src.models.pareto_result import ParetoResult


def generate_pareto(
    dataframe: pd.DataFrame,
    column_name: str,
    *,
    include_missing: bool = False,
    missing_label: str = "Not specified",
) -> ParetoResult:
    """
    Generate a Pareto analysis for a categorical column.

    The result contains category frequency, percentage and cumulative
    percentage, sorted by descending frequency.
    """

    if column_name not in dataframe.columns:
        raise KeyError(
            f"Column '{column_name}' does not exist in the dataset."
        )

    series = dataframe[column_name].copy()

    if pd.api.types.is_string_dtype(series) or series.dtype == object:
        series = (
            series.astype("string")
            .str.strip()
            .replace("", pd.NA)
        )

    if include_missing:
        series = series.fillna(missing_label)
    else:
        series = series.dropna()

    total_records = int(len(series))

    if total_records == 0:
        empty_table = pd.DataFrame(
            columns=[
                "category",
                "frequency",
                "percentage",
                "cumulative_percentage",
            ]
        )

        return ParetoResult(
            column_name=column_name,
            total_records=0,
            table=empty_table,
        )

    frequency_table = (
        series.value_counts(dropna=False)
        .rename_axis("category")
        .reset_index(name="frequency")
    )

    frequency_table["category"] = (
        frequency_table["category"].astype(str)
    )

    frequency_table["percentage"] = (
        frequency_table["frequency"]
        .div(total_records)
        .mul(100)
    )

    frequency_table["cumulative_percentage"] = (
        frequency_table["percentage"].cumsum()
    )

    frequency_table["percentage"] = (
        frequency_table["percentage"].round(2)
    )

    frequency_table["cumulative_percentage"] = (
        frequency_table["cumulative_percentage"]
        .round(2)
        .clip(upper=100.0)
    )

    return ParetoResult(
        column_name=column_name,
        total_records=total_records,
        table=frequency_table,
    )