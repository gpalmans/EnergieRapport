#!/usr/bin/env python3
"""
Verify 100% synchronization between EnergieRapport.jsx and public/offline.html
Extracts all text content and compares section by section.
"""

import re
import sys
from pathlib import Path

def extract_jsx_text_content(jsx_path):
    """Extract all text content from JSX file, organized by section"""
    with open(jsx_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    sections = {}
    
    # Extract Advies tab content - the most critical section
    advies_match = re.search(r'{tab === "advies" && \(<>(.+?)</>}\)', content, re.DOTALL)
    if advies_match:
        advies_content = advies_match.group(1)
        
        # Extract all text nodes (content between > and <)
        text_nodes = re.findall(r'>([^<>]+)<', advies_content)
        # Filter out JSX expressions and whitespace-only
        text_nodes = [t.strip() for t in text_nodes if t.strip() and not t.strip().startswith('{')]
        
        sections['advies'] = text_nodes
    
    return sections

def extract_html_text_content(html_path):
    """Extract all text content from offline HTML, organized by section"""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    sections = {}
    
    # Extract Advies tab content
    advies_match = re.search(r'<!-- ====== ADVIES ====== -->(.+?)<!-- ====== BRONNEN ====== -->', content, re.DOTALL)
    if advies_match:
        advies_content = advies_match.group(1)
        
        # Extract all text nodes (content between > and <)
        text_nodes = re.findall(r'>([^<>]+)<', advies_content)
        # Filter out whitespace-only and script content
        text_nodes = [t.strip() for t in text_nodes if t.strip() and not t.strip().startswith('function') and not t.strip().startswith('const')]
        
        sections['advies'] = text_nodes
    
    return sections

def compare_sections(jsx_sections, html_sections):
    """Compare sections and report differences"""
    differences = []
    
    for section_name in jsx_sections:
        jsx_texts = jsx_sections.get(section_name, [])
        html_texts = html_sections.get(section_name, [])
        
        # Compare lengths
        if len(jsx_texts) != len(html_texts):
            differences.append(f"Section '{section_name}': Different number of text nodes (JSX: {len(jsx_texts)}, HTML: {len(html_texts)})")
        
        # Compare content
        for i, jsx_text in enumerate(jsx_texts):
            if i >= len(html_texts):
                differences.append(f"Section '{section_name}': Missing in HTML: '{jsx_text[:100]}...'")
            elif jsx_text != html_texts[i]:
                # Normalize for comparison (handle HTML entities, etc.)
                jsx_normalized = jsx_text.replace('—', '—').replace('–', '–')
                html_normalized = html_texts[i].replace('&amp;', '&').replace('&mdash;', '—').replace('&ndash;', '–')
                
                if jsx_normalized != html_normalized:
                    differences.append(f"Section '{section_name}' text mismatch at position {i}:")
                    differences.append(f"  JSX:  '{jsx_text[:100]}...'")
                    differences.append(f"  HTML: '{html_texts[i][:100]}...'")
    
    return differences

def main():
    project_root = Path(__file__).parent.parent
    jsx_path = project_root / 'src' / 'EnergieRapport.jsx'
    html_path = project_root / 'public' / 'offline.html'
    
    print("🔍 Verifying synchronization between JSX and offline HTML...")
    print(f"JSX:  {jsx_path}")
    print(f"HTML: {html_path}")
    print()
    
    jsx_sections = extract_jsx_text_content(jsx_path)
    html_sections = extract_html_text_content(html_path)
    
    differences = compare_sections(jsx_sections, html_sections)
    
    if differences:
        print("❌ SYNCHRONIZATION FAILED - Differences found:")
        print()
        for diff in differences:
            print(diff)
        print()
        print(f"Total differences: {len(differences)}")
        sys.exit(1)
    else:
        print("✅ SYNCHRONIZATION VERIFIED - JSX and HTML are in sync!")
        sys.exit(0)

if __name__ == '__main__':
    main()
