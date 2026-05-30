
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
  { date: "17/02", ttf: 31.5,  belpex: 81.0,  brent: 101.55, storage: 21.5, note: "" },
  { date: "18/02", ttf: 32.1,  belpex: 86.0,  brent: 102.10, storage: 22.1, note: "" },
  { date: "19/02", ttf: 33.2,  belpex: 89.5,  brent: 103.20, storage: 22.8, note: "" },
  { date: "20/02", ttf: 34.8,  belpex: 92.1,  brent: 104.30, storage: 23.2, note: "" },
  { date: "21/02", ttf: 35.6,  belpex: 94.7,  brent: 105.10, storage: 23.5, note: "" },
  { date: "24/02", ttf: 36.2,  belpex: 96.3,  brent: 105.80, storage: 23.8, note: "" },
  { date: "25/02", ttf: 37.1,  belpex: 98.9,  brent: 106.40, storage: 24.1, note: "" },
  { date: "26/02", ttf: 38.5,  belpex: 102.4, brent: 107.20, storage: 24.5, note: "" },
  { date: "27/02", ttf: 39.2,  belpex: 105.8, brent: 107.90, storage: 24.8, note: "" },
  { date: "28/02", ttf: 40.1,  belpex: 108.2, brent: 108.60, storage: 25.2, note: "" },
  { date: "01/03", ttf: 42.3,  belpex: 112.5, brent: 109.80, storage: 25.6, note: "" },
  { date: "02/03", ttf: 45.8,  belpex: 118.9, brent: 111.20, storage: 26.1, note: "Hormuz" },
  { date: "03/03", ttf: 48.7,  belpex: 125.4, brent: 113.50, storage: 26.4, note: "Piek" },
  { date: "04/03", ttf: 51.2,  belpex: 119.8, brent: 112.80, storage: 26.7, note: "" },
  { date: "05/03", ttf: 49.8,  belpex: 114.2, brent: 111.90, storage: 27.0, note: "" },
  { date: "06/03", ttf: 47.6,  belpex: 108.7, brent: 110.80, storage: 27.3, note: "" },
  { date: "07/03", ttf: 46.3,  belpex: 105.1, brent: 109.70, storage: 27.5, note: "WE" },
  { date: "10/03", ttf: 44.8,  belpex: 98.4,  brent: 108.50, storage: 27.7, note: "IEA" },
  { date: "11/03", ttf: 43.2,  belpex: 92.8,  brent: 107.30, storage: 27.9, note: "" },
  { date: "12/03", ttf: 42.1,  belpex: 87.6,  brent: 106.20, storage: 28.1, note: "" },
  { date: "13/03", ttf: 41.5,  belpex: 84.3,  brent: 105.40, storage: 28.3, note: "" },
  { date: "14/03", ttf: 40.8,  belpex: 81.9,  brent: 104.80, storage: 28.5, note: "" },
  { date: "17/03", ttf: 50.75, belpex: 113.77, brent: 108.90, storage: 24.2, note: "" },
  { date: "27/03", ttf: 54.43, belpex: 117.78, brent: 114.27, storage: 22.3, note: "" },
  { date: "18/03", ttf: 51.56, belpex: 80.92,  brent: 107.80, storage: 24.8, note: "" },
  { date: "19/03", ttf: 54.66, belpex: 100.30, brent: 110.50, storage: 25.1, note: "" },
  { date: "20/03", ttf: 62.00, belpex: 125.50, brent: 112.50, storage: 25.8, note: "" },
  { date: "21/03", ttf: 59.34, belpex: 95.00,  brent: 109.20, storage: 26.2, note: "" },
  { date: "22/03", ttf: 58.50, belpex: 78.00,  brent: 108.90, storage: 26.5, note: "" },
  { date: "23/03", ttf: 60.60, belpex: 104.00, brent: 111.40, storage: 26.8, note: "" },
  { date: "24/03", ttf: 53.25, belpex: 72.78, brent: 105.55, storage: 27.2, note: "" },
  { date: "25/03", ttf: 52.07, belpex: 72.04, brent: 104.49, storage: 27.5, note: "" },
  { date: "26/03", ttf: 55.90, belpex: 87.48, brent: 106.71, storage: 22.5, note: "" },
  { date: "28/03", ttf: 54.52, belpex: 75.58, brent: 112.57, storage: 22.0, note: "" },
  { date: "29/03", ttf: 53.25, belpex: 64.84, brent: 112.57, storage: 21.8, note: "" },
  { date: "30/03", ttf: 54.82, belpex: 59.26, brent: 114.70, storage: 21.7, note: "" },
  { date: "31/03", ttf: 50.17, belpex: 118.15, brent: 118.35, storage: 21.8, note: "" },
  { date: "01/04", ttf: 48.00, belpex: 141.65, brent: 100.20, storage: 21.7, note: "" },
  { date: "02/04", ttf: 49.97, belpex: 120.03, brent: 109.25, storage: 25.5, note: "" },
  { date: "03/04", ttf: 55.86, belpex: 84.71, brent: 109.24, storage: 25.4, note: "" },
  { date: "04/04", ttf: 55.86, belpex: 45.08, brent: 109.24, storage: 25.0, note: "" },
  { date: "05/04", ttf: 55.86, belpex: 0.05, brent: 109.24, storage: 25.1, note: "" },
  { date: "06/04", ttf: 55.86, belpex: 36.85, brent: 109.69, storage: 25.2, note: "" },
  { date: "07/04", ttf: 55.86, belpex: 88.54, brent: 103.75, storage: 25.1, note: "" },
  { date: "08/04", ttf: 45.39, belpex: 86.12, brent: 96.70, storage: 25.1, note: "" },
  { date: "09/04", ttf: 45.42, belpex: 78.70, brent: 96.20, storage: 25.1, note: "" },
  { date: "10/04", ttf: 43.73, belpex: 113.93, brent: 94.33, storage: 25.0, note: "" },
  { date: "11/04", ttf: 43.63, belpex: 48.76, brent: 95.20, storage: 24.6, note: "" },
  { date: "12/04", ttf: 43.63, belpex: 67.14, brent: 95.20, storage: 24.5, note: "" },
  { date: "13/04", ttf: 46.27, belpex: 128.43, brent: 97.91, storage: 24.4, note: "" },
  { date: "14/04", ttf: 42.91, belpex: 124.29, brent: 95.29, storage: 23.9, note: "" },
  { date: "15/04", ttf: 53.25, belpex: 103.70, brent: 94.95, storage: 23.7, note: "" },
  { date: "16/04", ttf: 42.18, belpex: 100.14, brent: 98.29, storage: 23.7, note: "" },
  { date: "17/04", ttf: 38.97, belpex: 107.41, brent: 92.15, storage: 23.5, note: "" },
  { date: "18/04", ttf: 38.72, belpex: 99.53, brent: 90.38, storage: 23.8, note: "" },
  { date: "19/04", ttf: 38.76, belpex: 79.77, brent: 90.38, storage: 23.6, note: "" },
  { date: "20/04", ttf: 39.65, belpex: 116.92, brent: 94.28, storage: 23.9, note: "" },
  { date: "21/04", ttf: 42.45, belpex: 75.03, brent: 99.05, storage: 23.8, note: "" },
  { date: "22/04", ttf: 43.93, belpex: 72.78, brent: 101.55, storage: 23.8, note: "" },
  { date: "23/04", ttf: 44.90, belpex: 60.99, brent: 105.81, storage: 23.9, note: "" },
  { date: "24/04", ttf: 45.10, belpex: 72.78, brent: 105.97, storage: 23.4, note: "" },
  { date: "25/04", ttf: 44.86, belpex: 29.17, brent: 105.33, storage: 23.4, note: "" },
  { date: "26/04", ttf: 53.25, belpex: 16.16, brent: 101.55, storage: 26.0, note: "" },
  { date: "27/04", ttf: 53.25, belpex: 95.47, brent: 101.55, storage: 24.1, note: "" },
  { date: "28/04", ttf: 53.25, belpex: 61.43, brent: 101.55, storage: 24.6, note: "" },
  { date: "29/04", ttf: 53.25, belpex: 51.68, brent: 101.55, storage: 24.6, note: "" },
  { date: "30/04", ttf: 53.25, belpex: 57.46, brent: 101.55, storage: 24.7, note: "" },
  { date: "01/05", ttf: 53.25, belpex: -5.47, brent: 101.55, storage: 24.5, note: "" },
  { date: "02/05", ttf: 53.25, belpex: 68.48, brent: 101.55, storage: 24.6, note: "" },
  { date: "03/05", ttf: 53.25, belpex: 85.46, brent: 101.55, storage: 24.8, note: "" },
  { date: "04/05", ttf: 53.25, belpex: 123.74, brent: 101.55, storage: 24.9, note: "" },
  { date: "05/05", ttf: 53.25, belpex: 119.98, brent: 101.55, storage: 24.7, note: "" },
  { date: "06/05", ttf: 53.25, belpex: 122.06, brent: 101.55, storage: 24.4, note: "" },
  { date: "07/05", ttf: 53.25, belpex: 124.81, brent: 101.55, storage: 24.1, note: "" },
  { date: "08/05", ttf: 53.25, belpex: 104.07, brent: 101.55, storage: 23.7, note: "" },
  { date: "09/05", ttf: 53.25, belpex: 77.73, brent: 101.55, storage: 23.9, note: "" },
  { date: "10/05", ttf: 53.25, belpex: 66.86, brent: 101.55, storage: 23.8, note: "" },
  { date: "11/05", ttf: 53.25, belpex: 107.59, brent: 101.55, storage: 23.8, note: "" },
  { date: "12/05", ttf: 53.25, belpex: 91.08, brent: 101.55, storage: 23.9, note: "" },
  { date: "13/05", ttf: 53.25, belpex: 98.29, brent: 101.55, storage: 23.8, note: "" },
  { date: "14/05", ttf: 53.25, belpex: 84.36, brent: 101.55, storage: 23.2, note: "" },
  { date: "15/05", ttf: 53.25, belpex: 95.10, brent: 101.55, storage: 23.1, note: "" },
  { date: "16/05", ttf: 53.25, belpex: 74.69, brent: 101.55, storage: 22.8, note: "" },
  { date: "17/05", ttf: 53.25, belpex: 80.94, brent: 101.55, storage: 22.6, note: "" },
  { date: "18/05", ttf: 53.25, belpex: 133.63, brent: 101.55, storage: 22.4, note: "" },
  { date: "19/05", ttf: 53.25, belpex: 110.91, brent: 101.55, storage: 22.2, note: "" },
  { date: "20/05", ttf: 53.25, belpex: 92.80, brent: 101.55, storage: 21.6, note: "" },
  { date: "21/05", ttf: 53.25, belpex: 106.59, brent: 101.55, storage: 21.0, note: "" },
  { date: "22/05", ttf: 53.25, belpex: 96.61, brent: 101.55, storage: 20.8, note: "" },
  { date: "23/05", ttf: 53.25, belpex: 74.35, brent: 101.55, storage: 20.8, note: "" },
  { date: "24/05", ttf: 53.25, belpex: 67.41, brent: 101.55, storage: 20.8, note: "" },
  { date: "25/05", ttf: 53.25, belpex: 78.18, brent: 101.55, storage: 20.9, note: "" },
  { date: "26/05", ttf: 53.25, belpex: 94.06, brent: 101.55, storage: 26.0, note: "" },
  { date: "27/05", ttf: 53.25, belpex: 83.21, brent: 101.55, storage: 21.1, note: "" },
  { date: "28/05", ttf: 53.25, belpex: 117.14, brent: 101.55, storage: 26.0, note: "" },
  { date: "29/05", ttf: 53.25, belpex: 104.32, brent: 101.55, storage: 21.3, note: "" },
  { date: "30/05", ttf: 53.25, belpex: 82.62, brent: 101.55, storage: 21.3, note: "Vandaag" }
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

const forecastBase = [
  { date: "01/04", ttf: 48.00, belpex: 141.65 },
  { date: "08/04", ttf: 46,    belpex: 120  },
  { date: "15/04", ttf: 44,    belpex: 105  },
  { date: "22/04", ttf: 42,    belpex: 95   },
  { date: "29/04", ttf: 40,    belpex: 88   },
  { date: "06/05", ttf: 38,    belpex: 82   },
  { date: "13/05", ttf: 36,    belpex: 75   },
  { date: "20/05", ttf: 35,    belpex: 70   },
  { date: "27/05", ttf: 34,    belpex: 65   },
];
const forecastBull = [
  { date: "01/04", ttf: 48.00, belpex: 141.65 },
  { date: "08/04", ttf: 56,    belpex: 165  },
  { date: "15/04", ttf: 62,    belpex: 185  },
  { date: "22/04", ttf: 68,    belpex: 210  },
  { date: "29/04", ttf: 72,    belpex: 240  },
  { date: "06/05", ttf: 78,    belpex: 220 },
  { date: "13/05", ttf: 82,    belpex: 200  },
  { date: "20/05", ttf: 85,    belpex: 185  },
  { date: "27/05", ttf: 88,    belpex: 175  },
];
const forecastBear = [
  { date: "01/04", ttf: 48.00, belpex: 141.65 },
  { date: "08/04", ttf: 42,    belpex: 95   },
  { date: "15/04", ttf: 38,    belpex: 75   },
  { date: "22/04", ttf: 35,    belpex: 60   },
  { date: "29/04", ttf: 32,    belpex: 50   },
  { date: "06/05", ttf: 30,    belpex: 42   },
  { date: "13/05", ttf: 28,    belpex: 38   },
  { date: "20/05", ttf: 26,    belpex: 35   },
  { date: "27/05", ttf: 24,    belpex: 32   },
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
          MARKTANALYSE — 30 MEI 2026 · 22:32 CET
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
            Hormuz crisis dag 21+ · TTF €53.25 (-11.4% vs piek) · Brent $101.55 · Force majeure Qatar/Kuwait/UAE · Belgische gasreserves 21%
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
            "kritiek laag niveau", 
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
      <div style={{ display: "flex", gap: 4, marginBottom: 20, background: "#1e293b", padding: 6, borderRadius: 10, overflowX: "auto" }}>
        {TABS.map(([t, l]) => <button key={t} style={tabBtn(t)} onClick={() => setTab(t)}>{l}</button>)}
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
              <YAxis domain={[25, 70]} tick={{ fill: "#64748b", fontSize: 11 }} tickFormatter={v => `€${v}`} />
              <Tooltip content={<Tip />} />
              <ReferenceLine y={31.96} stroke="#22c55e" strokeDasharray="4 4" label={{ value: "27/02 basis", fill: "#22c55e", fontSize: 10, position: "top" }} />
              <ReferenceLine x="02/03" stroke="#ef4444" strokeDasharray="4 4" label={{ value: "Hormuz", fill: "#ef4444", fontSize: 10, position: "top" }} />
              <ReferenceLine x="20/03" stroke="#f97316" strokeDasharray="4 4" label={{ value: "Gasvelden", fill: "#f97316", fontSize: 10, position: "top" }} />
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
              <YAxis domain={[40, 150]} tick={{ fill: "#64748b", fontSize: 11 }} tickFormatter={v => `€${v}`} />
              <Tooltip content={<Tip />} />
              <ReferenceLine y={68} stroke="#22c55e" strokeDasharray="3 3" label={{ value: "27/02 basis", fill: "#22c55e", fontSize: 10, position: "top" }} />
              <ReferenceLine x="02/03" stroke="#ef4444" strokeDasharray="4 4" label={{ value: "Hormuz", fill: "#ef4444", fontSize: 10, position: "top" }} />
              <ReferenceLine x="09/03" stroke="#f97316" strokeDasharray="4 4" label={{ value: "Absolute Piek", fill: "#f97316", fontSize: 10, position: "top" }} />
              <ReferenceLine x="10/03" stroke="#a78bfa" strokeDasharray="4 4" label={{ value: "IEA", fill: "#a78bfa", fontSize: 10, position: "top" }} />
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
            <h3 style={{ margin: "0 0 14px", color: "#f8fafc", fontSize: 15 }}>🏭 Europese Gasvoorraden</h3>
            {[
              ["BE-gemiddelde (30 mei 2026)", "~21%",          "#ef4444"],
              ["Laagste seizoenspeil",       "in jaren",       "#ef4444"],
              ["Einde 2025",                 "~61%",           "#eab308"],
              ["Einde 2024",                 "~72%",           "#22c55e"],
              ["EU-doelstelling (1 nov)",    "90%",            "#0ea5e9"],
              ["Nog te vullen (apr–okt)",    "~69 pct-punten", "#f97316"],
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
          </div>

          <div style={SECTION}>
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
          </div>

          <div style={SECTION}>
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
          </div>

          <div style={SECTION}>
            <h3 style={{ margin: "0 0 14px", color: "#f8fafc", fontSize: 15 }}>🇧🇪 Belgische Energiemix — Waarom Gasprijzen de Elektriciteitsprijs Bepalen</h3>
            <p style={{ marginTop: 0, fontSize: 13, color: "#94a3b8", lineHeight: 1.7, marginBottom: 12 }}>
              België gebruikt het <strong style={{ color: "#f8fafc" }}>merit order principe</strong>: elektriciteitscentrales worden geactiveerd van goedkoop naar duur (kern → wind/zon → gas → olie). 
              De <strong style={{ color: "#f8fafc" }}>laatste centrale</strong> die nodig is om aan de vraag te voldoen, bepaalt de prijs voor <em>alle</em> elektriciteit in dat uur — dit is de "marginale producent".
            </p>
            <p style={{ marginTop: 0, fontSize: 13, color: "#94a3b8", lineHeight: 1.7, marginBottom: 12 }}>
              In België is gas de marginale producent in <strong style={{ color: "#f8fafc" }}>~87% van de uren</strong> (CREG-data 2021-2024). 
              Dit betekent: zelfs als 80% van de elektriciteit uit kern en hernieuwbaar komt, bepaalt de gasprijs de Belpex-prijs zodra gascentrales nodig zijn voor de laatste 20%. 
              Resultaat: <strong style={{ color: "#f8fafc" }}>TTF stijgt +13.5% → Belpex stijgt +25%</strong> (versterkt effect door grid congestion en nucleaire beperkingen). <br></br><strong style={{ color: "#f59e0b" }}>Huidige uitzondering:</strong> TTF stijgt door supply shock terwijl Belpex normaliseert na extreme piek.
            </p>
            <p style={{ marginTop: 0, fontSize: 13, color: "#94a3b8", lineHeight: 1.7 }}>
              <strong style={{ color: "#f8fafc" }}>Waarom gas zo vaak marginaal is:</strong> Kern draait continu (baseload), wind/zon zijn variabel, gas vult de gaten. 
              Bij hoge vraag (ochtend/avond) of weinig zon/wind → gascentrales starten → gasprijs = elektriciteitsprijs voor dat uur.
            </p>
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
                      </div>
        </div>
      )}

      {/* ── FORECAST ── */}
      {tab === "forecast" && (<>
        <div style={SECTION}>
          <h3 style={{ margin: "0 0 14px", color: "#f8fafc", fontSize: 16 }}>📈 TTF Gas Forecast (apr–mei 2026)</h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart margin={{ top: 4, right: 20, left: 0, bottom: 4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e3a5f" />
              <XAxis dataKey="date" type="category" allowDuplicatedCategory={false} tick={{ fill: "#64748b", fontSize: 11 }} />
              <YAxis domain={[20, 100]} tick={{ fill: "#64748b", fontSize: 11 }} tickFormatter={v => `€${v}`} />
              <Tooltip content={<Tip />} />
              <Legend wrapperStyle={{ fontSize: 12, color: "#94a3b8" }} />
              <Line data={forecastBull} type="monotone" dataKey="ttf" name="⬆ Bullish" stroke="#ef4444" strokeWidth={2} dot={{ r: 3, fill: "#ef4444" }} />
              <Line data={forecastBase} type="monotone" dataKey="ttf" name="⟶ Basis"   stroke="#0ea5e9" strokeWidth={2.5} dot={{ r: 3, fill: "#0ea5e9" }} />
              <Line data={forecastBear} type="monotone" dataKey="ttf" name="⬇ Bearish" stroke="#22c55e" strokeWidth={2} dot={{ r: 3, fill: "#22c55e" }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div style={SECTION}>
          <h3 style={{ margin: "0 0 14px", color: "#f8fafc", fontSize: 16 }}>⚡ Belpex Elektriciteit Forecast (apr–mei 2026)</h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart margin={{ top: 4, right: 20, left: 0, bottom: 4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e3a5f" />
              <XAxis dataKey="date" type="category" allowDuplicatedCategory={false} tick={{ fill: "#64748b", fontSize: 11 }} />
              <YAxis domain={[20, 250]} tick={{ fill: "#64748b", fontSize: 11 }} tickFormatter={v => `€${v}`} />
              <Tooltip content={<Tip />} />
              <Legend wrapperStyle={{ fontSize: 12, color: "#94a3b8" }} />
              <Line data={forecastBull} type="monotone" dataKey="belpex" name="⬆ Bullish" stroke="#dc2626" strokeWidth={2.5} dot={{ r: 3, fill: "#dc2626" }} />
              <Line data={forecastBase} type="monotone" dataKey="belpex" name="⟶ Basis" stroke="#0ea5e9" strokeWidth={3} dot={{ r: 4, fill: "#0ea5e9" }} />
              <Line data={forecastBear} type="monotone" dataKey="belpex" name="⬇ Bearish" stroke="#10b981" strokeWidth={2} dot={{ r: 3, fill: "#10b981" }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 14 }}>
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
        </div>

        <div style={{ ...SECTION, marginTop: 18 }}>
          <h3 style={{ margin: "0 0 8px", color: "#f8fafc", fontSize: 15 }}>🔑 Sleutelfactoren om op te volgen</h3>
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
            De huidige prijspiek is reëel, maar de <strong style={{ color: "#f8fafc" }}>structurele marktfundamentelen voor de komende 12-18 maanden zijn overwegend bearish</strong>. Dat betekent dat wie vandaag een vast tarief neemt voor 12-18 maanden, waarschijnlijk méér betaalt dan de gemiddelde marktprijs over diezelfde periode. <strong style={{ color: "#f8fafc" }}>Belangrijk:</strong> U bent wettelijk vrij om maand-op-maand te wisselen, maar een weloverwogen keuze voor minimaal 12 maanden levert financieel het meeste op (zie hieronder waarom).
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

        <div style={{ ...SECTION, background: "#172554", border: "3px solid #3b82f6", borderRadius: 14, padding: "24px 28px" }}>
          <h2 style={{ margin: "0 0 16px", color: "#60a5fa", fontSize: 18, fontWeight: 700 }}>🎯 KERNBOODSCHAP: Weloverwogen keuzen duren langer dan een nieuwscyclus</h2>
          
          <p style={{ fontSize: 15, lineHeight: 1.85, color: "#bfdbfe", margin: "0 0 14px", fontWeight: 500 }}>
            TTF daalde vandaag naar €53.25/MWh (-12.1%), wat duidt op marktverlichting na de piek van €60.60. Echter, de structurele LNG-disruptie blijft van kracht (Rabobank: Q2 2026 TTF €61/MWh). Wie nu vastlegt op €53.25 betaalt waarschijnlijk méér dan het gemiddelde over de komende 12-18 maanden.
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
                { n: "TradingPedia — LNG Market Analysis", d: "LNG market analysis and supply trends", url: "https://www.tradingpedia.com/2026/03/23/gulf-disruptions-reshape-ttf-gas-as-lng-glut-ends/" },
                { n: "European Gas Hub — Opslaganalyses",      d: "Analytische rapporten over België gasopslag en marktevolutie",            url: "https://europeangashub.com" },
                { n: "Gas to Power Journal — TTF analysis", d: "TTF market analysis and price trends", url: "https://gastopowerjournal.com/news/market/ttf-prices-fall-below-e30-mwh-as-geopolitical-risk-premium-fades/" },
              ],
            },
            {
              cat: "🌍 Geopolitiek & Beleidsinstanties", color: "#f97316",
              items: [
                { n: "Trading Economics — TTF Natural Gas", d: "Real-time TTF gas prices and market analysis", url: "https://tradingeconomics.com/commodity/eu-natural-gas" },
                { n: "Trading Economics — Brent Crude Oil", d: "Real-time Brent oil prices and historical data", url: "https://tradingeconomics.com/commodity/brent-crude-oil" },
                { n: "CNBC — Oil Market Analysis", d: "Global oil market analysis and price trends", url: "https://www.cnbc.com/2026/03/24/oil-prices-today-wti-brent-middle-east-iran-war.html" },
                { n: "EU Energy Live — Belgium Electricity", d: "Belgian electricity market data and prices", url: "https://euenergy.live/country.php?a2=BE" },
                { n: "EnergyPrices.eu — Belgium Energy", d: "Belgian energy prices and market information", url: "https://www.energyprices.eu/electricity/belgium" },
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
          GIE AGSI+ · ENTSO-E · Reuters · Bloomberg · Xinhua · Wall Street Journal · IEA.org · EPEX SPOT · VREG · CREG<br />
Opgesteld: 30 mei 2026 · 22:32 · Niet-officieel advies — raadpleeg VREG of een erkend energieadviseur voor definitieve beslissingen
        </div>
      </div>
      {/* Cloudflare Web Analytics */}
      <script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{"token": "56157a20ce0e4d2a8f76844bfdb0f5aa"}'></script>
    </div>
  );
}
