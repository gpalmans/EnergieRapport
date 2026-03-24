"""
JSX to HTML Compiler for EnergieRapport
Generates offline.html from JSX as derived artifact
"""

import json
from pathlib import Path
from dataclasses import asdict
from statistics import linear_regression
from scripts.shared_data_extractor import DataExtractor, EnergyReportData
from scripts.jsx_section_extractor import JsxSectionExtractor


class JsxToHtmlCompiler:
    """Compile JSX to standalone HTML"""

    def __init__(self):
        """Initialize compiler with data extractor and section extractor"""
        self.extractor = DataExtractor()
        self.section_extractor = JsxSectionExtractor()

    def _generate_price_table_rows(self, price_history) -> str:
        """
        Generate HTML table rows for price history with deltas, highlights, and badges.

        Args:
            price_history: List of PriceDataPoint objects

        Returns:
            HTML string with <tr> rows
        """
        rows = []
        for i, point in enumerate(price_history):
            # Calculate day-on-day % changes
            ttf_delta = ""
            belpex_delta = ""
            if i > 0:
                prev = price_history[i - 1]
                ttf_change = ((point.ttf - prev.ttf) / prev.ttf) * 100
                belpex_change = ((point.belpex - prev.belpex) / prev.belpex) * 100
                ttf_delta = f"{ttf_change:+.1f}%"
                belpex_delta = f"{belpex_change:+.1f}%"

            # Determine row classes
            row_class = ""
            if point.note == "Vandaag":
                row_class = 'class="today"'
            elif point.note in ["Hormuz", "Piek", "IEA"]:
                row_class = 'class="shock"'

            # Badge HTML for notes
            badge = ""
            if point.note:
                badge = f'<span class="badge badge-{point.note.lower()}">{point.note}</span>'

            row_html = f"""    <tr {row_class}>
      <td>{point.date}</td>
      <td>€{point.ttf:.2f}</td>
      <td>{ttf_delta}</td>
      <td>€{point.belpex:.2f}</td>
      <td>{belpex_delta}</td>
      <td>{badge}</td>
    </tr>"""
            rows.append(row_html)

        return "\n".join(rows)

    def _compute_trendlines(self, price_history) -> str:
        """
        Compute linear regression trendlines for TTF and Belpex.

        Args:
            price_history: List of PriceDataPoint objects

        Returns:
            JSON string with trendline data for all points and short-term (last 7)
        """
        trendlines = {
            'ttf_medium': [],
            'belpex_medium': [],
            'ttf_short': [],
            'belpex_short': []
        }

        if not price_history or len(price_history) < 2:
            return json.dumps(trendlines)

        # Medium trendline: all data points
        xs = list(range(len(price_history)))
        ttf_ys = [p.ttf for p in price_history]
        belpex_ys = [p.belpex for p in price_history]

        try:
            ttf_slope, ttf_intercept = linear_regression(xs, ttf_ys)
            belpex_slope, belpex_intercept = linear_regression(xs, belpex_ys)

            for i, point in enumerate(price_history):
                trendlines['ttf_medium'].append({
                    'date': point.date,
                    'value': round(ttf_intercept + ttf_slope * i, 2)
                })
                trendlines['belpex_medium'].append({
                    'date': point.date,
                    'value': round(belpex_intercept + belpex_slope * i, 2)
                })

            # Short trendline: last 7 points projected over all
            if len(price_history) >= 7:
                short_data = price_history[-7:]
                short_xs = list(range(len(short_data)))
                short_ttf_ys = [p.ttf for p in short_data]
                short_belpex_ys = [p.belpex for p in short_data]

                ttf_short_slope, ttf_short_intercept = linear_regression(short_xs, short_ttf_ys)
                belpex_short_slope, belpex_short_intercept = linear_regression(short_xs, short_belpex_ys)

                # Project over all points
                for i, point in enumerate(price_history):
                    # Map point index to position relative to last 7
                    relative_pos = i - (len(price_history) - 7)
                    trendlines['ttf_short'].append({
                        'date': point.date,
                        'value': round(ttf_short_intercept + ttf_short_slope * relative_pos, 2)
                    })
                    trendlines['belpex_short'].append({
                        'date': point.date,
                        'value': round(belpex_short_intercept + belpex_short_slope * relative_pos, 2)
                    })
        except:
            # Fallback if regression fails
            pass

        return json.dumps(trendlines)

    def compile(self, jsx_path: str, template_path: str, output_path: str) -> bool:
        """
        Compile JSX → Extract Data → Render HTML

        Args:
            jsx_path: Path to EnergieRapport.jsx
            template_path: Path to HTML template
            output_path: Where to write compiled HTML

        Returns:
            True if successful, False if failed
        """
        try:
            # 1. Extract structured data from JSX
            print(f"📖 Extracting data from JSX: {jsx_path}")
            data = self.extractor.extract_from_jsx(jsx_path)
            self.extractor.validate(data)
            print(f"   ✓ Extracted: {len(data.price_history)} price points, {len(data.forecast_base)} forecast scenarios")

            # 1b. Load raw JSX content for section extraction
            with open(jsx_path, 'r', encoding='utf-8') as f:
                jsx_content_str = f.read()

            # 2. Load HTML template
            print(f"📄 Loading template: {template_path}")
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()

            # 3. Prepare JSON data for embedding
            print("🔄 Preparing data for HTML embedding...")
            market_data_json = json.dumps([
                {
                    'date': p.date,
                    'ttf': p.ttf,
                    'belpex': p.belpex,
                    'note': p.note
                }
                for p in data.price_history
            ])

            forecast_base_json = json.dumps([
                {'date': p.date, 'ttf': p.ttf, 'belpex': p.belpex}
                for p in data.forecast_base
            ])

            forecast_bull_json = json.dumps([
                {'date': p.date, 'ttf': p.ttf, 'belpex': p.belpex}
                for p in data.forecast_bull
            ])

            forecast_bear_json = json.dumps([
                {'date': p.date, 'ttf': p.ttf, 'belpex': p.belpex}
                for p in data.forecast_bear
            ])

            # Generate price table rows and trendlines
            print("📊 Generating price table rows and trendlines...")
            price_table_rows = self._generate_price_table_rows(data.price_history)
            chart_trendlines_json = self._compute_trendlines(data.price_history)

            # 4. Render HTML by string substitution
            print("✨ Rendering HTML from template...")
            html_output = template_content

            # Replace placeholders
            html_output = html_output.replace('{{ report_date_upper }}', data.report_date.upper())
            html_output = html_output.replace('{{ report_time }}', data.report_time)
            html_output = html_output.replace('{{ month_year }}', data.report_date)
            html_output = html_output.replace('{{ report_date }}', data.report_date)

            # KPI values
            html_output = html_output.replace('{{ kpis_ttf }}', f"{data.kpis['ttf']:.2f}")
            html_output = html_output.replace('{{ kpis_belpex }}', f"{data.kpis['belpex']:.2f}")
            html_output = html_output.replace('{{ kpis_storage }}', f"{int(data.kpis.get('storage', 0))}")
            html_output = html_output.replace('{{ kpis_brent }}', f"{data.kpis.get('brent', 0):.2f}")

            # KPI delta labels
            html_output = html_output.replace('{{ kpis_ttf_delta }}', data.kpi_deltas.get('ttf_delta', ''))
            html_output = html_output.replace('{{ kpis_belpex_delta }}', data.kpi_deltas.get('belpex_delta', ''))
            html_output = html_output.replace('{{ kpis_storage_note }}', data.kpi_deltas.get('storage_note', ''))
            html_output = html_output.replace('{{ kpis_brent_delta }}', data.kpi_deltas.get('brent_delta', ''))

            # Alert banner
            html_output = html_output.replace('{{ alert_banner_title }}', data.alert_banner_title)
            html_output = html_output.replace('{{ alert_banner_text }}', data.alert_banner_text)

            # Data arrays (must be valid JSON)
            html_output = html_output.replace('{{ market_data_json }}', market_data_json)
            html_output = html_output.replace('{{ forecast_base_json }}', forecast_base_json)
            html_output = html_output.replace('{{ forecast_bull_json }}', forecast_bull_json)
            html_output = html_output.replace('{{ forecast_bear_json }}', forecast_bear_json)

            # Price table and trendlines
            html_output = html_output.replace('{{ price_table_rows }}', price_table_rows)
            html_output = html_output.replace('{{ chart_trendlines_json }}', chart_trendlines_json)

            # Dynamic tab sections extracted from JSX prose
            print("🔤 Rendering dynamic tab sections from JSX...")
            html_output = html_output.replace(
                '{{ section_context }}',
                self.section_extractor.render_context_section(jsx_content_str)
            )
            html_output = html_output.replace(
                '{{ section_forecast }}',
                self.section_extractor.render_forecast_section(jsx_content_str)
            )
            html_output = html_output.replace(
                '{{ section_advies }}',
                self.section_extractor.render_advies_section(jsx_content_str)
            )
            html_output = html_output.replace(
                '{{ section_bronnen }}',
                self.section_extractor.render_bronnen_section(jsx_content_str)
            )

            # 5. Write output
            print(f"💾 Writing compiled HTML: {output_path}")
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_output)

            print(f"✅ Successfully compiled HTML ({len(html_output)} bytes)")
            return True

        except Exception as e:
            print(f"❌ Compilation failed: {e}")
            return False
