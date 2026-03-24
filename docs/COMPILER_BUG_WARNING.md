# ⚠️ COMPILER BUG WAARSCHUWING

**Status**: 🔴 KRITIEK - Gebruik compiler NIET  
**Datum**: 24 maart 2026  
**Impact**: Data verlies bij regeneratie offline.html

---

## 🚨 **Probleem**

De `jsx_to_html_compiler.py` heeft een **fundamentele bug** die kritieke data verwijdert bij het regenereren van `offline.html`:

### **Verloren data:**
1. ✅ **KPI notes** - Alle percentage verschillen worden leeg gelaten
   - Voorbeeld: `<div class="kpi-note"></div>` in plaats van `<div class="kpi-note">-11.7% vs gisteren</div>`
   
2. ✅ **Geopolitieke Crisissituatie sectie** - Volledig leeg gemaakt
   - Alle badges en content verwijderd
   - Sectie blijft over als lege `<div>`

3. ✅ **Europees Weekend-effect** - Niet aanwezig in output

### **Data die WEL behouden blijft:**
- ✅ Sleutelfactoren (6 stuks)
- ✅ KPI waarden (€53.54, €72.78, etc.)
- ✅ Prijstabel data
- ✅ Trendlines

---

## 🔧 **Directe Impact**

**Voor**: Compiler run
```html
<div class="kpi-note">-11.7% vs gisteren</div>
```

**Na**: Compiler run
```html
<div class="kpi-note"></div>
```

**Geopolitieke sectie voor**:
```html
<div class="section">
  <h3>⚔️ Geopolitieke Crisissituatie</h3>
  <div style="margin-bottom:14px">
    <span class="badge badge-red">Hormuz Crisis + LNG Disruption</span>
    <p>De Straat van Hormuz is sinds 2 maart...</p>
  </div>
  <!-- 4 meer badges met content -->
</div>
```

**Geopolitieke sectie na**:
```html
<div class="section">
  <h3>⚔️ Geopolitieke Crisissituatie</h3>
  
  
</div>
```

---

## ❌ **NIET DOEN**

```bash
# NIET UITVOEREN - Verwijdert data!
python scripts/compile_html.py
```

---

## ✅ **WEL DOEN**

### **Handmatige synchronisatie**
1. Edit JSX eerst
2. Kopieer wijzigingen handmatig naar offline.html
3. Run validator: `python scripts/validate_sync.py`
4. Fix eventuele verschillen
5. Commit beide bestanden

### **Validator gebruiken**
```bash
python scripts/validate_sync.py
```

De validator controleert nu ook:
- KPI notes aanwezigheid
- Sleutelfactoren count (6 verplicht)
- Trendlines data
- Reference lines in charts

---

## 🔍 **Root Cause**

De compiler gebruikt `JsxSectionExtractor` die:
1. **Niet alle JSX content correct parseert**
2. **Lege placeholders genereert** voor complexe secties
3. **Geen fallback heeft** voor ontbrekende data

Specifieke problemen:
- KPI notes worden niet geëxtraheerd uit JSX array
- Geopolitieke badges worden niet herkend
- Inline styles in JSX worden niet correct omgezet

---

## 🛠️ **Herstel Procedure**

Als je per ongeluk de compiler hebt gebruikt:

### **Stap 1: Identificeer verloren data**
```bash
# Check KPI notes
grep -n "kpi-note" public/offline.html

# Check geopolitieke sectie
grep -A 5 "Geopolitieke Crisissituatie" public/offline.html
```

### **Stap 2: Herstel vanuit JSX**
Kopieer de volgende secties handmatig van JSX naar HTML:

**KPI Notes** (regel ~230):
```html
<div class="kpi-note">-11.7% vs gisteren</div>
<div class="kpi-note">-30.0% vs gisteren</div>
<div class="kpi-note">kritiek laag niveau</div>
<div class="kpi-note">+1.5% vs gisteren</div>
```

**Geopolitieke sectie** (regel ~564):
- Hormuz Crisis + LNG Disruption badge
- EU Gasopslag Niveau badge
- EU Gasopslag Kritiek badge
- Europees Weekend-effect badge
- Brent Olieprijzen badge

### **Stap 3: Valideer**
```bash
python scripts/validate_sync.py
```

---

## 📋 **Workflow Update**

De `/valideer-en-push` workflow is bijgewerkt met:

```markdown
**⚠️ WAARSCHUWING: Gebruik NIET `compile_html.py`**
De compiler heeft een bug en verwijdert kritieke data (KPI notes, geopolitieke sectie).
Synchroniseer handmatig tussen JSX en HTML tot de compiler is gefixed.
```

---

## 🔮 **Toekomstige Fix**

Om de compiler te fixen, moet `JsxSectionExtractor` worden uitgebreid om:

1. **KPI notes te extraheren** uit JSX array definitie
2. **Geopolitieke badges te parsen** inclusief inline styles
3. **Fallback mechanisme** toe te voegen voor complexe secties
4. **Test suite** te schrijven die data verlies detecteert

**Tot die tijd: GEBRUIK DE COMPILER NIET.**

---

## 📚 **Gerelateerde Documenten**

- `scripts/jsx_to_html_compiler.py` - Compiler met bug
- `scripts/sync_validator.py` - Validator (nu met extra checks)
- `.windsurf/workflows/valideer-en-push.md` - Bijgewerkte workflow
- `docs/SYNC_ISSUES_RESOLVED.md` - Eerdere sync problemen

---

**Conclusie**: De compiler is **niet betrouwbaar** en moet worden vermeden tot de bug is gefixed. Gebruik handmatige synchronisatie en de validator om data integriteit te waarborgen.
