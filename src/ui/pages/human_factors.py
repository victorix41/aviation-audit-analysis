"""Human-factor page."""

from src.ui.components import render_page_header, render_planned_sections


def render(description: str) -> None:
    """Render the human-factor page."""

    render_page_header("Human Factors", description)

    render_planned_sections(
        [
            "Specified and unspecified human-factor KPIs",
            "Leading human factor",
            "Human-factor Pareto chart",
            "Monthly, quarterly and yearly trends",
            "Downloadable analysis tables",
        ]
    )
