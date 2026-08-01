"""Shared text-standardisation utilities for analytics engines."""

import pandas as pd

DEFAULT_UNSPECIFIED_LABEL = "Unspecified"


def standardise_text_series(
    series: pd.Series,
    *,
    unspecified_label: str = DEFAULT_UNSPECIFIED_LABEL,
    sentence_case: bool = True,
    collapse_whitespace: bool = True,
) -> pd.Series:
    """
    Clean and standardise a pandas text series.

    Processing includes:

    - converting values to pandas' nullable string type;
    - removing leading and trailing whitespace;
    - optionally reducing repeated internal whitespace;
    - replacing blank and missing values with a supplied label;
    - optionally applying sentence-style capitalisation.

    Args:
        series:
            Pandas Series containing text values.

        unspecified_label:
            Replacement value for missing or blank entries.

        sentence_case:
            Whether to convert text to lowercase and capitalise its
            first character.

        collapse_whitespace:
            Whether repeated internal whitespace should be replaced
            by one space.

    Returns:
        A cleaned pandas Series using pandas' string dtype.

    Raises:
        TypeError:
            If ``series`` is not a pandas Series.

        ValueError:
            If ``unspecified_label`` is blank.
    """

    if not isinstance(series, pd.Series):
        raise TypeError("series must be a pandas Series.")

    cleaned_unspecified_label = str(unspecified_label).strip()

    if not cleaned_unspecified_label:
        raise ValueError("unspecified_label must not be blank.")

    cleaned_series = series.astype("string").str.strip()

    if collapse_whitespace:
        cleaned_series = cleaned_series.str.replace(
            r"\s+",
            " ",
            regex=True,
        )

    missing_mask = cleaned_series.isna() | cleaned_series.eq("")

    cleaned_series = cleaned_series.mask(
        missing_mask,
        cleaned_unspecified_label,
    )

    if sentence_case:
        specified_mask = cleaned_series.ne(cleaned_unspecified_label)

        cleaned_series = cleaned_series.mask(
            specified_mask,
            cleaned_series[specified_mask].str.lower().str.capitalize(),
        )

    return cleaned_series.astype("string")
