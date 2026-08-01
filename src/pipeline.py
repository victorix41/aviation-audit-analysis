from typing import Any

import pandas as pd

from src.config import CLEANED_OUTPUT_FILE
from src.data_cleaner import clean_audit_data
from src.data_loader import load_audit_data
from src.validator import validate_audit_data


def save_cleaned_data(
    dataframe: pd.DataFrame,
) -> None:
    """Save cleaned audit data to Excel."""

    CLEANED_OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe.to_excel(
        CLEANED_OUTPUT_FILE,
        index=False,
    )


def display_validation_results(
    results: dict[str, Any],
) -> None:
    """Display validation results."""

    print("\nData validation results")
    print("-----------------------")

    for name, value in results.items():
        if name == "invalid_severity_records":
            continue

        label = name.replace("_", " ").title()
        print(f"{label}: {value}")

    if results.get("invalid_severity_records"):
        print("\nInvalid severity records:")

        for record in results["invalid_severity_records"]:
            print(record)


def run_pipeline() -> None:
    """Run the complete audit processing pipeline."""

    print("Loading audit register...")
    raw_dataframe = load_audit_data()

    print(f"Successfully loaded {len(raw_dataframe)} records.")

    print("Cleaning audit register...")
    cleaned_dataframe = clean_audit_data(raw_dataframe)

    print("Validating cleaned audit register...")
    validation_results = validate_audit_data(cleaned_dataframe)

    display_validation_results(validation_results)

    save_cleaned_data(cleaned_dataframe)

    print(f"\nCleaned data saved successfully:\n{CLEANED_OUTPUT_FILE}")


if __name__ == "__main__":
    run_pipeline()
