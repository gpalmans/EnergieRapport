"""
JSX Section Extractor — Forecast Tab
Extracts the Forecast tab content from JSX and renders it as HTML.
"""

import re
import html as html_lib
from typing import Optional


def _find_array_end(text: str, start: int) -> int:
    """
    Find the closing bracket of a JS array using bracket counting.

    Args:
        text: Source text
        start: Index of the opening '['

    Returns:
        Index of the closing ']', or -1 if not found
    """
    depth = 0
    in_string = False
    string_char = None
    i = start
    while i < len(text):
        c = text[i]
        if in_string:
            if c == '\\':
                i += 2
                continue
            if c == string_char:
                in_string = False
        else:
            if c in ('"', "'", '`'):
                in_string = True
                string_char = c
            elif c == '[':
                depth += 1
            elif c == ']':
                depth -= 1
                if depth == 0:
                    return i
        i += 1
    return -1


def _find_object_end(text: str, start: int) -> int:
    """
    Find the closing brace of a JS object using brace counting.

    Args:
        text: Source text
        start: Index of the opening '{'

    Returns:
        Index of the closing '}', or -1 if not found
    """
    depth = 0
    in_string = False
    string_char = None
    i = start
    while i < len(text):
        c = text[i]
        if in_string:
            if c == '\\':
                i += 2
                continue
            if c == string_char:
                in_string = False
        else:
            if c in ('"', "'", '`'):
                in_string = True
                string_char = c
            elif c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    return i
        i += 1
    return -1


def _extract_string_prop(obj_text: str, key: str) -> str:
    """
    Extract a string property value from a JS object literal text.

    Args:
        obj_text: Text of the object (without outer braces)
        key: Property name to extract

    Returns:
        String value, or empty string if not found
    """
    m = re.search(rf'{re.escape(key)}:\s*"((?:[^"\\]|\\.)*)"', obj_text)
    if m:
        return m.group(1).replace('\\"', '"').replace("\\'", "'")
    return ""


def _extract_items_array(obj_text: str) -> list[str]:
    """
    Extract the items: [...] array from a scenario object literal text.

    Args:
        obj_text: Text of the object literal

    Returns:
        List of item strings
    """
    items_m = re.search(r'items:\s*\[', obj_text)
    if not items_m:
        return []
    arr_start = items_m.end() - 1
    arr_end = _find_array_end(obj_text, arr_start)
    if arr_end == -1:
        return []
    arr_content = obj_text[arr_start + 1:arr_end]
    # Parse individual strings
    items = re.findall(r'"((?:[^"\\]|\\.)*)"', arr_content)
    return [x.replace('\\"', '"').replace("\\'", "'") for x in items]


def _parse_scenario_objects(array_text: str) -> list[dict]:
    """
    Parse the array of scenario objects from JSX forecast section.

    Args:
        array_text: Text of the array containing 3 scenario objects

    Returns:
        List of dicts with keys: t, p, c, ttf, belpex, items, note
    """
    results = []
    i = 0
    while i < len(array_text):
        obj_start = array_text.find('{', i)
        if obj_start == -1:
            break
        obj_end = _find_object_end(array_text, obj_start)
        if obj_end == -1:
            break
        obj_text = array_text[obj_start + 1:obj_end]
        t = _extract_string_prop(obj_text, 't')
        if t:
            results.append({
                't': t,
                'p': _extract_string_prop(obj_text, 'p'),
                'c': _extract_string_prop(obj_text, 'c'),
                'ttf': _extract_string_prop(obj_text, 'ttf'),
                'belpex': _extract_string_prop(obj_text, 'belpex'),
                'items': _extract_items_array(obj_text),
                'note': _extract_string_prop(obj_text, 'note'),
            })
        i = obj_end + 1
    return results


def _parse_key_factor_triplets(array_text: str) -> list[tuple[str, str, str]]:
    """
    Parse key factor [icon, title, description] triplets from array text.

    Args:
        array_text: JS array literal content

    Returns:
        List of (icon, title, description) tuples
    """
    pattern = (
        r'\[\s*"((?:[^"\\]|\\.)*)"\s*,'
        r'\s*"((?:[^"\\]|\\.)*)"\s*,'
        r'\s*"((?:[^"\\]|\\.)*)"\s*\]'
    )
    results = []
    for m in re.finditer(pattern, array_text):
        icon = m.group(1).replace('\\"', '"').replace("\\'", "'")
        title = m.group(2).replace('\\"', '"').replace("\\'", "'")
        desc = m.group(3).replace('\\"', '"').replace("\\'", "'")
        results.append((icon, title, desc))
    return results


def _scenario_card_class(color: str) -> str:
    """Map scenario color to CSS card class."""
    mapping = {
        "#22c55e": "scenario-card-green",
        "#0ea5e9": "scenario-card-blue",
        "#ef4444": "scenario-card-red",
    }
    return mapping.get(color, "scenario-card-blue")


def _badge_class(color: str) -> str:
    """Map color to badge CSS class."""
    mapping = {
        "#22c55e": "badge-green",
        "#0ea5e9": "badge-blue",
        "#ef4444": "badge-red",
    }
    return mapping.get(color, "badge-blue")


def render_forecast_section(jsx_content: str) -> str:
    """
    Extract the forecast section from JSX and render as HTML.

    Args:
        jsx_content: Full JSX source string

    Returns:
        HTML string for the tab-forecast panel content
    """
    start = jsx_content.find("{/* ── FORECAST ── */}")
    end = jsx_content.find("{/* ── ADVIES ── */}", start + 1)
    if start == -1 or end == -1:
        return "<!-- forecast section not found -->"
    section = jsx_content[start:end]

    # --- 1. Scenario cards ---
    sc_marker = section.find('t: "⬇ Bearish')
    scenario_cards_html = ""
    if sc_marker != -1:
        arr_start = section.rfind("[", 0, sc_marker)
        arr_end = _find_array_end(section, arr_start)
        sc_raw = section[arr_start:arr_end + 1]
        scenarios = _parse_scenario_objects(sc_raw)

        card_parts = []
        for s in scenarios:
            card_cls = _scenario_card_class(s['c'])
            badge_cls = _badge_class(s['c'])
            items_html = "\n          ".join(
                f"<li>{html_lib.escape(x)}</li>" for x in s['items']
            )
            card_parts.append(f"""      <div class="{card_cls}">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;gap:6px">
          <h4 style="margin:0;color:{s['c']};font-size:13px;line-height:1.4">{html_lib.escape(s['t'])}</h4>
          <span class="badge {badge_cls}" style="flex-shrink:0">P: {html_lib.escape(s['p'])}</span>
        </div>
        <div style="margin-bottom:10px">
          <div style="font-size:11px;color:#64748b;margin-bottom:3px">Range apr–mei 2026</div>
          <div style="color:#0ea5e9;font-size:12px">TTF: <strong style="color:{s['c']}">{html_lib.escape(s['ttf'])}/MWh</strong></div>
          <div style="color:#a78bfa;font-size:12px">Belpex: <strong style="color:{s['c']}">{html_lib.escape(s['belpex'])}/MWh</strong></div>
        </div>
        <ul style="margin:0;padding:0 0 0 14px;font-size:12px;color:#94a3b8;line-height:1.9">
          {items_html}
        </ul>
        <div class="scenario-note">💡 {html_lib.escape(s['note'])}</div>
      </div>""")
        scenario_cards_html = "\n\n".join(card_parts)

    # --- 2. Key factors ---
    kf_marker = section.find('"🔴"')
    key_factors_html = ""
    if kf_marker != -1:
        arr_start = section.rfind("[", 0, kf_marker)
        arr_end = _find_array_end(section, arr_start)
        kf_raw = section[arr_start:arr_end + 1]
        factors = _parse_key_factor_triplets(kf_raw)
        kf_parts = []
        for icon, title, desc in factors:
            kf_parts.append(f"""      <div class="key-factor">
        <div class="key-factor-title">{html_lib.escape(icon)} {html_lib.escape(title)}</div>
        <div class="key-factor-text">{html_lib.escape(desc)}</div>
      </div>""")
        key_factors_html = "\n\n".join(kf_parts)

    return f"""
    <div class="section">
      <h3 style="margin:0 0 14px;color:#f8fafc;font-size:16px">📈 Drie Scenario&#39;s — TTF Gas-forecast (mrt–mei 2026)</h3>
      <canvas id="forecast-chart" width="900" height="250"></canvas>
    </div>

    <div class="scenario-grid" style="margin-bottom:18px">

{scenario_cards_html}

    </div>

    <div class="section" style="margin-top:18px">
      <h3 style="margin:0 0 8px;color:#f8fafc;font-size:15px">🔑 Sleutelfactoren om op te volgen</h3>
      <p style="font-size:12px;color:#64748b;margin-top:0;margin-bottom:14px">Gerangschikt op impact: 🔴 Kritiek · 🟡 Belangrijk · 🟢 Moderate invloed</p>

{key_factors_html}

    </div>"""
