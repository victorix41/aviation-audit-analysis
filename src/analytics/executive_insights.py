"""Rule-based executive insights for aviation audit analytics."""

from typing import Any, cast

from src.models.audit_summary import AuditSummary
from src.models.executive_insights import ExecutiveInsights
from src.models.human_factor_analysis import HumanFactorAnalysis
from src.models.root_cause_analysis import RootCauseAnalysis
from src.models.severity_analysis import SeverityAnalysis

MAJOR_ATTENTION_THRESHOLD = 20.0
CONCENTRATION_THRESHOLD = 80.0


def _generate_severity_observations(
    severity: SeverityAnalysis,
) -> list[str]:
    """Generate observations supported by severity analytics."""

    observations: list[str] = []

    severity_counts = {
        "Major": severity.major_count,
        "Minor": severity.minor_count,
        "Observation": severity.observation_count,
        "Unspecified": severity.unspecified_count,
    }

    severity_percentages = {
        "Major": severity.major_percentage,
        "Minor": severity.minor_percentage,
        "Observation": severity.observation_percentage,
        "Unspecified": severity.unspecified_percentage,
    }

    leading_severity = max(
        severity_counts,
        key=severity_counts.__getitem__,
    )

    observations.append(
        f"{leading_severity} is the largest severity category, "
        f"with {severity_counts[leading_severity]:,} findings "
        f"({severity_percentages[leading_severity]:.2f}%)."
    )

    pareto_table = severity.pareto.table

    if len(pareto_table) >= 2:
        top_two_percentage = float(pareto_table.head(2)["percentage"].sum())

        observations.append(
            "The two largest severity categories account for "
            f"{top_two_percentage:.2f}% of findings."
        )

    if severity.major_count > 0:
        observations.append(
            f"Major findings represent {severity.major_percentage:.2f}% "
            f"of all findings ({severity.major_count:,} records)."
        )

    return observations


def _generate_due_date_observations(
    summary: AuditSummary,
) -> list[str]:
    """Generate observations supported by response due dates."""

    observations: list[str] = []

    if summary.past_due_response_count > 0:
        observations.append(
            f"{summary.past_due_response_count:,} findings have recorded "
            "response due dates earlier than the selected as-of date. "
            "This does not confirm that those findings remain open."
        )

    if summary.due_within_30_days_count > 0:
        observations.append(
            f"{summary.due_within_30_days_count:,} findings have responses "
            "due within 30 days of the selected as-of date."
        )

    if summary.missing_due_date_count > 0:
        observations.append(
            f"{summary.missing_due_date_count:,} findings do not have a "
            "valid response due date."
        )

    return observations


def _generate_category_observations(
    human_factor: HumanFactorAnalysis,
    root_cause: RootCauseAnalysis,
) -> list[str]:
    """Generate observations for leading contributing categories."""

    observations: list[str] = []

    if human_factor.top_factor is not None:
        observations.append(
            f"{human_factor.top_factor} is the leading recorded human "
            f"factor, appearing in {human_factor.top_factor_frequency:,} "
            f"findings ({human_factor.top_factor_percentage:.2f}%)."
        )

    if root_cause.top_root_cause is not None:
        observations.append(
            f"{root_cause.top_root_cause} is the leading recorded root "
            f"cause, appearing in "
            f"{root_cause.top_root_cause_frequency:,} findings "
            f"({root_cause.top_root_cause_percentage:.2f}%)."
        )

    return observations


def _generate_workload_observations(
    severity: SeverityAnalysis,
) -> list[str]:
    """Generate observations from response-due-date workload trends."""

    monthly_trend = severity.monthly_trend

    if monthly_trend.empty:
        return []

    peak_index = monthly_trend["total"].idxmax()

    peak_period = str(
        cast(
            Any,
            monthly_trend.at[
                peak_index,
                "period",
            ],
        )
    )

    peak_total = int(
        cast(
            Any,
            monthly_trend.at[
                peak_index,
                "total",
            ],
        )
    )

    return [
        "The highest response-due-date workload occurs in "
        f"{peak_period}, with {peak_total:,} findings."
    ]


def _generate_recommendations(
    summary: AuditSummary,
    severity: SeverityAnalysis,
    human_factor: HumanFactorAnalysis,
    root_cause: RootCauseAnalysis,
) -> list[str]:
    """Generate conservative actions supported by the analytics."""

    recommendations: list[str] = []

    if severity.major_percentage >= MAJOR_ATTENTION_THRESHOLD:
        recommendations.append(
            "Prioritise management review of Major findings and confirm "
            "that appropriate containment and response actions are recorded."
        )
    elif severity.major_count > 0:
        recommendations.append(
            "Maintain timely management oversight of the recorded Major findings."
        )

    if summary.past_due_response_count > 0:
        recommendations.append(
            "Verify the current status and closure evidence for findings "
            "whose recorded response due dates are earlier than the "
            "selected as-of date."
        )

    if summary.due_within_30_days_count > 0:
        recommendations.append(
            "Confirm responsible owners and available resources for "
            "responses due within the next 30 days."
        )

    if summary.missing_due_date_count > 0:
        recommendations.append(
            "Complete or correct missing response due dates before relying "
            "on workload scheduling."
        )

    if human_factor.top_factor is not None:
        recommendations.append(
            "Review whether targeted controls, communication, or training "
            f"could address the recurring human factor: "
            f"{human_factor.top_factor}."
        )

    if root_cause.top_root_cause is not None:
        recommendations.append(
            "Assess whether a systemic improvement plan is appropriate for "
            f"the recurring root cause: {root_cause.top_root_cause}."
        )

    pareto_table = severity.pareto.table

    if len(pareto_table) >= 2:
        top_two_percentage = float(pareto_table.head(2)["percentage"].sum())

        if top_two_percentage >= CONCENTRATION_THRESHOLD:
            recommendations.append(
                "Focus improvement resources on the two largest severity "
                "categories because together they account for at least "
                "80% of findings."
            )

    return recommendations


def generate_executive_insights(
    *,
    summary: AuditSummary,
    severity: SeverityAnalysis,
    human_factor: HumanFactorAnalysis,
    root_cause: RootCauseAnalysis,
) -> ExecutiveInsights:
    """
    Generate deterministic management observations and recommendations.

    All messages are derived from the supplied analytics results.
    """

    if summary.total_findings == 0:
        return ExecutiveInsights(
            observations=("No audit findings are available for executive analysis.",),
            recommendations=(),
        )

    observations = [
        *_generate_severity_observations(severity),
        *_generate_due_date_observations(summary),
        *_generate_category_observations(
            human_factor,
            root_cause,
        ),
        *_generate_workload_observations(severity),
    ]

    recommendations = _generate_recommendations(
        summary,
        severity,
        human_factor,
        root_cause,
    )

    return ExecutiveInsights(
        observations=tuple(observations),
        recommendations=tuple(recommendations),
    )
