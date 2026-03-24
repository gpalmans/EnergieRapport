---
description: Voer de volledige kwaliteitschecklist uit, update UPDATE_LOG.md en push naar GitHub. Voer dit als laatste stap uit na collect-energie-data en update-energie-rapport.
---

## ⛔ BLOKKERENDE CHECKLIST — commit alleen als alles ✓ is

**Data volledigheid:**

- [ ] TTF, Belpex, EU Gasopslag, Brent alle 4 ✓ via 2+ bronnen
- [ ] Minimaal 3 datapunten in rawData met ✓
- [ ] TTF + Belpex data loopt t/m de rapportdatum

**Consistentie JSX ↔ PDF-output:**

- [ ] KPI-waarden en KPI-percentages in PDF komen exact overeen met JSX
- [ ] Belpex in PDF-tabellen behoudt decimalen en wordt niet afgerond tot hele getallen
- [ ] Forecast ranges, kansen en terminologie zijn identiek in JSX en PDF
- [ ] Geopolitieke tekstblokken en sleutelfactoren zijn inhoudelijk identiek in JSX en PDF
- [ ] **Precies 1x 'Vandaag' label** in de JSX-data en correcte mapping naar de PDF
- [ ] Forecast grafiek Y-as past bij bullish max + ≥5% marge

**Inhoudelijke kwaliteit:**

- [ ] Geopolitieke crisissituatie: elk item 2-3 zinnen (oorzaak / effect / evolutie)
- [ ] Belgische Energiemix: merit-order gas-elektriciteit koppeling uitgelegd
- [ ] Sleutelfactoren: gesorteerd van meest naar minst impact
- [ ] Sleutelfactoren: uniforme layout per factor (`impact` / `waarom` / `monitor`)
- [ ] Sleutelfactoren: expliciete min-max impactranges voor TTF en Belpex waar relevant
- [ ] Vaste vs. Variabel: enkel 12-18 mnd horizon, concrete TTF-drempels vermeld
- [ ] Adviesmatrix: elke rij actueel, `[bijgewerkt DD/MM]` toegevoegd indien gewijzigd
- [ ] Kernboodschap: visueel prominent, actuele TTF, korte én lange termijn verwachting
- [ ] Praktisch advies: concrete drempels, max 18 mnd termijn, anti-paniek afsluiting
- [ ] Forecastverdeling voelt realistisch: basis standaard dominant, bullish alleen verhoogd bij concrete escalatietrigger

**Data cross-check (consistent overal):**

- [ ] TTF consistent in KPI, rawData en geopolitieke tekst
- [ ] Belpex consistent in KPI, rawData en bronnen
- [ ] Brent consistent in KPI en geopolitieke sectie
- [ ] EU gasopslag consistent in KPI en contextsectie

**PDF-implementatie:**

- [ ] `src/hooks/usePDFDownload.js` gebruikt actuele waarden voor TTF, Belpex, Brent en forecastdata
- [ ] `src/utils/pdfGenerator.js` formatteert TTF/Belpex/Brent correct en zonder onbedoelde afronding

**Technisch:**

- [ ] Alle bron-URLs geldig, ~70% NL / ~30% EN, max 4 weken oud

---

## Stap 2 — Kwaliteitscontrole (Review)

---

## Stap 3 — UPDATE_LOG.md bijwerken

1. Voeg nieuwe entry toe aan het **begin** van `UPDATE_LOG.md`:

```markdown
## Update [N] — [DD maand YYYY]

### **Bevestigde Marktdata (✓)**
- **TTF Gas**: €XX.XX/MWh (+/-X.X%) - [bron]
- **Belpex**: €XXX.X/MWh (+/-X.X%) - [bron]
- **EU Gasopslag**: ~XX% - [bron]
- **Brent**: $XXX.XX/vat (+/-X.X%) - [bron]

### **Marktontwikkelingen & Geopolitiek**
- [2-3 bullets met datum + bron]

### **Forecast**: Bearish X% / Basis X% / Bullish X% — [toelichting]

### **Wijzigingen**: [wat is aangepast in JSX/PDF-logica]
```

---

## Stap 4 — Commit en push

// turbo
1. Voer uit vanuit de projectmap:

```bash
git add src/EnergieRapport.jsx UPDATE_LOG.md
git commit -m "update [DD-MM-YYYY]: TTF €XX.XX, Belpex €XXX.X — [één zin context]"
git push origin main
```

2. Cloudflare Pages bouwt automatisch na de push (~1-2 minuten).

---

## Optioneel — Lessons Learned

1. Nieuwe inzichten? Voeg toe aan `CLAUDE.md` onder `## Lessons Learned ([datum])`.
2. Verouderde start-instructie in CLAUDE.md? Pas aan en commit apart.
