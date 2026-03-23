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
    kpi_deltas: Dict[str, str]  # {ttf_delta, belpex_delta, storage_note, brent_delta}
    alert_banner: str
    alert_banner_title: str
    alert_banner_text: str


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

        # Extract KPI deltas
        kpi_deltas = self._extract_kpi_deltas(content)

        # Extract alert banner
        alert_banner_title, alert_banner_text = self._extract_alert_banner(content)

        return EnergyReportData(
            report_date=report_date,
            report_time=report_time,
            price_history=price_history,
            forecast_base=forecast_base,
            forecast_bull=forecast_bull,
            forecast_bear=forecast_bear,
            kpis=kpis,
            kpi_deltas=kpi_deltas,
            alert_banner=alert_banner_title,  # For backwards compatibility
            alert_banner_title=alert_banner_title,
            alert_banner_text=alert_banner_text
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
        """Extract KPI values from JSX - using LAST rawData entry (current prices)"""
        kpis = {}

        # Extract rawData section
        rawdata_match = re.search(
            r'const rawData = \[([\s\S]*?)\];',
            content
        )
        if rawdata_match:
            rawdata_section = rawdata_match.group(1)
            # Find ALL price entries in rawData
            all_entries = re.findall(
                r'\{\s*date:\s*"[^"]+",\s*ttf:\s*([\d.]+),\s*belpex:\s*([\d.]+)',
                rawdata_section
            )
            if all_entries:
                # Use LAST entry (most recent prices)
                last_ttf, last_belpex = all_entries[-1]
                kpis['ttf'] = float(last_ttf)
                kpis['belpex'] = float(last_belpex)

        # EU Storage percentage: look for pattern like "~26%"
        storage_match = re.search(r'~(\d+(?:\.\d+)?)%', content)
        if storage_match:
            kpis['storage'] = float(storage_match.group(1))

        # Brent crude: target the KPI grid specifically
        # Look for "Brent" label followed by $ amount
        brent_match = re.search(r'Brent.*?\$(\d+(?:\.\d+)?)', content, re.DOTALL)
        if brent_match:
            kpis['brent'] = float(brent_match.group(1))

        return kpis

    def _extract_kpi_deltas(self, content: str) -> Dict[str, str]:
        """Extract KPI delta labels from JSX - the "+3.6% vs gisteren" style labels"""
        deltas = {}

        # Extract the KPI array from JSX
        # Look for patterns like: { label: "TTF Gas vandaag", value: "€60.60", sub: "/MWh", delta: "+3.6% vs gisteren" }

        # Extract TTF delta
        ttf_delta_match = re.search(r'TTF Gas vandaag.*?delta:\s*"([^"]+)"', content, re.DOTALL)
        if ttf_delta_match:
            deltas['ttf_delta'] = ttf_delta_match.group(1)
        else:
            deltas['ttf_delta'] = ""

        # Extract Belpex delta
        belpex_delta_match = re.search(r'Belpex.*?delta:\s*"([^"]+)"', content, re.DOTALL)
        if belpex_delta_match:
            deltas['belpex_delta'] = belpex_delta_match.group(1)
        else:
            deltas['belpex_delta'] = ""

        # Extract storage note/label
        storage_note_match = re.search(r'EU Gasopslag.*?sub:\s*"([^"]+)"', content, re.DOTALL)
        if storage_note_match:
            deltas['storage_note'] = storage_note_match.group(1)
        else:
            deltas['storage_note'] = ""

        # Extract Brent delta
        brent_delta_match = re.search(r'Brent.*?delta:\s*"([^"]+)"', content, re.DOTALL)
        if brent_delta_match:
            deltas['brent_delta'] = brent_delta_match.group(1)
        else:
            deltas['brent_delta'] = ""

        return deltas

    def _extract_alert_banner(self, content: str) -> tuple:
        """Extract alert banner title and text from JSX.

        Returns:
            tuple: (alert_banner_title, alert_banner_text)
        """
        # Look for alert banner with "KRITIEKE MARKTSITUATIE" title
        # Pattern: KRITIEKE MARKTSITUATIE<...>color: "#fca5a5"...<...>content text
        alert_match = re.search(
            r'KRITIEKE MARKTSITUATIE[\s\S]*?color:\s*"#fca5a5"[^>]*>\s*([^<]+?)\s*</',
            content
        )
        if alert_match:
            alert_text = alert_match.group(1).strip()
            return ("⚠️ KRITIEKE MARKTSITUATIE", alert_text)

        return ("", "")

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
        if not isinstance(data.kpi_deltas, dict):
            raise ValueError("KPI deltas missing or invalid")

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

        # Alert banner fields may be empty strings in non-critical situations, so just check type
        if not isinstance(data.alert_banner_title, str):
            raise ValueError("Alert banner title must be a string")
        if not isinstance(data.alert_banner_text, str):
            raise ValueError("Alert banner text must be a string")

        return True
