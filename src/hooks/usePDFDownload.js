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

  const ttfChange = previous ? ((latest.ttf - previous.ttf) / Math.abs(previous.ttf)) * 100 : null;
  const belpexChange = previous ? ((latest.belpex - previous.belpex) / Math.abs(previous.belpex)) * 100 : null;
  const ttfVsBase = ((latest.ttf - 31.96) / 31.96) * 100;

  const dateStr = `${currentDate} \u00B7 ${currentTime}`;
  const dateSlug = currentDate.replace(/ /g, '_');

  const confirmedDates = ['27/02', '09/03', '11/03', '20/03', '21/03', '23/03'];

  return {
    date: dateStr,
    dateSlug,

    kpis: {
      ttf: latest.ttf, ttfChange,
      belpex: latest.belpex, belpexChange,
      storage: 26, brent: 113.00,
    },

    alert: `Hormuz crisis dag 21+ \u00B7 TTF \u20AC${latest.ttf.toFixed(2)} (${ttfVsBase > 0 ? '+' : ''}${ttfVsBase.toFixed(0)}% vs pre-crisis) \u00B7 Brent $113 \u00B7 Force majeure Qatar/Kuwait/UAE \u00B7 EU opslag 26%`,

    chartData: {
      ttf: marketData.map(d => ({ date: d.date, value: d.ttf })),
      belpex: marketData.map(d => ({ date: d.date, value: d.belpex })),
    },

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
      { title: 'Straat van Hormuz Blokkade', color: 'red', text: 'Volledig gesloten sinds 2 maart 2026. 21 aanvallen op koopvaardijschepen. Tankerverkeer -70%. 20% wereldwijde olie/gas afgesneden. Geen tekenen van de\u00EBscalatie; analisten verwachten 4-6 weken aanhoudend.' },
      { title: 'Force Majeure Golfstaten', color: 'amber', text: 'Qatar, Koeweit, UAE en Bahrein: force majeure op export. QatarEnergy stopte LNG-productie. Golfstaten -10M vaten/dag (-60%). Alternatieve routes Rode Zee beperkt.' },
      { title: 'Gasveld Aanvallen', color: 'red', text: 'Aanvallen op South Pars (Iran) en Ras Laffan (Qatar) vernietigen 17% Qatar LNG-export. Reparatie 3-5 maanden. TTF structureel \u20AC50-65 tot Q3 2026.' },
      { title: 'EU Gasopslag Kritiek', color: 'amber', text: 'Voorraden ~26% capaciteit (vs 52% vorig jaar). Duitsland 30%, Nederland 23.5%. Zomerinjectie moet 90% bereiken v\u00F3\u00F3r winter. Agressieve LNG-import vereist.' },
    ],

    gasStorage: [
      ['EU-gemiddelde (23 mrt)', '~26%', 'red'],
      ['Einde 2025', '~61%', 'amber'],
      ['Einde 2024', '~72%', 'green'],
      ['EU-doel (1 nov)', '90%', 'blue'],
      ['Nog te vullen', '~60 ppt', 'amber'],
    ],

    ieaReserves: [
      ['Volume', '400 mln vaten (record)'],
      ['% totale reserves', '~33% van 1.2 mld'],
      ['Status', 'Actief sinds 11/03'],
      ['Marktreactie', '$119 \u2192 $101/vat'],
      ['Effectiviteit', '~4 dagen globale vraag'],
    ],

    forecasts: [
      { name: 'Bearish', prob: '15%', color: 'green', ttf: '\u20AC28\u201338', belpex: '\u20AC50\u201370', trigger: 'Gasvelden herstellen 2-3 wk, Hormuz deels open, diplomatieke de-escalatie' },
      { name: 'Basis', prob: '45%', color: 'blue', ttf: '\u20AC38\u201355', belpex: '\u20AC72\u201395', trigger: 'Gasvelden 3-5 mnd buiten werking, Hormuz beperkt open, Qatar LNG -17%' },
      { name: 'Bullish', prob: '40%', color: 'red', ttf: '\u20AC55\u201385', belpex: '\u20AC95\u2013145', trigger: 'Nieuwe aanvallen infra, Hormuz dicht tot zomer, Qatar LNG langdurig stil' },
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
      ['EU Gasopslag', 'Injectieseizoen mrt-okt, doel 90%', 'amber'],
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
