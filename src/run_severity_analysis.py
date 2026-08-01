from src.analytics.severity_engine import (
    generate_severity_analysis,
)
from src.data_cleaner import clean_audit_data
from src.data_loader import load_audit_data


def run_severity_analysis() -> None:
    """Run severity analytics using the audit register."""

    raw_dataframe = load_audit_data()

    cleaned_dataframe = clean_audit_data(raw_dataframe)

    result = generate_severity_analysis(
        cleaned_dataframe,
        date_column="response_due_date",
    )

    print("\n")
    print("=" * 70)
    print("AVIATION MRO SEVERITY ANALYSIS")
    print("=" * 70)

    print(f"Trend date field: {result.date_column}")

    print(
        "\nImportant: the current trend is grouped by "
        "response due date, not audit finding date."
    )

    print("\nCurrent severity position")
    print("-" * 70)

    print(
        "Observation: "
        f"{result.observation_count} "
        f"({result.observation_percentage:.2f}%)"
    )

    print(f"Minor: {result.minor_count} ({result.minor_percentage:.2f}%)")

    print(f"Major: {result.major_count} ({result.major_percentage:.2f}%)")

    print(
        "Unspecified: "
        f"{result.unspecified_count} "
        f"({result.unspecified_percentage:.2f}%)"
    )

    print("\nSeverity Pareto")
    print("-" * 70)

    print(result.pareto.table.to_string(index=False))

    print("\nMonthly response-due-date trend")
    print("-" * 70)

    print(result.monthly_trend.to_string(index=False))

    print("\nQuarterly response-due-date trend")
    print("-" * 70)

    print(result.quarterly_trend.to_string(index=False))

    print("\nYearly response-due-date trend")
    print("-" * 70)

    print(result.yearly_trend.to_string(index=False))

    print("\nLatest monthly comparison")
    print("-" * 70)

    print(f"Total finding change: {result.latest_month_total_change}")

    print(
        "Total finding percentage change: "
        f"{result.latest_month_total_change_percentage}"
    )

    print(f"Major finding change: {result.latest_month_major_change}")

    print(
        "Major finding percentage change: "
        f"{result.latest_month_major_change_percentage}"
    )


if __name__ == "__main__":
    run_severity_analysis()
