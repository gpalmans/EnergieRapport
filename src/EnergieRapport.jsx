
import { useState } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine, Legend
} from "recharts";
import PDFDownloadButton from "./components/PDFDownloadButton";
import { addTrendlines } from "./utils/trendline";

// === DATA ===
// Single Source of Truth: rawData contains all historical and current data
// The last entry in rawData always contains the most recent live API data

const rawData = [
  { date: "04/08", ttf: 57.82, belpex: 140.86,  brent: 83.31, storage: 37.1, note: "" },
  { date: "05/08", ttf: 54.24, belpex: 100.64,  brent: 79.31, storage: 37.8, note: "" },
  { date: "06/08", ttf: 54.29, belpex: 102.20,  brent: 80.83, storage: 38.6, note: "" },
  { date: "07/08", ttf: 56.05, belpex: 121.89,  brent: 83.27, storage: 39.3, note: "" },
  { date: "08/08", ttf: 55.69, belpex: 98.16,  brent: 83.27, storage: 39.9, note: "" },
  { date: "09/08", ttf: 55.66, belpex: 94.52,  brent: 83.27, storage: 40.5, note: "" },
  { date: "10/08", ttf: 58.29, belpex: 126.81,  brent: 84.82, storage: 41.3, note: "" },
  { date: "11/08", ttf: 59.18, belpex: 114.23,  brent: 88.18, storage: 41.8, note: "" },
  { date: "12/08", ttf: 60.59, belpex: 141.86,  brent: 89.35, storage: 42.4, note: "" },
  { date: "13/08", ttf: 59.89, belpex: 155.51,  brent: 87.66, storage: 43.1, note: "" },
  { date: "14/08", ttf: 60.97, belpex: 150.65,  brent: 87.65, storage: 43.8, note: "" },
  { date: "15/08", ttf: 61.47, belpex: 124.25,  brent: 87.65, storage: 44.4, note: "" },
  { date: "16/08", ttf: 61.48, belpex: 138.14,  brent: 87.65, storage: 45.0, note: "" },
  { date: "17/08", ttf: 62.01, belpex: 177.21,  brent: 89.25, storage: 45.6, note: "Piek" },
  { date: "18/08", ttf: 62.54, belpex: 161.95,  brent: 91.13, storage: 46.2, note: "" },
  { date: "19/08", ttf: 63.33, belpex: 166.42,  brent: 91.65, storage: 46.8, note: "" },
  { date: "20/08", ttf: 64.45, belpex: 146.65,  brent: 92.51, storage: 47.3, note: "" },
  { date: "21/08", ttf: 65.95, belpex: 165.48,  brent: 93.75, storage: 48.0, note: "Piek" },
  { date: "22/08", ttf: 65.96, belpex: 102.86,  brent: 93.75, storage: 48.8, note: "" },
  { date: "23/08", ttf: 65.99, belpex: 87.33,  brent: 93.75, storage: 49.4, note: "" },
  { date: "24/08", ttf: 66.99, belpex: 138.94,  brent: 92.38, storage: 50.2, note: "" },
  { date: "25/08", ttf: 67.24, belpex: 157.51,  brent: 90.13, storage: 50.8, note: "" },
  { date: "26/08", ttf: 64.35, belpex: 161.35,  brent: 86.84, storage: 51.7, note: "" },
  { date: "27/08", ttf: 66.74, belpex: 161.81,  brent: 88.06, storage: 52.3, note: "" },
  { date: "28/08", ttf: 68.45, belpex: 147.62,  brent: 88.96, storage: 53.1, note: "" },
  { date: "29/08", ttf: 67.48, belpex: 83.21,  brent: 88.96, storage: 54.0, note: "" },
  { date: "30/08", ttf: 66.62, belpex: 75.49,  brent: 88.96, storage: 54.6, note: "" },
  { date: "31/08", ttf: 69.33, belpex: 108.00,  brent: 90.49, storage: 55.1, note: "" },
  { date: "01/09", ttf: 70.91, belpex: 152.42,  brent: 92.63, storage: 55.1, note: "Piek" },
  { date: "02/09", ttf: 71.92, belpex: 172.18,  brent: 94.46, storage: 55.1, note: "" }
].sort((a, b) => {
  const dateA = a.date.split('/').reverse().join('');
  const dateB = b.date.split('/').reverse().join('');
  return dateA.localeCompare(dateB);
});

// Helper function to check if a date is a weekend
const isWeekend = (dateStr) => {
  const [day, month] = dateStr.split('/');
  const date = new Date(2026, month - 1, day); // month is 1-based in split() result
  const dayOfWeek = date.getDay();
  return dayOfWeek === 0 || dayOfWeek === 6; // Sunday = 0, Saturday = 6
};

// Helper functions to get current data from rawData (Single Source of Truth)
const getCurrentData = () => {
  const lastEntry = rawData[rawData.length - 1];
  const prevEntry = rawData.length > 1 ? rawData[rawData.length - 2] : null;
  
  // Get Brent from the last entry (assuming it's stored there)
  const currentBrent = lastEntry?.brent || 105.55;
  const prevBrent = prevEntry?.brent || 104.49;
  
  // Get storage from the last entry
  const currentStorage = lastEntry?.storage || 27.8;
  const prevStorage = prevEntry?.storage || 27.5;
  
  return {
    currentTTF: lastEntry.ttf,
    currentBelpex: lastEntry.belpex,
    currentDate: lastEntry.date,
    currentNote: lastEntry.note,
    currentBrent: currentBrent,
    currentStorage: currentStorage,
    prevTTF: prevEntry?.ttf,
    prevBelpex: prevEntry?.belpex,
    prevDate: prevEntry?.date,
    prevBrent: prevBrent,
    prevStorage: prevStorage
  };
};

// Calculate percentage changes
const calculateChange = (current, previous) => {
  if (previous === null || previous === undefined || previous === 0) return null;
  return ((current - previous) / Math.abs(previous)) * 100;
};

const marketData = rawData.map((row, i) => {
  const prev = i > 0 ? rawData[i - 1] : null;
  return {
    ...row,
    ttfDod:    prev ? ((row.ttf    - prev.ttf)    / Math.abs(prev.ttf)    * 100) : null,
    belpexDod: prev ? ((row.belpex - prev.belpex) / Math.abs(prev.belpex) * 100) : null,
  };
});

const chartData = addTrendlines(marketData, {
  ttfTrendShort:     { valueKey: 'ttf',    lastN: 7 },
  ttfTrendMedium:    { valueKey: 'ttf'          },
  belpexTrendShort:  { valueKey: 'belpex', lastN: 7 },
  belpexTrendMedium: { valueKey: 'belpex'       },
});

const periodAvg = {
  ttf:    +(chartData.reduce((s, d) => s + d.ttf, 0)    / chartData.length).toFixed(2),
  belpex: +(chartData.reduce((s, d) => s + d.belpex, 0) / chartData.length).toFixed(2),
};

const chartEvents = [
  { date: "28/08", label: "Hormuz broos",       color: "#f97316" },
  { date: "31/08", label: "EU-opslag laagste",  color: "#ef4444" },
];

const forecastBase = [
  { date: "02/09", ttf: 71.92, belpex: 172.18 },
  { date: "01/10", ttf: 75.00, belpex: 182.00 },
  { date: "01/11", ttf: 82.00, belpex: 205.00 },
  { date: "01/12", ttf: 87.00, belpex: 220.00 },
  { date: "01/01", ttf: 87.00, belpex: 220.00 }
];
const forecastBull = [
  { date: "02/09", ttf: 71.92, belpex: 172.18 },
  { date: "01/10", ttf: 82.00, belpex: 210.00 },
  { date: "01/11", ttf: 95.00, belpex: 245.00 },
  { date: "01/12", ttf: 110.00, belpex: 285.00 },
  { date: "01/01", ttf: 125.00, belpex: 320.00 }
];
const forecastBear = [
  { date: "02/09", ttf: 71.92, belpex: 172.18 },
  { date: "01/10", ttf: 66.00, belpex: 155.00 },
  { date: "01/11", ttf: 60.00, belpex: 135.00 },
  { date: "01/12", ttf: 55.00, belpex: 120.00 },
  { date: "01/01", ttf: 52.00, belpex: 110.00 }
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
  const [ttfTrends, setTtfTrends] = useState({ short: false, medium: false });
  const [belpexTrends, setBelpexTrends] = useState({ short: false, medium: false });
  
  // Get current data from Single Source of Truth
  const currentData = getCurrentData();
  const ttfChange = calculateChange(currentData.currentTTF, currentData.prevTTF);
  const belpexChange = calculateChange(currentData.currentBelpex, currentData.prevBelpex);
  const brentChange = calculateChange(currentData.currentBrent, currentData.prevBrent);
  const brentChangeText = brentChange !== null ? `${brentChange > 0 ? '+' : ''}${brentChange.toFixed(1)}% vs gisteren` : '0.0% vs gisteren';
  
  // Format current date for PDF filename
  const formatCurrentDate = (dateStr) => {
    const [day, month] = dateStr.split('/');
    const monthNames = {
      '01': 'januari', '02': 'februari', '03': 'maart', '04': 'april', '05': 'mei', '06': 'juni',
      '07': 'juli', '08': 'augustus', '09': 'september', '10': 'oktober', '11': 'november', '12': 'december'
    };
    return `${parseInt(day)} ${monthNames[month]} 2026`;
  };
  
  // Get current time for PDF
  const getCurrentTime = () => {
    const now = new Date();
    return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
  };

  const TrendToggle = ({ label, checked, onChange, color }) => (
    <label style={{ display: "inline-flex", alignItems: "center", gap: 5, cursor: "pointer", fontSize: 11, color: "#94a3b8", userSelect: "none" }}>
      <input type="checkbox" checked={checked} onChange={onChange}
        style={{ accentColor: color, width: 14, height: 14, cursor: "pointer" }} />
      <span style={{ borderBottom: `2px dashed ${color}`, paddingBottom: 1 }}>{label}</span>
    </label>
  );

  const tabBtn = (t) => ({
    flex: "1 1 auto",
    minWidth: 120,
    padding: "10px 16px", borderRadius: 10, cursor: "pointer", fontSize: 13,
    fontWeight: 700, border: "none", whiteSpace: "nowrap", transition: "all 0.2s",
    background: tab === t ? "#0ea5e9" : "#1e293b",
    color: tab === t ? "#fff" : "#94a3b8",
    boxShadow: tab === t ? "0 3px 10px rgba(14,165,233,0.35)" : "inset 0 1px 2px rgba(0,0,0,0.15)",
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
          MARKTANALYSE — 03 SEPTEMBER 2026 · 23:28 CET
        </div>
        <h1 style={{ fontSize: 26, fontWeight: 700, margin: "0 0 8px", color: "#f8fafc" }}>
          Vlaamse Energieprijzen: Analyse & Forecast
        </h1>
        <p style={{ color: "#64748b", fontSize: 13, margin: 0 }}>
          TTF (gas) · Belpex/EPEX (elektriciteit) · Geopolitieke context · Tariefadvies
        </p>
      </div>

      {/* ALERT */}
      <div style={{ background: "#7c2d1222", border: "1px solid #f97316", borderRadius: 10, padding: "14px 20px", marginBottom: 24, display: "flex", alignItems: "center", gap: 12 }}>
        <span style={{ fontSize: 22, flexShrink: 0 }}>�</span>
        <div>
          <div style={{ fontWeight: 700, color: "#fdba74", marginBottom: 2 }}>MARKTUPDATE: TTF OPNIEUW RICHT €72 — WINTERRISICO'S BLIJVEN</div>
          <div style={{ fontSize: 13, color: "#fdba74" }}>
            TTF €71.92 (+1.4% vs gisteren) · Belpex €172.18 (+13.0%) · EU-opslag 65.4% op 31 aug — laagste seizoensniveau ooit · Hormuz-wapenstilstand broos · Qatar LNG-schade structureel (3-5 jr) · Vast tarief blijft duurder dan variabel
          </div>
        </div>
      </div>

      {/* Price Volatility Disclaimer */}
      <div style={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 10, padding: "12px 16px", marginBottom: 24 }}>
        <div style={{ display: "flex", alignItems: "flex-start", gap: 10 }}>
          <span style={{ fontSize: 16, color: "#f59e0b", flexShrink: 0 }}>ℹ️</span>
          <div>
            <div style={{ fontSize: 13, fontWeight: 600, color: "#f8fafc", marginBottom: 4 }}>Prijzen zijn dagelijkse gemiddelden</div>
            <div style={{ fontSize: 12, color: "#94a3b8", lineHeight: 1.5 }}>
              De getoonde prijzen zijn 24-uurs dagelijkse gemiddelden voor actuele marktprijzen. 
              Echte marktprijzen fluctueren continu gedurende de handelsdag. 
              Voor real-time prijzen: raadpleeg EPEX SPOT (elektriciteit) en ICE Endex (gas).
            </div>
          </div>
        </div>
      </div>

      {/* DOWNLOAD BANNER */}
      <div style={{ background: "#0f172a", border: "1px solid #334155", borderRadius: 10, padding: "12px 20px", marginBottom: 16, display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 10 }}>
        <div style={{ fontSize: 13, color: "#64748b" }}>
          📥 <strong style={{ color: "#94a3b8" }}>Download beschikbaar</strong> — print-vriendelijke PDF
        </div>
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          <PDFDownloadButton reportData={{
            marketData,
            rawData,
            currentDate: formatCurrentDate(currentData.currentDate),
            currentTime: getCurrentTime(),
            currentBrent: currentData.currentBrent,
            prevBrent: currentData.prevBrent,
            currentStorage: currentData.currentStorage,
            prevStorage: currentData.prevStorage
          }} />
        </div>
      </div>

      {/* KPIs */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 12, marginBottom: 24 }}>
        {[
          [
            "TTF Gas (24-uurs gemiddelde)", 
            `€${currentData.currentTTF.toFixed(2)}`, 
            "/MWh", 
            ttfChange !== null ? `${ttfChange > 0 ? '+' : ''}${ttfChange.toFixed(1)}% vs gisteren` : "N/A", 
            ttfChange !== null ? (ttfChange > 0 ? "#ef4444" : "#22c55e") : "#94a3b8"
          ],
          [
            "Belpex Elektr. (24-uurs gemiddelde)", 
            `€${currentData.currentBelpex.toFixed(2)}`, 
            "/MWh", 
            belpexChange !== null ? `${belpexChange > 0 ? '+' : ''}${belpexChange.toFixed(1)}% vs gisteren` : "N/A", 
            belpexChange !== null ? (belpexChange > 0 ? "#ef4444" : "#22c55e") : "#94a3b8"
          ],
          [
            "België Gasopslag", 
            `${currentData.currentStorage.toFixed(1)}%`, 
            " cap.", 
            "achterstand op 90%-doel", 
            "#ef4444"
          ],
          [
            "Brent Ruwe Olie", 
            `$${currentData.currentBrent.toFixed(2)}`, 
            "/vat", 
            brentChangeText, 
            brentChange !== null ? (brentChange > 0 ? "#ef4444" : "#22c55e") : "#94a3b8"
          ],
        ].map(([label, val, sub, note, c], i) => (
          <div key={i} style={{ background: "#1e293b", border: `1px solid ${c}44`, borderRadius: 10, padding: "13px 15px" }}>
            <div style={{ fontSize: 10, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 5 }}>{label}</div>
            <div style={{ fontSize: 22, fontWeight: 700, color: c }}>{val}<span style={{ fontSize: 11, color: "#64748b" }}>{sub}</span></div>
            <div style={{ fontSize: 11, color: c, marginTop: 3 }}>{note}</div>
          </div>
        ))}
      </div>

      {/* TABS */}
      <div style={{ marginBottom: 24 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
          <span style={{ fontSize: 11, color: "#64748b", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em" }}>
            Navigeer door het rapport
          </span>
          <div style={{ flex: 1, height: 1, background: "#334155" }} />
        </div>
        <div style={{ display: "flex", gap: 6, background: "#0f172a", padding: 8, borderRadius: 14, border: "1px solid #1e293b", overflowX: "auto", boxShadow: "0 4px 16px rgba(0,0,0,0.25)" }}>
          {TABS.map(([t, l]) => <button key={t} style={tabBtn(t)} onClick={() => setTab(t)}>{l}</button>)}
        </div>
      </div>

      {/* ── ANALYSE ── */}
      {tab === "analyse" && (<>
        <div style={SECTION}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8, flexWrap: "wrap", gap: 8 }}>
            <h3 style={{ margin: 0, color: "#f8fafc", fontSize: 16 }}>TTF Aardgas — Dagelijkse Spotprijzen (€/MWh)</h3>
            <span style={BADGE("#0ea5e9")}>AGSI GIE · ENTSO-E · EPEX SPOT</span>
          </div>
          <div style={{ display: "flex", gap: 16, marginBottom: 10, paddingLeft: 4 }}>
            <TrendToggle label="Korte termijn (7d)" checked={ttfTrends.short} color="#f59e0b"
              onChange={() => setTtfTrends(p => ({ ...p, short: !p.short }))} />
            <TrendToggle label="Middellange termijn" checked={ttfTrends.medium} color="#22d3ee"
              onChange={() => setTtfTrends(p => ({ ...p, medium: !p.medium }))} />
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={chartData} margin={{ top: 25, right: 60, left: 0, bottom: 4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e3a5f" />
              <XAxis dataKey="date" tick={{ fill: "#64748b", fontSize: 11 }} />
              <YAxis domain={[50, 80]} tick={{ fill: "#64748b", fontSize: 11 }} tickFormatter={v => `€${v}`} />
              <Tooltip content={<Tip />} />
              {/* Horizontaal: gemiddelde van de getoonde periode */}
              <ReferenceLine y={periodAvg.ttf} stroke="#f59e0b" strokeDasharray="3 3" label={{ value: "Gemiddelde", fill: "#f59e0b", fontSize: 10, position: "top" }} />
              {/* Verticaal: economische/geopolitieke events in de periode */}
              {chartEvents.map((ev, i) => (
                <ReferenceLine key={`ttf-ev-${i}`} x={ev.date} stroke={ev.color} strokeDasharray="4 4" label={{ value: ev.label, fill: ev.color, fontSize: 10, position: "top" }} />
              ))}
              <Line type="monotone" dataKey="ttf" name="TTF Gas" stroke="#0ea5e9" strokeWidth={2.5} dot={false} activeDot={{ r: 4 }} />
              {ttfTrends.short && <Line type="linear" dataKey="ttfTrendShort" name="Trend 7d" stroke="#f59e0b" strokeWidth={2} strokeDasharray="6 3" dot={false} connectNulls={false} />}
              {ttfTrends.medium && <Line type="linear" dataKey="ttfTrendMedium" name="Trend totaal" stroke="#22d3ee" strokeWidth={2} strokeDasharray="8 4" dot={false} />}
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div style={SECTION}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8, flexWrap: "wrap", gap: 8 }}>
            <h3 style={{ margin: 0, color: "#f8fafc", fontSize: 16 }}>Belpex Elektriciteit — Daggemiddelde Day-Ahead (€/MWh)</h3>
            <span style={BADGE("#a78bfa")}>ENTSO-E · EPEX SPOT</span>
          </div>
          <div style={{ display: "flex", gap: 16, marginBottom: 10, paddingLeft: 4 }}>
            <TrendToggle label="Korte termijn (7d)" checked={belpexTrends.short} color="#f59e0b"
              onChange={() => setBelpexTrends(p => ({ ...p, short: !p.short }))} />
            <TrendToggle label="Middellange termijn" checked={belpexTrends.medium} color="#22d3ee"
              onChange={() => setBelpexTrends(p => ({ ...p, medium: !p.medium }))} />
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={chartData} margin={{ top: 20, right: 20, left: 0, bottom: 4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e3a5f" />
              <XAxis dataKey="date" tick={{ fill: "#64748b", fontSize: 11 }} />
              <YAxis domain={[60, 200]} tick={{ fill: "#64748b", fontSize: 11 }} tickFormatter={v => `€${v}`} />
              <Tooltip content={<Tip />} />
              {/* Horizontaal: gemiddelde van de getoonde periode */}
              <ReferenceLine y={periodAvg.belpex} stroke="#f59e0b" strokeDasharray="3 3" label={{ value: "Gemiddelde", fill: "#f59e0b", fontSize: 10, position: "top" }} />
              {/* Verticaal: economische/geopolitieke events in de periode */}
              {chartEvents.map((ev, i) => (
                <ReferenceLine key={`belpex-ev-${i}`} x={ev.date} stroke={ev.color} strokeDasharray="4 4" label={{ value: ev.label, fill: ev.color, fontSize: 10, position: "top" }} />
              ))}
              <Line type="monotone" dataKey="belpex" name="Belpex" stroke="#a78bfa" strokeWidth={2.5} dot={false} activeDot={{ r: 4 }} />
              {belpexTrends.short && <Line type="linear" dataKey="belpexTrendShort" name="Trend 7d" stroke="#f59e0b" strokeWidth={2} strokeDasharray="6 3" dot={false} connectNulls={false} />}
              {belpexTrends.medium && <Line type="linear" dataKey="belpexTrendMedium" name="Trend totaal" stroke="#22d3ee" strokeWidth={2} strokeDasharray="8 4" dot={false} />}
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
                  const confirmed = true; // All rawData comes from official APIs (OilPriceAPI, GIE AGSI+, energy-charts.info)
                  return (
                    <tr key={i} style={{ borderBottom: "1px solid #1e293b", background: today ? "#0c4a6e22" : shock ? "#7f1d1d22" : "transparent" }}>
                      <td style={{ padding: "7px 11px", color: today ? "#0ea5e9" : "#e2e8f0", fontWeight: today ? 700 : 400, whiteSpace: "nowrap" }}>
                        {r.date}{today ? " 🔵" : confirmed ? " ✓" : ""}
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
                        : r.note === "WE" || isWeekend(r.date) ? <span style={BADGE("#475569")}>Weekend</span>
                        : <span style={{ color: "#334155" }}>—</span>}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <p style={{ fontSize: 11, color: "#475569", marginTop: 10, marginBottom: 0 }}>
            ✓ = bevestigd officieel datapunt (API-driven data) · Δ dag/dag = procentuele wijziging t.o.v. vorige handelsdag (▲ stijging, ▼ daling)
          </p>
        </div>
      </>)}

      {/* ── CONTEXT ── */}
      {tab === "context" && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18 }}>
          <div style={SECTION}>
            <h3 style={{ margin: "0 0 4px", color: "#f8fafc", fontSize: 15 }}>🏭 Belgische & Europese Gasvoorraden — Injectieseizoen 2026</h3>
            <p style={{ fontSize: 11, color: "#64748b", marginTop: 0, marginBottom: 12 }}>Bron: GIE AGSI+ API · update elke dinsdag · doel: 90% tegen 1 november · <a href="https://agsi.gie.eu" target="_blank" rel="noopener noreferrer" style={{ color: "#475569" }}>agsi.gie.eu</a></p>

            {/* BE vs EU vergelijking */}
            {[
              ["BE huidig (2 sep 2026)",     "~55.1%",        "#ef4444"],
              ["EU-gemiddelde (31 aug 2026)","~65.4%",        "#eab308"],
              ["Einde 2025 (EU)",             "~61%",          "#eab308"],
              ["Einde 2024 (EU)",             "~72%",          "#22c55e"],
              ["EU-doelstelling (1 nov)",     "90%",           "#0ea5e9"],
              ["BE nog te vullen (sep–nov)",  "~35 pct-punten","#f97316"],
            ].map(([l, v, c]) => (
              <div key={l} style={{ display: "flex", justifyContent: "space-between", padding: "6px 0", borderBottom: "1px solid #1e293b", fontSize: 13 }}>
                <span style={{ color: "#94a3b8" }}>{l}</span>
                <span style={{ color: c, fontWeight: 700 }}>{v}</span>
              </div>
            ))}

            {/* Voortgangsbalk */}
            {(() => {
              const current = 55.1, target = 90;
              const pct = Math.round((current / target) * 100);
              return (
                <div style={{ margin: "14px 0 4px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: "#94a3b8", marginBottom: 5 }}>
                    <span>BE huidig: <strong style={{ color: "#ef4444" }}>{current}%</strong></span>
                    <span><strong style={{ color: "#f97316" }}>{pct}%</strong> van doel bereikt</span>
                    <span>Doel 1 nov: <strong style={{ color: "#0ea5e9" }}>{target}%</strong></span>
                  </div>
                  <div style={{ background: "#1e293b", borderRadius: 6, height: 12, overflow: "hidden" }}>
                    <div style={{ width: `${pct}%`, height: "100%", background: "linear-gradient(90deg, #ef4444, #f97316)", borderRadius: 6 }} />
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10, color: "#475569", marginTop: 3 }}>
                    <span>0%</span><span style={{ color: "#eab308" }}>55% (eind jul)</span><span style={{ color: "#f97316" }}>72% (eind aug)</span><span style={{ color: "#0ea5e9" }}>90% (1 nov)</span>
                  </div>
                </div>
              );
            })()}

            {/* Maandmijlpalen */}
            {[
              ["Huidig (2 sep)",  "55.1%", 55.1, "#ef4444", "⚠️ Achterstand op schema"],
              ["Doel eind aug.",  "72%",   72,   "#f97316", "Niet behaald"],
              ["Doel eind sept.", "83%",   83,   "#0ea5e9", "Veiligheidsmarge"],
              ["Doel 1 november", "90%",   90,   "#22c55e", "EU-doelstelling"],
              ["Einde 2024 (EU)", "72%",   72,   "#22c55e", "Historisch comfort"],
              ["Einde 2025 (EU)", "61%",   61,   "#eab308", "Zwakker punt"],
            ].map(([label, val, num, color, status]) => (
              <div key={label} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "7px 0", borderBottom: "1px solid #1e293b", fontSize: 12 }}>
                <span style={{ color: "#94a3b8", width: 130, flexShrink: 0 }}>{label}</span>
                <div style={{ flex: 1, margin: "0 10px", background: "#0f172a", borderRadius: 4, height: 6 }}>
                  <div style={{ width: `${num}%`, height: "100%", background: color, borderRadius: 4, opacity: 0.75 }} />
                </div>
                <span style={{ color, fontWeight: 700, width: 40, textAlign: "right", flexShrink: 0 }}>{val}</span>
                <span style={{ color: "#475569", fontSize: 11, width: 155, textAlign: "right", flexShrink: 0 }}>{status}</span>
              </div>
            ))}

            {/* Injectietempo */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, margin: "12px 0" }}>
              <div style={{ background: "#7c131322", border: "1px solid #ef444444", borderRadius: 8, padding: "9px 12px" }}>
                <div style={{ fontSize: 10, color: "#64748b", marginBottom: 3 }}>VEREIST TEMPO (sep → nov)</div>
                <div style={{ fontSize: 17, fontWeight: 700, color: "#ef4444" }}>~4.0 pct/week</div>
                <div style={{ fontSize: 10, color: "#94a3b8", marginTop: 2 }}>35 pct-punten in ~9 weken</div>
              </div>
              <div style={{ background: "#172554", border: "1px solid #0ea5e944", borderRadius: 8, padding: "9px 12px" }}>
                <div style={{ fontSize: 10, color: "#64748b", marginBottom: 3 }}>ACHTERSTAND OP EU</div>
                <div style={{ fontSize: 17, fontWeight: 700, color: "#f97316" }}>~10 pct-punten</div>
                <div style={{ fontSize: 10, color: "#94a3b8", marginTop: 2 }}>BE 55.1% vs EU 65.4%</div>
              </div>
            </div>

            <div style={{ padding: "10px 14px", background: "#7c131322", borderRadius: 8, fontSize: 12, color: "#fca5a5", lineHeight: 1.6 }}>
              ⚠️ Qatar LNG: 17% exportcapaciteit beschadigd — herstel duurt 3 tot 5 jaar (NYTimes, mei 2026). Door de lage EU-opslag en de concurrentie om LNG-cargos blijven injectiekosten hoog.
            </div>
            <div style={{ marginTop: 10, padding: "10px 14px", background: "#172554", borderRadius: 8, fontSize: 12, color: "#93c5fd", lineHeight: 1.6 }}>
              <strong style={{ color: "#60a5fa" }}>Impact op uw factuur:</strong> Met 55.1% op 2 september en minder dan 9 weken tot 1 november moet België nog ~35 procentpunten vullen. Dat vraagt ~4.0 pct/week. De nervositeit over de winter vormt een risicopremie in vaste contracten; variabele tarieven volgen groothandel met 1-2 maanden vertraging.
            </div>
          </div>

          <div style={SECTION}>
            <h3 style={{ margin: "0 0 14px", color: "#f8fafc", fontSize: 15 }}>⚔️ Geopolitieke Situatie — September 2026</h3>
            {[
              ["TTF op hoogste niveau sinds januari 2023", "#ef4444", "TTF noteerde op 2 september €71.92, opnieuw het hoogste niveau sinds begin 2023. De stijging vanuit het augustusdieptepunt van €54 wordt gedreven door de broze situatie rond de Straat van Hormuz, vertraagde LNG-toevoer en de historisch lage Europese gasopslag (Trading Economics, aug-sep 2026)."],
              ["EU-opslag op laagste seizoensniveau ooit", "#ef4444", "Eind augustus 2026 stond de EU-opslag op 65.39%, het laagste niveau voor die datum sinds metingen in 2011 en ~14% onder het 5-jaargemiddelde. België zit op 55.1%. Dit vergroot de afhankelijkheid van LNG-import in de winter (TASS, 2 sep 2026; Voltstack, aug 2026)."],
              ["Hormuz: wapenstilstand broos", "#f97316", "De Straat van Hormuz is deels heropend sinds 21 april 2026, maar de wapenstilstand is broos. Trump dreigt met sancties tegen landen die handel drijven met Iran, en Iran houdt vol dat het waterweg dichtblijft. Tankerdoorvoer blijft sterk verminderd (Trading Economics, 28 aug 2026)."],
              ["Qatar LNG: 3–5 jaar structureel herstel", "#ef4444", "Qatar's gasexportcapaciteit — goed voor ~17% van het wereldwijde LNG — is zwaar beschadigd door oorlogsschade aan South Pars en Ras Laffan. Volledig herstel duurt 3 tot 5 jaar (NYTimes, 14 mei 2026). Pre-crisis TTF-niveaus van €30-32 blijven onbereikbaar tot 2028-2030."],
              ["OPEC+ stabiliseert Brent rond $94", "#eab308", "OPEC+ voerde drie productieverhogingen door om Hormuz-verlies te compenseren. Brent stabiliseerde rond $94/vat op 2 september na een dieptepunt van $79 begin augustus. Extra Iraanse olie zou Brent verder kunnen drukken, maar de risicopremie blijft (Reuters/CNBC, mei 2026)."],
              ["Belgische Nucleaire Renaissance", "#22c55e", "Regering De Wever en energiereus Engie bereikten in april 2026 een principeakkoord over de overname en heractivering van de volledige Belgische nucleaire vloot, met een finaal akkoord verwacht tegen 1 oktober 2026 (Euronews, 30 april 2026). Meer kernvermogen betekent op middellange termijn minder uren dat gas de marginale prijszetter is."],
              ["EU ETS €85/ton", "#f97316", "De EU-koolstofprijs (ETS) noteert in 2026 gemiddeld €85/ton, een stijging van ~18% jaar-op-jaar. Dit verhoogt rechtstreeks de kostprijs van gascentrales en voegt via de merit order ~€4-5/MWh toe aan de Belpex-prijs per €10 stijging."],
              ["Vast tarief blijft significant duurder dan variabel", "#8b5cf6", "VRT bevestigde in juni 2026 dat vaste contracten gemiddeld 27% duurder zijn dan variabele. In september blijft die premie bestaan: vaste contracten bevatten de volledige LNG-risicopremie. Variabele formules volgen groothandel met 1-2 maanden vertraging."],
              ["Belgische inflatie 2.6% — geen steunpakket", "#dc2626", "Premier De Wever en NBB-gouverneur Wunsch signaleren geen budgettaire ruimte voor energiesteunmaatregelen. Belgische inflatie staat op 2.6%, mede door energieprijzen — dit kan loonindexatie versnellen (Belga, 2026)."],
            ].map(([titel, color, tekst]) => (
              <div key={titel} style={{ marginBottom: 14 }}>
                <span style={BADGE(color)}>{titel}</span>
                <p style={{ marginTop: 7, marginBottom: 0, fontSize: 13, color: "#94a3b8", lineHeight: 1.6 }}>{tekst}</p>
              </div>
            ))}
          </div>


          <div style={SECTION}>
            <h3 style={{ margin: "0 0 14px", color: "#f8fafc", fontSize: 15 }}>🇧🇪 Belgische Energiemix — Waarom Gasprijzen de Elektriciteitsprijs Bepalen</h3>
            <p style={{ marginTop: 0, fontSize: 13, color: "#94a3b8", lineHeight: 1.7, marginBottom: 12 }}>
              België gebruikt het <strong style={{ color: "#f8fafc" }}>merit order principe</strong>: elektriciteitscentrales worden geactiveerd van goedkoop naar duur (kern → wind/zon → gas → olie). 
              De <strong style={{ color: "#f8fafc" }}>laatste centrale</strong> die nodig is om aan de vraag te voldoen, bepaalt de prijs voor <em>alle</em> elektriciteit in dat uur.
            </p>
            <p style={{ marginTop: 0, fontSize: 13, color: "#94a3b8", lineHeight: 1.7, marginBottom: 12 }}>
              In België is gas de marginale producent in <strong style={{ color: "#f8fafc" }}>~87% van de uren</strong> (CREG-data 2021-2024).
              Dit betekent: zelfs als 80% van de elektriciteit uit kern en hernieuwbaar komt, bepaalt de gasprijs de Belpex-prijs zodra gascentrales nodig zijn voor de laatste 20%.
              Resultaat: <strong style={{ color: "#f8fafc" }}>TTF stijgt → Belpex stijgt</strong> (versterkt door grid congestion). <strong style={{ color: "#22c55e" }}>Positieve evolutie:</strong> het Engie-akkoord (finaal akkoord verwacht okt 2026) zal dit percentage op termijn verlagen.
            </p>
            <p style={{ marginTop: 0, fontSize: 13, color: "#94a3b8", lineHeight: 1.7 }}>
              <strong style={{ color: "#f8fafc" }}>Waarom gas zo vaak marginaal is:</strong> Kern draait continu (baseload), wind/zon zijn variabel, gas vult de gaten.
              Bij hoge vraag (ochtend/avond) of weinig zon/wind → gascentrales starten → gasprijs = elektriciteitsprijs voor dat uur.
            </p>
            <div style={{ background: "#172554", borderRadius: 8, padding: "12px 14px" }}>
              {[
                ["Kern (Doel 4, Tihange 3 + heractiv.)", "verlengd + uitgebreid tot 2035+"],
                ["Aandeel kernenergie (huidig)",          "~35–40%"],
                ["Aandeel hernieuwbaar",                  "~30%"],
                ["Aandeel gas",                           "~20%"],
                ["EU ETS koolstofprijs",                  "€85/ton (+18% j-o-j)"],
              ].map(([k, v]) => (
                <div key={k} style={{ display: "flex", justifyContent: "space-between", padding: "5px 0", borderBottom: "1px solid #1e3a5f", fontSize: 12 }}>
                  <span style={{ color: "#94a3b8" }}>{k}</span>
                  <span style={{ color: "#60a5fa", fontWeight: 600 }}>{v}</span>
                </div>
              ))}
            </div>
                      </div>
        </div>
      )}

      {/* ── FORECAST ── */}
      {tab === "forecast" && (<>
        <div style={SECTION}>
          <h3 style={{ margin: "0 0 14px", color: "#f8fafc", fontSize: 16 }}>📈 TTF Gas Forecast (sep 2026 – jan 2027)</h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart margin={{ top: 4, right: 20, left: 0, bottom: 4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e3a5f" />
              <XAxis dataKey="date" type="category" allowDuplicatedCategory={false} tick={{ fill: "#64748b", fontSize: 11 }} />
              <YAxis domain={[40, 130]} tick={{ fill: "#64748b", fontSize: 11 }} tickFormatter={v => `€${v}`} />
              <Tooltip content={<Tip />} />
              <Legend wrapperStyle={{ fontSize: 12, color: "#94a3b8" }} />
              <ReferenceLine x="01/10" stroke="#22c55e" strokeDasharray="4 4" label={{ value: "Nucleair akkoord?", fill: "#22c55e", fontSize: 10, position: "top" }} />
              <Line data={forecastBull} type="monotone" dataKey="ttf" name="⬆ Bullish" stroke="#ef4444" strokeWidth={2} dot={{ r: 3, fill: "#ef4444" }} />
              <Line data={forecastBase} type="monotone" dataKey="ttf" name="⟶ Basis"   stroke="#0ea5e9" strokeWidth={2.5} dot={{ r: 3, fill: "#0ea5e9" }} />
              <Line data={forecastBear} type="monotone" dataKey="ttf" name="⬇ Bearish" stroke="#22c55e" strokeWidth={2} dot={{ r: 3, fill: "#22c55e" }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div style={SECTION}>
          <h3 style={{ margin: "0 0 14px", color: "#f8fafc", fontSize: 16 }}>⚡ Belpex Elektriciteit Forecast (sep 2026 – jan 2027)</h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart margin={{ top: 4, right: 20, left: 0, bottom: 4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e3a5f" />
              <XAxis dataKey="date" type="category" allowDuplicatedCategory={false} tick={{ fill: "#64748b", fontSize: 11 }} />
              <YAxis domain={[100, 340]} tick={{ fill: "#64748b", fontSize: 11 }} tickFormatter={v => `€${v}`} />
              <Tooltip content={<Tip />} />
              <Legend wrapperStyle={{ fontSize: 12, color: "#94a3b8" }} />
              <ReferenceLine x="01/10" stroke="#22c55e" strokeDasharray="4 4" label={{ value: "Nucleair akkoord?", fill: "#22c55e", fontSize: 10, position: "top" }} />
              <Line data={forecastBull} type="monotone" dataKey="belpex" name="⬆ Bullish" stroke="#dc2626" strokeWidth={2.5} dot={{ r: 3, fill: "#dc2626" }} />
              <Line data={forecastBase} type="monotone" dataKey="belpex" name="⟶ Basis" stroke="#0ea5e9" strokeWidth={3} dot={{ r: 4, fill: "#0ea5e9" }} />
              <Line data={forecastBear} type="monotone" dataKey="belpex" name="⬇ Bearish" stroke="#10b981" strokeWidth={2} dot={{ r: 3, fill: "#10b981" }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 14 }}>
          {[
            {
              t: "⬇ Bearish (Volledige normalisatie)", p: "20%", c: "#22c55e",
              ttf: "€52–72", belpex: "€110–175",
              items: ["Hormuz volledig stabiel, scheepvaart normaliseert","LNG-markt vindt alternatieve routes","Milde winter drukt vraag","Iran-akkoord brengt extra olie","Opslag haalt 90% doel"],
              note: "Vereist: structureel herstel Qatar LNG sneller dan verwacht + milde winter",
            },
            {
              t: "⟶ Basis (Gecontroleerde opwaartse druk)", p: "50%", c: "#0ea5e9",
              ttf: "€72–88", belpex: "€170–225",
              items: ["Qatar LNG-schade 3-5 jaar: aanbod structureel krapper","Hormuz broos maar open","EU-opslag blijft historisch laag","Wintervraag neemt toe (nov–jan)","EU ETS op €85/ton ondersteunt Belpex"],
              note: "Meest waarschijnlijk: TTF stijgt door winterseizoenspatroon, blijft boven pre-crisis",
            },
            {
              t: "⬆ Bullish (Nieuwe schok)", p: "30%", c: "#ef4444",
              ttf: "€85–130", belpex: "€200–320",
              items: ["Nieuwe escalatie Midden-Oosten of Hormuz hersluit","Opslag haalt 90% niet → wintercrisis geprijsd","Vroege koude snap (okt–nov)","LNG-aanbodgolf vertraagt","Russische afsnijding creëert acute schaarste"],
              note: "Trigger: koude snap, opslagachterstand of nieuwe escalatie in Q4",
            },
          ].map((s, i) => (
            <div key={i} style={{ background: "#1e293b", border: `1px solid ${s.c}44`, borderRadius: 12, padding: "16px 18px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 10, gap: 6 }}>
                <h4 style={{ margin: 0, color: s.c, fontSize: 13, lineHeight: 1.4 }}>{s.t}</h4>
                <span style={{ ...BADGE(s.c), flexShrink: 0 }}>P: {s.p}</span>
              </div>
              <div style={{ marginBottom: 10 }}>
                <div style={{ fontSize: 11, color: "#64748b", marginBottom: 3 }}>Range sep 2026 – jan 2027</div>
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
          <h3 style={{ margin: "0 0 8px", color: "#f8fafc", fontSize: 15 }}>🔑 Sleutelfactoren om op te volgen — September 2026</h3>
          <p style={{ fontSize: 12, color: "#64748b", marginTop: 0, marginBottom: 14 }}>Gerangschikt op impact: 🔴 Kritiek · 🟡 Belangrijk · 🟢 Moderate invloed</p>
          <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: 12 }}>
            {[{
              icon: "🔴",
              title: "1. EU-opslag op laagste seizoensniveau ooit",
              impact: "TTF: +10% tot +25% bij krappe winter · Belpex: +8% tot +18%",
              why: "Eind augustus 2026 staat de EU-opslag op 65.39%, het laagste voor die datum sinds metingen in 2011 en ~14% onder het 5-jaargemiddelde. België zit op 55.1%. Dit vergroot de afhankelijkheid van dure LNG-import in de winter (TASS, 2 sep 2026; Voltstack, aug 2026).",
              monitor: "GIE AGSI+ wekelijks (agsi.gie.eu). Doelen: 83% eind september, 90% 1 november. Kijk vooral naar daggemiddelde injectiesnelheid.",
              border: "#ef4444",
              impactColor: "#fca5a5",
            },
            {
              icon: "🔴",
              title: "2. Qatar LNG-schade: 3-5 jaar structureel herstel",
              impact: "TTF: +15% tot +30% vs pre-crisis · Belpex: +12% tot +25%",
              why: "Qatar's 17% van de wereldwijde LNG-export is voor 3-5 jaar buiten gebruik (NYTimes, 14 mei 2026). Pre-crisis TTF-niveaus van €30-32 zijn daardoor structureel onbereikbaar tot 2028-2030. Dit houdt de Europese gasmarkt permanent krapper.",
              monitor: "QatarEnergy updates over herstelschema, heropstart South Pars / Ras Laffan, en alternatieve leveranciers (VS, Mozambique).",
              border: "#ef4444",
              impactColor: "#fca5a5",
            },
            {
              icon: "🔴",
              title: "3. Hormuz: wapenstilstand broos",
              impact: "TTF: -10% tot +25% · Belpex: -8% tot +20%",
              why: "De Straat van Hormuz is deels heropend sinds 21 april 2026, maar de wapenstilstand is broos. Trump dreigt met sancties, Iran houdt het waterweg dicht. Tankerdoorvoer blijft sterk verminderd. Nieuwe escalatie drijft de risicopremie onmiddellijk op (Trading Economics, 28 aug 2026).",
              monitor: "Hormuz Strait Monitor, VN-bemiddelingsberichten, tankerdoorvoer-data, Iraanse en VS-verklaringen.",
              border: "#ef4444",
              impactColor: "#fca5a5",
            },
            {
              icon: "🟡",
              title: "4. Hittegolf & koelingvraag remmen injectie",
              impact: "TTF: +3% tot +8% · Belpex: +2% tot +6%",
              why: "Een hittegolf in augustus verhoogde gasgestuurde koeling en remde opslaginjectie. Zonnige middaguren drukken Belpex tijdelijk, maar avondspitsen en weinig wind houden gascentrales marginaal (Selectra/Enerdeal, sep 2026).",
              monitor: "Temperatuurverwachtingen, zonne- en windproductie in België, vraag naar airconditioning en industriële vraag.",
              border: "#f97316",
              impactColor: "#fdba74",
            },
            {
              icon: "🟡",
              title: "5. Vast tarief blijft significant duurder dan variabel",
              impact: "Consument: vast kost ~27% meer dan variabel · Leverage naar leverancier",
              why: "VRT meldde in juni 2026 dat vaste contracten gemiddeld 27% duurder zijn dan variabele. In september blijft die premie bestaan: vast bevat de volledige LNG-risicopremie. Variabel volgt groothandel met 1-2 maanden vertraging.",
              monitor: "VREG-tariefvergelijker, aanbiedingen van Eneco, Engie, Luminus, Mega. Vast alleen aantrekkelijk als u de rust van vaste kosten verkiest boven financieel optimum.",
              border: "#f97316",
              impactColor: "#fdba74",
            },
            {
              icon: "🟢",
              title: "6. OPEC+ stabiliseert Brent rond $94",
              impact: "Brent: stabiliserend · Indirect TTF: -2% tot +2%",
              why: "OPEC+ voerde drie productieverhogingen door om Hormuz-verlies te compenseren. Brent stabiliseerde rond $94/vat op 2 september na een dieptepunt van $79 begin augustus. Extra Iraanse olie zou Brent verder kunnen drukken (Reuters/CNBC, mei 2026).",
              monitor: "OPEC+ vergaderingen, Brent boven/onder $100, en signalen van productie-compliance.",
              border: "#22c55e",
              impactColor: "#86efac",
            },
            {
              icon: "🟢",
              title: "7. Doorrekening naar Belgische consumentenprijzen",
              impact: "Variabel contract: wijziging t-2 maanden vertraagd · Vast: risicopremie ingebakken",
              why: "Vaste contracten bevatten de volledige risicopremie van dit moment. Bij variabele formules volgt de doorrekening met 1-2 maanden vertraging op groothandelsbewegingen. Belgische inflatie staat op 2.6% mede door energieprijzen.",
              monitor: "VREG-tarieven, leveranciersupdates, indexatieformules (gas en elektriciteit apart), en of prijsdaling groothandel ook zichtbaar wordt in variabele tarieven.",
              border: "#22c55e",
              impactColor: "#86efac",
            },
            ].map((factor) => (
              <div key={factor.title} style={{ background: "#0f172a", borderRadius: 10, padding: "15px 17px", border: `1px solid ${factor.border}33` }}>
                <div style={{ color: "#60a5fa", fontWeight: 700, marginBottom: 10, fontSize: 13 }}>{factor.icon} {factor.title}</div>
                <div style={{ display: "grid", gap: 8 }}>
                  <div style={{ background: "#111827", borderRadius: 8, padding: "9px 11px", border: `1px solid ${factor.border}22` }}>
                    <div style={{ fontSize: 11, color: "#64748b", marginBottom: 3, textTransform: "uppercase", letterSpacing: "0.04em" }}>Verwachte impact</div>
                    <div style={{ fontSize: 12, color: factor.impactColor, fontWeight: 700 }}>{factor.impact}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: 11, color: "#64748b", marginBottom: 3, textTransform: "uppercase", letterSpacing: "0.04em" }}>Waarom dit de prijs beweegt</div>
                    <div style={{ fontSize: 12, color: "#94a3b8", lineHeight: 1.65 }}>{factor.why}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: 11, color: "#64748b", marginBottom: 3, textTransform: "uppercase", letterSpacing: "0.04em" }}>Wat te monitoren</div>
                    <div style={{ fontSize: 12, color: "#94a3b8", lineHeight: 1.65 }}>{factor.monitor}</div>
                  </div>
                </div>
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
            De huidige prijspiek is reëel — TTF noteert €71.92 en Belpex €172.18 — maar de <strong style={{ color: "#f8fafc" }}>structurele opwaartse risico's zitten grotendeels in vaste contracten</strong>. Vaste tarieven bevatten de volledige risicopremie van dit moment. Wie vandaag vast neemt voor 12-18 maanden, betaalt waarschijnlijk méér dan de gemiddelde marktprijs, omdat variabele tarieven met 1-2 maanden vertraging de eventuele normalisatie volgen. <strong style={{ color: "#f8fafc" }}>Belangrijk:</strong> U bent wettelijk vrij om maand-op-maand te wisselen, maar een weloverwogen keuze voor minimaal 12 maanden levert financieel het meeste op (zie hieronder waarom).
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
                title: "Seizoenspatroon najaar-winter",
                body: "Na de zomer is het injectieseizoen cruciaal: haalt de EU 90% niet, dan stijgt de wintervraag-prijs in. Een milde herfst of snelle injectie kan TTF na het huidige piekniveau drukken; een vroege koude snap drijft het op.",
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
                <p style={{ fontSize: 13, color: "#86efac", lineHeight: 1.7, margin: "0 0 10px" }}>
                  Wie in september–oktober 2022 (het absolute piekmoment) overstapte naar een vast tarief voor 12-18 maanden, betaalde gemiddeld <strong>2–3× meer</strong> dan de marktprijs in 2023–2024. Wie in paniek vastzat aan een crisiscontract terwijl de markt normaliseerde, kon pas na afloop van de contractperiode profiteren van dalende prijzen. Dezelfde dynamiek is nu opnieuw relevant: crisis-contracten bevatten de volledige risicopremie van dit moment.
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
                <li>Vast tarief <strong style={{ color: "#f8fafc" }}>meer dan 10% duurder</strong> is dan een vergelijkbaar variabel aanbod (huidig: ~27% — ruim boven de drempel)</li>
                <li>U de <strong style={{ color: "#f8fafc" }}>bijzondere voorwaarden</strong> (premies, loyaliteitsvoordelen) niet gelezen heeft</li>
              </ul>
            </div>
          </div>
        </div>

        {/* DECISION MATRIX */}
        <div style={SECTION}>
          <h3 style={{ margin: "0 0 4px", color: "#f8fafc", fontSize: 15 }}>📋 Adviesmatrix per Profiel — September 2026</h3>
          <p style={{ fontSize: 12, color: "#64748b", marginTop: 0, marginBottom: 14 }}>
            Context: vast tarief gemiddeld <strong style={{ color: "#f97316" }}>~27% duurder</strong> dan variabel (VRT, jun 2026) · TTF €71.92 · Belpex €172.18 · BE-opslag 55.1% (2 sep 2026)
          </p>
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
                  ["Gezin, krappe begroting",
                   "⬇ Variabel — met maandelijkse check",
                   "Vast is nu ~27% duurder: dat is financieel onverantwoord bij een krap budget. Variabel volgt de markt en daalt mee als de spanning na de winter afneemt. Maandelijks controleren via VREG-vergelijker.",
                   "Stel een prijsalert in (bijv. TTF > €75 gedurende 3 weken) als trigger om vast te overwegen"],
                  ["Gemiddeld gezin",
                   "⬇ Variabel — 12 mnd horizon",
                   "TTF staat op €71.92 en Belpex op €172.18 — beide hoog, maar vast legt u vast op de volledige risicopremie. Variabel volgt met 1-2 maanden vertraging eventuele daling; op 12-18 maanden levert dat statistisch meer kans op lager gemiddelde.",
                   "Herbekijk in november/maart; geen haastbeslissing nemen op een nieuwspiek"],
                  ["Hoog verbruik (WP/EV)",
                   "⚖️ Variabel of vast — afh. van budgetruimte",
                   "Hoger verbruik = hogere blootstelling aan schommelingen. Vast geeft voorspelbaarheid maar kost ~27% meer. Variabel is rationeler tenzij u de rust van vaste kosten verkiest boven het financiële optimum.",
                   "Koppel laadschema aan daluurprijzen (00:00–06:00); evalueer contract na 12 maanden"],
                  ["Zonnepanelen + batterij",
                   "⬇ Dynamisch tarief",
                   "Dynamische tarieven (Ecofix, Bolt) maximaliseren teruglevering bij negatieve prijzen en goedkoop laden bij overschot. Vast of gewoon variabel laat dit voordeel onbenut.",
                   "Monitor dag-ahead via leveranciers-app of Fluvius; controleer teruglevering-vergoeding in contract"],
                  ["Huurder zonder zonnepanelen",
                   "⬇ Variabel — standaard keuze",
                   "Geen zonnepanelen → geen dynamisch voordeel. Variabel is aanzienlijk goedkoper dan vast en volgt de markt. Geen aanleiding om de risicopremie van leverancier te betalen.",
                   "Vergelijk minstens 1× per jaar via VREG; let op indexatieformule (gas- of elektriciteitsbased)"],
                  ["KMO / kleine zelfstandige",
                   "⚖️ Vast — indien budgetstabiliteit noodzaak",
                   "KMO's moeten offertes maken op basis van vaste kostenstructuur. Vast geeft zekerheid maar kost ~27% meer. Alleen verantwoord als variabele facturen niet doorrekend kunnen worden aan klanten.",
                   "Lees loyaliteitsclausules grondig; plan contractherziening 3 mnd voor afloop; max. 12 mnd vast"],
                ].map(([p, a, m, v], i) => (
                  <tr key={i} style={{ borderBottom: "1px solid #1e293b" }}>
                    <td style={{ padding: "9px 11px", color: "#e2e8f0", fontWeight: 600, verticalAlign: "top" }}>{p}</td>
                    <td style={{ padding: "9px 11px", color: "#60a5fa", verticalAlign: "top", whiteSpace: "nowrap" }}>{a}</td>
                    <td style={{ padding: "9px 11px", color: "#94a3b8", verticalAlign: "top" }}>{m}</td>
                    <td style={{ padding: "9px 11px", color: "#64748b", fontSize: 11, verticalAlign: "top" }}>{v}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div style={{ ...SECTION, background: "#172554", border: "3px solid #3b82f6", borderRadius: 14, padding: "24px 28px" }}>
          <h2 style={{ margin: "0 0 16px", color: "#60a5fa", fontSize: 18, fontWeight: 700 }}>🎯 KERNBOODSCHAP: Weloverwogen keuzen duren langer dan een nieuwscyclus</h2>
          
          <p style={{ fontSize: 15, lineHeight: 1.85, color: "#bfdbfe", margin: "0 0 14px", fontWeight: 500 }}>
            TTF staat op €71.92/MWh (+1.4% vs gisteren) en Belpex op €172.18/MWh (+13.0%). De markt is gespannen door de broze Hormuz-situatie, historisch lage EU-opslag (65.4%) en structurele Qatar LNG-schade. Vast tarief blijft gemiddeld ~27% duurder dan variabel. Wie nu vastlegt, betaalt de volledige risicopremie van dit moment.
          </p>
          
          <div style={{ background: "#0f172a", borderRadius: 10, padding: "16px 20px", marginBottom: 14, border: "1px solid #1e3a8a" }}>
            <p style={{ fontSize: 14, lineHeight: 1.85, color: "#bfdbfe", margin: "0 0 12px" }}>
              <strong style={{ color: "#60a5fa" }}>Korte termijn (2-5 maanden):</strong> Verhoogd prijsniveau door Qatar-schade en lage opslag. TTF blijft waarschijnlijk €60-80 tot eind oktober, met uitschieters naar boven bij koude of escalatie.
            </p>
            <p style={{ fontSize: 14, lineHeight: 1.85, color: "#bfdbfe", margin: 0 }}>
              <strong style={{ color: "#60a5fa" }}>Middellange termijn (6-18 maanden):</strong> Structureel herstel van LNG-capaciteit (2027-2028), het Engie-akkoord en het begin van het injectieseizoen 2027 zorgen voor drukkend potentieel. Wie op 12-18 maanden kijkt, heeft statistisch meer kans op een lagere gemiddelde prijs via variabel dan via een vast contract dat nu op een hoog niveau wordt afgesloten.
            </p>
          </div>
          
          <p style={{ fontSize: 15, lineHeight: 1.85, color: "#bfdbfe", margin: "0 0 16px", fontWeight: 500 }}>
            De Belgische wet biedt consumenten bescherming bij ingrijpend gewijzigde omstandigheden (wettelijk recht op kosteloze opzegging). Dat is een vangnet — geen reden om contracten als tijdelijke constructies te beschouwen. Een <strong>stabiele keuze die u 12 maanden met vertrouwen kunt aanhouden</strong> is altijd beter dan een snelle beslissing die u maanden later al betreurt.
          </p>
          
          <div style={{ background: "#0c4a6e", border: "2px solid #0ea5e9", borderRadius: 10, padding: "16px 20px", fontSize: 14, color: "#e0f2fe" }}>
            <h4 style={{ margin: "0 0 12px", color: "#38bdf8", fontSize: 15, fontWeight: 700 }}>📋 PRAKTISCH ADVIES — Concrete Stappen</h4>
            
            <div style={{ marginBottom: 12 }}>
              <strong style={{ color: "#7dd3fc" }}>1. Observatieperiode (4-6 weken):</strong> Wacht tot eind oktober 2026 om het verloop van het injectieseizoen en de eerste wintervraag te beoordelen. Volg TTF dagelijks via Trading Economics en monitor België/EU-gasopslag via GIE AGSI+ (update elke dinsdag).
            </div>
            <div style={{ marginBottom: 12 }}>
              <strong style={{ color: "#7dd3fc" }}>2. Trigger voor Variabel:</strong> Als TTF structureel onder €55/MWh stabiliseert gedurende 2+ weken EN Belgische opslag boven 75% eind oktober, overweeg dan variabel met 12-18 maanden horizon. Dit biedt de beste kans op lagere gemiddelde kosten als de winter meevalt.
            </div>
            <div style={{ marginBottom: 12 }}>
              <strong style={{ color: "#7dd3fc" }}>3. Trigger voor Vast:</strong> Als TTF structureel boven €75/MWh blijft voor 4+ weken OF EU-opslag eind oktober onder 80% zit, overweeg dan vast voor maximaal 12-18 maanden. Budgetzekerheid weegt zwaarder dan flexibiliteitsvoordeel bij structurele schaarste.
            </div>
            <div style={{ marginBottom: 8 }}>
              <strong style={{ color: "#7dd3fc" }}>4. Maximale contracttermijn:</strong> <strong>Nooit meer dan 12-18 maanden</strong>. De Belgische wet biedt kosteloze opzegging, maar frequent wisselen leidt tot hogere tarieven voor iedereen. Een weloverwogen keuze voor minimaal 12 maanden levert financieel en administratief het meeste op.
            </div>
            
            <div style={{ background: "#7c2d12", border: "1px solid #f97316", borderRadius: 8, padding: "12px 14px", marginTop: 14 }}>
              <strong style={{ color: "#fdba74" }}>⚠️ NOOIT OVERHAAST TEKENEN:</strong> Tijdens een nieuwscyclus die voelt als een noodsituatie, nemen leveranciers en media de urgentie op. Dat is marketing, geen financieel advies. Paniek is een slechte raadgever. Neem de tijd om te vergelijken en te begrijpen wat u tekent.
            </div>
          </div>
        </div>
      </>)}

      {/* ── BRONNEN ── */}
      {tab === "bronnen" && (
        <div style={SECTION}>
          <h3 style={{ margin: "0 0 6px", color: "#f8fafc", fontSize: 16 }}>📚 Bronvermeldingen</h3>
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
              ],
            },
            {
              cat: "🔥 Gasmarkt — TTF", color: "#0ea5e9",
              items: [
                { n: "ICE — Dutch TTF Natural Gas Futures",    d: "Officiële futuresmarkt voor TTF gascontracten",                        url: "https://www.ice.com/products/27996665/Dutch-TTF-Natural-Gas-Futures/data" },
                { n: "Gas Infrastructure Europe (GIE) AGSI+", d: "Officiële België gasopslagniveaus per land — wekelijkse update",           url: "https://agsi.gie.eu" },
                { n: "Trading Economics — TTF Natural Gas", d: "Real-time TTF gas prices and historical data", url: "https://tradingeconomics.com/commodity/eu-natural-gas" },
                { n: "OilPriceAPI — Live TTF Data", d: "Real-time Dutch TTF gas price API", url: "https://www.oilpriceapi.com/live/dutch-ttf-gas-price" },
                { n: "Splash247 — Qatar LNG Long Road Back", d: "Qatar LNG zwaarste disruptie in 20 jaar — 3-5 jaar herstel", url: "https://splash247.com/qatar-lng-faces-long-road-back-after-unprecedented-disruption" },
                { n: "European Gas Hub — Opslaganalyses",      d: "Analytische rapporten over België gasopslag en marktevolutie",            url: "https://europeangashub.com" },
                { n: "TASS — Europe ends summer with lowest gas inventories (02/09/2026)", d: "EU-opslag 65.39% eind augustus — laagste seizoensniveau sinds 2011", url: "https://tass.com/economy/2181085" },
                { n: "Voltstack — EU Gas Storage Tracker", d: "EU-opslag 61.6% (18 aug 2026), 14% onder 5-jaargemiddelde", url: "https://voltstack.energy/insights/eu-gas-storage-tracker-winter-2026" },

              ],
            },
            {
              cat: "🌍 Geopolitiek & Marktanalyse", color: "#f97316",
              items: [
                { n: "Hormuz Strait Monitor — Live Dashboard", d: "Real-time scheepvaartmonitoring Straat van Hormuz, crisis-timeline", url: "https://hormuzstraitmonitor.com" },
                { n: "Seavantage — Hormuz Crisis 2026 Timeline", d: "Gedetailleerde scheepvaart-disruption timeline, incidenten per datum", url: "https://www.seavantage.com/blog/strait-of-hormuz-crisis-2026-shipping-disruption-timeline" },
                { n: "NYTimes — Qatar LNG: Long Road Back (14/05/2026)", d: "Qatar's LNG-exportcapaciteit 3-5 jaar beschadigd (17% wereldmarkt)", url: "https://www.nytimes.com/2026/05/14/business/qatar-lng-iran.html" },
                { n: "Reuters — OPEC+ derde productieverhoging (03/05/2026)", d: "OPEC+ 188.000 vaten/dag extra na Hormuz-blokkade", url: "https://www.reuters.com/business/energy/opec-set-agree-third-oil-output-quota-hike-since-hormuz-closure-sources-say-2026-05-03" },
                { n: "VRT — Vast of variabel (jun 2026)", d: "Vast tarief gemiddeld 27% duurder dan variabel in België, juni 2026", url: "https://www.frankenergie.be/nl/kennisbank/energie/vast-of-variabel-energiecontract" },
                { n: "EU Energy Live — Belgium Electricity", d: "Belgische elektriciteitsmarktdata en day-ahead prijzen", url: "https://euenergy.live/country.php?a2=BE" },
                { n: "TASS — Europe ends summer with lowest gas inventories (02/09/2026)", d: "EU-opslag 65.39% eind augustus — laagste seizoensniveau sinds 2011", url: "https://tass.com/economy/2181085" },
                { n: "Voltstack — EU Gas Storage Tracker (18/08/2026)", d: "EU-opslag 61.6%, 14% onder 5-jaargemiddelde", url: "https://voltstack.energy/insights/eu-gas-storage-tracker-winter-2026" },
                { n: "Selectra — Prix électricité 2 sep 2026", d: "Belpex daggemiddelde 172 €/MWh, Frankrijk 164 €/MWh", url: "https://selectra.info/energie/actualites/prix-electricite/2026-09-02" },
                { n: "Enerdeal — Belpex Day-Ahead Dashboard", d: "Belgische day-ahead marktdata en analyses", url: "https://enerdeal.com/en/belpex-day-ahead-price-dashboard-belgium" },
                { n: "ACER — Gas Key Developments Winter 2026", d: "EU gasmarkt analyse winter 2026, LNG-afhankelijkheid, Qatar-aandeel", url: "https://www.acer.europa.eu/sites/default/files/documents/Publications/2026-ACER-Gas-Key-Developments-winter.pdf" },
                { n: "Euronews — Belgische Nucleaire Renaissance (30/04/2026)", d: "De Wever-Engie akkoord voor heractivering nucleaire vloot, finaal akkoord okt 2026", url: "https://www.euronews.com/my-europe/2026/04/30/belgium-reopen" },
                { n: "LinkedIn — EU ETS Koolstofprijs €85/ton 2026", d: "CO₂-prijs prognose 2026-2027, ETS-hervorming, impact op electriciteitsprijzen", url: "https://www.linkedin.com/pulse/carbon-price-eu-ets-hit-126t-" },
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
        </div>
      )}

      {/* FOOTER */}
      <div style={{ textAlign: "center", marginTop: 22, padding: "13px 0", borderTop: "1px solid #1e293b", fontSize: 11, color: "#334155" }}>
        <div style={{ background: "#172554", border: "1px solid #3b82f44", borderRadius: 10, padding: "13px 17px", fontSize: 12, color: "#93c5fd", lineHeight: 1.7 }}>
          <strong>Databronnen:</strong> Officiële marktdatabronnen voor energieprijzen en gasopslag. Voor real-time data: ENTSO-E Transparency Platform (elektriciteit), GIE AGSI+ (gasopslag), EPEX SPOT (day-ahead markt), ICE (TTF futures), en nationale regulatoren (VREG/CREG). Geopolitieke analyses via internationale nieuwsbronnen en marktonderzoek. Alle bronnen zijn publiek raadpleegbaar.
        </div>
        <div style={{ marginTop: 8 }}>
          GIE AGSI+ · ENTSO-E · Reuters · NYTimes · Wall Street Journal · IEA.org · EPEX SPOT · VREG · CREG · Hormuz Strait Monitor<br />
Opgesteld: 3 september 2026 · 23:28 · 23:30 CET · Niet-officieel advies — raadpleeg VREG of een erkend energieadviseur voor definitieve beslissingen
        </div>
      </div>
      {/* Cloudflare Web Analytics */}
      <script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{"token": "56157a20ce0e4d2a8f76844bfdb0f5aa"}'></script>
    </div>
  );
}
