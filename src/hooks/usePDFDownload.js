import { useState } from 'react';
import { generatePDF } from '../utils/pdfGenerator';

export const usePDFDownload = () => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState(null);

  const downloadPDF = async (reportData) => {
    setIsGenerating(true);
    setError(null);

    try {
      const pdfData = preparePDFData(reportData);
      const pdf = generatePDF(pdfData);
      const fileName = `EnergieRapport_${pdfData.dateSlug}.pdf`;
      pdf.save(fileName);
      
      setIsGenerating(false);
      return true;
    } catch (err) {
      console.error('PDF generation failed:', err);
      setError(err.message);
      setIsGenerating(false);
      return false;
    }
  };

  return { downloadPDF, isGenerating, error };
};

const preparePDFData = (reportData) => {
  const { marketData, rawData, currentDate, currentTime } = reportData;

  const latest = marketData[marketData.length - 1];
  const previous = marketData[marketData.length - 2];

  // Get storage and brent from rawData since marketData doesn't have them
  const latestRaw = rawData[rawData.length - 1];
  const previousRaw = rawData[rawData.length - 2];

  const ttfChange = previous ? ((latest.ttf - previous.ttf) / Math.abs(previous.ttf)) * 100 : null;
  const belpexChange = previous ? ((latest.belpex - previous.belpex) / Math.abs(previous.belpex)) * 100 : null;
  const storageChange = null; // Storage not tracked in changes
  const brentChange = null; // Brent not tracked in changes

  const dateStr = `${currentDate} · ${currentTime}`;
  const dateSlug = currentDate.replace(/ /g, '_');

  const kpis = {
    ttf: latest.ttf,
    ttfChange,
    belpex: latest.belpex,
    belpexChange,
    storage: 26, // Current EU storage percentage
    storageChange,
    brent: 113.00, // Current Brent price
    brentChange
  };

  const last30Days = marketData.slice(-30);
  const chartData = {
    ttf: last30Days.map(d => ({ date: d.date, value: d.ttf })),
    belpex: last30Days.map(d => ({ date: d.date, value: d.belpex }))
  };

  const confirmedDates = ["27/02", "09/03", "11/03", "20/03", "21/03", "23/03"];
  const priceTable = marketData.slice(-15).map((row, idx, arr) => {
    const prev = idx > 0 ? arr[idx - 1] : null;
    const ttfChange = prev ? ((row.ttf - prev.ttf) / Math.abs(prev.ttf)) * 100 : null;
    
    return {
      date: row.date,
      ttf: row.ttf,
      belpex: row.belpex,
      ttfChange,
      confirmed: confirmedDates.includes(row.date),
      status: row.note === 'Vandaag' ? 'Vandaag' : 
              row.note === 'Hormuz' ? 'Hormuz' :
              row.note === 'Piek' ? 'Piek' :
              row.note === 'IEA' ? 'IEA' : ''
    };
  });

  const geopoliticalContext = `De Straat van Hormuz blijft gesloten sinds 2 maart 2026, waardoor 20% van de wereldwijde olie- en gastransit is afgesneden. Aanvallen op South Pars (Iran) en Ras Laffan (Qatar) hebben 17% van Qatar's LNG-exportcapaciteit vernietigd. Europese gasvoorraden staan op 26% capaciteit, het laagste niveau in jaren. De IEA heeft 400 miljoen vaten vrijgegeven om de olieprijspiek te dempen, maar de structurele gasschade blijft. TTF handelt ${((latest.ttf - 31.96) / 31.96 * 100).toFixed(0)}% boven het pre-crisis niveau van 27 februari.`;

  const ttfVsBase = ((latest.ttf - 31.96) / 31.96) * 100;
  const advice = {
    recommendation: ttfVsBase > 50 
      ? '⚖️ VAST TARIEF — maar wacht 4-6 weken voor weloverwogen keuze'
      : '⬇ VARIABEL TARIEF — blijf rationeel en monitor de markt',
    rationale: ttfVsBase > 50
      ? 'De huidige prijspiek wordt gedreven door geopolitieke schokken (Hormuz, Qatar LNG). Historisch gezien normaliseren dergelijke schokken binnen 2-5 maanden. Wie nu vastlegt, betaalt voor de volledige risicopremie. Wacht tot de impact van gasveld-herstel duidelijk is voor een weloverwogen keuze. Zekerheid primeert alleen bij krappe budgetten.'
      : 'TTF handelt op verhoogd niveau door tijdelijke supply shocks, maar structurele fundamentals blijven bearish op lange termijn. Variabele tarieven profiteren van normalisatie zodra Hormuz heropent en LNG-capaciteit herstelt. Monitor wekelijks en herbekijk jaarlijks. Geen reden tot haastbeslissing.'
  };

  return {
    date: dateStr,
    dateSlug,
    kpis,
    chartData,
    priceTable,
    geopoliticalContext,
    advice
  };
};
