"""
Tests for DataExtractor - verifies JSX parsing and data extraction
"""

import pytest
from pathlib import Path
from scripts.shared_data_extractor import DataExtractor


class TestDataExtractor:
    """Test JSX data extraction"""

    @pytest.fixture
    def extractor(self):
        """Create a DataExtractor instance"""
        return DataExtractor()

    def test_extract_from_jsx_complete(self, extractor):
        """Test that all data extracts successfully from JSX"""
        jsx_path = '../../../src/EnergieRapport.jsx'

        if not Path(jsx_path).exists():
            pytest.skip(f"JSX file not found at {jsx_path}")

        data = extractor.extract_from_jsx(jsx_path)

        # Verify all required fields are present
        assert data.report_date is not None
        assert data.report_time is not None
        assert len(data.price_history) >= 20
        assert len(data.forecast_base) >= 5
        assert len(data.forecast_bull) >= 5
        assert len(data.forecast_bear) >= 5
        assert len(data.kpis) >= 2  # At minimum ttf and belpex

    def test_extract_report_date_format(self, extractor):
        """Test that report date is properly formatted"""
        jsx_path = '../../../src/EnergieRapport.jsx'

        if not Path(jsx_path).exists():
            pytest.skip(f"JSX file not found at {jsx_path}")

        data = extractor.extract_from_jsx(jsx_path)

        # Should be format like "23 maart 2026"
        parts = data.report_date.split()
        assert len(parts) == 3
        assert parts[0].isdigit()  # Day
        assert len(parts[1]) > 0  # Month name in lowercase
        assert parts[2].isdigit()  # Year

    def test_extract_report_time_format(self, extractor):
        """Test that report time is properly formatted"""
        jsx_path = '../../../src/EnergieRapport.jsx'

        if not Path(jsx_path).exists():
            pytest.skip(f"JSX file not found at {jsx_path}")

        data = extractor.extract_from_jsx(jsx_path)

        # Should be format like "20:30"
        assert ':' in data.report_time
        parts = data.report_time.split(':')
        assert len(parts) == 2
        assert parts[0].isdigit()
        assert parts[1].isdigit()

    def test_extract_price_history(self, extractor):
        """Test that price history is extracted correctly"""
        jsx_path = '../../../src/EnergieRapport.jsx'

        if not Path(jsx_path).exists():
            pytest.skip(f"JSX file not found at {jsx_path}")

        data = extractor.extract_from_jsx(jsx_path)

        # Should have reasonable number of entries
        assert len(data.price_history) >= 20

        # First entry should have valid structure
        first = data.price_history[0]
        assert first.date is not None
        assert first.ttf > 0
        assert first.belpex > 0

        # Last entry should have "Vandaag" note
        last = data.price_history[-1]
        assert last.note == "Vandaag"

    def test_extract_kpi_values(self, extractor):
        """Test that KPI values are extracted"""
        jsx_path = '../../../src/EnergieRapport.jsx'

        if not Path(jsx_path).exists():
            pytest.skip(f"JSX file not found at {jsx_path}")

        data = extractor.extract_from_jsx(jsx_path)

        # Should have TTF and Belpex at minimum
        assert 'ttf' in data.kpis
        assert 'belpex' in data.kpis
        assert data.kpis['ttf'] > 0
        assert data.kpis['belpex'] > 0

        # Storage and Brent are optional but if present should be valid
        if 'storage' in data.kpis:
            assert data.kpis['storage'] > 0
        if 'brent' in data.kpis:
            assert data.kpis['brent'] > 0

    def test_extract_forecast_scenarios(self, extractor):
        """Test that all forecast scenarios are extracted"""
        jsx_path = '../../../src/EnergieRapport.jsx'

        if not Path(jsx_path).exists():
            pytest.skip(f"JSX file not found at {jsx_path}")

        data = extractor.extract_from_jsx(jsx_path)

        # Should have all three scenarios
        assert len(data.forecast_base) > 0
        assert len(data.forecast_bull) > 0
        assert len(data.forecast_bear) > 0

        # Each forecast point should have valid data
        for point in data.forecast_base:
            assert point.date is not None
            assert point.ttf > 0
            assert point.belpex > 0

    def test_validate_extracted_data(self, extractor):
        """Test that extracted data passes validation"""
        jsx_path = '../../../src/EnergieRapport.jsx'

        if not Path(jsx_path).exists():
            pytest.skip(f"JSX file not found at {jsx_path}")

        data = extractor.extract_from_jsx(jsx_path)

        # Should not raise any exception
        assert extractor.validate(data) is True

    def test_price_values_in_reasonable_range(self, extractor):
        """Test that extracted prices are in reasonable ranges"""
        jsx_path = '../../../src/EnergieRapport.jsx'

        if not Path(jsx_path).exists():
            pytest.skip(f"JSX file not found at {jsx_path}")

        data = extractor.extract_from_jsx(jsx_path)

        # TTF typically 20-150 €/MWh
        for point in data.price_history:
            assert 0 < point.ttf < 200, f"TTF {point.ttf} out of range"
            assert 0 < point.belpex < 300, f"Belpex {point.belpex} out of range"

    def test_forecast_consistency(self, extractor):
        """Test that forecast scenarios start with same point"""
        jsx_path = '../../../src/EnergieRapport.jsx'

        if not Path(jsx_path).exists():
            pytest.skip(f"JSX file not found at {jsx_path}")

        data = extractor.extract_from_jsx(jsx_path)

        # All forecasts should start with same date
        base_start = data.forecast_base[0].date
        bull_start = data.forecast_bull[0].date
        bear_start = data.forecast_bear[0].date

        assert base_start == bull_start == bear_start


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
