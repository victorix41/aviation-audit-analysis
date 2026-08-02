"""Tests for the Human Factors page."""

from unittest.mock import MagicMock, patch

import pandas as pd

from src.ui.pages.human_factors import render


def create_cleaned_dataframe() -> pd.DataFrame:
    """Create cleaned human-factor data for page tests."""

    return pd.DataFrame(
        {
            "human_factor": [
                "Knowledge gap",
                "Time pressure",
                "Knowledge gap",
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
            "src.ui.pages.human_factors.st.session_state",
            {},
        ),
        patch("src.ui.pages.human_factors.st.warning") as warning_mock,
        patch("src.ui.pages.human_factors.render_page_header"),
    ):
        render("Human-factor description")

    warning_mock.assert_called_once()


def test_render_generates_human_factor_analysis() -> None:
    dataframe = create_cleaned_dataframe()

    fake_analysis = MagicMock()
    fake_analysis.pareto.table = pd.DataFrame()
    fake_analysis.monthly_trend = pd.DataFrame()
    fake_analysis.quarterly_trend = pd.DataFrame()
    fake_analysis.yearly_trend = pd.DataFrame()

    with (
        patch(
            "src.ui.pages.human_factors.st.session_state",
            {
                "cleaned_dataframe": dataframe,
            },
        ),
        patch(
            "src.ui.pages.human_factors.generate_human_factor_analysis",
            return_value=fake_analysis,
        ) as analysis_mock,
        patch("src.ui.pages.human_factors.render_page_header"),
        patch("src.ui.pages.human_factors._render_human_factor_kpis"),
        patch("src.ui.pages.human_factors._render_human_factor_pareto"),
        patch("src.ui.pages.human_factors._render_human_factor_trends"),
        patch("src.ui.pages.human_factors._render_human_factor_observations"),
        patch("src.ui.pages.human_factors.st.spinner") as spinner_mock,
        patch("src.ui.pages.human_factors.st.divider"),
    ):
        spinner_mock.return_value.__enter__.return_value = None
        spinner_mock.return_value.__exit__.return_value = None

        render("Human-factor description")

    analysis_mock.assert_called_once_with(dataframe)
