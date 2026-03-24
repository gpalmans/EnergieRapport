"""
Report Updater voor EnergieRapport
Update JSX bestand met nieuwe marktdata
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReportUpdater:
    def __init__(self):
        self.jsx_path = 'src/EnergieRapport.jsx'
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
        """Update rawData array in JSX - update existing entry or add new one"""
        date_str = self.format_date(market_data.get('timestamp'))
        
        # Check if date already exists in rawData
        date_pattern = rf'\{{ date: "{re.escape(date_str)}", ttf: [\d.]+, belpex: [\d.]+, note: "[^"]*" \}}'
        existing_entry = re.search(date_pattern, content)
        
        if existing_entry:
            # Update existing entry
            updated_entry = (
                f'{{ date: "{date_str}", '
                f'ttf: {market_data["ttf"]:.2f}, '
                f'belpex: {market_data["belpex"]:.2f}, note: "Vandaag" }}'
            )
            content = re.sub(date_pattern, updated_entry, content)
            logger.info(f"Updated existing rawData entry for {date_str}")
        else:
            # Add new entry at the end of array (before closing bracket)
            pattern = r'(const rawData = \[[\s\S]*?)(\{ date: "[^"]+", ttf: [^,]+, belpex: [^,]+, note: "[^"]*" \})([\s\S]*?\];)'
            
            new_entry = (
                f'  {{ date: "{date_str}", '
                f'ttf: {market_data["ttf"]:.2f}, '
                f'belpex: {market_data["belpex"]:.2f}, note: "Vandaag" }}'
            )
            
            def replacer(match):
                return match.group(1) + match.group(2) + ',\n' + new_entry + match.group(3)
            
            updated = re.sub(pattern, replacer, content, count=1)
            
            if updated == content:
                logger.warning("Could not update rawData - pattern not found")
            else:
                logger.info(f"Added new rawData entry for {date_str}")
            
            content = updated
        
        return content
    
    def update_jsx_kpis(self, content: str, market_data: Dict) -> str:
        """Update KPI waarden in JSX array - preserve color codes"""
        
        # Extract previous values from rawData to calculate changes
        prev_ttf, prev_belpex = self.get_previous_values(content)
        
        # Calculate percentage changes
        ttf_change = self.calculate_change(market_data["ttf"], prev_ttf)
        belpex_change = self.calculate_change(market_data["belpex"], prev_belpex)
        brent_change = self.calculate_change(market_data["brent"], 101.55)  # vs previous day
        
        # Determine color codes based on changes
        try:
            # Extract just the number part (handle "+1.1%" or "-1.0%")
            ttf_num = ttf_change.split('%')[0].strip()
            ttf_change_val = float(ttf_num)
            ttf_color = "#22c55e" if ttf_change_val < 0 else "#ef4444"
        except:
            ttf_color = "#ef4444"
            
        try:
            belpex_num = belpex_change.split('%')[0].strip()
            belpex_change_val = float(belpex_num)
            belpex_color = "#22c55e" if belpex_change_val < 0 else "#ef4444"
        except:
            belpex_color = "#ef4444"
            
        try:
            brent_num = brent_change.split('%')[0].strip()
            brent_change_val = float(brent_num)
            brent_color = "#22c55e" if brent_change_val < 0 else "#ef4444"
        except:
            brent_color = "#ef4444"
        
        # Update TTF KPI - simple pattern matching entire line
        ttf_line_pattern = r'\["TTF Gas vandaag",\s*"€[\d.]+",\s*"/MWh",\s*"[^"]*",\s*"#[0-9a-f]+"\]'
        ttf_replacement = f'["TTF Gas vandaag", "€{market_data["ttf"]:.2f}", "/MWh", "{ttf_change}", "{ttf_color}"]'
        content = re.sub(ttf_line_pattern, ttf_replacement, content)
        
        # Update Belpex KPI
        belpex_line_pattern = r'\["Belpex Elektr\. vandaag",\s*"€[\d.]+",\s*"/MWh",\s*"[^"]*",\s*"#[0-9a-f]+"\]'
        belpex_replacement = f'["Belpex Elektr. vandaag", "€{market_data["belpex"]:.2f}", "/MWh", "{belpex_change}", "{belpex_color}"]'
        content = re.sub(belpex_line_pattern, belpex_replacement, content)
        
        # Update Storage KPI
        storage_line_pattern = r'\["België Gasopslag",\s*"~[\d.]+%",\s*" cap\.",\s*"[^"]*",\s*"#[0-9a-f]+"\]'
        storage_replacement = f'["België Gasopslag", "~{market_data["eu_storage"]:.0f}%", " cap.", "kritiek laag niveau", "#ef4444"]'
        content = re.sub(storage_line_pattern, storage_replacement, content)
        
        # Update Brent KPI
        brent_line_pattern = r'\["Brent Ruwe Olie",\s*"\$[\d.]+",\s*"/vat",\s*"[^"]*",\s*"#[0-9a-f]+"\]'
        brent_replacement = f'["Brent Ruwe Olie", "${market_data["brent"]:.2f}", "/vat", "{brent_change}", "{brent_color}"]'
        content = re.sub(brent_line_pattern, brent_replacement, content)
        
        logger.info("Updated KPI values with colors and changes")
        return content
    
    def get_previous_values(self, content: str) -> tuple:
        """Extract previous day values from rawData"""
        # Find all rawData entries
        pattern = r'\{ date: "([^"]+)", ttf: ([\d.]+), belpex: ([\d.]+), note: "([^"]*)" \}'
        entries = re.findall(pattern, content)
        
        if not entries:
            return 53.25, 72.78  # fallback values
        
        # Sort entries by date to get chronological order
        # Convert date format from DD/MM to comparable format
        def date_key(date_str):
            day, month = date_str.split('/')
            return f"{month.zfill(2)}{day.zfill(2)}"
        
        entries.sort(key=lambda x: date_key(x[0]))
        
        # Find the current "Vandaag" entry and return the previous one
        for i, (date, ttf, belpex, note) in enumerate(entries):
            if note == "Vandaag" and i > 0:
                prev_date, prev_ttf, prev_belpex, _ = entries[i-1]
                return float(prev_ttf), float(prev_belpex)
        
        # If no "Vandaag" found, return the last entry's previous
        if len(entries) >= 2:
            return float(entries[-2][1]), float(entries[-2][2])
        
        return 53.25, 72.78  # fallback values
    
    def calculate_change(self, current: float, previous: float) -> str:
        """Calculate percentage change and format as string"""
        if previous == 0:
            return "0.0% vs gisteren"
        
        change_pct = ((current - previous) / abs(previous)) * 100
        direction = "+" if change_pct > 0 else ""
        return f"{direction}{change_pct:.1f}% vs gisteren"
    
    def update_jsx_kpi_variables(self, content: str, market_data: Dict) -> str:
        """Update KPI variables in JSX for PDF and other applications"""
        
        # Update currentTTF variable
        ttf_var_pattern = r'(const currentTTF = )[\d.]+(;)'
        content = re.sub(ttf_var_pattern, f'\\g<1>{market_data["ttf"]:.2f}\\g<2>', content)
        
        # Update currentBelpex variable
        belpex_var_pattern = r'(const currentBelpex = )[\d.]+(;)'
        content = re.sub(belpex_var_pattern, f'\\g<1>{market_data["belpex"]:.2f}\\g<2>', content)
        
        # Update currentStorage variable
        storage_var_pattern = r'(const currentStorage = )[\d.]+(;)'
        content = re.sub(storage_var_pattern, f'\\g<1>{market_data["eu_storage"]:.1f}\\g<2>', content)
        
        # Update currentBrent variable
        brent_var_pattern = r'(const currentBrent = )[\d.]+(;)'
        content = re.sub(brent_var_pattern, f'\\g<1>{market_data["brent"]:.2f}\\g<2>', content)
        
        logger.info("Updated KPI variables")
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
    
    def update_critical_header(self, content: str, market_data: Dict) -> str:
        """Update critical market situation header with current KPI values"""
        
        # Create new header line with current values
        new_header = f'            Hormuz crisis dag 21+ · TTF €{market_data["ttf"]:.2f} (-11.4% vs piek) · Brent ${market_data["brent"]:.2f} · Force majeure Qatar/Kuwait/UAE · Belgische gasreserves {market_data["eu_storage"]:.0f}%'
        
        # Find the exact header line and replace it
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'Hormuz crisis dag 21+ · TTF €' in line and 'Brent $' in line and ('EU opslag' in line or 'Belgische gasreserves' in line):
                lines[i] = new_header
                logger.info(f"Updated critical header: TTF €{market_data['ttf']:.2f}, Brent ${market_data['brent']:.2f}, Storage {market_data['eu_storage']:.0f}%")
                break
        
        return '\n'.join(lines)
    
    def update_analysis_values(self, content: str, market_data: Dict) -> str:
        """Update hardcoded values in analysis sections to sync with API data"""
        
        # Update TTF value in analysis section
        ttf_analysis_pattern = r'(TTF daalde vandaag naar €)[\d.]+(/MWh)'
        content = re.sub(ttf_analysis_pattern, f'\\g<1>{market_data["ttf"]:.2f}\\g<2>', content)
        
        # Update Brent value in analysis
        brent_analysis_pattern = r'(Brent crude handelt op \$)[\d.]+(/vat)'
        content = re.sub(brent_analysis_pattern, f'\\g<1>{market_data["brent"]:.2f}\\g<2>', content)
        
        # Update Belpex value in notification
        belpex_notification_pattern = r'(Belpex op \d{2}/03 \()€[\d.]+( daggemiddelde\))'
        content = re.sub(belpex_notification_pattern, f'\\g<1>€{market_data["belpex"]:.2f}\\g<2>', content)
        
        logger.info(f"Updated analysis values: TTF €{market_data['ttf']:.2f}, Brent ${market_data['brent']:.2f}, Belpex €{market_data['belpex']:.2f}")
        return content
    
    def update_geopolitical_references(self, content: str, market_data: Dict) -> str:
        """Update geopolitical references to use Belgian storage instead of EU storage"""
        
        # Update geopolitical analysis section
        geopolitical_pattern = r'(EU opslag onder druk)'
        content = re.sub(geopolitical_pattern, 'Belgische opslag onder druk', content)
        
        # Update advice section
        advice_pattern = r'(EN EU opslag boven 35% eind mei)'
        content = re.sub(advice_pattern, f'EN Belgische opslag boven 35% eind mei', content)
        
        logger.info("Updated geopolitical references to Belgian storage")
        return content
    
    def update_storage_calculation(self, content: str, market_data: Dict) -> str:
        """Update storage calculation: nog te vullen = 90% doel - huidig niveau"""
        
        # Calculate correct remaining percentage
        remaining_pct = 90 - market_data["eu_storage"]
        
        # Update the "Nog te vullen" calculation with simpler pattern
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '["Nog te vullen (apr–okt)"' in line and '~' in line and 'pct-punten' in line:
                lines[i] = f'              ["Nog te vullen (apr–okt)",    "~{remaining_pct:.0f} pct-punten", "#f97316"],'
                logger.info(f"Updated storage calculation: {remaining_pct:.0f}% remaining to fill (90% - {market_data['eu_storage']:.0f}% current)")
                break
        
        return '\n'.join(lines)
    
    def find_ttf_peak(self, content: str) -> float:
        """Find TTF peak value in rawData"""
        pattern = r'\{ date: "[^"]+", ttf: ([\d.]+), belpex: [\d.]+, note: "([^"]*)" \}'
        entries = re.findall(pattern, content)
        
        if not entries:
            return 56.0  # fallback peak
        
        ttf_values = [float(ttf) for ttf, note in entries if "Piek" in note]
        return max(ttf_values) if ttf_values else 56.0
    
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
        pattern1 = r'(\["BE-gemiddelde \()[^)]+\)", "~\d+%"'
        content = re.sub(pattern1, f'\\g<1>{date_label})", "{storage_value}"', content)
        
        # 2. Update Geopolitieke section text
        pattern2 = r'(Europese gasvoorraden staan op ~)\d+(% capaciteit )(op|eind) [^,]+( 2026)'
        content = re.sub(pattern2, f'\\g<1>{market_data["eu_storage"]:.0f}\\g<2>op {date_label}\\g<4>', content)
        
        logger.info(f"Enforced gasopslag consistency: {storage_value} ({date_label})")
        return content
    
    def update_confirmed_dates(self, content: str, market_data: Dict) -> str:
        """Update list of confirmed dates for checkmarks in JSX - all API dates are confirmed"""
        
        # Extract all dates from rawData since they come from reliable API sources
        pattern = r'\{ date: "([^"]+)", ttf: [\d.]+, belpex: [\d.]+, note: "([^"]*)" \}'
        entries = re.findall(pattern, content)
        
        if not entries:
            return content
        
        # Get all unique dates from rawData
        dates = list(set([date for date, note in entries]))
        
        # Sort dates chronologically
        def date_key(date_str):
            day, month = date_str.split('/')
            return f"{month.zfill(2)}{day.zfill(2)}"
        
        dates.sort(key=date_key)
        
        # Keep only last 15 confirmed dates for performance
        dates = dates[-15:]
        new_dates_str = ', '.join([f'"{d}"' for d in dates])
        
        # Update confirmed dates array
        confirmed_pattern = r'(const confirmed = \[)[^\]]*(\]\.includes\(r\.date\))'
        content = re.sub(confirmed_pattern, f'\\g<1>{new_dates_str}\\g<2>', content)
        
        # Also update footer text with confirmed dates list
        footer_pattern = r'(✓ = bevestigd officieel datapunt \()([^)]+)(\) ·)'
        content = re.sub(footer_pattern, f'\\g<1>{new_dates_str}\\g<3>', content)
        
        logger.info(f"Updated confirmed dates: {len(dates)} API-driven dates marked as confirmed")
        return content
    
    def update_jsx_file(self, market_data: Dict):
        """Update JSX bestand"""
        logger.info(f"Updating {self.jsx_path}...")
        
        with open(self.jsx_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Voer updates uit
        content = self.update_jsx_rawdata(content, market_data)
        content = self.update_jsx_kpis(content, market_data)
        content = self.update_jsx_kpi_variables(content, market_data)
        content = self.update_jsx_dates(content, market_data)
        content = self.update_critical_header(content, market_data)
        content = self.update_analysis_values(content, market_data)
        content = self.update_geopolitical_references(content, market_data)
        content = self.update_storage_calculation(content, market_data)
        
        # CONSISTENCY ENFORCEMENT
        content = self.enforce_gasopslag_consistency(content, market_data)
        content = self.update_confirmed_dates(content, market_data)
        
        # Sla op
        with open(self.jsx_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Successfully updated {self.jsx_path}")
    
    def run_update(self):
        """Voer volledige update uit"""
        logger.info(f"Starting report update (mode: {self.update_mode})...")

        market_data = self.load_market_data()
        ai_analysis = self.load_ai_analysis()

        # Step 1: Update JSX file
        self.update_jsx_file(market_data)

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
    
    except FileNotFoundError as e:
        logger.error(f"Required file not found: {e}")
        return 1
    except Exception as e:
        logger.error(f"Report update failed: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
