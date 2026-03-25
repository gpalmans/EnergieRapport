---
description: Verzamel actuele marktdata voor het EnergieRapport via betrouwbare API's (TTF, Belpex, België gasopslag, Brent). Gebruik data_collector.py voor automatische API data verzameling. Deze data wordt automatisch gesynchroniseerd met alle secties in het rapport. Voer dit als eerste stap uit vóór update-energie-rapport.
---

# ⚡ Automatische Data Verzameling + Live Synchronisatie

**Nieuw vandaag**: Alle verzamelde data wordt automatisch gesynchroniseerd met:
- ✅ KPI kleurlogica (rood/groen gebaseerd op richting)
- ✅ Geopolitieke content (live Brent/TTF prijzen)
- ✅ IEA Strategische Reserves (dynamische analyse)
- ✅ Belgische Energiemix (complete percentages + actuele Belpex)
- ✅ Storage calculations (correct "nog te vullen")
- ✅ Timezone correctie (CET weergave)

---

# Stap 1 — Automatische API Data Verzameling

// turbo
1. **Run API data collector**:
   ```bash
   python scripts/data_collector.py
   ```
2. **Controleer data** in `data/latest_prices.json`:
   - TTF (€/MWh) - via AGSI GIE API
   - Belpex (€/MWh) - via energy-charts.info API  
   - België gasopslag (%) - via AGSI GIE API
   - Brent ($/vat) - via Oil Price API

---

# Stap 2 — Data Validatie

3. **Verifieer API output**:
   - Open `data/latest_prices.json`
   - Check dat alle 4 variabelen aanwezig zijn
   - Controleer redelijkheid van waarden (TTF ~50-150, Belpex ~50-200, Storage ~20-90%, Brent ~70-120)

4. **Bron verificatie** (optioneel):
   - Tavily search voor vali datie: "TTF gas price today [datum]"
   - Vergelijk met API data als extra check
   - Noteer eventuele afwijkingen >5%

---

# Stap 3 — Geopolitieke Context (via AI)

5. **Run AI analyzer** voor context:
   ```bash
   python scripts/ai_analyzer.py
   ```
6. **Controleer AI analyse** in `data/ai_analysis.json`:
   - Geopolitieke ontwikkelingen
   - Markt impact analyse
   - Grafiek event suggesties

---

# Stap 4 — Data Gateway Bevestiging

- [ ] TTF (€/MWh) — API data: €___
- [ ] Belpex (€/MWh) — API data: €___  
- [ ] België gasopslag (%) — API data: ___%
- [ ] Brent ($/vat) — API data: $___

**Na bevestiging**: voer update-energie-rapport uit voor volledige automatische synchronisatie.

---

# ⚡ Automatische Synchronisatie Resultaten

Na `update-energie-rapport` uitvoering:

✅ **KPI's**: TTF €53.82 (+1.1%), Belpex €72.04 (-1.0%), Brent $104.49 (+2.9%)  
✅ **Kleuren**: Automatisch rood voor stijging, groen voor daling  
✅ **Geopolitiek**: Brent/TTF prijzen live in content  
✅ **IEA**: Dynamische analyse gebaseerd op $104.49/vat  
✅ **Energiemix**: Kern 35-40% + Hernieuwbaar 30% + Gas 20% + Import/Overig 10-15% = 95-105%  
✅ **Storage**: 67% "nog te vullen" (90% doel - 23% huidig)  
✅ **Timezone**: Alle datums in CET, geen UTC mismatch  

---

# ⚡ API Voordelen vs Manual Search

✅ **Betrouwbaar**: Directe data van officiële bronnen  
✅ **Snel**: Automatisch verzameld in <30 seconden  
✅ **Consistent**: Altijd hetzelfde dataformaat  
✅ **Actueel**: Real-time market data  
✅ **Live Sync**: Automatische synchronisatie met alle rapportsecties  

❌ **Manual search**: Traag, onbetrouwbaar, variabele kwaliteit, geen automatische updates
