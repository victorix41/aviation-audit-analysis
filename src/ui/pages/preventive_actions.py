"""Preventive-action analysis page."""

import pandas as pd
import streamlit as st

from src.analytics.preventive_action_engine import (
    generate_preventive_action_analysis,
)
from src.models.preventive_action_analysis import (
    PreventiveActionAnalysis,
)
from src.ui.charts import build_horizontal_pareto_chart
from src.ui.components import (
    render_kpi_cards,
    render_page_header,
)


def _render_leading_preventive_action(
    analysis: PreventiveActionAnalysis,
) -> None:
    """Display the leading preventive action."""

    st.markdown("##### Leading Preventive Action")

    if analysis.top_preventive_action is None:
        st.info("No leading preventive action is available.")
        return

    st.markdown(f"**{analysis.top_preventive_action}**")

    st.caption(
        f"{analysis.top_preventive_action_frequency:,} findings "
        f"({analysis.top_preventive_action_percentage:.2f}% of all findings)"
    )


def _render_preventive_action_kpis(
    analysis: PreventiveActionAnalysis,
) -> None:

    render_kpi_cards(
        [
            (
                "Total Findings",
                analysis.total_findings,
                "Total findings.",
            ),
            (
                "Specified",
                analysis.specified_findings,
                f"{analysis.specified_percentage:.2f}% specified.",
            ),
            (
                "Unspecified",
                analysis.unspecified_findings,
                f"{analysis.unspecified_percentage:.2f}% unspecified.",
            ),
            (
                "Unique Preventive Actions",
                analysis.unique_preventive_actions,
                "Distinct preventive actions.",
            ),
        ],
        columns_per_row=4,
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        _render_leading_preventive_action(analysis)

    with col2:
        st.metric(
            "Latest Monthly Change",
            (
                analysis.latest_month_total_change
                if analysis.latest_month_total_change is not None
                else "N/A"
            ),
        )

    with col3:
        st.metric(
            "Latest Quarterly Change",
            (
                analysis.latest_quarter_total_change
                if analysis.latest_quarter_total_change is not None
                else "N/A"
            ),
        )

    with col4:
        st.metric(
            "Latest Yearly Change",
            (
                analysis.latest_year_total_change
                if analysis.latest_year_total_change is not None
                else "N/A"
            ),
        )


def _render_preventive_action_pareto(
    analysis: PreventiveActionAnalysis,
) -> None:

    st.subheader("Preventive Action Pareto")

    if analysis.pareto.table.empty:
        st.info("No preventive-action data is available.")
        return

    chart = build_horizontal_pareto_chart(
        analysis.pareto.table,
        title=("Preventive Action Distribution and Cumulative Percentage"),
        category_title="Preventive action",
    )

    st.altair_chart(
        chart,
        use_container_width=True,
    )

    with st.expander("View preventive-action Pareto table"):
        st.dataframe(
            analysis.pareto.table,
            hide_index=True,
            use_container_width=True,
        )


def _render_preventive_action_observations(
    analysis: PreventiveActionAnalysis,
) -> None:

    st.subheader("Preventive Action Observations")

    if analysis.top_preventive_action is None:
        st.info("No preventive-action observations are available.")
        return

    st.markdown(
        f"- {analysis.top_preventive_action} is the most frequently "
        "recorded preventive action, appearing in "
        f"{analysis.top_preventive_action_frequency:,} findings "
        f"({analysis.top_preventive_action_percentage:.2f}%)."
    )

    st.markdown(
        f"- {analysis.specified_percentage:.2f}% of findings "
        "include a specified preventive action."
    )

    if analysis.unspecified_findings > 0:
        st.markdown(
            f"- {analysis.unspecified_findings:,} findings do not "
            "contain a specified preventive action."
        )

    pareto_table = analysis.pareto.table

    if len(pareto_table) >= 3:
        top_three = float(pareto_table.head(3)["percentage"].sum())

        st.markdown(
            "- The three most common preventive actions account for "
            f"{top_three:.2f}% of findings."
        )

    st.subheader("Management Considerations")

    st.markdown(
        "- Review whether recurring preventive actions are addressing systemic issues."
    )

    st.markdown("- Verify long-term effectiveness through follow-up audits.")

    st.markdown(
        "- Standardise preventive actions where recurring patterns are identified."
    )

    st.caption(
        "These observations are generated using deterministic "
        "rules from the displayed analytics."
    )


def _render_preventive_action_trends(
    analysis: PreventiveActionAnalysis,
) -> None:
    """Display preventive-action trend tables."""

    st.subheader("Preventive Action Trend Tables")

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
        "preventive action was implemented or verified."
    )


def render(description: str) -> None:
    """Render the Preventive Actions page."""

    render_page_header(
        "Preventive Actions",
        description,
    )

    cleaned_dataframe = st.session_state.get("cleaned_dataframe")

    if not isinstance(
        cleaned_dataframe,
        pd.DataFrame,
    ):
        st.warning(
            "Upload and validate an audit register before viewing Preventive Actions."
        )
        return

    try:
        with st.spinner("Generating preventive-action analytics..."):
            analysis = generate_preventive_action_analysis(cleaned_dataframe)
    except (
        KeyError,
        TypeError,
        ValueError,
    ) as error:
        st.error("Preventive Action Analysis could not be generated.")

        with st.expander("Technical details"):
            st.code(str(error))

        return

    _render_preventive_action_kpis(analysis)

    st.divider()
    _render_preventive_action_pareto(analysis)

    st.divider()
    _render_preventive_action_trends(analysis)

    st.divider()
    _render_preventive_action_observations(analysis)
