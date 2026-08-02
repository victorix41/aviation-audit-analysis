"""Tests for the Severity Analysis page."""

from unittest.mock import MagicMock, patch

import pandas as pd

from src.ui.pages.severity import render


def create_cleaned_dataframe() -> pd.DataFrame:
    """Create cleaned severity data for the page test."""

    return pd.DataFrame(
        {
            "severity_level": [
                "Major",
                "Minor",
                "Observation",
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
            "src.ui.pages.severity.st.session_state",
            {},
        ),
        patch("src.ui.pages.severity.st.warning") as warning_mock,
        patch("src.ui.pages.severity.render_page_header"),
    ):
        render("Severity description")

    warning_mock.assert_called_once()


def test_render_generates_severity_analysis() -> None:
    dataframe = create_cleaned_dataframe()

    fake_analysis = MagicMock()
    fake_analysis.pareto.table = pd.DataFrame()
    fake_analysis.monthly_trend = pd.DataFrame()
    fake_analysis.quarterly_trend = pd.DataFrame()
    fake_analysis.yearly_trend = pd.DataFrame()

    with (
        patch(
            "src.ui.pages.severity.st.session_state",
            {
                "cleaned_dataframe": dataframe,
            },
        ),
        patch(
            "src.ui.pages.severity.generate_severity_analysis",
            return_value=fake_analysis,
        ) as analysis_mock,
        patch("src.ui.pages.severity.render_page_header"),
        patch("src.ui.pages.severity._render_severity_kpis"),
        patch("src.ui.pages.severity._render_severity_charts"),
        patch("src.ui.pages.severity._render_period_tables"),
        patch("src.ui.pages.severity._render_severity_observations"),
        patch("src.ui.pages.severity.st.spinner") as spinner_mock,
        patch("src.ui.pages.severity.st.divider"),
    ):
        spinner_mock.return_value.__enter__.return_value = None
        spinner_mock.return_value.__exit__.return_value = None

        render("Severity description")

    analysis_mock.assert_called_once_with(dataframe)
