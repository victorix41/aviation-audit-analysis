from pathlib import Path

import pandas as pd

from load_data import load_audit_data


PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = PROJECT_ROOT / "outputs" / "audit_findings_cleaned.xlsx"

VALID_SEVERITY_LEVELS = {
    "Observation",
    "Minor",
    "Major",
}


COLUMN_RENAME_MAP = {
    "Audit Finding Reference No.": "audit_reference_no",
    "Finding": "finding",
    "Severity Level (Observation, Minor, Major)": "severity_level",
    "Finding Response Due Date": "response_due_date",
    "Immediate Action": "immediate_action",
    "Root Cause": "root_cause",
    "Type of Human Factor(s) related Root Cause": "human_factor",
    "Corrective Action": "corrective_action",
    "Preventive Action": "preventive_action",
}


def standardise_text_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Remove unnecessary spaces from text columns."""

    cleaned_dataframe = dataframe.copy()

    text_columns = cleaned_dataframe.select_dtypes(include="str").columns

    for column in text_columns:
        cleaned_dataframe[column] = (
            cleaned_dataframe[column]
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )

    return cleaned_dataframe


def standardise_severity(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Standardise severity values."""

    cleaned_dataframe = dataframe.copy()

    cleaned_dataframe["severity_level"] = (
        cleaned_dataframe["severity_level"]
        .str.strip()
        .str.title()
    )

    return cleaned_dataframe


def validate_audit_data(dataframe: pd.DataFrame) -> dict:
    """Run data-quality validation checks."""

    validation_results = {}

    validation_results["total_records"] = len(dataframe)

    validation_results["duplicate_reference_numbers"] = int(
        dataframe["audit_reference_no"].duplicated().sum()
    )

    validation_results["missing_reference_numbers"] = int(
        dataframe["audit_reference_no"].isna().sum()
    )

    validation_results["missing_findings"] = int(
        dataframe["finding"].isna().sum()
    )

    validation_results["missing_due_dates"] = int(
        dataframe["response_due_date"].isna().sum()
    )

    invalid_severity_mask = ~dataframe["severity_level"].isin(
        VALID_SEVERITY_LEVELS
    )

    validation_results["invalid_severity_values"] = int(
        invalid_severity_mask.sum()
    )

    validation_results["invalid_severity_records"] = (
        dataframe.loc[
            invalid_severity_mask,
            ["audit_reference_no", "severity_level"],
        ]
        .to_dict(orient="records")
    )

    return validation_results


def clean_audit_data(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardise the audit dataset."""

    cleaned_dataframe = dataframe.copy()

    cleaned_dataframe = cleaned_dataframe.rename(
        columns=COLUMN_RENAME_MAP
    )

    cleaned_dataframe = standardise_text_columns(
        cleaned_dataframe
    )

    cleaned_dataframe = standardise_severity(
        cleaned_dataframe
    )

    cleaned_dataframe["response_due_date"] = pd.to_datetime(
        cleaned_dataframe["response_due_date"],
        errors="coerce",
    )

    cleaned_dataframe = cleaned_dataframe.sort_values(
        by="audit_reference_no"
    ).reset_index(drop=True)

    return cleaned_dataframe


def save_cleaned_data(
    dataframe: pd.DataFrame,
    output_file: Path = OUTPUT_FILE,
) -> None:
    """Save cleaned audit data to Excel."""

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe.to_excel(
        output_file,
        index=False,
    )


def display_validation_results(results: dict) -> None:
    """Display validation results in the terminal."""

    print("\nData validation results")
    print("-----------------------")
    print(f"Total records: {results['total_records']}")
    print(
        "Duplicate reference numbers: "
        f"{results['duplicate_reference_numbers']}"
    )
    print(
        "Missing reference numbers: "
        f"{results['missing_reference_numbers']}"
    )
    print(
        f"Missing findings: {results['missing_findings']}"
    )
    print(
        f"Missing due dates: {results['missing_due_dates']}"
    )
    print(
        "Invalid severity values: "
        f"{results['invalid_severity_values']}"
    )

    if results["invalid_severity_records"]:
        print("\nInvalid severity records:")

        for record in results["invalid_severity_records"]:
            print(record)


if __name__ == "__main__":
    raw_audit_data = load_audit_data()

    cleaned_audit_data = clean_audit_data(
        raw_audit_data
    )

    validation_results = validate_audit_data(
        cleaned_audit_data
    )

    display_validation_results(
        validation_results
    )

    save_cleaned_data(
        cleaned_audit_data
    )

    print(
        "\nCleaned audit data saved successfully:"
        f"\n{OUTPUT_FILE}"
    )