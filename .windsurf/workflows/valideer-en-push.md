---
description: Voer de volledige kwaliteitschecklist uit voor het volledig automatische EnergieRapport. Alle data wordt live gesynchroniseerd met KPI's. Update UPDATE_LOG.md en push naar GitHub. Voer dit als laatste stap uit na collect-energie-data en update-energie-rapport.
---

## ⛔ BLOKKERENDE CHECKLIST — commit alleen als alles ✓ is

**🔥 Nieuwe Automatische Features (vandaag geïmplementeerd):**

✅ **KPI Kleurlogica Automatisch**: Positief → Rood, Negatief → Groen  
✅ **Geopolitieke Content Live Sync**: Brent/TTF prijzen automatisch bijgewerkt  
✅ **IEA Strategische Reserves Dynamisch**: Analyse gebaseerd op actuele Brent  
✅ **Belgische Energiemix Compleet**: 95-105% totaal + actuele Belpex data  
✅ **Timezone Correctie**: CET-tijdweergave in hele rapport  
✅ **Storage Calculation Correct**: "Nog te vullen" = 90% - huidig niveau  

---

**Data volledigheid:**

- [ ] TTF, Belpex, België gasopslag, Brent alle 4 ✓ via 2+ bronnen
- [ ] Minimaal 3 datapunten in rawData met ✓
- [ ] TTF + Belpex data loopt t/m de rapportdatum
- [ ] **KPI kleurlogica correct**: Rood voor stijging, Groen voor daling
- [ ] **Geopolitieke content gesynchroniseerd** met actuele KPI's
- [ ] **IEA analyse dynamisch** gebaseerd op huidige Brent prijs
- [ ] **Energiemix percentages compleet** (95-105% totaal)

**Consistentie JSX ↔ PDF-output:**

- [ ] KPI-waarden en **automatische kleurlogica** in PDF komen exact overeen met JSX
- [ ] **Geopolitieke live content** identiek in JSX en PDF
- [ ] **IEA dynamische analyse** identiek in JSX en PDF
- [ ] **Energiemix volledige percentages** identiek in JSX en PDF
- [ ] Belpex in PDF-tabellen behoudt decimalen en wordt niet afgerond tot hele getallen
- [ ] Forecast ranges, kansen en terminologie zijn identiek in JSX en PDF
- [ ] **Precies 1x 'Vandaag' label** in de JSX-data en correcte mapping naar de PDF
- [ ] Forecast grafiek Y-as past bij bullish max + ≥5% marge

**Inhoudelijke kwaliteit:**

- [ ] Geopolitieke crisissituatie: elk item 2-3 zinnen (oorzaak / effect / evolutie)
- [ ] **Geopolitieke content reflecteert actuele Brent/TTF KPI's**
- [ ] **IEA Strategische Reserves**: analyse gebaseerd op huidige Brent prijsniveau
- [ ] Belgische Energiemix: merit-order gas-elektriciteit koppeling uitgelegd
- [ ] **Energiemix percentages compleet**: Kern (35-40%) + Hernieuwbaar (30%) + Gas (20%) + Import/Overig (10-15%)
- [ ] **Belpex notificatie up-to-date** met huidige datum en percentage
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
- [ ] België gasopslag consistent in KPI en contextsectie
- [ ] **KPI kleuren correct**: Positief = #ef4444, Negatief = #22c55e

**Automatische Synchronisatie Validatie:**

- [ ] **Geopolitieke content**: Brent $104.49/vat, TTF €53.82/MWh, percentages correct
- [ ] **IEA analyse**: Effectiviteit gebaseerd op huidige Brent prijs ($104.49)
- [ ] **Energiemix**: Import/Overig 10-15% toegevoegd, totaal 95-105%
- [ ] **Belpex notificatie**: 25/03, -1.0% vs gisteren (niet -42.0%)
- [ ] **Storage calculation**: 67% "nog te vullen" (90% - 23% huidig)
- [ ] **Timezone**: Alle datums in CET, geen UTC mismatch

**PDF-implementatie:**

- [ ] `src/hooks/usePDFDownload.js` gebruikt actuele waarden voor TTF, Belpex, Brent en forecastdata
- [ ] `src/utils/pdfGenerator.js` formatteert TTF/Belpex/Brent correct en zonder onbedoelde afronding

**Technisch:**

- [ ] Alle bron-URLs geldig, ~70% NL / ~30% EN, max 4 weken oud

---

## Stap 2 — Kwaliteitscontrole (Review)

**Focus op nieuwe automatische features:**

1. **KPI kleurlogica**: Controleer of rood/groen correct is voor alle KPI's
2. **Geopolitieke synchronisatie**: Brent/TTF prijzen up-to-date in tekst
3. **IEA dynamische analyse**: Effectiviteit correct voor huidige Brent niveau
4. **Energiemix volledigheid**: Alle 4 componenten aanwezig (95-105% totaal)
5. **Belpex notificatie**: Huidige datum en correct percentage

---

## Stap 3 — UPDATE_LOG.md bijwerken

1. Voeg nieuwe entry toe aan het **begin** van `UPDATE_LOG.md`:

```markdown
## Update [N] — [DD maand YYYY]

### **🔥 Nieuwe Automatische Features Geïmplementeerd**
- **KPI Kleurlogica**: Automatisch rood/groen gebaseerd op richting (+/-)
- **Geopolitieke Content Sync**: Live Brent/TTF synchronisatie met KPI's
- **IEA Strategische Reserves**: Dynamische analyse gebaseerd op Brent prijs
- **Belgische Energiemix**: Compleet 95-105% + actuele Belpex data
- **Timezone Correctie**: CET-tijdweergave in hele rapport
- **Storage Calculation**: Correct "nog te vullen" percentage

### **Bevestigde Marktdata (✓)**
- **TTF Gas**: €53.82/MWh (+1.1%) - [bron]
- **Belpex**: €72.04/MWh (-1.0%) - [bron]
- **België gasopslag**: ~23% - [bron]
- **Brent**: $104.49/vat (+2.9%) - [bron]

### **Marktontwikkelingen & Geopolitiek**
- [2-3 bullets met datum + bron]

### **Automatische Synchronisatie Resultaten**
- **Geopolitieke content**: Brent $104.49/vat (+2.9% vs gisteren)
- **IEA effectiviteit**: Matig (prijs $100-110/vat toont gedeeltelijke succes)
- **Energiemix**: Kern 35-40% + Hernieuwbaar 30% + Gas 20% + Import/Overig 10-15% = 95-105%
- **Storage**: 67% nog te vullen (90% doel - 23% huidig)

### **Forecast**: Bearish X% / Basis X% / Bullish X% — [toelichting]

### **Wijzigingen**: Volledig automatische synchronisatie van alle secties met live KPI-data
```

---

## Stap 4 — Commit en push

// turbo
1. Voer uit vanuit de projectmap:

```bash
git add src/EnergieRapport.jsx UPDATE_LOG.md
git commit -m "update [DD-MM-YYYY]: Volledige automatische synchronisatie - KPI kleurlogica, geopolitieke sync, IEA dynamisch, energiemix compleet, timezone fix"
git push origin main
```

2. Cloudflare Pages bouwt automatisch na de push (~1-2 minuten).

---

## Optioneel — Lessons Learned

1. Nieuwe inzichten over automatische synchronisatie? Voeg toe aan `CLAUDE.md` onder `## Lessons Learned ([datum])`.
2. Verouderde start-instructie in CLAUDE.md? Pas aan en commit apart.

---

## ✅ Automatische Update Voltooid

**Resultaat**: Het EnergieRapport is nu volledig automatisch up-to-date met:
- ✅ Live KPI synchronisatie
- ✅ Dynamische geopolitieke content  
- ✅ Intelligente IEA analyse
- ✅ Complete energiemix data
- ✅ Correcte timezone weergave
- ✅ Precieze storage calculations

**Het rapport is nu altijd 100% current met de marktsituatie! 🚀**
