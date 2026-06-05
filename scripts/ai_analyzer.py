"""
AI Analyzer voor EnergieRapport — Weekly mode
- Tavily: scant actueel geopolitiek energienieuws
- Claude: genereert gestructureerde JSON voor JSX-update
  (geopolitieke items, alert banner, kernboodschap, triggerteksten)
"""

import os
import json
import sys
import re
from datetime import datetime
from typing import Dict, List, Optional
import logging

try:
    import anthropic
except ImportError:
    anthropic = None
    logging.warning("Anthropic library not installed")

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    logging.warning("Tavily library not installed")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIAnalyzer:
    MODEL = "claude-haiku-4-5-20251001"

    # Tavily queries voor wekelijkse geopolitieke scan
    WEEKLY_QUERIES = [
        "TTF natural gas spot price Europe today EUR MWh",
        "EU gas storage levels Europe today 2026",
        "Strait of Hormuz shipping energy 2026",
        "Qatar LNG export supply 2026",
        "OPEC oil production June 2026",
        "Belgium nuclear energy Engie 2026",
        "Belgium energy prices consumer 2026",
        "EU ETS carbon price 2026",
        "Russia Ukraine gas contracts Europe 2026",
        "energieprijzen Belgie vast variabel 2026",
    ]

    def __init__(self):
        self.analysis_trigger = os.getenv('ANALYSIS_TRIGGER', 'weekly')
        self.model = os.getenv('CLAUDE_MODEL', self.MODEL)

        # Claude client
        self.claude = None
        if anthropic and os.getenv('ANTHROPIC_API_KEY'):
            self.claude = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
            logger.info(f"Claude ready ({self.model})")

        # Tavily client
        self.tavily = None
        if TAVILY_AVAILABLE and os.getenv('TAVILY_API_KEY'):
            self.tavily = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))
            logger.info("Tavily ready")

    # ── Data loaders ──────────────────────────────────────────────────────────

    def load_market_data(self) -> Dict:
        with open('data/latest_prices.json', 'r', encoding='utf-8') as f:
            return json.load(f)

    # ── Tavily: geopolitieke nieuwsscan ───────────────────────────────────────

    def run_tavily_searches(self) -> str:
        """Scan actueel energienieuws via Tavily. Retourneert gebundelde tekst."""
        if not self.tavily:
            logger.warning("Tavily niet beschikbaar — geen nieuwsscan")
            return ""

        snippets = []
        for query in self.WEEKLY_QUERIES:
            try:
                result = self.tavily.search(query, search_depth="basic", max_results=3)
                for x in result.get('results', []):
                    snippets.append(f"[{x['url']}]\n{x['content'][:350]}")
            except Exception as e:
                logger.warning(f"Tavily fout voor '{query}': {e}")

        context = "\n\n".join(snippets[:25])
        logger.info(f"Tavily scan: {len(snippets)} snippets verzameld")
        return context

    # ── Claude: gestructureerde JSON genereren ────────────────────────────────

    def generate_structured_analysis(self, market_data: Dict, news_context: str) -> Dict:
        """
        Laat Claude een gestructureerde JSON genereren voor de JSX-update.
        Retourneert een dict met: geopolitical_items, alert, kernboodschap, triggers.
        """
        if not self.claude:
            logger.warning("Claude niet beschikbaar — placeholder teruggeven")
            return self._placeholder_analysis(market_data)

        today = datetime.now().strftime("%-d %B %Y") if sys.platform != 'win32' \
            else datetime.now().strftime("%d %B %Y").lstrip("0")

        prompt = f"""Je bent een energie-marktanalist voor een Vlaams consumentenrapport (energie-rapport-2026.pages.dev).
Schrijf in het Nederlands. Vandaag is {today}.

ACTUELE MARKTDATA:
- TTF Gas:            €{market_data.get('ttf', 0):.2f}/MWh
- Belpex Elektr.:     €{market_data.get('belpex', 0):.2f}/MWh
- Belgische opslag:   {market_data.get('eu_storage', 0):.1f}%
- Brent Crude:        ${market_data.get('brent', 0):.2f}/vat

RECENT NIEUWS (via Tavily):
{news_context or '(geen nieuwscontext beschikbaar)'}

Genereer UITSLUITEND geldig JSON (geen markdown, geen uitleg), met deze structuur:

{{
  "geopolitical_items": [
    {{
      "titel": "Max 40 tekens",
      "color": "#hexkleur",
      "tekst": "2-3 zinnen: feit — effect op energieprijzen — verwachting"
    }}
  ],
  "alert": {{
    "title": "MARKTUPDATE: bondige titel",
    "text": "TTF €X · Belpex €Y · [1 zin context voor consument]",
    "is_critical": false
  }},
  "kernboodschap": "2-3 zinnen over huidige marktpositie en wat dit betekent voor een contractkeuze",
  "trigger_variabel": "Concrete prijsdrempel/conditie waarop variabel interessanter wordt",
  "trigger_vast": "Concrete prijsdrempel/conditie waarop vast overwogen moet worden"
}}

Richtlijnen geopolitieke items (6-9 items, sorteren van meest naar minst impactvol):
- #ef4444 rood: sterk prijsopdrijvend / negatief voor consument
- #f97316 oranje: risico / aandacht vereist
- #eab308 geel: onzeker / neutraal
- #22c55e groen: prijsdrukkend / positief voor consument
- #0ea5e9 blauw: informatief / beleid
- #8b5cf6 paars: Belgisch consumentenbeleid / tarieven
- #64748b grijs: macro / indirect

Verplichte items indien relevant voor huidige situatie:
- Belgische nucleaire renaissance (Engie-akkoord, oktober 2026)
- Qatar LNG structurele schade (3-5 jaar)
- EU ETS koolstofprijs (€85/ton)
- Belgische gasopslag (huidig niveau vs EU-gemiddelde)
- Hormuz scheepvaartstatus"""

        try:
            response = self.claude.messages.create(
                model=self.model,
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = response.content[0].text.strip()

            # Verwijder eventuele markdown-codeblokken
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0].strip()
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0].strip()

            result = json.loads(raw)
            logger.info(f"Claude analyse ontvangen: "
                        f"{len(result.get('geopolitical_items', []))} geo-items")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Claude JSON parse error: {e}")
            return self._placeholder_analysis(market_data)
        except Exception as e:
            logger.error(f"Claude API fout: {e}")
            return self._placeholder_analysis(market_data)

    def _placeholder_analysis(self, market_data: Dict) -> Dict:
        """Minimale placeholder als Claude of Tavily niet beschikbaar zijn."""
        ttf = market_data.get('ttf', 48.85)
        belpex = market_data.get('belpex', 52.59)
        storage = market_data.get('eu_storage', 21.9)
        brent = market_data.get('brent', 95.36)
        return {
            "geopolitical_items": [
                {
                    "titel": "Qatar LNG: 3-5 Jaar Herstel",
                    "color": "#ef4444",
                    "tekst": (
                        "Qatar's LNG-exportcapaciteit (17% van wereldmarkt) is structureel beschadigd "
                        "voor 3-5 jaar. Pre-crisis TTF-niveaus van €30-32 zijn onbereikbaar tot 2028-2030. "
                        "Dit houdt de gasmarkt structureel krapper dan voor 2026."
                    )
                },
                {
                    "titel": "Belgische Nucleaire Renaissance",
                    "color": "#22c55e",
                    "tekst": (
                        "Engie-akkoord voor heractivering nucleaire vloot verwacht oktober 2026. "
                        "Meer kernvermogen = minder uren dat gas de marginale prijszetter is "
                        "→ structureel lagere Belpex op middellange termijn."
                    )
                },
                {
                    "titel": f"Belgische Gasopslag: {storage:.1f}%",
                    "color": "#ef4444",
                    "tekst": (
                        f"Met {storage:.1f}% vulgraad staat België voor een record-injectie-uitdaging. "
                        "EU-gemiddelde is ~57%. Achterstand verhoogt de concurrentie voor LNG-cargos "
                        "en houdt TTF-forward-curve ondersteund."
                    )
                },
            ],
            "alert": {
                "title": "MARKTUPDATE: POST-CRISIS NORMALISATIE",
                "text": (
                    f"TTF €{ttf:.2f} · Belpex €{belpex:.2f}/MWh · "
                    f"Brent ${brent:.2f} · BE opslag {storage:.1f}% · "
                    "Vast tarief ~27% duurder dan variabel"
                ),
                "is_critical": False
            },
            "kernboodschap": (
                f"TTF staat op €{ttf:.2f}/MWh, een normalisatie na de piek van €62 in maart. "
                "Qatar LNG-schade (3-5 jaar) zorgt voor een structurele vloer boven pre-crisis niveaus. "
                "Vast tarief is momenteel ~27% duurder dan variabel — variabel heeft duidelijk voordeel "
                "tenzij u budgetzekerheid boven financieel optimum stelt."
            ),
            "trigger_variabel": (
                "Als TTF 2+ weken stabiel onder €45/MWh blijft "
                "EN Belgische opslag boven 35% eind juni uitkomt"
            ),
            "trigger_vast": (
                "Bij nieuw geopolitiek incident (Hormuz hersluit, escalatie) "
                "OF als Belgische opslag 60% niet haalt tegen september"
            )
        }

    # ── Opslaan ───────────────────────────────────────────────────────────────

    def save_analysis(self, structured: Dict):
        os.makedirs('data', exist_ok=True)
        report = {
            'timestamp': datetime.now().isoformat(),
            'trigger': self.analysis_trigger,
            'structured': structured,
            # Bewaar ook platte tekst voor backwards-compatibiliteit
            'analysis': structured.get('kernboodschap', '')
        }
        with open('data/ai_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        logger.info("AI-analyse opgeslagen in data/ai_analysis.json")

    # ── Hoofdflow ─────────────────────────────────────────────────────────────

    def run_analysis(self) -> Dict:
        logger.info(f"AI analyse gestart (trigger: {self.analysis_trigger})")

        market_data = self.load_market_data()

        # Stap 1: Tavily nieuwsscan (altijd proberen)
        news_context = self.run_tavily_searches()

        # Stap 2: Claude genereert gestructureerde JSON
        structured = self.generate_structured_analysis(market_data, news_context)

        # Stap 3: Opslaan
        self.save_analysis(structured)

        return structured


def main():
    analyzer = AIAnalyzer()
    try:
        result = analyzer.run_analysis()
        print("\n=== AI Analyse Resultaat ===")
        print(f"Alert: {result.get('alert', {}).get('title', '?')}")
        print(f"Geo-items: {len(result.get('geopolitical_items', []))}")
        print(f"Kernboodschap: {result.get('kernboodschap', '')[:120]}...")
        sys.exit(0)
    except FileNotFoundError as e:
        logger.error(f"Databestand niet gevonden: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"AI analyse mislukt: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
