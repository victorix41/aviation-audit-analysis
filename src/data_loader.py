from pathlib import Path

import pandas as pd

from src.config import DATA_FILE


def load_audit_data(
    file_path: Path = DATA_FILE,
) -> pd.DataFrame:
    """Load an aviation MRO audit register from Excel."""

    if not file_path.exists():
        raise FileNotFoundError(f"Audit file not found: {file_path}")

    try:
        dataframe = pd.read_excel(file_path)
    except Exception as error:
        raise RuntimeError(f"Unable to read the Excel file: {error}") from error

    if dataframe.empty:
        raise ValueError("The audit register contains no records.")

    return dataframe
