from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "Year 2026 - Audit findings.xlsx"

#checks that the file exists and reads it into a Pandas DataFrame
def load_audit_data(file_path: Path = DATA_FILE) -> pd.DataFrame:
    """Load the aviation MRO audit findings Excel file."""

    if not file_path.exists():
        raise FileNotFoundError(
            f"Audit file not found: {file_path}"
        )

    try:
        dataframe = pd.read_excel(file_path)
    except Exception as error:
        raise RuntimeError(
            f"Unable to read the Excel file: {error}"
        ) from error

    if dataframe.empty:
        raise ValueError("The audit register contains no data.")

    return dataframe

#To gives us an initial data-quality overview
def inspect_audit_data(dataframe: pd.DataFrame) -> None:
    """Display basic information about the audit dataset."""

    print("\nAudit register loaded successfully.")
    print(f"Number of rows: {len(dataframe)}")
    print(f"Number of columns: {len(dataframe.columns)}")

    print("\nColumn names:")
    for column in dataframe.columns:
        print(f"- {column}")

    print("\nData types:")
    print(dataframe.dtypes)

    print("\nMissing values by column:")
    print(dataframe.isna().sum())

    print("\nFirst five records:")
    print(dataframe.head())


if __name__ == "__main__":
    audit_data = load_audit_data()
    inspect_audit_data(audit_data)