"""Severity-analysis page."""

import pandas as pd
import streamlit as st

from src.analytics.severity_engine import (
    generate_severity_analysis,
)
from src.models.severity_analysis import SeverityAnalysis
from src.ui.charts import (
    build_monthly_workload_chart,
    build_pareto_chart,
)
from src.ui.components import (
    render_kpi_cards,
    render_page_header,
)


def _render_severity_kpis(
    analysis: SeverityAnalysis,
) -> None:
    """Display severity counts and percentages."""

    render_kpi_cards(
        [
            (
                "Total Findings",
                analysis.total_findings,
                "Total number of findings in the current dataset.",
            ),
            (
                "Major",
                analysis.major_count,
                f"{analysis.major_percentage:.2f}% of findings.",
            ),
            (
                "Minor",
                analysis.minor_count,
                f"{analysis.minor_percentage:.2f}% of findings.",
            ),
            (
                "Observations",
                analysis.observation_count,
                f"{analysis.observation_percentage:.2f}% of findings.",
            ),
            (
                "Unspecified",
                analysis.unspecified_count,
                f"{analysis.unspecified_percentage:.2f}% of findings.",
            ),
            (
                "Latest Monthly Change",
                (
                    analysis.latest_month_total_change
                    if analysis.latest_month_total_change is not None
                    else "N/A"
                ),
                "Change in total findings between the latest two months.",
            ),
            (
                "Latest Major Change",
                (
                    analysis.latest_month_major_change
                    if analysis.latest_month_major_change is not None
                    else "N/A"
                ),
                "Change in Major findings between the latest two months.",
            ),
        ],
        columns_per_row=4,
    )


def _render_severity_charts(
    analysis: SeverityAnalysis,
) -> None:
    """Display severity Pareto and trend charts."""

    first_column, second_column = st.columns(2)

    with first_column:
        st.subheader("Severity Pareto")

        if analysis.pareto.table.empty:
            st.info("No severity data is available.")
        else:
            chart = build_pareto_chart(
                analysis.pareto.table,
                title="Severity Distribution and Cumulative Percentage",
            )

            st.altair_chart(
                chart,
                use_container_width=True,
            )

            with st.expander("View severity Pareto table"):
                st.dataframe(
                    analysis.pareto.table,
                    use_container_width=True,
                    hide_index=True,
                )

    with second_column:
        st.subheader("Monthly severity workload")

        if analysis.monthly_trend.empty:
            st.info(
                "No valid response due dates are available "
                "for monthly severity analysis."
            )
        else:
            chart = build_monthly_workload_chart(
                analysis.monthly_trend,
                title="Severity by Response Due Month",
            )

            st.altair_chart(
                chart,
                use_container_width=True,
            )

            with st.expander("View monthly severity table"):
                st.dataframe(
                    analysis.monthly_trend,
                    use_container_width=True,
                    hide_index=True,
                )

    st.caption(
        "Trend note: monthly, quarterly, and yearly severity trends "
        "use response_due_date. They represent response workload rather "
        "than the date each finding originally occurred."
    )


def _render_period_tables(
    analysis: SeverityAnalysis,
) -> None:
    """Display monthly, quarterly, and yearly severity tables."""

    st.subheader("Trend tables")

    monthly_tab, quarterly_tab, yearly_tab = st.tabs(
        [
            "Monthly",
            "Quarterly",
            "Yearly",
        ]
    )

    with monthly_tab:
        st.dataframe(
            analysis.monthly_trend,
            use_container_width=True,
            hide_index=True,
        )

    with quarterly_tab:
        st.dataframe(
            analysis.quarterly_trend,
            use_container_width=True,
            hide_index=True,
        )

    with yearly_tab:
        st.dataframe(
            analysis.yearly_trend,
            use_container_width=True,
            hide_index=True,
        )


def _render_severity_observations(
    analysis: SeverityAnalysis,
) -> None:
    """Display deterministic severity observations."""

    st.subheader("Severity observations")

    severity_counts = {
        "Major": analysis.major_count,
        "Minor": analysis.minor_count,
        "Observation": analysis.observation_count,
        "Unspecified": analysis.unspecified_count,
    }

    severity_percentages = {
        "Major": analysis.major_percentage,
        "Minor": analysis.minor_percentage,
        "Observation": analysis.observation_percentage,
        "Unspecified": analysis.unspecified_percentage,
    }

    leading_severity = max(
        severity_counts,
        key=severity_counts.__getitem__,
    )

    st.markdown(
        f"- {leading_severity} is the largest severity category, "
        f"with {severity_counts[leading_severity]:,} findings "
        f"({severity_percentages[leading_severity]:.2f}%)."
    )

    if analysis.major_count > 0:
        st.markdown(
            f"- Major findings represent "
            f"{analysis.major_percentage:.2f}% of all findings."
        )

    pareto_table = analysis.pareto.table

    if len(pareto_table) >= 2:
        top_two_percentage = float(pareto_table.head(2)["percentage"].sum())

        st.markdown(
            "- The two largest severity categories account for "
            f"{top_two_percentage:.2f}% of all findings."
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


def render(description: str) -> None:
    """Render the Severity Analysis page."""

    render_page_header(
        "Severity Analysis",
        description,
    )

    cleaned_dataframe = st.session_state.get("cleaned_dataframe")

    if not isinstance(
        cleaned_dataframe,
        pd.DataFrame,
    ):
        st.warning(
            "Upload and validate an audit register before viewing Severity Analysis."
        )
        return

    try:
        with st.spinner("Generating severity analytics..."):
            analysis = generate_severity_analysis(cleaned_dataframe)
    except (
        KeyError,
        TypeError,
        ValueError,
    ) as error:
        st.error("Severity Analysis could not be generated.")

        with st.expander("Technical details"):
            st.code(str(error))

        return

    _render_severity_kpis(analysis)

    st.divider()
    _render_severity_charts(analysis)

    st.divider()
    _render_period_tables(analysis)

    st.divider()
    _render_severity_observations(analysis)
