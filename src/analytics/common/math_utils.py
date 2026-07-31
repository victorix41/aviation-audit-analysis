"""Shared mathematical utilities for analytics engines."""


def calculate_percentage(
    count: int,
    total: int,
    *,
    decimal_places: int = 2,
) -> float:
    """
    Calculate a percentage safely.

    Returns 0.0 when total is zero.
    """

    if decimal_places < 0:
        raise ValueError(
            "decimal_places must be zero or greater."
        )

    if total == 0:
        return 0.0

    return round(
        count / total * 100,
        decimal_places,
    )
