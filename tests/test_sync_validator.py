"""
Tests for SyncValidator
"""

import pytest
from pathlib import Path
from scripts.sync_validator import SyncValidator
from scripts.jsx_to_html_compiler import JsxToHtmlCompiler


class TestSyncValidator:
    """Test synchronization validation"""

    @pytest.fixture
    def validator(self):
        """Create validator instance"""
        return SyncValidator()

    @pytest.fixture
    def compiler(self):
        """Create compiler instance"""
        return JsxToHtmlCompiler()

    @pytest.fixture
    def compiled_html_path(self, compiler):
        """Compile HTML for testing"""
        output_path = Path('/tmp/test_compiled_for_validation.html')
        compiler.compile(
            'src/EnergieRapport.jsx',
            'templates/energy_report_template.html',
            str(output_path)
        )
        return output_path

    def test_validator_passes_for_compiled_html(self, validator, compiled_html_path):
        """After compilation, validation should pass"""
        is_synced = validator.validate_sync(
            'src/EnergieRapport.jsx',
            str(compiled_html_path)
        )

        print(validator.report())
        assert is_synced, "Compiled HTML should pass synchronization validation"

    def test_validator_report_on_success(self, validator, compiled_html_path):
        """Validation report should indicate success"""
        validator.validate_sync(
            'src/EnergieRapport.jsx',
            str(compiled_html_path)
        )

        report = validator.report()
        assert "✅" in report or "perfect sync" in report.lower()

    def test_validator_detects_missing_kpi(self, validator, compiled_html_path):
        """Validator should detect if KPI value is missing"""
        # Read compiled HTML
        with open(compiled_html_path, 'r', encoding='utf-8') as f:
            html = f.read()

        # Remove a KPI value
        html_modified = html.replace("€60.60", "€00.00")

        # Write modified HTML
        modified_path = Path('/tmp/test_modified_html.html')
        with open(modified_path, 'w', encoding='utf-8') as f:
            f.write(html_modified)

        # Validation should fail
        is_synced = validator.validate_sync(
            'src/EnergieRapport.jsx',
            str(modified_path)
        )

        assert is_synced is False, "Validator should detect KPI mismatch"

    def test_validator_detects_missing_data_arrays(self, validator, compiled_html_path):
        """Validator should detect if data arrays are missing"""
        # Read compiled HTML
        with open(compiled_html_path, 'r', encoding='utf-8') as f:
            html = f.read()

        # Remove marketData array
        html_modified = html.replace("const marketData = ", "const marketDataOld = ")

        # Write modified HTML
        modified_path = Path('/tmp/test_missing_array.html')
        with open(modified_path, 'w', encoding='utf-8') as f:
            f.write(html_modified)

        # Validation should fail
        is_synced = validator.validate_sync(
            'src/EnergieRapport.jsx',
            str(modified_path)
        )

        assert is_synced is False, "Validator should detect missing marketData"

    def test_validator_checks_timestamp(self, validator, compiled_html_path):
        """Validator should verify timestamps match"""
        # Read compiled HTML
        with open(compiled_html_path, 'r', encoding='utf-8') as f:
            html = f.read()

        # Change timestamp in HTML
        html_modified = html.replace("23 maart", "22 maart")

        # Write modified HTML
        modified_path = Path('/tmp/test_timestamp_mismatch.html')
        with open(modified_path, 'w', encoding='utf-8') as f:
            f.write(html_modified)

        # Validation should fail
        is_synced = validator.validate_sync(
            'src/EnergieRapport.jsx',
            str(modified_path)
        )

        assert is_synced is False, "Validator should detect timestamp mismatch"
