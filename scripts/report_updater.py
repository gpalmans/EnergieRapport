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
            # Timestamp from data collector is already local time (CET)
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            # Remove timezone info to treat as local time
            dt = dt.replace(tzinfo=None)
        else:
            # Use local time
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
        
        # First, reset any existing "Vandaag" note to empty string (only one Vandaag allowed)
        content = re.sub(r'note: "Vandaag"', 'note: ""', content)
        logger.info("Reset previous Vandaag entries to empty note")
        
        # Check if date already exists in rawData
        date_pattern = rf'\{{ date: "{re.escape(date_str)}", ttf: [\d.]+, belpex: [\d.]+, brent: [\d.]+, storage: [\d.]+, note: "[^"]*" \}}'
        existing_entry = re.search(date_pattern, content)
        
        if existing_entry:
            # Update existing entry
            updated_entry = (
                f'{{ date: "{date_str}", '
                f'ttf: {market_data["ttf"]:.2f}, '
                f'belpex: {market_data["belpex"]:.2f}, '
                f'brent: {market_data["brent"]:.2f}, '
                f'storage: {market_data["eu_storage"]:.1f}, note: "Vandaag" }}'
            )
            content = re.sub(date_pattern, updated_entry, content)
            logger.info(f"Updated existing rawData entry for {date_str}")
        else:
            # Add new entry at the end of array (before closing bracket or .sort)
            # Pattern handles both ]; and .sort((a, b) => after the array
            # Also handles optional comma after last entry
            pattern = r'(const rawData = \[[\s\S]*?)(\{ date: "[^"]+", ttf: [^,]+, belpex: [^,]+, brent: [^,]+, storage: [^,]+, note: "[^"]*" \}),?\s*(\]\.sort|\];)'
            
            new_entry = (
                f'  {{ date: "{date_str}", '
                f'ttf: {market_data["ttf"]:.2f}, '
                f'belpex: {market_data["belpex"]:.2f}, '
                f'brent: {market_data["brent"]:.2f}, '
                f'storage: {market_data["eu_storage"]:.1f}, note: "Vandaag" }}'
            )
            
            def replacer(match):
                # match.group(1) = everything before last entry
                # match.group(2) = last entry (with optional comma)
                # match.group(3) = ].sort or ];
                return match.group(1) + match.group(2) + ',\n' + new_entry + '\n' + match.group(3)
            
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
        
        # Update KPIs using line-by-line replacement
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if '["TTF Gas vandaag"' in line:
                lines[i] = f'          ["TTF Gas vandaag", "€{market_data["ttf"]:.2f}", "/MWh", "{ttf_change}", "{ttf_color}"],'
            elif '["Belpex Elektr. vandaag"' in line:
                lines[i] = f'          ["Belpex Elektr. vandaag", "€{market_data["belpex"]:.2f}", "/MWh", "{belpex_change}", "{belpex_color}"],'
            elif '["België Gasopslag"' in line:
                lines[i] = f'          ["België Gasopslag", "~{market_data["eu_storage"]:.0f}%", " cap.", "kritiek laag niveau", "#ef4444"],'
            elif '["Brent Ruwe Olie"' in line:
                lines[i] = f'          ["Brent Ruwe Olie", "${market_data["brent"]:.2f}", "/vat", "{brent_change}", "{brent_color}"],'
        
        content = '\n'.join(lines)
        
        logger.info("Updated KPI values with colors and changes")
        return content
    
    def get_previous_values(self, content: str) -> tuple:
        """Extract previous day values from rawData"""
        # Find all rawData entries including brent and storage
        pattern = r'\{ date: "([^"]+)", ttf: ([\d.]+), belpex: ([\d.]+), brent: [\d.]+, storage: [\d.]+, note: "([^"]*)" \}'
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
        
        # Update header: "MARKTANALYSE — 23 MAART 2026 · 20:30 CET"
        header_pattern = r'(MARKTANALYSE — )\d{2} \w+ \d{4}( · \d{2}:\d{2})( CET)?'
        content = re.sub(header_pattern, f'\\g<1>{date_upper} · {time_str} CET', content)
        
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
    
    def update_geopolitical_content(self, content: str, market_data: Dict) -> str:
        """Update geopolitical content to sync with current KPI values"""
        
        # Update Brent price in geopolitical analysis
        brent_pattern = r'(Brent crude handelt op \$)[\d.]+(/vat)'
        content = re.sub(brent_pattern, f'\\g<1>{market_data["brent"]:.2f}\\g<2>', content)
        
        # Update Brent percentage change ONLY in geopolitical section (not in KPIs)
        # Find the Brent Prijsstijging section and update the percentage there
        brent_section_pattern = r'(\["Brent Prijsstijging",.*?Brent crude handelt op \$[\d.]+/vat \()[\+\-\d.]+%( vs gisteren)'
        brent_change = self.calculate_brent_change(content, market_data["brent"])
        content = re.sub(brent_section_pattern, f'\\g<1>{brent_change}\\g<2>', content)
        
        # Update TTF references in geopolitical context
        ttf_pattern = r'(TTF-prijzen)[:]?[^,]*'  # More flexible pattern
        content = re.sub(ttf_pattern, f'TTF-prijzen: €{market_data["ttf"]:.2f}', content)
        
        # Update Mega Tariefstijging percentages based on actual TTF movement
        ttf_change_pct = self.get_ttf_change_percentage(content, market_data["ttf"])
        mega_gas_increase = max(14, int(abs(ttf_change_pct) * 0.8))  # Scale with actual change
        mega_elec_increase = max(12, int(abs(ttf_change_pct) * 0.6))
        
        mega_pattern = r'(gas \+)[\d]+(% tot \+)[\d]+(%, elektriciteit \+)[\d]+(% tot \+)[\d]+(%)'
        content = re.sub(mega_pattern, f'\\g<1>{mega_gas_increase}\\g<2>{mega_gas_increase+15}\\g<3>{mega_elec_increase}\\g<4>{mega_elec_increase+10}\\g<5>', content)
        
        # Update Energy Sector rotation percentage
        sector_rotation_pct = min(8, max(3, int(abs(ttf_change_pct) * 0.3)))
        sector_pattern = r'(Energy Select Sector SPDR stijgt \+)[\d]+(% in maart)'
        content = re.sub(sector_pattern, f'\\g<1>{sector_rotation_pct}\\g<2>', content)
        
        logger.info(f"Updated geopolitical content: Brent ${market_data['brent']:.2f}, TTF €{market_data['ttf']:.2f}, Mega gas +{mega_gas_increase}%, Sector +{sector_rotation_pct}%")
        return content
    
    def calculate_brent_change(self, content: str, current_brent: float) -> str:
        """Calculate Brent percentage change vs previous day"""
        # Extract previous Brent from rawData or use fallback
        previous_brent = self.get_previous_brent(content)
        if previous_brent > 0:
            change_pct = ((current_brent - previous_brent) / previous_brent) * 100
            return f"{change_pct:+.1f}%"
        return "+1.9%"  # Fallback
    
    # def update_iea_strategic_reserves (disabled)(self, content: str, market_data: Dict) -> str:
        """Update IEA Strategic Oil Reserves content with current Brent data"""
        
        # Calculate price movement and impact
        brent_price = market_data["brent"]
        brent_change = self.calculate_brent_change(content, brent_price)
        
        # Update main analysis text with current price
        # Replace the price range and current price reference
        main_pattern = r'(Brent daalde initieel van \$119 naar \$101/vat, maar stabiliseert nu rond )\$112-113(/vat — wat aangeeft dat de markt de structurele supply-shock zwaarder weegt dan de tijdelijke buffermaatregel\.)'
        content = re.sub(main_pattern, f'\\g<1>${brent_price:.2f}\\g<2>', content)
        
        # Update the market reaction data in the table
        market_reaction_pattern = r'(\["Marktreactie",\s*"Brent: )\$119 → \$101(/vat \(daling na IEA release)"\])'
        content = re.sub(market_reaction_pattern, f'\\g<1>${brent_price:.2f} ({brent_change.replace(" vs gisteren", "")})\\g<2>', content)
        
        # Update the effectiveness analysis based on current price
        if brent_price > 110:
            effectiveness = "Beperkt: prijs >$110/vat toont structurele impact Hormuz-blokkade > IEA buffer"
        elif brent_price > 100:
            effectiveness = "Matig: prijs $100-110/vat toont gedeeltelijke succes IEA maatregel"
        else:
            effectiveness = "Effectief: prijs <$100/vat toont succesvolle IEA interventie"
        
        effectiveness_pattern = r'(\["Effectiviteit",\s*")[^"]*("\])'
        content = re.sub(effectiveness_pattern, f'\\g<1>{effectiveness}\\g<2>', content)
        
        # Update the status date to current date
        current_date = self.format_date(market_data.get('timestamp'))
        status_pattern = r'(\["Status",\s*")[^"]*("\])'
        content = re.sub(status_pattern, f'\\g<1>Gezamenlijke vrijgave actief; huidige prijs ${brent_price:.2f}/vat ({current_date})\\g<2>', content)
        
        logger.info(f"Updated IEA Strategic Reserves: Brent ${brent_price:.2f}, change {brent_change}, effectiveness: {effectiveness}")
        return content
    
    def get_previous_brent(self, content: str) -> float:
        """Extract previous Brent value from content"""
        # Look for recent Brent reference in content or use fallback
        brent_match = re.search(r'Brent.*?\$([\d.]+)', content)
        if brent_match:
            return float(brent_match.group(1))
        return 102.5  # Fallback
    
    def get_ttf_change_percentage(self, content: str, current_ttf: float) -> float:
        """Calculate TTF change percentage from rawData"""
        # Use existing get_previous_values method
        prev_values = self.get_previous_values(content)
        if prev_values and len(prev_values) >= 2:
            prev_ttf = prev_values[0]  # First element is TTF
            return ((current_ttf - prev_ttf) / prev_ttf) * 100
        return 15.0  # Fallback
    
    def find_ttf_peak(self, content: str) -> float:
        """Find TTF peak value in rawData"""
        pattern = r'\{ date: "[^"]+", ttf: ([\d.]+), belpex: [\d.]+, brent: [\d.]+, storage: [\d.]+, note: "([^"]*)" \}'
        entries = re.findall(pattern, content)
        
        if not entries:
            return 56.0  # fallback peak
        
        ttf_values = [float(ttf) for ttf, note in entries if "Piek" in note]
        return max(ttf_values) if ttf_values else 56.0
    
    def update_sources_section(self, content: str, market_data: Dict) -> str:
        """Update sources section with current data and remove outdated dates"""
        date_str = self.format_date(market_data.get('timestamp'))
        
        # Update Trading Economics references with generic descriptions
        old_ttf_pattern = r'Trading Economics — TTF \d{2}/\d{2}/\d{4}.*?url: "https://tradingeconomics.com/commodity/eu-natural-gas"'
        new_ttf_ref = 'Trading Economics — TTF Natural Gas', 'Real-time TTF gas prices and historical data', 'url: "https://tradingeconomics.com/commodity/eu-natural-gas"'
        
        # Update Trading Economics Brent reference  
        old_brent_pattern = r'Trading Economics — Brent Oil \d{2}/\d{2}/\d{4}.*?url: "https://tradingeconomics.com/commodity/brent-crude-oil"'
        new_brent_ref = 'Trading Economics — Brent Crude Oil', 'Real-time Brent oil prices and historical data', 'url: "https://tradingeconomics.com/commodity/brent-crude-oil"'
        
        # Update OilPriceAPI references
        old_oilprice_pattern = r'OilPriceAPI — Live TTF Data \(\d{2}/\d{2}/\d{4}\).*?url: "https://www.oilpriceapi.com/live/dutch-ttf-gas-price"'
        new_oilprice_ref = 'OilPriceAPI — Live TTF Data', 'Real-time Dutch TTF gas price API', 'url: "https://www.oilpriceapi.com/live/dutch-ttf-gas-price"'
        
        # Update Elexys reference
        old_elexys_pattern = r'Elexys — Belpex Hourly Data.*?url: "https://www.elexys.be/en/insights/epex-spot"'
        new_elexys_ref = 'Elexys — Belpex Hourly Data', 'Official hourly Belpex prices and market analysis', 'url: "https://www.elexys.be/en/insights/epex-spot"'
        
        # Apply updates using regex
        content = re.sub(old_ttf_pattern, f'                {{ n: "{new_ttf_ref[0]}", d: "{new_ttf_ref[1]}", {new_ttf_ref[2]} }}', content)
        content = re.sub(old_brent_pattern, f'                {{ n: "{new_brent_ref[0]}", d: "{new_brent_ref[1]}", {new_brent_ref[2]} }}', content)
        content = re.sub(old_oilprice_pattern, f'                {{ n: "{new_oilprice_ref[0]}", d: "{new_oilprice_ref[1]}", {new_oilprice_ref[2]} }}', content)
        content = re.sub(old_elexys_pattern, f'                {{ n: "{new_elexys_ref[0]}", d: "{new_elexys_ref[1]}", {new_elexys_ref[2]} }}', content)
        
        # Remove outdated geopolitical references with specific dates
        outdated_patterns = [
            r'                { n: "De Standaard — Energiecrisis Analyse \(\d{2}/\d{2}/\d{4}\).*?},?\n',
            r'                { n: "De Standaard — Benzineprijzen Stijgen \(\d{2}/\d{2}/\d{4}\).*?},?\n',
            r'                { n: "De Standaard — VS Dronefabrieken \(\d{2}/\d{2}/\d{4}\).*?},?\n',
            r'                { n: "HLN — Trump Briefing \(\d{2}/\d{2}/\d{4}\).*?},?\n',
            r'                { n: "CBS News — Iran War Escalation \(\d{2}/\d{2}/\d{4}\).*?},?\n',
            r'                { n: "NBC News — Gas Field Damage \(\d{2}/\d{2}/\d{4}\).*?},?\n',
            r'                { n: "Reuters — Iran War Energy Shock \(\d{2}/\d{2}/\d{4}\).*?},?\n',
            r'                { n: "WSJ — Qatar LNG Impact \(\d{2}/\d{2}/\d{4}\).*?},?\n',
            r'                { n: "Fortune — Oil Price Surge \(\d{2}/\d{2}/\d{4}\).*?},?\n',
            r'                { n: "Test-Aankoop — Mega Tariefstijging \(\d{2}/\d{2}/\d{4}\).*?},?\n',
            r'                { n: "Eneco — TTF Volatiliteit \(\d{2}/\d{2}/\d{4}\).*?},?\n',
            r'                { n: "FinancialContent — Energy Sector Rotation \(\d{2}/\d{2}/\d{4}\).*?},?\n',
            r'                { n: "CNBC — IEA Consumentenadvies \(\d{2}/\d{2}/\d{4}\).*?},?\n',
            r'                { n: "Trading Economics — TTF Gas \(\d{2}/\d{2}/\d{4}\).*?},?\n',
            r'                { n: "Trading Economics — Brent Oil \(\d{2}/\d{2}/\d{4}\).*?},?\n',
            r'                { n: "CNBC — Brent Oil Analysis \(\d{2}/\d{2}/\d{4}\).*?},?\n',
            r'                { n: "EU Energy Live — Belpex \(\d{2}/\d{2}/\d{4}\).*?},?\n',
            r'                { n: "EnergyPrices.eu — Belgium \(\d{2}/\d{2}/\d{4}\).*?},?\n',
            r'                { n: "TradingPedia — LNG Glut Analysis \(\d{2}/\d{2}/\d{4}\).*?},?\n',
            r'                { n: "Gas to Power Journal — TTF analysis.*?€\d+.*?},?\n',
            # Fix for duplicate entries with extra spaces
            r'                { n: "                { n: "[^"]+".*?} },?\n',
        ]
        
        for pattern in outdated_patterns:
            content = re.sub(pattern, '', content, flags=re.MULTILINE)
        
        logger.info(f"Updated sources section with generic descriptions (no specific prices)")
        return content
    
    def calculate_ttf_change(self, content: str) -> float:
        """Calculate TTF change vs previous day"""
        pattern = r'\{ date: "[^"]+", ttf: ([\d.]+), belpex: [\d.]+, brent: [\d.]+, storage: [\d.]+, note: "([^"]*)" \}'
        entries = re.findall(pattern, content)
        
        if len(entries) >= 2:
            current_ttf = float(entries[-1][0])
            prev_ttf = float(entries[-2][0])
            return ((current_ttf - prev_ttf) / prev_ttf) * 100
        return 0.0  # fallback
    
    def calculate_belpex_change(self, content: str) -> float:
        """Calculate Belpex change vs previous day"""
        pattern = r'\{ date: "[^"]+", ttf: [\d.]+, belpex: ([\d.]+), brent: [\d.]+, storage: [\d.]+, note: "([^"]*)" \}'
        entries = re.findall(pattern, content)
        
        if len(entries) >= 2:
            current_belpex = float(entries[-1][0])
            prev_belpex = float(entries[-2][0])
            return ((current_belpex - prev_belpex) / prev_belpex) * 100
        return 0.0  # fallback
    
    def enforce_gasopslag_consistency(self, content: str, market_data: Dict) -> str:
        """Enforce gasopslag consistency across all sections in JSX"""
        storage_value = f"~{market_data['eu_storage']:.0f}%"
        date_str = self.format_date(market_data.get('timestamp'))
        
        # Parse date for full format: "23 mrt 2026"
        if market_data.get('timestamp'):
            dt = datetime.fromisoformat(market_data['timestamp'].replace('Z', '+00:00'))
        else:
            # Use UTC time and convert to CET
            from datetime import timezone, timedelta
            dt = datetime.now(timezone.utc) + timedelta(hours=1)
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
    
    # def update_confirmed_dates (disabled - footer is static)(self, content: str, market_data: Dict) -> str:
        """Update list of confirmed dates for checkmarks in JSX - all API dates are confirmed"""

        # Extract all dates from rawData since they come from reliable API sources
        pattern = r'\{ date: "([^"]+)", ttf: [\d.]+, belpex: [\d.]+, brent: [\d.]+, storage: [\d.]+, note: "([^"]*)" \}'
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
    
    # ── Wekelijkse uitbreidingen ──────────────────────────────────────────────

    def trim_rawdata_to_30_days(self, content: str) -> str:
        """Trim rawData zodat enkel de laatste 30 handelsdagen bewaard blijven."""
        pattern = r'\{ date: "(\d{2}/\d{2})", ttf: [\d.\-]+, belpex: [\d.\-]+, brent: [\d.]+, storage: [\d.]+, note: "[^"]*" \}'
        entries = re.findall(pattern, content)
        if len(entries) <= 30:
            logger.info(f"rawData heeft {len(entries)} entries — geen trim nodig")
            return content

        # Sorteer chronologisch (DD/MM → MMDD voor vergelijking)
        def sort_key(d):
            day, month = d.split('/')
            return month + day

        sorted_dates = sorted(set(entries), key=sort_key)
        dates_to_keep = set(sorted_dates[-30:])
        dates_to_remove = set(sorted_dates[:-30])

        lines = content.split('\n')
        new_lines = []
        removed = 0
        for line in lines:
            skip = False
            for d in dates_to_remove:
                if f'date: "{d}"' in line:
                    skip = True
                    removed += 1
                    break
            if not skip:
                new_lines.append(line)

        logger.info(f"rawData getrimd: {removed} oude entries verwijderd, {len(dates_to_keep)} bewaard")
        return '\n'.join(new_lines)

    def apply_ai_geopolitical(self, content: str, ai_data: Dict) -> str:
        """Vervang de geopolitieke items array met AI-gegenereerde items."""
        items = ai_data.get('geopolitical_items', [])
        if not items:
            logger.warning("Geen geopolitieke items in AI-analyse — sectie ongewijzigd")
            return content

        # Genereer nieuwe items-string
        items_js = ',\n'.join([
            f'              ["{item["titel"]}", "{item["color"]}", "{item["tekst"]}"]'
            for item in items
        ])

        # Vervang de array tussen {[ en ].map( in de geopolitieke sectie
        pattern = (
            r'(⚔️ Geopolitieke Situatie[^\n]*\n\s*\{?\s*\[)'
            r'([\s\S]*?)'
            r'(\]\.map\(\(\[titel, color, tekst\]\))'
        )
        replacement = r'\g<1>\n' + items_js + r'\n            \g<3>'
        new_content = re.sub(pattern, replacement, content, count=1)

        if new_content == content:
            logger.warning("Geopolitieke items pattern niet gevonden — sectie ongewijzigd")
        else:
            logger.info(f"Geopolitieke sectie bijgewerkt: {len(items)} items")

        return new_content

    def apply_ai_alert(self, content: str, ai_data: Dict) -> str:
        """Update de alert banner met AI-gegenereerde tekst."""
        alert = ai_data.get('alert', {})
        if not alert:
            return content

        title = alert.get('title', '')
        text  = alert.get('text', '')
        is_critical = alert.get('is_critical', False)

        border_color = "#ef4444" if is_critical else "#f97316"
        text_color   = "#fca5a5" if is_critical else "#fdba74"
        bg_color     = "#7c131322" if is_critical else "#7c2d1222"
        icon         = "⚠️" if is_critical else "📉"

        # Vervang de volledige alert div
        pattern = (
            r'(\{/\* ALERT \*/\}\s*)'
            r'<div style=\{\{[^}]*background: "[^"]*"[^}]*border: "1px solid [^"]*"[^}]*\}\}>'
            r'[\s\S]*?'
            r'</div>\s*</div>\s*</div>'
        )
        new_alert = (
            r'\g<1>'
            f'<div style={{{{ background: "{bg_color}", border: "1px solid {border_color}", '
            f'borderRadius: 10, padding: "14px 20px", marginBottom: 24, display: "flex", '
            f'alignItems: "center", gap: 12 }}}}>\n'
            f'        <span style={{{{ fontSize: 22, flexShrink: 0 }}}}>{icon}</span>\n'
            f'        <div>\n'
            f'          <div style={{{{ fontWeight: 700, color: "{text_color}", marginBottom: 2 }}}}>{title}</div>\n'
            f'          <div style={{{{ fontSize: 13, color: "{text_color}" }}}}>\n'
            f'            {text}\n'
            f'          </div>\n'
            f'        </div>\n'
            f'      </div>'
        )

        new_content = re.sub(pattern, new_alert, content, count=1, flags=re.DOTALL)
        if new_content != content:
            logger.info("Alert banner bijgewerkt")
        else:
            # Fallback: vervang alleen de tekst in de bestaande banner
            content = re.sub(
                r'(MARKTUPDATE:[^<]*|KRITIEKE MARKTSITUATIE)',
                title, content, count=1
            )
            logger.info("Alert banner: alleen titel bijgewerkt (fallback)")
        return new_content if new_content != content else content

    def apply_ai_kernboodschap(self, content: str, ai_data: Dict) -> str:
        """Update de kernboodschap-paragraaf en triggerteksten."""
        kernboodschap  = ai_data.get('kernboodschap', '')
        trig_variabel  = ai_data.get('trigger_variabel', '')
        trig_vast      = ai_data.get('trigger_vast', '')

        if kernboodschap:
            # Vervang de eerste <p> in het kernboodschap-blok
            pattern = (
                r'(KERNBOODSCHAP:[^\n]*\n\s*</h2>\s*\n\s*)'
                r'<p style=\{\{ fontSize: 15,[^>]*\}\}>\s*\n\s*'
                r'([\s\S]*?)'
                r'\s*</p>'
            )
            replacement = (
                r'\g<1>'
                f'<p style={{{{ fontSize: 15, lineHeight: 1.85, color: "#bfdbfe", '
                f'margin: "0 0 14px", fontWeight: 500 }}}}>\n'
                f'            {kernboodschap}\n'
                f'          </p>'
            )
            new_content = re.sub(pattern, replacement, content, count=1, flags=re.DOTALL)
            if new_content != content:
                logger.info("Kernboodschap bijgewerkt")
                content = new_content

        if trig_variabel:
            content = re.sub(
                r'(Trigger voor Variabel[^:]*:</strong>\s*)([^<]+)',
                rf'\g<1>{trig_variabel} ',
                content, count=1
            )

        if trig_vast:
            content = re.sub(
                r'(Trigger voor Vast[^:]*:</strong>\s*)([^<]+)',
                rf'\g<1>{trig_vast} ',
                content, count=1
            )

        return content

    def apply_ai_header_datum(self, content: str, ai_data: Dict) -> str:
        """Update de geopolitieke sectie-header met huidige maand/jaar."""
        month_nl = {
            1:"januari",2:"februari",3:"maart",4:"april",5:"mei",6:"juni",
            7:"juli",8:"augustus",9:"september",10:"oktober",11:"november",12:"december"
        }
        now = datetime.now()
        label = f"{month_nl[now.month].capitalize()} {now.year}"
        content = re.sub(
            r'(⚔️ Geopolitieke Situatie — )[^\n<"]+',
            rf'\g<1>{label}',
            content, count=1
        )
        return content

    # ── Hoofd JSX-update ──────────────────────────────────────────────────────

    def update_jsx_file(self, market_data: Dict, ai_data: Optional[Dict] = None):
        """Update JSX bestand — dagelijks + optionele wekelijkse AI-updates."""
        logger.info(f"Updating {self.jsx_path} (mode: {self.update_mode})...")

        with open(self.jsx_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # ── Altijd (dagelijks + wekelijks) ──────────────────────────────────
        content = self.trim_rawdata_to_30_days(content)
        content = self.update_jsx_rawdata(content, market_data)
        content = self.update_jsx_kpis(content, market_data)
        content = self.update_jsx_kpi_variables(content, market_data)
        content = self.update_jsx_dates(content, market_data)
        content = self.update_critical_header(content, market_data)
        content = self.update_analysis_values(content, market_data)
        content = self.update_geopolitical_references(content, market_data)
        content = self.update_storage_calculation(content)
        content = self.enforce_gasopslag_consistency(content, market_data)
        content = self.update_sources_section(content, market_data)

        # ── Alleen wekelijks: AI-gegenereerde inhoud ─────────────────────────
        if self.update_mode == 'weekly' and ai_data:
            logger.info("Weekly mode: AI-inhoud toepassen...")
            content = self.apply_ai_header_datum(content, ai_data)
            content = self.apply_ai_geopolitical(content, ai_data)
            content = self.apply_ai_alert(content, ai_data)
            content = self.apply_ai_kernboodschap(content, ai_data)
            logger.info("AI-inhoud toegepast")

        with open(self.jsx_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"JSX succesvol bijgewerkt: {self.jsx_path}")

    def load_ai_structured(self) -> Optional[Dict]:
        """Laad gestructureerde AI-analyse indien beschikbaar."""
        filepath = 'data/ai_analysis.json'
        if not os.path.exists(filepath):
            return None
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('structured')
        except Exception as e:
            logger.warning(f"Kon AI-analyse niet laden: {e}")
            return None

    def update_storage_calculation(self, content: str, market_data: Dict = None) -> str:
        """Update storage calculation — market_data optioneel voor backwards compat."""
        if market_data is None:
            return content
        remaining_pct = 90 - market_data["eu_storage"]
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '["Nog te vullen (apr–okt)"' in line and '~' in line and 'pct-punten' in line:
                lines[i] = f'              ["Nog te vullen (apr–okt)",    "~{remaining_pct:.0f} pct-punten", "#f97316"],'
                logger.info(f"Storage calculation updated: {remaining_pct:.0f}%")
                break
        return '\n'.join(lines)

    def run_update(self):
        """Voer volledige update uit."""
        logger.info(f"Report update gestart (mode: {self.update_mode})...")

        market_data = self.load_market_data()

        # Laad gestructureerde AI-analyse (beschikbaar na wekelijkse ai_analyzer run)
        ai_data = self.load_ai_structured() if self.update_mode == 'weekly' else None
        if self.update_mode == 'weekly':
            if ai_data:
                logger.info("Gestructureerde AI-analyse geladen")
            else:
                logger.warning("Geen AI-analyse gevonden — JSX-teksten ongewijzigd")

        self.update_jsx_file(market_data, ai_data)
        logger.info("Report update voltooid")

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
