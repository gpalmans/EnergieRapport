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

**Twee deliverables per update:**
- `src/EnergieRapport.jsx` — interactieve React/Recharts versie (hoofdrapport)
- `public/offline.html` — volledig standalone HTML zonder externe dependencies

Beide bestanden moeten bij elke update gesynchroniseerd worden met identieke data.

---

## Synchronisatie Architectuur — Single Source of Truth

**NIEUW:** Dit project gebruikt nu een deterministische synchronisatie-architectuur:

### Hoe het werkt

1. **JSX als authoritative bron** — EnergieRapport.jsx is de enige bron van waarheid
2. **HTML als derived artifact** — offline.html wordt automatisch gegenereerd uit JSX
3. **Structurele validatie** — Validatie checkt data-integriteit, niet text-patterns

### Automatische workflow

```
JSX Update
    ↓
Compiler (extract data from JSX)
    ↓
HTML Compile (generate offline.html)
    ↓
Validator (verify perfect sync)
    ↓
✓ Deploy or ✗ Reject
```

### Wat dit betekent voor je

- **JSX updaten is genoeg** — HTML wordt automatisch gegenereerd
- **Geen handmatige HTML updates meer** — Die gebeurt via de compiler
- **Garantie perfect in-sync** — Validator controleert vóór deployment
- **Sneller & betrouwbaarder** — Geen sync-drift mogelijk

### GitHub Actions Integration

De GitHub Actions workflow voert nu automatisch uit:
1. Update JSX met marktdata
2. Compileer offline.html uit JSX (`scripts/compile_html.py`)
3. Valideer synchronisatie (`scripts/validate_sync.py`)
4. Push alleen als validatie passed

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

---

## Stap 3 — JSX bijwerken (`src/EnergieRapport.jsx`)

### Automatische HTML-Synchronisatie (NEW)

Na het updaten van de JSX, wordt de `offline.html` **automatisch gegenereerd** en **100% gesynchroniseerd**:

```bash
python scripts/report_updater.py
```

Dit script:
1. ✅ Update JSX met nieuwe marktdata
2. ✅ Generate HTML uit JSX (single source of truth)
3. ✅ Valideer perfecte synchronisatie
4. ✅ Commit changes (als validatie passed)

**Geen handmatige HTML-edits meer nodig.** De HTML wordt volledig gegenereerd uit JSX via deterministische compilation.

Voor lokale testing of handmatige stappen:

```bash
# Only compile HTML (without updating JSX)
python scripts/jsx_to_html_compiler.py src/EnergieRapport.jsx templates/energy_report_template.html public/offline.html

# Verify synchronization
python scripts/sync_validator.py
```

Voor volledig overzicht van architectuur, zie [docs/SYNCHRONIZATION_ARCHITECTURE.md](docs/SYNCHRONIZATION_ARCHITECTURE.md).

### Wat aanpassen:
1. `rawData` array — nieuwe dagprijzen toevoegen, oudste verwijderen (houd ~30 handelsdagen)
2. `forecastBase/Bull/Bear` arrays — startpunt = laatste ✓ datapunt, einddatum = +6-8 weken
3. KPI blokken — actuele TTF, Belpex, EU opslag%, Brent + wijziging vs. vorige ankerpunt
4. Alert banner — tekst aanpassen aan actuele crisissituatie (of verwijderen als markt rustig)
5. **Header datum — `MARKTANALYSE — DD MAAND YYYY` (altijd up-to-date)**
6. **Alle secties up-to-date houden — Analyse, Geopolitiek, Forecast, Bronnen**
7. **Geopolitieke sectie (tab "context") — feiten bijwerken met NL/EN mix**
8. **Bronnen tab — gebruikte bronnen met publicatiedatums, NL voorrang**

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

### Wat NIET aanpassen zonder expliciete opdracht:
- Algehele structuur (5 tabs, KPI grid, sectie-indeling)
- Visueel thema (kleuren, donkere achtergrond #0f172a)
- Vast/variabel advieslogica en Belgische juridische context
- 12-maanden loyaliteitsboodschap
- Disclaimer in de footer

---

## Stap 4 — Offline HTML syncen (`public/offline.html`)

**KRITISCH: HTML en JSX moeten 100% in-sync zijn. Dit is een veelvoorkomend probleem.**

De offline.html is een zelfstandige Canvas-implementatie zonder externe libs.
Na het updaten van de JSX, pas identiek aan:

1. `marketData` JavaScript array (= zelfde waarden als JSX `rawData`)
2. `forecastBase/Bull/Bear` arrays
3. KPI-blokken in de HTML
4. Alert-banner tekst
5. **Header datum — identiek aan JSX versie**
6. **Bronvermeldingen — identiek aan JSX, met NL/EN mix en datums**
7. **Prijstabel — identieke 'vandaag' labeling als JSX**
8. **KERNBOODSCHAP sectie — ALTIJD syncen (dit is een veelvoorkomend missend element)**
9. **Alle tabs en secties — Analyse, Geopolitiek, Forecast, Advies, Bronnen**

### HTML/JSX Synchronisatie Checklist (VERPLICHT)

Voor ELKE update, voer deze checklist uit:

**Structuur & Inhoud:**
- [ ] Kernboodschap sectie aanwezig in offline.html (check: "Weloverwogen keuzen duren langer")
- [ ] Alle 5 tabs aanwezig: Analyse, Geopolitiek, Forecast, Advies, Bronnen
- [ ] KPI-grid identiek (TTF, Belpex, EU Opslag, Brent)
- [ ] Alert banner tekst identiek
- [ ] Header datum identiek (MARKTANALYSE — DD MAAND YYYY · HH:MM)
- [ ] Footer datum identiek (Opgesteld: DD maand YYYY · HH:MM)

**Data Waarden:**
- [ ] TTF prijs identiek in beide bestanden
- [ ] Belpex prijs identiek in beide bestanden
- [ ] Brent prijs identiek in beide bestanden
- [ ] EU Gasopslag % identiek in beide bestanden
- [ ] Alle percentages en wijzigingen (vs gisteren) identiek

**Tekst & Bronnen:**
- [ ] Geopolitieke sectie tekst identiek
- [ ] Kernboodschap tekst identiek
- [ ] Praktisch advies stappen identiek
- [ ] Bronvermeldingen identiek (inclusief publicatiedatums)
- [ ] Alle links/URLs identiek

**Technisch:**
- [ ] Geen kapotte apostrofs in offline.html JavaScript
- [ ] Forecast arrays identiek
- [ ] rawData/marketData arrays identiek
- [ ] Geen dubbele 'vandaag' labels

### KRITISCH — apostrof-regel:
Controleer altijd op apostrofs in JavaScript strings in de offline HTML.
De offline.html wordt gegenereerd via een Python f-string. Een apostrof zoals
`Lloyd's` moet geschreven worden als `Lloyd\\'s` in de Python broncode zodat
de JavaScript output `Lloyd\'s` bevat. Een kapotte apostrof crasht de volledige
`<script>` block en maakt het hele bestand onbruikbaar.

Test na het aanpassen: open offline.html lokaal in Chrome en controleer de
browser console op SyntaxError meldingen voor je commit.

---

## Stap 5 — GitHub push

```bash
git add src/EnergieRapport.jsx public/offline.html UPDATE_LOG.md
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

- [ ] KPI's in JSX en offline.html zijn identiek
- [ ] Header datum klopt in beide bestanden
- [ ] Bronvermeldingen zijn identiek in beide bestanden
- [ ] **SLECHTS 1x 'vandaag' label** in beide versies

### Technische Validatie

- [ ] Geen kapotte apostrofs in offline.html JavaScript
- [ ] Alle bron URLs zijn geldig en testbaar
- [ ] **Geen verouderde bronnen** (ouder dan 4 weken, tenzij unieke historische context)
- [ ] **NL/EN mix correct** (~70% NL, ~30% EN, NL voorrang bij duplicate info)

### Documentatie

- [ ] UPDATE_LOG.md bijgewerkt met deze sessie
- [ ] Commit message is beschrijvend
- [ ] Publicatiedatums staan in alle bronvermeldingen

---

## Vaste databronnen (referentie)

| Bron | Wat | URL |
|------|-----|-----|
| ENTSO-E | Belpex dagprijzen | <https://transparency.entsoe.eu> |
| dayaheadmarket.eu | Belpex dagprijzen | <https://www.dayaheadmarket.eu/belgium> |
| EU-Energy | Belpex dagprijzen | <https://euenergy.live/electricity-prices/belgium/antwerpen> |
| Elia | Belgische day-ahead ref | <https://www.elia.be/en/grid-data/transmission/day-ahead-reference-price> |
| GIE AGSI+ | EU gasopslag % | <https://agsi.gie.eu> |
| ICE TTF | TTF futures/spot | <https://www.ice.com/products/27996665> |
| IEA | Beleidswijzigingen | <https://www.iea.org> |
| VREG | Belgische tariefwijzigingen | <https://www.vreg.be> |
| CREG | Belgische marktmonitor | <https://www.creg.be> |

---

## Hoe een update-sessie starten

Open Claude Code in de projectmap en typ:

```
Lees CLAUDE.md en UPDATE_LOG.md.
Voer een volledige update uit voor vandaag.

**Data verzameling:"
Gebruik Tavily om actuele TTF, Belpex, EU gasopslag en Brent data op te halen.
Valideer datapunten met minstens 2 bronnen (✓).

**Context analyse:"
Gebruik Tavily om actuele nieuwsberichten te zoeken (max 4 weken oud).
- NL-talige bronnen krijgen voorrang
- EN-talig alleen voor unieke informatie
- Publicatiedatums altijd vermelden
- URLs valideren op geldigheid

**Implementatie:"
- Update alle secties (Analyse, Geopolitiek, Forecast, Bronnen)
- Zorg voor 1x 'vandaag' label in prijstabel
- Sync JSX en offline.html identiek
- Header datum up-to-date

**Kritische Validatie (zie Lessons Learned):"
- [ ] Forecast grafiek Y-as past bij scenario maxima (bv. 20-90 voor €85 bullisch)
- [ ] Advies sectie argumenten passen bij huidige geopolitieke situatie
- [ ] Tijdslijnen realistisch gegeven fysieke herstelperiodes (gasvelden 3-5 mnd)
- [ ] Prijsdoelen reflecteren actuele marktrealiteit (€50-60 range)
- [ ] Onderscheid korte vs. middellange termijn duidelijk

**Validatie & push:"
- Gebruik uitgebreide checklist uit Lessons Learned sectie
- Controleer alle URLs en datums
- Vul UPDATE_LOG.md in (incl. sectie verbeteringen)
- Push naar GitHub.
```

Claude Code voert dan autonoom alle stappen uit.

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
- **Oplossing**: Y-axis domain aangepast van [20, 80] naar [20, 90] in beide JSX en offline.html

### Data Consistentie Validatie

**Checklist Uitgebreid:**
- [ ] Forecast grafiek Y-as past bij scenario maxima
- [ ] Advies sectie argumenten passen bij huidige geopolitieke situatie
- [ ] Tijdslijnen zijn realistisch gegeven fysieke herstelperiodes
- [ ] Prijsdoelen reflecteren actuele marktrealiteit
- [ ] Onderscheid tussen korte en middellange termijn duidelijk

---

## Lessons Learned (Update 19-03-2026)

### Data Consistentie Issues

**Probleem 1: Brent Prijs Inconsistentie**
- Header KPI: $97.06/vat
- Geopolitiek sectie: $101.06/vat
- **Oplossing**: Altijd alle voorkomens van dezelfde data synchroniseren

**Probleem 2: EU Gasopslag Data "Niet Beschikbaar"**
- Header KPI: "N.v.t. - data niet beschikbaar"
- Context sectie: 29.0% (18/03/2026)
- **Oplossing**: Zoek actief naar alternatieve bronnen (Swiss Info, GIE AGSI via Chinese financial sources)

**Probleem 3: Verouderde Datumreferenties**
- Tekst bevatte nog 18/03 referenties na update naar 19/03
- **Oplossing**: Systematisch alle verouderde data verwijderen of updaten

### Data Verzamelingsstrategie

**EU Gasopslag Alternatieve Bronnen:**
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
- [ ] Alle KPI's identiek in JSX en offline.html
- [ ] Geopolitiek sectie data matches KPI's
- [ ] Geen verouderde datumreferenties in tekst
- [ ] Alle bron URLs geldig en up-to-date
- [ ] Publicatiedatums relevant (max 4 weken oud)

**Data Cross-Check:**
- [ ] TTF prijs consistent overal
- [ ] Belpex prijs consistent overal  
- [ ] Brent prijs consistent overal
- [ ] EU gasopslag consistent overal
- [ ] Header datum = huidige rapportdatum

### Bronnen Strategie

**NL/EN Mix Realisatie:**
- 73% NL, 27% EN is haalbaar en effectief
- NL bronnen krijgen voorrang bij duplicate info
- EN bronnen voor unieke internationale context

**Data Verificatie:**
- Trading Economics: TTF en Brent (betrouwbaar)
- dayaheadmarket.eu: Belpex average (nauwkeurig)
- Swiss Info: EU gasopslag (actueel)
- GIE AGSI: Primaire bron (via secondary sources)

---

## Projectlocatie

- **Repository:** `https://github.com/gpalmans/TariffAnalysisComparison`
- **Cloudflare URL:** `https://energie-rapport-2026.pages.dev`
- **Lokale map:** `D:\Users\Gijs\Documents\Automatisering\EnergieRapport`

---