---
description: Voer een volledige end-to-end update uit van het EnergieRapport voor de huidige datum. Verzamelt actuele marktdata, verwerkt geopolitieke context, updatet JSX en offline.html, valideert alles en pusht naar GitHub.
---

# EnergieRapport — Volledige Update Workflow

Lees eerst `CLAUDE.md` en `UPDATE_LOG.md` volledig voor je begint. Deze workflow is gebaseerd op alle instructies, best-practices en lessons learned uit die bestanden.

---

## Stap 1 — Context laden

// turbo
1. Lees `CLAUDE.md` volledig.
2. Lees de laatste 3 entries in `UPDATE_LOG.md` voor context uit vorige sessies.
3. Lees de huidige `src/EnergieRapport.jsx` om de bestaande `rawData`, `forecastBase/Bull/Bear` arrays, KPI's en geopolitieke context te kennen. Focus op lijnen 1-100 (data arrays) en de KPI/alert sectie.
4. Noteer intern: rapportdatum = vandaag (gebruik de werkelijke datum), laatste datapunt in rawData, huidige forecast maxima.

---

## Stap 2 — TTF Aardgas data verzamelen

5. Voer de volgende Tavily searches uit om de actuele TTF-prijs te bepalen:
   - `tavily_search: "TTF natural gas price today €/MWh [huidige maand] [huidig jaar]"`
   - `tavily_search: "Dutch TTF gas spot price history last 30 days"`
   - `tavily_search: "TTF gas price Trading Economics [huidige datum]"`
   - Valideer via: https://www.oilpriceapi.com/live/dutch-ttf-gas-price

6. Verzamel dagelijkse slotprijzen voor de afgelopen ~30 handelsdagen (alle werkdagen, geen weekends). Markeer elk punt als ✓ (2+ bronnen overeenkomen ±2%) of ~ (1 bron/interpolatie).

---

## Stap 3 — Belpex elektriciteit data verzamelen

7. Voer de volgende Tavily searches uit:
   - `tavily_search: "Belpex day-ahead electricity price Belgium today [huidige maand] [huidig jaar]"`
   - `tavily_search: "EPEX SPOT Belgium electricity average price [huidige week]"`
   - Valideer via: https://euenergy.live/country.php?a2=BE en https://www.dayaheadmarket.eu/belgium

8. Doel: daggemiddelde day-ahead prijs (€/MWh) voor dezelfde periode als TTF. Let op: dayaheadmarket.eu toont €/kWh → vermenigvuldig met 1000 voor €/MWh.

---

## Stap 4 — EU Gasopslag en Brent data verzamelen

9. EU Gasopslag:
   - `tavily_search: "EU gas storage level percentage today [huidig jaar]"`
   - `tavily_search: "European natural gas storage GIE AGSI [huidige maand] [huidig jaar]"`
   - Alternatieve bronnen als GIE AGSI niet direct beschikbaar: Swiss Info, Bruegel, Energy Dashboard
   - Markeer als ✓ als 2 bronnen overeenkomen

10. Brent Crude Oil:
    - `tavily_search: "Brent crude oil price today $/barrel"`
    - `tavily_search: "Brent oil price [huidige datum] [huidig jaar]"`
    - Bronnen: Investing.com, Yahoo Finance, Trading Economics

---

## Stap 5 — Geopolitieke en nieuwscontext scannen

11. Scan minstens 4 van deze bronnen op relevante ontwikkelingen (max 4 weken oud):
    - `tavily_search: "energieprijzen België [huidige maand] [huidig jaar]"`
    - `tavily_search: "TTF gas geopolitiek nieuws [huidige maand] [huidig jaar]"`
    - `tavily_search: "energy market geopolitical risk [huidige maand] [huidig jaar]"`
    - `tavily_search: "Hormuz LNG supply disruption [huidig jaar]"`
    - `tavily_search: "IEA energy policy announcement [huidige maand] [huidig jaar]"`
    - `tavily_search: "Belgium energy tariff VREG [huidige maand] [huidig jaar]"`
    - `tavily_search: "energiecrisis België gas elektriciteit [huidige maand]"`

12. Verwerk bevindingen:
    - Minimaal 2-5 relevante items
    - Per item: bron, publicatiedatum, 1-zin samenvatting, impactlabel (positief/negatief/neutraal)
    - Conclusie: effect op TTF, Belpex, basis/bullish/bearish scenario
    - **NL-talige bronnen krijgen voorrang** (~70% NL, ~30% EN)
    - Controleer elke URL op geldigheid voor opname

---

## Stap 6 — Forecast scenario's bijwerken

13. Bepaal de drie forecast scenario's op basis van actuele marktomstandigheden:
    - **Bearish**: geopolitieke spanning daalt, LNG-aanbod herstelt → kans omlaag bij escalatie
    - **Basis**: altijd het meest waarschijnlijke scenario
    - **Bullish**: nieuwe escalatie, koud weer, opslagtekort → kans omhoog bij crisis
    - Kansen moeten altijd optellen tot 100%

14. **KRITISCH — Y-as validatie (lesson learned 20-03-2026)**:
    - Bepaal het maximum van alle bullish datapunten in de forecast
    - Controleer of `YAxis domain` in JSX (en `yMax` in offline.html) hoog genoeg is
    - Voeg minimaal 5-10% marge toe boven het bullish maximum
    - Pas aan als bullish maximum > huidige yMax

15. Stel forecastperiode in: rapportdatum + 6 à 8 weken, in 5-6 datapunten.

---

## Stap 7 — `src/EnergieRapport.jsx` bijwerken

16. Update de `rawData` array:
    - Voeg nieuwe dagprijzen toe (TTF + Belpex per handelsdag)
    - Verwijder oudste datapunten zodat ~30 handelsdagen overblijven
    - Zorg dat **precies 1 datapunt** de note `"Vandaag"` heeft (de rapportdatum)
    - Geen dubbele Vandaag-labels

17. Update de `forecastBase`, `forecastBull`, `forecastBear` arrays:
    - Startpunt = laatste ✓ datapunt uit rawData
    - Einddatum = rapportdatum + 6-8 weken

18. Update de KPI-blokken:
    - TTF actuele prijs + % wijziging vs. vorig ankerpunt
    - Belpex actuele prijs + % wijziging
    - EU gasopslag %
    - Brent actuele prijs + % wijziging

19. Update de alert-banner:
    - Tekst aanpassen aan actuele crisissituatie
    - Verwijderen als markt rustig is

20. Update de header datum: `MARKTANALYSE — DD MAAND YYYY`

21. Update de geopolitieke sectie (tab "context"):
    - Feiten bijwerken met actuele context
    - NL/EN mix, publicatiedatums vermelden

22. **KRITISCH — Advies sectie her-evalueren (lesson learned 20-03-2026)**:
    - Zijn de argumenten in "Vaste vs. Variabel" nog actueel?
    - Passen de tijdslijnen bij de huidige geopolitieke situatie?
    - Zijn de prijsdoelen realistisch gezien de actuele markt?
    - Onderscheid korte termijn (2-5 mnd) vs. middellange termijn (6-18 mnd) duidelijk?
    - Pas aan als nodig; pas NIET aan als advieslogica nog correct is

23. Update de bronnen tab:
    - Voeg gebruikte bronnen toe met publicatiedatums
    - NL bronnen eerst, dan EN voor unieke context
    - Verwijder bronnen ouder dan 4 weken (tenzij unieke historische context)
    - Valideer alle URLs

24. Update de `YAxis domain` als bullisch maximum dit vereist:
    ```jsx
    <YAxis domain={[20, <nieuw_max>]} ... />
    ```

---

## Stap 8 — `public/offline.html` syncen

25. Update de `marketData` JavaScript array (= identiek aan JSX `rawData`)
26. Update de `forecastBase`, `forecastBull`, `forecastBear` arrays (= identiek aan JSX)
27. Update de KPI-blokken in HTML (= identiek aan JSX KPI's)
28. Update de alert-banner tekst (= identiek aan JSX)
29. Update de header datum (= identiek aan JSX)
30. Update de bronvermeldingen (= identiek aan JSX bronnen tab)
31. Update `const yMin = 20, yMax = <nieuw_max>;` als Y-as aangepast is

32. **KRITISCH — Apostrof-controle**:
    - Controleer alle JavaScript strings in offline.html op apostrofs
    - `Lloyd's` → `Lloyd\'s` in JavaScript strings
    - Een kapotte apostrof crasht de volledige `<script>` block

---

## Stap 9 — Data cross-check (vóór commit)

Voer deze volledige checklist uit en bevestig elk punt:

**Data Kwaliteit:**
- [ ] Minimaal 3 datapunten met ✓ (twee bronnen bevestigd)
- [ ] TTF en Belpex data lopen tot en met de rapportdatum
- [ ] Forecast startpunt = laatste ✓ datapunt

**Synchronisatie JSX ↔ offline.html:**
- [ ] Alle KPI-waarden identiek in beide bestanden
- [ ] Header datum identiek in beide bestanden
- [ ] rawData / marketData arrays identiek
- [ ] forecastBase/Bull/Bear arrays identiek
- [ ] Bronvermeldingen identiek
- [ ] **SLECHTS 1x 'Vandaag' label** in beide versies

**Technische validatie:**
- [ ] Geen kapotte apostrofs in offline.html JavaScript
- [ ] Alle bron URLs zijn geldig en controleerbaar
- [ ] Geen verouderde bronnen (ouder dan 4 weken)
- [ ] ~70% NL, ~30% EN bronnen
- [ ] Forecast grafiek Y-as past bij bullisch scenario maximum + marge

**Advies sectie (lesson learned 20-03-2026):**
- [ ] Tijdslijnen in advies zijn realistisch gegeven actuele herstelperiodes
- [ ] Prijsdoelen reflecteren actuele marktrealiteit
- [ ] IEA-argument klopt bij het type marktschok (psychologisch vs. fysiek)
- [ ] Onderscheid korte vs. middellange termijn aanwezig

**Data cross-check:**
- [ ] TTF prijs consistent in KPI, rawData, geopolitieke tekst
- [ ] Belpex prijs consistent in KPI, rawData, bronnen
- [ ] Brent prijs consistent in KPI, geopolitieke sectie
- [ ] EU gasopslag consistent in KPI en context sectie

---

## Stap 10 — UPDATE_LOG.md bijwerken

33. Voeg een nieuwe entry toe aan het begin van `UPDATE_LOG.md`:

```markdown
## Update [N] — [DD maand YYYY]

### **Bevestigde Marktdata (✓)**
- **TTF Gas**: €XX.XX/MWh (+/-X.X% vs gisteren) - [bron] bevestigd
- **Belpex Elektriciteit**: €XXX.X/MWh (+/-X.X% vs gisteren) - [bron]
- **EU Gasopslag**: ~XX% - GIE AGSI bevestigd
- **Brent Ruwe Olie**: $XXX.XX/vat (+/-X.X% vs gisteren) - [bron]

### **Belangrijke Marktontwikkelingen**
- [bevinding 1]
- [bevinding 2]

### **Geopolitieke Context**
- [context punt 1]
- [context punt 2]

### **Forecast Aanpassingen**
- **Scenario Probabiliteiten**: Bearish X% / Basis X% / Bullish X%
- [toelichting]

### **Technische Updates**
- **EnergieRapport.jsx**: [wat gewijzigd]
- **offline.html**: [wat gewijzigd]

### **Bronnen Update**
- **TTF Data**: [bron] - €XX.XX/MWh bevestigd
- **Belpex Data**: [bron]
- **EU Gas Storage**: [bron]
```

---

## Stap 11 — Commit en push

// turbo
34. Voer de volgende git commando's uit vanuit de projectmap:

```bash
git add src/EnergieRapport.jsx public/offline.html UPDATE_LOG.md CLAUDE.md
git commit -m "update [DD-MM-YYYY]: TTF €XX.XX, Belpex €XXX.X — [één zin context]"
git push origin main
```

35. Bevestig dat de push succesvol was. Cloudflare Pages bouwt automatisch (~1-2 minuten) na de push.

---

## Optionele Stap 12 — Lessons Learned bijwerken

36. Als er tijdens deze update nieuwe inzichten zijn opgedaan (nieuwe bugs, nieuwe databronnen, gewijzigde argumenten), voeg dan een nieuwe sectie toe aan `CLAUDE.md` onder `## Lessons Learned ([datum])`.

37. Als de start-instructie (`## Hoe een update-sessie starten`) verouderd is, pas die dan ook aan.

38. Commit CLAUDE.md apart als er significante wijzigingen zijn:
```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md lessons learned [DD-MM-YYYY]"
git push origin main
```
