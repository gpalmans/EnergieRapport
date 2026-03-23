"""
Report Updater voor EnergieRapport
Update JSX en HTML bestanden met nieuwe marktdata
"""

import os
import sys
import json
import re
from datetime import datetime
from typing import Dict, Optional
import logging

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.jsx_to_html_compiler import JsxToHtmlCompiler
from scripts.sync_validator import SyncValidator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReportUpdater:
    def __init__(self):
        self.jsx_path = 'src/EnergieRapport.jsx'
        self.html_path = 'public/offline.html'
        self.template_path = 'templates/energy_report_template.html'
        self.update_mode = os.getenv('UPDATE_MODE', 'daily')
    
    def load_market_data(self) -> Dict:
        """Laad verzamelde marktdata"""
        filepath = 'data/latest_prices.json'
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"No market data found at {filepath}")
        
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def load_ai_analysis(self) -> Optional[str]:
        """Laad AI analyse indien beschikbaar"""
        filepath = 'data/ai_analysis.json'
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
                return data.get('analysis', '')
        return None
    
    def format_date(self, date_str: Optional[str] = None) -> str:
        """Formatteer datum voor rapport"""
        if date_str:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            dt = datetime.now()
        
        # Format: "23/03"
        return dt.strftime("%d/%m")
    
    def format_datetime_full(self, date_str: Optional[str] = None) -> tuple:
        """Formatteer datum en tijd voor header/footer"""
        if date_str:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            dt = datetime.now()
        
        # Return: ("23 maart 2026", "20:30")
        month_names = {
            1: "januari", 2: "februari", 3: "maart", 4: "april",
            5: "mei", 6: "juni", 7: "juli", 8: "augustus",
            9: "september", 10: "oktober", 11: "november", 12: "december"
        }
        date_full = f"{dt.day} {month_names[dt.month]} {dt.year}"
        time_str = dt.strftime("%H:%M")
        
        # Also return uppercase version for header
        date_upper = f"{dt.day:02d} {month_names[dt.month].upper()} {dt.year}"
        
        return (date_full, time_str, date_upper)
    
    def update_jsx_rawdata(self, content: str, market_data: Dict) -> str:
        """Update rawData array in JSX"""
        date_str = self.format_date(market_data.get('timestamp'))
        
        # Vind laatste entry in rawData
        pattern = r'(const rawData = \[[\s\S]*?)(\{ date: "[^"]+", ttf: [^,]+, belpex: [^,]+, storage: [^,]+, brent: [^}]+ \})([\s\S]*?\];)'
        
        new_entry = (
            f'{{ date: "{date_str}", '
            f'ttf: {market_data["ttf"]:.2f}, '
            f'belpex: {market_data["belpex"]:.2f}, '
            f'storage: {market_data["eu_storage"]:.1f}, '
            f'brent: {market_data["brent"]:.2f} }}'
        )
        
        # Voeg nieuwe entry toe aan einde van array
        def replacer(match):
            return match.group(1) + match.group(2) + ',\n    ' + new_entry + match.group(3)
        
        updated = re.sub(pattern, replacer, content, count=1)
        
        if updated == content:
            logger.warning("Could not update rawData - pattern not found")
        else:
            logger.info(f"Added new rawData entry for {date_str}")
        
        return updated
    
    def update_jsx_kpis(self, content: str, market_data: Dict) -> str:
        """Update KPI waarden in JSX"""
        
        # Update TTF KPI
        ttf_pattern = r'(const ttfKpi = \{[^}]*value: )[0-9.]+([^}]*\})'
        content = re.sub(ttf_pattern, f'\\g<1>{market_data["ttf"]:.2f}\\g<2>', content)
        
        # Update Belpex KPI
        belpex_pattern = r'(const belpexKpi = \{[^}]*value: )[0-9.]+([^}]*\})'
        content = re.sub(belpex_pattern, f'\\g<1>{market_data["belpex"]:.2f}\\g<2>', content)
        
        # Update Storage KPI
        storage_pattern = r'(const storageKpi = \{[^}]*value: )[0-9.]+([^}]*\})'
        content = re.sub(storage_pattern, f'\\g<1>{market_data["eu_storage"]:.1f}\\g<2>', content)
        
        # Update Brent KPI
        brent_pattern = r'(const brentKpi = \{[^}]*value: )[0-9.]+([^}]*\})'
        content = re.sub(brent_pattern, f'\\g<1>{market_data["brent"]:.2f}\\g<2>', content)
        
        logger.info("Updated KPI values")
        return content
    
    def update_jsx_dates(self, content: str, market_data: Dict) -> str:
        """Update header en footer datums met tijd"""
        date_full, time_str, date_upper = self.format_datetime_full(market_data.get('timestamp'))
        
        # Update header: "MARKTANALYSE — 23 MAART 2026 · 20:30"
        header_pattern = r'(MARKTANALYSE — )\d{2} \w+ \d{4}( · \d{2}:\d{2})?'
        content = re.sub(header_pattern, f'\\g<1>{date_upper} · {time_str}', content)
        
        # Update footer: "Opgesteld: 23 maart 2026 · 20:30 ·"
        footer_pattern = r'(Opgesteld: )\d{1,2} \w+ \d{4}( · \d{2}:\d{2})?( ·)'
        content = re.sub(footer_pattern, f'\\g<1>{date_full} · {time_str}\\g<3>', content)
        
        logger.info(f"Updated dates to {date_full} {time_str}")
        return content
    
    def enforce_gasopslag_consistency(self, content: str, market_data: Dict) -> str:
        """Enforce gasopslag consistency across all sections in JSX"""
        storage_value = f"~{market_data['eu_storage']:.0f}%"
        date_str = self.format_date(market_data.get('timestamp'))
        
        # Parse date for full format: "23 mrt 2026"
        if market_data.get('timestamp'):
            dt = datetime.fromisoformat(market_data['timestamp'].replace('Z', '+00:00'))
        else:
            dt = datetime.now()
        month_short = {1:"jan",2:"feb",3:"mrt",4:"apr",5:"mei",6:"jun",
                      7:"jul",8:"aug",9:"sep",10:"okt",11:"nov",12:"dec"}[dt.month]
        date_label = f"{dt.day} {month_short} {dt.year}"
        
        # 1. Update Europese Gasvoorraden section label and value
        pattern1 = r'(\["EU-gemiddelde \()[^)]+\)", "~\d+%"'
        content = re.sub(pattern1, f'\\g<1>{date_label})", "{storage_value}"', content)
        
        # 2. Update Geopolitieke section text
        pattern2 = r'(Europese gasvoorraden staan op ~)\d+(% capaciteit )(op|eind) [^,]+( 2026)'
        content = re.sub(pattern2, f'\\g<1>{market_data["eu_storage"]:.0f}\\g<2>op {date_label}\\g<4>', content)
        
        logger.info(f"Enforced gasopslag consistency: {storage_value} ({date_label})")
        return content
    
    def update_confirmed_dates(self, content: str, market_data: Dict) -> str:
        """Update list of confirmed dates for checkmarks in JSX"""
        date_str = self.format_date(market_data.get('timestamp'))
        
        # Find the confirmed dates array and add new date if not present
        pattern = r'(const confirmed = \[)([^\]]+)(\]\.includes\(r\.date\))'
        
        def add_date_if_missing(match):
            dates_str = match.group(2)
            dates = [d.strip().strip('"').strip("'") for d in dates_str.split(',')]
            
            if date_str not in dates:
                dates.append(date_str)
                # Keep only last 10 confirmed dates
                dates = dates[-10:]
                new_dates_str = ', '.join([f'"{d}"' for d in dates])
                logger.info(f"Added {date_str} to confirmed dates")
                return f"{match.group(1)}{new_dates_str}{match.group(3)}"
            return match.group(0)
        
        content = re.sub(pattern, add_date_if_missing, content)
        
        # Also update footer text with confirmed dates list
        footer_pattern = r'(✓ = bevestigd officieel datapunt \()([^)]+)(\) ·)'
        content = re.sub(footer_pattern, add_date_if_missing, content)
        
        return content
    
    def update_html_marketdata(self, content: str, market_data: Dict) -> str:
        """Update marketData array in HTML"""
        date_str = self.format_date(market_data.get('timestamp'))
        
        # Vind marketData array
        pattern = r'(const marketData = \[[\s\S]*?)(\{ date: "[^"]+", ttf: [^,]+, belpex: [^,]+, storage: [^,]+, brent: [^}]+ \})([\s\S]*?\];)'
        
        new_entry = (
            f'{{ date: "{date_str}", '
            f'ttf: {market_data["ttf"]:.2f}, '
            f'belpex: {market_data["belpex"]:.2f}, '
            f'storage: {market_data["eu_storage"]:.1f}, '
            f'brent: {market_data["brent"]:.2f} }}'
        )
        
        def replacer(match):
            return match.group(1) + match.group(2) + ',\n        ' + new_entry + match.group(3)
        
        updated = re.sub(pattern, replacer, content, count=1)
        
        if updated == content:
            logger.warning("Could not update HTML marketData - pattern not found")
        else:
            logger.info(f"Added new HTML marketData entry for {date_str}")
        
        return updated
    
    def update_html_dates(self, content: str, market_data: Dict) -> str:
        """Update header en footer datums met tijd in HTML"""
        date_full, time_str, date_upper = self.format_datetime_full(market_data.get('timestamp'))
        
        # Update header: "MARKTANALYSE — 23 MAART 2026 · 20:30"
        header_pattern = r'(MARKTANALYSE — )\d{2} \w+ \d{4}( · \d{2}:\d{2})?'
        content = re.sub(header_pattern, f'\\g<1>{date_upper} · {time_str}', content)
        
        # Update footer: "Opgesteld: 23 maart 2026 · 20:30 ·"
        footer_pattern = r'(Opgesteld: )\d{1,2} \w+ \d{4}( · \d{2}:\d{2})?( ·)'
        content = re.sub(footer_pattern, f'\\g<1>{date_full} · {time_str}\\g<3>', content)
        
        logger.info(f"Updated HTML dates to {date_full} {time_str}")
        return content
    
    def update_html_kpis(self, content: str, market_data: Dict) -> str:
        """Update KPI waarden in HTML"""
        
        # Update KPI values in HTML
        kpi_updates = [
            (r'(id="ttf-value"[^>]*>)[0-9.]+', f'\\g<1>{market_data["ttf"]:.2f}'),
            (r'(id="belpex-value"[^>]*>)[0-9.]+', f'\\g<1>{market_data["belpex"]:.2f}'),
            (r'(id="storage-value"[^>]*>)[0-9.]+', f'\\g<1>{market_data["eu_storage"]:.1f}'),
            (r'(id="brent-value"[^>]*>)[0-9.]+', f'\\g<1>{market_data["brent"]:.2f}'),
        ]
        
        for pattern, replacement in kpi_updates:
            content = re.sub(pattern, replacement, content)
        
        logger.info("Updated HTML KPI values")
        return content
    
    def update_jsx_file(self, market_data: Dict):
        """Update JSX bestand"""
        logger.info(f"Updating {self.jsx_path}...")
        
        with open(self.jsx_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Voer updates uit
        content = self.update_jsx_rawdata(content, market_data)
        content = self.update_jsx_kpis(content, market_data)
        content = self.update_jsx_dates(content, market_data)
        
        # CONSISTENCY ENFORCEMENT
        content = self.enforce_gasopslag_consistency(content, market_data)
        content = self.update_confirmed_dates(content, market_data)
        
        # Sla op
        with open(self.jsx_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Successfully updated {self.jsx_path}")
    
    def enforce_html_gasopslag_consistency(self, content: str, market_data: Dict) -> str:
        """Enforce gasopslag consistency in HTML"""
        storage_value = f"~{market_data['eu_storage']:.0f}%"
        date_str = self.format_date(market_data.get('timestamp'))
        
        # Parse date for full format
        if market_data.get('timestamp'):
            dt = datetime.fromisoformat(market_data['timestamp'].replace('Z', '+00:00'))
        else:
            dt = datetime.now()
        month_short = {1:"jan",2:"feb",3:"mrt",4:"apr",5:"mei",6:"jun",
                      7:"jul",8:"aug",9:"sep",10:"okt",11:"nov",12:"dec"}[dt.month]
        date_label = f"{dt.day} {month_short} {dt.year}"
        
        # 1. Update JavaScript buildContext storageRows
        pattern1 = r"(\['EU-gemiddelde \()[^)]+\)', '~\d+%'"
        content = re.sub(pattern1, f"\\g<1>{date_label})', '{storage_value}'", content)
        
        # 2. Update geopolitical text in HTML
        pattern2 = r'(Europese gasvoorraden staan op ~)\d+(% capaciteit )(op|eind) [^,]+( 2026)'
        content = re.sub(pattern2, f'\\g<1>{market_data["eu_storage"]:.0f}\\g<2>op {date_label}\\g<4>', content)
        
        logger.info(f"Enforced HTML gasopslag consistency: {storage_value} ({date_label})")
        return content
    
    def update_html_confirmed_dates(self, content: str, market_data: Dict) -> str:
        """Update confirmed dates array in HTML JavaScript"""
        date_str = self.format_date(market_data.get('timestamp'))
        
        # Update confirmed array in buildPriceTable function
        pattern = r"(const confirmed = \[)([^\]]+)(\]\.includes\(r\.date\))"
        
        def add_date_if_missing(match):
            dates_str = match.group(2)
            dates = [d.strip().strip('"').strip("'") for d in dates_str.split(',')]
            
            if date_str not in dates:
                dates.append(date_str)
                dates = dates[-10:]  # Keep last 10
                new_dates_str = ', '.join([f"'{d}'" for d in dates])
                logger.info(f"Added {date_str} to HTML confirmed dates")
                return f"{match.group(1)}{new_dates_str}{match.group(3)}"
            return match.group(0)
        
        content = re.sub(pattern, add_date_if_missing, content)
        
        # Update footer text
        footer_pattern = r'(✓ = bevestigd officieel datapunt \()([^)]+)(\) ·)'
        content = re.sub(footer_pattern, add_date_if_missing, content)
        
        return content
    
    def update_html_file(self, market_data: Dict):
        """Update HTML bestand"""
        logger.info(f"Updating {self.html_path}...")
        
        with open(self.html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Voer updates uit
        content = self.update_html_marketdata(content, market_data)
        content = self.update_html_dates(content, market_data)
        content = self.update_html_kpis(content, market_data)
        
        # CONSISTENCY ENFORCEMENT
        content = self.enforce_html_gasopslag_consistency(content, market_data)
        content = self.update_html_confirmed_dates(content, market_data)
        
        # Sla op
        with open(self.html_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Successfully updated {self.html_path}")
    
    def run_update(self):
        """Voer volledige update uit"""
        logger.info(f"Starting report update (mode: {self.update_mode})...")

        market_data = self.load_market_data()
        ai_analysis = self.load_ai_analysis()

        # Step 1: Update JSX file
        self.update_jsx_file(market_data)

        # Step 2: Compile HTML from JSX (single source of truth)
        logger.info("Compiling offline.html from updated JSX...")
        compiler = JsxToHtmlCompiler()
        try:
            compiler.compile(self.jsx_path, self.template_path, self.html_path)
            logger.info(f"Successfully compiled {self.html_path} from {self.jsx_path}")
        except Exception as e:
            logger.error(f"Compilation failed: {e}")
            raise

        # Step 3: Validate synchronization between JSX and HTML
        logger.info("Validating JSX and HTML synchronization...")
        validator = SyncValidator()
        try:
            validator.validate_sync(self.jsx_path, self.html_path)
            logger.info("OK: JSX and HTML are perfectly synchronized")
        except ValueError as e:
            logger.error(f"Synchronization validation failed: {e}")
            raise

        if ai_analysis:
            logger.info("AI analysis available - consider manual integration")

        logger.info("Report update completed successfully")

def main():
    updater = ReportUpdater()
    
    try:
        updater.run_update()
        
        print("\n=== Report Update Voltooid ===")
        print(f"Mode: {updater.update_mode}")
        print(f"JSX: {updater.jsx_path}")
        print(f"HTML: {updater.html_path}")
    
    except FileNotFoundError as e:
        logger.error(f"Required file not found: {e}")
        return 1
    except Exception as e:
        logger.error(f"Report update failed: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
