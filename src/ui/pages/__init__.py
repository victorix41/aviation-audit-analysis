"""Page registry for the Streamlit application."""

from collections.abc import Callable

from src.ui.pages.corrective_actions import render as render_corrective_actions
from src.ui.pages.data_quality import render as render_data_quality
from src.ui.pages.data_upload import render as render_data_upload
from src.ui.pages.executive_overview import render as render_executive_overview
from src.ui.pages.human_factors import render as render_human_factors
from src.ui.pages.preventive_actions import render as render_preventive_actions
from src.ui.pages.reports import render as render_reports
from src.ui.pages.root_causes import render as render_root_causes
from src.ui.pages.severity import render as render_severity

PageRenderer = Callable[[str], None]

PAGE_RENDERERS: dict[str, PageRenderer] = {
    "Data Upload": render_data_upload,
    "Executive Overview": render_executive_overview,
    "Severity Analysis": render_severity,
    "Human Factors": render_human_factors,
    "Root Causes": render_root_causes,
    "Corrective Actions": render_corrective_actions,
    "Preventive Actions": render_preventive_actions,
    "Data Quality": render_data_quality,
    "Reports": render_reports,
}
