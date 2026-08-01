"""Tests for the Streamlit data service layer."""

from io import BytesIO

import pandas as pd
import pytest

from src.ui.data_service import (
    load_uploaded_audit_data,
    process_uploaded_audit_file,
)


def create_source_dataframe() -> pd.DataFrame:
    """Create source data using the spreadsheet column names."""

    return pd.DataFrame(
        {
            "Audit Finding Reference No.": [
                "AF-002",
                "AF-001",
            ],
            "Finding": [
                "Finding two",
                "Finding one",
            ],
            "Severity Level (Observation, Minor, Major)": [
                "major",
                " minor ",
            ],
            "Finding Response Due Date": [
                "2026-03-10",
                "2026-02-10",
            ],
            "Immediate Action": [
                "Action two",
                "Action one",
            ],
            "Root Cause": [
                "Cause two",
                "Cause one",
            ],
            "Type of Human Factor(s) related Root Cause": [
                "Time pressure",
                "Knowledge gap",
            ],
            "Corrective Action": [
                "Corrective two",
                "Corrective one",
            ],
            "Preventive Action": [
                "Preventive two",
                "Preventive one",
            ],
        }
    )


def create_csv_upload() -> BytesIO:
    """Create an in-memory CSV upload."""

    dataframe = create_source_dataframe()
    buffer = BytesIO()
    buffer.write(dataframe.to_csv(index=False).encode("utf-8"))
    buffer.seek(0)
    return buffer


def test_load_uploaded_csv() -> None:
    uploaded_file = create_csv_upload()

    result = load_uploaded_audit_data(
        uploaded_file,
        file_name="audit.csv",
    )

    assert len(result) == 2
    assert "Audit Finding Reference No." in result.columns


def test_process_uploaded_csv() -> None:
    uploaded_file = create_csv_upload()

    result = process_uploaded_audit_file(
        uploaded_file,
        file_name="audit.csv",
    )

    assert result.file_name == "audit.csv"
    assert len(result.raw_dataframe) == 2
    assert len(result.cleaned_dataframe) == 2

    assert result.cleaned_dataframe["audit_reference_no"].tolist() == [
        "AF-001",
        "AF-002",
    ]

    assert result.cleaned_dataframe["severity_level"].tolist() == [
        "Minor",
        "Major",
    ]

    assert result.validation_results["validation_passed"] is True


def test_unsupported_file_type_raises_error() -> None:
    uploaded_file = BytesIO(b"not supported")

    with pytest.raises(
        ValueError,
        match="Unsupported file type",
    ):
        load_uploaded_audit_data(
            uploaded_file,
            file_name="audit.txt",
        )


def test_empty_csv_raises_error() -> None:
    uploaded_file = BytesIO(b"column_a,column_b\n")

    with pytest.raises(
        ValueError,
        match="contains no records",
    ):
        load_uploaded_audit_data(
            uploaded_file,
            file_name="audit.csv",
        )
