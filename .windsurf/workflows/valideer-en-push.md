---
description: Voer de volledige kwaliteitschecklist uit, update UPDATE_LOG.md en push naar GitHub. Voer dit als laatste stap uit na collect-energie-data en update-energie-rapport.
---

# ⛔ BLOKKERENDE CHECKLIST — commit alleen als alles ✓ is

**Data volledigheid:**
- [ ] TTF, Belpex, EU Gasopslag, Brent alle 4 ✓ via 2+ bronnen
- [ ] Minimaal 3 datapunten in rawData met ✓
- [ ] TTF + Belpex data loopt t/m de rapportdatum

**Synchronisatie JSX ↔ offline.html (identiek):**
- [ ] KPI-waarden, header datum, rawData/marketData arrays, forecastBase/Bull/Bear
- [ ] Grafiek events (referentielijnen) in beide versies aanwezig
- [ ] Bronvermeldingen identiek
- [ ] **Precies 1x 'Vandaag' label** in beide versies
- [ ] Forecast grafiek Y-as past bij bullisch max + ≥5% marge

**Inhoudelijke kwaliteit:**
- [ ] Geopolitieke crisissituatie: elk item 2-3 zinnen (oorzaak / effect / evolutie)
- [ ] Belgische Energiemix: merit-order gas-elektriciteit koppeling uitgelegd
- [ ] Sleutelfactoren: ranking 🔴/🟠/🟡 + oorzaak + gevolg per factor
- [ ] Vaste vs. Variabel: enkel 12-18 mnd horizon, concrete TTF-drempels vermeld
- [ ] Adviesmatrix: elke rij actueel, `[bijgewerkt DD/MM]` toegevoegd indien gewijzigd
- [ ] Kernboodschap: visueel prominent, actuele TTF, korte én lange termijn verwachting
- [ ] Praktisch advies: concrete drempels, max 18 mnd termijn, anti-paniek afsluiting

**Data cross-check (consistent overal):**
- [ ] TTF consistent in KPI, rawData en geopolitieke tekst
- [ ] Belpex consistent in KPI, rawData en bronnen
- [ ] Brent consistent in KPI en geopolitieke sectie
- [ ] EU gasopslag consistent in KPI en contextsectie

**Technisch:**
- [ ] Geen kapotte apostrofs in offline.html JavaScript
- [ ] Alle bron-URLs geldig, ~70% NL / ~30% EN, max 4 weken oud

---

# Stap 2 — UPDATE_LOG.md bijwerken

1. Voeg nieuwe entry toe aan het **begin** van `UPDATE_LOG.md`:

```markdown
## Update [N] — [DD maand YYYY]

### **Bevestigde Marktdata (✓)**
- **TTF Gas**: €XX.XX/MWh (+/-X.X%) - [bron]
- **Belpex**: €XXX.X/MWh (+/-X.X%) - [bron]
- **EU Gasopslag**: ~XX% - [bron]
- **Brent**: $XXX.XX/vat (+/-X.X%) - [bron]

### **Marktontwikkelingen & Geopolitiek**
- [2-3 bullets met datum + bron]

### **Forecast**: Bearish X% / Basis X% / Bullish X% — [toelichting]

### **Wijzigingen**: [wat is aangepast in JSX/HTML]
```

---

# Stap 3 — Commit en push

// turbo
2. Voer uit vanuit de projectmap:

```bash
git add src/EnergieRapport.jsx public/offline.html UPDATE_LOG.md
git commit -m "update [DD-MM-YYYY]: TTF €XX.XX, Belpex €XXX.X — [één zin context]"
git push origin main
```

3. Cloudflare Pages bouwt automatisch na de push (~1-2 minuten).

---

# Optioneel — Lessons Learned

4. Nieuwe inzichten? Voeg toe aan `CLAUDE.md` onder `## Lessons Learned ([datum])`.
5. Verouderde start-instructie in CLAUDE.md? Pas aan en commit apart.
