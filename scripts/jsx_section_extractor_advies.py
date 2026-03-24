"""
JSX Section Extractor — Advies Tab
Extracts the Advies tab content from JSX and renders it as HTML.

The advies section has both dynamic arrays (LNG arg cards, decision matrix)
and large static prose blocks (panic warning, Belgian law, KERNBOODSCHAP).
Static prose is extracted verbatim from JSX via regex and rendered as-is.
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


def _parse_lng_arg_objects(array_text: str) -> list[dict]:
    """
    Parse LNG argument card objects from the array literal.

    Args:
        array_text: Array literal text

    Returns:
        List of dicts with keys: icon, title, body, color
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
        icon = _extract_string_prop(obj_text, 'icon')
        if icon:
            results.append({
                'icon': icon,
                'title': _extract_string_prop(obj_text, 'title'),
                'body': _extract_string_prop(obj_text, 'body'),
                'color': _extract_string_prop(obj_text, 'color'),
            })
        i = obj_end + 1
    return results


def _parse_matrix_rows(array_text: str) -> list[tuple]:
    """
    Parse decision matrix row tuples from array literal.

    Args:
        array_text: Array literal text

    Returns:
        List of (profile, recommendation, motivation, precaution) tuples
    """
    pattern = (
        r'\[\s*"((?:[^"\\]|\\.)*)"\s*,'
        r'\s*"((?:[^"\\]|\\.)*)"\s*,'
        r'\s*"((?:[^"\\]|\\.)*)"\s*,'
        r'\s*"((?:[^"\\]|\\.)*)"\s*\]'
    )
    results = []
    for m in re.finditer(pattern, array_text):
        results.append((
            m.group(1).replace('\\"', '"').replace("\\'", "'"),
            m.group(2).replace('\\"', '"').replace("\\'", "'"),
            m.group(3).replace('\\"', '"').replace("\\'", "'"),
            m.group(4).replace('\\"', '"').replace("\\'", "'"),
        ))
    return results


def _extract_prose_block(section: str, start_comment: str) -> str:
    """
    Extract a prose block of JSX after a comment marker, stripping JSX style props.
    Used for panic warning, Belgian law, KERNBOODSCHAP blocks.

    This returns the raw JSX-derived text content of paragraphs within a named block.

    Args:
        section: The advies section JSX text
        start_comment: Comment string like 'PANIC WARNING'

    Returns:
        Dict with extracted text fields keyed by location
    """
    idx = section.find(start_comment)
    if idx == -1:
        return {}
    return idx


def _jsx_to_html_text(raw: str) -> str:
    """
    Convert JSX text content to HTML, handling style props and escaping.

    Args:
        raw: Raw JSX text

    Returns:
        HTML-ready text
    """
    # Convert JSX strong style={{ color: "#xxx" }} to HTML strong style="color:#xxx"
    raw = re.sub(
        r'<strong\s+style=\{\{\s*color:\s*"(#[a-fA-F0-9]+)"\s*\}\}>',
        r'<strong style="color:\1">',
        raw
    )
    # Remove remaining JSX style expression blocks
    raw = re.sub(r'\s*style=\{\{[^}]*\}\}', '', raw)
    # Normalize whitespace
    raw = re.sub(r'\s+', ' ', raw).strip()
    return raw


def _extract_panic_texts(section: str) -> dict:
    """
    Extract text content from the panic warning block.

    Args:
        section: Advies section JSX

    Returns:
        Dict with 'title', 'para', 'box'
    """
    m_title = re.search(r'Opgelet: Beslissen[^"<\n]+', section)
    m_para = re.search(
        r'De energiemarkten bevinden zich(.*?)</p>',
        section, re.DOTALL
    )
    m_box = re.search(
        r'<strong>Wat u moet weten:</strong>(.*?)</div>',
        section, re.DOTALL
    )
    return {
        'title': m_title.group(0).strip() if m_title else "",
        'para': _jsx_to_html_text(
            "De energiemarkten bevinden zich" + m_para.group(1)
            if m_para else ""
        ),
        'box': _jsx_to_html_text(m_box.group(1).strip() if m_box else ""),
    }


def _extract_variabel_intro_para(section: str) -> str:
    """
    Extract the intro paragraph of the variabel argument section.

    Args:
        section: Advies section JSX

    Returns:
        HTML paragraph text
    """
    m = re.search(
        r'structurele marktfundamentelen voor de komende(.*?)</p>',
        section, re.DOTALL
    )
    if not m:
        return ""
    raw = "structurele marktfundamentelen voor de komende" + m.group(1)
    return _jsx_to_html_text(raw)


def _extract_hist_precedent_text(section: str) -> str:
    """
    Extract the historical precedent paragraph.

    Args:
        section: Advies section JSX

    Returns:
        HTML paragraph text
    """
    m = re.search(
        r'Wie in september.*?</p>',
        section, re.DOTALL
    )
    if not m:
        return ""
    return _jsx_to_html_text(m.group(0).replace('</p>', '').strip())


def _extract_law_texts(section: str) -> dict:
    """
    Extract text from the Belgian legal right block.

    Args:
        section: Advies section JSX

    Returns:
        Dict with 'title', 'para', 'box'
    """
    m_title = re.search(r'Belgische wet: consumentenbescherming[^"<\n]+', section)
    m_para = re.search(
        r'Sinds 2012 geldt(.*?)</p>',
        section, re.DOTALL
    )
    m_box = re.search(
        r'<strong>⚠️ Financiële valkuil(.*?)</div>',
        section, re.DOTALL
    )
    return {
        'title': m_title.group(0).strip() if m_title else "Belgische wet: consumentenbescherming als vangnet — voor particulier én KMO",
        'para': _jsx_to_html_text("Sinds 2012 geldt" + m_para.group(1) if m_para else ""),
        'box': _jsx_to_html_text(m_box.group(1).strip() if m_box else ""),
    }


def _extract_nuance_text(section: str) -> str:
    """
    Extract the systemic nuance text.

    Args:
        section: Advies section JSX

    Returns:
        Text string
    """
    m = re.search(
        r'Waarom de 12-maanden horizon(.*?)</div>',
        section, re.DOTALL
    )
    if not m:
        return ""
    return _jsx_to_html_text("Waarom de 12-maanden horizon" + m.group(1))


def _extract_kernboodschap_texts(section: str) -> dict:
    """
    Extract text blocks from the KERNBOODSCHAP section.

    Args:
        section: Advies section JSX

    Returns:
        Dict with 'para1', 'short_term', 'medium_term', 'para3', 'obs', 'criteria', 'checklist', 'never'
    """
    m_p1 = re.search(r'De huidige marktbeweging is extreem(.*?)</p>', section, re.DOTALL)
    m_short = re.search(r'<strong[^>]*>Korte termijn.*?</strong>(.*?)</p>', section, re.DOTALL)
    m_medium = re.search(r'<strong[^>]*>Middellange termijn.*?</strong>(.*?)</p>', section, re.DOTALL)
    m_p3 = re.search(r'De Belgische wet biedt consumenten(.*?)</p>', section, re.DOTALL)
    m_obs = re.search(r'<strong[^>]*>1\. Observatieperiode.*?</strong>(.*?)</div>', section, re.DOTALL)
    m_crit = re.search(r'<strong[^>]*>2\. Beslissingscriteria.*?</strong>(.*?)</div>', section, re.DOTALL)
    m_check = re.search(r'<strong[^>]*>3\. Contractvoorwaarden.*?</strong>(.*?)</div>', section, re.DOTALL)
    m_never = re.search(r'<strong[^>]*>⚠️ NOOIT OVERHAAST.*?</strong>(.*?)</div>', section, re.DOTALL)

    def clean(m, prefix=""):
        if not m:
            return ""
        return _jsx_to_html_text(prefix + m.group(1))

    return {
        'para1': _jsx_to_html_text(
            "De huidige marktbeweging is extreem" + m_p1.group(1) if m_p1 else ""
        ),
        'short_term': clean(m_short),
        'medium_term': clean(m_medium),
        'para3': _jsx_to_html_text(
            "De Belgische wet biedt consumenten" + m_p3.group(1) if m_p3 else ""
        ),
        'obs': clean(m_obs),
        'criteria': clean(m_crit),
        'checklist': clean(m_check),
        'never': clean(m_never),
    }


def render_advies_section(jsx_content: str) -> str:
    """
    Extract the advies section from JSX and render as HTML.

    Args:
        jsx_content: Full JSX source string

    Returns:
        HTML string for the tab-advies panel content
    """
    start = jsx_content.find("{/* ── ADVIES ── */}")
    end = jsx_content.find("{/* ── BRONNEN ── */}", start + 1)
    if start == -1 or end == -1:
        return "<!-- advies section not found -->"
    section = jsx_content[start:end]

    # --- Extract panic texts ---
    panic = _extract_panic_texts(section)

    # --- Extract variabel intro paragraph ---
    var_intro = _extract_variabel_intro_para(section)

    # --- Extract LNG argument cards ---
    lng_marker = section.find('"🌊"')
    if lng_marker == -1:
        lng_cards_html = ""
    else:
        arr_start = section.rfind("[", 0, lng_marker)
        arr_end = _find_array_end(section, arr_start)
        lng_raw = section[arr_start:arr_end + 1]
        lng_cards = _parse_lng_arg_objects(lng_raw)
        card_parts = []
        for c in lng_cards:
            card_parts.append(
                f'        <div class="arg-card" style="border:1px solid {c["color"]}33">\n'
                f'          <div class="arg-icon">{c["icon"]}</div>\n'
                f'          <div class="arg-title" style="color:{c["color"]}">'
                f'{html_lib.escape(c["title"])}</div>\n'
                f'          <div class="arg-body">{html_lib.escape(c["body"])}</div>\n'
                f'        </div>'
            )
        lng_cards_html = "\n".join(card_parts)

    # --- Historical precedent ---
    hist_text = _extract_hist_precedent_text(section)

    # --- Belgian law texts ---
    law = _extract_law_texts(section)

    # --- Nuance text ---
    nuance_text = _extract_nuance_text(section)

    # --- Decision matrix rows ---
    matrix_marker = section.find('"Gezin, krappe begroting"')
    matrix_rows_html = ""
    if matrix_marker != -1:
        arr_start = section.rfind("[", 0, matrix_marker)
        arr_end = _find_array_end(section, arr_start)
        matrix_raw = section[arr_start:arr_end + 1]
        matrix_rows = _parse_matrix_rows(matrix_raw)
        row_parts = []
        for p, a, m, v in matrix_rows:
            row_parts.append(
                f'            <tr style="border-bottom:1px solid #1e293b">\n'
                f'              <td style="padding:9px 11px;color:#e2e8f0;font-weight:600">{html_lib.escape(p)}</td>\n'
                f'              <td style="padding:9px 11px;color:#60a5fa">{html_lib.escape(a)}</td>\n'
                f'              <td style="padding:9px 11px;color:#94a3b8">{html_lib.escape(m)}</td>\n'
                f'              <td style="padding:9px 11px;color:#64748b;font-size:11px">{html_lib.escape(v)}</td>\n'
                f'            </tr>'
            )
        matrix_rows_html = "\n".join(row_parts)

    # --- KERNBOODSCHAP texts ---
    kern = _extract_kernboodschap_texts(section)

    return f"""
    <!-- PANIC WARNING -->
    <div class="section-panic">
      <div style="display:flex;align-items:flex-start;gap:14px">
        <span style="font-size:26px;flex-shrink:0">🚨</span>
        <div>
          <h3 style="color:#fb923c;margin:0 0 10px;font-size:16px">{html_lib.escape(panic['title'])}</h3>
          <p style="font-size:14px;color:#fed7aa;line-height:1.8;margin:0 0 10px">
            {panic['para']}
          </p>
          <div style="background:#431407;border-radius:8px;padding:12px 16px;font-size:13px;color:#fdba74;line-height:1.7">
            <strong>Wat u moet weten:</strong>{panic['box']}
          </div>
        </div>
      </div>
    </div>

    <!-- MEDIUM-TERM VARIABEL ARGUMENT -->
    <div class="section-blue">
      <h3 style="margin:0 0 14px;color:#38bdf8;font-size:16px">📉 Waarom variabel op de (middel)lange termijn waarschijnlijk goedkoper uitvalt</h3>
      <p style="font-size:14px;color:#94a3b8;line-height:1.8;margin-bottom:16px">
        De huidige prijspiek is reëel, maar de {var_intro}
      </p>
      <div class="two-col-args">
{lng_cards_html}
      </div>
      <div class="card-green-inner">
        <div style="display:flex;gap:10px;align-items:flex-start">
          <span style="font-size:18px;flex-shrink:0">📊</span>
          <div>
            <div style="color:#4ade80;font-weight:700;font-size:14px;margin-bottom:6px">Historisch precedent: 2022 crisis vs. daarna</div>
            <p style="font-size:13px;color:#86efac;line-height:1.7;margin:0">
              {hist_text}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- BELGIAN LEGAL RIGHT -->
    <div class="section-law">
      <div style="display:flex;align-items:flex-start;gap:14px">
        <span style="font-size:24px;flex-shrink:0">⚖️</span>
        <div>
          <h3 style="color:#4ade80;margin:0 0 10px;font-size:16px">{html_lib.escape(law['title'])}</h3>
          <p style="font-size:14px;color:#86efac;line-height:1.8;margin:0 0 12px">
            Sinds 2012 geldt in België een {law['para']}
          </p>
          <div style="background:#451a03;border:1px solid #f9731666;border-radius:8px;padding:12px 16px;font-size:13px;color:#fed7aa;line-height:1.7">
            <strong>⚠️ Financiële valkuil bij vroegtijdig vertrek:</strong>{law['box']}
          </div>
        </div>
      </div>
    </div>

    <!-- SYSTEMIC NUANCE -->
    <div class="section-nuance">
      <strong style="color:#a5b4fc">📌 Waarom de 12-maanden horizon verstandig is — ook voor u:</strong> {nuance_text}
    </div>

    <!-- WHEN FIXED IS JUSTIFIED -->
    <div class="section">
      <h3 style="margin:0 0 14px;color:#f8fafc;font-size:16px">🏠 Wanneer is een vast tarief dan wél verantwoord?</h3>
      <div class="section-warning">
        <strong>Eerlijke boodschap:</strong> Vast of variabel — beide zijn correcte keuzes, mits gemaakt op rationele gronden en niet gedreven door marktpaniek. De vuistregel: kies een formule die u met overtuiging voor <strong>minimaal 12 maanden</strong> kunt aanhouden. Snel schakelen tussen contractvormen kost u geld (verloren premies, administratieve lasten) en levert zelden het verwachte voordeel op.
      </div>
      <div class="two-col">
        <div class="vast-card">
          <h4 style="color:#22c55e;margin:0 0 10px;font-size:14px">✅ Vast tarief overwegen als…</h4>
          <ul style="margin:0;padding:0 0 0 16px;font-size:13px;color:#94a3b8;line-height:2">
            <li>Uw budget <strong style="color:#f8fafc">geen schommelingen verdraagt</strong> (sociale situatie, schulden)</li>
            <li>U <strong style="color:#f8fafc">extreem hoog verbruik</strong> heeft (warmtepomp, elektrische wagen, grote woning)</li>
            <li>U als KMO <strong style="color:#f8fafc">vaste kostenstructuur</strong> nodig heeft voor offertes/klanten</li>
            <li>U de rust en stabiliteit van een <strong style="color:#f8fafc">bekende maandkost</strong> verkiest boven marktvolatiliteit</li>
          </ul>
        </div>
        <div class="var-card">
          <h4 style="color:#ef4444;margin:0 0 10px;font-size:14px">❌ Vast tarief vermijden als…</h4>
          <ul style="margin:0;padding:0 0 0 16px;font-size:13px;color:#94a3b8;line-height:2">
            <li>U <strong style="color:#f8fafc">zonnepanelen of een batterij</strong> heeft (variabel maximaliseert uw voordeel)</li>
            <li>U de beslissing neemt <strong style="color:#f8fafc">puur door de nieuwscyclus</strong>, niet door uw verbruiksprofiel</li>
            <li>De aangeboden prijs <strong style="color:#f8fafc">méér dan 15% boven</strong> het pre-crisis niveau ligt</li>
            <li>U de <strong style="color:#f8fafc">bijzondere voorwaarden</strong> (premies, loyaliteitsvoordelen) niet gelezen heeft</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- DECISION MATRIX -->
    <div class="section">
      <h3 style="margin:0 0 12px;color:#f8fafc;font-size:15px">📋 Adviesmatrix per Profiel</h3>
      <div style="overflow-x:auto">
        <table style="width:100%;border-collapse:collapse;font-size:12.5px">
          <thead>
            <tr class="matrix-header">
              <th style="padding:9px 11px;text-align:left;color:#64748b;font-size:11px;border-bottom:2px solid #334155">Profiel</th>
              <th style="padding:9px 11px;text-align:left;color:#64748b;font-size:11px;border-bottom:2px solid #334155">Aanbeveling</th>
              <th style="padding:9px 11px;text-align:left;color:#64748b;font-size:11px;border-bottom:2px solid #334155">Motivering</th>
              <th style="padding:9px 11px;text-align:left;color:#64748b;font-size:11px;border-bottom:2px solid #334155">Voorzorgsmaatregel</th>
            </tr>
          </thead>
          <tbody>
{matrix_rows_html}
          </tbody>
        </table>
      </div>
    </div>

    <!-- KERNBOODSCHAP -->
    <div class="section-kernboodschap">
      <h2 style="margin:0 0 16px;color:#60a5fa;font-size:18px;font-weight:700">🎯 KERNBOODSCHAP: Weloverwogen keuzen duren langer dan een nieuwscyclus</h2>
      <p style="font-size:15px;line-height:1.85;color:#bfdbfe;margin:0 0 14px;font-weight:500">
        {kern['para1']}
      </p>
      <div style="background:#0f172a;border-radius:10px;padding:16px 20px;margin-bottom:14px;border:1px solid #1e3a8a">
        <p style="font-size:14px;line-height:1.85;color:#bfdbfe;margin:0 0 12px">
          <strong style="color:#60a5fa">Korte termijn (2-5 maanden):</strong>{kern['short_term']}
        </p>
        <p style="font-size:14px;line-height:1.85;color:#bfdbfe;margin:0">
          <strong style="color:#60a5fa">Middellange termijn (6-18 maanden):</strong>{kern['medium_term']}
        </p>
      </div>
      <p style="font-size:15px;line-height:1.85;color:#bfdbfe;margin:0 0 16px;font-weight:500">
        {kern['para3']}
      </p>
      <div class="card-practical">
        <h4 style="margin:0 0 12px;color:#38bdf8;font-size:15px;font-weight:700">📋 PRAKTISCH ADVIES — Concrete Stappen</h4>
        <div style="margin-bottom:12px">
          <strong style="color:#7dd3fc">1. Observatieperiode (4-6 weken):</strong>{kern['obs']}
        </div>
        <div style="margin-bottom:12px">
          <strong style="color:#7dd3fc">2. Beslissingscriteria TTF:</strong>{kern['criteria']}
        </div>
        <div style="margin-bottom:12px">
          <strong style="color:#7dd3fc">3. Contractvoorwaarden checklist:</strong>{kern['checklist']}
        </div>
        <div class="card-never">
          <strong style="color:#fdba74">⚠️ NOOIT OVERHAAST TEKENEN:</strong>{kern['never']}
        </div>
      </div>
    </div>"""
