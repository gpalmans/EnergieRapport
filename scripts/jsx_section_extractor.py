"""
JSX Section Extractor — Main Interface
Provides a JsxSectionExtractor class that renders all four dynamic tab sections
(context, forecast, advies, bronnen) from JSX source to HTML strings.

Each section renderer:
  1. Locates the section in JSX using comment markers
  2. Extracts data arrays and prose text via regex + bracket-counting
  3. Renders HTML using the same CSS classes as energy_report_template.html

Renders are split across four submodules to keep each file under 500 lines:
  - jsx_section_extractor_context.py
  - jsx_section_extractor_forecast.py
  - jsx_section_extractor_advies.py
  - jsx_section_extractor_bronnen.py
"""

from scripts.jsx_section_extractor_context import render_context_section
from scripts.jsx_section_extractor_forecast import render_forecast_section
from scripts.jsx_section_extractor_advies import render_advies_section
from scripts.jsx_section_extractor_bronnen import render_bronnen_section


class JsxSectionExtractor:
    """
    Extracts and renders all four dynamic tab sections from JSX source.

    Usage:
        extractor = JsxSectionExtractor()
        html = extractor.render_context_section(jsx_content_str)
    """

    def render_context_section(self, jsx_content: str) -> str:
        """
        Render the Geopolitiek/Context tab section from JSX.

        Args:
            jsx_content: Full JSX source string

        Returns:
            HTML string for the tab-context panel content
        """
        return render_context_section(jsx_content)

    def render_forecast_section(self, jsx_content: str) -> str:
        """
        Render the Forecast tab section from JSX.

        Args:
            jsx_content: Full JSX source string

        Returns:
            HTML string for the tab-forecast panel content
        """
        return render_forecast_section(jsx_content)

    def render_advies_section(self, jsx_content: str) -> str:
        """
        Render the Advies tab section from JSX.

        Args:
            jsx_content: Full JSX source string

        Returns:
            HTML string for the tab-advies panel content
        """
        return render_advies_section(jsx_content)

    def render_bronnen_section(self, jsx_content: str) -> str:
        """
        Render the Bronnen tab section from JSX.

        Args:
            jsx_content: Full JSX source string

        Returns:
            HTML string for the tab-bronnen panel content
        """
        return render_bronnen_section(jsx_content)
