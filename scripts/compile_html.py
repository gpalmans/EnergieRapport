#!/usr/bin/env python3
"""
CLI entry point for compiling offline.html from JSX.
Usage: python scripts/compile_html.py
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.jsx_to_html_compiler import JsxToHtmlCompiler

def main():
    print("Compiling offline.html from JSX...")
    compiler = JsxToHtmlCompiler()
    
    try:
        result = compiler.compile(
            'src/EnergieRapport.jsx',
            'templates/energy_report_template.html',
            'public/offline.html'
        )
        
        if not result:
            print("ERROR: Compilation failed")
            return 1
        
        print("[OK] offline.html compiled successfully")
        return 0
    
    except Exception as e:
        print(f"ERROR: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
