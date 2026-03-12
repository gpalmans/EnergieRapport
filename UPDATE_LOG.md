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

