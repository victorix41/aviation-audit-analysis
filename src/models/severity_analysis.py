from dataclasses import dataclass

import pandas as pd

from src.models.pareto_result import ParetoResult


@dataclass(frozen=True)
class SeverityAnalysis:
    """Structured output from the severity analytics engine."""

    date_column: str
    total_findings: int

    observation_count: int
    minor_count: int
    major_count: int
    unspecified_count: int

    observation_percentage: float
    minor_percentage: float
    major_percentage: float
    unspecified_percentage: float

    pareto: ParetoResult

    monthly_trend: pd.DataFrame
    quarterly_trend: pd.DataFrame
    yearly_trend: pd.DataFrame

    latest_month_total_change: int | None
    latest_month_total_change_percentage: float | None

    latest_month_major_change: int | None
    latest_month_major_change_percentage: float | None

    @property
    def severity_total(self) -> int:
        """Return the total of all severity categories."""

        return (
            self.observation_count
            + self.minor_count
            + self.major_count
            + self.unspecified_count
        )

    @property
    def major_share(self) -> float:
        """Return the percentage of findings classified as Major."""

        return self.major_percentage

    @property
    def has_monthly_comparison(self) -> bool:
        """Return whether two monthly periods exist for comparison."""

        return self.latest_month_total_change is not None
