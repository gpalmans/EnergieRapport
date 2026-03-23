"""
Crisis Detector voor EnergieRapport
Detecteert significante prijsschokken die AI-analyse triggeren
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CrisisDetector:
    def __init__(self, threshold: float = 0.10):
        """
        Args:
            threshold: Percentage verandering die als crisis wordt beschouwd (default 10%)
        """
        self.threshold = threshold
        self.crisis_detected = False
        self.crisis_details = []
    
    def load_current_data(self) -> Dict:
        """Laad huidige prijsdata"""
        filepath = 'data/latest_prices.json'
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"No current data found at {filepath}")
        
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def load_previous_data(self) -> Optional[Dict]:
        """Laad vorige dag prijsdata"""
        filepath = 'data/previous_prices.json'
        if not os.path.exists(filepath):
            logger.warning("No previous data found - skipping crisis detection")
            return None
        
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def detect_price_shock(self, current: float, previous: float, name: str) -> bool:
        """Detecteer prijsschok voor een specifieke commodity"""
        if previous == 0:
            logger.warning(f"Previous {name} price is 0, cannot calculate change")
            return False
        
        change_pct = ((current - previous) / previous) * 100
        abs_change = abs(change_pct)
        
        if abs_change >= (self.threshold * 100):
            direction = "stijging" if change_pct > 0 else "daling"
            self.crisis_details.append({
                'commodity': name,
                'change_pct': round(change_pct, 2),
                'direction': direction,
                'current': current,
                'previous': previous
            })
            logger.warning(
                f"CRISIS DETECTED: {name} {direction} van {abs_change:.1f}% "
                f"({previous:.2f} → {current:.2f})"
            )
            return True
        
        logger.info(f"{name}: {change_pct:+.1f}% (no crisis)")
        return False
    
    def analyze(self) -> bool:
        """Analyseer of er een crisis situatie is"""
        current = self.load_current_data()
        previous = self.load_previous_data()
        
        if previous is None:
            logger.info("No previous data - no crisis detection possible")
            return False
        
        # Check elke commodity
        crisis_flags = []
        
        if current.get('ttf') and previous.get('ttf'):
            crisis_flags.append(
                self.detect_price_shock(current['ttf'], previous['ttf'], 'TTF Gas')
            )
        
        if current.get('belpex') and previous.get('belpex'):
            crisis_flags.append(
                self.detect_price_shock(current['belpex'], previous['belpex'], 'Belpex')
            )
        
        if current.get('brent') and previous.get('brent'):
            crisis_flags.append(
                self.detect_price_shock(current['brent'], previous['brent'], 'Brent Oil')
            )
        
        if current.get('eu_storage') and previous.get('eu_storage'):
            # Voor storage: absolute change van >5% is significant
            storage_change = abs(current['eu_storage'] - previous['eu_storage'])
            if storage_change >= 5.0:
                self.crisis_details.append({
                    'commodity': 'EU Gas Storage',
                    'change_pct': round(storage_change, 2),
                    'direction': 'change',
                    'current': current['eu_storage'],
                    'previous': previous['eu_storage']
                })
                crisis_flags.append(True)
                logger.warning(
                    f"CRISIS DETECTED: EU Storage change van {storage_change:.1f}% "
                    f"({previous['eu_storage']:.1f}% → {current['eu_storage']:.1f}%)"
                )
            else:
                logger.info(f"EU Storage: {storage_change:+.1f}% (no crisis)")
                crisis_flags.append(False)
        
        self.crisis_detected = any(crisis_flags)
        return self.crisis_detected
    
    def save_crisis_report(self):
        """Sla crisis rapport op"""
        if not self.crisis_detected:
            return
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'crisis_detected': True,
            'details': self.crisis_details
        }
        
        os.makedirs('data', exist_ok=True)
        with open('data/crisis_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Crisis report saved with {len(self.crisis_details)} alerts")
    
    def archive_current_as_previous(self):
        """Archiveer huidige data als vorige voor volgende run"""
        current_path = 'data/latest_prices.json'
        previous_path = 'data/previous_prices.json'
        
        if os.path.exists(current_path):
            with open(current_path, 'r') as f:
                current = json.load(f)
            
            with open(previous_path, 'w') as f:
                json.dump(current, f, indent=2)
            
            logger.info("Current data archived as previous")

def main():
    detector = CrisisDetector(threshold=0.10)
    
    try:
        crisis = detector.analyze()
        detector.save_crisis_report()
        detector.archive_current_as_previous()
        
        # Output voor GitHub Actions
        if crisis:
            print("\n=== CRISIS GEDETECTEERD ===")
            for detail in detector.crisis_details:
                print(f"{detail['commodity']}: {detail['change_pct']:+.1f}% {detail['direction']}")
            print("::set-output name=crisis_detected::true")
            sys.exit(0)  # Success maar met crisis flag
        else:
            print("\n=== Geen crisis gedetecteerd ===")
            print("::set-output name=crisis_detected::false")
            sys.exit(0)
    
    except FileNotFoundError as e:
        logger.error(f"Data file not found: {e}")
        print("::set-output name=crisis_detected::false")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Crisis detection failed: {e}")
        print("::set-output name=crisis_detected::false")
        sys.exit(1)

if __name__ == '__main__':
    main()
