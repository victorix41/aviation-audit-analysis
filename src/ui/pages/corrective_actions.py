"""Corrective-action analysis page."""

import pandas as pd
import streamlit as st

from src.analytics.corrective_action_engine import (
    generate_corrective_action_analysis,
)
from src.models.corrective_action_analysis import (
    CorrectiveActionAnalysis,
)
from src.ui.charts import build_horizontal_pareto_chart
from src.ui.components import (
    render_kpi_cards,
    render_page_header,
)


def _render_leading_corrective_action(
    analysis: CorrectiveActionAnalysis,
) -> None:
    """Display the leading corrective action without truncating its name."""

    st.markdown("##### Leading Corrective Action")

    if analysis.top_corrective_action is None:
        st.info("No leading corrective action is available.")
        return

    st.markdown(f"**{analysis.top_corrective_action}**")

    st.caption(
        f"{analysis.top_corrective_action_frequency:,} findings "
        f"({analysis.top_corrective_action_percentage:.2f}% of all findings)"
    )


def _render_corrective_action_kpis(
    analysis: CorrectiveActionAnalysis,
) -> None:
    """Display corrective-action KPI cards."""

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
                "Unique Corrective Actions",
                analysis.unique_corrective_actions,
                "Number of distinct specified corrective-action categories.",
            ),
        ],
        columns_per_row=4,
    )

    leading_column, monthly_column, quarterly_column, yearly_column = st.columns(4)

    with leading_column:
        _render_leading_corrective_action(analysis)

    with monthly_column:
        st.metric(
            label="Latest Monthly Change",
            value=(
                analysis.latest_month_total_change
                if analysis.latest_month_total_change is not None
                else "N/A"
            ),
            help=("Change in corrective-action records between the latest two months."),
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
                "Change in corrective-action records between the latest two quarters."
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
            help=("Change in corrective-action records between the latest two years."),
        )


def _render_corrective_action_pareto(
    analysis: CorrectiveActionAnalysis,
) -> None:
    """Display the corrective-action Pareto chart and table."""

    st.subheader("Corrective Action Pareto")

    pareto_table = analysis.pareto.table

    if pareto_table.empty:
        st.info("No corrective-action data is available for Pareto analysis.")
        return

    chart = build_horizontal_pareto_chart(
        pareto_table,
        title=("Corrective Action Distribution and Cumulative Percentage"),
        category_title="Corrective action",
    )

    st.altair_chart(
        chart,
        use_container_width=True,
    )

    with st.expander("View corrective-action Pareto table"):
        st.dataframe(
            pareto_table,
            use_container_width=True,
            hide_index=True,
        )


def _render_corrective_action_trends(
    analysis: CorrectiveActionAnalysis,
) -> None:
    """Display corrective-action trend tables."""

    st.subheader("Corrective Action Trend Tables")

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
        "They represent response workload, not the date on which each "
        "corrective action was implemented or completed."
    )


def _render_corrective_action_observations(
    analysis: CorrectiveActionAnalysis,
) -> None:
    """Display deterministic observations and considerations."""

    st.subheader("Corrective Action Observations")

    if analysis.top_corrective_action is None:
        st.info("No corrective-action observations are available.")
        return

    st.markdown(
        f"- {analysis.top_corrective_action} is the most frequently "
        "recorded corrective action, appearing in "
        f"{analysis.top_corrective_action_frequency:,} findings "
        f"({analysis.top_corrective_action_percentage:.2f}%)."
    )

    st.markdown(
        f"- {analysis.specified_percentage:.2f}% of findings include "
        "a specified corrective action."
    )

    if analysis.unspecified_findings > 0:
        st.markdown(
            f"- {analysis.unspecified_findings:,} findings do not contain "
            "a specified corrective action."
        )

    pareto_table = analysis.pareto.table

    if len(pareto_table) >= 3:
        top_three_percentage = float(pareto_table.head(3)["percentage"].sum())

        st.markdown(
            "- The three most frequently recorded corrective actions "
            f"account for {top_three_percentage:.2f}% of findings."
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
        "- Review whether the most frequently used corrective action "
        "addresses the underlying root cause rather than only correcting "
        f"the immediate condition: {analysis.top_corrective_action}."
    )

    if analysis.unspecified_findings > 0:
        st.markdown(
            "- Complete missing corrective-action records before relying "
            "on the analysis for management assurance."
        )

    if len(pareto_table) >= 3:
        st.markdown(
            "- Review recurring corrective-action patterns for possible "
            "standardisation, duplication, or overreliance on short-term "
            "administrative controls."
        )

    st.markdown(
        "- Verify corrective-action effectiveness using objective evidence "
        "and follow-up monitoring where appropriate."
    )

    st.caption(
        "These observations and considerations are generated using "
        "deterministic rules from the displayed analytics. The dataset "
        "does not currently confirm implementation or effectiveness."
    )


def render(description: str) -> None:
    """Render the Corrective Actions page."""

    render_page_header(
        "Corrective Actions",
        description,
    )

    cleaned_dataframe = st.session_state.get("cleaned_dataframe")

    if not isinstance(
        cleaned_dataframe,
        pd.DataFrame,
    ):
        st.warning(
            "Upload and validate an audit register before viewing Corrective Actions."
        )
        return

    try:
        with st.spinner("Generating corrective-action analytics..."):
            analysis = generate_corrective_action_analysis(cleaned_dataframe)
    except (
        KeyError,
        TypeError,
        ValueError,
    ) as error:
        st.error("Corrective Action Analysis could not be generated.")

        with st.expander("Technical details"):
            st.code(str(error))

        return

    _render_corrective_action_kpis(analysis)

    st.divider()
    _render_corrective_action_pareto(analysis)

    st.divider()
    _render_corrective_action_trends(analysis)

    st.divider()
    _render_corrective_action_observations(analysis)
