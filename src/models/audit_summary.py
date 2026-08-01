from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class AuditSummary:
    """Structured KPI summary for an audit findings dataset."""

    as_of_date: date
    total_findings: int

    observation_count: int
    minor_count: int
    major_count: int
    unspecified_severity_count: int

    observation_percentage: float
    minor_percentage: float
    major_percentage: float
    unspecified_severity_percentage: float

    past_due_response_count: int
    due_within_30_days_count: int
    future_due_count: int
    missing_due_date_count: int

    earliest_due_date: date | None
    latest_due_date: date | None

    @property
    def high_attention_count(self) -> int:
        """Return the number of Major findings."""

        return self.major_count

    @property
    def severity_total(self) -> int:
        """Return the total number of severity records."""

        return (
            self.observation_count
            + self.minor_count
            + self.major_count
            + self.unspecified_severity_count
        )
