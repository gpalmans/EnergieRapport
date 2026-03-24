# CLAUDE.md — Werkinstructies voor Energie Rapport Updates

Dit bestand vertelt Claude Code hoe het energierapport periodiek bijgewerkt moet worden.
Lees dit bestand volledig voor je begint. Raadpleeg ook `UPDATE_LOG.md` voor context
uit vorige sessies.

---

## Tooling & MCP configuratie

Dit project gebruikt de **Tavily MCP server** voor web search. Claude Code moet
deze server beschikbaar hebben als tool. Zie onderaan dit bestand voor de setup.

Bij elke update gebruik je Tavily om actuele marktdata op te halen. Zoek altijd
via meerdere queries om datapunten te kruisvalideren.

---

## Wat is dit project?

Een interactief energierapport voor Vlaamse residentiële klanten, gepubliceerd op
Cloudflare Pages. Het vergelijkt TTF-gasprijzen en Belpex-elektriciteitsprijzen,
geeft geopolitieke context, en biedt een vast/variabel tariefadvies.

### Primaire deliverable per update:

- `src/EnergieRapport.jsx` — interactieve React/Recharts versie (hoofdrapport)

### Afgeleide output die altijd mee gecontroleerd moet worden:

- PDF-uitvoer via `src/hooks/usePDFDownload.js` en `src/utils/pdfGenerator.js`
- Wijzigingen in JSX-teksten, KPI's, forecast ranges of contextblokken moeten dus ook in de PDF-data/mapping correct doorkomen.

---

## Operationele waarheid — JSX + PDF-consistentie

### Actuele realiteit:

1. **`src/EnergieRapport.jsx` is de primaire bron van waarheid** voor de rapportinhoud.
2. **PDF-output is afgeleid maar moet inhoudelijk identiek blijven** voor KPI's, ranges, tekstblokken en tabelwaarden.
3. **Offline HTML / compiler-flow is geen standaard updatepad meer** en mag niet opnieuw als verplichte synchronisatiestap worden ingevoerd.

### Wat dit betekent voor je

- **Werk primair in `src/EnergieRapport.jsx`**
- **Controleer altijd de PDF-pariteit** als cijfers, forecast ranges, KPI-teksten of contextblokken aangepast zijn
- **Controleer expliciet** `src/hooks/usePDFDownload.js` en `src/utils/pdfGenerator.js` wanneer dezelfde data of teksten daar gespiegeld worden
- **Gebruik geen oude compile/sync scripts als standaardaanpak**

---

## Stap 1 — Data verzamelen via Tavily

Voer de volgende Tavily searches uit. Gebruik altijd meerdere queries per datapunt
om te kruisvalideren. Markeer elk cijfer als ✓ (twee bronnen overeenkomen) of
~ (één bron of interpolatie).

### TTF Aardgas (€/MWh)

```text
tavily_search: "TTF natural gas price today €/MWh"
tavily_search: "TTF gas spot price [huidige maand] [huidig jaar]"
tavily_search: "Dutch TTF gas price history last 30 days"
```

**Primaire bronnen voor validatie:**

- **Vandaag**: <https://www.oilpriceapi.com/live/dutch-ttf-gas-price>
- **Historisch**: <https://www.investing.com/commodities/dutch-ttf-gas-c1-futures-historical-data>

Doel: dagelijkse slotprijzen voor de afgelopen ~30 handelsdagen.
Ankerpunten bevestigen via ICE of GIE AGSI+.

### Belpex / EPEX Elektriciteit (€/MWh)

```text
tavily_search: "Belpex day-ahead electricity price Belgium today"
tavily_search: "EPEX SPOT Belgium electricity [huidige maand] [huidig jaar]"
```

**Primaire bron voor validatie:**

- **Vandaag & Historisch**: <https://euenergy.live/country.php?a2=BE>

Doel: daggemiddelde day-ahead prijzen zelfde periode als TTF.

### EU Gas Storage (%)

```text
tavily_search: "EU gas storage level percentage today"
tavily_search: "European gas storage levels 2026"
```

**Bronnen:** GIE AGSI+, Energy Dashboard.

### Brent Crude Oil ($/vat)

```text
tavily_search: "Brent crude oil price today"
tavily_search: "Brent oil price March 2026"
```

**Bronnen:** Investing.com, Yahoo Finance.

---

## Stap 1.5 — Geopolitieke & Marktanalyse Bronnen Scannen

Na het verzamelen van de basisdata scan je aanvullende nieuws- en marktbronnen op
informatie die de energieprijzen, de geopolitieke context en de forecastscenario's
kan beïnvloeden.

Belangrijk:
- Gebruik deze bronnen als **context- en interpretatiebron**, niet als primaire validatie
  van TTF-, Belpex-, opslag- of Brent-cijfers.
- Numerieke kerncijfers blijven gevalideerd via de primaire databronnen uit stap 1.
- Neem alleen items op die **concreet relevant** zijn voor prijsbewegingen,
  marktverwachtingen of Belgische eindklanten.

### 📅 BEST PRACTICES — Nieuws-Horizon & Taal

**4-weken nieuws-horizon:**

- Gebruik alleen nieuwsberichten van maximaal 4 weken oud
- Prioriteit aan meest recente artikelen (huidige datum > 1 week oud > 2-4 weken oud)
- Publicatiedatums ALTIJD expliciet vermelden in bronvermeldingen

**NL/EN Taalstrategie:**

- Mix van NL en EN talige bronnen is toegestaan
- **NL-talig krijgt voorrang** bij dezelfde informatie
- EN-talig alleen toevoegen voor unieke informatie die niet beschikbaar is in NL
- Doel: ~70% NL, ~30% EN voor maximale relevantie en internationale context

**Bronvalidatie:**

- Controleer elke URL op geldigheid voor toevoeging
- Vervang ongeldige links onmiddellijk
- Gebruik korte, functionele URLs (bv. VRT: vrtnws.be/p.0Y6qkWYOx)

### Belgische & Nederlandse Energiebronnen

- **Mijn Energie Blog**: <https://www.mijnenergie.be/blog>
  - Focus: Belgische energiemarkt, tariefontwikkelingen, beleidsupdates
  - Zoektermen: "energieprijzen", "gas elektriciteit", "tarieven"

- **De Tijd**: <https://www.tijd.be/>
  - Focus: Financiële analyse, energiebedrijven, marktontwikkelingen
  - Zoektermen: "energie", "TTF", "Belpex", "gas"

- **VRT Nieuws Energie**: <https://www.vrt.be/vrtnws/nl/dossiers/2021/09/energieprijzen/>
  - Focus: Nieuws over energieprijzen, beleid, consumentenimpact
  - Zoektermen: "energieprijzen", "gas elektriciteit"

- **VRT Nieuws Milieu & Energie**: <https://www.vrt.be/vrtnws/nl/net-binnen/milieu-en-klimaat/energie/>
  - Focus: Klimaatbeleid, hernieuwbare energie, energietransitie
  - Zoektermen: "hernieuwbaar", "zonne-energie", "wind"

- **De Redactie**: <https://www.deredactie.be>
  - Focus: Politiek nieuws, energiebeleid, EU-regelgeving
  - Zoektermen: "energiebeleid", "EU", "klimaat"

### Regulatorische & Marktdata Bronnen

- **CREG Publicaties**: <https://www.creg.be/en/publications>
  - Focus: Belgische energieregulator, marktrapporten, tariefbesluiten
  - Zoektermen: "tariff", "market report", "electricity", "gas"

- **Montel News**: <https://montelnews.com/>
  - Focus: Europese energiemarkt nieuws, trading, prijzen
  - Zoektermen: "power prices", "gas", "TTF", "Belgium"

- **EEX Newsroom**: <https://www.eex.com/en/newsroom>
  - Focus: Energy Exchange nieuws, marktdata, trading
  - Zoektermen: "power", "gas", "market news"

### Scan Strategie per Update

Scan per update **minstens 4 van deze bronnen**, waarvan:

- minstens 1 Belgische consumenten- of nieuwsbron
- minstens 1 regulatorische of professionele marktbron
- minstens 1 bron met expliciete geopolitieke of beleidscontext

Zoek in die bronnen naar:

1. **Directe prijsinvloeden:**
   - Nieuwe overheidsmaatregelen of subsidies
   - Onderhoud aan kerncentrales of gasinfrastructuur
   - LNG-leveringsproblemen of nieuwe contracten
   - Weergerelateerde vraagveranderingen

2. **Geopolitieke ontwikkelingen:**
   - EU-sancties of energiebeleid wijzigingen
   - Rusland-Oekraïne conflict impact
   - Midden-Oosten spanningen (Hormuz, Qatar LNG)
   - Internationale klimaatovereenkomsten

3. **Structurele marktveranderingen:**
   - Nieuwe capaciteit (zonnepanelen, wind, batterijen)
   - Netwerkuitbreidingen of beperkingen
   - Opslagontwikkelingen (gas, elektriciteit)
   - Leveranciersstrategie en tariefontwikkelingen

4. **Consumentenimpact:**
   - Nieuwe tariefvoorstellen van leveranciers
   - VREG/CREG beslissingen
   - Overheidssteun of maatregelen
   - Marktverwachtingen en adviezen

### Minimale output van deze scan

Leg per update minstens het volgende vast:
- 2 tot 5 relevante bevindingen
- per bevinding: bron, datum, samenvatting in 1 zin, en impactlabel `positief`,
  `negatief` of `neutraal`
- een korte conclusie over het effect op:
  - TTF
  - Belpex
  - het basis/bullish/bearish scenario

### Integratie in Rapport

De gevonden informatie wordt verwerkt in:

- **Analyse tab:** Marktontwikkelingen en prijsfactoren
- **Geopolitiek tab:** Internationale context en risico's
- **Forecast scenario's:** Aanpassing van kansen en trends
- **Bronnen tab:** Referenties naar gebruikte bronnen
- **Alert banner:** Acute crisissituaties of belangrijke wijzigingen

### Geopolitieke context (extra scanning)

```text
tavily_search: "energy market geopolitical risk [huidige maand] [huidig jaar]"
tavily_search: "Strait of Hormuz LNG supply disruption [huidig jaar]"
tavily_search: "IEA energy policy announcement [huidige maand] [huidig jaar]"
tavily_search: "Belgium energy tariff VREG [huidige maand] [huidig jaar]"
```

Doel: actieve crisissituaties, beleidswijzigingen, marktbewegende nieuwsfeiten.

### Validatieregel

Gebruik een datapunt ALLEEN als ✓ als minstens twee onafhankelijke bronnen
hetzelfde cijfer (±2%) bevestigen. Noteer bij elk punt de bronnen.

---

## Stap 2 — Forecast bijwerken

Pas de drie scenario's aan op basis van actuele marktomstandigheden.
De kansen mogen verschuiven maar moeten optellen tot 100%.

| Scenario | Standaard kans | Aanpassen als... |
|----------|---------------|-----------------|
| Bearish  | 25%           | Geopolitieke spanning daalt, LNG-aanbod herstelt |
| Basis    | 50%           | Altijd het meest waarschijnlijke scenario |
| Bullish  | 25%           | Nieuwe escalatie, koud weer, opslagtekort |

Forecastperiode = rapportdatum + 6 à 8 weken, in 5-6 datapunten.

- Kalibreer de ranges op **actuele spotprijs + plausibele normalisatie/escalatie**, niet op oude defaults.
- Basis blijft standaard dominant, tenzij harde marktdata of concrete escalatie dat tegenspreken.
- Bullish is geen standaard tweede basisscenario; gebruik het als scenario met duidelijke trigger en realistische tail-risk bandbreedte.

---

## Stap 3 — JSX bijwerken (`src/EnergieRapport.jsx`)

### Wat aanpassen:
1. `rawData` array — nieuwe dagprijzen toevoegen, oudste verwijderen (houd ~30 handelsdagen)
2. `forecastBase/Bull/Bear` arrays — startpunt = laatste ✓ datapunt, einddatum = +6-8 weken
3. KPI blokken — actuele TTF, Belpex, EU opslag%, Brent + wijziging vs. vorige ankerpunt
4. Alert banner — tekst aanpassen aan actuele crisissituatie (of verwijderen als markt rustig)
5. **Header datum — `MARKTANALYSE — DD MAAND YYYY` (altijd up-to-date)**
6. **Alle secties up-to-date houden — Analyse, Geopolitiek, Forecast, Bronnen**
7. **Geopolitieke sectie (tab "context") — feiten bijwerken met NL/EN mix**
8. **Bronnen tab — gebruikte bronnen met publicatiedatums, NL voorrang**
9. **Sleutelfactoren — uniforme layout per factor**:
    - Verwachte impact: `TTF [min-max%] · Belpex [min-max%]`
    - Waarom dit de prijs beweegt
    - Wat te monitoren
10. **PDF-pariteit** — check of dezelfde inhoud ook in `usePDFDownload.js` en `pdfGenerator.js` juist wordt weergegeven

### 📅 BEST PRACTICES — Data Consistentie

**Datumconsistentie:**

- Header datum = huidige rapportdatum
- Alle publicatiedatums in bronnen moeten relevant en up-to-date zijn
- Geen verouderde artikelen (bv. 2013) in bronvermeldingen
- Forecast data start vanaf laatste datapunt

**Prijstabel labeling:**

- **SLECHTS 1x 'vandaag' label** in de prijs tabel
- 'Vandaag' label alleen op huidige rapportdatum
- Geen dubbele 'vandaag' labels of verwarrende markeringen
- Status badges consistent: Hormuz Shock, Piekprijs, IEA, Vandaag, Weekend

**Geopolitieke en forecast inhoud:**

- Geopolitieke items krijgen 2-3 zinnen: feit, effect, verwachte evolutie
- Sleutelfactoren altijd sorteren van meest impactvol naar minst impactvol
- Forecast ranges moeten realistisch blijven t.o.v. actuele TTF en headline risk

### Wat NIET aanpassen zonder expliciete opdracht:
- Algehele structuur (5 tabs, KPI grid, sectie-indeling)
- Visueel thema (kleuren, donkere achtergrond #0f172a)
- Vast/variabel advieslogica en Belgische juridische context
- 12-maanden loyaliteitsboodschap
- Disclaimer in de footer

---

## Stap 4 — PDF-consistentie controleren

**KRITISCH: PDF en JSX moeten inhoudelijk 100% overeenkomen op alle kernwaarden.**

Controleer na elke inhoudelijke update minstens dit:

1. KPI-waarden en KPI-percentages identiek
2. Belpex decimalen blijven correct in PDF-prijstabellen
3. Forecast ranges en kansen identiek
4. Geopolitieke sectie en sleutelfactoren tekstueel identiek
5. Brent-, TTF-, Belpex- en opslagwaarden overal consistent

### JSX/PDF Consistentie Checklist (VERPLICHT)

Voor ELKE update, voer deze checklist uit:

**Structuur & Inhoud:**

- [ ] KPI-grid waarden identiek tussen scherm en PDF
- [ ] Header datum/tijd en rapportcontext logisch doorgegeven aan PDF
- [ ] Kernboodschap, praktisch advies, geopolitiek en sleutelfactoren volledig meegenomen

**Data Waarden:**

- [ ] TTF prijs consistent overal
- [ ] Belpex prijs consistent overal  
- [ ] Brent prijs consistent overal
- [ ] België gasopslag consistent overal
- [ ] Header datum = huidige rapportdatum

**Tekst & Bronnen:**

- [ ] Geopolitieke sectie tekst identiek
- [ ] Sleutelfactoren structuur identiek (`impact / waarom / monitor`)
- [ ] Praktisch advies stappen identiek
- [ ] Bronvermeldingen inhoudelijk correct en up-to-date

**Technisch:**

- [ ] `usePDFDownload.js` gebruikt actuele waarden voor KPI's, forecast en tekstblokken
- [ ] `pdfGenerator.js` rondt Belpex niet onbedoeld af
- [ ] Geen dubbele of verouderde datumlabels

---

## Stap 5 — GitHub push

```bash
git add src/EnergieRapport.jsx UPDATE_LOG.md
git commit -m "update [DD-MM-YYYY]: TTF €XX.XX, Belpex €XX.X — [één zin context]"
git push origin main
```

Cloudflare Pages bouwt automatisch na de push (~1-2 minuten).
Controleer de build status op <https://dash.cloudflare.com> na de push.

---

## Datavalidatie checklist (uitvoeren vóór commit)

### Data Kwaliteit

- [ ] Minimaal 3 datapunten met ✓ (twee bronnen bevestigd)
- [ ] TTF en Belpex data lopen tot en met de rapportdatum
- [ ] Forecast startpunt = laatste ✓ datapunt
- [ ] Alle datums zijn up-to-date en relevant

### Synchronisatie

- [ ] KPI's in JSX en PDF zijn identiek
- [ ] Header datum en rapportcontext kloppen in beide representaties
- [ ] Bronvermeldingen zijn inhoudelijk consistent
- [ ] **SLECHTS 1x 'vandaag' label** in de brondata

### Technische Validatie

- [ ] Geen onbedoelde afronding van Belpex of KPI-percentages in PDF-output
- [ ] Alle bron URLs zijn geldig en testbaar
- [ ] **Geen verouderde bronnen** (ouder dan 4 weken, tenzij unieke historische context)
- [ ] **NL/EN mix correct** (~70% NL, ~30% EN, NL voorrang bij duplicate info)

### Documentatie

- [ ] UPDATE_LOG.md bijgewerkt met deze sessie
- [ ] Commit message is beschrijvend

---

## Lessons Learned (Update 20-03-2026)

### Critical Analysis of Advice Sections

**Probleem: Verouderde Argumenten na Geopolitieke Escalatie**
- IEA-argument was te optimistisch na gasveld aanvallen
- Praktisch advies had onrealistische tijdslijnen (2-3 weken te kort)
- Prijsdoelen waren niet aangepast aan nieuwe realiteit (€40 onhaalbaar)
- **Oplossing**: Altijd kritisch her-evalueren van advies bij structurele marktveranderingen

**Aanpassingen Vaste vs. Variabel Sectie:**
- IEA-argument: "breekt piek binnen weken" → "dempt maar lost structurele schade niet op"
- Observatieperiode: 2-3 weken → 4-6 weken (gasveld herstel duurt 3-5 maanden)
- Prijsdoelen: €40 variabel aantrekkelijk → €50 (realistischer)
- Prijsdoelen: €50 vast overwegen → €60 voor 6+ weken
- Adviesmatrix: Genuanceerde motivering met korte vs. middellange termijn onderscheid

**Kernboodschap Tijdshorizon:**
- **Korte termijn (2-5 maanden)**: Verhoogd niveau door fysieke schade
- **Middellange termijn (6-18 maanden)**: Normalisatie door seizoen + LNG-golf
- Onderscheid tussen psychologische piek vs. fysieke supply disruption

### Forecast Grafiek Technische Issues

**Probleem: Y-as Cap Te Laag**
- Bullisch scenario stijgt tot €85/MWh
- Grafiek had maximum van €80/MWh
- Lijnen vielen buiten zichtbaar bereik
- **Oplossing**: Y-axis domain aanpassen in JSX zodat alle scenario's zichtbaar blijven met voldoende marge

### Data Consistentie Validatie

**Checklist Uitgebreid:**
- [ ] Forecast grafiek Y-as past bij scenario maxima
- [ ] Advies sectie argumenten passen bij huidige geopolitieke situatie
- [ ] Tijdslijnen zijn realistisch gegeven fysieke herstelperiodes
- [ ] Prijsdoelen reflecteren actuele marktrealiteit
- [ ] Onderscheid tussen korte en middellange termijn duidelijk

### Data Verzamelingsstrategie

**België gasopslag Alternatieve Bronnen:**
- Swiss Info: Europese storage facilities percentages
- Chinese financial sources: GIE AGSI data vertalingen
- Bruegel: European natural gas imports datasets
- Caliber.az: Europe gas storage level mentions

**Belpex Data Validatie:**
- dayaheadmarket.eu: Average Price (€/kWh → omrekenen naar €/MWh)
- euenergy.live: Real-time prijzen (check op actualiteit)
- Elia.be: Day-ahead reference price (scraping nodig)

### Consistentie Validatie Checklist

**Voor Commit:**
- [ ] Alle KPI's identiek in JSX en PDF
- [ ] Geopolitiek sectie data matches KPI's
- [ ] Geen verouderde datumreferenties in tekst
- [ ] Alle bron URLs zijn geldig en up-to-date
- [ ] Publicatiedatums relevant (max 4 weken oud)

**Data Cross-Check:**
- [ ] TTF prijs consistent overal
- [ ] Belpex prijs consistent overal  
- [ ] Brent prijs consistent overal
- [ ] België gasopslag consistent overal
- [ ] Header datum = huidige rapportdatum

### Bronnen Strategie

**NL/EN Mix Realisatie:**
- 73% NL, 27% EN is haalbaar en effectief
- NL bronnen krijgen voorrang bij duplicate info
- EN bronnen voor unieke internationale context

**Data Verificatie:**
- Trading Economics: TTF en Brent (betrouwbaar)
- dayaheadmarket.eu: Belpex average (nauwkeurig)
- Swiss Info: België gasopslag (actueel)
- GIE AGSI: Primaire bron (via secondary sources)

---

## Lessons Learned (Update 19-03-2026)

### Data Consistentie Issues

**Probleem 1: Brent Prijs Inconsistentie**
- Header KPI: $97.06/vat
- Geopolitiek sectie: $101.06/vat
- **Oplossing**: Altijd alle voorkomens van dezelfde data synchroniseren

**Probleem 2: België gasopslag Data "Niet Beschikbaar"**
- Header KPI: "N.v.t. - data niet beschikbaar"
- Context sectie: 29.0% (18/03/2026)
- **Oplossing**: Zoek actief naar alternatieve bronnen (Swiss Info, GIE AGSI via Chinese financial sources)

**Probleem 3: Verouderde Datumreferenties**
- Tekst bevatte nog 18/03 referenties na update naar 19/03
- **Oplossing**: Systematisch alle verouderde data verwijderen of updaten

### Data Verzamelingsstrategie

**België gasopslag Alternatieve Bronnen:**
- Swiss Info: Europese storage facilities percentages
- Chinese financial sources: GIE AGSI data vertalingen
- Bruegel: European natural gas imports datasets
- Caliber.az: Europe gas storage level mentions

**Belpex Data Validatie:**
- dayaheadmarket.eu: Average Price (€/kWh → omrekenen naar €/MWh)
- euenergy.live: Real-time prijzen (check op actualiteit)
- Elia.be: Day-ahead reference price (scraping nodig)

### Consistentie Validatie Checklist

**Voor Commit:**
- [ ] Alle KPI's identiek in JSX en PDF
- [ ] Geopolitiek sectie data matches KPI's
- [ ] Geen verouderde datumreferenties in tekst
- [ ] Alle bron URLs zijn geldig en up-to-date
- [ ] Publicatiedatums relevant (max 4 weken oud)

**Data Cross-Check:**
- [ ] TTF prijs consistent overal
- [ ] Belpex prijs consistent overal  
- [ ] Brent prijs consistent overal
- [ ] België gasopslag consistent overal
- [ ] Header datum = huidige rapportdatum

### Bronnen Strategie

**NL/EN Mix Realisatie:**
- 73% NL, 27% EN is haalbaar en effectief
- NL bronnen krijgen voorrang bij duplicate info
- EN bronnen voor unieke internationale context

**Data Verificatie:**
- Trading Economics: TTF en Brent (betrouwbaar)
- dayaheadmarket.eu: Belpex average (nauwkeurig)
- Swiss Info: België gasopslag (actueel)
- GIE AGSI: Primaire bron (via secondary sources)

---

## Projectlocatie

- **Repository:** `https://github.com/gpalmans/TariffAnalysisComparison`
- **Cloudflare URL:** `https://energie-rapport-2026.pages.dev`
- **Lokale map:** `D:\Users\Gijs\Documents\Automatisering\EnergieRapport`

---