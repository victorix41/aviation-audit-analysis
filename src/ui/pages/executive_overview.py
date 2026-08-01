"""Executive-overview page."""

from src.ui.components import render_page_header, render_planned_sections


def render(description: str) -> None:
    """Render the executive-overview page."""

    render_page_header("Executive Overview", description)

    render_planned_sections(
        [
            "Executive KPI cards",
            "Severity Pareto analysis",
            "Monthly response-due-date workload",
            "Leading human factors",
            "Leading root causes",
            "Rule-based management observations",
        ]
    )
