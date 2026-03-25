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

  const ttfChange = previous ? ((latest.ttf - previous.ttf) / Math.abs(previous.ttf)) * 100 : null;
  const belpexChange = previous ? ((latest.belpex - previous.belpex) / Math.abs(previous.belpex)) * 100 : null;
  const brentChange = previous ? ((latest.brent - previous.brent) / Math.abs(previous.brent)) * 100 : null;

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

    alert: `Hormuz crisis dag 21+ · TTF €${currentTTF.toFixed(2)} (${ttfVsBase > 0 ? '+' : ''}${ttfVsBase.toFixed(0)}% vs pre-crisis) · Brent $${currentBrent.toFixed(2)} · Force majeure Qatar/Kuwait/UAE · Belgische gasreserves ${Math.round(currentStorage)}%`,

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
      return {
        date: row.date, ttf: row.ttf, belpex: row.belpex,
        ttfChange: prev ? ((row.ttf - prev.ttf) / Math.abs(prev.ttf)) * 100 : null,
        belpexChange: prev ? ((row.belpex - prev.belpex) / Math.abs(prev.belpex)) * 100 : null,
        confirmed: confirmedDates.includes(row.date),
        status: row.note === 'Vandaag' ? 'Vandaag' : row.note === 'Hormuz' ? 'Hormuz' : row.note === 'Piek' ? 'Piek' : row.note === 'IEA' ? 'IEA' : '',
      };
    }),

    crisisItems: [
      { title: 'Mega Tariefstijging België', color: 'red', text: 'Mega verhoogt onverwacht tarieven vanaf 6 maart: gas +14% tot +29%, elektriciteit +12% tot +22%. CREG betreurt deze praktijk en noemt het \'gevaarlijk precedent\' voor consumenten.' },
      { title: 'Hormuz Crisis Volatiliteit', color: 'amber', text: 'Onrust Midden-Oosten veroorzaakt grote schommelingen in TTF-prijzen. Gasunie adviseert strategische noodvoorraad aan te leggen. Termijnprijzen elektriciteit volgen sterke stijging gasprijzen.' },
      { title: 'Energy Sector Rotation', color: 'yellow', text: 'Energy Select Sector SPDR stijgt +8% in maart door geopolitieke spanningen. Great rotation naar energie sectoren terwijl yield-sensitive sectoren dalen.' },
      { title: 'IEA Consumentenadvies', color: 'blue', text: 'IEA adviseert consumenten energieverbruik te verminderen: werk thuis, rij langzamer, gebruik geen gas kokers. Doel is prijzen stabiliseren tijdens conflict.' },
      { title: 'Brent Prijsstijging', color: 'purple', text: `Brent handelt op $${currentBrent.toFixed(2)}/vat (+${((currentBrent - 101.55) / 101.55 * 100).toFixed(1)}% vs gisteren) na optimisme over Iran de-escalatie. Stijging volgt op scherpe daling van -11% op maandag.` },
    ],

    gasStorage: [
      [`BE-gemiddelde (${currentDate.split(' ')[0]} mrt)`, `~${Math.round(currentStorage)}%`, 'red'],
      ['Einde 2025', '~61%', 'amber'],
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
      { name: 'Bearish', prob: '20%', color: 'green', ttf: '\u20AC30\u201340', belpex: '\u20AC50\u201365', trigger: 'Gasvelden herstellen 2-3 wk, Hormuz deels open, diplomatieke de-escalatie' },
      { name: 'Basis', prob: '55%', color: 'blue', ttf: '\u20AC40\u201358', belpex: '\u20AC70\u201385', trigger: 'Gasvelden 3-5 mnd buiten werking, Hormuz beperkt open, Qatar LNG -17%' },
      { name: 'Bullish', prob: '25%', color: 'red', ttf: '\u20AC58\u201375', belpex: '\u20AC85\u2013110', trigger: 'Nieuwe aanvallen infra, Hormuz dicht tot zomer, Qatar LNG langdurig stil' },
    ],

    adviceMatrix: [
      ['Gezin, krappe begroting', 'Vast \u2014 wacht 4-6 wk', 'Zekerheid primeert; wacht gasveld-impact af'],
      ['Gemiddeld gezin', 'Variabel', 'Structureel bearish na crisis; normalisatie 2-5 mnd'],
      ['Hoog verbruik (WP/EV)', 'Vast \u2014 weloverwogen', 'Hoge blootstelling; vaste maandkost stabiel'],
      ['Zonnepanelen + batterij', 'Variabel/dynamisch', 'Hernieuwbaar maximaliseert daluurvoordeel'],
      ['KMO / zelfstandige', 'Vast \u2014 budgetstabiliteit', 'Voorspelbare kosten; herzie na 12 maanden'],
    ],

    kernboodschap: 'De huidige marktbeweging is extreem, maar niet ongezien. In 2022 sloten tienduizenden Belgische gezinnen een vast contract af op een historisch piekmoment, terwijl de markt nadien sterk normaliseerde. Hoewel de Vlaamse consument wettelijk altijd kosteloos kan wisselen, gaan welkomstpremies en loyaliteitsvoordelen verloren bij vroegtijdig vertrek \u2014 waardoor velen alsnog te veel betaalden.',

    practicalAdvice: [
      'Observatieperiode (4-6 wk): Wacht tot eind april om gasveld-herstel impact te beoordelen. Volg TTF dagelijks.',
      'TTF < \u20AC50 structureel (2+ wk) \u2192 variabel aantrekkelijk. TTF > \u20AC60 (6+ wk) \u2192 vast overwegen.',
      'Lees bijzondere voorwaarden: welkomstpremie-clausules, opzegtermijn, indexeringsformule bij variabel.',
      'Nooit overhaast tekenen. Paniek is marketing, geen financieel advies. Neem tijd om te vergelijken.',
    ],

    keyFactors: [
      ['Hormuz Blokkade', 'Heropening vs. prolongatie \u2014 dagelijks monitoren', 'red'],
      ['Gasveld Herstel', 'South Pars/Ras Laffan reparatie 3-5 mnd', 'red'],
      ['België gasopslag', 'Injectieseizoen mrt-okt, doel 90%', 'amber'],
      ['IEA Reserves', 'Nog 800M vaten beschikbaar, 2e vrijgave onwaarschijnlijk', 'amber'],
      ['Diplomatie VS/Israel', 'Escalatie +10-15%, de-escalatie -20-30%', 'green'],
      ['VREG Tarieven', 'Consumentenprijzen +15-25% in mei-juni 2026', 'green'],
    ],

    advice: {
      recommendation: ttfVsBase > 50
        ? 'VAST TARIEF \u2014 maar wacht 4-6 weken voor weloverwogen keuze'
        : 'VARIABEL TARIEF \u2014 blijf rationeel en monitor de markt',
      rationale: ttfVsBase > 50
        ? 'Prijspiek door geopolitieke schokken (Hormuz, Qatar LNG). Historisch normaliseren schokken binnen 2-5 maanden. Wie nu vastlegt betaalt de volledige risicopremie. Zekerheid primeert alleen bij krappe budgetten.'
        : 'TTF verhoogd door tijdelijke supply shocks, structurele fundamentals bearish op lange termijn. Variabel profiteert van normalisatie. Monitor wekelijks. Geen reden tot haastbeslissing.',
    },
  };
};
