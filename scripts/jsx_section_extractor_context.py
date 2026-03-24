"""
JSX Section Extractor — Context Tab
Extracts the Geopolitiek/Context tab content from JSX and renders it as HTML.
"""

import re
import html as html_lib
from typing import Optional


def _extract_between_markers(jsx: str, start_marker: str, end_marker: str) -> Optional[str]:
    """
    Extract JSX content between two comment markers.

    Args:
        jsx: Full JSX source string
        start_marker: Comment marker string to start at
        end_marker: Comment marker string to end at

    Returns:
        Content between markers, or None if not found
    """
    start_idx = jsx.find(start_marker)
    end_idx = jsx.find(end_marker, start_idx + 1)
    if start_idx == -1 or end_idx == -1:
        return None
    return jsx[start_idx:end_idx]


def _find_array_end(text: str, start: int) -> int:
    """
    Find the closing bracket of a JS array using bracket counting.

    Args:
        text: Source text
        start: Index of the opening bracket '['

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


def _parse_simple_string_triplets(array_text: str) -> list[tuple[str, str, str]]:
    """
    Parse array of ["a", "b", "c"] triplets from JS array literal text.

    Args:
        array_text: String content of the array (without outer brackets)

    Returns:
        List of (a, b, c) tuples
    """
    # Match array items like ["text", "text", "#color"] possibly with escaped chars
    pattern = r'\[\s*"((?:[^"\\]|\\.)*)"\s*,\s*"((?:[^"\\]|\\.)*)"\s*,\s*"((?:[^"\\]|\\.)*)"\s*\]'
    results = []
    for m in re.finditer(pattern, array_text):
        a = m.group(1).replace('\\"', '"').replace("\\'", "'")
        b = m.group(2).replace('\\"', '"').replace("\\'", "'")
        c = m.group(3).replace('\\"', '"').replace("\\'", "'")
        results.append((a, b, c))
    return results


def _parse_simple_string_pairs(array_text: str) -> list[tuple[str, str]]:
    """
    Parse array of ["a", "b"] pairs from JS array literal text.

    Args:
        array_text: String content of the array (without outer brackets)

    Returns:
        List of (a, b) tuples
    """
    pattern = r'\[\s*"((?:[^"\\]|\\.)*)"\s*,\s*"((?:[^"\\]|\\.)*)"\s*\]'
    results = []
    for m in re.finditer(pattern, array_text):
        a = m.group(1).replace('\\"', '"').replace("\\'", "'")
        b = m.group(2).replace('\\"', '"').replace("\\'", "'")
        results.append((a, b))
    return results


def _extract_iea_text_para(section_text: str) -> str:
    """
    Extract the IEA paragraph text from the context JSX section.

    Args:
        section_text: Context section JSX text

    Returns:
        Paragraph text with HTML entities preserved
    """
    # Find the <p> block after IEA heading
    m = re.search(
        r'IEA Strategische Oliereserves.*?<p[^>]*>\s*(.*?)\s*</p>',
        section_text,
        re.DOTALL
    )
    if not m:
        return ""
    # Collapse whitespace and strip JSX expression delimiters
    raw = m.group(1)
    # Remove JSX-style strong tags like <strong style={{...}}>...</strong>
    # Convert them to HTML strong tags
    raw = re.sub(r'<strong\s+style=\{\{[^}]*\}\}>', '<strong style="color:#f8fafc">', raw)
    # Remove JSX style props from generic elements
    raw = re.sub(r'\s+style=\{\{[^}]*\}\}', '', raw)
    raw = re.sub(r'\s+', ' ', raw).strip()
    return raw


def _extract_be_mix_note(section_text: str) -> str:
    """
    Extract the Belgian energy mix note text.

    Args:
        section_text: Context section JSX text

    Returns:
        Note text string
    """
    m = re.search(
        r'⚡ Belpex[^<"]*',
        section_text
    )
    if m:
        return m.group(0).strip()
    return ""


def _badge_style(color: str) -> str:
    """
    Generate inline badge style for a given color hex.

    Args:
        color: Hex color string like '#ef4444'

    Returns:
        style attribute value string
    """
    return f"background:{color}22;color:{color};border:1px solid {color}44"


def _crisis_badge_class(color: str) -> str:
    """Map hex color to badge CSS class name."""
    color_map = {
        "#ef4444": "badge-red",
        "#f97316": "badge-orange",
        "#eab308": "",  # custom
        "#8b5cf6": "badge-purple",
        "#22c55e": "badge-green",
        "#0ea5e9": "badge-blue",
    }
    return color_map.get(color, "")


def render_context_section(jsx_content: str) -> str:
    """
    Extract the context (Geopolitiek) section from JSX and render as HTML.

    Args:
        jsx_content: Full JSX source string

    Returns:
        HTML string for the tab-context panel content
    """
    section = _extract_between_markers(jsx_content, "{/* ── CONTEXT ── */}", "{/* ── FORECAST ── */}")
    if not section:
        return "<!-- context section not found -->"

    # --- 1. Gas storage rows ---
    # Find the array starting after "Europese Gasvoorraden"
    storage_marker = section.find('"EU-gemiddelde')
    if storage_marker == -1:
        storage_rows_html = ""
    else:
        arr_start = section.rfind("[", 0, storage_marker)
        arr_end = _find_array_end(section, arr_start)
        storage_raw = section[arr_start:arr_end + 1]
        storage_items = _parse_simple_string_triplets(storage_raw)
        storage_rows_parts = []
        for i, (label, value, color) in enumerate(storage_items):
            border = "" if i < len(storage_items) - 1 else "border-bottom:none"
            storage_rows_parts.append(
                f'<div class="storage-row" style="{border}">'
                f'<span class="storage-label">{html_lib.escape(label)}</span>'
                f'<span style="color:{color};font-weight:700">{html_lib.escape(value)}</span>'
                f'</div>'
            )
        storage_rows_html = "\n        ".join(storage_rows_parts)

    # --- 2. Geopolitical crisis items ---
    crisis_marker = section.find("Straat van Hormuz Blokkade")
    crisis_html_parts = []
    if crisis_marker != -1:
        arr_start = section.rfind("[", 0, crisis_marker)
        arr_end = _find_array_end(section, arr_start)
        crisis_raw = section[arr_start:arr_end + 1]
        crisis_items = _parse_simple_string_triplets(crisis_raw)
        for i, (title, color, text) in enumerate(crisis_items):
            mb = "margin-bottom:14px" if i < len(crisis_items) - 1 else ""
            badge_class = _crisis_badge_class(color)
            if badge_class:
                badge_html = f'<span class="badge {badge_class}">{html_lib.escape(title)}</span>'
            else:
                badge_html = (f'<span class="badge" style="{_badge_style(color)}">'
                              f'{html_lib.escape(title)}</span>')
            crisis_html_parts.append(
                f'<div style="{mb}">\n'
                f'  {badge_html}\n'
                f'  <p style="margin-top:7px;margin-bottom:0;font-size:13px;color:#94a3b8;line-height:1.6">'
                f'{html_lib.escape(text)}</p>\n'
                f'</div>'
            )

    # --- 3. IEA table rows ---
    iea_marker = section.find('"Volume"')
    if iea_marker == -1:
        iea_rows_html = ""
        iea_para = ""
        iea_source = ""
    else:
        arr_start = section.rfind("[", 0, iea_marker)
        arr_end = _find_array_end(section, arr_start)
        iea_raw = section[arr_start:arr_end + 1]
        iea_items = _parse_simple_string_pairs(iea_raw)
        iea_row_parts = []
        for i, (k, v) in enumerate(iea_items):
            border = "" if i < len(iea_items) - 1 else "border-bottom:none"
            iea_row_parts.append(
                f'<div class="iea-row" style="{border}">'
                f'<span class="iea-key">{html_lib.escape(k)}</span>'
                f'<span class="iea-val">{html_lib.escape(v)}</span>'
                f'</div>'
            )
        iea_rows_html = "\n          ".join(iea_row_parts)

        # IEA paragraph
        iea_para_m = re.search(
            r'IEA Strategische Oliereserves.*?<p[^>]*>(.*?)</p>',
            section, re.DOTALL
        )
        if iea_para_m:
            raw_para = iea_para_m.group(1)
            # Convert JSX strong style to HTML
            raw_para = re.sub(
                r'<strong\s+style=\{\{\s*color:\s*"(#[a-fA-F0-9]+)"\s*\}\}>',
                r'<strong style="color:\1">',
                raw_para
            )
            raw_para = re.sub(r'\s+', ' ', raw_para).strip()
            iea_para = raw_para
        else:
            iea_para = ""

        # IEA source line
        iea_source_m = re.search(r'Bronnen: IEA[^"<\n]+', section)
        iea_source = iea_source_m.group(0).strip() if iea_source_m else ""

    # --- 4. Belgian mix table rows ---
    be_mix_marker = section.find('"Kern (Doel 4')
    if be_mix_marker == -1:
        be_mix_rows_html = ""
    else:
        arr_start = section.rfind("[", 0, be_mix_marker)
        arr_end = _find_array_end(section, arr_start)
        be_mix_raw = section[arr_start:arr_end + 1]
        be_mix_items = _parse_simple_string_pairs(be_mix_raw)
        be_mix_parts = []
        for i, (k, v) in enumerate(be_mix_items):
            border = "" if i < len(be_mix_items) - 1 else "border-bottom:none"
            be_mix_parts.append(
                f'<div class="be-mix-row" style="{border}">'
                f'<span style="color:#94a3b8">{html_lib.escape(k)}</span>'
                f'<span style="color:#60a5fa;font-weight:600">{html_lib.escape(v)}</span>'
                f'</div>'
            )
        be_mix_rows_html = "\n          ".join(be_mix_parts)

    # Belgian mix paragraphs (3 prose paragraphs before the table)
    be_mix_para_m = re.search(
        r'Belgische Energiemix.*?<p[^>]*>(.*?)</p>.*?<p[^>]*>(.*?)</p>.*?<p[^>]*>(.*?)</p>',
        section, re.DOTALL
    )
    be_para1 = be_para2 = be_para3 = ""
    if be_mix_para_m:
        def _clean_jsx_para(raw: str) -> str:
            raw = re.sub(r'<strong\s+style=\{\{\s*color:\s*"(#[a-fA-F0-9]+)"\s*\}\}>',
                         r'<strong style="color:\1">', raw)
            raw = re.sub(r'<em>', '<em>', raw)
            raw = re.sub(r'\s+', ' ', raw).strip()
            return raw
        be_para1 = _clean_jsx_para(be_mix_para_m.group(1))
        be_para2 = _clean_jsx_para(be_mix_para_m.group(2))
        be_para3 = _clean_jsx_para(be_mix_para_m.group(3))

    # Belgian mix note
    be_note_m = re.search(r'⚡ Belpex[^\n"<]+', section)
    be_note = be_note_m.group(0).strip() if be_note_m else ""

    # Storage alert note
    storage_note_m = re.search(r'⚠️ Gasvelden[^\n"<]+', section)
    storage_note = storage_note_m.group(0).strip() if storage_note_m else ""

    # --- Render HTML ---
    crisis_joined = "\n\n        ".join(crisis_html_parts)

    return f"""<div class="two-col">

      <div class="section">
        <h3 style="margin:0 0 14px;color:#f8fafc;font-size:15px">🏭 Europese Gasvoorraden</h3>
        {storage_rows_html}
        <div class="storage-block-note">
          {html_lib.escape(storage_note)}
        </div>
      </div>

      <div class="section">
        <h3 style="margin:0 0 14px;color:#f8fafc;font-size:15px">⚔️ Geopolitieke Crisissituatie</h3>

        {crisis_joined}
      </div>

      <div class="section">
        <h3 style="margin:0 0 14px;color:#f8fafc;font-size:15px">🛢️ IEA Strategische Oliereserves</h3>
        <p style="margin-top:0;font-size:13px;color:#94a3b8;line-height:1.7;margin-bottom:12px">
          {iea_para}
        </p>
        <div class="iea-bg">
          {iea_rows_html}
        </div>
        <p class="iea-source" style="margin-top:12px">{html_lib.escape(iea_source)}</p>
      </div>

      <div class="section">
        <h3 style="margin:0 0 14px;color:#f8fafc;font-size:15px">🇧🇪 Belgische Energiemix — Waarom Gasprijzen de Elektriciteitsprijs Bepalen</h3>
        <p style="margin-top:0;font-size:13px;color:#94a3b8;line-height:1.7;margin-bottom:12px">
          {be_para1}
        </p>
        <p style="margin-top:0;font-size:13px;color:#94a3b8;line-height:1.7;margin-bottom:12px">
          {be_para2}
        </p>
        <p style="margin-top:0;font-size:13px;color:#94a3b8;line-height:1.7">
          {be_para3}
        </p>
        <div class="be-mix-bg" style="margin-top:12px">
          {be_mix_rows_html}
        </div>
        <p class="be-mix-note">
          {html_lib.escape(be_note)}
        </p>
      </div>

    </div>"""
