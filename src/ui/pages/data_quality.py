"""Data-quality page."""

from src.ui.components import render_page_header, render_planned_sections


def render(description: str) -> None:
    """Render the data-quality page."""

    render_page_header("Data Quality", description)

    render_planned_sections(
        [
            "Rows loaded",
            "Missing required fields",
            "Duplicate audit references",
            "Invalid severity values",
            "Invalid response due dates",
            "Downloadable validation report",
        ]
    )
