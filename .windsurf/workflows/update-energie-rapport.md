---
description: Update alle inhoud van het EnergieRapport (JSX + offline.html) op basis van de verzamelde marktdata. Voer EERST collect-energie-data uit. Daarna valideer-en-push.
---

# Vereiste: collect-energie-data moet klaar zijn (alle 4 variabelen ✓)

---

# Stap 1 — Basisdata bijwerken in `src/EnergieRapport.jsx`

1. **`rawData` array**: voeg nieuwe dagprijzen toe, verwijder oudste (houd ~30 handelsdagen). Precies **1x** `note: "Vandaag"` op de rapportdatum.
2. **`forecastBase/Bull/Bear`**: startpunt = laatste ✓ datapunt, einddatum = +6-8 weken, kansen optellen tot 100%.
3. **KPI-blokken**: TTF, Belpex, EU opslag %, Brent + % wijziging vs. vorig ankerpunt.
4. **Alert-banner**: aanpassen aan actuele crisissituatie (of verwijderen als markt rustig).
5. **Header datum**: `MARKTANALYSE — DD MAAND YYYY`
6. **Y-as forecast**: als bullish max > huidige `yMax`, verhoog met 10% marge. Pas aan in JSX (`YAxis domain`) én offline.html (`yMax`).

---

# Stap 2 — Grafiek events

7. Bepaal welke significante marktevenementen vallen **binnen de rawData datumrange** (gebruik bevindingen van collect-energie-data).
8. Voeg per event een `referenceLine` of annotatie toe in de **TTF-grafiek** (en Belpex als relevant):
   - 🔴 Prijsstijgend (blokkade, aanval, onderhoud): `stroke="#ef4444"`, label = naam + datum
   - 🟢 Prijsdalend (IEA-vrijgave, deëscalatie): `stroke="#22c55e"`, label = naam + datum
9. Verwijder events waarvan de datum buiten de huidige data window valt.

---

# Stap 3 — Geopolitieke Crisissituatie

10. Elk item krijgt **2-3 zinnen** (niet meer):
    - Zin 1: wat is het event? (feitelijk, neutraal)
    - Zin 2: direct, aantoonbaar effect op energieprijzen of aanvoer (met cijfers)
    - Zin 3 (optioneel): verwachte evolutie, tijdslijn of risico komende weken

---

# Stap 4 — Belgische Energiemix

11. Leg het **merit-order mechanisme** uit in max 4 begrijpelijke zinnen:
    - Gascentrales als marginale producent bepalen de spotprijs voor **alle** geleverde elektriciteit
    - Voorbeeld: "Als een gascentrale €80/MWh nodig heeft, is dat de marktprijs — ook voor windenergie"
    - Vermeld actueel aandeel gascentrales in de Belgische productiemix (zoek via Elia of Tavily)
    - Consumentenimplicatie: variabele tarieven volgen de spotmarkt; hoge gasprijzen = hogere elektriciteitsfactuur, ook bij groene stroom

---

# Stap 5 — Sleutelfactoren om op te volgen

12. Geef elke factor een ranking + oorzaak + gevolg. Sorteer van meest naar minst impact. Gebruik dit formaat:
    ```
    📌 🔴/🟠/🟡 [Naam]
    Oorzaak: [wat is de factor?]
    Gevolg: [effect op TTF/Belpex, richting, termijn]
    ```
    - 🔴 Kritisch | 🟠 Belangrijk | 🟡 Opvolgen
    - Minimaal 5, maximaal 8 factoren

---

# Stap 6 — Vaste vs. Variabel tariefadvies

13. Horizont: **uitsluitend 12-18 maanden**. Nooit langer. De consument kan kosteloos veranderen, vaak maand-op-maand.
14. **Argumenten voor Variabel** (als TTF bearish/stabiliserend): benoem concrete structurele factoren (LNG-golf, injectieseizoen), historische vergelijking, flexibiliteitsvoordeel, concrete TTF-drempel (bv. "onder €50/MWh").
15. **Argumenten voor Vast** (als TTF bullish/aanhoudend hoog): concrete factoren (fysieke disruption, lange herstelperiode), budgetzekerheid, concrete drempel (bv. ">€60/MWh voor 6+ weken"). Waarschuwing: nooit vastleggen op een piek.
16. Gebruik **actuele TTF-niveaus** uit de verzamelde data — geen generieke clichés.

---

# Stap 7 — Adviesmatrix verificatie

17. Controleer **elke rij**: aanbeveling correct? Tijdshorizon 12-18 mnd? Motivering specifiek? Voorzorgsmaatregel actueel?
18. Pas verouderde rijen aan. Voeg `[bijgewerkt DD/MM]` toe in de motivering bij elke gewijzigde rij.

---

# Stap 8 — Kernboodschap en Praktisch Advies

19. **Kernboodschap** (visueel prominent kleurblok):
    - Verwijst naar **actuele TTF-prijs** + korte termijn (2-5 mnd) én lange termijn (6-18 mnd) verwachting
    - Erkent verhoogd niveau als er een crisis is, relativeer met lange termijn trend
    - Max 3-4 zinnen, begrijpelijk voor de gemiddelde consument

20. **Praktisch Advies** (concreet blok):
    - "Als TTF stabiliseert onder €X/MWh → doe Y"
    - "Als TTF boven €X/MWh blijft voor Z weken → overweeg Y"
    - Maximale contracttermijn: **nooit meer dan 12-18 maanden** expliciet vermelden
    - Afsluiting (verplicht): *"Nooit overhaast tekenen tijdens een nieuwscyclus die voelt als een noodsituatie. Paniek is een slechte raadgever."*

---

# Stap 9 — Bronnen

21. Voeg gebruikte bronnen toe met publicatiedatum. NL eerst (~70%), dan EN voor unieke context. Verwijder bronnen ouder dan 4 weken. Valideer alle URLs.

---

# Stap 10 — `public/offline.html` syncen

22. Sync **identiek** aan JSX: `marketData`, `forecastBase/Bull/Bear`, KPI-blokken, alert, header datum, grafiek events, alle tekstsecties (geopolitiek, energiemix, sleutelfactoren, vaste/variabel, kernboodschap, praktisch advies), bronnen, `yMax`.
23. **Apostrof-controle**: `Lloyd's` → `Lloyd\'s` in JS strings. Een kapotte apostrof crasht de volledige `<script>` block.

---

> Voer na voltooiing `valideer-en-push` uit.
