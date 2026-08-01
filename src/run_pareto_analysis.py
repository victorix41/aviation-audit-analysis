from src.analytics.pareto_engine import generate_pareto
from src.data_cleaner import clean_audit_data
from src.data_loader import load_audit_data

PARETO_COLUMNS = [
    "severity_level",
    "human_factor",
    "root_cause",
    "corrective_action",
    "preventive_action",
]


def run_pareto_analysis() -> None:
    """Run Pareto analyses for the main audit categories."""

    raw_dataframe = load_audit_data()
    cleaned_dataframe = clean_audit_data(raw_dataframe)

    for column_name in PARETO_COLUMNS:
        result = generate_pareto(
            cleaned_dataframe,
            column_name,
        )

        print("\n")
        print("=" * 70)
        print(f"Pareto analysis: {column_name.replace('_', ' ').title()}")
        print("=" * 70)

        print(result.table.to_string(index=False))

        print(f"\nTop category: {result.top_category}")
        print(f"Top category frequency: {result.top_category_frequency}")


if __name__ == "__main__":
    run_pareto_analysis()
