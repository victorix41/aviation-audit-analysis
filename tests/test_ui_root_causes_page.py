"""Tests for the Root Causes page."""

from unittest.mock import MagicMock, patch

import pandas as pd

from src.ui.pages.root_causes import render


def create_cleaned_dataframe() -> pd.DataFrame:
    """Create cleaned root-cause data for page tests."""

    return pd.DataFrame(
        {
            "root_cause": [
                "Procedure weakness",
                "Training gap",
                "Procedure weakness",
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
            "src.ui.pages.root_causes.st.session_state",
            {},
        ),
        patch("src.ui.pages.root_causes.st.warning") as warning_mock,
        patch("src.ui.pages.root_causes.render_page_header"),
    ):
        render("Root-cause description")

    warning_mock.assert_called_once()


def test_render_generates_root_cause_analysis() -> None:
    dataframe = create_cleaned_dataframe()

    fake_analysis = MagicMock()
    fake_analysis.pareto.table = pd.DataFrame()
    fake_analysis.monthly_trend = pd.DataFrame()
    fake_analysis.quarterly_trend = pd.DataFrame()
    fake_analysis.yearly_trend = pd.DataFrame()

    with (
        patch(
            "src.ui.pages.root_causes.st.session_state",
            {
                "cleaned_dataframe": dataframe,
            },
        ),
        patch(
            "src.ui.pages.root_causes.generate_root_cause_analysis",
            return_value=fake_analysis,
        ) as analysis_mock,
        patch("src.ui.pages.root_causes.render_page_header"),
        patch("src.ui.pages.root_causes._render_root_cause_kpis"),
        patch("src.ui.pages.root_causes._render_root_cause_pareto"),
        patch("src.ui.pages.root_causes._render_root_cause_trends"),
        patch("src.ui.pages.root_causes._render_root_cause_observations"),
        patch("src.ui.pages.root_causes.st.spinner") as spinner_mock,
        patch("src.ui.pages.root_causes.st.divider"),
    ):
        spinner_mock.return_value.__enter__.return_value = None
        spinner_mock.return_value.__exit__.return_value = None

        render("Root-cause description")

    analysis_mock.assert_called_once_with(dataframe)
