---
description: Verzamel actuele marktdata voor het EnergieRapport (TTF, Belpex, België gasopslag, Brent). Blokkeert totdat alle 4 variabelen via 2+ onafhankelijke bronnen (±2%) bevestigd zijn. Voer dit als eerste stap uit vóór update-energie-rapport.
---

# Stap 1 — Context laden

// turbo
1. Lees `src/EnergieRapport.jsx` (focus: `rawData` array, KPI-waarden, header datum).
2. Noteer: laatste datapunt in rawData, rapportdatum = vandaag.

---

# Stap 2 — TTF Aardgas (BLOKKEEREND — zoek tot ✓ gevonden)

3. Zoek actuele TTF-slotprijs (€/MWh):
   - `tavily_search: "TTF natural gas price today €/MWh [maand] [jaar]"`
   - `tavily_search: "Dutch TTF gas price Trading Economics [datum]"`
   - Fallback: oilpriceapi.com, Investing.com, ICE TTF, Bloomberg Energy
4. Verzamel dagelijkse slotprijzen ~30 handelsdagen. Markeer: ✓ (2+ bronnen ±2%) of ~ (interpolatie).

---

# Stap 3 — Belpex Elektriciteit (BLOKKEEREND — zoek tot ✓ gevonden)

5. Zoek daggemiddelde day-ahead prijs (€/MWh):
   - `tavily_search: "Belpex EPEX Belgium electricity price today [maand] [jaar]"`
   - Valideer via euenergy.live/country.php?a2=BE en dayaheadmarket.eu/belgium
   - Let op: dayaheadmarket.eu geeft €/kWh → ×1000 voor €/MWh
   - Fallback: `tavily_search: "Belgium electricity spot price €/MWh [gisteren]"`

---

# Stap 4 — België gasopslag + Brent (BLOKKEEREND — zoek tot beide ✓)

6. België gasopslag (%):
   - `tavily_search: "EU gas storage level percentage [maand] [jaar]"`
   - Fallback: Swiss Info, Bruegel, Energy Dashboard, Caliber.az
7. Brent Crude ($/vat):
   - `tavily_search: "Brent crude oil price today $/barrel"`
   - Bronnen: Trading Economics, Investing.com, Yahoo Finance

---

# Stap 5 — Geopolitieke scan

8. Scan minimaal 4 bronnen (max 4 weken oud, ~70% NL):
   - `tavily_search: "energieprijzen België [maand] [jaar]"`
   - `tavily_search: "TTF gas geopolitiek [maand] [jaar]"`
   - `tavily_search: "energy market geopolitical risk [maand] [jaar]"`
   - `tavily_search: "IEA energy policy [maand] [jaar]"` + Hormuz/LNG/VREG indien relevant
9. Noteer per bevinding: bron, datum, 1-zin samenvatting, impact (positief/negatief/neutraal).
10. Identificeer welke events als grafiekmarkers dienen (zie update-energie-rapport).

---

# GATE — Bevestig alle 4 variabelen voor je verdergaat

- [ ] TTF (€/MWh) — bevestigd via 2+ bronnen: €___
- [ ] Belpex (€/MWh) — bevestigd via 2+ bronnen: €___
- [ ] België gasopslag (%) — bevestigd via 2+ bronnen: ___%
- [ ] Brent ($/vat) — bevestigd via 2+ bronnen: $___

Pas na bevestiging van alle 4: voer update-energie-rapport uit.
