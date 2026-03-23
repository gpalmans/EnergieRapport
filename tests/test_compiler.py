"""
Tests for JSX-to-HTML Compiler
"""

import pytest
import json
from pathlib import Path
from scripts.jsx_to_html_compiler import JsxToHtmlCompiler


class TestJsxToHtmlCompiler:
    """Test JSX to HTML compilation"""

    @pytest.fixture
    def compiler(self):
        """Create compiler instance"""
        return JsxToHtmlCompiler()

    @pytest.fixture
    def test_output_path(self):
        """Temporary output path for compiled HTML"""
        return Path('/tmp/test_compiled_energy_report.html')

    def test_compilation_succeeds(self, compiler, test_output_path):
        """Test that HTML compilation succeeds"""
        result = compiler.compile(
            'src/EnergieRapport.jsx',
            'templates/energy_report_template.html',
            str(test_output_path)
        )

        assert result is True, "Compilation should succeed"
        assert test_output_path.exists(), "Output file should be created"

    def test_compiled_html_contains_critical_elements(self, compiler, test_output_path):
        """Test that compiled HTML has critical elements"""
        compiler.compile(
            'src/EnergieRapport.jsx',
            'templates/energy_report_template.html',
            str(test_output_path)
        )

        with open(test_output_path, 'r', encoding='utf-8') as f:
            html = f.read()

        # Critical sections must exist
        assert 'MARKTANALYSE' in html
        assert 'TTF Gas vandaag' in html
        assert 'Belpex' in html
        assert 'const marketData' in html

    def test_compiled_html_has_valid_json_arrays(self, compiler, test_output_path):
        """Test that compiled HTML contains valid JSON arrays"""
        compiler.compile(
            'src/EnergieRapport.jsx',
            'templates/energy_report_template.html',
            str(test_output_path)
        )

        with open(test_output_path, 'r', encoding='utf-8') as f:
            html = f.read()

        # Extract and validate marketData array
        for array_name in ['marketData', 'forecastBase', 'forecastBull', 'forecastBear']:
            pattern = f'const {array_name} = '
            assert pattern in html, f"{array_name} not found in HTML"

            # Find the JSON
            start_idx = html.find(pattern) + len(pattern)
            end_idx = html.find(';', start_idx)
            json_str = html[start_idx:end_idx]

            try:
                parsed = json.loads(json_str)
                assert len(parsed) > 0, f"{array_name} should not be empty"
                assert isinstance(parsed, list), f"{array_name} should be an array"
            except json.JSONDecodeError as e:
                pytest.fail(f"Invalid JSON in {array_name}: {e}")

    def test_kpi_values_are_numeric(self, compiler, test_output_path):
        """Test that KPI values are properly formatted as numbers"""
        compiler.compile(
            'src/EnergieRapport.jsx',
            'templates/energy_report_template.html',
            str(test_output_path)
        )

        with open(test_output_path, 'r', encoding='utf-8') as f:
            html = f.read()

        # KPI values should be numeric patterns like "€60.60" or "$112"
        import re

        # Look for TTF KPI
        ttf_match = re.search(r'TTF Gas vandaag.*?€([\d.]+)', html, re.DOTALL)
        assert ttf_match is not None, "TTF KPI should be in HTML"
        ttf_value = float(ttf_match.group(1))
        assert 0 < ttf_value < 200, "TTF value should be reasonable"

        # Look for Belpex KPI
        belpex_match = re.search(r'Belpex.*?€([\d.]+)', html, re.DOTALL)
        assert belpex_match is not None, "Belpex KPI should be in HTML"
        belpex_value = float(belpex_match.group(1))
        assert 0 < belpex_value < 300, "Belpex value should be reasonable"

    def test_timestamp_is_present(self, compiler, test_output_path):
        """Test that report timestamp is included"""
        compiler.compile(
            'src/EnergieRapport.jsx',
            'templates/energy_report_template.html',
            str(test_output_path)
        )

        with open(test_output_path, 'r', encoding='utf-8') as f:
            html = f.read()

        # Should have timestamp pattern like "MARKTANALYSE — 23 MAART 2026 · 20:30"
        import re
        timestamp_match = re.search(r'MARKTANALYSE — \d{2} \w+ \d{4} · \d{2}:\d{2}', html)
        assert timestamp_match is not None, "Timestamp should be in HTML"
