"""
JSX to HTML Compiler for EnergieRapport
Generates offline.html from JSX as derived artifact
"""

import json
from pathlib import Path
from dataclasses import asdict
from scripts.shared_data_extractor import DataExtractor, EnergyReportData


class JsxToHtmlCompiler:
    """Compile JSX to standalone HTML"""

    def __init__(self):
        """Initialize compiler with data extractor"""
        self.extractor = DataExtractor()

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

            # Data arrays (must be valid JSON)
            html_output = html_output.replace('{{ market_data_json }}', market_data_json)
            html_output = html_output.replace('{{ forecast_base_json }}', forecast_base_json)
            html_output = html_output.replace('{{ forecast_bull_json }}', forecast_bull_json)
            html_output = html_output.replace('{{ forecast_bear_json }}', forecast_bear_json)

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
