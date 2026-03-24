"""
JSX Section Extractor — Bronnen Tab
Extracts the Bronnen (sources) tab content from JSX and renders it as HTML.
"""

import re
import html as html_lib


def _find_array_end(text: str, start: int) -> int:
    """
    Find closing bracket using bracket counting.

    Args:
        text: Source text
        start: Index of opening '['

    Returns:
        Index of closing ']', or -1
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
    Find closing brace using brace counting.

    Args:
        text: Source text
        start: Index of opening '{'

    Returns:
        Index of closing '}', or -1
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
    Extract a string property value from JS object literal text.

    Args:
        obj_text: Object contents (without outer braces)
        key: Property key name

    Returns:
        Property value or empty string
    """
    m = re.search(rf'(?<![a-zA-Z]){re.escape(key)}:\s*"((?:[^"\\]|\\.)*)"', obj_text)
    if m:
        return m.group(1).replace('\\"', '"').replace("\\'", "'")
    return ""


def _parse_items_in_category(obj_text: str) -> list[dict]:
    """
    Parse the items array inside a source category object.

    Args:
        obj_text: Object content text

    Returns:
        List of dicts with keys: n, d, url
    """
    items_m = re.search(r'items:\s*\[', obj_text)
    if not items_m:
        return []
    arr_start = items_m.end() - 1
    arr_end = _find_array_end(obj_text, arr_start)
    if arr_end == -1:
        return []
    arr_text = obj_text[arr_start:arr_end + 1]

    results = []
    i = 0
    while i < len(arr_text):
        obj_start = arr_text.find('{', i)
        if obj_start == -1:
            break
        obj_end = _find_object_end(arr_text, obj_start)
        if obj_end == -1:
            break
        item_text = arr_text[obj_start + 1:obj_end]
        n = _extract_string_prop(item_text, 'n')
        if n:
            results.append({
                'n': n,
                'd': _extract_string_prop(item_text, 'd'),
                'url': _extract_string_prop(item_text, 'url'),
            })
        i = obj_end + 1
    return results


def _parse_source_categories(array_text: str) -> list[dict]:
    """
    Parse the full source categories array from JSX.

    Args:
        array_text: Array literal text containing category objects

    Returns:
        List of dicts with keys: cat, color, items
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
        cat = _extract_string_prop(obj_text, 'cat')
        if cat:
            results.append({
                'cat': cat,
                'color': _extract_string_prop(obj_text, 'color'),
                'items': _parse_items_in_category(obj_text),
            })
        i = obj_end + 1
    return results


def _extract_bron_data_note(section: str) -> str:
    """
    Extract the Databenadering footnote text from the bronnen section.

    Args:
        section: Bronnen section JSX text

    Returns:
        Note text string
    """
    m = re.search(r'<strong>Databenadering:</strong>(.*?)</div>', section, re.DOTALL)
    if m:
        raw = m.group(1).strip()
        raw = re.sub(r'\s+', ' ', raw).strip()
        return raw
    return ""


def render_bronnen_section(jsx_content: str) -> str:
    """
    Extract the bronnen section from JSX and render as HTML.

    Args:
        jsx_content: Full JSX source string

    Returns:
        HTML string for the tab-bronnen panel content
    """
    start = jsx_content.find("{/* ── BRONNEN ── */}")
    # End at the FOOTER comment
    end = jsx_content.find("{/* FOOTER */}", start + 1)
    if start == -1:
        return "<!-- bronnen section not found -->"
    if end == -1:
        end = len(jsx_content)
    section = jsx_content[start:end]

    # --- Find the categories array ---
    cat_marker = section.find('"⚡ Elektriciteitsmarkt')
    if cat_marker == -1:
        return "<!-- bronnen categories not found -->"

    arr_start = section.rfind("[", 0, cat_marker)
    arr_end = _find_array_end(section, arr_start)
    if arr_end == -1:
        return "<!-- bronnen array end not found -->"

    cats_raw = section[arr_start:arr_end + 1]
    categories = _parse_source_categories(cats_raw)

    # --- Render categories ---
    cat_parts = []
    for cat in categories:
        color = cat['color']
        # Escape ampersands in category title
        cat_title = html_lib.escape(cat['cat'])
        items_html_parts = []
        for item in cat['items']:
            items_html_parts.append(
                f'        <div class="bron-item">\n'
                f'          <div>'
                f'<div class="bron-name">{html_lib.escape(item["n"])}</div>'
                f'<div class="bron-desc">{html_lib.escape(item["d"])}</div>'
                f'</div>\n'
                f'          <a href="{html_lib.escape(item["url"])}" target="_blank" '
                f'rel="noopener noreferrer" class="bron-link" '
                f'style="color:{color};background:{color}22;border:1px solid {color}44">'
                f'Bezoek &#x2197;</a>\n'
                f'        </div>'
            )
        items_joined = "\n".join(items_html_parts)
        cat_parts.append(
            f'      <div class="bron-cat">\n'
            f'        <h4 class="bron-cat-title" '
            f'style="color:{color};border-bottom:1px solid {color}33;padding-bottom:8px">'
            f'{cat_title}</h4>\n'
            f'{items_joined}\n'
            f'      </div>'
        )

    cats_joined = "\n\n".join(cat_parts)

    # --- Databenadering note ---
    bron_note = _extract_bron_data_note(section)

    return f"""    <div class="section">
      <h3 style="margin:0 0 6px;color:#f8fafc;font-size:16px">📚 Bronvermeldingen</h3>
      <p style="font-size:13px;color:#64748b;margin-top:0;margin-bottom:22px">
        Alle bronnen zijn publiek raadpleegbaar. Bevestigde exacte datapunten zijn gemarkeerd met &#x2713; in de tabellen.
      </p>

{cats_joined}

      <div class="bron-data-note">
        <strong>Databenadering:</strong>{bron_note}
      </div>
    </div>"""
