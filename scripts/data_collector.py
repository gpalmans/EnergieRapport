"""
Data Collector voor EnergieRapport
Verzamelt TTF, Belpex, EU Gas Storage, en Brent prijzen van meerdere bronnen
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnergyDataCollector:
    def __init__(self):
        self.data = {
            'ttf': None,
            'belpex': None,
            'eu_storage': None,
            'brent': None,
            'timestamp': datetime.now().isoformat(),
            'sources': {}
        }
        self.verification_threshold = 0.02  # 2% difference allowed
    
    def collect_ttf_price(self) -> Optional[float]:
        """Verzamel TTF aardgas prijs van meerdere bronnen"""
        sources = []
        
        # Bron 1: Trading Economics (via web scraping fallback)
        try:
            # Placeholder - in productie zou dit een echte API call zijn
            logger.info("Collecting TTF price from Trading Economics...")
            # ttf_price = self._scrape_trading_economics_ttf()
            # sources.append(('Trading Economics', ttf_price))
        except Exception as e:
            logger.warning(f"Failed to get TTF from Trading Economics: {e}")
        
        # Bron 2: ICE Endex (via API indien beschikbaar)
        try:
            logger.info("Collecting TTF price from ICE Endex...")
            # ttf_price = self._get_ice_endex_ttf()
            # sources.append(('ICE Endex', ttf_price))
        except Exception as e:
            logger.warning(f"Failed to get TTF from ICE Endex: {e}")
        
        # Voor demo: gebruik placeholder waarde
        # In productie: implementeer echte data sources
        ttf_demo = 60.60
        sources.append(('Demo Source', ttf_demo))
        
        if sources:
            verified_price = self._verify_sources(sources, 'TTF')
            self.data['ttf'] = verified_price
            self.data['sources']['ttf'] = [s[0] for s in sources]
            return verified_price
        
        return None
    
    def collect_belpex_price(self) -> Optional[float]:
        """Verzamel Belpex elektriciteit prijs"""
        sources = []
        
        # Bron 1: EPEX SPOT
        try:
            logger.info("Collecting Belpex price from EPEX...")
            # belpex_price = self._get_epex_belpex()
            # sources.append(('EPEX', belpex_price))
        except Exception as e:
            logger.warning(f"Failed to get Belpex from EPEX: {e}")
        
        # Bron 2: ENTSO-E Transparency Platform
        try:
            logger.info("Collecting Belpex price from ENTSO-E...")
            # belpex_price = self._get_entsoe_belpex()
            # sources.append(('ENTSO-E', belpex_price))
        except Exception as e:
            logger.warning(f"Failed to get Belpex from ENTSO-E: {e}")
        
        # Demo waarde
        belpex_demo = 104.00
        sources.append(('Demo Source', belpex_demo))
        
        if sources:
            verified_price = self._verify_sources(sources, 'Belpex')
            self.data['belpex'] = verified_price
            self.data['sources']['belpex'] = [s[0] for s in sources]
            return verified_price
        
        return None
    
    def collect_eu_storage(self) -> Optional[float]:
        """Verzamel EU gas storage percentage"""
        sources = []
        
        # Bron 1: AGSI+ (Gas Infrastructure Europe)
        try:
            logger.info("Collecting EU storage from AGSI+...")
            # storage_pct = self._get_agsi_storage()
            # sources.append(('AGSI+', storage_pct))
        except Exception as e:
            logger.warning(f"Failed to get storage from AGSI+: {e}")
        
        # Demo waarde
        storage_demo = 26.0
        sources.append(('Demo Source', storage_demo))
        
        if sources:
            verified_storage = self._verify_sources(sources, 'EU Storage')
            self.data['eu_storage'] = verified_storage
            self.data['sources']['eu_storage'] = [s[0] for s in sources]
            return verified_storage
        
        return None
    
    def collect_brent_price(self) -> Optional[float]:
        """Verzamel Brent crude oil prijs"""
        sources = []
        
        # Bron 1: EIA
        try:
            logger.info("Collecting Brent price from EIA...")
            # brent_price = self._get_eia_brent()
            # sources.append(('EIA', brent_price))
        except Exception as e:
            logger.warning(f"Failed to get Brent from EIA: {e}")
        
        # Demo waarde
        brent_demo = 113.00
        sources.append(('Demo Source', brent_demo))
        
        if sources:
            verified_price = self._verify_sources(sources, 'Brent')
            self.data['brent'] = verified_price
            self.data['sources']['brent'] = [s[0] for s in sources]
            return verified_price
        
        return None
    
    def _verify_sources(self, sources: List[Tuple[str, float]], data_type: str) -> float:
        """Verifieer dat bronnen binnen threshold liggen"""
        if len(sources) < 1:
            raise ValueError(f"No sources available for {data_type}")
        
        if len(sources) == 1:
            logger.warning(f"Only one source for {data_type}: {sources[0][0]}")
            return sources[0][1]
        
        # Bereken gemiddelde
        values = [s[1] for s in sources]
        avg = sum(values) / len(values)
        
        # Check of alle waarden binnen threshold liggen
        for source_name, value in sources:
            diff_pct = abs((value - avg) / avg)
            if diff_pct > self.verification_threshold:
                logger.warning(
                    f"{data_type} source {source_name} differs {diff_pct*100:.1f}% from average"
                )
        
        logger.info(f"{data_type}: {avg:.2f} (verified from {len(sources)} sources)")
        return round(avg, 2)
    
    def collect_all(self) -> Dict:
        """Verzamel alle data"""
        logger.info("Starting data collection...")
        
        self.collect_ttf_price()
        self.collect_belpex_price()
        self.collect_eu_storage()
        self.collect_brent_price()
        
        # Valideer dat alle data verzameld is
        missing = [k for k, v in self.data.items() if v is None and k not in ['timestamp', 'sources']]
        if missing:
            logger.error(f"Failed to collect: {', '.join(missing)}")
            raise ValueError(f"Missing required data: {missing}")
        
        logger.info("Data collection completed successfully")
        return self.data
    
    def save_to_file(self, filepath: str = 'data/latest_prices.json'):
        """Sla verzamelde data op naar bestand"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(self.data, f, indent=2)
        logger.info(f"Data saved to {filepath}")

def main():
    collector = EnergyDataCollector()
    data = collector.collect_all()
    collector.save_to_file()
    
    # Print samenvatting
    print("\n=== Verzamelde Data ===")
    print(f"TTF Gas: €{data['ttf']:.2f}/MWh")
    print(f"Belpex: €{data['belpex']:.2f}/MWh")
    print(f"EU Storage: {data['eu_storage']:.1f}%")
    print(f"Brent: ${data['brent']:.2f}/barrel")
    print(f"Timestamp: {data['timestamp']}")

if __name__ == '__main__':
    main()
