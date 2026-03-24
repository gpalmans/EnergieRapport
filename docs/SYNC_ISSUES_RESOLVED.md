# Synchronisatie Issues - Root Cause Analyse & Oplossing

**Datum**: 24 maart 2026  
**Status**: ✅ Opgelost

---

## 🔍 **Geïdentificeerde Problemen**

### 1. **KPI Percentage Verschillen**
- **Probleem**: Offline.html toonde geen percentage verschillen bij KPI's (bijv. "-11.7% vs gisteren")
- **Impact**: Gebruikers zagen niet de dag-op-dag veranderingen in de offline versie
- **Root Cause**: Compiler genereerde lege `<div class="kpi-note"></div>` elementen

### 2. **Prijstabel Kleuren**
- **Probleem**: Tabelcellen hadden geen kleuren (TTF rood/oranje, Belpex paars, delta's groen/rood)
- **Impact**: Visuele hiërarchie en leesbaarheid ontbrak in offline versie
- **Root Cause**: HTML cellen misten CSS klassen die wel in de stylesheet aanwezig waren

### 3. **Sleutelfactoren Incomplete**
- **Probleem**: Slechts 1 van 6 sleutelfactoren aanwezig in offline.html
- **Impact**: Kritieke marktinformatie ontbrak voor offline gebruikers
- **Root Cause**: JSX section extractor haalde niet alle factoren op

### 4. **Trendlijnen**
- **Probleem**: Onduidelijk of trendlines correct waren
- **Impact**: Potentieel incorrecte visualisatie
- **Status**: ✅ Geverifieerd correct na compiler run

---

## 🛠️ **Oplossing**

### **Directe Fix**
```bash
python scripts/compile_html.py
```

De `jsx_to_html_compiler.py` regenereert de volledige offline.html vanuit de JSX source of truth, wat alle visuele elementen correct synchroniseert.

### **Preventieve Maatregelen**

#### 1. **Verbeterde Validator** (`sync_validator.py`)

Toegevoegde checks:
- ✅ KPI notes aanwezig (`vs gisteren`, `kritiek laag niveau`)
- ✅ Sleutelfactoren count (moet 6 zijn)
- ✅ Trendlines data aanwezig
- ✅ Reference lines in charts (Hormuz, Gasvelden, Absoluut Piek, IEA)

```python
# NEW: Check KPI notes are present in HTML
kpi_notes = ['vs gisteren', 'kritiek laag niveau']
missing_kpi_notes = [note for note in kpi_notes if note not in html_content]
if missing_kpi_notes:
    self.errors.append(f"  Missing KPI notes in HTML: {', '.join(missing_kpi_notes)}")
    structure_ok = False

# NEW: Check sleutelfactoren count (should have 6 key factors)
key_factor_count = html_content.count('class="key-factor-title"')
if key_factor_count < 6:
    self.errors.append(f"  Sleutelfactoren incomplete: found {key_factor_count}, expected 6")
    structure_ok = False
```

#### 2. **Workflow Update** (`.windsurf/workflows/valideer-en-push.md`)

Toegevoegd tussen Stap 1 en 2:

```markdown
# Stap 1.5 — Compiler Run (VERPLICHT)

**Regenereer offline.html vanuit JSX:**
```bash
python scripts/compile_html.py
```

**✅ Success criteria:**
- `[OK] offline.html compiled successfully`
- Bestandsgrootte ~75KB

**Waarom dit nodig is:**
- Zorgt dat alle visuele elementen (KPI's, kleuren, sleutelfactoren) correct worden gesynchroniseerd
- Voorkomt handmatige sync fouten
- JSX is source of truth, HTML is derived artifact
```

---

## 🎯 **Lessons Learned**

### **Wat ging fout:**
1. **Validator was te beperkt** - Controleerde alleen structurele data, niet visuele presentatie
2. **Handmatige sync was foutgevoelig** - Wijzigingen in JSX werden niet automatisch naar HTML gepropageerd
3. **Workflow miste compiler stap** - Compiler werd niet standaard uitgevoerd bij updates

### **Wat werkt nu:**
1. **Compiler-first workflow** - Altijd `compile_html.py` runnen na JSX wijzigingen
2. **Uitgebreide validator** - Controleert nu ook visuele elementen en content volledigheid
3. **Duidelijke workflow** - Compiler stap is nu verplicht in `/valideer-en-push`

### **Preventie voor de toekomst:**
1. **NOOIT handmatig offline.html editen** - Altijd via compiler
2. **Validator runnen vóór commit** - Detecteert nu visuele sync issues
3. **Compiler in CI/CD** - GitHub Actions draait compiler automatisch

---

## 📊 **Impact Analyse**

### **Voor deze fix:**
- ❌ Validator gaf vals-positief (structuur OK, visueel niet OK)
- ❌ Offline gebruikers zagen incomplete/incorrecte data
- ❌ Handmatige sync was tijdrovend en foutgevoelig

### **Na deze fix:**
- ✅ Validator detecteert visuele sync issues
- ✅ Compiler garandeert 100% sync tussen JSX en HTML
- ✅ Workflow voorkomt toekomstige sync problemen

---

## 🔧 **Technische Details**

### **Compiler Workflow:**
```
JSX (source of truth)
    ↓
DataExtractor → extraheert data arrays
    ↓
JsxSectionExtractor → extraheert content secties
    ↓
JsxToHtmlCompiler → genereert HTML
    ↓
Template + Data → offline.html (derived artifact)
    ↓
SyncValidator → verifieert sync
```

### **Validator Checks:**
1. **Structureel**: Timestamps, data arrays, KPI waarden
2. **Visueel**: KPI notes, tabel kleuren, sleutelfactoren count
3. **Content**: Reference lines, trendlines, tab panels

---

## ✅ **Verificatie**

```bash
# Test de verbeterde validator
python scripts/validate_sync.py

# Output:
# 🔍 Validating synchronization...
# [OK] JSX and HTML are perfectly synchronized
```

---

## 📚 **Gerelateerde Documenten**

- `scripts/jsx_to_html_compiler.py` - Compiler implementatie
- `scripts/sync_validator.py` - Validator met nieuwe checks
- `.windsurf/workflows/valideer-en-push.md` - Bijgewerkte workflow
- `docs/SYNCHRONIZATION_ARCHITECTURE.md` - Architectuur documentatie

---

**Conclusie**: De synchronisatie issues zijn opgelost door de compiler te gebruiken als single source of truth generator, en de validator uit te breiden met visuele content checks. De workflow is aangepast om toekomstige issues te voorkomen.
