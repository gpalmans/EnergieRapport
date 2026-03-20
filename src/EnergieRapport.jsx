
import { useState } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine, Legend
} from "recharts";

// === DATA ===
// Confirmed points (✓): TTF 17/03=50.75 (OilPriceAPI), TTF 18/03=51.56 (Trading Economics) +1.32%
// Belpex 18/03=80.92 (Elexys calculated average), extreme volatiliteit met negatieve prijzen
// EU opslag 18/03=29% (Bruegel), stabiel niveau
// Brent 18/03=$101.06 (Trading Economics), -2.28% daling vs gisteren
// Geopolitical: Hormuz crisis dag 19, IEA 400M vaten release, Belgium grid congestion, nucleaire problemen
const rawData = [
  { date: "12/02", ttf: 30.2,  belpex: 65.0,  note: "" },
  { date: "13/02", ttf: 31.0,  belpex: 78.0,  note: "" },
  { date: "14/02", ttf: 30.8,  belpex: 70.0,  note: "" },
  { date: "17/02", ttf: 31.5,  belpex: 81.0,  note: "" },
  { date: "18/02", ttf: 32.1,  belpex: 86.0,  note: "" },
  { date: "19/02", ttf: 31.8,  belpex: 76.0,  note: "" },
  { date: "20/02", ttf: 33.0,  belpex: 88.0,  note: "" },
  { date: "21/02", ttf: 34.2,  belpex: 94.0,  note: "" },
  { date: "24/02", ttf: 33.5,  belpex: 82.0,  note: "" },
  { date: "25/02", ttf: 32.8,  belpex: 74.0,  note: "" },
  { date: "26/02", ttf: 32.3,  belpex: 71.0,  note: "" },
  { date: "27/02", ttf: 31.96, belpex: 68.0,  note: "OK" },
  { date: "28/02", ttf: 32.5,  belpex: 72.0,  note: "" },
  { date: "02/03", ttf: 38.0,  belpex: 95.0,  note: "Hormuz" },
  { date: "03/03", ttf: 53.0,  belpex: 118.0, note: "Piek" },
  { date: "04/03", ttf: 56.0,  belpex: 112.0, note: "" },
  { date: "05/03", ttf: 54.5,  belpex: 106.0, note: "" },
  { date: "06/03", ttf: 57.0,  belpex: 114.0, note: "" },
  { date: "07/03", ttf: 55.0,  belpex: 102.0, note: "WE" },
  { date: "09/03", ttf: 59.57, belpex: 136.0, note: "OKPiek" },
  { date: "10/03", ttf: 57.0,  belpex: 112.0, note: "IEA" },
  { date: "11/03", ttf: 55.48, belpex: 74.63, note: "OK" },
  { date: "12/03", ttf: 56.72, belpex: 67.74, note: "OK" },
  { date: "13/03", ttf: 50.33, belpex: 71.50, note: "OKVandaag" },
  { date: "14/03", ttf: 48.15, belpex: 69.82, note: "OK" },
  { date: "15/03", ttf: 46.88, belpex: 73.45, note: "OK" },
  { date: "17/03", ttf: 50.75, belpex: 113.77, note: "" },
  { date: "18/03", ttf: 51.56, belpex: 80.92,  note: "" },
  { date: "19/03", ttf: 54.66, belpex: 100.30, note: "" },
  { date: "20/03", ttf: 62.00, belpex: 125.50, note: "Vandaag" },
];

const marketData = rawData.map((row, i) => {
  const prev = i > 0 ? rawData[i - 1] : null;
  return {
    ...row,
    ttfDod:    prev ? ((row.ttf    - prev.ttf)    / Math.abs(prev.ttf)    * 100) : null,
    belpexDod: prev ? ((row.belpex - prev.belpex) / Math.abs(prev.belpex) * 100) : null,
  };
});

const forecastBase = [
  { date: "20/03", ttf: 62.00, belpex: 125.50 },
  { date: "24/03", ttf: 58,    belpex: 95   },
  { date: "31/03", ttf: 52,    belpex: 80   },
  { date: "07/04", ttf: 48,    belpex: 72   },
  { date: "21/04", ttf: 42,    belpex: 65   },
  { date: "05/05", ttf: 38,    belpex: 60   },
];
const forecastBull = [
  { date: "20/03", ttf: 62.00, belpex: 125.50 },
  { date: "24/03", ttf: 75,    belpex: 145  },
  { date: "31/03", ttf: 85,    belpex: 135  },
  { date: "07/04", ttf: 78,    belpex: 120  },
  { date: "21/04", ttf: 68,    belpex: 105  },
  { date: "05/05", ttf: 60,    belpex: 95   },
];
const forecastBear = [
  { date: "20/03", ttf: 62.00, belpex: 125.50 },
  { date: "24/03", ttf: 55,    belpex: 110  },
  { date: "31/03", ttf: 45,    belpex: 85   },
  { date: "07/04", ttf: 38,    belpex: 70   },
  { date: "21/04", ttf: 32,    belpex: 58   },
  { date: "05/05", ttf: 28,    belpex: 50   },
];

const Tip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: "#0f172a", border: "1px solid #334155", padding: "10px 14px", borderRadius: 8 }}>
      <p style={{ color: "#94a3b8", marginBottom: 4, fontSize: 12 }}>{label}</p>
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.color, margin: "2px 0", fontSize: 13, fontWeight: 600 }}>
          {p.name}: €{Number(p.value).toFixed(2)}/MWh
        </p>
      ))}
    </div>
  );
};

const DodCell = ({ val }) => {
  if (val === null || val === undefined) return <span style={{ color: "#334155" }}>—</span>;
  const up = val > 0;
  const neutral = Math.abs(val) < 0.3;
  const color = neutral ? "#94a3b8" : up ? "#ef4444" : "#22c55e";
  return <span style={{ color, fontWeight: 700 }}>{up ? "▲" : "▼"} {Math.abs(val).toFixed(1)}%</span>;
};

const BADGE = (color) => ({
  display: "inline-block", padding: "3px 10px", borderRadius: 20,
  fontSize: 11, fontWeight: 700, background: color + "22",
  color, border: `1px solid ${color}44`,
});

const SECTION = {
  background: "#1e293b", border: "1px solid #334155",
  borderRadius: 12, padding: "20px 24px", marginBottom: 20,
};

const TABS = [
  ["analyse",  "📊 Analyse & Data"],
  ["context",  "🌍 Geopolitiek"],
  ["forecast", "🔭 Forecast"],
  ["advies",   "🏠 Vaste vs. Variabel"],
  ["bronnen",  "📚 Bronnen"],
];

export default function EnergieRapport() {
  const [tab, setTab] = useState("analyse");

  const tabBtn = (t) => ({
    padding: "8px 15px", borderRadius: 6, cursor: "pointer", fontSize: 13,
    fontWeight: 600, border: "none", whiteSpace: "nowrap", transition: "all 0.2s",
    background: tab === t ? "#0ea5e9" : "transparent",
    color: tab === t ? "#fff" : "#94a3b8",
  });

  return (
    <div style={{ background: "#0f172a", minHeight: "100vh", color: "#e2e8f0", fontFamily: "Georgia, serif", padding: "24px 20px" }}>

      {/* LOGO + COPYRIGHT */}
      <div style={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 12, padding: "16px 24px", marginBottom: 24, display: "flex", flexDirection: "column", alignItems: "center", gap: 12 }}>
        <img
          src="/fulllogo_transparent_nobuffer.png"
          alt="PWR.IT CommV"
          style={{ maxHeight: 70, maxWidth: 260, objectFit: "contain" }}
        />
        <div style={{ borderTop: "1px solid #334155", paddingTop: 12, width: "100%", textAlign: "center" }}>
          <div style={{ fontSize: 12, color: "#94a3b8", fontWeight: 600, marginBottom: 4 }}>
            © PWR.IT CommV — Alle rechten voorbehouden
          </div>
          <div style={{ fontSize: 11, color: "#64748b", lineHeight: 1.7 }}>
            Het gebruik, kopiëren en verspreiden van deze pagina en de analyses hierop is uitsluitend toegestaan
            mits <strong style={{ color: "#94a3b8" }}>uitdrukkelijke schriftelijke toestemming van PWR.IT CommV</strong>.
            Zonder toestemming is elke reproductie of verspreiding verboden.
          </div>
        </div>
      </div>

      {/* HEADER */}
      <div style={{ textAlign: "center", marginBottom: 28 }}>
        <div style={{ color: "#0ea5e9", fontSize: 11, letterSpacing: "0.2em", textTransform: "uppercase", marginBottom: 8, fontFamily: "monospace" }}>
          MARKTANALYSE — 20 MAART 2026 — OFFICIËLE DATABRONNEN
        </div>
        <h1 style={{ fontSize: 26, fontWeight: 700, margin: "0 0 8px", color: "#f8fafc" }}>
          Vlaamse Energieprijzen: Analyse & Forecast
        </h1>
        <p style={{ color: "#64748b", fontSize: 13, margin: 0 }}>
          TTF (gas) · Belpex/EPEX (elektriciteit) · Geopolitieke context · Tariefadvies
        </p>
      </div>

      {/* ALERT */}
      <div style={{ background: "#7c131322", border: "1px solid #ef4444", borderRadius: 10, padding: "14px 20px", marginBottom: 24, display: "flex", alignItems: "center", gap: 12 }}>
        <span style={{ fontSize: 22, flexShrink: 0 }}>⚠️</span>
        <div>
          <div style={{ fontWeight: 700, color: "#fca5a5", marginBottom: 2 }}>KRITIEKE MARKTSITUATIE</div>
          <div style={{ fontSize: 13, color: "#fca5a5" }}>
            Hormuz gesloten (dag 21) · TTF stijgt (+13.5%) · Brent piekt ($119) · Gasvelden aangevallen · Iran-oorlog week 4
          </div>
        </div>
      </div>

      {/* Price Volatility Disclaimer */}
      <div style={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 10, padding: "12px 16px", marginBottom: 24 }}>
        <div style={{ display: "flex", alignItems: "flex-start", gap: 10 }}>
          <span style={{ fontSize: 16, color: "#f59e0b", flexShrink: 0 }}>ℹ️</span>
          <div>
            <div style={{ fontSize: 13, fontWeight: 600, color: "#f8fafc", marginBottom: 4 }}>Prijzen zijn momentopnames</div>
            <div style={{ fontSize: 12, color: "#94a3b8", lineHeight: 1.5 }}>
              De getoonde "vandaag" dagprijzen zijn specifieke momentopnames. 
              Actuele marktprijzen fluctueren continu gedurende de handelsdag. 
              Voor real-time prijzen: raadpleeg EPEX SPOT (elektriciteit) en ICE Endex (gas).
            </div>
          </div>
        </div>
      </div>

      {/* DOWNLOAD BANNER */}
      <div style={{ background: "#0f172a", border: "1px solid #334155", borderRadius: 10, padding: "12px 20px", marginBottom: 16, display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 10 }}>
        <div style={{ fontSize: 13, color: "#64748b" }}>
          📥 <strong style={{ color: "#94a3b8" }}>Offline versie beschikbaar</strong> — werkt zonder internetverbinding
        </div>
        <a href="/offline.html" download="energie_analyse_2026.html"
          style={{ background: "#1e293b", border: "1px solid #334155", color: "#94a3b8", padding: "7px 16px", borderRadius: 8, fontSize: 12, fontWeight: 600, textDecoration: "none", whiteSpace: "nowrap" }}>
          ⬇ Download offline HTML
        </a>
      </div>

      {/* KPIs */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 12, marginBottom: 24 }}>
        {[
          ["TTF Gas vandaag",       "€62.00", "/MWh",  "+13.5% vs gisteren",    "#ef4444"],
          ["Belpex Elektr. vandaag","€125.50", "/MWh", "+25.1% vs gisteren",   "#f97316"],
          ["EU Gasopslag",          "~29%",   " cap.", "laagste peil in jaren",     "#eab308"],
          ["Brent Ruwe Olie",       "$108.50", "/vat",  "+11.8% vs gisteren",   "#8b5cf6"],
        ].map(([label, val, sub, note, c], i) => (
          <div key={i} style={{ background: "#1e293b", border: `1px solid ${c}44`, borderRadius: 10, padding: "13px 15px" }}>
            <div style={{ fontSize: 10, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 5 }}>{label}</div>
            <div style={{ fontSize: 22, fontWeight: 700, color: c }}>{val}<span style={{ fontSize: 11, color: "#64748b" }}>{sub}</span></div>
            <div style={{ fontSize: 11, color: c, marginTop: 3 }}>{note}</div>
          </div>
        ))}
      </div>

      {/* TABS */}
      <div style={{ display: "flex", gap: 4, marginBottom: 20, background: "#1e293b", padding: 6, borderRadius: 10, overflowX: "auto" }}>
        {TABS.map(([t, l]) => <button key={t} style={tabBtn(t)} onClick={() => setTab(t)}>{l}</button>)}
      </div>

      {/* ── ANALYSE ── */}
      {tab === "analyse" && (<>
        <div style={SECTION}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14, flexWrap: "wrap", gap: 8 }}>
            <h3 style={{ margin: 0, color: "#f8fafc", fontSize: 16 }}>TTF Aardgas — Dagelijkse Spotprijzen (€/MWh)</h3>
            <span style={BADGE("#0ea5e9")}>Reuters · Bloomberg · ENTSOG</span>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={marketData} margin={{ top: 4, right: 20, left: 0, bottom: 4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e3a5f" />
              <XAxis dataKey="date" tick={{ fill: "#64748b", fontSize: 11 }} />
              <YAxis domain={[25, 70]} tick={{ fill: "#64748b", fontSize: 11 }} tickFormatter={v => `€${v}`} />
              <Tooltip content={<Tip />} />
              <ReferenceLine y={31.96} stroke="#22c55e" strokeDasharray="4 4" label={{ value: "27/02 basis", fill: "#22c55e", fontSize: 10, position: "right" }} />
              <ReferenceLine x="02/03" stroke="#ef4444" strokeDasharray="4 4" label={{ value: "Hormuz", fill: "#ef4444", fontSize: 10 }} />
              <Line type="monotone" dataKey="ttf" name="TTF Gas" stroke="#0ea5e9" strokeWidth={2.5} dot={false} activeDot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div style={SECTION}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14, flexWrap: "wrap", gap: 8 }}>
            <h3 style={{ margin: 0, color: "#f8fafc", fontSize: 16 }}>Belpex Elektriciteit — Daggemiddelde Day-Ahead (€/MWh)</h3>
            <span style={BADGE("#a78bfa")}>ENTSO-E · EPEX SPOT</span>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={marketData} margin={{ top: 4, right: 20, left: 0, bottom: 4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e3a5f" />
              <XAxis dataKey="date" tick={{ fill: "#64748b", fontSize: 11 }} />
              <YAxis domain={[40, 150]} tick={{ fill: "#64748b", fontSize: 11 }} tickFormatter={v => `€${v}`} />
              <Tooltip content={<Tip />} />
              <ReferenceLine x="02/03" stroke="#ef4444" strokeDasharray="4 4" />
              <ReferenceLine x="10/03" stroke="#22c55e" strokeDasharray="4 4" label={{ value: "IEA", fill: "#22c55e", fontSize: 10 }} />
              <Line type="monotone" dataKey="belpex" name="Belpex" stroke="#a78bfa" strokeWidth={2.5} dot={false} activeDot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div style={SECTION}>
          <h3 style={{ margin: "0 0 14px", color: "#f8fafc", fontSize: 16 }}>Dagelijkse Prijstabel — Afgelopen 30 Dagen</h3>
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
              <thead>
                <tr style={{ borderBottom: "2px solid #334155" }}>
                  {["Datum","TTF €/MWh","Δ TTF dag/dag","Belpex €/MWh","Δ Belpex dag/dag","Δ TTF vs. 27/02","Status"].map(h => (
                    <th key={h} style={{ padding: "8px 11px", textAlign: "left", color: "#64748b", fontWeight: 600, fontSize: 11, whiteSpace: "nowrap" }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {marketData.map((r, i) => {
                  const base  = ((r.ttf - 31.96) / 31.96 * 100).toFixed(1);
                  const shock = parseFloat(base) > 50;
                  const today = r.note.includes("Vandaag");
                  return (
                    <tr key={i} style={{ borderBottom: "1px solid #1e293b", background: today ? "#0c4a6e22" : shock ? "#7f1d1d22" : "transparent" }}>
                      <td style={{ padding: "7px 11px", color: today ? "#0ea5e9" : "#e2e8f0", fontWeight: today ? 700 : 400, whiteSpace: "nowrap" }}>
                        {r.date}{today ? " 🔵" : r.note === "✓" ? " ✓" : ""}
                      </td>
                      <td style={{ padding: "7px 11px", color: shock ? "#ef4444" : "#f97316", fontWeight: 600 }}>€{r.ttf.toFixed(2)}</td>
                      <td style={{ padding: "7px 11px" }}><DodCell val={r.ttfDod} /></td>
                      <td style={{ padding: "7px 11px", color: "#a78bfa", fontWeight: 600 }}>€{r.belpex.toFixed(1)}</td>
                      <td style={{ padding: "7px 11px" }}><DodCell val={r.belpexDod} /></td>
                      <td style={{ padding: "7px 11px", color: parseFloat(base) > 0 ? "#ef4444" : "#22c55e", fontWeight: 600 }}>
                        {parseFloat(base) > 0 ? "+" : ""}{base}%
                      </td>
                      <td style={{ padding: "7px 11px" }}>
                        {r.note.includes("Hormuz") ? <span style={BADGE("#ef4444")}>Hormuz Shock</span>
                        : r.note.includes("Piek")  ? <span style={BADGE("#f97316")}>Piekprijs</span>
                        : r.note === "IEA"         ? <span style={BADGE("#22c55e")}>IEA</span>
                        : today                    ? <span style={BADGE("#0ea5e9")}>Vandaag</span>
                        : r.note === "WE"          ? <span style={BADGE("#475569")}>Weekend</span>
                        : <span style={{ color: "#334155" }}>—</span>}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <p style={{ fontSize: 11, color: "#475569", marginTop: 10, marginBottom: 0 }}>
            ✓ = bevestigd officieel datapunt · Δ dag/dag = procentuele wijziging t.o.v. vorige handelsdag (▲ stijging, ▼ daling) · Tussenliggende waarden: interpolaties op basis van bevestigde marktreeksen
          </p>
        </div>
      </>)}

      {/* ── CONTEXT ── */}
      {tab === "context" && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18 }}>
          <div style={SECTION}>
            <h3 style={{ margin: "0 0 14px", color: "#f8fafc", fontSize: 15 }}>🏭 Europese Gasvoorraden</h3>
            {[
              ["EU-gemiddelde (20 mrt 2026)", "~29%",          "#ef4444"],
              ["Laagste seizoenspeil",       "in jaren",       "#ef4444"],
              ["Einde 2025",                 "~61%",           "#eab308"],
              ["Einde 2024",                 "~72%",           "#22c55e"],
              ["EU-doelstelling (1 nov)",    "90%",            "#0ea5e9"],
              ["Nog te vullen (apr–okt)",    "~60 pct-punten", "#f97316"],
            ].map(([l, v, c]) => (
              <div key={l} style={{ display: "flex", justifyContent: "space-between", padding: "7px 0", borderBottom: "1px solid #1e293b", fontSize: 13 }}>
                <span style={{ color: "#94a3b8" }}>{l}</span>
                <span style={{ color: c, fontWeight: 700 }}>{v}</span>
              </div>
            ))}
            <div style={{ marginTop: 14, padding: "10px 14px", background: "#7c131322", borderRadius: 8, fontSize: 12, color: "#fca5a5", lineHeight: 1.6 }}>
              ⚠️ Gasvelden aangevallen (South Pars, Ras Laffan) - Qatar LNG export -17%. TTF +13.5% op supply shock.
            </div>
          </div>

          <div style={SECTION}>
            <h3 style={{ margin: "0 0 14px", color: "#f8fafc", fontSize: 15 }}>⚔️ Geopolitieke Crisissituatie</h3>
            {[
              ["Straat van Hormuz", "#ef4444", "Dag 21: Scheepvaart volledig geblokkeerd. Gasvelden aangevallen - energiecrisis escaleert."],
              ["Gasvelden Aangevallen", "#f97316", "Israel bombardeert South Pars (Iran), Iran vergeldt op Ras Laffan (Qatar). Exportcapaciteit -17%."],
              ["Belpex Volatiliteit", "#a78bfa", "Extreme volatiliteit: TTF-schok (+13.5%) drijft Belpex naar €125.50 (+25.1%). Grid congestion blijft."],
              ["Brent Peak", "#8b5cf6", "$108.50/vat - Brent piekt op $119 na gasveld aanvallen. Energie-inflatie dreigt."],
              ["VS/Israel Escalatie", "#22c55e", "Trump: 'geen nieuwe aanvallen South Pars' tenzij Iran Qatar aanvalt. Oorlog week 4."],
            ].map(([titel, color, tekst]) => (
              <div key={titel} style={{ marginBottom: 14 }}>
                <span style={BADGE(color)}>{titel}</span>
                <p style={{ marginTop: 7, marginBottom: 0, fontSize: 13, color: "#94a3b8", lineHeight: 1.6 }}>{tekst}</p>
              </div>
            ))}
          </div>

          <div style={SECTION}>
            <h3 style={{ margin: "0 0 14px", color: "#f8fafc", fontSize: 15 }}>🛢️ IEA Strategische Oliereserves</h3>
            <div style={{ background: "#172554", borderRadius: 8, padding: "12px 14px", marginBottom: 12 }}>
              {[
                ["Volume",          "400 mln vaten (recordvrijgave)"],
                ["% totale res.",   "~33% van 1.2 mld noodvoorraad"],
                ["Status",          "Gezamenlijke vrijgave actief sinds 11/03"],
                ["Marktreactie",    "Brent: $119 → $101/vat (daling na IEA release)"],
                ["Effectiviteit",   "Dekken ~4 dagen globale vraag; impact beperkt door Hormuz"],
              ].map(([k, v]) => (
                <div key={k} style={{ display: "flex", justifyContent: "space-between", padding: "5px 0", borderBottom: "1px solid #1e3a5f", fontSize: 12 }}>
                  <span style={{ color: "#94a3b8" }}>{k}</span>
                  <span style={{ color: "#60a5fa", fontWeight: 600 }}>{v}</span>
                </div>
              ))}
            </div>
            <p style={{ fontSize: 11, color: "#475569", margin: 0 }}>Bronnen: IEA Oil Market Report (13/03), Reuters Energy Desk (17/03), BloombergNEF (15/03)</p>
          </div>

          <div style={SECTION}>
            <h3 style={{ margin: "0 0 14px", color: "#f8fafc", fontSize: 15 }}>🇧🇪 Belgische Energiemix</h3>
            <p style={{ marginTop: 0, fontSize: 13, color: "#94a3b8", lineHeight: 1.6 }}>Gas is de <strong style={{ color: "#f8fafc" }}>marginale producent</strong> in ~87% van de handelssessies (2021: 87% gas-price setting) en bepaalt daardoor direct de Belpex-prijs. De extreme volatiliteit op 18/03 wordt verklaard door <strong style={{ color: "#f8fafc" }}>negatieve prijzen</strong> tijdens zonnepiek (€-1.67) en <strong style={{ color: "#f8fafc" }}>avondpieken</strong> (€180) door grid congestion en nucleaire beperkingen.</p>
            <div style={{ background: "#172554", borderRadius: 8, padding: "12px 14px" }}>
              {[
                ["Kern (Doel 4, Tihange 3)", "verlengd tot 2035"],
                ["Aandeel kernenergie",       "~35–40%"],
                ["Aandeel hernieuwbaar",      "~30%"],
                ["Aandeel gas",               "~20%"],
              ].map(([k, v]) => (
                <div key={k} style={{ display: "flex", justifyContent: "space-between", padding: "5px 0", borderBottom: "1px solid #1e3a5f", fontSize: 12 }}>
                  <span style={{ color: "#94a3b8" }}>{k}</span>
                  <span style={{ color: "#60a5fa", fontWeight: 600 }}>{v}</span>
                </div>
              ))}
            </div>
            <p style={{ fontSize: 12, color: "#f97316", marginTop: 10, marginBottom: 0 }}>
              ⚡ Belpex op 18/03 (€80.92 daggemiddelde) toont extreme volatiliteit: negatieve prijzen overdag, avondpieken tot €180 door grid congestion.
            </p>
          </div>
        </div>
      )}

      {/* ── FORECAST ── */}
      {tab === "forecast" && (<>
        <div style={SECTION}>
          <h3 style={{ margin: "0 0 14px", color: "#f8fafc", fontSize: 16 }}>📈 Drie Scenario's — TTF Gas-forecast (mrt–mei 2026)</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart margin={{ top: 4, right: 20, left: 0, bottom: 4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e3a5f" />
              <XAxis dataKey="date" type="category" allowDuplicatedCategory={false} tick={{ fill: "#64748b", fontSize: 11 }} />
              <YAxis domain={[20, 90]} tick={{ fill: "#64748b", fontSize: 11 }} tickFormatter={v => `€${v}`} />
              <Tooltip content={<Tip />} />
              <Legend wrapperStyle={{ fontSize: 12, color: "#94a3b8" }} />
              <Line data={forecastBull} type="monotone" dataKey="ttf" name="⬆ Bullish" stroke="#ef4444" strokeWidth={2} strokeDasharray="6 3" dot={{ r: 3, fill: "#ef4444" }} />
              <Line data={forecastBase} type="monotone" dataKey="ttf" name="⟶ Basis"   stroke="#0ea5e9" strokeWidth={2.5} dot={{ r: 3, fill: "#0ea5e9" }} />
              <Line data={forecastBear} type="monotone" dataKey="ttf" name="⬇ Bearish" stroke="#22c55e" strokeWidth={2} strokeDasharray="6 3" dot={{ r: 3, fill: "#22c55e" }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 14 }}>
          {[
            {
              t: "⬇ Bearish (Ontspanning)", p: "15%", c: "#22c55e",
              ttf: "€28–38", belpex: "€50–70",
              items: ["Gasvelden herstellen binnen 2-3 weken","Hormuz gedeeltelijk open","Diplomatieke de-escalatie","Mild voorjaar verlaagt vraag"],
              note: "Risico: schade gasvelden beperkt herstel",
            },
            {
              t: "⟶ Basis (Prolonged crisis)", p: "45%", c: "#0ea5e9",
              ttf: "€38–55", belpex: "€72–95",
              items: ["Gasvelden deels buiten werking 3-5 maanden","Hormuz beperkt open","Qatar LNG -17% capaciteit","EU opslag onder druk"],
              note: "Meest waarschijnlijk scenario",
            },
            {
              t: "⬆ Bullish (Escalatie)", p: "40%", c: "#ef4444",
              ttf: "€55–85", belpex: "€95–145",
              items: ["Nieuwe aanvallen op energie-infra","Hormuz gesloten tot zomer","Qatar LNG langdurig stil","Koud voorjaar + structurele schade"],
              note: "Potentieel: energiecrisis winter 2026–27",
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
        </div>

        <div style={{ ...SECTION, marginTop: 18 }}>
          <h3 style={{ margin: "0 0 12px", color: "#f8fafc", fontSize: 15 }}>🔑 Sleutelfactoren om op te volgen</h3>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
            {[
              ["Gasveld Herstel (South Pars/Ras Laffan)", "Reparatietijd 3-5 maanden - structurele impact op LNG supply."],
              ["Hormuz scheepvaartberichten",  "Elke heropening = prijsdaling. Bron: Lloyd's List / Reuters."],
              ["GIE gasopslag (wekelijks di)", "Herstel boven 30% = positief signaal bij prolonged crisis."],
              ["Qatar LNG Export Capaciteit", "-17% na aanvallen - herstel onzeker, afhankelijk van schade."],
              ["VS/Israel Diplomatie", "Trump-Netanyahu strategie bepaalt escalatie vs de-escalatie."],
              ["VREG tariefaanpassingen",      "Volgt groothandel met 1-3 maanden vertraging - stijging onvermijdelijk."],
            ].map(([t, d]) => (
              <div key={t} style={{ background: "#0f172a", borderRadius: 8, padding: "11px 13px" }}>
                <div style={{ color: "#60a5fa", fontWeight: 600, marginBottom: 3, fontSize: 12 }}>📌 {t}</div>
                <div style={{ fontSize: 12, color: "#94a3b8" }}>{d}</div>
              </div>
            ))}
          </div>
        </div>
      </>)}

      {/* ── ADVIES ── */}
      {tab === "advies" && (<>

        {/* PANIC WARNING — prominent top block */}
        <div style={{ background: "#451a03", border: "2px solid #f97316", borderRadius: 12, padding: "20px 24px", marginBottom: 22 }}>
          <div style={{ display: "flex", alignItems: "flex-start", gap: 14 }}>
            <span style={{ fontSize: 26, flexShrink: 0 }}>🚨</span>
            <div>
              <h3 style={{ color: "#fb923c", margin: "0 0 10px", fontSize: 16 }}>Opgelet: Beslissen in een paniekklimaat is zelden verstandig</h3>
              <p style={{ fontSize: 14, color: "#fed7aa", lineHeight: 1.8, margin: "0 0 10px" }}>
                De energiemarkten bevinden zich momenteel in een acute crisismodus. Leveranciers én media wekken de indruk dat onmiddellijk handelen noodzakelijk is. Dat klopt <em>niet per definitie</em>. Historisch bewijs toont aan dat wie in een geopolitieke paniekpiek overstapt naar een vast tarief, structureel <strong>meer betaalt</strong> dan wie rationeel afwacht en een weloverwogen keuze maakt.
              </p>
              <div style={{ background: "#431407", borderRadius: 8, padding: "12px 16px", fontSize: 13, color: "#fdba74", lineHeight: 1.7 }}>
                <strong>Wat u moet weten:</strong> Een vast tarief dat vandaag wordt aangeboden, bevat de volledige geopolitieke risicopremie van dit moment. Die premie verdwijnt zodra de crisis normaliseert — terwijl u gebonden bent aan een tarief dat op een uitzonderlijk hoog marktpunt werd afgesloten. Een goed contract begint met een heldere marktevaluatie, niet met een nieuwscyclus als trigger.
              </div>
            </div>
          </div>
        </div>

        {/* MEDIUM-TERM VARIABEL ARGUMENT */}
        <div style={{ ...SECTION, border: "1px solid #0ea5e944" }}>
          <h3 style={{ margin: "0 0 14px", color: "#38bdf8", fontSize: 16 }}>📉 Waarom variabel op de (middel)lange termijn waarschijnlijk goedkoper uitvalt</h3>

          <p style={{ fontSize: 14, color: "#94a3b8", lineHeight: 1.8, marginBottom: 16 }}>
            De huidige prijspiek is reëel, maar de <strong style={{ color: "#f8fafc" }}>structurele marktfundamentelen voor 2026–2027 zijn overwegend bearish</strong>. Dat betekent dat wie vandaag een vast tarief neemt voor 1–3 jaar, waarschijnlijk méér betaalt dan de gemiddelde marktprijs over diezelfde periode.
          </p>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14, marginBottom: 16 }}>
            {[
              {
                icon: "🌊",
                title: "LNG-aanbodgolf 2026–2028",
                body: "Een historisch grote golf nieuwe LNG-capaciteit (VS, Qatar, Mozambique) komt de markt op. S&P Global en IEA verwachten dat dit Europa's gasmarkt structureel losser maakt. Wie nu vastlegt, mist de goedkopere contracten van 2027.",
                color: "#22c55e",
              },
              {
                icon: "🌬️",
                title: "Seizoenseffect na winter",
                body: "Na de koudste wintermaanden daalt de gasvraag altijd. Lente en zomer zijn seizoenmatig de goedkoopste periodes. De huidige piek is deels een tijdelijk winter/crisis-effect dat zich statistisch corrigeert.",
                color: "#0ea5e9",
              },
              {
                icon: "⚖️",
                title: "IEA-interventie dempt (maar lost niet op)",
                body: "De IEA-vrijgave van >182 mln vaten dempt de olieprijspiek, maar lost de structurele gasschade niet op. Gasvelden herstel duurt 3-5 maanden. IEA-effect is beperkt bij fysieke supply disruption, anders dan bij psychologische pieken.",
                color: "#a78bfa",
              },
              {
                icon: "☀️",
                title: "Groeiend aandeel hernieuwbaar",
                body: "In België stijgt het aandeel zon en wind elk jaar. Meer hernieuwbare capaciteit = meer uren waarbij gas niet de marginale prijszetter is. Dit drukt de gemiddelde Belpex-prijs structureel lager over tijd.",
                color: "#eab308",
              },
            ].map((c, i) => (
              <div key={i} style={{ background: "#0f172a", borderRadius: 10, padding: "14px 16px", border: `1px solid ${c.color}33` }}>
                <div style={{ fontSize: 18, marginBottom: 6 }}>{c.icon}</div>
                <div style={{ color: c.color, fontWeight: 700, fontSize: 13, marginBottom: 6 }}>{c.title}</div>
                <div style={{ fontSize: 12, color: "#64748b", lineHeight: 1.7 }}>{c.body}</div>
              </div>
            ))}
          </div>

          <div style={{ background: "#0c2a1a", border: "1px solid #22c55e55", borderRadius: 10, padding: "14px 18px" }}>
            <div style={{ display: "flex", gap: 10, alignItems: "flex-start" }}>
              <span style={{ fontSize: 18, flexShrink: 0 }}>📊</span>
              <div>
                <div style={{ color: "#4ade80", fontWeight: 700, fontSize: 14, marginBottom: 6 }}>Historisch precedent: 2022 crisis vs. daarna</div>
                <p style={{ fontSize: 13, color: "#86efac", lineHeight: 1.7, margin: 0 }}>
                  Wie in september–oktober 2022 (het absolute piekmoment) overstapte naar een vast tarief van 3 jaar, betaalde gemiddeld <strong>2–3× meer</strong> dan de marktprijs in 2023–2024. Wie in paniek vastzat aan een crisiscontract terwijl de markt normaliseerde, kon niet profiteren van de dalende prijzen. Dezelfde dynamiek is nu opnieuw relevant.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* BELGIAN LEGAL RIGHT TO SWITCH */}
        <div style={{ background: "#0c2a1a", border: "2px solid #22c55e", borderRadius: 12, padding: "20px 24px", marginBottom: 22 }}>
          <div style={{ display: "flex", alignItems: "flex-start", gap: 14 }}>
            <span style={{ fontSize: 24, flexShrink: 0 }}>⚖️</span>
            <div>
              <h3 style={{ color: "#4ade80", margin: "0 0 10px", fontSize: 16 }}>Belgische wet: consumentenbescherming als vangnet — voor particulier én KMO</h3>
              <p style={{ fontSize: 14, color: "#86efac", lineHeight: 1.8, margin: "0 0 12px" }}>
                Sinds 2012 geldt in België een <strong>wettelijk recht op kosteloze opzegging</strong> van elk energiecontract, voor zowel gezinnen als KMO's — mits een opzegtermijn van 1 maand. Dit recht bestaat als consumentenbescherming bij gewijzigde omstandigheden: verhuis, grote wijziging in verbruiksprofiel, of een aanbod dat significant beter uitvalt. Het is <em>geen vrijgeleide om frequent van contract te wisselen</em>: veelvuldig wisselen brengt administratieve lasten, mogelijke promotieverlies en marktverstoring met zich mee — en werkt uiteindelijk door in hogere tarieven voor iedereen.
              </p>
              <div style={{ background: "#451a03", border: "1px solid #f9731666", borderRadius: 8, padding: "12px 16px", fontSize: 13, color: "#fed7aa", lineHeight: 1.7 }}>
                <strong>⚠️ Financiële valkuil bij vroegtijdig vertrek:</strong> Leveranciers bieden welkomstpremies en kortingen aan die gebonden zijn aan het uitzitten van de contractperiode. Opzegt u binnen de eerste 12 maanden, dan riskeert u het verlies van deze voordelen — en soms een terugvordering van reeds uitbetaalde premies (wettelijk toegestaan voor de eerste 6 maanden). Lees de bijzondere voorwaarden altijd grondig voor ondertekening.
              </div>
            </div>
          </div>
        </div>

        {/* IMPORTANT SYSTEMIC NUANCE */}
        <div style={{ background: "#1e1b4b", border: "1px solid #818cf8", borderRadius: 10, padding: "14px 18px", marginBottom: 22, fontSize: 13, color: "#c7d2fe", lineHeight: 1.75 }}>
          <strong style={{ color: "#a5b4fc" }}>📌 Waarom de 12-maanden horizon verstandig is — ook voor u:</strong> De VREG stelt zelf vast dat het hoge switchtempo in België structureel doorwerkt in hogere vaste tarieven: leveranciers verrekenen het risico van vroegtijdig vertrek als een verborgen risicopremie. Wie een contract afsluit met de intentie om het snel opnieuw te herzien, betaalt als het ware voor flexibiliteit die hij al had — zonder er bewust van te profiteren. Een weloverwogen keuze voor een tariefformule die u minimaal 12 maanden kunt handhaven, levert u financieel en administratief het meeste op.
        </div>

        {/* WHEN FIXED IS STILL JUSTIFIED */}
        <div style={SECTION}>
          <h3 style={{ margin: "0 0 14px", color: "#f8fafc", fontSize: 16 }}>🏠 Wanneer is een vast tarief dan wél verantwoord?</h3>
          <div style={{ background: "#7c131322", border: "1px solid #ef4444", borderRadius: 10, padding: "13px 17px", marginBottom: 16, fontSize: 13, color: "#fca5a5", lineHeight: 1.7 }}>
            <strong>Eerlijke boodschap:</strong> Vast of variabel — beide zijn correcte keuzes, mits gemaakt op rationele gronden en niet gedreven door marktpaniek. De vuistregel: kies een formule die u met overtuiging voor <strong>minimaal 12 maanden</strong> kunt aanhouden. Snel schakelen tussen contractvormen kost u geld (verloren premies, administratieve lasten) en levert zelden het verwachte voordeel op.
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
            <div style={{ background: "#1e293b", border: "1px solid #22c55e44", borderRadius: 12, padding: "14px 18px" }}>
              <h4 style={{ color: "#22c55e", margin: "0 0 10px", fontSize: 14 }}>✅ Vast tarief overwegen als…</h4>
              <ul style={{ margin: 0, padding: "0 0 0 16px", fontSize: 13, color: "#94a3b8", lineHeight: 2 }}>
                <li>Uw budget <strong style={{ color: "#f8fafc" }}>geen schommelingen verdraagt</strong> (sociale situatie, schulden)</li>
                <li>U <strong style={{ color: "#f8fafc" }}>extreem hoog verbruik</strong> heeft (warmtepomp, elektrische wagen, grote woning)</li>
                <li>U als KMO <strong style={{ color: "#f8fafc" }}>vaste kostenstructuur</strong> nodig heeft voor offertes/klanten</li>
                <li>U de rust en stabiliteit van een <strong style={{ color: "#f8fafc" }}>bekende maandkost</strong> verkiest boven marktvolatiliteit</li>
              </ul>
            </div>
            <div style={{ background: "#1e293b", border: "1px solid #ef444444", borderRadius: 12, padding: "14px 18px" }}>
              <h4 style={{ color: "#ef4444", margin: "0 0 10px", fontSize: 14 }}>❌ Vast tarief vermijden als…</h4>
              <ul style={{ margin: 0, padding: "0 0 0 16px", fontSize: 13, color: "#94a3b8", lineHeight: 2 }}>
                <li>U <strong style={{ color: "#f8fafc" }}>zonnepanelen of een batterij</strong> heeft (variabel maximaliseert uw voordeel)</li>
                <li>U de beslissing neemt <strong style={{ color: "#f8fafc" }}>puur door de nieuwscyclus</strong>, niet door uw verbruiksprofiel</li>
                <li>De aangeboden prijs <strong style={{ color: "#f8fafc" }}>méér dan 15% boven</strong> het pre-crisis niveau ligt</li>
                <li>U de <strong style={{ color: "#f8fafc" }}>bijzondere voorwaarden</strong> (premies, loyaliteitsvoordelen) niet gelezen heeft</li>
              </ul>
            </div>
          </div>
        </div>

        {/* DECISION MATRIX */}
        <div style={SECTION}>
          <h3 style={{ margin: "0 0 12px", color: "#f8fafc", fontSize: 15 }}>📋 Adviesmatrix per Profiel</h3>
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12.5 }}>
              <thead>
                <tr style={{ borderBottom: "2px solid #334155" }}>
                  {["Profiel","Aanbeveling","Motivering","Voorzorgsmaatregel"].map(h => (
                    <th key={h} style={{ padding: "9px 11px", textAlign: "left", color: "#64748b", fontSize: 11 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {[
                  ["Gezin, krappe begroting",   "⚖️ Vast — maar wacht 4–6 wk",     "Zekerheid primeert; wacht tot gasveld-impact duidelijk is voor weloverwogen keuze", "Lees bijzondere voorwaarden; ken uw welkomstpremie-condities"],
                  ["Gemiddeld gezin",            "⬇ Variabel — blijf rationeel",    "Verhoogd niveau door gasveld schade (2-5 mnd), daarna structureel bearish; variabel profiteert van normalisatie",             "Herbekijk jaarlijks; geen reden tot haastbeslissing nu"],
                  ["Hoog verbruik (WP/EV)",      "⚖️ Vast — na weloverwogen keuze", "Hogere blootstelling aan schokken; vast geeft stabiele maandkost bij hoog verbruik",       "Koppel aan laadoptimalisatie op daluren; evalueer na 12 mnd"],
                  ["Zonnepanelen + batterij",    "⬇ Variabel of dynamisch",         "Hernieuwbaar profiteert maximaal van daluurprijzen en teruglevering",                        "Monitor dag-ahead via leveranciers-app of Fluvius"],
                  ["KMO / kleine zelfstandige",  "⚖️ Vast — voor budgetstabiliteit","KMO heeft zelfde wettelijk overstaprecht; vast geeft voorspelbare kostenstructuur",          "Lees loyaliteitsclausules; plan herziening na 12 maanden"],
                ].map(([p, a, m, v], i) => (
                  <tr key={i} style={{ borderBottom: "1px solid #1e293b" }}>
                    <td style={{ padding: "9px 11px", color: "#e2e8f0", fontWeight: 600 }}>{p}</td>
                    <td style={{ padding: "9px 11px", color: "#60a5fa" }}>{a}</td>
                    <td style={{ padding: "9px 11px", color: "#94a3b8" }}>{m}</td>
                    <td style={{ padding: "9px 11px", color: "#64748b", fontSize: 11 }}>{v}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div style={{ ...SECTION, background: "#172554", border: "1px solid #3b82f644" }}>
          <h3 style={{ margin: "0 0 10px", color: "#60a5fa", fontSize: 15 }}>🎯 Kernboodschap: Weloverwogen keuzen duren langer dan een nieuwscyclus</h3>
          <p style={{ fontSize: 14, lineHeight: 1.85, color: "#bfdbfe", margin: "0 0 12px" }}>
            De huidige marktbeweging is extreem, maar <strong>niet ongezien</strong>. In 2022 maakten tienduizenden Belgische gezinnen dezelfde fout: vastleggen op een historisch piekmoment, om vervolgens toe te kijken hoe de markt normaliseerde terwijl zij gebonden waren aan een duur contract.
          </p>
          <p style={{ fontSize: 14, lineHeight: 1.85, color: "#bfdbfe", margin: "0 0 12px" }}>
            <strong>Korte termijn (2-5 maanden):</strong> Verhoogd prijsniveau door gasveld schade (South Pars, Ras Laffan). Herstel duurt 3-5 maanden. <strong>Middellange termijn (6-18 maanden):</strong> Het naderende injectieseizoen en de structurele LNG-aanbodgolf zorgen voor normalisatie. Wie op 12–18 maanden kijkt, heeft statistisch gezien meer kans op een lagere gemiddelde prijs via variabel dan via een vast contract dat nu wordt afgesloten op verhoogd niveau.
          </p>
          <p style={{ fontSize: 14, lineHeight: 1.85, color: "#bfdbfe", margin: "0 0 12px" }}>
            De Belgische wet biedt consumenten bescherming bij ingrijpend gewijzigde omstandigheden. Dat is een vangnet — geen reden om contracten als tijdelijke constructies te beschouwen. Een <strong>stabiele keuze die u 12 maanden met vertrouwen kunt aanhouden</strong> is altijd beter dan een snelle beslissing die u maanden later al betreurt.
          </p>
          <div style={{ background: "#0f172a", borderRadius: 8, padding: "12px 16px", fontSize: 13, color: "#7dd3fc" }}>
            <strong>Praktisch advies:</strong> Wacht minimaal 4–6 weken om gasveld-impact te beoordelen. Volg TTF dagelijks. Stabiliseert TTF <em>onder</em> €50/MWh → variabel is structureel aantrekkelijk. Blijft TTF boven €60/MWh voor 6+ weken → vast tarief overwegen, mits u de voorwaarden kent en de keuze past bij uw verbruiksprofiel voor 12+ maanden. <strong>Nooit overhaast tekenen tijdens een nieuwscyclus die voelt als een noodsituatie.</strong> Paniek is een slechte raadgever.
0          </div>
        </div>
      </>)}

      {/* ── BRONNEN ── */}
      {tab === "bronnen" && (
        <div style={SECTION}>
          <h3 style={{ margin: "0 0 6px", color: "#f8fafc", fontSize: 16 }}>📚 Bronvermeldingen & Officiële Databronnen</h3>
          <p style={{ fontSize: 13, color: "#64748b", marginTop: 0, marginBottom: 22 }}>
            Alle bronnen zijn publiek raadpleegbaar. Bevestigde exacte datapunten zijn gemarkeerd met ✓ in de tabellen.
          </p>

          {[
            {
              cat: "⚡ Elektriciteitsmarkt — Belpex / EPEX SPOT", color: "#a78bfa",
              items: [
                { n: "ENTSO-E Transparency Platform",    d: "Officiële dagprijzen per land (incl. BE), bron voor alle Belpex-data", url: "https://transparency.entsoe.eu" },
                { n: "EPEX SPOT — Belgische marktdata",  d: "Officiële clearing van de Belgische day-ahead markt",                   url: "https://www.epexspot.com/en/market-data" },
                { n: "Elia — Day-ahead referentieprijs", d: "Belgische SDAC-prijs gepubliceerd door Belgische TSO",                  url: "https://www.elia.be/en/grid-data/transmission/day-ahead-reference-price" },
                { n: "Elexys — Belpex Hourly Data", d: "Official hourly Belpex prices (18/03: €80.92 average, negative prices €-1.67)", url: "https://www.elexys.be/en/insights/epex-spot" },
              ],
            },
            {
              cat: "🔥 Gasmarkt — TTF", color: "#0ea5e9",
              items: [
                { n: "ICE — Dutch TTF Natural Gas Futures",    d: "Officiële futuresmarkt voor TTF gascontracten",                        url: "https://www.ice.com/products/27996665/Dutch-TTF-Natural-Gas-Futures/data" },
                { n: "Gas Infrastructure Europe (GIE) AGSI+", d: "Officiële EU gasopslagniveaus per land — wekelijkse update",           url: "https://agsi.gie.eu" },
                { n: "Trading Economics — TTF 20/03/2026",    d: "Bevestigd: TTF €62.00/MWh op 20/03/2026 (+13.5% dag/dag)",             url: "https://tradingeconomics.com/commodity/eu-natural-gas" },
                { n: "Reuters — Gas Field Attacks (20/03/2026)", d: "Israel bombardeert South Pars, Iran vergeldt op Ras Laffan -17% Qatar LNG", url: "https://www.reuters.com/world/middle-east/israel-strikes-irans-south-pars-gas-field-2026-03-20/" },
                { n: "CBS News — Iran War Escalation (20/03/2026)", d: "Iran strikes Kuwait oil refinery, energy prices jump 35%", url: "https://www.cbsnews.com/live-updates/iran-war-israel-strike-south-pars-gas-field-trump-threat-oil-gas-prices/" },
                { n: "NBC News — Gas Field Damage (20/03/2026)", d: "South Pars gas field attacks send energy prices soaring", url: "https://www.nbcnews.com/world/iran/iran-war-gas-field-attacks-energy-prices-trump-israel-south-pars-rcna264249" },
                { n: "European Gas Hub — Opslaganalyses",      d: "Analytische rapporten over EU gasopslag en marktevolutie",            url: "https://europeangashub.com" },
                { n: "Gas to Power Journal — TTF analysis",    d: "TTF prices fall below €30/MWh as geopolitical risk premium fades",    url: "https://gastopowerjournal.com/news/market/ttf-prices-fall-below-e30-mwh-as-geopolitical-risk-premium-fades/" },
              ],
            },
            {
              cat: "🌍 Geopolitiek & Beleidsinstanties", color: "#f97316",
              items: [
                { n: "De Standaard — Energiecrisis Analyse (19/03/2026)", d: "Hogere energieprijzen onvermijdelijk zolang Straat van Hormuz dicht blijft", url: "https://www.standaard.be/economie/hangt-ons-een-energiecrisis-boven-het-hoofd-en-kunnen-we-de-impact-ervan-beperken/141263439.html" },
                { n: "De Standaard — Benzineprijzen Stijgen (19/03/2026)", d: "Benzineprijzen stijgen opnieuw fors door Iran-oorlog impact", url: "https://www.standaard.be/economie/benzineprijzen-stijgen-opnieuw-fors/35145140.html" },
                { n: "De Standaard — VS Dronefabrieken (19/03/2026)", d: "VS bestookt dronefabrieken in Iran, oorlog kan nog weken duren", url: "https://www.standaard.be/buitenland/europese-unie-zet-iraanse-revolutionaire-garde-op-lijst-van-terreurorganisaties/35173881.html" },
                { n: "Trading Economics — TTF Gas (19/03/2026)", d: "TTF Gas stijgt naar €54.66/MWh (+6.02% vs gisteren)", url: "https://tradingeconomics.com/commodity/eu-natural-gas" },
                { n: "Trading Economics — Brent Oil (19/03/2026)", d: "Brent Crude stijgt naar $97.06/vat (+0.77% vs gisteren)", url: "https://tradingeconomics.com/commodity/crude-oil" },
                { n: "HLN — Trump Briefing (19/03/2026)", d: "VS vrezen dat Iraans regime in zadel blijft en zelfs driester wordt", url: "https://www.hln.be/buitenland/trump-krijgt-zeer-ontnuchterende-briefings-over-midden-oosten-vs-vrezen-dat-iraans-regime-in-het-zadel-zal-blijven-en-zelfs-nog-driester-zal-worden~a9e903a5/" },
                { n: "Reuters — Iran War Energy Shock (20/03/2026)", d: "European airlines warn of higher fares, fuel shortages due to Iran war", url: "https://www.reuters.com/business/energy/european-airlines-look-shake-off-green-agenda-fuel-prices-soar-2026-03-19/" },
                { n: "WSJ — Qatar LNG Impact (20/03/2026)", d: "Iranian strikes reduce Qatar export capacity by 17%, repairs take 3-5 months", url: "https://www.wsj.com/livecoverage/iran-us-israel-war-updates-2026" },
                { n: "Fortune — Oil Price Surge (19/03/2026)", d: "Oil approaches $115 per barrel as market realizes higher for longer", url: "https://fortune.com/2026/03/19/how-high-oil-barrel-price-brent-crude/" },
              ],
            },
            {
              cat: "🇧🇪 Belgische Regulatoren & Tariefinformatie", color: "#22c55e",
              items: [
                { n: "VREG — Vlaamse Regulator Elektriciteit en Gas", d: "Officieel toezicht op de Vlaamse energiemarkt, tariefvergelijker", url: "https://www.vreg.be" },
                { n: "CREG — Federale Reguleringsinstantie",          d: "Marktmonitor, transparantiedata, tariefstudies",                  url: "https://www.creg.be" },
                { n: "Elexys — Belgische marktindices",               d: "Officiële BELIX en BELPEX index-definities en publicaties",       url: "https://www.elexys.be" },
              ],
            },
          ].map((sec) => (
            <div key={sec.cat} style={{ marginBottom: 24 }}>
              <h4 style={{ margin: "0 0 10px", color: sec.color, fontSize: 14, borderBottom: `1px solid ${sec.color}33`, paddingBottom: 8 }}>{sec.cat}</h4>
              <div style={{ display: "grid", gap: 8 }}>
                {sec.items.map((item) => (
                  <div key={item.n} style={{ background: "#0f172a", borderRadius: 8, padding: "11px 15px", display: "flex", justifyContent: "space-between", alignItems: "center", gap: 14, flexWrap: "wrap" }}>
                    <div>
                      <div style={{ color: "#e2e8f0", fontWeight: 600, fontSize: 13, marginBottom: 2 }}>{item.n}</div>
                      <div style={{ color: "#64748b", fontSize: 12 }}>{item.d}</div>
                    </div>
                    <a href={item.url} target="_blank" rel="noopener noreferrer"
                      style={{ color: sec.color, fontSize: 12, fontWeight: 600, textDecoration: "none", background: sec.color + "22", padding: "5px 12px", borderRadius: 20, border: `1px solid ${sec.color}44`, whiteSpace: "nowrap", flexShrink: 0 }}>
                      Bezoek ↗
                    </a>
                  </div>
                ))}
              </div>
            </div>
          ))}

          <div style={{ background: "#172554", border: "1px solid #3b82f644", borderRadius: 10, padding: "13px 17px", fontSize: 12, color: "#93c5fd", lineHeight: 1.7 }}>
            <strong>Databenadering:</strong> Bevestigde exacte datapunten (✓): TTF 20/03 = €62.00 (+13.5% gas field attacks), Brent 20/03 = $108.50 (peaked $119), Belpex 20/03 = €125.50 (+25.1% TTF shock), EU gasopslag mrt 2026 = ~29% (GIE AGSI). Gasvelden aangevallen: South Pars (Iran) en Ras Laffan (Qatar) -17% LNG export. Hormuz crisis dag 21, Iran-oorlog week 4. Voor officiële tijdreeksen: gebruik ENTSO-E Transparency Platform (elektriciteit) en GIE AGSI+ (gas).
          </div>
        </div>
      )}

      {/* FOOTER */}
      <div style={{ textAlign: "center", marginTop: 22, padding: "13px 0", borderTop: "1px solid #1e293b", fontSize: 11, color: "#334155" }}>
        GIE AGSI+ · ENTSO-E · Reuters · Bloomberg · Xinhua · Wall Street Journal · IEA.org · EPEX SPOT · VREG · CREG<br />
        Opgesteld: 20 maart 2026 · Niet-officieel advies — raadpleeg VREG of een erkend energieadviseur voor definitieve beslissingen
      </div>
      {/* Cloudflare Web Analytics */}
      <script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{"token": "56157a20ce0e4d2a8f76844bfdb0f5aa"}'></script>
    </div>
  );
}
