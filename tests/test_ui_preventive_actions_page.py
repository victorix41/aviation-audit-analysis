"""Tests for the Preventive Actions page."""

from unittest.mock import MagicMock, patch

import pandas as pd

from src.ui.pages.preventive_actions import render


def create_cleaned_dataframe() -> pd.DataFrame:
    """Create cleaned preventive-action data for page tests."""

    return pd.DataFrame(
        {
            "preventive_action": [
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
            "src.ui.pages.preventive_actions.st.session_state",
            {},
        ),
        patch("src.ui.pages.preventive_actions.st.warning") as warning_mock,
        patch("src.ui.pages.preventive_actions.render_page_header"),
    ):
        render("preventive-action description")

    warning_mock.assert_called_once()


def test_render_generates_preventive_action_analysis() -> None:
    dataframe = create_cleaned_dataframe()

    fake_analysis = MagicMock()
    fake_analysis.pareto.table = pd.DataFrame()
    fake_analysis.monthly_wide_trend = pd.DataFrame()
    fake_analysis.quarterly_wide_trend = pd.DataFrame()
    fake_analysis.yearly_wide_trend = pd.DataFrame()

    with (
        patch(
            "src.ui.pages.preventive_actions.st.session_state",
            {
                "cleaned_dataframe": dataframe,
            },
        ),
        patch(
            "src.ui.pages.preventive_actions.generate_preventive_action_analysis",
            return_value=fake_analysis,
        ) as analysis_mock,
        patch("src.ui.pages.preventive_actions.render_page_header"),
        patch("src.ui.pages.preventive_actions._render_preventive_action_kpis"),
        patch("src.ui.pages.preventive_actions._render_preventive_action_pareto"),
        patch("src.ui.pages.preventive_actions._render_preventive_action_trends"),
        patch("src.ui.pages.preventive_actions._render_preventive_action_observations"),
        patch("src.ui.pages.preventive_actions.st.spinner") as spinner_mock,
        patch("src.ui.pages.preventive_actions.st.divider"),
    ):
        spinner_mock.return_value.__enter__.return_value = None
        spinner_mock.return_value.__exit__.return_value = None

        render("preventive-action description")

    analysis_mock.assert_called_once_with(dataframe)
