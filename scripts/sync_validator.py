"""
Synchronization Validator for EnergieRapport
Validates structural equivalence between JSX and HTML
"""

import re
import json
from pathlib import Path
from scripts.shared_data_extractor import DataExtractor


class SyncValidator:
    """Validate JSX-HTML synchronization"""

    def __init__(self):
        """Initialize validator with data extractor"""
        self.extractor = DataExtractor()
        self.errors = []

    def validate_sync(self, jsx_path: str, html_path: str) -> bool:
        """
        Validate that JSX and HTML are structurally equivalent

        Args:
            jsx_path: Path to EnergieRapport.jsx
            html_path: Path to offline.html

        Returns:
            True if perfectly synced, False if differences found
        """
        self.errors = []

        try:
            # 1. Extract data from JSX (source of truth)
            jsx_data = self.extractor.extract_from_jsx(jsx_path)
            self.extractor.validate(jsx_data)
        except Exception as e:
            self.errors.append(f"JSX validation failed: {e}")
            return False

        # 2. Read HTML
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # 3. Run validation checks
        print("🔍 Validating synchronization...")

        if not self._check_timestamp_match(jsx_path, html_path):
            self.errors.append("❌ Timestamps do not match between JSX and HTML")

        if not self._check_kpi_values_match(jsx_data, html_content):
            self.errors.append("❌ KPI values do not match")

        if not self._check_data_arrays_in_html(jsx_data, html_content):
            self.errors.append("❌ Data arrays missing or invalid in HTML")

        if not self._check_structural_integrity(jsx_path, html_path):
            self.errors.append("❌ Structural elements missing")

        if not self._check_complete_structure(jsx_path, html_path, jsx_data):
            self.errors.append("❌ Complete structure validation failed")

        return len(self.errors) == 0

    def _check_timestamp_match(self, jsx_path: str, html_path: str) -> bool:
        """Verify timestamps match"""
        with open(jsx_path, 'r', encoding='utf-8') as f:
            jsx_content = f.read()
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Extract timestamp from both: "MARKTANALYSE — 23 MAART 2026 · 20:30"
        jsx_match = re.search(
            r'MARKTANALYSE — (\d{2} \w+ \d{4}) · (\d{2}:\d{2})',
            jsx_content
        )
        html_match = re.search(
            r'MARKTANALYSE — (\d{2} \w+ \d{4}) · (\d{2}:\d{2})',
            html_content
        )

        if not jsx_match or not html_match:
            self.errors.append("  Could not extract timestamp from one or both files")
            return False

        jsx_timestamp = jsx_match.group(0)
        html_timestamp = html_match.group(0)

        match = jsx_timestamp == html_timestamp
        if not match:
            self.errors.append(f"  JSX: {jsx_timestamp}")
            self.errors.append(f"  HTML: {html_timestamp}")
        return match

    def _check_kpi_values_match(self, jsx_data, html_content: str) -> bool:
        """Verify KPI values in HTML match JSX"""
        all_match = True

        # Check TTF
        ttf_pattern = f"€{jsx_data.kpis['ttf']:.2f}"
        if ttf_pattern not in html_content:
            self.errors.append(f"  TTF value €{jsx_data.kpis['ttf']:.2f} not found in HTML")
            all_match = False

        # Check Belpex
        belpex_pattern = f"€{jsx_data.kpis['belpex']:.2f}"
        if belpex_pattern not in html_content:
            self.errors.append(f"  Belpex value €{jsx_data.kpis['belpex']:.2f} not found in HTML")
            all_match = False

        return all_match

    def _check_data_arrays_in_html(self, jsx_data, html_content: str) -> bool:
        """Verify marketData array exists and is valid JSON"""
        try:
            # Extract marketData array from HTML
            market_match = re.search(
                r'const marketData = (\[[\s\S]*?\]);',
                html_content
            )
            if not market_match:
                self.errors.append("  marketData array not found in HTML")
                return False

            market_json = market_match.group(1)
            parsed = json.loads(market_json)

            # Verify data matches
            if len(parsed) != len(jsx_data.price_history):
                self.errors.append(
                    f"  Data length mismatch: JSX={len(jsx_data.price_history)}, HTML={len(parsed)}"
                )
                return False

            # Verify at least first and last entries match
            if parsed[0]['ttf'] != jsx_data.price_history[0].ttf:
                self.errors.append(
                    f"  First entry TTF mismatch: JSX={jsx_data.price_history[0].ttf}, HTML={parsed[0]['ttf']}"
                )
                return False

            last_idx = len(parsed) - 1
            if parsed[last_idx]['ttf'] != jsx_data.price_history[last_idx].ttf:
                self.errors.append(
                    f"  Last entry TTF mismatch: JSX={jsx_data.price_history[last_idx].ttf}, HTML={parsed[last_idx]['ttf']}"
                )
                return False

            return True
        except json.JSONDecodeError as e:
            self.errors.append(f"  Invalid JSON in HTML: {e}")
            return False

    def _check_structural_integrity(self, jsx_path: str, html_path: str) -> bool:
        """Check critical structural elements present"""
        with open(jsx_path, 'r', encoding='utf-8') as f:
            jsx_content = f.read()
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # ESSENTIAL elements (not content-specific strings)
        # Only check for structural elements necessary for data synchronization
        critical_elements = [
            # KPI references (necessary for KPI values)
            "kpi", "KPI",
            # Data arrays (necessary for chart data)
            "marketData", "forecastBase", "forecastBull", "forecastBear",
            # Header timestamp
            "MARKTANALYSE",
        ]

        missing_elements = []
        for elem in critical_elements:
            if elem not in jsx_content:
                missing_elements.append(f"  JSX missing: {elem}")
            if elem not in html_content:
                missing_elements.append(f"  HTML missing: {elem}")

        if missing_elements:
            self.errors.extend(missing_elements)
            return False

        return True

    def _check_complete_structure(self, jsx_path: str, html_path: str, jsx_data) -> bool:
        """Verify complete HTML structure with all tabs, charts, and critical sections"""
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        structure_ok = True

        # Check all 5 tab panels present
        required_tabs = ['tab-analyse', 'tab-context', 'tab-forecast', 'tab-advies', 'tab-bronnen']
        for tab_id in required_tabs:
            if f'id="{tab_id}"' not in html_content:
                self.errors.append(f"  Missing tab panel: {tab_id}")
                structure_ok = False

        # Check canvas elements for charts
        required_canvases = ['ttf-chart', 'belpex-chart', 'forecast-chart']
        for canvas_id in required_canvases:
            if f'id="{canvas_id}"' not in html_content:
                self.errors.append(f"  Missing canvas element: {canvas_id}")
                structure_ok = False

        # Check KERNBOODSCHAP section (critical content)
        if 'Weloverwogen keuzen' not in html_content:
            self.errors.append("  KERNBOODSCHAP section missing from HTML")
            structure_ok = False

        # Check price table row count matches price history
        table_row_count = html_content.count('<tr ')
        expected_rows = len(jsx_data.price_history)
        # Account for header row (should have expected_rows + 1 total tr elements)
        if table_row_count < expected_rows:
            self.errors.append(
                f"  Price table row count mismatch: expected ~{expected_rows}, found {table_row_count - 1}"
            )
            structure_ok = False

        return structure_ok

    def report(self) -> str:
        """Generate validation report"""
        if not self.errors:
            return "✅ Synchronization verified — JSX and HTML are in perfect sync!"

        report = "❌ Synchronization validation FAILED\n"
        for error in self.errors:
            report += f"{error}\n"
        return report
