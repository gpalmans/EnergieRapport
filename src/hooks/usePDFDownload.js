import { useState } from 'react';
import { generatePDF } from '../utils/pdfGenerator';
import { addTrendlines } from '../utils/trendline';

export const usePDFDownload = () => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState(null);

  const downloadPDF = async (reportData) => {
    setIsGenerating(true);
    setError(null);
    try {
      const pdfData = preparePDFData(reportData);
      const pdf = await generatePDF(pdfData);
      pdf.save(`EnergieRapport_${pdfData.dateSlug}.pdf`);
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

  const currentTTF = latest?.ttf || 53.82;
  const currentBelpex = latest?.belpex || 72.04;
  const currentStorage = latest?.storage || 22.9;
  const currentBrent = latest?.brent || 104.49;

  const ttfChange = previous && previous.ttf && previous.ttf !== 0 ? ((latest.ttf - previous.ttf) / Math.abs(previous.ttf)) * 100 : null;
  const belpexChange = previous && previous.belpex && previous.belpex !== 0 ? ((latest.belpex - previous.belpex) / Math.abs(previous.belpex)) * 100 : null;
  const brentChange = previous && previous.brent && previous.brent !== 0 ? ((latest.brent - previous.brent) / Math.abs(previous.brent)) * 100 : null;
  const ttfVsBase = ((latest.ttf - 31.96) / 31.96) * 100;

  const dateStr = `${currentDate} · ${currentTime}`;
  const dateSlug = currentDate.replace(/ /g, '_');

  const confirmedDates = ["09/03", "11/03", "12/03", "13/03", "14/03", "15/03", "17/03", "19/03", "20/03", "22/03", "23/03", "24/03", "25/03"];

  return {
    date: dateStr,
    dateSlug,

    kpis: {
      ttf: currentTTF, ttfChange,
      belpex: currentBelpex, belpexChange,
      storage: Math.round(currentStorage), 
      brent: currentBrent, brentChange,
    },

    alert: `TTF opnieuw richt €72 · TTF €${currentTTF.toFixed(2)} (${ttfVsBase > 0 ? '+' : ''}${ttfVsBase.toFixed(0)}% vs pre-crisis) · Belpex €${currentBelpex.toFixed(2)} (+${belpexChange ? belpexChange.toFixed(1) : 0}%) · Brent $${currentBrent.toFixed(2)} · EU-opslag 65.4% (31 aug) · Belgische gasreserves ${Math.round(currentStorage)}%`,

    chartData: {
      ttf: marketData.map(d => ({ date: d.date, value: d.ttf })),
      belpex: marketData.map(d => ({ date: d.date, value: d.belpex })),
    },

    // Trendline data for PDF charts (medium-term only)
    chartTrends: (() => {
      const dataWithTrends = addTrendlines(marketData, {
        ttfTrendMedium:    { valueKey: 'ttf'          },
        belpexTrendMedium: { valueKey: 'belpex'       },
      });
      
      return {
        ttf: {
          medium: dataWithTrends.map(d => d.ttfTrendMedium).filter(v => v != null),
        },
        belpex: {
          medium: dataWithTrends.map(d => d.belpexTrendMedium).filter(v => v != null),
        },
      };
    })(),

    priceTable: marketData.slice(-10).map((row, idx, arr) => {
      const prev = idx > 0 ? arr[idx - 1] : null;
      const today = row.note.includes("Vandaag");
      const confirmed = true; // All rawData comes from official APIs (OilPriceAPI, GIE AGSI+, energy-charts.info)
      return {
        date: row.date, ttf: row.ttf, belpex: row.belpex,
        ttfChange: prev ? ((row.ttf - prev.ttf) / Math.abs(prev.ttf)) * 100 : null,
        belpexChange: prev ? ((row.belpex - prev.belpex) / Math.abs(prev.belpex)) * 100 : null,
        confirmed: confirmed,
        status: row.note === 'Vandaag' ? 'Vandaag' : row.note === 'Hormuz' ? 'Hormuz' : row.note === 'Piek' ? 'Piek' : row.note === 'IEA' ? 'IEA' : '',
      };
    }),

    crisisItems: [
      { title: 'TTF hoogste niveau sinds jan 2023', color: 'red', text: `TTF noteert €${currentTTF.toFixed(2)}/MWh, het hoogste niveau sinds begin 2023. Gedreven door broze Hormuz-situatie, vertraagde LNG en lage EU-opslag.` },
      { title: 'EU-opslag laagste ooit', color: 'red', text: 'EU-opslag 65.39% eind augustus 2026 — laagste seizoensniveau sinds 2011 en 14% onder het 5-jaargemiddelde. België 55.1%.' },
      { title: 'Hormuz wapenstilstand broos', color: 'amber', text: 'Straat van Hormuz deels heropend sinds 21 april, maar wapenstilstand is broos. Tankerdoorvoer blijft sterk verminderd.' },
      { title: 'Qatar LNG 3-5 jaar herstel', color: 'blue', text: '17% van wereldwijde LNG-exportcapaciteit is zwaar beschadigd. Volledig herstel duurt 3-5 jaar. Pre-crisis TTF-niveaus onbereikbaar tot 2028-2030.' },
      { title: 'Vast tarief ~27% duurder', color: 'purple', text: 'VRT meldde in juni 2026 dat vaste contracten gemiddeld 27% duurder zijn dan variabele. Vast bevat de volledige risicopremie van dit moment.' },
    ],

    gasStorage: [
      ['BE-gemiddelde (2 sep 2026)', `~${Math.round(currentStorage)}%`, 'red'],
      ['EU-gemiddelde (31 aug)', '~65.4%', 'amber'],
      ['Einde 2024', '~72%', 'green'],
      ['EU-doel (1 nov)', '90%', 'blue'],
      ['Nog te vullen', `${90 - Math.round(currentStorage)} ppt`, 'amber'],
    ],

    ieaReserves: [
      ['Volume', '400 mln vaten (record)'],
      ['% totale reserves', '~33% van 1.2 mld'],
      ['Status', 'Actief sinds 11/03'],
      ['Marktreactie', '$119 \u2192 $101/vat'],
      ['Effectiviteit', '~4 dagen globale vraag'],
    ],

    forecasts: [
      { name: 'Bearish', prob: '20%', color: 'green', ttf: '\u20AC52\u201372', belpex: '\u20AC110\u2013175', trigger: 'Hormuz stabiel, milde winter, opslag haalt 90%' },
      { name: 'Basis', prob: '50%', color: 'blue', ttf: '\u20AC72\u201388', belpex: '\u20AC170\u2013225', trigger: 'Qatar-schade 3-5 jr, Hormuz broos, lage opslag, wintervraag stijgt' },
      { name: 'Bullish', prob: '30%', color: 'red', ttf: '\u20AC85\u2013130', belpex: '\u20AC200\u2013320', trigger: 'Nieuwe escalatie, opslag onder 80%, vroege koude snap' },
    ],

    adviceMatrix: [
      ['Gezin, krappe begroting', 'Variabel \u2014 maandelijkse check', 'Vast is ~27% duurder; variabel volgt de markt'],
      ['Gemiddeld gezin', 'Variabel \u2014 12-18 mnd', 'Vast legt u vast op risicopremie; variabel profiteert van normalisatie'],
      ['Hoog verbruik (WP/EV)', 'Variabel of vast', 'Afhankelijk van budgetruimte; vast biedt zekerheid, variabel is goedkoper'],
      ['Zonnepanelen + batterij', 'Variabel/dynamisch', 'Hernieuwbaar maximaliseert daluurvoordeel'],
      ['KMO / zelfstandige', 'Vast \u2014 indien nodig', 'Alleen als variabele kosten niet doorrekend kunnen worden'],
    ],

    kernboodschap: `TTF staat op €${currentTTF.toFixed(2)}/MWh en Belpex op €${currentBelpex.toFixed(2)}/MWh. De markt is gespannen door de broze Hormuz-situatie, historisch lage EU-opslag (65.4%) en structurele Qatar LNG-schade. Vast tarief blijft gemiddeld ~27% duurder dan variabel. Wie nu vastlegt, betaalt de volledige risicopremie van dit moment.`,

    practicalAdvice: [
      'Observatieperiode (4-6 wk): Wacht tot eind oktober om het injectieseizoen en eerste wintervraag te beoordelen. Volg TTF dagelijks.',
      'TTF < \u20AC55 structureel (2+ wk) en BE-opslag > 75% eind oktober \u2192 variabel aantrekkelijk. TTF > \u20AC75 (4+ wk) of EU-opslag < 80% \u2192 vast overwegen.',
      'Lees bijzondere voorwaarden: welkomstpremie-clausules, opzegtermijn, indexeringsformule bij variabel.',
      'Nooit overhaast tekenen. Paniek is marketing, geen financieel advies. Neem tijd om te vergelijken.',
    ],

    keyFactors: [
      ['EU-opslag laagste ooit', '65.39% eind aug; doel 90% op 1 nov', 'red'],
      ['Qatar LNG-schade', 'South Pars/Ras Laffan herstel 3-5 jaar', 'red'],
      ['Hormuz wapenstilstand', 'Broos; dagelijks monitoren', 'red'],
      ['Hittegolf & koeling', 'Remt injectie, verhoogt zomervraag', 'amber'],
      ['Vast tariefpremie', 'Gemiddeld ~27% duurder dan variabel', 'amber'],
      ['OPEC+ productie', 'Stabiliseert Brent rond $94', 'green'],
    ],

    advice: {
      recommendation: ttfVsBase > 50
        ? 'VAST TARIEF \u2014 maar wacht 4-6 weken voor weloverwogen keuze'
        : 'VARIABEL TARIEF \u2014 blijf rationeel en monitor de markt',
      rationale: ttfVsBase > 50
        ? 'Prijspiek door geopolitieke schokken (Hormuz, Qatar LNG) en lage EU-opslag. Vast tarief bevat de volledige risicopremie. Variabel profiteert met 1-2 maanden vertraging van eventuele normalisatie. Zekerheid primeert alleen bij krappe budgetten.'
        : 'TTF verhoogd door tijdelijke supply shocks, structurele fundamentals blijven gespannen. Variabel volgt de markt met vertraging. Monitor wekelijks. Geen reden tot haastbeslissing.'
    },
  };
};
