"""Root-cause analysis page."""

import pandas as pd
import streamlit as st

from src.analytics.root_cause_engine import (
    generate_root_cause_analysis,
)
from src.models.root_cause_analysis import RootCauseAnalysis
from src.ui.charts import build_horizontal_pareto_chart
from src.ui.components import (
    render_kpi_cards,
    render_page_header,
)


def _render_leading_root_cause(
    analysis: RootCauseAnalysis,
) -> None:
    """Display the leading root cause without truncating its name."""

    st.markdown("##### Leading Root Cause")

    if analysis.top_root_cause is None:
        st.info("No leading root cause is available.")
        return

    st.markdown(f"**{analysis.top_root_cause}**")

    st.caption(
        f"{analysis.top_root_cause_frequency:,} findings "
        f"({analysis.top_root_cause_percentage:.2f}% of all findings)"
    )


def _render_root_cause_kpis(
    analysis: RootCauseAnalysis,
) -> None:
    """Display root-cause KPI cards."""

    render_kpi_cards(
        [
            (
                "Total Findings",
                analysis.total_findings,
                "Total number of findings in the current dataset.",
            ),
            (
                "Specified",
                analysis.specified_findings,
                f"{analysis.specified_percentage:.2f}% of findings.",
            ),
            (
                "Unspecified",
                analysis.unspecified_findings,
                f"{analysis.unspecified_percentage:.2f}% of findings.",
            ),
            (
                "Unique Root Causes",
                analysis.unique_root_causes,
                "Number of distinct specified root-cause categories.",
            ),
        ],
        columns_per_row=4,
    )

    leading_column, monthly_column, quarterly_column, yearly_column = st.columns(4)

    with leading_column:
        _render_leading_root_cause(analysis)

    with monthly_column:
        st.metric(
            label="Latest Monthly Change",
            value=(
                analysis.latest_month_total_change
                if analysis.latest_month_total_change is not None
                else "N/A"
            ),
            help=("Change in total root-cause records between the latest two months."),
        )

    with quarterly_column:
        st.metric(
            label="Latest Quarterly Change",
            value=(
                analysis.latest_quarter_total_change
                if analysis.latest_quarter_total_change is not None
                else "N/A"
            ),
            help=(
                "Change in total root-cause records between the latest two quarters."
            ),
        )

    with yearly_column:
        st.metric(
            label="Latest Yearly Change",
            value=(
                analysis.latest_year_total_change
                if analysis.latest_year_total_change is not None
                else "N/A"
            ),
            help=("Change in total root-cause records between the latest two years."),
        )


def _render_root_cause_pareto(
    analysis: RootCauseAnalysis,
) -> None:
    """Display the horizontal root-cause Pareto chart and table."""

    st.subheader("Root Cause Pareto")

    pareto_table = analysis.pareto.table

    if pareto_table.empty:
        st.info("No root-cause data is available for Pareto analysis.")
        return

    chart = build_horizontal_pareto_chart(
        pareto_table,
        title="Root Cause Distribution and Cumulative Percentage",
        category_title="Root cause",
    )

    st.altair_chart(
        chart,
        use_container_width=True,
    )

    with st.expander("View root-cause Pareto table"):
        st.dataframe(
            pareto_table,
            use_container_width=True,
            hide_index=True,
        )


def _render_root_cause_trends(
    analysis: RootCauseAnalysis,
) -> None:
    """Display root-cause trend tables."""

    st.subheader("Root Cause Trend Tables")

    monthly_tab, quarterly_tab, yearly_tab = st.tabs(
        [
            "Monthly",
            "Quarterly",
            "Yearly",
        ]
    )

    with monthly_tab:
        if analysis.monthly_wide_trend.empty:
            st.info("No valid response due dates are available for monthly analysis.")
        else:
            st.dataframe(
                analysis.monthly_wide_trend,
                use_container_width=True,
                hide_index=True,
            )

    with quarterly_tab:
        if analysis.quarterly_wide_trend.empty:
            st.info("No valid response due dates are available for quarterly analysis.")
        else:
            st.dataframe(
                analysis.quarterly_wide_trend,
                use_container_width=True,
                hide_index=True,
            )

    with yearly_tab:
        if analysis.yearly_wide_trend.empty:
            st.info("No valid response due dates are available for yearly analysis.")
        else:
            st.dataframe(
                analysis.yearly_wide_trend,
                use_container_width=True,
                hide_index=True,
            )

    st.caption(
        "Trend note: these tables group findings by response_due_date. "
        "They represent response workload, not the date each finding "
        "originally occurred."
    )


def _render_root_cause_observations(
    analysis: RootCauseAnalysis,
) -> None:
    """Display deterministic observations and considerations."""

    st.subheader("Root Cause Observations")

    if analysis.top_root_cause is None:
        st.info("No root-cause observations are available.")
        return

    st.markdown(
        f"- {analysis.top_root_cause} is the leading recorded root cause, "
        f"appearing in {analysis.top_root_cause_frequency:,} findings "
        f"({analysis.top_root_cause_percentage:.2f}%)."
    )

    st.markdown(
        f"- {analysis.specified_percentage:.2f}% of findings include "
        "a specified root cause."
    )

    if analysis.unspecified_findings > 0:
        st.markdown(
            f"- {analysis.unspecified_findings:,} findings do not contain "
            "a specified root cause."
        )

    pareto_table = analysis.pareto.table

    if len(pareto_table) >= 3:
        top_three_percentage = float(pareto_table.head(3)["percentage"].sum())

        st.markdown(
            "- The three most frequent root causes account for "
            f"{top_three_percentage:.2f}% of findings."
        )

    if analysis.has_monthly_comparison:
        change = analysis.latest_month_total_change

        if change is not None:
            if change > 0:
                direction = "increased"
            elif change < 0:
                direction = "decreased"
            else:
                direction = "did not change"

            st.markdown(
                "- The latest monthly response workload "
                f"{direction} by {abs(change):,} finding(s)."
            )

    st.subheader("Management Considerations")

    st.markdown(
        "- Assess whether a systemic improvement plan is appropriate "
        f"for the recurring root cause: {analysis.top_root_cause}."
    )

    if analysis.unspecified_findings > 0:
        st.markdown(
            "- Improve root-cause recording and classification so that "
            "management decisions are based on complete information."
        )

    if len(pareto_table) >= 3:
        st.markdown(
            "- Prioritise investigation and improvement resources on "
            "the most frequent root causes before lower-frequency causes."
        )

    st.caption(
        "These observations and considerations are generated using "
        "deterministic rules from the displayed analytics."
    )


def render(description: str) -> None:
    """Render the Root Causes page."""

    render_page_header(
        "Root Causes",
        description,
    )

    cleaned_dataframe = st.session_state.get("cleaned_dataframe")

    if not isinstance(
        cleaned_dataframe,
        pd.DataFrame,
    ):
        st.warning("Upload and validate an audit register before viewing Root Causes.")
        return

    try:
        with st.spinner("Generating root-cause analytics..."):
            analysis = generate_root_cause_analysis(cleaned_dataframe)
    except (
        KeyError,
        TypeError,
        ValueError,
    ) as error:
        st.error("Root Cause Analysis could not be generated.")

        with st.expander("Technical details"):
            st.code(str(error))

        return

    _render_root_cause_kpis(analysis)

    st.divider()
    _render_root_cause_pareto(analysis)

    st.divider()
    _render_root_cause_trends(analysis)

    st.divider()
    _render_root_cause_observations(analysis)
