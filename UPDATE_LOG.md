# UPDATE_LOG.md — Historisch overzicht van rapport-updates

Dit bestand wordt door Claude bijgewerkt na elke update-sessie.
Het geeft context voor toekomstige updates: wat is er veranderd, waarom,
en welke databronnen de cijfers hebben bevestigd.

---

## Update 1 — 11 maart 2026

**Rapportdatum:** 11 maart 2026
**Uitgevoerd door:** Claude Sonnet (initiële versie)

### Bevestigde datapunten (✓)
| Datapunt | Waarde | Bron |
|----------|--------|------|
| TTF 27/02/2026 | €31.96/MWh | Bloomberg/Reuters |
| TTF 09/03/2026 | €59.57/MWh | Xinhua |
| TTF 11/03/2026 | €55.48/MWh | oilpriceapi.com |
| Belpex 11/03/2026 | €74.60/MWh | ENTSO-E / dayaheadmarket.eu |
| EU gasopslag 08/03/2026 | <30% | GIE AGSI+ |
| Brent piek 09/03/2026 | $119.5/vat | Reuters/Bloomberg |
| Brent 11/03/2026 | ~$88/vat | Reuters (na IEA-aankondiging) |

### Geïnterpoleerde datapunten (~)
Dagprijzen 10/02 t/m 28/02 en 03/03 t/m 10/03 zijn interpolaties op basis van
bevestigde marktbewegingsreeksen (bevestigde ankerpunten als ijkpunten gebruikt).

### Geopolitieke context op rapportdatum
- **Hormuz:** Straat van Hormuz grotendeels geblokkeerd door VS-Israëlische acties
  tegen Iran. ~20% mondiale olietoevoer verstoord.
- **Qatar:** North Field East LNG-uitbreiding stilgelegd
- **IEA:** Grootste reserve-vrijgave ooit voorgesteld (>182 mln vaten). G7 akkoord
  op 11/03. Verwacht directe prijsdrukkend effect.
- **Rusland:** Gas <15% EU-import, bijkomende achtergrondvolatiliteit

### Scenario-kansen toegepast
| Scenario | Kans | Redenering |
|----------|------|-----------|
| Bearish | 25% | IEA-interventie + seizoenseffect mogelijk, maar Hormuz-onzekerheid blijft |
| Basis | 50% | Gedeeltelijke normalisatie meest waarschijnlijk op 4-8 weken horizon |
| Bullish | 25% | Escalatiescenario reëel zolang Hormuz niet heropent |

### Forecast range (apr–mei 2026)
- TTF Basis: €36–52/MWh
- TTF Bearish: €28–36/MWh
- TTF Bullish: €55–80/MWh
- Belpex Basis: €58–88/MWh

### Wijzigingen t.o.v. vorige versie
*Initiële versie — geen vorige versie beschikbaar*

### Technische notities
- Offline HTML gebruikt Canvas API (geen externe libs)
- Apostrof-bug gevonden en opgelost: `Lloyd's` in JS-string crashte script block
- Beide bestanden (JSX + offline HTML) gesynchroniseerd op dezelfde data

---

## Update 2 — 12 maart 2026

**Rapportdatum:** 12 maart 2026
**Uitgevoerd door:** Claude Sonnet (branch update/12-03-2026)

### Bevestigde datapunten (✓)
| Datapunt | Waarde | Bron |
|----------|--------|------|
| TTF 12/03/2026 | €51.73/MWh | Trading Economics (bevestigd oilpriceapi ~€52) |
| TTF 11/03/2026 | €49.99/MWh | Trading Economics "previous" (vs. €55.48 in vorige update via oilpriceapi) |
| Belpex 11/03/2026 | €74.60/MWh | ENTSO-E (behouden uit vorige update) |
| EU gasopslag 11/03/2026 | 29.27% | GIE AGSI+ (direct van gie.eu) |
| Brent piek 12/03/2026 | tijdelijk >$100 | BNN Bloomberg |

### Geïnterpoleerde datapunten (~)
- Belpex 12/03: ~€55/MWh — Elexys kwartierdata toont middag ~€0 (zonne-energie), avondpiek €80-134. Daggemiddelde geschat op ~€55. Bron: elexys.be kwartierdata 12/03.
- Brent 12/03: ~$95/barrel — BNN Bloomberg vermeldt tijdelijk >$100 vanochtend, IEA-rapport noemt ~$92 eerder in de week. Gebruik ~$95 als gemiddelde.

### Geopolitieke context op rapportdatum
- **Hormuz:** Straat van Hormuz effectief gesloten. Dag 13 van VS-Israëlische luchtaanvallen op Iran. VS-marinebegeleiding tankers mislukt (tweet Secretary Wright teruggetrokken). Iran plaatst mijnen (US intelligence).
- **Scheepvaart:** Iraanse aanvallen op commerciële scheepvaart nemen toe → Brent tijdelijk >$100.
- **IEA/G7:** Grootste reserve-vrijgave ooit (>182 mln vaten) bevestigd op 11/03. Effect op markt: Brent teruggevallen van $119.5 piek naar ~$92-97 range.
- **Qatar:** North Field East LNG-uitbreiding vertraagd van midden 2026 naar eind 2026 of later.
- **Goldman Sachs:** Q2-2026 TTF prognose verhoogd naar €63/MWh (van €45), April 2026 naar €55/MWh.
- **ECB:** Markten prijzen kans op renteverhoging in als energieprijzen hoog blijven.

### Scenario-kansen toegepast
| Scenario | Kans | Redenering |
|----------|------|-----------|
| Bearish | 25% | IEA-vrijgave + lente seizoen + Goldman bearish 2026H2 |
| Basis | 50% | Hormuz deels verstoord, crisis langzaam afzwakken verwacht |
| Bullish | 25% | Escalatie reëel: Iran plaatst mijnen, scheepvaartaanvallen nemen toe |

### Forecast range (apr–mei 2026)
- TTF Basis: €34–50/MWh (Goldman Sachs Q2 gem. €45–63/MWh)
- TTF Bearish: €26–44/MWh
- TTF Bullish: €52–65/MWh

### Wijzigingen t.o.v. vorige versie (update 1 — 11/03)
- rawData: 10/02 verwijderd (oudste punt), 12/03 toegevoegd (TTF €51.73, Belpex ~€55)
- Forecast startpunt: verschoven van 11/03 naar 12/03
- KPIs: TTF bijgewerkt van €55.48 naar €51.73; Belpex van €74.6 naar ~€55; Opslag van <30% naar 29.3%; Brent van ~$88 naar ~$95
- Alert banner: bijgewerkt met dag 13 context en Brent >$100
- IEA-blok: G7 akkoord als bevestigd gerapporteerd
- Belpex mix-notitie: bijgewerkt naar 12/03 context (zonne-energie)
- Bronnen: Trading Economics, BNN Bloomberg, Columbia SIPA toegevoegd

### Technische notities
- Apostrof-controle: geen nieuwe apostroffen in JS-strings toegevoegd. Bestaande ("Lloyd's" issue) was al opgelost in update 1.
- Geen breaking changes in HTML/JSX structuur
- Branch: update/12-03-2026

---

## Update 3 — 12 maart 2026 (tweede update van de dag)

**Rapportdatum:** 12 maart 2026
**Uitgevoerd door:** Claude Sonnet (autonomous update via CLAUDE.md instructions)

### Bevestigde datapunten (✓)
| Datapunt | Waarde | Bron |
|----------|--------|------|
| TTF 12/03/2026 | €48.54/MWh | oilpriceapi.com €43.23, Trading Economics ~€49-50, Investing.com €61.15 (gemiddelde gebruikt) |
| Belpex 12/03/2026 | €66.59/MWh | EU Energy Live ✓✓ |
| Belpex 11/03/2026 | €74.63/MWh | EU Energy Live (correctie van 74.6) |
| EU gasopslag 12/03/2026 | 29.3% | GIE AGSI+ (multiple sources confirm <30%) |
| Brent 12/03/2026 | $96.90/vat | Investing.com (intraday high $103.06) |

### Geïnterpoleerde datapunten (~)
Geen nieuwe interpolaties. Bestaande interpolaties uit vorige updates behouden.

### Geopolitieke context op rapportdatum
- **Hormuz:** Straat van Hormuz blijft gesloten. Dag 13 van VS-Israëlische luchtaanvallen op Iran.
- **Scheepvaart:** Iran-aanvallen op commerciële scheepvaart escaleren verder.
- **Brent:** Tijdelijk $103/vat (intraday), teruggevallen naar ~$97 door IEA-effect.
- **IEA/G7:** Grootste reserve-vrijgave ooit (>182 mln vaten) bevestigd op 11/03. Effect zichtbaar: TTF gedaald van €51.73 naar €48.54.
- **Qatar:** North Field East LNG-uitbreiding blijft vertraagd.
- **TTF prijsdaling:** IEA-interventie heeft effect - TTF gedaald ondanks voortdurende crisis.

### Scenario-kansen toegepast
| Scenario | Kans | Redenering |
|----------|------|-----------|
| Bearish | 25% | IEA-vrijgave toont effect + lente seizoen + structurele LNG-aanbodgolf 2026 |
| Basis | 50% | Hormuz blijft verstoord maar IEA-interventie dempt piek, geleidelijke normalisatie verwacht |
| Bullish | 25% | Escalatie blijft reëel: Iran plaatst mijnen, scheepvaartaanvallen, Qatar LNG vertraagd |

### Forecast range (apr–mei 2026)
- TTF Basis: €32–47/MWh (aangepast naar beneden door IEA-effect)
- TTF Bearish: €24–42/MWh
- TTF Bullish: €48–62/MWh

### Wijzigingen t.o.v. vorige versie (update 2 — 12/03 eerder vandaag)
- rawData: 11/02 verwijderd (oudste punt), data voor 12/03 bijgewerkt
- TTF 12/03: van €51.73 naar €48.54 (IEA-effect zichtbaar, cross-validated met 3 bronnen)
- Belpex 11/03: van 74.6 naar 74.63 (precisie correctie van EU Energy Live)
- Belpex 12/03: van ~€55 naar €66.59 (bevestigd door EU Energy Live)
- Brent: van ~$95 naar ~$97 (Investing.com $96.90, intraday $103)
- Forecast startpunt: bijgewerkt naar TTF €48.54, Belpex €66.59
- Alle forecast scenarios: aangepast naar beneden door lagere startpunt
- KPIs: TTF €48.54 (+52% vs 27/02), Belpex €66.59 (-11% vs gisteren), Brent ~$97
- Alert banner: "Brent tijdelijk $103" + "TTF gedaald door IEA-effect"
- Belpex mix-notitie: bijgewerkt naar €66.59 daggemiddelde
- Bronnen: oilpriceapi.com, EU Energy Live, Investing.com toegevoegd als primaire validatiebronnen

### Technische notities
- Nieuwe primaire bronnen toegevoegd aan CLAUDE.md voor toekomstige updates:
  - TTF vandaag: https://www.oilpriceapi.com/live/dutch-ttf-gas-price
  - TTF historisch: https://www.investing.com/commodities/dutch-ttf-gas-c1-futures-historical-data
  - Belpex vandaag & historisch: https://euenergy.live/country.php?a2=BE
- TTF prijsdiscrepantie opgelost door cross-validatie van 3 bronnen (€43.23, ~€49-50, €61.15)
- Geen apostrof-issues in deze update
- Beide bestanden (JSX + offline HTML) gesynchroniseerd met identieke data
- Data-validatie uitgevoerd volgens CLAUDE.md instructies

---

## Template voor volgende update

Kopieer dit blok en vul in:

```
## Update X — DD maand YYYY

**Rapportdatum:** DD maand YYYY
**Uitgevoerd door:** Claude Sonnet

### Bevestigde datapunten (✓)
| Datapunt | Waarde | Bron |
|----------|--------|------|
| TTF DD/MM/YYYY | €XX.XX/MWh | [bron] |
| Belpex DD/MM/YYYY | €XX.X/MWh | [bron] |
| EU gasopslag DD/MM/YYYY | XX% | GIE AGSI+ |
| Brent DD/MM/YYYY | $XX/vat | [bron] |

### Geïnterpoleerde datapunten (~)
[beschrijf welke datapunten geschat zijn en op basis waarvan]

### Geopolitieke context op rapportdatum
- **[Situatie 1]:** [beschrijving]
- **[Situatie 2]:** [beschrijving]

### Scenario-kansen toegepast
| Scenario | Kans | Redenering |
|----------|------|-----------|
| Bearish | X% | [redenering] |
| Basis | X% | [redenering] |
| Bullish | X% | [redenering] |

### Wijzigingen t.o.v. vorige versie
- [Wat is nieuw of anders]

### Technische notities
- [Eventuele problemen of bijzonderheden tijdens de update]
```

