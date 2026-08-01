"""Service layer connecting the Streamlit UI to the data pipeline."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO

import pandas as pd

from src.data_cleaner import clean_audit_data
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
