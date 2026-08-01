"""Reports page."""

from src.ui.components import render_page_header, render_planned_sections


def render(description: str) -> None:
    """Render the reports page."""

    render_page_header("Reports", description)

    render_planned_sections(
        [
            "Executive summary report",
            "Severity report",
            "Human-factor report",
            "Root-cause report",
            "Corrective-action report",
            "Preventive-action report",
            "Excel, Word and PDF export options",
        ]
    )
