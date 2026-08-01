from src.analytics.human_factor_engine import (
    generate_human_factor_analysis,
)
from src.data_cleaner import clean_audit_data
from src.data_loader import load_audit_data


def _format_change(
    change: int | None,
    percentage_change: float | None,
) -> str:
    """Format a period-comparison result for terminal display."""

    if change is None:
        return "Not available — fewer than two periods exist."

    percentage_text = (
        "Not defined" if percentage_change is None else f"{percentage_change:.2f}%"
    )

    return f"{change:+d} findings ({percentage_text})"


def run_human_factor_analysis() -> None:
    """Run human-factor analytics using the audit register."""

    raw_dataframe = load_audit_data()

    cleaned_dataframe = clean_audit_data(raw_dataframe)

    result = generate_human_factor_analysis(
        cleaned_dataframe,
        date_column="response_due_date",
    )

    print()
    print("=" * 80)
    print("AVIATION MRO HUMAN FACTOR ANALYSIS")
    print("=" * 80)

    print(f"Trend date field: {result.date_column}")

    print(
        "\nImportant: the current trend is grouped by "
        "response due date, not audit finding date."
    )

    print("\nCurrent human-factor position")
    print("-" * 80)

    print(f"Total findings: {result.total_findings}")

    print(
        f"Specified human factors: "
        f"{result.specified_findings} "
        f"({result.specified_percentage:.2f}%)"
    )

    print(
        f"Unspecified human factors: "
        f"{result.unspecified_findings} "
        f"({result.unspecified_percentage:.2f}%)"
    )

    print(f"Unique specified human factors: {result.unique_human_factors}")

    print("\nLeading human factor")
    print("-" * 80)

    print(f"Top factor: {result.top_factor}")

    print(f"Frequency: {result.top_factor_frequency}")

    print(f"Percentage of all findings: {result.top_factor_percentage:.2f}%")

    print("\nHuman-factor Pareto")
    print("-" * 80)

    if result.pareto.table.empty:
        print("No human-factor data is available.")
    else:
        print(result.pareto.table.to_string(index=False))

    print("\nMonthly response-due-date trend")
    print("-" * 80)

    if result.monthly_trend.empty:
        print("No monthly trend data is available.")
    else:
        print(result.monthly_trend.to_string(index=False))

    print("\nQuarterly response-due-date trend")
    print("-" * 80)

    if result.quarterly_trend.empty:
        print("No quarterly trend data is available.")
    else:
        print(result.quarterly_trend.to_string(index=False))

    print("\nYearly response-due-date trend")
    print("-" * 80)

    if result.yearly_trend.empty:
        print("No yearly trend data is available.")
    else:
        print(result.yearly_trend.to_string(index=False))

    print("\nLatest period comparisons")
    print("-" * 80)

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
    run_human_factor_analysis()
