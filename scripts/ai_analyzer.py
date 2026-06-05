"""
AI Analyzer voor EnergieRapport
Gebruikt Claude API voor geopolitieke analyse en marktinterpretatie
"""

import os
import json
import sys
from datetime import datetime
from typing import Dict, List
import logging

try:
    import anthropic
except ImportError:
    anthropic = None
    logging.warning("Anthropic library not installed - AI analysis will be skipped")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIAnalyzer:
    # Model preferences: use active Claude models (not deprecated/retired)
    MODELS = [
        "claude-haiku-4-5-20251001",  # Claude Haiku 4.5 (cost-effective, active until Oct 2026)
    ]
    
    def __init__(self):
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        self.client = None
        self.analysis_trigger = os.getenv('ANALYSIS_TRIGGER', 'weekly')
        # Allow model override via environment variable
        self.model = os.getenv('CLAUDE_MODEL', self.MODELS[0])
        
        if anthropic and self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
            logger.info(f"Using Claude model: {self.model}")
        else:
            logger.warning("Claude API not configured - analysis will be limited")
    
    def load_market_data(self) -> Dict:
        """Laad huidige marktdata"""
        filepath = 'data/latest_prices.json'
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"No market data found at {filepath}")
        
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def load_crisis_report(self) -> Dict:
        """Laad crisis rapport indien aanwezig"""
        filepath = 'data/crisis_report.json'
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return {}
    
    def load_historical_data(self) -> List[Dict]:
        """Laad historische data voor trend analyse"""
        filepath = 'data/historical_prices.json'
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return []
    
    def build_analysis_prompt(self, market_data: Dict, crisis_data: Dict, historical: List[Dict]) -> str:
        """Bouw prompt voor Claude analyse"""
        
        prompt = f"""Je bent een energie markt analist die een dagelijks rapport maakt voor Belgische consumenten.

**Huidige Marktdata ({market_data.get('timestamp', 'N/A')}):**
- TTF Aardgas: €{market_data.get('ttf', 0):.2f}/MWh
- Belpex Elektriciteit: €{market_data.get('belpex', 0):.2f}/MWh
- EU Gas Opslag: {market_data.get('eu_storage', 0):.1f}%
- Brent Crude: ${market_data.get('brent', 0):.2f}/vat

"""
        
        if crisis_data and crisis_data.get('crisis_detected'):
            prompt += "**CRISIS ALERT:**\n"
            for detail in crisis_data.get('details', []):
                prompt += f"- {detail['commodity']}: {detail['change_pct']:+.1f}% {detail['direction']}\n"
            prompt += "\n"
        
        if historical:
            prompt += f"**Historische Context:** {len(historical)} dagen data beschikbaar\n\n"
        
        prompt += """**Analyseer de volgende aspecten:**

1. **Marktdynamiek**: Wat zijn de belangrijkste drivers achter de huidige prijzen?
2. **Geopolitieke Factoren**: Welke geopolitieke gebeurtenissen beïnvloeden de markt?
3. **Vooruitzichten**: Wat zijn de verwachtingen voor de komende weken?
4. **Consumentenadvies**: Wat betekent dit voor Belgische consumenten die een energiecontract moeten kiezen?

Geef een beknopte maar informatieve analyse in het Nederlands, geschikt voor consumenten.
Maximaal 300 woorden."""

        return prompt
    
    def analyze_with_claude(self, prompt: str) -> str:
        """Voer analyse uit met Claude API"""
        if not self.client:
            logger.warning("Claude client not available - returning placeholder analysis")
            return self._generate_placeholder_analysis()
        
        try:
            logger.info("Requesting Claude analysis...")
            
            message = self.client.messages.create(
                model=self.model,  # Gebruik configured model
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            analysis = message.content[0].text
            logger.info(f"Claude analysis received ({len(analysis)} chars)")
            return analysis
        
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return self._generate_placeholder_analysis()
    
    def _generate_placeholder_analysis(self) -> str:
        """Genereer placeholder analyse wanneer AI niet beschikbaar is"""
        return """**Marktanalyse Placeholder**

De energiemarkt vertoont momenteel volatiliteit door verschillende factoren:
- Seizoensinvloeden op vraag en aanbod
- Geopolitieke ontwikkelingen in producerende regio's
- EU beleid rond energie transitie

Voor consumenten blijft het advies om marktbewegingen te volgen en contractkeuzes 
af te stemmen op persoonlijke risicotolerantie en verbruikspatronen.

*Opmerking: Dit is een automatisch gegenereerde placeholder. Voor volledige AI-analyse 
is Claude API configuratie vereist.*"""
    
    def save_analysis(self, analysis: str):
        """Sla analyse op naar bestand"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'trigger': self.analysis_trigger,
            'analysis': analysis
        }
        
        os.makedirs('data', exist_ok=True)
        with open('data/ai_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info("AI analysis saved")
    
    def run_analysis(self) -> str:
        """Voer volledige analyse uit"""
        logger.info(f"Starting AI analysis (trigger: {self.analysis_trigger})...")
        
        market_data = self.load_market_data()
        crisis_data = self.load_crisis_report()
        historical = self.load_historical_data()
        
        prompt = self.build_analysis_prompt(market_data, crisis_data, historical)
        analysis = self.analyze_with_claude(prompt)
        
        self.save_analysis(analysis)
        
        return analysis

def main():
    analyzer = AIAnalyzer()
    
    try:
        analysis = analyzer.run_analysis()
        
        print("\n=== AI Analyse Resultaat ===")
        print(analysis)
        print("\n" + "="*50)
        
        sys.exit(0)
    
    except FileNotFoundError as e:
        logger.error(f"Required data file not found: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"AI analysis failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
