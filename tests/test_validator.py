import pandas as pd

from src.validator import validate_audit_data


def create_valid_test_data() -> pd.DataFrame:
    """Create valid sample data for testing."""

    return pd.DataFrame(
        {
            "audit_reference_no": [
                "QA-2026-001",
                "QA-2026-002",
            ],
            "finding": [
                "Finding one",
                "Finding two",
            ],
            "severity_level": [
                "Minor",
                "Major",
            ],
            "response_due_date": pd.to_datetime(
                [
                    "2026-08-01",
                    "2026-08-02",
                ]
            ),
            "immediate_action": [
                "Action one",
                "Action two",
            ],
            "root_cause": [
                "Cause one",
                "Cause two",
            ],
            "human_factor": [
                "Communication",
                "Attention lapse",
            ],
            "corrective_action": [
                "Correction one",
                "Correction two",
            ],
            "preventive_action": [
                "Prevention one",
                "Prevention two",
            ],
        }
    )


def test_valid_data_passes_validation() -> None:
    dataframe = create_valid_test_data()

    results = validate_audit_data(dataframe)

    assert results["validation_passed"] is True
    assert results["duplicate_reference_numbers"] == 0
    assert results["invalid_severity_values"] == 0


def test_duplicate_reference_is_detected() -> None:
    dataframe = create_valid_test_data()

    dataframe.loc[
        1,
        "audit_reference_no",
    ] = "QA-2026-001"

    results = validate_audit_data(dataframe)

    assert results["validation_passed"] is False
    assert results["duplicate_reference_numbers"] == 2


def test_invalid_severity_is_detected() -> None:
    dataframe = create_valid_test_data()

    dataframe.loc[
        0,
        "severity_level",
    ] = "Critical"

    results = validate_audit_data(dataframe)

    assert results["validation_passed"] is False
    assert results["invalid_severity_values"] == 1