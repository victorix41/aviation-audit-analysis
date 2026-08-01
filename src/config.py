from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = PROJECT_ROOT / "data" / "Year 2026 - Audit findings.xlsx"

CLEANED_OUTPUT_FILE = PROJECT_ROOT / "outputs" / "audit_findings_cleaned.xlsx"

VALID_SEVERITY_LEVELS = {
    "Observation",
    "Minor",
    "Major",
}

REQUIRED_COLUMNS = {
    "audit_reference_no",
    "finding",
    "severity_level",
    "response_due_date",
    "immediate_action",
    "root_cause",
    "human_factor",
    "corrective_action",
    "preventive_action",
}
