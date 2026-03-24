"""
Data Collector voor EnergieRapport - HYBRID APPROACH
- Belpex: REST API (energy-charts.info) - betrouwbaar & gratis
- TTF, Storage, Brent: Claude API - intelligent web search & parsing
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("anthropic library not installed - Claude API calls will be skipped")


class EnergyDataCollector:
    """
    HYBRID AUTONOME DAGELIJKSE DATA COLLECTOR

    Strategie:
    - Belpex: ✅ REST API (gratis, stabiel)
    - TTF, Storage, Brent: Claude API (intelligent parsing)
    - Fallback: vorige dag's data als noodoplossing
    """

    def __init__(self):
        self.data = {
            'ttf': None,
            'belpex': None,
            'eu_storage': None,
            'brent': None,
            'timestamp': datetime.now().isoformat(),
            'sources': {},
            'validation': {},
            'data_source': 'live_collection',
            'collection_status': {}
        }

        # HTTP session for REST APIs
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # Claude API client
        self.claude_client = None
        self.claude_model = os.getenv('CLAUDE_MODEL', 'claude-haiku-4-5-20251001')

        if ANTHROPIC_AVAILABLE:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key:
                self.claude_client = anthropic.Anthropic(api_key=api_key)
                logger.info(f"Claude API available (model: {self.claude_model})")
            else:
                logger.warning("ANTHROPIC_API_KEY not set - Claude API disabled")
        else:
            logger.warning("Anthropic SDK not installed - Claude API disabled")

        self.previous_data = self._load_previous_data()

    def _load_previous_data(self) -> Dict:
        """Load previous day's data for fallback"""
        try:
            if os.path.exists('data/latest_prices.json'):
                with open('data/latest_prices.json', 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load previous data: {e}")
        return {}

    # ============ BELPEX: REST API (betrouwbaar & gratis) ============

    def collect_belpex_price(self) -> Optional[float]:
        """
        Collect Belgium electricity price from energy-charts.info REST API
        Official source: Bundesnetzagentur (German regulator)
        Returns: Daily average of quarter-hourly prices
        """
        logger.info("Collecting Belpex (Belgium electricity)...")

        try:
            url = 'https://api.energy-charts.info/price?bzn=BE'
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()

            data = resp.json()

            if not data.get('price'):
                logger.warning("   No price data in API response")
                return self._fallback_value('belpex')

            prices = data['price']
            daily_avg = sum(prices) / len(prices)
            min_price = min(prices)
            max_price = max(prices)

            logger.info(f"   Belpex: €{daily_avg:.2f}/MWh (min: €{min_price:.2f}, max: €{max_price:.2f}, {len(prices)} points)")

            self.data['belpex'] = round(daily_avg, 2)
            self.data['sources']['belpex'] = ['energy-charts.info (Bundesnetzagentur)']
            self.data['validation']['belpex'] = ''
            self.data['collection_status']['belpex'] = f"Live API ({len(prices)} quarter-hourly points)"

            return self.data['belpex']

        except requests.exceptions.Timeout:
            logger.warning("   API timeout")
            return self._fallback_value('belpex')
        except requests.exceptions.RequestException as e:
            logger.warning(f"   API request failed: {e}")
            return self._fallback_value('belpex')
        except Exception as e:
            logger.warning(f"   Error: {e}")
            return self._fallback_value('belpex')

    # ============ TTF, STORAGE, BRENT: Claude API (intelligent parsing) ============

    def collect_via_claude(self) -> bool:
        """
        Use Claude API to intelligently search and parse energy market data
        Returns: True if successful, False if skipped/failed
        """
        if not self.claude_client:
            logger.warning("Claude API not available - using fallback for TTF, Storage, Brent")
            self._fallback_value('ttf')
            self._fallback_value('eu_storage')
            self._fallback_value('brent')
            return False

        logger.info("Collecting TTF, EU Storage, Brent via Claude API...")

        try:
            prompt = """
            Find TODAY's energy market prices. Search the web for current values.

            Return ONLY valid JSON (no markdown, no explanation):
            {
                "ttf_eur_mwh": <float: Dutch TTF gas €/MWh, typical range 20-150>,
                "ttf_source": "<source used>",
                "eu_storage_percent": <float: EU gas storage %, typical range 10-90>,
                "storage_source": "<source used>",
                "brent_usd_barrel": <float: Brent crude oil $/barrel, typical range 50-150>,
                "brent_source": "<source used>"
            }

            IMPORTANT:
            - All prices must be realistic (TTF 20-150, Storage 10-90%, Brent 50-150)
            - If you can't find a value, use null
            - Use most recent available prices
            - Quote sources (e.g., "Trading Economics", "GIE AGSI+", "Investing.com")
            """

            message = self.claude_client.messages.create(
                model=self.claude_model,
                max_tokens=512,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = message.content[0].text

            # Parse JSON response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                logger.warning("   Claude response doesn't contain valid JSON")
                self._fallback_value('ttf')
                self._fallback_value('eu_storage')
                self._fallback_value('brent')
                return False

            result = json.loads(json_match.group())

            # Validate and store TTF
            if result.get('ttf_eur_mwh') and 15 < float(result['ttf_eur_mwh']) < 300:
                ttf = round(float(result['ttf_eur_mwh']), 2)
                self.data['ttf'] = ttf
                self.data['sources']['ttf'] = [result.get('ttf_source', 'Claude search')]
                self.data['validation']['ttf'] = ''
                self.data['collection_status']['ttf'] = 'Live (Claude API)'
                logger.info(f"   TTF: €{ttf:.2f}/MWh ({result.get('ttf_source', 'unknown')})")
            else:
                logger.warning(f"   TTF value invalid: {result.get('ttf_eur_mwh')}")
                self._fallback_value('ttf')

            # Validate and store EU Storage
            if result.get('eu_storage_percent') and 0 < float(result['eu_storage_percent']) <= 100:
                storage = round(float(result['eu_storage_percent']), 1)
                self.data['eu_storage'] = storage
                self.data['sources']['eu_storage'] = [result.get('storage_source', 'Claude search')]
                self.data['validation']['eu_storage'] = ''
                self.data['collection_status']['eu_storage'] = 'Live (Claude API)'
                logger.info(f"   Storage: {storage:.1f}% ({result.get('storage_source', 'unknown')})")
            else:
                logger.warning(f"   Storage value invalid: {result.get('eu_storage_percent')}")
                self._fallback_value('eu_storage')

            # Validate and store Brent
            if result.get('brent_usd_barrel') and 30 < float(result['brent_usd_barrel']) < 250:
                brent = round(float(result['brent_usd_barrel']), 2)
                self.data['brent'] = brent
                self.data['sources']['brent'] = [result.get('brent_source', 'Claude search')]
                self.data['validation']['brent'] = ''
                self.data['collection_status']['brent'] = 'Live (Claude API)'
                logger.info(f"   Brent: ${brent:.2f}/barrel ({result.get('brent_source', 'unknown')})")
            else:
                logger.warning(f"   Brent value invalid: {result.get('brent_usd_barrel')}")
                self._fallback_value('brent')

            return True

        except json.JSONDecodeError:
            logger.warning("   Failed to parse Claude's JSON response")
            self._fallback_value('ttf')
            self._fallback_value('eu_storage')
            self._fallback_value('brent')
            return False
        except Exception as e:
            logger.warning(f"   Claude API error: {e}")
            self._fallback_value('ttf')
            self._fallback_value('eu_storage')
            self._fallback_value('brent')
            return False

    def _fallback_value(self, key: str) -> Optional[float]:
        """Use previous day's value as fallback"""
        if self.previous_data.get(key):
            prev_value = self.previous_data[key]
            logger.warning(f"     Using fallback (previous): {prev_value}")
            self.data[key] = prev_value
            self.data['sources'][key] = ['fallback from previous collection']
            self.data['validation'][key] = ''
            self.data['collection_status'][key] = 'fallback (source unavailable)'
            self.data['data_source'] = 'fallback'
            return prev_value

        logger.error(f"     No fallback available for {key}")
        return None

    def collect_all(self) -> Dict:
        """Collect all data points"""
        logger.info("=" * 75)
        logger.info(" AUTONOMOUS ENERGY MARKET DATA COLLECTION")
        logger.info("=" * 75)

        # Collect Belpex via REST API
        self.collect_belpex_price()

        # Collect TTF, Storage, Brent via Claude API
        self.collect_via_claude()

        # Verify all required data
        missing = [k for k, v in self.data.items()
                  if v is None and k not in ['timestamp', 'sources', 'validation', 'data_source', 'collection_status']]

        if missing:
            logger.error(f" FATAL: Missing critical data: {', '.join(missing)}")
            raise ValueError(f"Cannot proceed without: {missing}")

        logger.info("=" * 75)
        if self.data['data_source'] == 'fallback':
            logger.warning("  WARNING: Using fallback data (some sources were unavailable)")
        else:
            logger.info("✅ SUCCESS: All data collected from live sources")
        logger.info("=" * 75)

        return self.data

    def save_to_file(self, filepath: str = 'data/latest_prices.json'):
        """Save collected data to JSON file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(self.data, f, indent=2)
        logger.info(f" Saved to {filepath}")


def main():
    try:
        collector = EnergyDataCollector()
        data = collector.collect_all()
        collector.save_to_file()

        # Print summary
        print("\n" + "=" * 75)
        print("COLLECTED MARKET DATA")
        print("=" * 75)

        ttf_status = data['validation'].get('ttf', '?')
        belpex_status = data['validation'].get('belpex', '?')
        storage_status = data['validation'].get('eu_storage', '?')
        brent_status = data['validation'].get('brent', '?')

        print(f"TTF Gas:                €{data['ttf']:.2f}/MWh [{ttf_status}]")
        print(f"Belpex Elektriciteit:   €{data['belpex']:.2f}/MWh [{belpex_status}]")
        print(f"EU Gas Storage:         {data['eu_storage']:.1f}% [{storage_status}]")
        print(f"Brent Crude Oil:        ${data['brent']:.2f}/barrel [{brent_status}]")
        print()
        print(f"Timestamp:              {data['timestamp']}")
        print(f"Data Source:            {data['data_source']}")
        print()

        for key in ['ttf', 'belpex', 'eu_storage', 'brent']:
            status = data['collection_status'].get(key, '?')
            sources = ', '.join(data['sources'].get(key, ['none']))
            print(f"{key.upper():16} {status:40} ({sources})")

        print("=" * 75)
        return 0

    except Exception as e:
        logger.error(f" COLLECTION FAILED: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
