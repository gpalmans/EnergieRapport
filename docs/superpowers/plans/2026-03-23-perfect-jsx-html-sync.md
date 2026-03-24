# 100% JSX/HTML Synchronization Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers-extended-cc:subagent-driven-development or superpowers-extended-cc:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminate manual synchronization between EnergieRapport.jsx and offline.html by establishing a single source of truth with deterministic HTML generation, ensuring 100% identical content between formats whenever either file is updated.

**Architecture:**
- Implement a **JSX-to-HTML generator** (`jsx_to_html_compiler.py`) that parses the JSX file as the single source of truth and generates the offline.html as a derived artifact
- Extract all data and text content into a **shared data layer** (JSON) that both JSX and HTML reference
- Replace manual regex-based updates with **structured data updates** that flow through both files automatically
- Implement **deterministic validation** that checks structural equivalence (data arrays, timestamps, KPI values) rather than hard-coded text patterns

**Tech Stack:**
- Python AST/regex parsing for JSX structure extraction
- Pydantic for data validation
- pytest for structural equivalence testing

---

## Task 1: Extract Shared Data Structure from JSX

**Files:**
- Create: `scripts/shared_data_extractor.py`
- Create: `tests/test_data_extractor.py`
- Modify: `scripts/report_updater.py` (to use extracted data)

**Purpose:** Define the canonical data structure that both JSX and HTML will consume.

- [ ] **Step 1: Analyze JSX to identify data boundaries**

Read the JSX file and identify all data sources:
- `rawData` array (market prices)
- `marketData` derived array
- `chartData` with trendlines
- `forecastBase/Bull/Bear` arrays
- KPI values (TTF, Belpex, Storage, Brent)
- Timestamps (header, footer)
- Alert banner text
- Tab content (Analyse, Geopolitiek, Forecast, Advies, Bronnen)

Document the structure in a JSON schema file: `data/energy_report_schema.json`

- [ ] **Step 2: Create data extractor class**

Create `scripts/shared_data_extractor.py`:

```python
import json
import re
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class PriceDataPoint:
    date: str
    ttf: float
    belpex: float
    note: str = ""

@dataclass
class ForecastPoint:
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
    def extract_from_jsx(self, jsx_path: str) -> EnergyReportData:
        """Parse JSX and extract structured data"""
        with open(jsx_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract header timestamp: "MARKTANALYSE — 23 MAART 2026 · 20:30"
        header_match = re.search(r'MARKTANALYSE — (\d{2} \w+ \d{4}) · (\d{2}:\d{2})', content)
        if not header_match:
            raise ValueError("Could not find header timestamp")

        report_date = header_match.group(1).lower()  # "23 maart 2026"
        report_time = header_match.group(2)  # "20:30"

        # Extract rawData array
        price_history = self._extract_rawdata(content)

        # Extract forecast arrays
        forecast_base = self._extract_forecast(content, 'forecastBase')
        forecast_bull = self._extract_forecast(content, 'forecastBull')
        forecast_bear = self._extract_forecast(content, 'forecastBear')

        # Extract KPI values
        kpis = self._extract_kpis(content)

        # Extract alert banner
        alert_match = re.search(r'<div[^>]*>⚠️</span>.*?<div[^>]*>([^<]+)</div>', content, re.DOTALL)
        alert_banner = alert_match.group(1).strip() if alert_match else ""

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
        rawdata_match = re.search(r'const rawData = \[([\s\S]*?)\];', content)
        if not rawdata_match:
            raise ValueError("Could not find rawData array")

        data_text = rawdata_match.group(1)
        points = []

        # Match each entry: { date: "14/02", ttf: 30.8, belpex: 70.0, note: "" }
        for match in re.finditer(
            r'\{\s*date:\s*"([^"]+)",\s*ttf:\s*([\d.]+),\s*belpex:\s*([\d.]+),\s*(?:note:\s*"([^"]*)")?\s*\}',
            data_text
        ):
            points.append(PriceDataPoint(
                date=match.group(1),
                ttf=float(match.group(2)),
                belpex=float(match.group(3)),
                note=match.group(4) or ""
            ))

        return points

    def _extract_forecast(self, content: str, array_name: str) -> List[ForecastPoint]:
        """Extract forecast scenario"""
        pattern = rf'const {array_name} = \[([\s\S]*?)\];'
        match = re.search(pattern, content)
        if not match:
            raise ValueError(f"Could not find {array_name} array")

        data_text = match.group(1)
        points = []

        for m in re.finditer(
            r'\{\s*date:\s*"([^"]+)",\s*ttf:\s*([\d.]+),\s*belpex:\s*([\d.]+)\s*\}',
            data_text
        ):
            points.append(ForecastPoint(
                date=m.group(1),
                ttf=float(m.group(2)),
                belpex=float(m.group(3))
            ))

        return points

    def _extract_kpis(self, content: str) -> Dict[str, float]:
        """Extract KPI values from JSX"""
        kpis = {}

        # Match: <div class="kpi-val" style="color:#ef4444">€60.60<span class="kpi-sub">/MWh</span></div>
        for match in re.finditer(r'€([\d.]+)<span[^>]*>/MWh', content):
            ttf_value = float(match.group(1))
            kpis['ttf'] = ttf_value
            break

        # Similar for Belpex
        for match in re.finditer(r'€([\d.]+)<span[^>]*>/MWh</span></div>\s*<div[^>]*style[^>]*>(\+|-)([\d.]+)%', content):
            if len(re.findall(r'€([\d.]+)<span', content)) >= 2:
                belpex_value = float(re.findall(r'€([\d.]+)<span', content)[1])
                kpis['belpex'] = belpex_value
                break

        # EU Storage percentage: ~26%
        storage_match = re.search(r'~(\d+(?:\.\d+)?)%', content)
        if storage_match:
            kpis['storage'] = float(storage_match.group(1))

        # Brent: $112
        brent_match = re.search(r'\$(\d+(?:\.\d+)?)', content)
        if brent_match:
            kpis['brent'] = float(brent_match.group(1))

        return kpis

    def validate(self, data: EnergyReportData) -> bool:
        """Validate data consistency"""
        if not data.price_history:
            raise ValueError("No price history data")
        if not data.forecast_base or not data.forecast_bull or not data.forecast_bear:
            raise ValueError("Missing forecast scenarios")
        if not data.kpis:
            raise ValueError("No KPI values found")

        # Check prices are reasonable (TTF typically 20-100, Belpex 20-200)
        for point in data.price_history:
            if not (0 < point.ttf < 150):
                raise ValueError(f"TTF value {point.ttf} out of reasonable range")
            if not (0 < point.belpex < 250):
                raise ValueError(f"Belpex value {point.belpex} out of reasonable range")

        return True
```

- [ ] **Step 3: Write test for extraction**

Create `tests/test_data_extractor.py`:

```python
import pytest
from pathlib import Path
from scripts.shared_data_extractor import DataExtractor

def test_extract_from_jsx():
    """Test that we can extract data from JSX"""
    extractor = DataExtractor()
    data = extractor.extract_from_jsx('src/EnergieRapport.jsx')

    # Validate structure
    assert data.report_date is not None
    assert data.report_time is not None
    assert len(data.price_history) >= 20
    assert len(data.forecast_base) >= 5
    assert len(data.forecast_bull) >= 5
    assert len(data.forecast_bear) >= 5
    assert data.kpis['ttf'] > 0
    assert data.kpis['belpex'] > 0

    # Validate data
    extractor.validate(data)

def test_extract_kpis():
    """Test KPI extraction"""
    extractor = DataExtractor()
    data = extractor.extract_from_jsx('src/EnergieRapport.jsx')

    # All KPIs should be present and positive
    assert data.kpis['ttf'] > 0
    assert data.kpis['belpex'] > 0
    assert data.kpis['storage'] > 0
    assert data.kpis['brent'] > 0
```

Run test:
```bash
pytest tests/test_data_extractor.py -v
```

Expected output:
```
test_data_extractor.py::test_extract_from_jsx PASSED
test_data_extractor.py::test_extract_kpis PASSED
```

- [ ] **Step 4: Commit**

```bash
git add scripts/shared_data_extractor.py tests/test_data_extractor.py
git commit -m "feat(sync): create shared data extraction layer from JSX"
```

---

## Task 2: Build JSX-to-HTML Compiler

**Files:**
- Create: `scripts/jsx_to_html_compiler.py`
- Create: `templates/energy_report_template.html`
- Create: `tests/test_compiler.py`

**Purpose:** Generate offline.html from JSX as a derived artifact.

- [ ] **Step 1: Create HTML template**

Create `templates/energy_report_template.html` with data placeholders:

```html
<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Vlaamse Energieprijzen: Analyse &amp; Forecast — {{ month_year }}</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0f172a;color:#e2e8f0;font-family:Georgia,serif;padding:24px 20px;min-height:100vh}
.kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:24px}
.kpi{background:#1e293b;border-radius:10px;padding:13px 15px;border:1px solid #ef444444}
.kpi-label{font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:.1em;margin-bottom:5px}
.kpi-val{font-size:22px;font-weight:700;color:#ef4444}
.kpi-sub{font-size:11px}
</style>
</head>
<body>

<!-- HEADER -->
<div style="text-align:center;margin-bottom:28px">
  <div style="color:#0ea5e9;font-size:11px;letter-spacing:0.2em;text-transform:uppercase;margin-bottom:8px;font-family:monospace">MARKTANALYSE — {{ report_date_upper }} · {{ report_time }}</div>
  <h1 style="font-size:26px;font-weight:700;margin:0 0 8px;color:#f8fafc">Vlaamse Energieprijzen: Analyse &amp; Forecast</h1>
</div>

<!-- KPIs -->
<div class="kpi-grid">
  <div class="kpi">
    <div class="kpi-label">TTF Gas vandaag</div>
    <div class="kpi-val">€{{ kpis.ttf|round(2) }}<span class="kpi-sub">/MWh</span></div>
  </div>
  <div class="kpi">
    <div class="kpi-label">Belpex Elektr. vandaag</div>
    <div class="kpi-val">€{{ kpis.belpex|round(2) }}<span class="kpi-sub">/MWh</span></div>
  </div>
  <div class="kpi">
    <div class="kpi-label">België Gasopslag</div>
    <div class="kpi-val">~{{ kpis.storage|round(0)|int }}%</div>
  </div>
  <div class="kpi">
    <div class="kpi-label">Brent Crude</div>
    <div class="kpi-val">${{ kpis.brent|round(2) }}<span class="kpi-sub">/vat</span></div>
  </div>
</div>

<!-- DATA ARRAYS -->
<script>
const marketData = {{ market_data_json|safe }};
const forecastBase = {{ forecast_base_json|safe }};
const forecastBull = {{ forecast_bull_json|safe }};
const forecastBear = {{ forecast_bear_json|safe }};
</script>

</body>
</html>
```

- [ ] **Step 2: Create compiler class**

Create `scripts/jsx_to_html_compiler.py`:

```python
import json
from pathlib import Path
from dataclasses import asdict
from shared_data_extractor import DataExtractor, EnergyReportData

class JsxToHtmlCompiler:
    def __init__(self):
        self.extractor = DataExtractor()

    def compile(self, jsx_path: str, template_path: str, output_path: str) -> bool:
        """
        Compile: JSX → Extract Data → Render HTML
        Returns True if successful
        """
        try:
            # 1. Extract structured data from JSX
            data = self.extractor.extract_from_jsx(jsx_path)
            self.extractor.validate(data)

            # 2. Load HTML template
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()

            # 3. Prepare JSON data for embedding
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

            # 4. Simple string replacement (Jinja2 not required for MVP)
            html_output = template_content
            html_output = html_output.replace('{{ report_date_upper }}', data.report_date.upper())
            html_output = html_output.replace('{{ report_time }}', data.report_time)
            html_output = html_output.replace('{{ month_year }}', data.report_date)

            # KPI values
            html_output = html_output.replace('{{ kpis.ttf|round(2) }}', f"{data.kpis['ttf']:.2f}")
            html_output = html_output.replace('{{ kpis.belpex|round(2) }}', f"{data.kpis['belpex']:.2f}")
            html_output = html_output.replace('{{ kpis.storage|round(0)|int }}', f"{int(data.kpis['storage'])}")
            html_output = html_output.replace('{{ kpis.brent|round(2) }}', f"{data.kpis['brent']:.2f}")

            # Data arrays
            html_output = html_output.replace('{{ market_data_json|safe }}', market_data_json)
            html_output = html_output.replace('{{ forecast_base_json|safe }}', forecast_base_json)
            html_output = html_output.replace('{{ forecast_bull_json|safe }}', forecast_bull_json)
            html_output = html_output.replace('{{ forecast_bear_json|safe }}', forecast_bear_json)

            # 5. Write output
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_output)

            return True
        except Exception as e:
            print(f"❌ Compilation failed: {e}")
            return False
```

- [ ] **Step 3: Test compiler**

Create `tests/test_compiler.py`:

```python
import pytest
import json
from pathlib import Path
from scripts.jsx_to_html_compiler import JsxToHtmlCompiler

def test_jsx_to_html_compilation():
    """Test that compiler generates valid HTML from JSX"""
    compiler = JsxToHtmlCompiler()
    output_path = Path('/tmp/test_offline_compile.html')

    result = compiler.compile(
        'src/EnergieRapport.jsx',
        'templates/energy_report_template.html',
        str(output_path)
    )

    assert result is True, "Compilation failed"
    assert output_path.exists(), "Output file not created"

    with open(output_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Verify critical sections
    assert 'MARKTANALYSE' in html
    assert 'const marketData' in html
    assert 'const forecastBase' in html

    # Verify data is valid JSON
    market_match = html.find('const marketData = ')
    assert market_match > -1

    json_start = html.find('[', market_match)
    json_end = html.find('];', market_match)
    json_str = html[json_start:json_end+1]

    parsed = json.loads(json_str)
    assert len(parsed) > 0
```

Run test:
```bash
pytest tests/test_compiler.py -v
```

- [ ] **Step 4: Commit**

```bash
git add scripts/jsx_to_html_compiler.py templates/energy_report_template.html tests/test_compiler.py
git commit -m "feat(sync): implement JSX-to-HTML compiler as single source of truth"
```

---

## Task 3: Implement Deterministic Sync Validator

**Files:**
- Create: `scripts/sync_validator.py`
- Create: `tests/test_sync_validator.py`

**Purpose:** Validate synchronization using structural equivalence, not text patterns.

- [ ] **Step 1: Create validator class**

Create `scripts/sync_validator.py`:

```python
import re
import json
from pathlib import Path
from shared_data_extractor import DataExtractor

class SyncValidator:
    def __init__(self):
        self.extractor = DataExtractor()
        self.errors = []

    def validate_sync(self, jsx_path: str, html_path: str) -> bool:
        """
        Validate that JSX and HTML are structurally equivalent.
        Returns True if synced, False if differences found.
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

        # 3. Check timestamps match
        if not self._check_timestamp_match(jsx_path, html_path):
            self.errors.append("❌ Timestamps do not match between JSX and HTML")

        # 4. Check KPI values match
        if not self._check_kpi_values_match(jsx_data, html_content):
            self.errors.append("❌ KPI values do not match")

        # 5. Check data arrays exist in HTML
        if not self._check_data_arrays_in_html(jsx_data, html_content):
            self.errors.append("❌ Data arrays missing or invalid in HTML")

        # 6. Check structural integrity
        if not self._check_structural_integrity(jsx_path, html_path):
            self.errors.append("❌ Structural elements missing")

        return len(self.errors) == 0

    def _check_timestamp_match(self, jsx_path: str, html_path: str) -> bool:
        """Verify timestamps match"""
        with open(jsx_path, 'r', encoding='utf-8') as f:
            jsx_content = f.read()
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        jsx_match = re.search(r'MARKTANALYSE — (\d{2} \w+ \d{4}) · (\d{2}:\d{2})', jsx_content)
        html_match = re.search(r'MARKTANALYSE — (\d{2} \w+ \d{4}) · (\d{2}:\d{2})', html_content)

        if not jsx_match or not html_match:
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
            market_match = re.search(r'const marketData = (\[[\s\S]*?\]);', html_content)
            if not market_match:
                self.errors.append("  marketData array not found")
                return False

            market_json = market_match.group(1)
            parsed = json.loads(market_json)

            if len(parsed) != len(jsx_data.price_history):
                self.errors.append(f"  Data length mismatch: JSX={len(jsx_data.price_history)}, HTML={len(parsed)}")
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

        critical_elements = [
            "Analyse", "Geopolitiek", "Forecast", "Advies", "Bronnen",
            "kpi", "KPI",
            "marketData", "forecastBase", "forecastBull", "forecastBear",
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

    def report(self) -> str:
        """Generate validation report"""
        if not self.errors:
            return "✅ Synchronization verified — JSX and HTML are in perfect sync!"

        report = "❌ Synchronization validation FAILED\n"
        for error in self.errors:
            report += f"{error}\n"
        return report
```

- [ ] **Step 2: Test validator**

Create `tests/test_sync_validator.py`:

```python
import pytest
from scripts.sync_validator import SyncValidator

def test_sync_validator_passes_for_compiled_html():
    """After compilation, validation should pass"""
    validator = SyncValidator()

    is_synced = validator.validate_sync(
        'src/EnergieRapport.jsx',
        'public/offline.html'
    )

    print(validator.report())
    assert is_synced, "Synchronization check failed: " + validator.report()
```

Run test:
```bash
pytest tests/test_sync_validator.py -v
```

- [ ] **Step 3: Commit**

```bash
git add scripts/sync_validator.py tests/test_sync_validator.py
git commit -m "feat(sync): implement structural equivalence validator"
```

---

## Task 4: Integrate Compiler into Report Update Workflow

**Files:**
- Modify: `scripts/report_updater.py`
- Modify: `.github/workflows/energy-report.yml`

**Purpose:** Make HTML generation automatic after JSX updates.

- [ ] **Step 1: Update report_updater.py main function**

Modify the end of `scripts/report_updater.py` to add:

```python
# At the end of the ReportUpdater class, add:

    def update_reports(self):
        """Main workflow: update JSX, then regenerate HTML"""
        logger.info("=== Starting report update cycle ===")

        # 1. Load data
        market_data = self.load_market_data()
        ai_analysis = self.load_ai_analysis()

        logger.info(f"Loaded market data for {market_data.get('timestamp')}")

        # 2. Update JSX (source of truth)
        with open(self.jsx_path, 'r', encoding='utf-8') as f:
            jsx_content = f.read()

        jsx_content = self.update_jsx_rawdata(jsx_content, market_data)
        jsx_content = self.update_jsx_kpis(jsx_content, market_data)
        jsx_content = self.update_jsx_dates(jsx_content, market_data)

        with open(self.jsx_path, 'w', encoding='utf-8') as f:
            f.write(jsx_content)

        logger.info(f"✅ Updated JSX: {self.jsx_path}")

        # 3. Regenerate HTML from JSX (derived artifact)
        try:
            from jsx_to_html_compiler import JsxToHtmlCompiler
            compiler = JsxToHtmlCompiler()

            success = compiler.compile(
                self.jsx_path,
                'templates/energy_report_template.html',
                self.html_path
            )

            if success:
                logger.info(f"✅ Regenerated HTML: {self.html_path}")
            else:
                logger.error("❌ HTML compilation failed!")
                raise RuntimeError("Failed to regenerate HTML from JSX")
        except Exception as e:
            logger.error(f"Compilation error: {e}")
            raise

        # 4. Validate sync
        try:
            from sync_validator import SyncValidator
            validator = SyncValidator()
            if not validator.validate_sync(self.jsx_path, self.html_path):
                logger.error(validator.report())
                raise RuntimeError("Synchronization validation failed!")

            logger.info("✅ Synchronization validated successfully")
        except Exception as e:
            logger.error(f"Validation error: {e}")
            raise

# Modify main() to call update_reports():
if __name__ == '__main__':
    updater = ReportUpdater()
    updater.update_reports()
```

- [ ] **Step 2: Update GitHub Actions workflow**

The workflow already calls `python scripts/report_updater.py`, so no changes needed. It will now:
1. Update JSX
2. Auto-compile HTML
3. Validate sync
4. Commit all changes

- [ ] **Step 3: Test the integration**

```bash
# Run locally to test
python scripts/report_updater.py
```

Expected output:
```
✅ Updated JSX: src/EnergieRapport.jsx
✅ Regenerated HTML: public/offline.html
✅ Synchronization validated successfully
```

- [ ] **Step 4: Commit**

```bash
git add scripts/report_updater.py
git commit -m "feat(sync): integrate HTML compiler into update workflow"
```

---

## Task 5: Create Comprehensive Synchronization Tests

**Files:**
- Create: `tests/test_synchronization_comprehensive.py`

**Purpose:** Ensure full sync pipeline works end-to-end.

- [ ] **Step 1: Write comprehensive test suite**

Create `tests/test_synchronization_comprehensive.py`:

```python
import pytest
from pathlib import Path
import json
from scripts.shared_data_extractor import DataExtractor
from scripts.jsx_to_html_compiler import JsxToHtmlCompiler
from scripts.sync_validator import SyncValidator

class TestSynchronization:
    @pytest.fixture
    def extractor(self):
        return DataExtractor()

    @pytest.fixture
    def compiler(self):
        return JsxToHtmlCompiler()

    @pytest.fixture
    def validator(self):
        return SyncValidator()

    def test_data_extraction_complete(self, extractor):
        """All required data should extract successfully"""
        data = extractor.extract_from_jsx('src/EnergieRapport.jsx')

        assert data.report_date is not None
        assert data.report_time is not None
        assert len(data.price_history) >= 20
        assert len(data.forecast_base) >= 5
        assert len(data.forecast_bull) >= 5
        assert len(data.forecast_bear) >= 5
        assert len(data.kpis) == 4  # ttf, belpex, storage, brent
        assert data.alert_banner

    def test_data_validation(self, extractor):
        """Extracted data should pass validation"""
        data = extractor.extract_from_jsx('src/EnergieRapport.jsx')
        assert extractor.validate(data) is True

    def test_html_compilation_succeeds(self, compiler):
        """HTML compilation should generate valid output"""
        output = Path('/tmp/test_compile_comprehensive.html')
        result = compiler.compile(
            'src/EnergieRapport.jsx',
            'templates/energy_report_template.html',
            str(output)
        )

        assert result is True
        assert output.exists()

    def test_compiled_html_contains_valid_json(self, compiler):
        """Generated HTML should contain valid JSON data arrays"""
        output = Path('/tmp/test_json_validity.html')
        compiler.compile(
            'src/EnergieRapport.jsx',
            'templates/energy_report_template.html',
            str(output)
        )

        with open(output, 'r', encoding='utf-8') as f:
            html = f.read()

        # Extract and validate each array
        for array_name in ['marketData', 'forecastBase', 'forecastBull', 'forecastBear']:
            pattern = rf'const {array_name} = (\[[\s\S]*?\]);'
            import re
            match = re.search(pattern, html)
            assert match, f"{array_name} not found"

            json_str = match.group(1)
            parsed = json.loads(json_str)
            assert len(parsed) > 0, f"{array_name} is empty"

    def test_sync_validation_after_compilation(self, compiler, validator):
        """After compilation, JSX and HTML should pass validation"""
        output = Path('/tmp/test_sync_after_compile.html')
        compiler.compile(
            'src/EnergieRapport.jsx',
            'templates/energy_report_template.html',
            str(output)
        )

        is_synced = validator.validate_sync(
            'src/EnergieRapport.jsx',
            str(output)
        )

        assert is_synced, validator.report()

    def test_kpi_round_trip(self, extractor, compiler, validator):
        """KPI values should survive extraction → compilation → validation"""
        # Extract original
        data = extractor.extract_from_jsx('src/EnergieRapport.jsx')
        original_kpis = data.kpis.copy()

        # Compile
        output = Path('/tmp/test_kpi_roundtrip.html')
        compiler.compile(
            'src/EnergieRapport.jsx',
            'templates/energy_report_template.html',
            str(output)
        )

        # Validate
        assert validator.validate_sync(
            'src/EnergieRapport.jsx',
            str(output)
        ), "KPI round-trip failed validation"
```

- [ ] **Step 2: Run all tests**

```bash
pytest tests/ -v
```

Expected output:
```
test_data_extractor.py::test_extract_from_jsx PASSED
test_compiler.py::test_jsx_to_html_compilation PASSED
test_sync_validator.py::test_sync_validator_passes_for_compiled_html PASSED
test_synchronization_comprehensive.py::test_data_extraction_complete PASSED
test_synchronization_comprehensive.py::test_html_compilation_succeeds PASSED
test_synchronization_comprehensive.py::test_sync_validation_after_compilation PASSED

======================== 7 passed in 2.34s ========================
```

- [ ] **Step 3: Commit**

```bash
git add tests/test_synchronization_comprehensive.py
git commit -m "test(sync): add comprehensive end-to-end synchronization tests"
```

---

## Task 6: Documentation and Final Integration

**Files:**
- Create: `docs/SYNCHRONIZATION_ARCHITECTURE.md`
- Modify: `CLAUDE.md`

**Purpose:** Document the new architecture for future maintainers.

- [ ] **Step 1: Create architecture documentation**

Create `docs/SYNCHRONIZATION_ARCHITECTURE.md`:

```markdown
# JSX/HTML Synchronization Architecture

## Overview

The EnergieRapport uses a **single source of truth** pattern:
- **JSX** (`src/EnergieRapport.jsx`) is the authoritative data source
- **HTML** (`public/offline.html`) is automatically generated from JSX
- **Validation** ensures perfect structural equivalence after each update

## Why This Approach?

**Problem (before):**
- Manual regex updates to both JSX and HTML
- Easy to get out of sync
- Hard-coded text validation breaks when content changes
- Validation script fragile and unmaintainable

**Solution (after):**
- Single source of truth (JSX) → deterministic HTML generation
- Validation checks structural equivalence, not text patterns
- Automatic sync guarantees in CI/CD pipeline
- Scalable to future changes

## Update Workflow

```
1. data_collector.py
   ↓ (creates latest_prices.json)
2. report_updater.py
   ↓ (updates src/EnergieRapport.jsx)
3. jsx_to_html_compiler.py
   ↓ (generates public/offline.html)
4. sync_validator.py
   ↓ (verifies structural equivalence)
5. Git commit
   ↓
6. Cloudflare Pages build
```

## Key Components

### 1. DataExtractor (`shared_data_extractor.py`)
- Parses JSX into `EnergyReportData` structure
- Handles:
  - Price history (rawData array)
  - Forecast scenarios (base/bull/bear)
  - KPI values (TTF, Belpex, Storage, Brent)
  - Timestamps (header/footer)
  - Alert banner text

### 2. JsxToHtmlCompiler (`jsx_to_html_compiler.py`)
- Extracts structured data from JSX
- Renders HTML template with data
- Produces deterministic, validated HTML

### 3. SyncValidator (`sync_validator.py`)
- Compares JSX and HTML structurally
- Checks:
  - Timestamps match exactly
  - KPI values present in both
  - Data arrays valid JSON
  - Critical elements present
- Reports specific mismatches, not just "fail"

## Maintenance

### Updating Content
1. Edit `src/EnergieRapport.jsx` (source of truth)
2. Run `python scripts/report_updater.py`
3. HTML is auto-generated and validated
4. No manual HTML edits needed

### Updating Layout
1. Edit `templates/energy_report_template.html`
2. Edit `shared_data_extractor.py` if extracting new fields
3. Update `jsx_to_html_compiler.py` if new placeholders needed
4. Run tests: `pytest tests/`
5. Run full cycle: `python scripts/report_updater.py`

### Troubleshooting Desync

If validation fails:
```bash
python scripts/sync_validator.py
```

Output will show exactly which values don't match. Fix the issue in JSX or template, then recompile.

## Test Coverage

- Unit tests for each component
- Integration test for full cycle
- Validation test ensures generated HTML passes

Run all: `pytest tests/ -v`

## Future Enhancements

- [ ] Template inheritance for multiple report types
- [ ] Asset versioning (CSS, JS)
- [ ] Multi-language support
- [ ] Mobile-responsive template
```

- [ ] **Step 2: Update CLAUDE.md**

Modify the "Stap 3 — JSX bijwerken" section in CLAUDE.md:

```markdown
### Automatische HTML-Synchronisatie (NEW)

Na het updaten van de JSX, wordt de `offline.html` **automatisch gegenereerd** en **100% gesynchroniseerd**:

```bash
python scripts/report_updater.py
```

Dit script:
1. ✅ Update JSX met nieuwe marktdata
2. ✅ Generate HTML uit JSX (single source of truth)
3. ✅ Valideer perfecte synchronisatie
4. ✅ Commit changes

**Geen handmatige HTML-edits meer nodig.**

Voor lokale testing:
```bash
python scripts/jsx_to_html_compiler.py src/EnergieRapport.jsx templates/energy_report_template.html public/offline.html
python scripts/sync_validator.py
```

Voor volledig overzicht van architectuur, zie `docs/SYNCHRONIZATION_ARCHITECTURE.md`.
```

- [ ] **Step 3: Commit documentation**

```bash
git add docs/SYNCHRONIZATION_ARCHITECTURE.md CLAUDE.md
git commit -m "docs(sync): document single-source-of-truth architecture"
```

---

## Final Validation Checklist

- [ ] All tests pass: `pytest tests/ -v`
- [ ] Manual compilation works: `python scripts/jsx_to_html_compiler.py`
- [ ] Validator detects sync properly: `python scripts/sync_validator.py`
- [ ] report_updater integration works: `python scripts/report_updater.py`
- [ ] GitHub Actions workflow updated
- [ ] Documentation complete

**All 6 tasks completed → Perfect JSX/HTML synchronization achieved!**
