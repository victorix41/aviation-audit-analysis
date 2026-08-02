"""Human-factor analysis page."""

import pandas as pd
import streamlit as st

from src.analytics.human_factor_engine import (
    generate_human_factor_analysis,
)
from src.models.human_factor_analysis import HumanFactorAnalysis
from src.ui.charts import build_pareto_chart
from src.ui.components import (
    render_kpi_cards,
    render_page_header,
)


def _render_human_factor_kpis(
    analysis: HumanFactorAnalysis,
) -> None:
    """Display human-factor KPI cards."""

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
                "Unique Human Factors",
                analysis.unique_human_factors,
                "Number of distinct specified human-factor categories.",
            ),
            (
                "Leading Human Factor",
                analysis.top_factor or "N/A",
                (
                    f"{analysis.top_factor_frequency:,} findings "
                    f"({analysis.top_factor_percentage:.2f}%)."
                    if analysis.top_factor is not None
                    else "No leading human factor is available."
                ),
            ),
            (
                "Latest Monthly Change",
                (
                    analysis.latest_month_total_change
                    if analysis.latest_month_total_change is not None
                    else "N/A"
                ),
                "Change in total human-factor records between the latest two months.",
            ),
            (
                "Latest Quarterly Change",
                (
                    analysis.latest_quarter_total_change
                    if analysis.latest_quarter_total_change is not None
                    else "N/A"
                ),
                "Change in total human-factor records between the latest two quarters.",
            ),
            (
                "Latest Yearly Change",
                (
                    analysis.latest_year_total_change
                    if analysis.latest_year_total_change is not None
                    else "N/A"
                ),
                "Change in total human-factor records between the latest two years.",
            ),
        ],
        columns_per_row=4,
    )


def _render_human_factor_pareto(
    analysis: HumanFactorAnalysis,
) -> None:
    """Display the human-factor Pareto chart and table."""

    st.subheader("Human Factor Pareto")

    pareto_table = analysis.pareto.table

    if pareto_table.empty:
        st.info("No human-factor data is available for Pareto analysis.")
        return

    chart = build_pareto_chart(
        pareto_table,
        title="Human Factor Distribution and Cumulative Percentage",
    )

    st.altair_chart(
        chart,
        use_container_width=True,
    )

    with st.expander("View human-factor Pareto table"):
        st.dataframe(
            pareto_table,
            use_container_width=True,
            hide_index=True,
        )


def _render_human_factor_trends(
    analysis: HumanFactorAnalysis,
) -> None:
    """Display monthly, quarterly, and yearly trend tables."""

    st.subheader("Human Factor Trend Tables")

    monthly_tab, quarterly_tab, yearly_tab = st.tabs(
        [
            "Monthly",
            "Quarterly",
            "Yearly",
        ]
    )

    with monthly_tab:
        if analysis.monthly_trend.empty:
            st.info("No valid response due dates are available for monthly analysis.")
        else:
            st.dataframe(
                analysis.monthly_trend,
                use_container_width=True,
                hide_index=True,
            )

    with quarterly_tab:
        if analysis.quarterly_trend.empty:
            st.info("No valid response due dates are available for quarterly analysis.")
        else:
            st.dataframe(
                analysis.quarterly_trend,
                use_container_width=True,
                hide_index=True,
            )

    with yearly_tab:
        if analysis.yearly_trend.empty:
            st.info("No valid response due dates are available for yearly analysis.")
        else:
            st.dataframe(
                analysis.yearly_trend,
                use_container_width=True,
                hide_index=True,
            )

    st.caption(
        "Trend note: these tables group findings by response_due_date. "
        "They represent response workload, not the date each finding originally occurred."
    )


def _render_human_factor_observations(
    analysis: HumanFactorAnalysis,
) -> None:
    """Display deterministic observations and considerations."""

    st.subheader("Human Factor Observations")

    if analysis.top_factor is None:
        st.info("No human-factor observations are available.")
        return

    st.markdown(
        f"- {analysis.top_factor} is the leading recorded human factor, "
        f"appearing in {analysis.top_factor_frequency:,} findings "
        f"({analysis.top_factor_percentage:.2f}%)."
    )

    st.markdown(
        f"- {analysis.specified_percentage:.2f}% of findings include "
        "a specified human factor."
    )

    if analysis.unspecified_findings > 0:
        st.markdown(
            f"- {analysis.unspecified_findings:,} findings do not contain "
            "a specified human factor."
        )

    pareto_table = analysis.pareto.table

    if len(pareto_table) >= 3:
        top_three_percentage = float(pareto_table.head(3)["percentage"].sum())

        st.markdown(
            "- The three most frequent human factors account for "
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
        f"- Review whether targeted controls, communication, supervision, "
        f"or training could address the recurring human factor: "
        f"{analysis.top_factor}."
    )

    if analysis.unspecified_findings > 0:
        st.markdown(
            "- Improve completion and consistency of human-factor classification "
            "to support more reliable trend analysis."
        )

    if len(pareto_table) >= 3:
        st.markdown(
            "- Focus initial improvement efforts on the most frequent human-factor "
            "categories before addressing lower-frequency categories."
        )

    st.caption(
        "These observations and considerations are generated using deterministic "
        "rules from the displayed analytics."
    )


def render(description: str) -> None:
    """Render the Human Factors page."""

    render_page_header(
        "Human Factors",
        description,
    )

    cleaned_dataframe = st.session_state.get("cleaned_dataframe")

    if not isinstance(
        cleaned_dataframe,
        pd.DataFrame,
    ):
        st.warning(
            "Upload and validate an audit register before viewing Human Factors."
        )
        return

    try:
        with st.spinner("Generating human-factor analytics..."):
            analysis = generate_human_factor_analysis(cleaned_dataframe)
    except (
        KeyError,
        TypeError,
        ValueError,
    ) as error:
        st.error("Human Factor Analysis could not be generated.")

        with st.expander("Technical details"):
            st.code(str(error))

        return

    _render_human_factor_kpis(analysis)

    st.divider()
    _render_human_factor_pareto(analysis)

    st.divider()
    _render_human_factor_trends(analysis)

    st.divider()
    _render_human_factor_observations(analysis)
