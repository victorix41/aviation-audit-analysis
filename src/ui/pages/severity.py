"""Severity-analysis page."""

from src.ui.components import render_page_header, render_planned_sections


def render(description: str) -> None:
    """Render the severity-analysis page."""

    render_page_header("Severity Analysis", description)

    render_planned_sections(
        [
            "Severity KPI cards",
            "Severity Pareto chart",
            "Monthly, quarterly and yearly trends",
            "Major-finding period comparison",
            "Downloadable severity tables",
        ]
    )
