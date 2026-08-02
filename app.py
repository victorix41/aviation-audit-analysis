"""Streamlit entry point for Aviation Audit Analytics."""

import streamlit as st

from src.ui.components import render_sidebar_status
from src.ui.pages import PAGE_RENDERERS
from src.ui.state import initialize_session_state

PAGE_DESCRIPTIONS = {
    "Data Upload": ("Upload and validate an aviation audit register before analysis."),
    "Executive Overview": (
        "Review the organisation's overall audit position and key indicators."
    ),
    "Severity Analysis": (
        "Examine finding severity distribution, Pareto concentration and trends."
    ),
    "Human Factors": (
        "Identify the human factors most frequently associated with findings."
    ),
    "Root Causes": (
        "Analyse recurring root causes and their response-due-date trends."
    ),
    "Corrective Actions": (
        "Review corrective-action patterns and recurring response approaches."
    ),
    "Preventive Actions": (
        "Review preventive-action patterns and longer-term improvement measures."
    ),
    "Data Quality": (
        "Review validation outcomes, missing values and data-quality exceptions."
    ),
    "Reports": ("Prepare management-ready analytics reports and downloadable outputs."),
}


def main() -> None:
    """Run the Streamlit application."""

    st.set_page_config(
        page_title="Aviation Audit Analytics",
        page_icon="✈️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    initialize_session_state()

    with st.sidebar:
        st.title("Aviation Audit Analytics")
        st.caption("Management decision-support dashboard")

        selected_page = st.radio(
            "Navigation",
            options=list(PAGE_RENDERERS),
            key="selected_page",
        )

        st.divider()
        render_sidebar_status()

        st.divider()
        st.caption("Phase 8.3 — Executive dashboard")

    renderer = PAGE_RENDERERS[selected_page]
    renderer(PAGE_DESCRIPTIONS[selected_page])


if __name__ == "__main__":
    main()
