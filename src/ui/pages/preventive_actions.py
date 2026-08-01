"""Preventive-action page."""

from src.ui.components import render_page_header, render_planned_sections


def render(description: str) -> None:
    """Render the preventive-action page."""

    render_page_header("Preventive Actions", description)

    render_planned_sections(
        [
            "Specified and unspecified preventive-action KPIs",
            "Leading preventive action",
            "Preventive-action Pareto chart",
            "Monthly, quarterly and yearly trends",
            "Downloadable analysis tables",
        ]
    )
