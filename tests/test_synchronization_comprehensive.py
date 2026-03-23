"""
Comprehensive synchronization tests - end-to-end workflow
"""

import pytest
from pathlib import Path
from scripts.shared_data_extractor import DataExtractor
from scripts.jsx_to_html_compiler import JsxToHtmlCompiler
from scripts.sync_validator import SyncValidator


class TestSynchronizationPipeline:
    """Test the complete synchronization pipeline"""

    @pytest.fixture
    def extractor(self):
        return DataExtractor()

    @pytest.fixture
    def compiler(self):
        return JsxToHtmlCompiler()

    @pytest.fixture
    def validator(self):
        return SyncValidator()

    def test_full_pipeline_jsx_to_validated_html(self, extractor, compiler, validator):
        """Test complete pipeline: JSX → Extract → Compile → Validate"""
        output_html = Path('/tmp/final_test_output.html')

        # Step 1: Extract from JSX
        data = extractor.extract_from_jsx('src/EnergieRapport.jsx')
        assert extractor.validate(data) is True

        # Step 2: Compile to HTML
        success = compiler.compile(
            'src/EnergieRapport.jsx',
            'templates/energy_report_template.html',
            str(output_html)
        )
        assert success is True
        assert output_html.exists()

        # Step 3: Validate synchronization
        is_synced = validator.validate_sync(
            'src/EnergieRapport.jsx',
            str(output_html)
        )
        assert is_synced is True

    def test_extracted_data_structure_valid(self, extractor):
        """Extracted data should have valid structure"""
        data = extractor.extract_from_jsx('src/EnergieRapport.jsx')

        # All required fields present
        assert hasattr(data, 'report_date')
        assert hasattr(data, 'report_time')
        assert hasattr(data, 'price_history')
        assert hasattr(data, 'forecast_base')
        assert hasattr(data, 'forecast_bull')
        assert hasattr(data, 'forecast_bear')
        assert hasattr(data, 'kpis')
        assert hasattr(data, 'alert_banner')

    def test_compiler_output_is_valid_html(self, compiler):
        """Compiled HTML should be valid"""
        output = Path('/tmp/test_html_validity.html')
        compiler.compile(
            'src/EnergieRapport.jsx',
            'templates/energy_report_template.html',
            str(output)
        )

        with open(output, 'r', encoding='utf-8') as f:
            html = f.read()

        # Basic HTML structure
        assert html.startswith('<!DOCTYPE html>')
        assert '<html' in html
        assert '</html>' in html
        assert '<script>' in html or '<script' in html

    def test_validator_strict_checks(self, compiler, validator):
        """Validator should catch any desynchronization"""
        output = Path('/tmp/test_strict_validation.html')
        compiler.compile(
            'src/EnergieRapport.jsx',
            'templates/energy_report_template.html',
            str(output)
        )

        # Original should validate
        is_synced = validator.validate_sync(
            'src/EnergieRapport.jsx',
            str(output)
        )
        assert is_synced is True

        # Check the report is clean
        report = validator.report()
        assert "✅" in report or "perfect sync" in report.lower()

    def test_integration_error_handling(self, extractor):
        """Integration should handle errors gracefully"""
        # Non-existent file
        with pytest.raises(Exception):
            extractor.extract_from_jsx('nonexistent.jsx')

    def test_data_consistency_across_pipeline(self, extractor, compiler):
        """Data should remain consistent through extraction and compilation"""
        # Extract
        data = extractor.extract_from_jsx('src/EnergieRapport.jsx')
        original_ttf = data.kpis['ttf']
        original_belpex = data.kpis['belpex']

        # Compile
        output = Path('/tmp/test_consistency.html')
        compiler.compile(
            'src/EnergieRapport.jsx',
            'templates/energy_report_template.html',
            str(output)
        )

        # Verify in output HTML
        with open(output, 'r', encoding='utf-8') as f:
            html = f.read()

        ttf_str = f"{original_ttf:.2f}"
        belpex_str = f"{original_belpex:.2f}"

        assert ttf_str in html, f"TTF {ttf_str} should be in compiled HTML"
        assert belpex_str in html, f"Belpex {belpex_str} should be in compiled HTML"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
