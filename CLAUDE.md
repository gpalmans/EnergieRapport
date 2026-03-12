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

## Stap 1 — Data verzamelen via Tavily

Voer de volgende Tavily searches uit. Gebruik altijd meerdere queries per datapunt
om te kruisvalideren. Markeer elk cijfer als ✓ (twee bronnen overeenkomen) of
~ (één bron of interpolatie).

### TTF Aardgas (€/MWh)
```
tavily_search: "TTF natural gas price today €/MWh"
tavily_search: "TTF gas spot price [huidige maand] [huidig jaar]"
tavily_search: "Dutch TTF gas price history last 30 days"
```
**Primaire bronnen voor validatie:**
- **Vandaag**: https://www.oilpriceapi.com/live/dutch-ttf-gas-price
- **Historisch**: https://www.investing.com/commodities/dutch-ttf-gas-c1-futures-historical-data

Doel: dagelijkse slotprijzen voor de afgelopen ~30 handelsdagen.
Ankerpunten bevestigen via ICE of GIE AGSI+.

### Belpex / EPEX Elektriciteit (€/MWh)
```
tavily_search: "Belpex day-ahead electricity price Belgium today"
tavily_search: "EPEX SPOT Belgium electricity [huidige maand] [huidig jaar]"
```
**Primaire bron voor validatie:**
- **Vandaag & Historisch**: https://euenergy.live/country.php?a2=BE

Doel: daggemiddelde day-ahead prijzen zelfde periode als TTF.

### EU Gasopslag (%)
```
tavily_search: "EU gas storage level percentage today GIE AGSI"
tavily_search: "European natural gas storage [huidige maand] [huidig jaar]"
```
Doel: meest recente weekcijfer, EU-gemiddelde en vergelijking met vorig jaar.

### Olieprijzen
```
tavily_search: "Brent crude oil price today $/barrel"
```
Doel: meest recente slotkoers + eventuele uitschieters.

### Geopolitieke context
```
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

### Wat aanpassen:
1. `rawData` array — nieuwe dagprijzen toevoegen, oudste verwijderen (houd ~30 handelsdagen)
2. `forecastBase/Bull/Bear` arrays — startpunt = laatste ✓ datapunt, einddatum = +6-8 weken
3. KPI blokken — actuele TTF, Belpex, EU opslag%, Brent + wijziging vs. vorige ankerpunt
4. Alert banner — tekst aanpassen aan actuele crisissituatie (of verwijderen als markt rustig)
5. Datum in header — `MARKTANALYSE — DD MAAND YYYY`
6. Geopolitieke sectie (tab "context") — feiten bijwerken
7. Bronnen tab — gebruikte bronnen voor deze update toevoegen

### Wat NIET aanpassen zonder expliciete opdracht:
- Algehele structuur (5 tabs, KPI grid, sectie-indeling)
- Visueel thema (kleuren, donkere achtergrond #0f172a)
- Vast/variabel advieslogica en Belgische juridische context
- 12-maanden loyaliteitsboodschap
- Disclaimer in de footer

---

## Stap 4 — Offline HTML syncen (`public/offline.html`)

De offline.html is een zelfstandige Canvas-implementatie zonder externe libs.
Na het updaten van de JSX, pas identiek aan:

1. `marketData` JavaScript array (= zelfde waarden als JSX `rawData`)
2. `forecastBase/Bull/Bear` arrays
3. KPI-blokken in de HTML
4. Alert-banner tekst
5. Datum in de header

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
Controleer de build status op https://dash.cloudflare.com na de push.

---

## Datavalidatie checklist (uitvoeren vóór commit)

- [ ] Minimaal 3 datapunten met ✓ (twee bronnen bevestigd)
- [ ] TTF en Belpex data lopen tot en met de rapportdatum
- [ ] Forecast startpunt = laatste ✓ datapunt
- [ ] KPI's in JSX en offline.html zijn identiek
- [ ] Datum in header klopt in beide bestanden
- [ ] Geen kapotte apostrofs in offline.html JavaScript
- [ ] UPDATE_LOG.md bijgewerkt met deze sessie
- [ ] Commit message is beschrijvend

---

## Vaste databronnen (referentie)

| Bron | Wat | URL |
|------|-----|-----|
| ENTSO-E | Belpex dagprijzen | https://transparency.entsoe.eu |
| dayaheadmarket.eu | Belpex dagprijzen | https://www.dayaheadmarket.eu/belgium |
| Elia | Belgische day-ahead ref | https://www.elia.be/en/grid-data/transmission/day-ahead-reference-price |
| GIE AGSI+ | EU gasopslag % | https://agsi.gie.eu |
| ICE TTF | TTF futures/spot | https://www.ice.com/products/27996665 |
| IEA | Beleidswijzigingen | https://www.iea.org |
| VREG | Belgische tariefwijzigingen | https://www.vreg.be |
| CREG | Belgische marktmonitor | https://www.creg.be |

---

## Hoe een update-sessie starten

Open Claude Code in de projectmap en typ:

```
Lees CLAUDE.md en UPDATE_LOG.md.
Voer een volledige update uit voor vandaag.
Gebruik Tavily om actuele TTF, Belpex, EU gasopslag en Brent data op te halen.
Update src/EnergieRapport.jsx en public/offline.html.
Vul UPDATE_LOG.md in.
Push naar GitHub.
```

Claude Code voert dan autonoom alle stappen uit.

---

## Projectlocatie

- **Repository:** `https://github.com/UWGEBRUIKER/energie-rapport-2026`
  *(pas aan naar uw eigen GitHub gebruikersnaam)*
- **Cloudflare URL:** `https://energie-rapport-2026.pages.dev`
- **Lokale map:** de map waar u deze repo gecloned heeft

---

## MCP Configuratie (eenmalige setup)

### 1. Tavily API key ophalen
Ga naar https://app.tavily.com → Sign up (gratis, geen creditcard) →
API Keys → kopieer de key (formaat: `tvly-xxxxxxxxxxxx`)

### 2. Claude Code MCP config aanpassen

Open of maak het bestand `~/.claude/claude_desktop_config.json`
(op Windows: `%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "tavily": {
      "command": "npx",
      "args": ["-y", "tavily-mcp"],
      "env": {
        "TAVILY_API_KEY": "tvly-UW-API-KEY-HIER"
      }
    }
  }
}
```

Vervang `tvly-UW-API-KEY-HIER` door uw echte Tavily key.

### 3. Verificatie

Start Claude Code opnieuw op. Typ in Claude Code:
```
gebruik tavily om de huidige TTF gasprijs op te zoeken
```

Als Tavily correct geconfigureerd is, ziet u een zoekresultaat.
Als u een foutmelding krijgt, controleer of `npx` beschikbaar is
(`npx --version` in een terminal) en of de API key correct is.

### 4. GitHub toegang voor Claude Code

Claude Code heeft schrijftoegang tot de repo nodig voor `git push`.
Controleer dat uw lokale git geconfigureerd is:

```bash
git config --global user.email "uw@email.com"
git config --global user.name "Uw Naam"
```

En dat u SSH of HTTPS toegang heeft tot de repo:
```bash
git remote -v  # moet uw repo URL tonen
git push --dry-run origin main  # test zonder te pushen
```

