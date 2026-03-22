---
description: Voer een volledige end-to-end update uit van het EnergieRapport voor de huidige datum. Verzamelt actuele marktdata, verwerkt geopolitieke context, updatet JSX en offline.html, valideert alles en pusht naar GitHub.
---

# EnergieRapport — Volledige Update Workflow

Lees eerst `CLAUDE.md` en `UPDATE_LOG.md` volledig voor je begint. Deze workflow is gebaseerd op alle instructies, best-practices en lessons learned uit die bestanden.

> ⛔ **BLOKKERENDE REGEL**: De analyse is NIET compleet en mag NIET worden gecommit of gepusht totdat voor **alle vier** kernvariabelen (TTF, Belpex, EU Gasopslag, Brent) een bevestigde ✓ waarde is gevonden via minimaal 2 onafhankelijke bronnen (±2%). Blijf alternatieve zoekstrategieën toepassen totdat dit is bereikt.

---

## Stap 1 — Context laden

// turbo
1. Lees `CLAUDE.md` volledig.
2. Lees de laatste 3 entries in `UPDATE_LOG.md` voor context uit vorige sessies.
3. Lees de huidige `src/EnergieRapport.jsx` om de bestaande `rawData`, `forecastBase/Bull/Bear` arrays, KPI's en geopolitieke context te kennen.
4. Noteer intern: rapportdatum = vandaag (gebruik de werkelijke datum), laatste datapunt in rawData, huidige forecast maxima, welke grafiekevents al aanwezig zijn.

---

## Stap 2 — TTF Aardgas data verzamelen (BLOKKEEREND)


5. Voer de volgende Tavily searches uit om de actuele TTF-prijs te bepalen:
   - `tavily_search: "TTF natural gas price today €/MWh [huidige maand] [huidig jaar]"`
   - `tavily_search: "Dutch TTF gas spot price history last 30 days"`
   - `tavily_search: "TTF gas price Trading Economics [huidige datum]"`
   - Valideer via: https://www.oilpriceapi.com/live/dutch-ttf-gas-price

6. Als geen ✓ gevonden na eerste ronde, gebruik alternatieve queries:
   - `tavily_search: "TTF gas price €/MWh [gisteren of eergisteren datum]"`
   - `tavily_search: "natural gas futures Europe price [huidig jaar]"`
   - `tavily_search: "ICE TTF settlement price [huidige week]"`
   - Probeer ook: Investing.com, Bloomberg Energy, Reuters Commodities

7. Verzamel dagelijkse slotprijzen voor de afgelopen ~30 handelsdagen (werkdagen, geen weekends). Markeer elk punt als ✓ (2+ bronnen ±2%) of ~ (1 bron/interpolatie). Minstens 3 punten moeten ✓ zijn.

---

## Stap 3 — Belpex elektriciteit data verzamelen (BLOKKEEREND)

8. Voer de volgende Tavily searches uit:
   - `tavily_search: "Belpex day-ahead electricity price Belgium today [huidige maand] [huidig jaar]"`
   - `tavily_search: "EPEX SPOT Belgium electricity average price [huidige week]"`
   - Valideer via: https://euenergy.live/country.php?a2=BE en https://www.dayaheadmarket.eu/belgium

9. Als geen ✓ gevonden na eerste ronde, gebruik alternatieve queries:
   - `tavily_search: "Belgium electricity spot price €/MWh [gisteren of eergisteren datum]"`
   - `tavily_search: "Belpex EPEX Belgium power price [huidige datum]"`
   - Let op: dayaheadmarket.eu toont €/kWh → vermenigvuldig ×1000 voor €/MWh

10. Doel: daggemiddelde day-ahead prijs (€/MWh) voor dezelfde periode als TTF.

---

## Stap 4 — EU Gasopslag en Brent data verzamelen (BLOKKEEREND)


11. EU Gasopslag:
    - `tavily_search: "EU gas storage level percentage today [huidig jaar]"`
    - `tavily_search: "European natural gas storage GIE AGSI [huidige maand] [huidig jaar]"`
    - Alternatieve bronnen als GIE AGSI niet direct beschikbaar: Swiss Info, Bruegel, Energy Dashboard, Caliber.az
    - Markeer als ✓ als 2 bronnen overeenkomen

12. Brent Crude Oil:
    - `tavily_search: "Brent crude oil price today $/barrel"`
    - `tavily_search: "Brent oil price [huidige datum] [huidig jaar]"`
    - Bronnen: Investing.com, Yahoo Finance, Trading Economics

13. ⛔ **GATE**: Ga NIET verder naar Stap 5 totdat alle 4 variabelen ✓ zijn bevestigd:
    - [ ] TTF (€/MWh) — ✓ via 2+ bronnen
    - [ ] Belpex (€/MWh) — ✓ via 2+ bronnen
    - [ ] EU Gasopslag (%) — ✓ via 2+ bronnen
    - [ ] Brent ($/vat) — ✓ via 2+ bronnen

---

## Stap 5 — Geopolitieke en nieuwscontext scannen

14. Scan minstens 4 van deze bronnen op relevante ontwikkelingen (max 4 weken oud):
    - `tavily_search: "energieprijzen België [huidige maand] [huidig jaar]"`
    - `tavily_search: "TTF gas geopolitiek nieuws [huidige maand] [huidig jaar]"`
    - `tavily_search: "energy market geopolitical risk [huidige maand] [huidig jaar]"`
    - `tavily_search: "Hormuz LNG supply disruption [huidig jaar]"`
    - `tavily_search: "IEA energy policy announcement [huidige maand] [huidig jaar]"`
    - `tavily_search: "Belgium energy tariff VREG [huidige maand] [huidig jaar]"`
    - `tavily_search: "energiecrisis België gas elektriciteit [huidige maand]"`

15. Verwerk bevindingen (minimaal 2-5 items):
    - Per item: bron, publicatiedatum, 1-zin samenvatting, impactlabel (positief/negatief/neutraal)
    - Conclusie: effect op TTF, Belpex, basis/bullish/bearish scenario
    - **NL-talige bronnen krijgen voorrang** (~70% NL, ~30% EN)
    - Identificeer ook welke events als grafiekmarkers dienen (zie Stap 7a)

---

## Stap 6 — Forecast scenario's bijwerken


16. Bepaal de drie forecast scenario's op basis van actuele marktomstandigheden:
    - **Bearish**: geopolitieke spanning daalt, LNG-aanbod herstelt → kans omlaag bij escalatie
    - **Basis**: altijd het meest waarschijnlijke scenario
    - **Bullish**: nieuwe escalatie, koud weer, opslagtekort → kans omhoog bij crisis
    - Kansen moeten altijd optellen tot 100%

17. **KRITISCH — Y-as validatie (lesson learned 20-03-2026)**:
    - Bepaal het maximum van alle bullish datapunten
    - Controleer of `YAxis domain` in JSX (en `yMax` in offline.html) hoog genoeg is
    - Voeg minimaal 5-10% marge toe boven het bullish maximum
    - Pas aan als bullish maximum > huidige yMax

18. Stel forecastperiode in: rapportdatum + 6 à 8 weken, in 5-6 datapunten.

---

## Stap 7 — `src/EnergieRapport.jsx` bijwerken

### 7.1 — Basisdata

19. Update de `rawData` array:
    - Voeg nieuwe dagprijzen toe (TTF + Belpex per handelsdag)
    - Verwijder oudste datapunten zodat ~30 handelsdagen overblijven
    - Zorg dat **precies 1 datapunt** de note `"Vandaag"` heeft (de rapportdatum)
    - Geen dubbele Vandaag-labels

20. Update de `forecastBase`, `forecastBull`, `forecastBear` arrays:
    - Startpunt = laatste ✓ datapunt uit rawData
    - Einddatum = rapportdatum + 6-8 weken

21. Update de KPI-blokken (TTF, Belpex, EU opslag, Brent) en de alert-banner.

22. Update de header datum: `MARKTANALYSE — DD MAAND YYYY`

---

### 7.2 — Grafiek events opnemen (punt 2)

23. Identificeer alle significante marktevenementen die zich voordoen **binnen de datumrange van de rawData**:
    - Voorbeelden: start Hormuz-blokkade, IEA-vrijgave aankondiging, gasveld aanvallen, kerncentrale herstart, beleidswijziging
    - Gebruik de geopolitieke bevindingen uit Stap 5 als input

24. Voeg voor elk relevant event een `referenceLine` of annotatie toe in de TTF-grafiek **en** de Belpex-grafiek (als het beide markten beïnvloedt):
    - **Prijsstijgend event** (bv. blokkade, aanval): gebruik `stroke="#ef4444"` (rood) met label
    - **Prijsdalend event** (bv. IEA-vrijgave, deëscalatie): gebruik `stroke="#22c55e"` (groen) met label
    - Label = korte naam + datum, bv. `"Hormuz"` of `"IEA"`
    - Verwijder events waarvan de datum buiten de huidige rawData window valt

---

### 7.3 — Geopolitieke Crisissituatie (punt 3)

25. Update elk item in de "Geopolitieke Crisissituatie" sectie met **2 tot 3 informatieve zinnen**:
    - **Zin 1**: Wat is het event? (feitelijke beschrijving, neutraal)
    - **Zin 2**: Wat is het directe, aantoonbare effect op de energieprijzen of aanvoer?
    - **Zin 3** (optioneel): Wat is de verwachte evolutie, tijdslijn of risico voor de komende weken?
    - Gebruik concrete cijfers waar beschikbaar (bv. "-17% LNG-exportcapaciteit", "dag 21 blokkade")
    - Maximaal 3 zinnen per item — niet meer

---

### 7.4 — Belgische Energiemix (punt 4)

26. Update de "Belgische Energiemix" sectie met een **expliciete uitleg van de gas-elektriciteitskoppeling**:
    - Leg het **merit-order mechanisme** uit: gascentrales draaien vaak als marginale producenten en bepalen daarmee de prijs voor **alle** geleverde elektriciteit op de day-ahead markt, ook groene stroom
    - Concreet voorbeeld: "Als een gascentrale €80/MWh nodig heeft om winstgevend te draaien, is dat de spotprijs — ook al levert een windpark voor €20/MWh"
    - Vermeld het actuele aandeel gascentrales in de Belgische productiemix (zoek op via Elia of Tavily)
    - Sluit af met de consumentenimplicatie: variabele tarieven volgen de spotmarkt; bij hoge gasprijzen betaal je dus meer, ook bij groene stroom
    - Schrijf dit in maximaal 4 begrijpelijke zinnen voor de gemiddelde consument

---

### 7.5 — Sleutelfactoren om op te volgen (punt 5)

27. Update de "Sleutelfactoren" sectie. Geef elke factor:
    - **Een ranking** (🔴 Kritisch / 🟠 Belangrijk / 🟡 Opvolgen)
    - **Oorzaak**: wat is de factor precies?
    - **Gevolg**: hoe beïnvloedt dit TTF en/of Belpex? In welke richting? Op welke termijn?
    - Sorteer van meest naar minst impactvol
    - Gebruik dit formaat per factor:
      ```
      📌 [Ranking] [Naam van de factor]
      Oorzaak: [beschrijving van wat het is]
      Gevolg: [verwacht effect op prijs, richting, termijn]
      ```
    - Minimaal 5, maximaal 8 factoren

---

### 7.6 — Vaste vs. Variabel tariefadvies (punt 6 + 7)

28. Update de "Vaste vs. Variabel" sectie met de volgende vaste regels:

    **Horizont**: Alle aanbevelingen zijn uitsluitend voor **12 tot maximaal 18 maanden**. Nooit langere termijnen adviseren. De consument heeft in België het wettelijk recht om kosteloos te veranderen, vaak maand-op-maand — dit maakt lange commitments onnodig en risicovol.

    **Argumenten voor Variabel** (als TTF bearish of stabiliserend):
    - Welke concrete structurele factoren maken variabel aantrekkelijk? (bv. LNG-aanbodgolf, injectieseizoen, normalisatie na crisis)
    - Historisch bewijs: in dalende markten was variabel X% goedkoper dan vast op 12 maanden
    - Flexibiliteit: bij verdere daling profiteert de consument direct
    - Wanneer omschakelen? Concrete TTF-drempel vermelden (bv. "als TTF stabiliseert onder €50/MWh")

    **Argumenten voor Vast** (als TTF aanhoudend hoog of bullish):
    - Welke concrete factoren maken vast aantrekkelijk? (bv. fysieke supply disruption, lange herstelperiode)
    - Budgetzekerheid vs. risico op verdere stijging
    - Wanneer overwegen? Concrete TTF-drempel en tijdsduur (bv. "als TTF >€60/MWh voor 6+ weken")
    - Waarschuwing: nooit vastleggen op een piekte — wacht op stabilisatie

    **Vermijd** generieke clichés. Gebruik altijd **actuele TTF-niveaus** en **concrete verwachte trends** uit de forecast.

---

### 7.7 — Adviesmatrix verificatie (punt 7)

29. Controleer **elke rij** van de adviesmatrix op actualiteit:
    - Is de aanbeveling (vast/variabel/neutraal) nog correct gegeven huidige TTF en geopolitieke situatie?
    - Past de tijdshorizon (12-18 maanden) bij de aanbeveling?
    - Is de motivering specifiek genoeg (geen generieke zinnen)?
    - Is de voorzorgsmaatregel relevant voor de actuele markt?
    - Pas elke verouderde rij aan. Voeg `[bijgewerkt DD/MM]` toe in de motivering als je een rij wijzigt.

---

### 7.8 — Kernboodschap en Praktisch Advies (punt 8)

30. Update de "Kernboodschap" sectie:
    - Maak deze **visueel prominent**: opvallend kleurblok, grotere achtergrond, duidelijk afgebakend van omliggende secties
    - De inhoud moet de **actuele marktситуatie weerspiegelen** — geen generieke tekst
    - Vermeld expliciet: huidige TTF-prijs, korte termijn verwachting (2-5 mnd) én lange termijn verwachting (6-18 mnd)
    - Maximaal 3-4 zinnen, scherp en begrijpelijk voor de gemiddelde consument
    - Als er een crisis is: erken het korte termijn verhoogde niveau, maar relativeer met de lange termijn trend

31. Update het "Praktisch Advies" blok:
    - Geef **concrete, uitvoerbare actie-items** gebaseerd op actuele TTF:
      - "Als TTF stabiliseert onder €X/MWh → doe Y"
      - "Als TTF boven €X/MWh blijft voor Z weken → overweeg Y"
    - Vermeld expliciet de **maximale contracttermijn**: nooit meer dan 12-18 maanden
    - Vermeld de **concrete wachttijd** (bv. 4-6 weken) voor marktbeoordeling als er hoge volatiliteit is
    - Sluit ALTIJD af met de anti-paniek boodschap: **"Nooit overhaast tekenen tijdens een nieuwscyclus die voelt als een noodsituatie. Paniek is een slechte raadgever."**

---

### 7.9 — Bronnen en Y-as

32. Update de bronnen tab:
    - Voeg gebruikte bronnen toe met publicatiedatums
    - NL bronnen eerst, dan EN voor unieke context
    - Verwijder bronnen ouder dan 4 weken (tenzij unieke historische context)
    - Valideer alle URLs

33. Update de `YAxis domain` als bullisch maximum dit vereist:
    ```jsx
    <YAxis domain={[20, <nieuw_max>]} ... />
    ```

---

## Stap 8 — `public/offline.html` syncen

34. Update de `marketData` JavaScript array (= identiek aan JSX `rawData`)
35. Update de `forecastBase`, `forecastBull`, `forecastBear` arrays (= identiek aan JSX)
36. Update de KPI-blokken in HTML (= identiek aan JSX KPI's)
37. Update de alert-banner tekst (= identiek aan JSX)
38. Update de header datum (= identiek aan JSX)
39. Update de bronvermeldingen (= identiek aan JSX bronnen tab)
40. Update `const yMin = 20, yMax = <nieuw_max>;` als Y-as aangepast is
41. Sync alle inhoudelijke wijzigingen uit Stap 7.2 t/m 7.8: grafiek events, geopolitieke teksten, energiemix uitleg, sleutelfactoren ranking, vaste/variabel argumenten, adviesmatrix, kernboodschap en praktisch advies

42. **KRITISCH — Apostrof-controle**:
    - Controleer alle JavaScript strings in offline.html op apostrofs
    - `Lloyd's` → `Lloyd\'s` in JavaScript strings
    - Een kapotte apostrof crasht de volledige `<script>` block

---

## Stap 9 — Data cross-check (vóór commit)

> ⛔ **BLOKKERENDE GATE**: Commit ALLEEN als alle items hieronder ✓ zijn.

**Data volledigheid (BLOKKEEREND):**
- [ ] TTF (€/MWh) — ✓ bevestigd via 2+ onafhankelijke bronnen
- [ ] Belpex (€/MWh) — ✓ bevestigd via 2+ onafhankelijke bronnen
- [ ] EU Gasopslag (%) — ✓ bevestigd via 2+ onafhankelijke bronnen
- [ ] Brent ($/vat) — ✓ bevestigd via 2+ onafhankelijke bronnen
- [ ] Minimaal 3 datapunten in rawData met ✓

**Synchronisatie JSX ↔ offline.html:**
- [ ] Alle KPI-waarden identiek in beide bestanden
- [ ] Header datum identiek in beide bestanden
- [ ] rawData / marketData arrays identiek
- [ ] forecastBase/Bull/Bear arrays identiek
- [ ] Bronvermeldingen identiek
- [ ] **SLECHTS 1x 'Vandaag' label** in beide versies
- [ ] Grafiek events (referentielijnen) identiek in beide versies

**Technische validatie:**
- [ ] Geen kapotte apostrofs in offline.html JavaScript
- [ ] Alle bron URLs zijn geldig en controleerbaar
- [ ] Geen verouderde bronnen (ouder dan 4 weken)
- [ ] ~70% NL, ~30% EN bronnen
- [ ] Forecast grafiek Y-as past bij bullisch scenario maximum + marge

**Inhoudelijke validatie:**
- [ ] Grafiek events aanwezig voor alle significante marktevenementen in de data window
- [ ] Geopolitieke crisissituatie: elk item heeft 2-3 zinnen (oorzaak, effect, verwachting)
- [ ] Belgische Energiemix: merit-order koppeling gas-elektriciteit uitgelegd
- [ ] Sleutelfactoren: ranking (🔴/🟠/🟡) + oorzaak + gevolg per factor
- [ ] Vaste vs. Variabel: enkel 12-18 maanden horizon, concrete TTF-drempels vermeld
- [ ] Adviesmatrix: elke rij actueel, motivering specifiek, tijdshorizon 12-18 mnd
- [ ] Kernboodschap: visueel prominent, verwijst naar actuele TTF, korte én lange termijn
- [ ] Praktisch advies: concrete actie-items met drempels, max 18 mnd termijn, anti-paniek afsluiting

**Data cross-check:**
- [ ] TTF prijs consistent in KPI, rawData, geopolitieke tekst
- [ ] Belpex prijs consistent in KPI, rawData, bronnen
- [ ] Brent prijs consistent in KPI, geopolitieke sectie
- [ ] EU gasopslag consistent in KPI en context sectie

**Advies sectie (lesson learned 20-03-2026):**
- [ ] Tijdslijnen in advies zijn realistisch gegeven actuele herstelperiodes
- [ ] Prijsdoelen reflecteren actuele marktrealiteit
- [ ] IEA-argument klopt bij het type marktschok (psychologisch vs. fysiek)

---

## Stap 10 — UPDATE_LOG.md bijwerken

43. Voeg een nieuwe entry toe aan het begin van `UPDATE_LOG.md`:

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
44. Voer de volgende git commando's uit vanuit de projectmap:

```bash
git add src/EnergieRapport.jsx public/offline.html UPDATE_LOG.md
git commit -m "update [DD-MM-YYYY]: TTF €XX.XX, Belpex €XXX.X — [één zin context]"
git push origin main
```

45. Bevestig dat de push succesvol was. Cloudflare Pages bouwt automatisch (~1-2 minuten) na de push.

---

## Optionele Stap 12 — Lessons Learned bijwerken

46. Als er tijdens deze update nieuwe inzichten zijn opgedaan (nieuwe bugs, nieuwe databronnen, gewijzigde argumenten), voeg dan een nieuwe sectie toe aan `CLAUDE.md` onder `## Lessons Learned ([datum])`.

47. Als de start-instructie (`## Hoe een update-sessie starten`) verouderd is, pas die dan ook aan.

48. Commit `CLAUDE.md` apart als er significante wijzigingen zijn:

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md lessons learned [DD-MM-YYYY]"
git push origin main
```
