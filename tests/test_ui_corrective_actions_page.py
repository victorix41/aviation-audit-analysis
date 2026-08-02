"""Tests for the Corrective Actions page."""

from unittest.mock import MagicMock, patch

import pandas as pd

from src.ui.pages.corrective_actions import render


def create_cleaned_dataframe() -> pd.DataFrame:
    """Create cleaned corrective-action data for page tests."""

    return pd.DataFrame(
        {
            "corrective_action": [
                "Revise procedure",
                "Provide refresher training",
                "Revise procedure",
            ],
            "response_due_date": pd.to_datetime(
                [
                    "2026-01-10",
                    "2026-02-10",
                    "2026-03-10",
                ]
            ),
        }
    )


def test_render_warns_when_data_is_missing() -> None:
    with (
        patch(
            "src.ui.pages.corrective_actions.st.session_state",
            {},
        ),
        patch("src.ui.pages.corrective_actions.st.warning") as warning_mock,
        patch("src.ui.pages.corrective_actions.render_page_header"),
    ):
        render("Corrective-action description")

    warning_mock.assert_called_once()


def test_render_generates_corrective_action_analysis() -> None:
    dataframe = create_cleaned_dataframe()

    fake_analysis = MagicMock()
    fake_analysis.pareto.table = pd.DataFrame()
    fake_analysis.monthly_wide_trend = pd.DataFrame()
    fake_analysis.quarterly_wide_trend = pd.DataFrame()
    fake_analysis.yearly_wide_trend = pd.DataFrame()

    with (
        patch(
            "src.ui.pages.corrective_actions.st.session_state",
            {
                "cleaned_dataframe": dataframe,
            },
        ),
        patch(
            "src.ui.pages.corrective_actions.generate_corrective_action_analysis",
            return_value=fake_analysis,
        ) as analysis_mock,
        patch("src.ui.pages.corrective_actions.render_page_header"),
        patch("src.ui.pages.corrective_actions._render_corrective_action_kpis"),
        patch("src.ui.pages.corrective_actions._render_corrective_action_pareto"),
        patch("src.ui.pages.corrective_actions._render_corrective_action_trends"),
        patch("src.ui.pages.corrective_actions._render_corrective_action_observations"),
        patch("src.ui.pages.corrective_actions.st.spinner") as spinner_mock,
        patch("src.ui.pages.corrective_actions.st.divider"),
    ):
        spinner_mock.return_value.__enter__.return_value = None
        spinner_mock.return_value.__exit__.return_value = None

        render("Corrective-action description")

    analysis_mock.assert_called_once_with(dataframe)
