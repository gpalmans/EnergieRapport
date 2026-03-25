---
description: Update alle inhoud van het EnergieRapport in `src/EnergieRapport.jsx` met volledige automatische synchronisatie. Alle data, content, analyses en voorspellingen worden automatisch gesynchroniseerd met actuele KPI-waarden. Voer EERST collect-energie-data uit. Daarna valideer-en-push.
---

## ⚡ AUTOMATISCHE SYNCHRONISATIE — Alle data wordt live bijgewerkt

**Nieuwe automatische features (vandaag geïmplementeerd):**

✅ **KPI Kleurlogica**: Automatische kleurtoewijzing gebaseerd op richting (+/-)
✅ **Geopolitieke Content**: Live synchronisatie met Brent/TTF KPI's  
✅ **IEA Strategische Reserves**: Dynamische analyse gebaseerd op actuele Brent prijs
✅ **Belgische Energiemix**: Complete percentages (95-105%) + actuele Belpex data
✅ **Timezone Correctie**: CET-tijdweergave in hele rapport
✅ **Storage Calculation**: Correct "nog te vullen" percentage (90% - huidig niveau)

---

## Stap 1 — Automatische Basisdata Bijwerken

De `report_updater.py` voert nu automatisch uit:

1. **KPI Array** met kleurlogica:
   - Positief (>0%) → **Rood** (#ef4444) - Prijs gestegen
   - Negatief (<0%) → **Groen** (#22c55e) - Prijs gedaald
   - Automatische berekening vs vorige dag

2. **Geopolitieke Content Synchronisatie**:
   - Brent prijzen: `$104.49/vat (+2.9% vs gisteren)`
   - TTF referenties: `€53.82/MWh` 
   - Mega Tariefstijging: Geschaald op basis van actuele TTF beweging
   - Energy Sector rotation: Dynamisch berekend

3. **IEA Strategische Oliereserves**:
   - Actuele Brent prijs in analyse: `$104.49/vat`
   - Dynamische effectiviteitsanalyse:
     - >$110/vat: "Beperkt: structurele impact Hormuz > IEA buffer"
     - $100-110/vat: "Matig: gedeeltelijke succes IEA maatregel"  
     - <$100/vat: "Effectief: succesvolle IEA interventie"
   - Status met huidige prijs en datum

4. **Belgische Energiemix**:
   - Complete percentages: Kern (35-40%) + Hernieuwbaar (30%) + Gas (20%) + Import/Overig (10-15%) = **95-105%**
   - Actuele Belpex notificatie: `⚡ Belpex op 25/03 (€72.04 daggemiddelde) toont daling: -1.0% vs gisteren`

5. **Storage Calculation**:
   - Correcte "nog te vullen": `67%` (90% doel - 23% huidig)
   - Belgische gasopslag consistentie over alle secties

6. **Timezone Correctie**:
   - Header/footer in CET: `25 maart 2026 · 01:01`
   - Geen UTC vs CET discrepantie meer

---

## Stap 2 — Handmatige Verfijning (optioneel)

**Alleen als er specifieke redenen zijn om de automatische data aan te passen:**

1. **`rawData` array**: voeg nieuwe dagprijzen toe, verwijder oudste (houd ~30 handelsdagen). Precies **1x** `note: "Vandaag"` op de rapportdatum.
2. **`forecastBase/Bull/Bear`**: startpunt = laatste ✓ datapunt, einddatum = +6-8 weken, kansen optellen tot 100%.
3. **Alert-banner**: aanpassen aan actuele crisissituatie (of verwijderen als markt rustig).
4. **Y-as forecast**: als bullish max > huidige `YAxis domain`, verhoog met 10% marge.

---

## Stap 3 — Geopolitieke Crisissituatie (Auto-geüpdatet)

De geopolitieke content wordt nu automatisch bijgewerkt met:
- Actuele Brent en TTF prijzen
- Percentage veranderingen vs vorige dag
- Geschaalde Mega Tariefstijging percentages
- Dynamische sector rotatie percentages

**Handmatige finetuning alleen nodig voor:**
- Nieuwe geopolitieke gebeurtenissen
- Diepgaande analyse van specifieke ontwikkelingen

---

## Stap 4 — Sleutelfactoren om op te volgen

1. Geef elke factor een uniforme kaartopbouw en sorteer van meest naar minst impact:
    ```text
    📌 🔴/🟠/🟡 [Naam]
    Verwachte impact: TTF [min-max%] · Belpex [min-max%]
    Waarom dit de prijs beweegt: [causale uitleg]
    Wat te monitoren: [concrete datapunten / bronnen / signalen]
    ```
2. Minimaal 5, maximaal 8 factoren
3. Gebruik expliciete `min-max` impactranges

---

## Stap 5 — Vaste vs. Variabel tariefadvies

1. Horizont: **uitsluitend 12-18 maanden**
2. Gebruik **actuele TTF-niveaus** uit de verzamelde data
3. Concrete drempels: "onder €50/MWh" vs ">€60/MWh voor 6+ weken"

---

## Stap 6 — PDF-consistentie bewaken

1. Controleer of de PDF-output inhoudelijk identiek blijft aan de JSX voor:
   - KPI-waarden en **automatische kleurlogica**
   - **Geopolitieke content** (live gesynchroniseerd)
   - **IEA analyse** (dynamisch gebaseerd op Brent)
   - **Energiemix percentages** (compleet 95-105%)
   - **Storage calculation** (correcte "nog te vullen")

---

## Stap 7 — Automatische Validatie

De updater voert automatisch uit:
- **KPI consistentie check**: Alle prijzen en percentages synchroon
- **Geopolitieke synchronisatie**: Content reflecteert actuele KPI's
- **Storage consistentie**: Belgische opslag data overal identiek
- **Timezone correctie**: Geen UTC/CET mismatch meer

---

> **Resultaat**: Het rapport is nu volledig automatisch up-to-date met actuele markdata!
> 
> Voer na voltooiing `valideer-en-push` uit voor kwaliteitscontrole en commit.
