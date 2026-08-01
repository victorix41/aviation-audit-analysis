"""Corrective-action page."""

from src.ui.components import render_page_header, render_planned_sections


def render(description: str) -> None:
    """Render the corrective-action page."""

    render_page_header("Corrective Actions", description)

    render_planned_sections(
        [
            "Specified and unspecified corrective-action KPIs",
            "Leading corrective action",
            "Corrective-action Pareto chart",
            "Monthly, quarterly and yearly trends",
            "Downloadable analysis tables",
        ]
    )
