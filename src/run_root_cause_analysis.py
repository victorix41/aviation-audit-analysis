"""Command-line runner for root-cause analytics."""

from src.analytics.root_cause_engine import (
    generate_root_cause_analysis,
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
        "Not defined" if percentage_change is None else f"{percentage_change:.2f}%"
    )

    return f"{change:+d} findings ({percentage_text})"


def run_root_cause_analysis() -> None:
    """Run root-cause analysis using the audit register."""

    raw_dataframe = load_audit_data()

    cleaned_dataframe = clean_audit_data(raw_dataframe)

    result = generate_root_cause_analysis(
        cleaned_dataframe,
        date_column="response_due_date",
    )

    print()
    print("=" * 90)
    print("AVIATION MRO ROOT CAUSE ANALYSIS")
    print("=" * 90)

    print(f"Trend date field: {result.date_column}")

    print(
        "\nImportant: the current trend is grouped by "
        "response due date, not audit finding date."
    )

    print("\nCurrent root-cause position")
    print("-" * 90)

    print(f"Total findings: {result.total_findings}")

    print(
        f"Specified root causes: "
        f"{result.specified_findings} "
        f"({result.specified_percentage:.2f}%)"
    )

    print(
        f"Unspecified root causes: "
        f"{result.unspecified_findings} "
        f"({result.unspecified_percentage:.2f}%)"
    )

    print(f"Unique specified root causes: {result.unique_root_causes}")

    print("\nLeading root cause")
    print("-" * 90)

    print(f"Top root cause: {result.top_root_cause}")

    print(f"Frequency: {result.top_root_cause_frequency}")

    print(f"Percentage of all findings: {result.top_root_cause_percentage:.2f}%")

    print("\nRoot-cause Pareto")
    print("-" * 90)

    if result.pareto.table.empty:
        print("No root-cause data is available.")
    else:
        print(result.pareto.table.to_string(index=False))

    print("\nMonthly root-cause trend — long format")
    print("-" * 90)

    if result.monthly_trend.empty:
        print("No monthly trend data is available.")
    else:
        print(result.monthly_trend.to_string(index=False))

    print("\nMonthly root-cause trend — wide format")
    print("-" * 90)

    if result.monthly_wide_trend.empty:
        print("No monthly trend data is available.")
    else:
        print(result.monthly_wide_trend.to_string(index=False))

    print("\nQuarterly root-cause trend")
    print("-" * 90)

    if result.quarterly_trend.empty:
        print("No quarterly trend data is available.")
    else:
        print(result.quarterly_trend.to_string(index=False))

    print("\nYearly root-cause trend")
    print("-" * 90)

    if result.yearly_trend.empty:
        print("No yearly trend data is available.")
    else:
        print(result.yearly_trend.to_string(index=False))

    print("\nLatest period comparisons")
    print("-" * 90)

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
    run_root_cause_analysis()
