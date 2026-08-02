"""Service layer connecting the Streamlit UI to the data pipeline."""

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, BinaryIO

import pandas as pd

from src.analytics.executive_insights import (
    generate_executive_insights,
)
from src.analytics.human_factor_engine import (
    generate_human_factor_analysis,
)
from src.analytics.kpi_engine import generate_audit_summary
from src.analytics.root_cause_engine import (
    generate_root_cause_analysis,
)
from src.analytics.severity_engine import generate_severity_analysis
from src.data_cleaner import clean_audit_data
from src.models.audit_summary import AuditSummary
from src.models.executive_insights import ExecutiveInsights
from src.models.human_factor_analysis import HumanFactorAnalysis
from src.models.root_cause_analysis import RootCauseAnalysis
from src.models.severity_analysis import SeverityAnalysis
from src.validator import validate_audit_data

SUPPORTED_FILE_EXTENSIONS = {
    ".csv",
    ".xls",
    ".xlsx",
}


@dataclass(frozen=True)
class UploadedAuditResult:
    """Processed result returned after an audit file is uploaded."""

    file_name: str
    raw_dataframe: pd.DataFrame
    cleaned_dataframe: pd.DataFrame
    validation_results: dict[str, Any]


@dataclass(frozen=True)
class ExecutiveOverviewResult:
    """Combined analytics used by the Executive Overview page."""

    audit_summary: AuditSummary
    severity_analysis: SeverityAnalysis
    human_factor_analysis: HumanFactorAnalysis
    root_cause_analysis: RootCauseAnalysis
    executive_insights: ExecutiveInsights


def load_uploaded_audit_data(
    uploaded_file: BinaryIO,
    *,
    file_name: str,
) -> pd.DataFrame:
    """
    Load an uploaded Excel or CSV audit register.

    Args:
        uploaded_file:
            Binary file-like object supplied by Streamlit.

        file_name:
            Original uploaded filename, used to determine file type.

    Returns:
        Raw audit DataFrame.

    Raises:
        ValueError:
            If the file type is unsupported or the file is empty.

        RuntimeError:
            If pandas cannot read the uploaded file.
    """

    extension = Path(file_name).suffix.lower()

    if extension not in SUPPORTED_FILE_EXTENSIONS:
        supported_text = ", ".join(sorted(SUPPORTED_FILE_EXTENSIONS))

        raise ValueError(
            f"Unsupported file type. Supported extensions are: {supported_text}"
        )

    try:
        if extension == ".csv":
            dataframe = pd.read_csv(uploaded_file)
        else:
            dataframe = pd.read_excel(uploaded_file)
    except Exception as error:
        raise RuntimeError(
            f"Unable to read uploaded file '{file_name}': {error}"
        ) from error

    if dataframe.empty:
        raise ValueError("The uploaded audit register contains no records.")

    return dataframe


def process_uploaded_audit_file(
    uploaded_file: BinaryIO,
    *,
    file_name: str,
) -> UploadedAuditResult:
    """
    Load, clean, and validate an uploaded audit register.

    The existing project cleaner and validator remain the source of
    truth for data preparation and validation behaviour.
    """

    raw_dataframe = load_uploaded_audit_data(
        uploaded_file,
        file_name=file_name,
    )

    cleaned_dataframe = clean_audit_data(raw_dataframe)

    validation_results = validate_audit_data(cleaned_dataframe)

    return UploadedAuditResult(
        file_name=file_name,
        raw_dataframe=raw_dataframe,
        cleaned_dataframe=cleaned_dataframe,
        validation_results=validation_results,
    )


def generate_executive_overview(
    dataframe: pd.DataFrame,
    *,
    as_of_date: date | None = None,
) -> ExecutiveOverviewResult:
    """Generate analytics required by the Executive Overview page."""

    audit_summary = generate_audit_summary(
        dataframe,
        as_of_date=as_of_date,
    )

    severity_analysis = generate_severity_analysis(dataframe)

    human_factor_analysis = generate_human_factor_analysis(dataframe)

    root_cause_analysis = generate_root_cause_analysis(dataframe)

    executive_insights = generate_executive_insights(
        summary=audit_summary,
        severity=severity_analysis,
        human_factor=human_factor_analysis,
        root_cause=root_cause_analysis,
    )

    return ExecutiveOverviewResult(
        audit_summary=audit_summary,
        severity_analysis=severity_analysis,
        human_factor_analysis=human_factor_analysis,
        root_cause_analysis=root_cause_analysis,
        executive_insights=executive_insights,
    )
