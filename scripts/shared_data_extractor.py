"""
Shared Data Extractor for EnergieRapport
Extracts structured data from JSX as single source of truth
"""

import json
import re
from dataclasses import dataclass, asdict
from typing import Dict, List
from datetime import datetime


@dataclass
class PriceDataPoint:
    """Single price data point"""
    date: str
    ttf: float
    belpex: float
    note: str = ""


@dataclass
class ForecastPoint:
    """Single forecast point"""
    date: str
    ttf: float
    belpex: float


@dataclass
class EnergyReportData:
    """Single source of truth for all report data"""
    report_date: str  # "23 maart 2026"
    report_time: str  # "20:30"
    price_history: List[PriceDataPoint]
    forecast_base: List[ForecastPoint]
    forecast_bull: List[ForecastPoint]
    forecast_bear: List[ForecastPoint]
    kpis: Dict[str, float]  # {ttf, belpex, storage, brent}
    alert_banner: str


class DataExtractor:
    """Extract structured data from EnergieRapport.jsx"""

    def extract_from_jsx(self, jsx_path: str) -> EnergyReportData:
        """
        Parse JSX and extract structured data

        Args:
            jsx_path: Path to EnergieRapport.jsx

        Returns:
            EnergyReportData with all extracted information

        Raises:
            ValueError: If critical data cannot be extracted
        """
        with open(jsx_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract header timestamp: "MARKTANALYSE — 23 MAART 2026 · 20:30"
        header_match = re.search(
            r'MARKTANALYSE — (\d{2}) (\w+) (\d{4}) · (\d{2}:\d{2})',
            content
        )
        if not header_match:
            raise ValueError("Could not find header timestamp in JSX")

        day = header_match.group(1)
        month_upper = header_match.group(2)
        year = header_match.group(3)
        report_time = header_match.group(4)

        # Convert month name to lowercase for report_date
        month_lower = month_upper.lower()
        report_date = f"{day} {month_lower} {year}"

        # Extract rawData array (price history)
        price_history = self._extract_rawdata(content)

        # Extract forecast arrays
        forecast_base = self._extract_forecast(content, 'forecastBase')
        forecast_bull = self._extract_forecast(content, 'forecastBull')
        forecast_bear = self._extract_forecast(content, 'forecastBear')

        # Extract KPI values
        kpis = self._extract_kpis(content)

        # Extract alert banner text
        alert_banner = self._extract_alert_banner(content)

        return EnergyReportData(
            report_date=report_date,
            report_time=report_time,
            price_history=price_history,
            forecast_base=forecast_base,
            forecast_bull=forecast_bull,
            forecast_bear=forecast_bear,
            kpis=kpis,
            alert_banner=alert_banner
        )

    def _extract_rawdata(self, content: str) -> List[PriceDataPoint]:
        """Extract price history from rawData array"""
        rawdata_match = re.search(
            r'const rawData = \[([\s\S]*?)\];',
            content
        )
        if not rawdata_match:
            raise ValueError("Could not find rawData array in JSX")

        data_text = rawdata_match.group(1)
        points = []

        # Match each entry: { date: "14/02", ttf: 30.8, belpex: 70.0, note: "" }
        for match in re.finditer(
            r'\{\s*date:\s*"([^"]+)",\s*ttf:\s*([\d.]+),\s*belpex:\s*([\d.]+),\s*note:\s*"([^"]*)"\s*\}',
            data_text
        ):
            points.append(PriceDataPoint(
                date=match.group(1),
                ttf=float(match.group(2)),
                belpex=float(match.group(3)),
                note=match.group(4)
            ))

        if not points:
            raise ValueError("No price data points extracted from rawData")

        return points

    def _extract_forecast(self, content: str, array_name: str) -> List[ForecastPoint]:
        """Extract forecast scenario array"""
        pattern = rf'const {array_name} = \[([\s\S]*?)\];'
        match = re.search(pattern, content)
        if not match:
            raise ValueError(f"Could not find {array_name} array in JSX")

        data_text = match.group(1)
        points = []

        # Match each entry: { date: "23/03", ttf: 60.60, belpex: 104.00 }
        for m in re.finditer(
            r'\{\s*date:\s*"([^"]+)",\s*ttf:\s*([\d.]+),\s*belpex:\s*([\d.]+)\s*\}',
            data_text
        ):
            points.append(ForecastPoint(
                date=m.group(1),
                ttf=float(m.group(2)),
                belpex=float(m.group(3))
            ))

        if not points:
            raise ValueError(f"No forecast points extracted from {array_name}")

        return points

    def _extract_kpis(self, content: str) -> Dict[str, float]:
        """Extract KPI values from JSX"""
        kpis = {}

        # Extract TTF from first price in last rawData entry
        # Look for: { date: "23/03", ttf: 60.60, belpex: 104.00, note: "Vandaag" }
        last_entry_match = re.search(
            r'\{\s*date:\s*"[^"]+",\s*ttf:\s*([\d.]+),\s*belpex:\s*([\d.]+)',
            content
        )
        if last_entry_match:
            kpis['ttf'] = float(last_entry_match.group(1))
            kpis['belpex'] = float(last_entry_match.group(2))

        # EU Storage percentage: look for pattern like "~26%"
        storage_match = re.search(r'~(\d+(?:\.\d+)?)%', content)
        if storage_match:
            kpis['storage'] = float(storage_match.group(1))

        # Brent crude: look for pattern like "$112.19"
        brent_match = re.search(r'\$(\d+(?:\.\d+)?)', content)
        if brent_match:
            kpis['brent'] = float(brent_match.group(1))

        return kpis

    def _extract_alert_banner(self, content: str) -> str:
        """Extract alert banner text from JSX"""
        # Look for alert banner div with critical market situation text
        alert_match = re.search(
            r'<div[^>]*>⚠️[^<]*</span>\s*<div[^>]*>([^<]+)</div>',
            content
        )
        if alert_match:
            return alert_match.group(1).strip()
        return ""

    def validate(self, data: EnergyReportData) -> bool:
        """
        Validate extracted data consistency

        Args:
            data: EnergyReportData to validate

        Returns:
            True if valid

        Raises:
            ValueError: If validation fails
        """
        if not data.price_history:
            raise ValueError("No price history data")
        if not data.forecast_base or not data.forecast_bull or not data.forecast_bear:
            raise ValueError("Missing forecast scenarios")
        if not data.kpis:
            raise ValueError("No KPI values found")

        # Check prices are reasonable
        # TTF typically 20-150 €/MWh
        # Belpex typically 20-200 €/MWh
        for point in data.price_history:
            if not (0 < point.ttf < 200):
                raise ValueError(f"TTF value {point.ttf} out of reasonable range (0-200)")
            if not (0 < point.belpex < 300):
                raise ValueError(f"Belpex value {point.belpex} out of reasonable range (0-300)")

        # Check KPI values
        if data.kpis.get('ttf', 0) <= 0:
            raise ValueError("TTF KPI value missing or invalid")
        if data.kpis.get('belpex', 0) <= 0:
            raise ValueError("Belpex KPI value missing or invalid")

        return True
