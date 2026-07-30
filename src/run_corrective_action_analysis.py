"""Command-line runner for corrective-action analytics."""

from src.analytics.corrective_action_engine import (
    generate_corrective_action_analysis,
)
from src.data_cleaner import clean_audit_data
from src.data_loader import load_audit_data


def _format_change(
    change: int | None,
    percentage_change: float | None,
) -> str:
    """Format a period comparison for terminal output."""

    if change is None:
        return "Not available — fewer than two periods exist."

    percentage_text = (
        "Not defined"
        if percentage_change is None
        else f"{percentage_change:.2f}%"
    )

    return (
        f"{change:+d} findings "
        f"({percentage_text})"
    )


def run_corrective_action_analysis() -> None:
    """Run corrective-action analysis using the audit register."""

    raw_dataframe = load_audit_data()

    cleaned_dataframe = clean_audit_data(
        raw_dataframe
    )

    result = generate_corrective_action_analysis(
        cleaned_dataframe,
        date_column="response_due_date",
    )

    print()
    print("=" * 100)
    print("AVIATION MRO CORRECTIVE ACTION ANALYSIS")
    print("=" * 100)

    print(
        f"Trend date field: "
        f"{result.date_column}"
    )

    print(
        "\nImportant: the current trend is grouped by "
        "response due date, not audit finding date."
    )

    print("\nCurrent corrective-action position")
    print("-" * 100)

    print(
        f"Total findings: "
        f"{result.total_findings}"
    )

    print(
        f"Specified corrective actions: "
        f"{result.specified_findings} "
        f"({result.specified_percentage:.2f}%)"
    )

    print(
        f"Unspecified corrective actions: "
        f"{result.unspecified_findings} "
        f"({result.unspecified_percentage:.2f}%)"
    )

    print(
        f"Unique specified corrective actions: "
        f"{result.unique_corrective_actions}"
    )

    print("\nLeading corrective action")
    print("-" * 100)

    print(
        f"Top corrective action: "
        f"{result.top_corrective_action}"
    )

    print(
        f"Frequency: "
        f"{result.top_corrective_action_frequency}"
    )

    print(
        f"Percentage of all findings: "
        f"{result.top_corrective_action_percentage:.2f}%"
    )

    print("\nCorrective-action Pareto")
    print("-" * 100)

    if result.pareto.table.empty:
        print("No corrective-action data is available.")
    else:
        print(
            result.pareto.table.to_string(
                index=False
            )
        )

    print("\nMonthly corrective-action trend — long format")
    print("-" * 100)

    if result.monthly_trend.empty:
        print("No monthly trend data is available.")
    else:
        print(
            result.monthly_trend.to_string(
                index=False
            )
        )

    print("\nMonthly corrective-action trend — wide format")
    print("-" * 100)

    if result.monthly_wide_trend.empty:
        print("No monthly trend data is available.")
    else:
        print(
            result.monthly_wide_trend.to_string(
                index=False
            )
        )

    print("\nQuarterly corrective-action trend")
    print("-" * 100)

    if result.quarterly_trend.empty:
        print("No quarterly trend data is available.")
    else:
        print(
            result.quarterly_trend.to_string(
                index=False
            )
        )

    print("\nYearly corrective-action trend")
    print("-" * 100)

    if result.yearly_trend.empty:
        print("No yearly trend data is available.")
    else:
        print(
            result.yearly_trend.to_string(
                index=False
            )
        )

    print("\nLatest period comparisons")
    print("-" * 100)

    print(
        "Monthly total change: "
        + _format_change(
            result.latest_month_total_change,
            result.latest_month_total_change_percentage,
        )
    )

    print(
        "Quarterly total change: "
        + _format_change(
            result.latest_quarter_total_change,
            result.latest_quarter_total_change_percentage,
        )
    )

    print(
        "Yearly total change: "
        + _format_change(
            result.latest_year_total_change,
            result.latest_year_total_change_percentage,
        )
    )


if __name__ == "__main__":
    run_corrective_action_analysis()