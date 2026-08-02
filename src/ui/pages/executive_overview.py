"""Executive-overview page."""

from datetime import date

import pandas as pd
import streamlit as st

from src.ui.charts import (
    build_monthly_workload_chart,
    build_pareto_chart,
)
from src.ui.components import (
    render_kpi_cards,
    render_page_header,
)
from src.ui.data_service import (
    ExecutiveOverviewResult,
    generate_executive_overview,
)


def _render_primary_kpis(
    overview: ExecutiveOverviewResult,
) -> None:
    """Display finding and severity KPIs."""

    summary = overview.audit_summary

    render_kpi_cards(
        [
            (
                "Total Findings",
                summary.total_findings,
                "Total number of audit findings in the current dataset.",
            ),
            (
                "Major Findings",
                summary.major_count,
                f"{summary.major_percentage:.2f}% of all findings.",
            ),
            (
                "Minor Findings",
                summary.minor_count,
                f"{summary.minor_percentage:.2f}% of all findings.",
            ),
            (
                "Observations",
                summary.observation_count,
                f"{summary.observation_percentage:.2f}% of all findings.",
            ),
        ]
    )


def _render_due_date_kpis(
    overview: ExecutiveOverviewResult,
) -> None:
    """Display response-due-date KPIs."""

    summary = overview.audit_summary

    render_kpi_cards(
        [
            (
                "Past Due",
                summary.past_due_response_count,
                (
                    "Response due dates before the selected as-of date. "
                    "This does not prove that the findings remain open."
                ),
            ),
            (
                "Due Within 30 Days",
                summary.due_within_30_days_count,
                "Responses due from the as-of date through the next 30 days.",
            ),
            (
                "Future Due",
                summary.future_due_count,
                "Responses due more than 30 days after the as-of date.",
            ),
            (
                "Missing Due Date",
                summary.missing_due_date_count,
                "Findings without a valid response due date.",
            ),
        ]
    )


def _render_analysis_preview(
    overview: ExecutiveOverviewResult,
) -> None:
    """Display headline category results before charts are added."""

    st.subheader("Leading categories")

    first_column, second_column = st.columns(2)

    human_factor = overview.human_factor_analysis
    root_cause = overview.root_cause_analysis

    with first_column:
        st.markdown("#### Leading human factor")

        if human_factor.top_factor is None:
            st.info("No human-factor category is available.")
        else:
            st.metric(
                label=human_factor.top_factor,
                value=human_factor.top_factor_frequency,
                help=(f"{human_factor.top_factor_percentage:.2f}% of all findings."),
            )

    with second_column:
        st.markdown("#### Leading root cause")

        if root_cause.top_root_cause is None:
            st.info("No root-cause category is available.")
        else:
            st.metric(
                label=root_cause.top_root_cause,
                value=root_cause.top_root_cause_frequency,
                help=(f"{root_cause.top_root_cause_percentage:.2f}% of all findings."),
            )


def _render_executive_charts(
    overview: ExecutiveOverviewResult,
) -> None:
    """Display severity Pareto and monthly workload charts."""

    severity_analysis = overview.severity_analysis

    first_column, second_column = st.columns(2)

    with first_column:
        st.subheader("Severity Pareto")

        pareto_table = severity_analysis.pareto.table

        if pareto_table.empty:
            st.info("No severity data is available for Pareto analysis.")
        else:
            pareto_chart = build_pareto_chart(
                pareto_table,
                title="Severity Distribution and Cumulative Percentage",
            )

            st.altair_chart(
                pareto_chart,
                use_container_width=True,
            )

            with st.expander("View Severity Pareto table"):
                st.dataframe(
                    pareto_table,
                    use_container_width=True,
                    hide_index=True,
                )

    with second_column:
        st.subheader("Monthly response workload")

        monthly_trend = severity_analysis.monthly_trend

        if monthly_trend.empty:
            st.info(
                "No valid response due dates are available "
                "for monthly workload analysis."
            )
        else:
            workload_chart = build_monthly_workload_chart(
                monthly_trend,
                title="Findings Grouped by Response Due Month",
            )

            st.altair_chart(
                workload_chart,
                use_container_width=True,
            )

            with st.expander("View Monthly Workload table"):
                st.dataframe(
                    monthly_trend,
                    use_container_width=True,
                    hide_index=True,
                )

    st.caption(
        "Trend note: the monthly chart groups findings by "
        "response_due_date. It represents response workload, "
        "not the date on which each finding originally occurred."
    )


def _render_management_insights(
    overview: ExecutiveOverviewResult,
) -> None:
    """Display rule-based observations and recommendations."""

    insights = overview.executive_insights

    st.subheader("Management observations")

    if insights.has_observations:
        for observation in insights.observations:
            st.markdown(f"- {observation}")
    else:
        st.info("No management observations are available.")

    st.subheader("Management considerations")

    if insights.has_recommendations:
        for recommendation in insights.recommendations:
            st.markdown(f"- {recommendation}")
    else:
        st.info("No additional management considerations were generated.")

    st.caption(
        "These statements are generated using deterministic rules from "
        "the displayed analytics. They are not AI-generated conclusions."
    )


def render(description: str) -> None:
    """Render the Executive Overview page."""

    render_page_header(
        "Executive Overview",
        description,
    )

    cleaned_dataframe = st.session_state.get("cleaned_dataframe")

    if not isinstance(
        cleaned_dataframe,
        pd.DataFrame,
    ):
        st.warning(
            "Upload and validate an audit register before viewing "
            "the Executive Overview."
        )
        return

    as_of_date = st.date_input(
        "As-of date",
        value=date.today(),
        help=(
            "Used to classify response due dates as past due, "
            "due within 30 days, or future due."
        ),
    )

    try:
        with st.spinner("Generating executive analytics..."):
            overview = generate_executive_overview(
                cleaned_dataframe,
                as_of_date=as_of_date,
            )
    except (
        KeyError,
        TypeError,
        ValueError,
    ) as error:
        st.error("The Executive Overview could not be generated.")

        with st.expander("Technical details"):
            st.code(str(error))

        return

    st.caption(
        f"Response due-date position as at "
        f"{overview.audit_summary.as_of_date:%d %B %Y}."
    )

    st.subheader("Finding profile")
    _render_primary_kpis(overview)

    st.subheader("Response due-date position")
    _render_due_date_kpis(overview)

    st.info(
        "Past due means the recorded response due date is earlier than "
        "the as-of date. The dataset does not currently contain a finding "
        "status or closure date, so this does not prove that the finding "
        "remains open."
    )

    _render_analysis_preview(overview)

    st.divider()
    _render_executive_charts(overview)

    st.divider()
    _render_management_insights(overview)
