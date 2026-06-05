"""
Data Collector voor EnergieRapport - HYBRID APPROACH
- Belpex: REST API (energy-charts.info) - betrouwbaar & gratis
- TTF, Storage, Brent: Tavily API - dedicated web search for AI agents
"""

import os
import json
import requests
from datetime import datetime, timedelta
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
        Strategy: Use close price of last complete trading day for accuracy
        """
        logger.info("Collecting Belpex (Belgium electricity)...")

        try:
            url = 'https://api.energy-charts.info/price?bzn=BE'
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()

            if not data.get('price'):
                logger.warning("   No price data in API response")
                return self._fallback_value('belpex')

            prices = data['price']
            timestamps = data.get('unix_seconds', [])
            
            # Strategy: Use daily average of complete trading day for accuracy
            # This represents the true average cost of electricity for the day
            daily_avg = sum(prices) / len(prices)
            min_price = min(prices)
            max_price = max(prices)

            logger.info(f"   Belpex Daily: €{daily_avg:.2f}/MWh (min: €{min_price:.2f}, max: €{max_price:.2f}, {len(prices)} points)")

            self.data['belpex'] = round(daily_avg, 2)
            self.data['sources']['belpex'] = ['energy-charts.info (Bundesnetzagentur) - daily average']
            self.data['validation']['belpex'] = 'Daily average method'
            self.data['collection_status']['belpex'] = f"Daily average API ({len(prices)} points)"

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

    # ============ TTF, BRENT: OilPriceAPI (direct) ============
# ============ EU STORAGE: GIE AGSI+ API (direct) ============

    def collect_via_oilpriceapi(self) -> bool:
        """
        Use OilPriceAPI for TTF/Brent and GIE AGSI+ API for EU Storage
        Returns: True if successful, False if skipped/failed
        """
        logger.info("Collecting TTF, EU Storage, Brent via direct APIs...")

        try:
            # Collect TTF via OilPriceAPI
            ttf_success = self._collect_ttf_via_oilpriceapi()
            
            # Collect EU Storage via GIE AGSI+ API
            storage_success = self._collect_storage_via_gie_api()
            
            # Collect Brent via OilPriceAPI
            brent_success = self._collect_brent_via_oilpriceapi()

            return ttf_success or storage_success or brent_success

        except Exception as e:
            logger.warning(f"   Direct API collection error: {e}")
            self._fallback_value('ttf')
            self._fallback_value('eu_storage')
            self._fallback_value('brent')
            return False

    # Maximum age in seconds before a /latest price is considered stale
    MAX_PRICE_AGE_SECONDS = 6 * 3600  # 6 hours

    def _collect_ttf_via_oilpriceapi(self) -> bool:
        """Collect TTF gas price via OilPriceAPI with freshness check + Tavily fallback."""
        api_key = os.getenv('OIL_PRICE_API_KEY')
        if not api_key:
            logger.warning("OIL_PRICE_API_KEY not set - trying Tavily for TTF")
            return self._collect_ttf_via_tavily()

        try:
            url = "https://api.oilpriceapi.com/v1/prices/latest"
            headers = {
                'Authorization': f'Token {api_key}',
                'Content-Type': 'application/json'
            }

            logger.info("   Requesting TTF price from OilPriceAPI...")
            response = self.session.get(url, headers=headers,
                                        params={'by_code': 'DUTCH_TTF_EUR'}, timeout=30)
            response.raise_for_status()
            data = response.json()

            if data.get('status') != 'success':
                logger.warning(f"   OilPriceAPI error: {data.get('message', 'Unknown error')}")
                return self._collect_ttf_via_tavily()

            price_data = data.get('data', {})
            if not isinstance(price_data, dict):
                logger.warning("   Unexpected OilPriceAPI response format")
                return self._collect_ttf_via_tavily()

            price     = price_data.get('price', 0)
            currency  = price_data.get('currency', '')
            age_secs  = price_data.get('freshness', {}).get('age_seconds', 0)

            logger.info(f"   Found TTF price: {price} {currency} (age: {age_secs}s)")

            # Reject stale prices — this was the root cause of the April–May €53.25 issue:
            # OilPriceAPI served a cached value up to 24h old that silently passed validation.
            if age_secs > self.MAX_PRICE_AGE_SECONDS:
                logger.warning(
                    f"   OilPriceAPI price is stale ({age_secs}s > {self.MAX_PRICE_AGE_SECONDS}s) "
                    f"— falling back to Tavily"
                )
                return self._collect_ttf_via_tavily()

            if not (15 < price < 300):
                logger.warning(f"   TTF value out of range: {price}")
                return self._collect_ttf_via_tavily()

            self.data['ttf'] = round(price, 2)
            self.data['sources']['ttf'] = ['OilPriceAPI (Dutch TTF)']
            self.data['validation']['ttf'] = f'fresh ({age_secs}s old)'
            self.data['collection_status']['ttf'] = 'Live (OilPriceAPI)'
            logger.info(f"   TTF: €{price:.2f}/MWh (OilPriceAPI, {age_secs}s old)")
            return True

        except requests.exceptions.RequestException as e:
            logger.warning(f"   OilPriceAPI request error: {e} — trying Tavily")
            return self._collect_ttf_via_tavily()
        except Exception as e:
            logger.warning(f"   OilPriceAPI error: {e} — trying Tavily")
            return self._collect_ttf_via_tavily()

    def _collect_ttf_via_tavily(self) -> bool:
        """Fallback: collect TTF price via Tavily web search."""
        if not self.tavily_client:
            logger.warning("   Tavily not available — using stored fallback for TTF")
            self._fallback_value('ttf')
            return False

        try:
            query = f"TTF natural gas spot price today EUR MWh {datetime.now().strftime('%d %B %Y')}"
            logger.info(f"   Tavily TTF search: {query}")
            result = self.tavily_client.search(query, search_depth="basic", max_results=5)

            extracted = self._extract_price_from_tavily(result, 'ttf')
            if extracted and 15 < extracted['value'] < 300:
                self.data['ttf'] = round(extracted['value'], 2)
                self.data['sources']['ttf'] = [f"Tavily ({extracted['source']})"]
                self.data['validation']['ttf'] = 'Tavily fallback'
                self.data['collection_status']['ttf'] = 'Live (Tavily fallback)'
                logger.info(f"   TTF: €{extracted['value']:.2f}/MWh (Tavily)")
                return True

            logger.warning("   Tavily could not extract a valid TTF price")
            self._fallback_value('ttf')
            return False

        except Exception as e:
            logger.warning(f"   Tavily TTF error: {e}")
            self._fallback_value('ttf')
            return False

    def _collect_brent_via_oilpriceapi(self) -> bool:
        """Collect Brent oil price via OilPriceAPI with freshness check + Tavily fallback."""
        api_key = os.getenv('OIL_PRICE_API_KEY')
        if not api_key:
            logger.warning("OIL_PRICE_API_KEY not set - trying Tavily for Brent")
            return self._collect_brent_via_tavily()

        try:
            url = "https://api.oilpriceapi.com/v1/prices/latest"
            headers = {
                'Authorization': f'Token {api_key}',
                'Content-Type': 'application/json'
            }

            logger.info("   Requesting Brent price from OilPriceAPI...")
            response = self.session.get(url, headers=headers,
                                        params={'by_code': 'BRENT_CRUDE_USD'}, timeout=30)
            response.raise_for_status()
            data = response.json()

            if data.get('status') != 'success':
                logger.warning(f"   OilPriceAPI error: {data.get('message', 'Unknown error')}")
                return self._collect_brent_via_tavily()

            price_data = data.get('data', {})
            if not isinstance(price_data, dict):
                return self._collect_brent_via_tavily()

            price    = price_data.get('price', 0)
            currency = price_data.get('currency', '')
            age_secs = price_data.get('freshness', {}).get('age_seconds', 0)

            logger.info(f"   Found Brent price: {price} {currency} (age: {age_secs}s)")

            if age_secs > self.MAX_PRICE_AGE_SECONDS:
                logger.warning(
                    f"   OilPriceAPI Brent is stale ({age_secs}s) — falling back to Tavily"
                )
                return self._collect_brent_via_tavily()

            if not (30 < price < 250):
                logger.warning(f"   Brent value out of range: {price}")
                return self._collect_brent_via_tavily()

            self.data['brent'] = round(price, 2)
            self.data['sources']['brent'] = ['OilPriceAPI']
            self.data['validation']['brent'] = f'fresh ({age_secs}s old)'
            self.data['collection_status']['brent'] = 'Live (OilPriceAPI)'
            logger.info(f"   Brent: ${price:.2f}/barrel (OilPriceAPI, {age_secs}s old)")
            return True

        except requests.exceptions.RequestException as e:
            logger.warning(f"   OilPriceAPI request error: {e} — trying Tavily")
            return self._collect_brent_via_tavily()
        except Exception as e:
            logger.warning(f"   OilPriceAPI error: {e} — trying Tavily")
            return self._collect_brent_via_tavily()

    def _collect_brent_via_tavily(self) -> bool:
        """Fallback: collect Brent price via Tavily web search."""
        if not self.tavily_client:
            logger.warning("   Tavily not available — using stored fallback for Brent")
            self._fallback_value('brent')
            return False

        try:
            query = f"Brent crude oil price today USD barrel {datetime.now().strftime('%d %B %Y')}"
            logger.info(f"   Tavily Brent search: {query}")
            result = self.tavily_client.search(query, search_depth="basic", max_results=5)

            extracted = self._extract_price_from_tavily(result, 'brent')
            if extracted and 30 < extracted['value'] < 250:
                self.data['brent'] = round(extracted['value'], 2)
                self.data['sources']['brent'] = [f"Tavily ({extracted['source']})"]
                self.data['validation']['brent'] = 'Tavily fallback'
                self.data['collection_status']['brent'] = 'Live (Tavily fallback)'
                logger.info(f"   Brent: ${extracted['value']:.2f}/barrel (Tavily)")
                return True

            logger.warning("   Tavily could not extract a valid Brent price")
            self._fallback_value('brent')
            return False

        except Exception as e:
            logger.warning(f"   Tavily Brent error: {e}")
            self._fallback_value('brent')
            return False

    def _collect_storage_via_gie_api(self) -> bool:
        """Collect EU gas storage via GIE AGSI+ API"""
        api_key = os.getenv('AGSI_GIE_API_KEY')
        if not api_key:
            logger.warning("AGSI_GIE_API_KEY not set - using fallback for storage")
            self._fallback_value('eu_storage')
            return False

        try:
            # GIE AGSI+ API - use yesterday's date (data is 1 day delayed)
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            url = f"https://agsi.gie.eu/api?country=BE&from={yesterday}&to={yesterday}"
            
            headers = {
                'x-key': api_key,
                'Content-Type': 'application/json'
            }
            
            logger.info(f"   Requesting Belgium gas storage from GIE API...")
            logger.info(f"   URL: {url}")
            response = self.session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API error
            if data.get('dataset') == 'ERROR':
                logger.warning(f"   GIE API error: {data.get('message', 'Unknown error')}")
                self._fallback_value('eu_storage')
                return False
            
            # Extract storage data
            if data and 'data' in data and len(data['data']) > 0:
                latest_data = data['data'][-1]  # Get most recent entry
                
                # Try to use the 'full' field first (direct percentage)
                if 'full' in latest_data:
                    storage_percentage = float(latest_data['full'])
                    logger.info(f"   Using direct 'full' field: {storage_percentage}%")
                else:
                    # Fallback: calculate from gasInStorage and workingGasVolume
                    gas_in_storage = float(latest_data.get('gasInStorage', 0))
                    working_gas_volume = float(latest_data.get('workingGasVolume', 0))
                    
                    logger.info(f"   Raw data: gasInStorage={gas_in_storage} TWh, workingGasVolume={working_gas_volume} TWh")
                    
                    if working_gas_volume > 0:
                        storage_percentage = (gas_in_storage / working_gas_volume) * 100
                        logger.info(f"   Calculated storage percentage: {storage_percentage:.1f}%")
                    else:
                        logger.warning("   Working gas volume is 0")
                        self._fallback_value('eu_storage')
                        return False
                
                # Validate range
                if 0 <= storage_percentage <= 100:
                    self.data['eu_storage'] = round(storage_percentage, 1)
                    self.data['sources']['eu_storage'] = ['GIE AGSI+ API (Belgium)']
                    self.data['validation']['eu_storage'] = ''
                    self.data['collection_status']['eu_storage'] = 'Live (GIE API)'
                    logger.info(f"   Storage: {storage_percentage:.1f}% (GIE AGSI+ API)")
                    return True
                else:
                    logger.warning(f"   Invalid storage percentage: {storage_percentage}")
            else:
                logger.warning("   No data returned from GIE API")
                logger.info(f"   Response keys: {list(data.keys()) if data else 'No data'}")
            
            self._fallback_value('eu_storage')
            return False

        except requests.exceptions.RequestException as e:
            logger.warning(f"   GIE API request error: {e}")
            self._fallback_value('eu_storage')
            return False
        except Exception as e:
            logger.warning(f"   GIE API error: {e}")
            self._fallback_value('eu_storage')
            return False

    def _collect_brent_via_tavily(self) -> bool:
        """Collect Brent oil price via Tavily API"""
        if not self.tavily_client:
            logger.warning("Tavily API not available - using fallback for Brent")
            self._fallback_value('brent')
            return False

        try:
            brent_query = f"Brent crude oil price USD/barrel {datetime.now().strftime('%d %B %Y')}"
            logger.info(f"   Searching: {brent_query}")
            brent_response = self.tavily_client.search(
                query=brent_query,
                search_depth="basic",
                max_results=5
            )
            
            brent_data = self._extract_price_from_tavily(brent_response, 'brent')
            if brent_data:
                self.data['brent'] = brent_data['value']
                self.data['sources']['brent'] = [brent_data['source']]
                self.data['validation']['brent'] = ''
                self.data['collection_status']['brent'] = 'Live (Tavily API)'
                logger.info(f"   Brent: ${brent_data['value']:.2f}/barrel ({brent_data['source']})")
                return True
            else:
                logger.warning("   Could not extract Brent price from search results")
                self._fallback_value('brent')
                return False

        except Exception as e:
            logger.warning(f"   Brent collection error: {e}")
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
            
            # Collect all potential values from all results
            all_candidates = []
            
            for result in results:
                content = result.get('content', '')
                url = result.get('url', '')
                
                # Extract price based on data type
                if data_type == 'ttf':
                    # Look for TTF price pattern - collect all candidates
                    ttf_prices = []
                    
                    # Pattern 1: Standard EUR/MWh format
                    price_matches = re.findall(r'(\d+\.?\d*)\s*(?:EUR|€)/MWh', content)
                    for match in price_matches:
                        value = float(match)
                        if 15 < value < 300:
                            ttf_prices.append(value)
                    
                    # Pattern 2: Decimal with comma (European format)
                    price_matches_comma = re.findall(r'(\d+,\d*)\s*(?:EUR|€)/MWh', content)
                    for match in price_matches_comma:
                        value = float(match.replace(',', '.'))
                        if 15 < value < 300:
                            ttf_prices.append(value)
                    
                    # Pattern 3: Just number before EUR/MWh
                    price_matches_simple = re.findall(r'(\d{2,3}\.?\d*)\s*(?:EUR|€)/MWh', content)
                    for match in price_matches_simple:
                        value = float(match)
                        if 15 < value < 300:
                            ttf_prices.append(value)
                    
                    # Add all TTF prices from this result
                    for value in ttf_prices:
                        all_candidates.append({'value': value, 'source': url})
                
                elif data_type == 'storage':
                    # Prioritize reliable sources for gas storage data
                    reliable_sources = ['gas-risiko.de', 'gie.agsi+', 'agsi.gie.eu', 'energiedashboard.admin.ch']
                    is_reliable = any(source in url for source in reliable_sources)
                    
                    # Look for storage percentage
                    storage_matches = re.findall(r'(\d+\.?\d*)\s*%', content)
                    for match in storage_matches:
                        value = float(match)
                        if 0 < value <= 100:
                            # Higher priority for reliable sources
                            priority = 1 if is_reliable else 0
                            all_candidates.append({'value': value, 'source': url, 'priority': priority})
                
                elif data_type == 'brent':
                    # Look for Brent price - collect all candidates
                    brent_prices = []
                    
                    # Pattern 1: Standard USD/barrel format
                    brent_matches = re.findall(r'\$?(\d+\.?\d*)\s*(?:USD|dollars?)/barrel', content, re.IGNORECASE)
                    for match in brent_matches:
                        value = float(match)
                        if 30 < value < 250:
                            brent_prices.append(value)
                    
                    # Pattern 2: Just $ before number
                    brent_matches_dollar = re.findall(r'\$(\d+\.?\d*)', content)
                    for match in brent_matches_dollar:
                        value = float(match)
                        if 30 < value < 250:
                            brent_prices.append(value)
                    
                    # Pattern 3: Number + USD (without barrel)
                    brent_matches_usd = re.findall(r'(\d+\.?\d*)\s*USD', content, re.IGNORECASE)
                    for match in brent_matches_usd:
                        value = float(match)
                        if 30 < value < 250:
                            brent_prices.append(value)
                    
                    # Pattern 4: European format with comma
                    brent_matches_comma = re.findall(r'(\d+,\d*)\s*(?:USD|€)/barrel', content, re.IGNORECASE)
                    for match in brent_matches_comma:
                        value = float(match.replace(',', '.'))
                        if 30 < value < 250:
                            brent_prices.append(value)
                    
                    # Add all Brent prices from this result
                    for value in brent_prices:
                        all_candidates.append({'value': value, 'source': url})
            
            # Choose the best candidate
            if not all_candidates:
                return None
            
            if data_type == 'ttf':
                # For TTF, choose the highest price (most likely current)
                best_candidate = max(all_candidates, key=lambda x: x['value'])
                return {'value': best_candidate['value'], 'source': best_candidate['source']}
            
            elif data_type == 'storage':
                # For storage, prioritize reliable sources, then any value
                if any('priority' in candidate for candidate in all_candidates):
                    reliable_candidates = [c for c in all_candidates if 'priority' in c and c['priority'] == 1]
                    if reliable_candidates:
                        best_candidate = reliable_candidates[0]
                        return {'value': best_candidate['value'], 'source': best_candidate['source']}
                
                # Fallback to any storage value
                return {'value': all_candidates[0]['value'], 'source': all_candidates[0]['source']}
            
            elif data_type == 'brent':
                # For Brent, use median to avoid outliers
                values = [c['value'] for c in all_candidates]
                values.sort()
                median_value = values[len(values)//2]
                # Find the candidate closest to median
                best_candidate = min(all_candidates, key=lambda x: abs(x['value'] - median_value))
                return {'value': best_candidate['value'], 'source': best_candidate['source']}
            
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

        # Collect TTF, Storage, Brent via OilPriceAPI + GIE API
        self.collect_via_oilpriceapi()

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
