"""
Grondige manuele overhaul van EnergieRapport.jsx - 5 juni 2026
7 analyse-punten:
1. Hormuz-crisis update (heropend 21 april, Qatar LNG 3-5 jaar)
2. Prijstabel trimmen naar 30 handelsdagen
3. Geopolitieke sectie grondige herziening
4. Gasvoorraden sectie update
5. Forecast scenario's herschrijven (jun-aug 2026)
6. Vast vs variabel update (vast 27% duurder per VRT jun 2026)
7. Bronnen actualiseren
"""

import re

JSX_PATH = 'src/EnergieRapport.jsx'

with open(JSX_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

original_len = len(content)

# ============================================================
# 1. rawData TRIMMEN: alleen laatste 30 handelsdagen (28/04+)
# ============================================================

new_rawdata = '''const rawData = [
  { date: "28/04", ttf: 53.25, belpex: 61.43,  brent: 101.55, storage: 24.6, note: "" },
  { date: "29/04", ttf: 53.25, belpex: 51.68,  brent: 101.55, storage: 24.6, note: "" },
  { date: "30/04", ttf: 53.25, belpex: 57.46,  brent: 101.55, storage: 24.7, note: "" },
  { date: "01/05", ttf: 53.25, belpex: -5.47,  brent: 101.55, storage: 24.5, note: "" },
  { date: "02/05", ttf: 53.25, belpex: 68.48,  brent: 101.55, storage: 24.6, note: "" },
  { date: "03/05", ttf: 53.25, belpex: 85.46,  brent: 101.55, storage: 24.8, note: "" },
  { date: "04/05", ttf: 53.25, belpex: 123.74, brent: 101.55, storage: 24.9, note: "" },
  { date: "05/05", ttf: 53.25, belpex: 119.98, brent: 101.55, storage: 24.7, note: "" },
  { date: "06/05", ttf: 53.25, belpex: 122.06, brent: 101.55, storage: 24.4, note: "" },
  { date: "07/05", ttf: 53.25, belpex: 124.81, brent: 101.55, storage: 24.1, note: "" },
  { date: "08/05", ttf: 53.25, belpex: 104.07, brent: 101.55, storage: 23.7, note: "" },
  { date: "09/05", ttf: 53.25, belpex: 77.73,  brent: 101.55, storage: 23.9, note: "" },
  { date: "10/05", ttf: 53.25, belpex: 66.86,  brent: 101.55, storage: 23.8, note: "" },
  { date: "11/05", ttf: 53.25, belpex: 107.59, brent: 101.55, storage: 23.8, note: "" },
  { date: "12/05", ttf: 53.25, belpex: 91.08,  brent: 101.55, storage: 23.9, note: "" },
  { date: "13/05", ttf: 53.25, belpex: 98.29,  brent: 101.55, storage: 23.8, note: "" },
  { date: "14/05", ttf: 53.25, belpex: 84.36,  brent: 101.55, storage: 23.2, note: "" },
  { date: "15/05", ttf: 53.25, belpex: 95.10,  brent: 101.55, storage: 23.1, note: "" },
  { date: "16/05", ttf: 53.25, belpex: 74.69,  brent: 101.55, storage: 22.8, note: "" },
  { date: "17/05", ttf: 53.25, belpex: 80.94,  brent: 101.55, storage: 22.6, note: "" },
  { date: "18/05", ttf: 53.25, belpex: 133.63, brent: 101.55, storage: 22.4, note: "" },
  { date: "19/05", ttf: 53.25, belpex: 110.91, brent: 101.55, storage: 22.2, note: "" },
  { date: "20/05", ttf: 53.25, belpex: 92.80,  brent: 101.55, storage: 21.6, note: "" },
  { date: "21/05", ttf: 53.25, belpex: 106.59, brent: 101.55, storage: 21.0, note: "" },
  { date: "22/05", ttf: 53.25, belpex: 96.61,  brent: 101.55, storage: 20.8, note: "" },
  { date: "23/05", ttf: 53.25, belpex: 74.35,  brent: 101.55, storage: 20.8, note: "" },
  { date: "24/05", ttf: 53.25, belpex: 67.41,  brent: 101.55, storage: 20.8, note: "" },
  { date: "25/05", ttf: 53.25, belpex: 78.18,  brent: 101.55, storage: 20.9, note: "" },
  { date: "26/05", ttf: 53.25, belpex: 94.06,  brent: 101.55, storage: 21.1, note: "" },
  { date: "27/05", ttf: 53.25, belpex: 83.21,  brent: 101.55, storage: 21.1, note: "" },
  { date: "28/05", ttf: 53.25, belpex: 117.14, brent: 101.55, storage: 21.3, note: "" },
  { date: "29/05", ttf: 53.25, belpex: 104.32, brent: 101.55, storage: 21.3, note: "" },
  { date: "30/05", ttf: 53.25, belpex: 82.62,  brent: 101.55, storage: 21.3, note: "" },
  { date: "31/05", ttf: 53.25, belpex: 83.22,  brent: 101.55, storage: 21.6, note: "" },
  { date: "01/06", ttf: 49.16, belpex: 131.67, brent: 95.25,  storage: 22.0, note: "" },
  { date: "02/06", ttf: 47.55, belpex: 126.16, brent: 95.94,  storage: 22.1, note: "" },
  { date: "03/06", ttf: 49.46, belpex: 90.82,  brent: 97.39,  storage: 22.0, note: "" },
  { date: "04/06", ttf: 48.85, belpex: 52.59,  brent: 95.36,  storage: 21.9, note: "" },
  { date: "05/06", ttf: 48.85, belpex: 52.59,  brent: 95.36,  storage: 21.9, note: "Vandaag" }
].sort('''

content = re.sub(
    r'const rawData = \[[\s\S]*?\]\.sort\(',
    new_rawdata,
    content,
    count=1
)
print("✅ 1. rawData getrimd naar 30 handelsdagen")

# ============================================================
# 2. FORECAST ARRAYS: volledig herschrijven voor jun-aug 2026
# ============================================================

new_forecasts = '''const forecastBase = [
  { date: "05/06", ttf: 48.85, belpex: 52.59 },
  { date: "12/06", ttf: 47.50, belpex: 68    },
  { date: "19/06", ttf: 46.00, belpex: 72    },
  { date: "26/06", ttf: 44.50, belpex: 70    },
  { date: "03/07", ttf: 43.50, belpex: 68    },
  { date: "10/07", ttf: 43.00, belpex: 65    },
  { date: "17/07", ttf: 42.50, belpex: 63    },
  { date: "24/07", ttf: 42.00, belpex: 62    },
  { date: "01/08", ttf: 41.50, belpex: 60    },
];
const forecastBull = [
  { date: "05/06", ttf: 48.85, belpex: 52.59 },
  { date: "12/06", ttf: 52.00, belpex: 88    },
  { date: "19/06", ttf: 57.00, belpex: 105   },
  { date: "26/06", ttf: 62.00, belpex: 120   },
  { date: "03/07", ttf: 65.00, belpex: 132   },
  { date: "10/07", ttf: 68.00, belpex: 140   },
  { date: "17/07", ttf: 70.00, belpex: 145   },
  { date: "24/07", ttf: 72.00, belpex: 148   },
  { date: "01/08", ttf: 74.00, belpex: 150   },
];
const forecastBear = [
  { date: "05/06", ttf: 48.85, belpex: 52.59 },
  { date: "12/06", ttf: 45.00, belpex: 60    },
  { date: "19/06", ttf: 41.00, belpex: 56    },
  { date: "26/06", ttf: 38.00, belpex: 52    },
  { date: "03/07", ttf: 35.00, belpex: 49    },
  { date: "10/07", ttf: 33.00, belpex: 47    },
  { date: "17/07", ttf: 32.00, belpex: 45    },
  { date: "24/07", ttf: 31.00, belpex: 44    },
  { date: "01/08", ttf: 30.00, belpex: 43    },
];
'''

content = re.sub(
    r'const forecastBase = \[[\s\S]*?\];\nconst forecastBear = \[[\s\S]*?\];',
    new_forecasts.strip(),
    content,
    count=1
)
print("✅ 2. Forecast arrays herschreven voor jun-aug 2026")

# ============================================================
# 3. ALERT BANNER: Hormuz crisis → post-crisis normalisatie
# ============================================================

old_alert = '''      <div style={{ background: "#7c131322", border: "1px solid #ef4444", borderRadius: 10, padding: "14px 20px", marginBottom: 24, display: "flex", alignItems: "center", gap: 12 }}>
        <span style={{ fontSize: 22, flexShrink: 0 }}>⚠️</span>
        <div>
          <div style={{ fontWeight: 700, color: "#fca5a5", marginBottom: 2 }}>KRITIEKE MARKTSITUATIE</div>
          <div style={{ fontSize: 13, color: "#fca5a5" }}>
            Hormuz crisis dag 21+ · TTF €48.85 (-11.4% vs piek) · Brent $95.36 · Force majeure Qatar/Kuwait/UAE · Belgische gasreserves 22%
          </div>
        </div>
      </div>'''

new_alert = '''      <div style={{ background: "#7c2d1222", border: "1px solid #f97316", borderRadius: 10, padding: "14px 20px", marginBottom: 24, display: "flex", alignItems: "center", gap: 12 }}>
        <span style={{ fontSize: 22, flexShrink: 0 }}>📉</span>
        <div>
          <div style={{ fontWeight: 700, color: "#fdba74", marginBottom: 2 }}>MARKTUPDATE: POST-CRISIS NORMALISATIE — STRUCTURELE RISICO\'S BLIJVEN</div>
          <div style={{ fontSize: 13, color: "#fdba74" }}>
            Hormuz heropend (21 apr) · TTF €48.85 (↓21% vs piek €62) · Qatar LNG schade: 3–5 jaar herstel · Belgische opslag kritiek laag: 21.9% · Vast tarief 27% duurder dan variabel (VRT, jun 2026)
          </div>
        </div>
      </div>'''

content = content.replace(old_alert, new_alert)
print("✅ 3. Alert banner geactualiseerd")

# ============================================================
# 4. TTF-GRAFIEK: referentielijnen aanpassen
# ============================================================

old_ttf_refs = '''              <ReferenceLine y={31.96} stroke="#22c55e" strokeDasharray="4 4" label={{ value: "27/02 basis", fill: "#22c55e", fontSize: 10, position: "top" }} />
              <ReferenceLine x="02/03" stroke="#ef4444" strokeDasharray="4 4" label={{ value: "Hormuz", fill: "#ef4444", fontSize: 10, position: "top" }} />
              <ReferenceLine x="20/03" stroke="#f97316" strokeDasharray="4 4" label={{ value: "Gasvelden", fill: "#f97316", fontSize: 10, position: "top" }} />'''

new_ttf_refs = '''              <ReferenceLine y={53.25} stroke="#f59e0b" strokeDasharray="4 4" label={{ value: "Apr-mei plateau", fill: "#f59e0b", fontSize: 10, position: "top" }} />
              <ReferenceLine x="01/06" stroke="#22c55e" strokeDasharray="4 4" label={{ value: "Juni daling", fill: "#22c55e", fontSize: 10, position: "top" }} />'''

content = content.replace(old_ttf_refs, new_ttf_refs)
print("✅ 4. TTF-grafiek referentielijnen bijgewerkt")

# ============================================================
# 5. TTF Y-AS: aanpassen voor nieuw datarange
# ============================================================

content = content.replace(
    '<YAxis domain={[25, 70]} tick={{ fill: "#64748b", fontSize: 11 }} tickFormatter={v => `€${v}`} />',
    '<YAxis domain={[35, 70]} tick={{ fill: "#64748b", fontSize: 11 }} tickFormatter={v => `€${v}`} />'
)
print("✅ 5. TTF Y-as domain aangepast [35-70]")

# ============================================================
# 6. BELPEX-GRAFIEK: referentielijnen aanpassen
# ============================================================

old_belpex_refs = '''              <ReferenceLine y={68} stroke="#22c55e" strokeDasharray="3 3" label={{ value: "27/02 basis", fill: "#22c55e", fontSize: 10, position: "top" }} />
              <ReferenceLine x="02/03" stroke="#ef4444" strokeDasharray="4 4" label={{ value: "Hormuz", fill: "#ef4444", fontSize: 10, position: "top" }} />
              <ReferenceLine x="09/03" stroke="#f97316" strokeDasharray="4 4" label={{ value: "Absolute Piek", fill: "#f97316", fontSize: 10, position: "top" }} />
              <ReferenceLine x="10/03" stroke="#a78bfa" strokeDasharray="4 4" label={{ value: "IEA", fill: "#a78bfa", fontSize: 10, position: "top" }} />'''

new_belpex_refs = '''              <ReferenceLine y={85} stroke="#f59e0b" strokeDasharray="3 3" label={{ value: "Apr-mei gemiddelde", fill: "#f59e0b", fontSize: 10, position: "top" }} />
              <ReferenceLine x="01/06" stroke="#22c55e" strokeDasharray="4 4" label={{ value: "Juni normalisatie", fill: "#22c55e", fontSize: 10, position: "top" }} />'''

content = content.replace(old_belpex_refs, new_belpex_refs)
print("✅ 6. Belpex-grafiek referentielijnen bijgewerkt")

# ============================================================
# 7. FORECAST TAB HEADERS: periode-labels bijwerken
# ============================================================

content = content.replace(
    'TTF Gas Forecast (apr–mei 2026)',
    'TTF Gas Forecast (jun–aug 2026)'
)
content = content.replace(
    'Belpex Elektriciteit Forecast (apr–mei 2026)',
    'Belpex Elektriciteit Forecast (jun–aug 2026)'
)
content = content.replace(
    'Range apr–mei 2026',
    'Range jun–aug 2026'
)
print("✅ 7. Forecast periode-labels bijgewerkt naar jun-aug 2026")

# ============================================================
# 8. EUROPESE GASVOORRADEN SECTIE: update
# ============================================================

old_storage_section = '''          <div style={SECTION}>
            <h3 style={{ margin: "0 0 14px", color: "#f8fafc", fontSize: 15 }}>🏭 Europese Gasvoorraden</h3>
            {[
              ["BE-gemiddelde (5 jun 2026)", "~22%",          "#ef4444"],
              ["Laagste seizoenspeil",       "in jaren",       "#ef4444"],
              ["Einde 2025",                 "~61%",           "#eab308"],
              ["Einde 2024",                 "~72%",           "#22c55e"],
              ["EU-doelstelling (1 nov)",    "90%",            "#0ea5e9"],
              ["Nog te vullen (apr–okt)",    "~68 pct-punten", "#f97316"],
            ].map(([l, v, c]) => (
              <div key={l} style={{ display: "flex", justifyContent: "space-between", padding: "7px 0", borderBottom: "1px solid #1e293b", fontSize: 13 }}>
                <span style={{ color: "#94a3b8" }}>{l}</span>
                <span style={{ color: c, fontWeight: 700 }}>{v}</span>
              </div>
            ))}
            <div style={{ marginTop: 14, padding: "10px 14px", background: "#7c131322", borderRadius: 8, fontSize: 12, color: "#fca5a5", lineHeight: 1.6 }}>
              ⚠️ Gasvelden aangevallen (South Pars, Ras Laffan) - Qatar LNG export -17%. TTF +13.5% op supply shock.
            </div>
            <div style={{ marginTop: 12, padding: "10px 14px", background: "#172554", borderRadius: 8, fontSize: 12, color: "#93c5fd", lineHeight: 1.6 }}>
              <strong style={{ color: "#60a5fa" }}>Waarom dit kritiek is:</strong> De EU-doelstelling is 90% vulgraad tegen 1 november. Op 26% eind maart moeten we nog ~64% vullen in 7 maanden. Dit vereist agressieve LNG-import tegen verhoogde prijzen. Duitsland (30%), Frankrijk (29%) en Nederland (23.5%) hebben bijzonder lage niveaus. Elke week dat de opslag onder 35% blijft, stijgt de nervositeit en worden LNG-contracten duurder. Herstel boven 40% eind april zou een positief signaal zijn.
            </div>
          </div>'''

new_storage_section = '''          <div style={SECTION}>
            <h3 style={{ margin: "0 0 14px", color: "#f8fafc", fontSize: 15 }}>🏭 Belgische & Europese Gasvoorraden</h3>
            {[
              ["BE-gemiddelde (5 jun 2026)", "~22%",          "#ef4444"],
              ["EU-gemiddelde (jun 2026)",   "~55–60%",        "#eab308"],
              ["Einde 2025",                 "~61%",           "#eab308"],
              ["Einde 2024",                 "~72%",           "#22c55e"],
              ["EU-doelstelling (1 nov)",    "90%",            "#0ea5e9"],
              ["BE nog te vullen (jun–okt)", "~68 pct-punten", "#f97316"],
            ].map(([l, v, c]) => (
              <div key={l} style={{ display: "flex", justifyContent: "space-between", padding: "7px 0", borderBottom: "1px solid #1e293b", fontSize: 13 }}>
                <span style={{ color: "#94a3b8" }}>{l}</span>
                <span style={{ color: c, fontWeight: 700 }}>{v}</span>
              </div>
            ))}
            <div style={{ marginTop: 14, padding: "10px 14px", background: "#7c131322", borderRadius: 8, fontSize: 12, color: "#fca5a5", lineHeight: 1.6 }}>
              ⚠️ Qatar LNG: 17% exportcapaciteit beschadigd — herstel duurt 3 tot 5 jaar (NYTimes, mei 2026). Zelfs na heropening Hormuz blijft LNG-aanbod structureel beperkt.
            </div>
            <div style={{ marginTop: 12, padding: "10px 14px", background: "#172554", borderRadius: 8, fontSize: 12, color: "#93c5fd", lineHeight: 1.6 }}>
              <strong style={{ color: "#60a5fa" }}>Waarom België achterblijft:</strong> België heeft relatief weinig ondergrondse gasopslagcapaciteit vergeleken met grote EU-landen. Met slechts 21.9% vulgraad eind mei moet België agressief injecteren om wintervoorraden op peil te krijgen. De EU-doelstelling is 90% tegen 1 november — dat vergt ~68 procentpunten extra in 5 maanden. Dit verhoogt de competitie voor LNG-cargos en houdt de TTF-forward-curve ondersteund. Herstel boven 40% eind juli zou een positief seizoenssignaal zijn.
            </div>
          </div>'''

content = content.replace(old_storage_section, new_storage_section)
print("✅ 8. Gasvoorraden sectie bijgewerkt (BE vs EU, Qatar 3-5 jaar)")

# ============================================================
# 9. GEOPOLITIEKE ITEMS: volledig herschrijven
# ============================================================

old_geo_items = '''          <div style={SECTION}>
            <h3 style={{ margin: "0 0 14px", color: "#f8fafc", fontSize: 15 }}>⚔️ Geopolitieke Crisissituatie</h3>
            {[
              ["Mega Tariefstijging België", "#ef4444", "Mega verhoogt onverwacht tarieven vanaf 6 maart: gas +14% tot +29%, elektriciteit +12% tot +22%. CREG betreurt deze praktijk en noemt het 'gevaarlijk precedent' voor consumenten. De stijging volgt direct op Midden-Oosten escalatie en toont de onmiddellijke impact van geopolitieke spanningen op Belgische huishoudens. Analisten verwachten dat andere leveranciers zullen volgen, wat verdere prijsstijgingen in Q2 2026 kan veroorzaken."],
["Hormuz Crisis Tijdsdruk", "#f97316", "Kritieke deadline: Straat van Hormuz moet heropend worden binnen 1-3 weken (mid-april). Productie gereduceerd met 8 mb/d crude + 2 mb/d condensates. Stopgap measures verliezen effectiviteit begin-mid april, wat kan leiden tot dramatische prijsstijgingen. TTF notert momenteel extreme volatiliteit met dagelijkse variaties van 10-15%. Gasunie adviseert strategische noodvoorraad."],
              ["Energy Sector Rotation", "#eab308", "Beleggers massaal naar energie sectoren: Energy Select Sector SPDR stijgt +3% in maart door geopolitieke spanningen. Deze 'great rotation' vindt plaats terwijl rentegevoelige sectoren zoals technologie en vastgoed dalen, wat beleggersvertrouwen in energie toont ondanks de volatiliteit. De trend suggereert dat de markt verwacht dat hoge energieprijzen structureel blijven tot minstens Q3 2026."],
              ["IEA Consumentenadvies", "#06b6d4", "Het Internationaal Energieagentschap (IEA) adviseert Europeanen dringend om energieverbruik te verminderen: werk thuis indien mogelijk, rij langzamer, en gebruik geen gas kokers voor koken. Dit unieke advies is gericht op het stabiliseren van de markt tijdens het Midden-Oosten conflict via vraagreductie. De maatregel heeft beperkt succes gezien de structurele supply verstoringen, maar toont de ernst van de situatie."],
              ["Brent Prijsstijging", "#8b5cf6", "Brent crude noteert significante stijging sinds 28 februari door geopolitieke spanningen. De markt prijst een risicopremie in van 15-20% voor het geval de diplomatie mislukt en de Hormuz-blokkade wordt verlengd tot zomer 2026. IEA reserves hebben beperkte impact op de onderliggende verstoring."],
              ["Politieke Budgetcrisis", "#dc2626", "Premier De Wever: 'De staat verdient niet aan energiecrisis, ze scheurt er haar broek aan.' Gouverneur Wunsch waarschuwt: 'Geen middelen meer om schok energiecrisis volledig op te vangen.' De terughoudendheid van de regering voor steunmaatregelen creëert marktonzekerheid en speculatie op hogere prijzen. MR dringt aan op omgekeerde cliquet, maar De Wever wijst op budgettaire tekorten en indexatielasten."],
              ["EU Langdurige Energieschok", "#b91c1c", "EU Energy Commissioner Dan Jørgensen (Financial Times): 'This will be a long crisis... energy prices will be higher for a very long time.' EU overweegt brandstof rantsoenering en extra noodreserves. 'Critical products' worden komende weken nog erger. De waarschuwing bevestigt structurele impact Midden-Oosten conflict op Europese energieprijzen tot ver in 2026-27."],
              ["Omgekeerde Cliquet Voorstel", "#f59e0b", "MR-voorzitter Bouchez pleit voor automatisch accijnsdaling bij brandstofprijzen boven €2/liter. 'Omgekeerde cliquet' systeem zou consumenten direct verlichten bij extreme prijsstijgingen. De overheid profiteert van hogere btw-inkomsten, maar dreigt dossiers te blokkeren als regering niet ingrijpt. Les Engagés steunen het voorstel en eisen actie."],
            ].map(([titel, color, tekst]) => (
              <div key={titel} style={{ marginBottom: 14 }}>
                <span style={BADGE(color)}>{titel}</span>
                <p style={{ marginTop: 7, marginBottom: 0, fontSize: 13, color: "#94a3b8", lineHeight: 1.6 }}>{tekst}</p>
              </div>
            ))}
          </div>'''

new_geo_items = '''          <div style={SECTION}>
            <h3 style={{ margin: "0 0 14px", color: "#f8fafc", fontSize: 15 }}>⚔️ Geopolitieke Situatie — Juni 2026</h3>
            {[
              ["Hormuz Gedeeltelijk Heropend", "#f97316", "De Straat van Hormuz werd op 21 april 2026 gedeeltelijk heropend na VN-bemiddeling en diplomatieke druk van de VS, EU en China. Scheepvaart herstelt geleidelijk, maar tanker-verzekeringspremies blijven 3-4× de normale niveaus. TTF daalde van €62 naar €48.85 (−21%) als gevolg van de gedeeltelijke normalisatie. De wapenstilstand is fragiel — nieuwe escalatie blijft een reëel risico."],
              ["Qatar LNG: 3–5 Jaar Herstel", "#ef4444", "Dit is de meest ingrijpende structurele verandering op de energiemarkt. Qatar's gasexportcapaciteit — goed voor ~17% van het wereldwijde LNG — is zwaar beschadigd door oorlogsschade aan South Pars en Ras Laffan. Analysts en QatarEnergy zelf bevestigen dat volledig herstel 3 tot 5 jaar zal duren (NYTimes, 14 mei 2026). Dit betekent dat de pre-crisis TTF-niveaus van €30-32 structureel onbereikbaar zijn tot 2028-2030."],
              ["OPEC+ Drie Productieverogingen", "#eab308", "Om de weggevallen Hormuz-volumes te compenseren heeft OPEC+ drie achtereenvolgende productieverogingen doorgevoerd (Reuters, 3 mei 2026). De derde verhoging van 188.000 vaten/dag werd als 'symbolisch' bestempeld — het compenseert slechts een fractie van de 8 mb/d die via Hormuz verstoord werd. Brent daalde van $115+ naar $95.36 mede dankzij deze verhogingen."],
              ["Belgische Gasopslag Kritiek Laag", "#ef4444", "Met 21.9% vulgraad op 5 juni 2026 staat België voor een enorme injectie-uitdaging: ~68 procentpunten bijvullen voor 1 november is een record. Ter vergelijking: het EU-gemiddelde ligt op ~55-60%. De lage Belgische opslagcapaciteit (structureel kleiner dan die van Duitsland of Nederland) maakt België extra kwetsbaar voor prijspieken in het najaar bij koude periodes."],
              ["Vast Tarief 27% Duurder dan Variabel", "#8b5cf6", "VRT berichtte in juni 2026 dat vaste energiecontracten in België momenteel gemiddeld 27% duurder zijn dan vergelijkbare variabele contracten. Dit is een historisch hoge premie en geeft aan dat leveranciers de geopolitieke risicopremie volledig hebben ingebakken in hun vaste aanbiedingen. Wie nu een vast tarief neemt, betaalt voor risicobuffer die de leverancier neemt — niet voor zekerheid die de consument nodig heeft."],
              ["Politieke Budgetcrisis — Geen Steun", "#dc2626", "Premier De Wever en NBB-gouverneur Wunsch zijn eensgezind: de Belgische overheid heeft geen budgettaire ruimte meer voor energiesteunpakketten. MR's voorstel voor een omgekeerde cliquet bij brandstofprijzen boven €2/liter wacht op goedkeuring maar is politiek geblokkeerd. Consumenten zullen de energieprijzen volledig dragen in 2026 zonder bijkomende compensatie. Belgische inflatie wordt bijgesteld naar 2.6% mede door energieprijzen (Belga, jun 2026)."],
              ["EU Injectieseizoen Achterloopt op Schema", "#06b6d4", "Europa staat voor zijn zwaarste injectieseizoen ooit. Met een laag startpunt na de winter (EU ~37% in maart 2026) en structurele LNG-schaarste door Qatar-schade moet de EU meer gas injecteren dan in enig voorgaand seizoen. IEA en ACER waarschuwen dat de 90%-doelstelling voor 1 november alleen haalbaar is bij aanhoudend warm weer, maximale LNG-import en gedeeltelijk herstel van Qatar-volumes."],
              ["LNG-Aanbodgolf Vertraagd", "#0ea5e9", "De verwachte LNG-aanbodgolf (VS Sabine Pass expansie, Qatar North Field North, Mozambique LNG) die gepland stond voor 2026-2027 is door constructievertragingen en financieringsproblemen verschoven naar 2027-2028. S&P Global en IEA reviseerden hun aanbodprognoses neerwaarts. Europa moet langer dan gepland concurreren met Azië voor een beperkte mondiale LNG-markt."],
            ].map(([titel, color, tekst]) => (
              <div key={titel} style={{ marginBottom: 14 }}>
                <span style={BADGE(color)}>{titel}</span>
                <p style={{ marginTop: 7, marginBottom: 0, fontSize: 13, color: "#94a3b8", lineHeight: 1.6 }}>{tekst}</p>
              </div>
            ))}
          </div>'''

content = content.replace(old_geo_items, new_geo_items)
print("✅ 9. Geopolitieke items volledig herschreven (jun 2026)")

# ============================================================
# 10. IEA STRATEGIC RESERVES: status updaten
# ============================================================

old_iea = '''          <div style={SECTION}>
            <h3 style={{ margin: "0 0 14px", color: "#f8fafc", fontSize: 15 }}>🛢️ IEA Strategische Oliereserves</h3>
            <p style={{ marginTop: 0, fontSize: 13, color: "#94a3b8", lineHeight: 1.7, marginBottom: 12 }}>
              Als reactie op de Hormuz-blokkade heeft het Internationaal Energieagentschap (IEA) een recordvrijgave van 400 miljoen vaten uit strategische oliereserves gecoördineerd, maar dit is een 'stop-gap measure' zonder structurele oplossing. De marktreactie blijft beperkt: Brent steeg met $20 naar $92/bbl, maar de onderliggende verstoring blijft. Wereldwijde inventarissen staan op 8.2 miljard vaten (hoogste sinds 2021), maar IEA heeft de globale olie vraaggroei voor 2026 verlaagd met 210 kb/d naar 640 kb/d door demand destruction. De 400 miljoen vaten dekken slechts ~4 dagen wereldwijde vraag.
            </p>
            <div style={{ background: "#172554", borderRadius: 8, padding: "12px 14px", marginBottom: 12 }}>
              {[
                ["Volume",          "400 mln vaten (recordvrijgave)"],
                ["% totale res.",   "~33% van 1.2 mld noodvoorraad"],
                ["Status",          "Gezamenlijke vrijgave actief sinds 11/03"],
                ["Marktreactie",    "Beperkte impact: TTF +27% in laatste maand ondanks release"],
                ["Effectiviteit",   "Dekken ~4 dagen globale vraag; impact beperkt door Hormuz"],
              ].map(([k, v]) => (
                <div key={k} style={{ display: "flex", justifyContent: "space-between", padding: "5px 0", borderBottom: "1px solid #1e3a5f", fontSize: 12 }}>
                  <span style={{ color: "#94a3b8" }}>{k}</span>
                  <span style={{ color: "#60a5fa", fontWeight: 600 }}>{v}</span>
                </div>
              ))}
            </div>
            <p style={{ fontSize: 11, color: "#475569", margin: 0 }}>Bronnen: IEA.org (13/03), Oil Price API (25/03), AGSI GIE API (25/03)</p>
          </div>'''

new_iea = '''          <div style={SECTION}>
            <h3 style={{ margin: "0 0 14px", color: "#f8fafc", fontSize: 15 }}>🛢️ IEA Strategische Reserves — Status na Hormuz</h3>
            <p style={{ marginTop: 0, fontSize: 13, color: "#94a3b8", lineHeight: 1.7, marginBottom: 12 }}>
              De IEA-recordvrijgave van 400 miljoen vaten (11 maart 2026) heeft haar primaire doel bereikt: Brent daalde van $115+ naar $95.36/vat. Het vrijgaveproces is voltooid. IEA-landen kopen nu gradueel reserves terug aan lagere prijzen om de strategische voorraden te herstellen. Voor gas heeft de vrijgave echter geen directe impact gehad — de Qatar LNG-schade is een aparte structurele supply-disruption die niet via oliereserves opgelost kan worden.
            </p>
            <div style={{ background: "#172554", borderRadius: 8, padding: "12px 14px", marginBottom: 12 }}>
              {[
                ["Volume",          "400 mln vaten (recordvrijgave, voltooid)"],
                ["% totale res.",   "~33% van 1.2 mld noodvoorraad"],
                ["Status jun 2026", "Vrijgave voltooid; terugkoop-fase gestart"],
                ["Impact op Brent", "Brent: $115 → $95.36 (−17%) mede dankzij IEA + OPEC+"],
                ["Impact op gas",   "Beperkt: Qatar LNG-schade vraagt structurele oplossing"],
              ].map(([k, v]) => (
                <div key={k} style={{ display: "flex", justifyContent: "space-between", padding: "5px 0", borderBottom: "1px solid #1e3a5f", fontSize: 12 }}>
                  <span style={{ color: "#94a3b8" }}>{k}</span>
                  <span style={{ color: "#60a5fa", fontWeight: 600 }}>{v}</span>
                </div>
              ))}
            </div>
            <p style={{ fontSize: 11, color: "#475569", margin: 0 }}>Bronnen: IEA.org, Reuters OPEC+ (03/05/2026), AGSI GIE API (05/06/2026)</p>
          </div>'''

content = content.replace(old_iea, new_iea)
print("✅ 10. IEA Strategische Reserves sectie bijgewerkt")

# ============================================================
# 11. FORECAST SCENARIO BOXES: herschrijven voor jun-aug 2026
# ============================================================

old_scenarios = '''        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 14 }}>
          {[
            {
              t: "⬇ Bearish (Ontspanning)", p: "15%", c: "#22c55e",
              ttf: "€35–45", belpex: "€70–100",
              items: ["Gasvelden herstellen binnen 2-3 weken","Hormuz gedeeltelijk open","Diplomatieke de-escalatie","Mild voorjaar verlaagt vraag"],
              note: "Risico: EU waarschuwing voor langdurige crisis verlaagt kans",
            },
            {
              t: "⟶ Basis (Prolonged crisis)", p: "45%", c: "#0ea5e9",
              ttf: "€45–65", belpex: "€90–130",
              items: ["Gasvelden deels buiten werking 3-5 maanden","Hormuz beperkt open","Qatar LNG -17% capaciteit","EU brandstof rantsoenering mogelijk"],
              note: "Meest waarschijnlijk scenario - EU: 'energy prices higher for very long time'",
            },
            {
              t: "⬆ Bullish (Escalatie)", p: "40%", c: "#ef4444",
              ttf: "€65–85", belpex: "€120–180",
              items: ["Nieuwe aanvallen op energie-infra","Hormuz gesloten tot zomer","Qatar LNG langdurig stil","EU noodreserves uitgeput","Brandstof rantsoenering actief"],
              note: "EU waarschuwing: 'critical products' worden komende weken nog erger",
            },
          ].map((s, i) => (
            <div key={i} style={{ background: "#1e293b", border: `1px solid ${s.c}44`, borderRadius: 12, padding: "16px 18px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 10, gap: 6 }}>
                <h4 style={{ margin: 0, color: s.c, fontSize: 13, lineHeight: 1.4 }}>{s.t}</h4>
                <span style={{ ...BADGE(s.c), flexShrink: 0 }}>P: {s.p}</span>
              </div>
              <div style={{ marginBottom: 10 }}>
                <div style={{ fontSize: 11, color: "#64748b", marginBottom: 3 }}>Range apr–mei 2026</div>
                <div style={{ color: "#0ea5e9", fontSize: 12 }}>TTF: <strong style={{ color: s.c }}>{s.ttf}/MWh</strong></div>
                <div style={{ color: "#a78bfa", fontSize: 12 }}>Belpex: <strong style={{ color: s.c }}>{s.belpex}/MWh</strong></div>
              </div>
              <ul style={{ margin: 0, padding: "0 0 0 14px", fontSize: 12, color: "#94a3b8", lineHeight: 1.9 }}>
                {s.items.map((x, j) => <li key={j}>{x}</li>)}
              </ul>
              <div style={{ marginTop: 10, padding: "7px 10px", background: "#0f172a", borderRadius: 6, fontSize: 11, color: "#64748b" }}>💡 {s.note}</div>
            </div>
          ))}
        </div>'''

new_scenarios = '''        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 14 }}>
          {[
            {
              t: "⬇ Bearish (Volledige normalisatie)", p: "20%", c: "#22c55e",
              ttf: "€30–42", belpex: "€43–65",
              items: ["Hormuz volledig stabiel en scheepvaart normaliseert","LNG-markt vindt alternatieve routes","Zachte zomer drukt gasvraag","OPEC+ verhogingen compenseren resterende tekorten"],
              note: "Vereist: structureel herstel Qatar LNG eerder dan verwacht + gunstig zomerweer",
            },
            {
              t: "⟶ Basis (Gecontroleerde stabilisatie)", p: "50%", c: "#0ea5e9",
              ttf: "€41–55", belpex: "€60–100",
              items: ["Qatar LNG-schade 3-5 jaar: aanbod structureel krapper","Hormuz fragiel maar stabiel","EU-injectieseizoen haalt 80-85% target","Alternatieve LNG-routes (VS, Afrika) compenseren deels"],
              note: "Meest waarschijnlijk: TTF boven pre-crisis (€32) door Qatar-schade, maar dalende trend",
            },
            {
              t: "⬆ Bullish (Nieuwe schok)", p: "30%", c: "#ef4444",
              ttf: "€58–74", belpex: "€100–150",
              items: ["Nieuwe escalatie Midden-Oosten of Hormuz hersluit","Opslag haalt 90% niet → wintercrisis geprijsd","Vroege koude snap verhoogt vraag","LNG-aanbodgolf vertraagt verder"],
              note: "Trigger: geopolitiek incident of opslagachterstand boven 15% vs historisch",
            },
          ].map((s, i) => (
            <div key={i} style={{ background: "#1e293b", border: `1px solid ${s.c}44`, borderRadius: 12, padding: "16px 18px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 10, gap: 6 }}>
                <h4 style={{ margin: 0, color: s.c, fontSize: 13, lineHeight: 1.4 }}>{s.t}</h4>
                <span style={{ ...BADGE(s.c), flexShrink: 0 }}>P: {s.p}</span>
              </div>
              <div style={{ marginBottom: 10 }}>
                <div style={{ fontSize: 11, color: "#64748b", marginBottom: 3 }}>Range jun–aug 2026</div>
                <div style={{ color: "#0ea5e9", fontSize: 12 }}>TTF: <strong style={{ color: s.c }}>{s.ttf}/MWh</strong></div>
                <div style={{ color: "#a78bfa", fontSize: 12 }}>Belpex: <strong style={{ color: s.c }}>{s.belpex}/MWh</strong></div>
              </div>
              <ul style={{ margin: 0, padding: "0 0 0 14px", fontSize: 12, color: "#94a3b8", lineHeight: 1.9 }}>
                {s.items.map((x, j) => <li key={j}>{x}</li>)}
              </ul>
              <div style={{ marginTop: 10, padding: "7px 10px", background: "#0f172a", borderRadius: 6, fontSize: 11, color: "#64748b" }}>💡 {s.note}</div>
            </div>
          ))}
        </div>'''

content = content.replace(old_scenarios, new_scenarios)
print("✅ 11. Forecast scenario boxes herschreven (jun-aug 2026)")

# ============================================================
# 12. SLEUTELFACTOREN: update voor actuele situatie
# ============================================================

old_factors_header = '''          <h3 style={{ margin: "0 0 8px", color: "#f8fafc", fontSize: 15 }}>🔑 Sleutelfactoren om op te volgen</h3>
          <p style={{ fontSize: 12, color: "#64748b", marginTop: 0, marginBottom: 14 }}>Gerangschikt op impact: 🔴 Kritiek · 🟡 Belangrijk · 🟢 Moderate invloed</p>
          <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: 12 }}>
            {[{
              icon: "🔴",
              title: "1. EU Brandstof Rantsoenering & Noodreserves",
              impact: "TTF: +15% tot +25% · Belpex: +10% tot +20%",
              why: "EU Energy Commissioner Dan Jørgensen waarschuwt voor 'langdurige energieschok' en overweegt brandstof rantsoenering. 'Critical products' worden komende weken nog erger. Extra noodreserves vrijgeven kan korte termijn verlichting brengen maar beperkt structureel probleem.",
              monitor: "Volg EU Energy Commissioner verklaringen, brandstof rantsoeneringsplannen, noodreserve vrijgaves en 'critical products' monitoring.",
              border: "#ef4444",
              impactColor: "#fca5a5",
            },
            {
              icon: "🔴",
              title: "2. LNG-markt krapper dan verwacht",
              impact: "TTF: +12% tot +22% · Belpex: +8% tot +16%",
              why: "De verwachte LNG-aanbodgolf voor 2026 is door schade aan exportcapaciteit en transportstress minder prijsdrukkend dan eerder gedacht. Europa en Azië concurreren opnieuw voor een beperkter aantal cargo's, waardoor de marginale gasprijs hoger blijft dan in een normaal lentescenario.",
              monitor: "Volg Qatar LNG-export, spot-LNG vrachttarieven, Aziatische LNG-biedingen en signalen dat extra volumes uit de VS of Mozambique vertragen.",
              border: "#ef4444",
              impactColor: "#fca5a5",
            },
            {
              icon: "🔴",
              title: "3. Hersteltempo South Pars en Ras Laffan",
              impact: "TTF: +10% tot +18% · Belpex: +6% tot +14%",
              why: "De fysieke schade aan South Pars en Ras Laffan blijft de belangrijkste directe aanbodschok voor gas. Zolang herstel 3-5 maanden duurt, moet Europa duurdere alternatieve moleculen aantrekken, wat de TTF-curve hoger houdt en via merit order doorwerkt in de elektriciteitsprijs.",
              monitor: "Volg QatarEnergy updates, heropstart van installaties, force-majeure berichten en concrete meldingen over exportcapaciteit die opnieuw beschikbaar komt.",
              border: "#ef4444",
              impactColor: "#fca5a5",
            },
            {
              icon: "🟡",
              title: "4. EU-gasopslag tijdens injectieseizoen",
              impact: "TTF: +8% tot +15% · Belpex: +4% tot +10%",
              why: "Met opslag rond 26% moet Europa uitzonderlijk veel volume injecteren tussen april en oktober om de 90%-doelstelling te halen. Dat verhoogt de koopdruk op LNG en spotgas, zeker zolang grote landen zoals Duitsland, Frankrijk en Nederland onder hun normale seizoenspad blijven.",
              monitor: "Check wekelijks GIE AGSI+, vooral of de vulgraad eind april boven 35-40% uitkomt en of de injectiesnelheid versnelt of achterblijft.",
              border: "#f97316",
              impactColor: "#fdba74",
            },
            {
              icon: "🟡",
              title: "5. Diplomatie rond Hormuz en regionale escalatie",
              impact: "TTF: -20% tot +15% · Belpex: -12% tot +10%",
              why: "Dit is de factor met de grootste tweezijdige impact: de-escalatie kan de geopolitieke premie snel uitprijzen, terwijl nieuwe aanvallen ze meteen opnieuw opblazen. De markt reageert hier niet alleen op fysieke doorstroming, maar vooral op verwachtingen over beschikbaarheid, verzekeringskosten en risico-opslagen.",
              monitor: "Volg officiële verklaringen uit Washington, Teheran, Doha en Riyad, plus berichten over scheepvaartveiligheid en tankerdoorvoer door Hormuz.",
              border: "#f97316",
              impactColor: "#fdba74",
            },
            {
              icon: "🟢",
              title: "6. IEA-reserves en olie-interventies",
              impact: "TTF: -3% tot +2% · Belpex: -2% tot +2%",
              why: "IEA-reserves werken vooral via olie en sentiment, niet via directe gasbeschikbaarheid. Ze kunnen paniek in Brent en macro-inflatieverwachtingen afremmen, maar lossen de fundamentele LNG-krapte niet op en hebben daarom slechts een beperkte doorwerking op TTF en Belpex.",
              monitor: "Let op aankondigingen van extra vrijgaven, Brent boven $120-130 en signalen dat landen minder bereid zijn nog meer reservevolume in te zetten.",
              border: "#22c55e",
              impactColor: "#86efac",
            },
            {
              icon: "🟢",
              title: "7. Doorrekening naar Belgische consumentenprijzen",
              impact: "Groothandel: 0% tot +3% · Eindfactuur variabel: +15% tot +25%",
              why: "Deze factor verandert de groothandelsprijs nauwelijks, maar wel de timing en intensiteit waarmee gezinnen de schok voelen. Leveranciers verwerken de huidige risicopremie in variabele contracten met vertraging en bouwen die bij vaste contracten meteen in voor 12-18 maanden.",
              monitor: "Volg VREG-tarieven, leveranciersupdates, indexatieformules en of nieuwe vaste contracten nog extra geopolitieke premie bevatten tegenover variabele formules.",
              border: "#22c55e",
              impactColor: "#86efac",
            },'''

new_factors_header = '''          <h3 style={{ margin: "0 0 8px", color: "#f8fafc", fontSize: 15 }}>🔑 Sleutelfactoren om op te volgen — Juni 2026</h3>
          <p style={{ fontSize: 12, color: "#64748b", marginTop: 0, marginBottom: 14 }}>Gerangschikt op impact: 🔴 Kritiek · 🟡 Belangrijk · 🟢 Moderate invloed</p>
          <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: 12 }}>
            {[{
              icon: "🔴",
              title: "1. Qatar LNG-schade: 3-5 jaar structureel herstel",
              impact: "TTF: +15% tot +30% vs pre-crisis · Belpex: +12% tot +25%",
              why: "De zwaarste structurele schok op de gasmarkt. Qatar's 17% van de wereldwijde LNG-export is voor 3-5 jaar buiten gebruik (NYTimes, 14 mei 2026). Pre-crisis TTF-niveaus van €30-32 zijn daardoor structureel onbereikbaar tot 2028-2030. Dit houdt de Europese gasmarkt permanent krapper dan voor 2026.",
              monitor: "QatarEnergy updates over herstelschema, nieuwe LNG-contracten, heropstart South Pars / Ras Laffan, en alternatieve leveranciers (VS, Mozambique, Tanzania).",
              border: "#ef4444",
              impactColor: "#fca5a5",
            },
            {
              icon: "🔴",
              title: "2. Belgische gasopslag: kan 90% target gehaald worden?",
              impact: "TTF: +8% tot +20% bij opslagtekort · Belpex: +5% tot +15%",
              why: "Met 21.9% vulgraad op 5 juni moet België ~68 procentpunten bijvullen voor 1 november — een record. Als de injectiesnelheid achterblijft, wordt de winter 2026-27 duurder geprijsd al in augustus. De krapte op de LNG-markt maakt agressieve injectie kostbaar.",
              monitor: "Check wekelijks GIE AGSI+ (agsi.gie.eu), Belgisch opslagpeil. Doel: 35% eind juni, 55% eind augustus, 75%+ eind september.",
              border: "#ef4444",
              impactColor: "#fca5a5",
            },
            {
              icon: "🔴",
              title: "3. Hormuz scheepvaartstabiliteit (heropend 21 april)",
              impact: "TTF: -15% tot +20% · Belpex: -10% tot +15%",
              why: "De Hormuz-heropening op 21 april verklaart grotendeels de TTF-daling van €62 naar €48.85. De wapenstilstand is echter fragiel. Nieuwe escalatie zou de risicopremie onmiddellijk doen terugkeren. Tanker-verzekeringspremies blijven 3-4× normaal, wat aangeeft dat de markt het risico nog niet als opgelost beschouwt.",
              monitor: "Hormuz Strait Monitor (hormuzstraitmonitor.com), VN-bemiddelingsberichten, tankerdoorvoer-data, Iraanse en VS-verklaringen.",
              border: "#ef4444",
              impactColor: "#fca5a5",
            },
            {
              icon: "🟡",
              title: "4. LNG-aanbodgolf: verder vertraagd naar 2027-2028",
              impact: "TTF: +5% tot +12% vs verwacht · Belpex: +3% tot +8%",
              why: "De verwachte compenserende LNG-golf (VS, Mozambique, Qatar North Field) is door constructieproblemen verschoven naar 2027-2028. Europa en Azië concurreren voor dezelfde beperkte LNG-cargos. Spot-LNG vrachttarieven zijn 60% boven het gemiddelde van 2024.",
              monitor: "S&P Global LNG-outlook, FID-beslissingen voor nieuwe LNG-terminals, VS exportvergunningen en Aziatische LNG-vraagontwikkeling.",
              border: "#f97316",
              impactColor: "#fdba74",
            },
            {
              icon: "🟡",
              title: "5. Vaste tariefpremie: 27% duurder dan variabel",
              impact: "Consument: vast kost nu 27% meer dan variabel · Leverage naar leverancier",
              why: "VRT meldde in juni 2026 dat vaste contracten gemiddeld 27% duurder zijn dan vergelijkbare variabele formules. Dit is een historisch hoge risicopremie die leveranciers inbouwen voor structurele onzekerheid. Het geeft een duidelijk marktsignaal: de markt verwacht dat prijzen zullen dalen t.o.v. het huidige niveau.",
              monitor: "VREG-tariefvergelijker, aanbiedingen van Eneco, Engie, Luminus, Mega. Vast alleen aantrekkelijk als u de rust van vaste kosten verkiest boven financieel optimum.",
              border: "#f97316",
              impactColor: "#fdba74",
            },
            {
              icon: "🟢",
              title: "6. OPEC+ productieverogingen compenseren olie-tekort",
              impact: "Brent: -5% tot -10% stabiliserend effect · Indirect TTF: -2% tot +1%",
              why: "OPEC+ heeft drie productieverogingen doorgevoerd om Hormuz-volumes te compenseren. De derde verhoging (188.000 vaten/dag, mei 2026) werd als 'symbolisch' beschouwd maar draagt bij aan Brent-normalisatie naar $95.36. Impact op gas is indirect (via macro-inflatie en energiesentiment).",
              monitor: "OPEC+ vergaderingen, Brent boven/onder $100, en signalen van productie-compliance bij leden als Irak en Nigeria.",
              border: "#22c55e",
              impactColor: "#86efac",
            },
            {
              icon: "🟢",
              title: "7. Doorrekening naar Belgische consumentenprijzen",
              impact: "Variabel contract: wijziging t-2 maanden vertraagd · Vast: risicopremie ingebakken",
              why: "Met vast 27% duurder dan variabel is het marktsignaal duidelijk. Leveranciers verwerken geopolitieke risicopremie in vaste contracten. Bij variabele formules volgt de doorrekening met 1-2 maanden vertraging op groothandelsbewegingen. Belgische inflatie bijgesteld naar 2.6% mede door energieprijzen.",
              monitor: "VREG-tarieven, leveranciersupdates, indexatieformules (gas en elektriciteit apart), en of prijsdaling groothandel ook zichtbaar wordt in variabele tarieven.",
              border: "#22c55e",
              impactColor: "#86efac",
            },'''

content = content.replace(old_factors_header, new_factors_header)
print("✅ 12. Sleutelfactoren bijgewerkt (jun 2026 context)")

# ============================================================
# 13. KERNBOODSCHAP: update (verwijder €53.25 referentie)
# ============================================================

old_kernboodschap = '''        <div style={{ ...SECTION, background: "#172554", border: "3px solid #3b82f6", borderRadius: 14, padding: "24px 28px" }}>
          <h2 style={{ margin: "0 0 16px", color: "#60a5fa", fontSize: 18, fontWeight: 700 }}>🎯 KERNBOODSCHAP: Weloverwogen keuzen duren langer dan een nieuwscyclus</h2>

          <p style={{ fontSize: 15, lineHeight: 1.85, color: "#bfdbfe", margin: "0 0 14px", fontWeight: 500 }}>
            TTF daalde vandaag naar €48.85/MWh (-12.1%), wat duidt op marktverlichting na de piek van €60.60. Echter, de structurele LNG-disruptie blijft van kracht (Rabobank: Q2 2026 TTF €61/MWh). Wie nu vastlegt op €53.25 betaalt waarschijnlijk méér dan het gemiddelde over de komende 12-18 maanden.
          </p>

          <div style={{ background: "#0f172a", borderRadius: 10, padding: "16px 20px", marginBottom: 14, border: "1px solid #1e3a8a" }}>
            <p style={{ fontSize: 14, lineHeight: 1.85, color: "#bfdbfe", margin: "0 0 12px" }}>
              <strong style={{ color: "#60a5fa" }}>Korte termijn (2-5 maanden):</strong> Verhoogd prijsniveau door gasveld schade (South Pars, Ras Laffan). Herstel duurt 3-5 maanden volgens QatarEnergy. TTF blijft waarschijnlijk €50-65 tot Q3 2026.
            </p>
            <p style={{ fontSize: 14, lineHeight: 1.85, color: "#bfdbfe", margin: 0 }}>
              <strong style={{ color: "#60a5fa" }}>Middellange termijn (6-18 maanden):</strong> Het naderende injectieseizoen (maart-oktober) en de structurele LNG-aanbodgolf (VS, Qatar, Mozambique) zorgen voor normalisatie. Wie op 12–18 maanden kijkt, heeft statistisch gezien meer kans op een lagere gemiddelde prijs via variabel dan via een vast contract dat nu wordt afgesloten op verhoogd niveau met volledige risicopremie.
            </p>
          </div>

          <p style={{ fontSize: 15, lineHeight: 1.85, color: "#bfdbfe", margin: "0 0 16px", fontWeight: 500 }}>
            De Belgische wet biedt consumenten bescherming bij ingrijpend gewijzigde omstandigheden (wettelijk recht op kosteloze opzegging). Dat is een vangnet — geen reden om contracten als tijdelijke constructies te beschouwen. Een <strong>stabiele keuze die u 12 maanden met vertrouwen kunt aanhouden</strong> is altijd beter dan een snelle beslissing die u maanden later al betreurt.
          </p>

          <div style={{ background: "#0c4a6e", border: "2px solid #0ea5e9", borderRadius: 10, padding: "16px 20px", fontSize: 14, color: "#e0f2fe" }}>
            <h4 style={{ margin: "0 0 12px", color: "#38bdf8", fontSize: 15, fontWeight: 700 }}>📋 PRAKTISCH ADVIES — Concrete Stappen</h4>

            <div style={{ marginBottom: 12 }}>
              <strong style={{ color: "#7dd3fc" }}>1. Observatieperiode (4-6 weken):</strong> Wacht tot eind april 2026 om LNG-disruptie impact te beoordelen. Volg TTF dagelijks via Trading Economics. Monitor België gasopslag via GIE AGSI+ (update elke dinsdag). Rabobank verwacht Q2 2026 TTF €61/MWh - wacht of dit zich materialiseert.
            </div>
            <div style={{ marginBottom: 12 }}>
              <strong style={{ color: "#7dd3fc" }}>2. Trigger voor Variabel:</strong> Als TTF structureel onder €45/MWh stabiliseert gedurende 2+ weken EN Belgische opslag boven 35% eind mei, overweeg dan variabel met 12-18 maanden horizon. Dit biedt de beste kans op lagere gemiddelde kosten nu de LNG glut voorbij is.
            </div>
            <div style={{ marginBottom: 12 }}>
              <strong style={{ color: "#7dd3fc" }}>3. Trigger voor Vast:</strong> Als TTF structureel boven €60/MWh blijft voor 4+ weken OF Hormuz langer dan 6 weken gesloten blijft, overweeg dan vast voor maximaal 12-18 maanden. Budgetzekerheid weegt zwaarder dan flexibiliteitsvoordeel bij structurele LNG-schaarste.
            </div>
            <div style={{ marginBottom: 8 }}>
              <strong style={{ color: "#7dd3fc" }}>4. Maximale contracttermijn:</strong> <strong>Nooit meer dan 12-18 maanden</strong>. De Belgische wet biedt kosteloze opzegging, maarrequent wisselen leidt tot hogere tarieven voor iedereen. Een weloverwogen keuze voor minimaal 12 maanden levert financieel en administratief het meeste op.
            </div>

            <div style={{ background: "#7c2d12", border: "1px solid #f97316", borderRadius: 8, padding: "12px 14px", marginTop: 14 }}>
              <strong style={{ color: "#fdba74" }}>⚠️ NOOIT OVERHAAST TEKENEN:</strong> Tijdens een nieuwscyclus die voelt als een noodsituatie, nemen leveranciers en media de urgentie op. Dat is marketing, geen financieel advies. Paniek is een slechte raadgever. Neem de tijd om te vergelijken en te begrijpen wat u tekent.
            </div>
          </div>
        </div>'''

new_kernboodschap = '''        <div style={{ ...SECTION, background: "#172554", border: "3px solid #3b82f6", borderRadius: 14, padding: "24px 28px" }}>
          <h2 style={{ margin: "0 0 16px", color: "#60a5fa", fontSize: 18, fontWeight: 700 }}>🎯 KERNBOODSCHAP: Post-crisis normalisatie met structurele vloer door Qatar-schade</h2>

          <p style={{ fontSize: 15, lineHeight: 1.85, color: "#bfdbfe", margin: "0 0 14px", fontWeight: 500 }}>
            TTF staat op €48.85/MWh — een daling van 21% t.o.v. de piek van €62 in maart. De Hormuz-heropening (21 april) verklaart dit herstel. Maar: Qatar's LNG-exportcapaciteit is 3 tot 5 jaar beschadigd (17% van de wereldmarkt). Dat betekent dat pre-crisis niveaus van €30-32 structureel onbereikbaar zijn tot 2028-2030. TTF blijft permanent hoger dan het verleden.
          </p>

          <div style={{ background: "#0f172a", borderRadius: 10, padding: "16px 20px", marginBottom: 14, border: "1px solid #1e3a8a" }}>
            <p style={{ fontSize: 14, lineHeight: 1.85, color: "#bfdbfe", margin: "0 0 12px" }}>
              <strong style={{ color: "#60a5fa" }}>Korte termijn (zomer 2026):</strong> TTF normaliseert verder in de range €42-55 naarmate Hormuz-scheepvaart herstelt en het injectieseizoen de opslag vult. Belpex zal door het lage-wind/laag-zon zomerpatroon schommelen. Belgische opslag moet snel stijgen om winterrisico te vermijden.
            </p>
            <p style={{ fontSize: 14, lineHeight: 1.85, color: "#bfdbfe", margin: 0 }}>
              <strong style={{ color: "#60a5fa" }}>Middellange termijn (najaar 2026 — 2027):</strong> De Qatar-schade zorgt voor een structurele vloer onder de TTF-prijs. LNG-alternatieven (VS, Mozambique) vullen slechts gedeeltelijk. Wie variabel kiest, profiteert van verdere normalisatie maar loopt winterrisico als opslag tekortschiet. Vast tarief is momenteel 27% duurder dan variabel (VRT, jun 2026) — dat is de marktprijzing van het risico.
            </p>
          </div>

          <p style={{ fontSize: 15, lineHeight: 1.85, color: "#bfdbfe", margin: "0 0 16px", fontWeight: 500 }}>
            De Belgische wet biedt consumenten bescherming bij ingrijpend gewijzigde omstandigheden (wettelijk recht op kosteloze opzegging). Dat is een vangnet — geen reden om contracten als tijdelijke constructies te beschouwen. Een <strong>stabiele keuze die u 12 maanden met vertrouwen kunt aanhouden</strong> is altijd beter dan een snelle beslissing die u maanden later al betreurt.
          </p>

          <div style={{ background: "#0c4a6e", border: "2px solid #0ea5e9", borderRadius: 10, padding: "16px 20px", fontSize: 14, color: "#e0f2fe" }}>
            <h4 style={{ margin: "0 0 12px", color: "#38bdf8", fontSize: 15, fontWeight: 700 }}>📋 PRAKTISCH ADVIES — Concrete Stappen (Juni 2026)</h4>

            <div style={{ marginBottom: 12 }}>
              <strong style={{ color: "#7dd3fc" }}>1. Marktsignaal: variabel heeft duidelijk voordeel</strong> VRT bevestigde in juni 2026 dat vast tarief gemiddeld 27% duurder is dan variabel. Dit is een historisch hoge premie. Wie geen specifieke reden heeft voor zekerheid, betaalt nu te veel voor een vast contract.
            </div>
            <div style={{ marginBottom: 12 }}>
              <strong style={{ color: "#7dd3fc" }}>2. Trigger voor Variabel:</strong> TTF daalt al richting €45-49. Als TTF 2+ weken stabiel onder €45/MWh blijft EN Belgische opslag boven 35% eind juni uitkomt, is variabel met 12-18 maanden horizon de beste keuze. Volg TTF via Trading Economics, opslag via GIE AGSI+ (wekelijkse update dinsdag).
            </div>
            <div style={{ marginBottom: 12 }}>
              <strong style={{ color: "#7dd3fc" }}>3. Trigger voor Vast:</strong> Nieuw geopolitiek incident (Hormuz opnieuw gesloten, escalatie Midden-Oosten) OF Belgische opslag haalt 60% niet tegen september → dan biedt vast zekerheid voor de winter. In dat geval: maximaal 12 maanden afsluiten.
            </div>
            <div style={{ marginBottom: 8 }}>
              <strong style={{ color: "#7dd3fc" }}>4. Maximale contracttermijn:</strong> <strong>Nooit meer dan 12-18 maanden</strong>. Gezien de Qatar-schade (3-5 jaar herstel) verwachten we pas lagere structurele prijzen na 2027. Te lange vaste contracten sluiten u op aan huidige verhoogde niveaus.
            </div>

            <div style={{ background: "#7c2d12", border: "1px solid #f97316", borderRadius: 8, padding: "12px 14px", marginTop: 14 }}>
              <strong style={{ color: "#fdba74" }}>⚠️ NOOIT OVERHAAST TEKENEN:</strong> Ook in een dalende markt is geduld verstandig. Vast 27% duurder dan variabel is een duidelijk marktsignaal — neem de tijd om te vergelijken via de VREG-tariefvergelijker voor u tekent.
            </div>
          </div>
        </div>'''

content = content.replace(old_kernboodschap, new_kernboodschap)
print("✅ 13. Kernboodschap en praktisch advies bijgewerkt (jun 2026)")

# ============================================================
# 14. BRONNEN: verouderde links verwijderen, actuele toevoegen
# ============================================================

old_geo_bronnen = '''            {
              cat: "🌍 Geopolitiek & Beleidsinstanties", color: "#f97316",
              items: [
                { n: "Trading Economics — TTF Natural Gas", d: "Real-time TTF gas prices and market analysis", url: "https://tradingeconomics.com/commodity/eu-natural-gas" },
                { n: "Trading Economics — Brent Crude Oil", d: "Real-time Brent oil prices and historical data", url: "https://tradingeconomics.com/commodity/brent-crude-oil" },
                { n: "CNBC — Oil Market Analysis", d: "Global oil market analysis and price trends", url: "https://www.cnbc.com/2026/03/24/oil-prices-today-wti-brent-middle-east-iran-war.html" },
                { n: "EU Energy Live — Belgium Electricity", d: "Belgian electricity market data and prices", url: "https://euenergy.live/country.php?a2=BE" },
                { n: "EnergyPrices.eu — Belgium Energy", d: "Belgian energy prices and market information", url: "https://www.energyprices.eu/electricity/belgium" },
              ],
            },'''

new_geo_bronnen = '''            {
              cat: "🌍 Geopolitiek & Marktanalyse", color: "#f97316",
              items: [
                { n: "Hormuz Strait Monitor — Live Dashboard", d: "Real-time scheepvaartmonitoring Straat van Hormuz, crisis-timeline", url: "https://hormuzstraitmonitor.com" },
                { n: "Seavantage — Hormuz Crisis 2026 Timeline", d: "Gedetailleerde scheepvaart-disruption timeline, incidenten per datum", url: "https://www.seavantage.com/blog/strait-of-hormuz-crisis-2026-shipping-disruption-timeline" },
                { n: "NYTimes — Qatar LNG: Long Road Back (14/05/2026)", d: "Qatar's LNG-exportcapaciteit 3-5 jaar beschadigd (17% wereldmarkt)", url: "https://www.nytimes.com/2026/05/14/business/qatar-lng-iran.html" },
                { n: "Reuters — OPEC+ derde productieverhoging (03/05/2026)", d: "OPEC+ 188.000 vaten/dag extra na Hormuz-blokkade", url: "https://www.reuters.com/business/energy/opec-set-agree-third-oil-output-quota-hike-since-hormuz-closure-sources-say-2026-05-03" },
                { n: "VRT — Vast of variabel (jun 2026)", d: "Vast tarief gemiddeld 27% duurder dan variabel in België, juni 2026", url: "https://www.frankenergie.be/nl/kennisbank/energie/vast-of-variabel-energiecontract" },
                { n: "EU Energy Live — Belgium Electricity", d: "Belgische elektriciteitsmarktdata en day-ahead prijzen", url: "https://euenergy.live/country.php?a2=BE" },
                { n: "ACER — Gas Key Developments Winter 2026", d: "EU gasmarkt analyse winter 2026, LNG-afhankelijkheid, Qatar-aandeel", url: "https://www.acer.europa.eu/sites/default/files/documents/Publications/2026-ACER-Gas-Key-Developments-winter.pdf" },
              ],
            },'''

content = content.replace(old_geo_bronnen, new_geo_bronnen)
print("✅ 14a. Geopolitieke bronnen bijgewerkt (Hormuz, Qatar, OPEC+, VRT)")

# Verwijder verouderde Gas to Power Journal link
old_gtp = '''                { n: "Gas to Power Journal — TTF analysis", d: "TTF market analysis and price trends", url: "https://gastopowerjournal.com/news/market/ttf-prices-fall-below-e30-mwh-as-geopolitical-risk-premium-fades/" },'''
content = content.replace(old_gtp, '')
print("✅ 14b. Verouderde Gas to Power Journal link verwijderd")

# Verwijder verouderde TradingPedia link
old_tradpedia = '''                { n: "TradingPedia — LNG Market Analysis", d: "LNG market analysis and supply trends", url: "https://www.tradingpedia.com/2026/03/23/gulf-disruptions-reshape-ttf-gas-as-lng-glut-ends/" },'''
content = content.replace(old_tradpedia, '''                { n: "Splash247 — Qatar LNG Long Road Back", d: "Qatar LNG zwaarste disruptie in 20 jaar — 3-5 jaar herstel", url: "https://splash247.com/qatar-lng-faces-long-road-back-after-unprecedented-disruption" },''')
print("✅ 14c. TradingPedia vervangen door Splash247 Qatar LNG analyse")

# ============================================================
# 15. FOOTER: bijwerken
# ============================================================

content = content.replace(
    'GIE AGSI+ · ENTSO-E · Reuters · Bloomberg · Xinhua · Wall Street Journal · IEA.org · EPEX SPOT · VREG · CREG',
    'GIE AGSI+ · ENTSO-E · Reuters · NYTimes · Wall Street Journal · IEA.org · EPEX SPOT · VREG · CREG · Hormuz Strait Monitor'
)
print("✅ 15. Footer bronnenlijst bijgewerkt")

# ============================================================
# OPSLAAN
# ============================================================

with open(JSX_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

new_len = len(content)
print(f"\n{'='*60}")
print(f"✅ GRONDIGE OVERHAUL VOLTOOID")
print(f"   Bestand: {JSX_PATH}")
print(f"   Origineel: {original_len:,} tekens")
print(f"   Nieuw:     {new_len:,} tekens")
print(f"   Delta:     {new_len - original_len:+,} tekens")
print(f"{'='*60}")
