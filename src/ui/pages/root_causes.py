"""Root-cause page."""

from src.ui.components import render_page_header, render_planned_sections


def render(description: str) -> None:
    """Render the root-cause page."""

    render_page_header("Root Causes", description)

    render_planned_sections(
        [
            "Specified and unspecified root-cause KPIs",
            "Leading root cause",
            "Root-cause Pareto chart",
            "Monthly, quarterly and yearly trends",
            "Downloadable analysis tables",
        ]
    )
