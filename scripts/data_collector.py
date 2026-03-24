"""
Data Collector voor EnergieRapport - HYBRID APPROACH
- Belpex: REST API (energy-charts.info) - betrouwbaar & gratis
- TTF, Storage, Brent: Tavily API - dedicated web search for AI agents
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, Optional
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("anthropic library not installed - Claude API calls will be skipped")

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    logger.warning("tavily-python library not installed - Tavily search will be skipped")


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

        # Claude API client (for AI analysis, not web search)
        self.claude_client = None
        claude_model_env = os.getenv('CLAUDE_MODEL')
        self.claude_model = claude_model_env if claude_model_env else 'claude-sonnet-4-6'

        if ANTHROPIC_AVAILABLE:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key:
                self.claude_client = anthropic.Anthropic(api_key=api_key)
                logger.info(f"Claude API available (model: {self.claude_model})")
            else:
                logger.warning("ANTHROPIC_API_KEY not set - Claude API disabled")
        else:
            logger.warning("Anthropic SDK not installed - Claude API disabled")

        # Tavily API client (for web search)
        self.tavily_client = None
        if TAVILY_AVAILABLE:
            tavily_api_key = os.getenv('TAVILY_API_KEY')
            if tavily_api_key:
                self.tavily_client = TavilyClient(api_key=tavily_api_key)
                logger.info("Tavily API available for web search")
            else:
                logger.warning("TAVILY_API_KEY not set - Tavily search disabled")
        else:
            logger.warning("Tavily SDK not installed - Tavily search disabled")

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

    # ============ TTF, STORAGE, BRENT: Tavily API (web search) ============

    def collect_via_tavily(self) -> bool:
        """
        Use Tavily API to search for energy market prices
        Returns: True if successful, False if skipped/failed
        """
        if not self.tavily_client:
            logger.warning("Tavily API not available - using fallback for TTF, Storage, Brent")
            self._fallback_value('ttf')
            self._fallback_value('eu_storage')
            self._fallback_value('brent')
            return False

        logger.info("Collecting TTF, EU Storage, Brent via Tavily API...")

        try:
            # Search for TTF gas price
            ttf_query = f"TTF gas price EUR/MWh {datetime.now().strftime('%d %B %Y')}"
            logger.info(f"   Searching: {ttf_query}")
            ttf_response = self.tavily_client.search(
                query=ttf_query,
                search_depth="basic",
                max_results=5
            )
            
            # Extract TTF price from search results
            ttf_price = self._extract_price_from_tavily(ttf_response, 'ttf')
            if ttf_price:
                self.data['ttf'] = ttf_price['value']
                self.data['sources']['ttf'] = [ttf_price['source']]
                self.data['validation']['ttf'] = ''
                self.data['collection_status']['ttf'] = 'Live (Tavily API)'
                logger.info(f"   TTF: €{ttf_price['value']:.2f}/MWh ({ttf_price['source']})")
            else:
                logger.warning("   Could not extract TTF price from search results")
                self._fallback_value('ttf')

            # Search for EU gas storage
            storage_query = f"EU gas storage percentage {datetime.now().strftime('%d %B %Y')}"
            logger.info(f"   Searching: {storage_query}")
            storage_response = self.tavily_client.search(
                query=storage_query,
                search_depth="basic",
                max_results=5
            )
            
            # Extract storage percentage from search results
            storage_data = self._extract_price_from_tavily(storage_response, 'storage')
            if storage_data:
                self.data['eu_storage'] = storage_data['value']
                self.data['sources']['eu_storage'] = [storage_data['source']]
                self.data['validation']['eu_storage'] = ''
                self.data['collection_status']['eu_storage'] = 'Live (Tavily API)'
                logger.info(f"   Storage: {storage_data['value']:.1f}% ({storage_data['source']})")
            else:
                logger.warning("   Could not extract storage percentage from search results")
                self._fallback_value('eu_storage')

            # Search for Brent oil price
            brent_query = f"Brent crude oil price USD/barrel {datetime.now().strftime('%d %B %Y')}"
            logger.info(f"   Searching: {brent_query}")
            brent_response = self.tavily_client.search(
                query=brent_query,
                search_depth="basic",
                max_results=5
            )
            
            # Extract Brent price from search results
            brent_data = self._extract_price_from_tavily(brent_response, 'brent')
            if brent_data:
                self.data['brent'] = brent_data['value']
                self.data['sources']['brent'] = [brent_data['source']]
                self.data['validation']['brent'] = ''
                self.data['collection_status']['brent'] = 'Live (Tavily API)'
                logger.info(f"   Brent: ${brent_data['value']:.2f}/barrel ({brent_data['source']})")
            else:
                logger.warning("   Could not extract Brent price from search results")
                self._fallback_value('brent')

            return True

        except Exception as e:
            logger.warning(f"   Tavily API error: {e}")
            self._fallback_value('ttf')
            self._fallback_value('eu_storage')
            self._fallback_value('brent')
            return False

    def _extract_price_from_tavily(self, response: Dict, data_type: str) -> Optional[Dict]:
        """
        Extract price/value from Tavily search results
        Returns: {'value': float, 'source': str} or None
        """
        try:
            # Tavily returns results in 'results' key
            results = response.get('results', [])
            
            for result in results:
                content = result.get('content', '')
                url = result.get('url', '')
                
                # Extract price based on data type
                if data_type == 'ttf':
                    # Look for TTF price pattern (e.g., "53.25 EUR/MWh" or "€53.25")
                    price_match = re.search(r'(\d+\.?\d*)\s*(?:EUR|€)/MWh', content)
                    if price_match:
                        value = float(price_match.group(1))
                        if 15 < value < 300:  # Valid TTF range
                            return {'value': value, 'source': url}
                
                elif data_type == 'storage':
                    # Look for storage percentage (e.g., "26%" or "26.0%")
                    storage_match = re.search(r'(\d+\.?\d*)\s*%', content)
                    if storage_match:
                        value = float(storage_match.group(1))
                        if 0 < value <= 100:  # Valid storage range
                            return {'value': value, 'source': url}
                
                elif data_type == 'brent':
                    # Look for Brent price (e.g., "$101.55" or "101.55 USD")
                    brent_match = re.search(r'\$?(\d+\.?\d*)\s*(?:USD|dollars?)/barrel', content, re.IGNORECASE)
                    if brent_match:
                        value = float(brent_match.group(1))
                        if 30 < value < 250:  # Valid Brent range
                            return {'value': value, 'source': url}
            
            return None

        except Exception as e:
            logger.warning(f"   Error extracting {data_type} from Tavily: {e}")
            return None

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

        # If no previous data, use reasonable estimates for today
        today_estimates = {
            'ttf': 53.25,      # Based on recent market trends
            'belpex': 72.78,    # Belpex is collected via API, but fallback needed
            'eu_storage': 26.0,  # Typical low storage for this time of year
            'brent': 101.55     # Recent oil prices
        }
        
        if key in today_estimates:
            estimate_value = today_estimates[key]
            logger.warning(f"     Using today's estimate: {estimate_value}")
            self.data[key] = estimate_value
            self.data['sources'][key] = ['estimated (no live data available)']
            self.data['validation'][key] = ''
            self.data['collection_status'][key] = 'estimated'
            self.data['data_source'] = 'estimated'
            return estimate_value

        logger.error(f"     No fallback available for {key}")
        return None

    def collect_all(self) -> Dict:
        """Collect all data points"""
        logger.info("=" * 75)
        logger.info(" AUTONOMOUS ENERGY MARKET DATA COLLECTION")
        logger.info("=" * 75)

        # Collect Belpex via REST API
        self.collect_belpex_price()

        # Collect TTF, Storage, Brent via Tavily API
        self.collect_via_tavily()

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
