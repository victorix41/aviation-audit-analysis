from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class ParetoResult:
    """Structured result returned by the Pareto analytics engine."""

    column_name: str
    total_records: int
    table: pd.DataFrame

    @property
    def categories(self) -> list[str]:
        """Return Pareto categories in descending frequency order."""

        return self.table["category"].tolist()

    @property
    def frequencies(self) -> list[int]:
        """Return category frequencies."""

        return self.table["frequency"].tolist()

    @property
    def percentages(self) -> list[float]:
        """Return category percentages."""

        return self.table["percentage"].tolist()

    @property
    def cumulative_percentages(self) -> list[float]:
        """Return cumulative percentages."""

        return self.table["cumulative_percentage"].tolist()

    @property
    def top_category(self) -> str | None:
        """Return the category with the highest frequency."""

        if self.table.empty:
            return None

        return str(self.table.iloc[0]["category"])

    @property
    def top_category_frequency(self) -> int:
        """Return the frequency of the highest-ranked category."""

        if self.table.empty:
            return 0

        return int(self.table.iloc[0]["frequency"])