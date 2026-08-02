"""Tests for deterministic executive insights."""

from datetime import date

import pandas as pd

from src.analytics.executive_insights import (
    generate_executive_insights,
)
from src.analytics.human_factor_engine import (
    generate_human_factor_analysis,
)
from src.analytics.kpi_engine import generate_audit_summary
from src.analytics.root_cause_engine import (
    generate_root_cause_analysis,
)
from src.analytics.severity_engine import generate_severity_analysis


def create_audit_dataframe() -> pd.DataFrame:
    """Create cleaned audit data for insight testing."""

    return pd.DataFrame(
        {
            "severity_level": [
                "Major",
                "Major",
                "Minor",
                "Observation",
            ],
            "response_due_date": pd.to_datetime(
                [
                    "2026-01-01",
                    "2026-02-01",
                    "2026-04-01",
                    "2026-04-15",
                ]
            ),
            "human_factor": [
                "Knowledge gap",
                "Knowledge gap",
                "Time pressure",
                "Time pressure",
            ],
            "root_cause": [
                "Procedure weakness",
                "Procedure weakness",
                "Training gap",
                "Training gap",
            ],
        }
    )


def generate_insights():
    """Generate all analytics used by the insight engine."""

    dataframe = create_audit_dataframe()

    summary = generate_audit_summary(
        dataframe,
        as_of_date=date(2026, 3, 1),
    )

    severity = generate_severity_analysis(dataframe)
    human_factor = generate_human_factor_analysis(dataframe)
    root_cause = generate_root_cause_analysis(dataframe)

    return generate_executive_insights(
        summary=summary,
        severity=severity,
        human_factor=human_factor,
        root_cause=root_cause,
    )


def test_generates_observations() -> None:
    insights = generate_insights()

    assert insights.has_observations is True
    assert len(insights.observations) > 0


def test_generates_recommendations() -> None:
    insights = generate_insights()

    assert insights.has_recommendations is True
    assert len(insights.recommendations) > 0


def test_reports_major_findings() -> None:
    insights = generate_insights()

    assert any(
        "Major findings represent" in observation
        for observation in insights.observations
    )


def test_reports_past_due_dates_with_qualification() -> None:
    insights = generate_insights()

    matching_observations = [
        observation
        for observation in insights.observations
        if "earlier than the selected as-of date" in observation
    ]

    assert len(matching_observations) == 1
    assert "does not confirm" in matching_observations[0]


def test_reports_leading_human_factor() -> None:
    insights = generate_insights()

    assert any(
        "Knowledge gap is the leading recorded human factor" in observation
        for observation in insights.observations
    )


def test_reports_leading_root_cause() -> None:
    insights = generate_insights()

    assert any(
        "Procedure weakness is the leading recorded root cause" in observation
        for observation in insights.observations
    )
