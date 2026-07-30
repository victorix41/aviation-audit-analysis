"""Result model for preventive-action analytics."""

from dataclasses import dataclass

import pandas as pd

from src.models.pareto_result import ParetoResult


@dataclass(frozen=True)
class PreventiveActionAnalysis:
    """Structured output from the preventive-action analytics engine."""

    date_column: str

    total_findings: int
    specified_findings: int
    unspecified_findings: int
    unique_preventive_actions: int

    top_preventive_action: str | None
    top_preventive_action_frequency: int
    top_preventive_action_percentage: float

    pareto: ParetoResult

    monthly_trend: pd.DataFrame
    quarterly_trend: pd.DataFrame
    yearly_trend: pd.DataFrame

    monthly_wide_trend: pd.DataFrame
    quarterly_wide_trend: pd.DataFrame
    yearly_wide_trend: pd.DataFrame

    latest_month_total_change: int | None
    latest_month_total_change_percentage: float | None

    latest_quarter_total_change: int | None
    latest_quarter_total_change_percentage: float | None

    latest_year_total_change: int | None
    latest_year_total_change_percentage: float | None

    @property
    def specified_percentage(self) -> float:
        """Return the percentage of specified preventive actions."""

        if self.total_findings == 0:
            return 0.0

        return round(
            self.specified_findings
            / self.total_findings
            * 100,
            2,
        )

    @property
    def unspecified_percentage(self) -> float:
        """Return the percentage of unspecified preventive actions."""

        if self.total_findings == 0:
            return 0.0

        return round(
            self.unspecified_findings
            / self.total_findings
            * 100,
            2,
        )

    @property
    def has_monthly_comparison(self) -> bool:
        """Return whether at least two monthly periods exist."""

        return self.latest_month_total_change is not None

    @property
    def has_quarterly_comparison(self) -> bool:
        """Return whether at least two quarterly periods exist."""

        return self.latest_quarter_total_change is not None

    @property
    def has_yearly_comparison(self) -> bool:
        """Return whether at least two yearly periods exist."""

        return self.latest_year_total_change is not None