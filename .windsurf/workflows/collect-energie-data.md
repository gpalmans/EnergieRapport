---
description: Verzamel actuele marktdata voor het EnergieRapport via betrouwbare API's (TTF, Belpex, België gasopslag, Brent). Gebruik data_collector.py voor automatische API data verzameling. Voer dit als eerste stap uit vóór update-energie-rapport.
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

**Na bevestiging**: voer update-energie-rapport uit.

---

# ⚡ API Voordelen vs Manual Search

✅ **Betrouwbaar**: Directe data van officiële bronnen  
✅ **Snel**: Automatisch verzameld in <30 seconden  
✅ **Consistent**: Altijd hetzelfde dataformaat  
✅ **Actueel**: Real-time market data  

❌ **Manual search**: Traag, onbetrouwbaar, variabele kwaliteit
