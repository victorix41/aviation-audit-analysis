import pandas as pd


COLUMN_RENAME_MAP = {
    "Audit Finding Reference No.": "audit_reference_no",
    "Finding": "finding",
    "Severity Level (Observation, Minor, Major)": (
        "severity_level"
    ),
    "Finding Response Due Date": "response_due_date",
    "Immediate Action": "immediate_action",
    "Root Cause": "root_cause",
    "Type of Human Factor(s) related Root Cause": (
        "human_factor"
    ),
    "Corrective Action": "corrective_action",
    "Preventive Action": "preventive_action",
}


def clean_text_columns(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Remove leading, trailing and repeated spaces."""

    cleaned_dataframe = dataframe.copy()

    text_columns = cleaned_dataframe.select_dtypes(
        include=["object", "string"]
    ).columns

    for column in text_columns:
        cleaned_dataframe[column] = (
            cleaned_dataframe[column]
            .astype("string")
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )

    return cleaned_dataframe


def clean_audit_data(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Clean and standardise the audit register."""

    cleaned_dataframe = dataframe.copy()

    cleaned_dataframe = cleaned_dataframe.rename(
        columns=COLUMN_RENAME_MAP
    )

    cleaned_dataframe = clean_text_columns(
        cleaned_dataframe
    )

    if "severity_level" in cleaned_dataframe.columns:
        cleaned_dataframe["severity_level"] = (
            cleaned_dataframe["severity_level"]
            .str.title()
        )

    if "response_due_date" in cleaned_dataframe.columns:
        cleaned_dataframe["response_due_date"] = (
            pd.to_datetime(
                cleaned_dataframe["response_due_date"],
                errors="coerce",
            )
        )

    if "audit_reference_no" in cleaned_dataframe.columns:
        cleaned_dataframe = (
            cleaned_dataframe
            .sort_values("audit_reference_no")
            .reset_index(drop=True)
        )

    return cleaned_dataframe