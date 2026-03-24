#!/usr/bin/env python3
"""
CLI entry point for validating JSX and HTML synchronization.
Usage: python scripts/validate_sync.py
"""

import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.sync_validator import SyncValidator

def main():
    print("Validating JSX and HTML synchronization...")
    validator = SyncValidator()
    
    try:
        validator.validate_sync(
            'src/EnergieRapport.jsx',
            'public/offline.html'
        )
        
        print("[OK] JSX and HTML are perfectly synchronized")
        return 0
    
    except ValueError as e:
        print(f"ERROR: {e}")
        return 1
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
