import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

const PW = 794, PH = 1123, SCALE = 2;

const colorHex = { red: '#dc2626', amber: '#d97706', green: '#16a34a', blue: '#0284c7', purple: '#7c3aed' };
const colorBg  = { red: '#fef2f2', amber: '#fffbeb', green: '#f0fdf4', blue: '#f0f9ff', purple: '#faf5ff' };

const pill = (text, color) =>
  `<span style="display:inline-block;padding:2px 8px;border-radius:10px;font-size:8px;font-weight:700;color:#fff;background:${color};letter-spacing:.3px">${text}</span>`;

const secTitle = (text, color) =>
  `<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
    <div style="width:4px;height:16px;border-radius:2px;background:${color}"></div>
    <span style="font-size:11px;font-weight:800;color:#0f172a;text-transform:uppercase;letter-spacing:.8px">${text}</span>
    <div style="flex:1;height:1px;background:linear-gradient(90deg,${color}33,transparent)"></div>
  </div>`;

const svgChart = (points, w, h, color, label, trendlines = {}) => {
  if (!points || points.length < 2) return '';
  const vals = points.map(p => p.value);
  const mn = Math.min(...vals), mx = Math.max(...vals);
  const pad = (mx - mn) * 0.1 || 2;
  const lo = mn - pad, hi = mx + pad, range = hi - lo;
  const mL = 40, mR = 10, mT = 24, mB = 26;
  const iw = w - mL - mR, ih = h - mT - mB;
  const toX = i => mL + (i / (points.length - 1)) * iw;
  const toY = v => mT + ih - ((v - lo) / range) * ih;

  const polyline = points.map((p, i) => `${toX(i).toFixed(1)},${toY(p.value).toFixed(1)}`).join(' ');
  const gradId = `g${color.replace('#', '')}`;

  // Trendlines (medium-term only)
  let trendlineSvg = '';
  const trendColor = '#22d3ee';
  const trendLabel = 'Middellange termijn';
  
  if (trendlines.medium && Array.isArray(trendlines.medium)) {
    const trendPolyline = trendlines.medium.map((v, i) => {
      if (v == null) return '';
      return `${toX(i).toFixed(1)},${toY(v).toFixed(1)}`;
    }).filter(Boolean).join(' ');
    
    if (trendPolyline) {
      trendlineSvg += `<polyline points="${trendPolyline}" fill="none" stroke="${trendColor}" stroke-width="2" stroke-dasharray="8,4" stroke-linejoin="round" stroke-linecap="round"/>`;
    }
  }

  // Legend
  let legendSvg = '';
  if (trendlines.medium && Array.isArray(trendlines.medium)) {
    const legendY = h - 8;
    const legendX = mL + 10;
    legendSvg += `<line x1="${legendX}" y1="${legendY}" x2="${legendX + 15}" y2="${legendY}" stroke="${trendColor}" stroke-width="2" stroke-dasharray="8,4"/>`;
    legendSvg += `<text x="${legendX + 20}" y="${legendY + 3}" fill="#64748b" font-size="7" font-family="system-ui">${trendLabel}</text>`;
  }

  let yTicks = '';
  for (let i = 0; i <= 4; i++) {
    const v = lo + (range / 4) * i;
    const py = toY(v).toFixed(1);
    yTicks += `<line x1="${mL}" y1="${py}" x2="${mL + iw}" y2="${py}" stroke="#e2e8f0" stroke-width="0.5"/>`;
    yTicks += `<text x="${mL - 5}" y="${+py + 3}" text-anchor="end" fill="#64748b" font-size="9" font-family="system-ui">\u20AC${v.toFixed(0)}</text>`;
  }
  let xTicks = '';
  for (let i = 0; i < 5; i++) {
    const idx = Math.round(i * (points.length - 1) / 4);
    const px = toX(idx).toFixed(1);
    xTicks += `<text x="${px}" y="${mT + ih + 16}" text-anchor="middle" fill="#64748b" font-size="8" font-family="system-ui">${points[idx].date}</text>`;
  }
  const lastPt = points[points.length - 1];
  const lx = toX(points.length - 1), ly = toY(lastPt.value);

  return `<svg viewBox="0 0 ${w} ${h}" width="100%" height="${h}" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="${gradId}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="${color}" stop-opacity="0.2"/>
        <stop offset="100%" stop-color="${color}" stop-opacity="0.02"/>
      </linearGradient>
    </defs>
    <rect width="${w}" height="${h}" rx="8" fill="#fff" stroke="#e2e8f0" stroke-width="1"/>
    <text x="${w/2}" y="16" text-anchor="middle" fill="${color}" font-size="11" font-weight="700" font-family="system-ui">${label}</text>
    ${yTicks}${xTicks}
    <line x1="${mL}" y1="${mT+ih}" x2="${mL+iw}" y2="${mT+ih}" stroke="#cbd5e1" stroke-width="0.7"/>
    <polygon points="${toX(0).toFixed(1)},${(mT+ih).toFixed(1)} ${polyline} ${toX(points.length-1).toFixed(1)},${(mT+ih).toFixed(1)}" fill="url(#${gradId})"/>
    <polyline points="${polyline}" fill="none" stroke="${color}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>
    ${trendlineSvg}
    <circle cx="${lx.toFixed(1)}" cy="${ly.toFixed(1)}" r="5" fill="#fff" stroke="${color}" stroke-width="2.5"/>
    <circle cx="${lx.toFixed(1)}" cy="${ly.toFixed(1)}" r="2" fill="${color}"/>
    <rect x="${lx - 24}" y="${ly - 20}" width="48" height="14" rx="4" fill="${color}"/>
    <text x="${lx.toFixed(1)}" y="${(ly - 10).toFixed(1)}" text-anchor="middle" fill="#fff" font-size="9" font-weight="700" font-family="system-ui">\u20AC${lastPt.value.toFixed(1)}</text>
    ${legendSvg}
  </svg>`;
};

const buildPage1 = (d) => {
  const kpis = [
    { l: 'TTF Gas', v: `\u20AC${d.kpis.ttf.toFixed(2)}`, u: '/MWh', ch: d.kpis.ttfChange, c: '#0284c7', bg: '#f0f9ff', icon: '\uD83D\uDD25' },
    { l: 'Belpex', v: `\u20AC${d.kpis.belpex}`, u: '/MWh', ch: d.kpis.belpexChange, c: '#7c3aed', bg: '#faf5ff', icon: '\u26A1' },
    { l: 'Belgische gasopslag', v: `${d.kpis.storage}%`, u: '', ch: null, c: '#d97706', bg: '#fffbeb', icon: '\uD83D\uDCE6' },
    { l: 'Brent Olie', v: `$${d.kpis.brent.toFixed(2)}`, u: '/vat', ch: d.kpis.brentChange, c: '#475569', bg: '#f8fafc', icon: '\uD83D\uDEE2\uFE0F' },
  ];

  const kpiCards = kpis.map(k => {
    const chHtml = k.ch !== null
      ? `<div style="font-size:10px;font-weight:700;color:${k.ch > 0 ? '#dc2626' : '#16a34a'};margin-top:2px">${k.ch > 0 ? '\u25B2' : '\u25BC'} ${k.ch > 0 ? '+' : ''}${k.ch.toFixed(1)}%</div>`
      : '';
    return `<div style="flex:1;background:${k.bg};border-radius:10px;padding:12px 14px;border-top:3px solid ${k.c};box-shadow:0 1px 3px rgba(0,0,0,.08)">
      <div style="font-size:9px;font-weight:700;color:${k.c};text-transform:uppercase;letter-spacing:.7px;margin-bottom:4px">${k.icon} ${k.l}</div>
      <div style="font-size:20px;font-weight:900;color:#0f172a">${k.v}<span style="font-size:11px;font-weight:500;color:#64748b">${k.u}</span></div>
      ${chHtml}
    </div>`;
  }).join('');

  const tableRows = d.priceTable.map((r, i) => {
    const bg = i % 2 === 0 ? '#f8fafc' : '#ffffff';
    const ttfChColor = r.ttfChange > 0 ? '#dc2626' : '#16a34a';
    const ttfChStr = r.ttfChange !== null ? `<span style="color:${ttfChColor};font-weight:700">${r.ttfChange > 0 ? '+' : ''}${r.ttfChange.toFixed(1)}%</span>` : '';
    const bxChColor = r.belpexChange > 0 ? '#dc2626' : '#16a34a';
    const bxChStr = r.belpexChange !== null ? `<span style="color:${bxChColor};font-weight:700">${r.belpexChange > 0 ? '+' : ''}${r.belpexChange.toFixed(1)}%</span>` : '';
    const statusBadge = r.status ? pill(r.status, { Vandaag: '#0284c7', Piek: '#dc2626', IEA: '#16a34a', Hormuz: '#d97706' }[r.status] || '#64748b') : '';
    const conf = r.confirmed ? ` <span style="color:#16a34a">\u2713</span>` : '';
    return `<tr style="background:${bg}">
      <td style="padding:5px 8px;font-size:10px;color:#1e293b;${r.confirmed ? 'font-weight:700' : ''}">${r.date}${conf}</td>
      <td style="padding:5px 8px;font-size:10px;color:#1e293b;font-weight:600">\u20AC${r.ttf.toFixed(2)}</td>
      <td style="padding:5px 8px;font-size:10px">${ttfChStr}</td>
      <td style="padding:5px 8px;font-size:10px;color:#1e293b">\u20AC${r.belpex.toFixed(2)}</td>
      <td style="padding:5px 8px;font-size:10px">${bxChStr}</td>
      <td style="padding:5px 8px">${statusBadge}</td>
    </tr>`;
  }).join('');

  const crisisCards = d.crisisItems.map(it => {
    const c = colorHex[it.color] || '#64748b';
    const bg = colorBg[it.color] || '#f8fafc';
    return `<div style="flex:1;min-width:46%;background:${bg};border-radius:8px;padding:10px 12px;border-left:3px solid ${c};box-shadow:0 1px 2px rgba(0,0,0,.05)">
      <div style="font-size:9.5px;font-weight:800;color:${c};margin-bottom:3px;text-transform:uppercase;letter-spacing:.3px">${it.title}</div>
      <div style="font-size:8.5px;color:#475569;line-height:1.5">${it.text}</div>
    </div>`;
  }).join('');

  return `<div style="padding:0 28px 16px">
    <!-- HEADER -->
    <div style="background:linear-gradient(135deg,#0f172a 0%,#1e3a8a 50%,#0f172a 100%);border-radius:0 0 14px 14px;padding:20px 26px;margin:0 -28px 14px;display:flex;align-items:center;gap:18px">
      <img src="/fulllogo_transparent_nobuffer.png" style="height:40px;object-fit:contain" crossorigin="anonymous"/>
      <div style="flex:1">
        <div style="font-size:24px;font-weight:900;color:#fff;letter-spacing:2px">ENERGIERAPPORT</div>
        <div style="font-size:11px;color:#93c5fd;margin-top:3px;letter-spacing:.5px">Marktanalyse  \u2014  ${d.date}</div>
      </div>
      <div style="text-align:right">
        <div style="font-size:8px;color:#94a3b8;text-transform:uppercase;letter-spacing:.5px">Gegenereerd</div>
        <div style="font-size:9px;color:#cbd5e1;margin-top:1px">${new Date().toLocaleString('nl-NL')}</div>
      </div>
    </div>

    <!-- COPYRIGHT -->
    <div style="text-align:center;font-size:7.5px;color:#94a3b8;padding:2px 0 10px;margin-bottom:10px;border-bottom:1px solid #e2e8f0">
      \u00A9 PWR.IT CommV \u2014 Alle rechten voorbehouden. Gebruik alleen met schriftelijke toestemming.
    </div>

    <!-- ALERT -->
    <div style="background:#fef2f2;border-left:4px solid #dc2626;border-radius:0 8px 8px 0;padding:10px 14px;margin-bottom:12px;box-shadow:0 1px 3px rgba(220,38,38,.15)">
      <div style="font-size:10px;font-weight:800;color:#dc2626;letter-spacing:.8px;margin-bottom:3px">\u26A0 KRITIEKE MARKTSITUATIE</div>
      <div style="font-size:9px;color:#7f1d1d;line-height:1.5">${d.alert}</div>
    </div>

    <!-- KPIs -->
    <div style="display:flex;gap:10px;margin-bottom:12px">${kpiCards}</div>

    <!-- CHARTS -->
    ${secTitle('Prijsontwikkeling', '#0284c7')}
    <div style="display:flex;gap:10px;margin-bottom:14px">
      <div style="flex:1">${svgChart(d.chartData.ttf, 365, 185, '#0284c7', 'TTF Gas (\u20AC/MWh)', d.chartTrends?.ttf || {})}</div>
      <div style="flex:1">${svgChart(d.chartData.belpex, 365, 185, '#7c3aed', 'Belpex (\u20AC/MWh)', d.chartTrends?.belpex || {})}</div>
    </div>

    <!-- PRICE TABLE -->
    ${secTitle('Historische Prijzen \u2014 Laatste 10 Dagen', '#0f172a')}
    <table style="width:100%;border-collapse:collapse;border-radius:8px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.08)">
      <thead><tr style="background:linear-gradient(90deg,#0f172a,#1e293b)">
        ${['Datum','TTF','\u0394 TTF','Belpex','\u0394 Belpex','Status'].map(h =>
          `<th style="padding:6px 10px;text-align:left;font-size:9px;color:#94a3b8;font-weight:600;text-transform:uppercase;letter-spacing:.5px">${h}</th>`).join('')}
      </tr></thead>
      <tbody>${tableRows}</tbody>
    </table>

    <div style="height:14px"></div>

    <!-- CRISIS ITEMS -->
    ${secTitle('Geopolitieke Crisissituatie', '#d97706')}
    <div style="display:flex;flex-wrap:wrap;gap:8px">${crisisCards}</div>
  </div>`;
};

const buildPage2 = (d) => {
  const storageRows = d.gasStorage.map(([label, val, col]) =>
    `<div style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid #f1f5f9">
      <span style="font-size:10px;color:#475569">${label}</span>
      <span style="font-size:10px;font-weight:700;color:${colorHex[col] || '#1e293b'}">${val}</span>
    </div>`).join('');

  const ieaRows = d.ieaReserves.map(([label, val]) =>
    `<div style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid #f1f5f9">
      <span style="font-size:10px;color:#475569">${label}</span>
      <span style="font-size:10px;font-weight:700;color:#0284c7">${val}</span>
    </div>`).join('');

  const scenarioCards = d.forecasts.map(f => {
    const c = colorHex[f.color] || '#0284c7';
    const bg = colorBg[f.color] || '#f0f9ff';
    return `<div style="flex:1;border-radius:10px;overflow:hidden;box-shadow:0 2px 4px rgba(0,0,0,.08)">
      <div style="background:${c};padding:8px 12px;text-align:center">
        <div style="font-size:12px;font-weight:900;color:#fff;letter-spacing:.5px">${f.name}</div>
        <div style="font-size:10px;color:#ffffffcc;font-weight:600">Kans: ${f.prob}</div>
      </div>
      <div style="background:${bg};padding:10px 12px">
        <div style="font-size:11px;font-weight:800;color:${c}">TTF: ${f.ttf}</div>
        <div style="font-size:11px;font-weight:800;color:${c};margin-bottom:5px">Belpex: ${f.belpex}</div>
        <div style="font-size:8.5px;color:#475569;line-height:1.5">${f.trigger}</div>
      </div>
    </div>`;
  }).join('');

  const factorRows = d.keyFactors.map(([title, desc, col]) => {
    const c = colorHex[col] || '#64748b';
    return `<div style="display:flex;align-items:center;gap:10px;padding:5px 0;border-bottom:1px solid #f1f5f9">
      <div style="width:10px;height:10px;border-radius:50%;background:${c};flex-shrink:0;box-shadow:0 0 0 3px ${c}22"></div>
      <span style="font-size:10px;font-weight:700;color:#1e293b;min-width:120px">${title}</span>
      <span style="font-size:9px;color:#64748b;flex:1">${desc}</span>
    </div>`;
  }).join('');

  const matrixRows = d.adviceMatrix.map(([profiel, aanb, motiv], i) => {
    const bg = i % 2 === 0 ? '#f8fafc' : '#ffffff';
    return `<tr style="background:${bg}">
      <td style="padding:6px 10px;font-size:9.5px;font-weight:700;color:#1e293b">${profiel}</td>
      <td style="padding:6px 10px;font-size:9.5px;color:#0284c7;font-weight:700">${aanb}</td>
      <td style="padding:6px 10px;font-size:9px;color:#64748b">${motiv}</td>
    </tr>`;
  }).join('');

  const adviceSteps = d.practicalAdvice.map(s =>
    `<div style="display:flex;gap:8px;align-items:flex-start;padding:4px 0">
      <div style="width:6px;height:6px;border-radius:50%;background:#16a34a;margin-top:4px;flex-shrink:0"></div>
      <span style="font-size:9px;color:#1e293b;line-height:1.5">${s}</span>
    </div>`).join('');

  return `<div style="padding:24px 28px">
    <!-- GAS STORAGE + IEA -->
    <div style="display:flex;gap:12px;margin-bottom:14px">
      <div style="flex:1;background:#fffbeb;border-radius:10px;padding:12px 16px;border-left:4px solid #d97706;box-shadow:0 1px 3px rgba(0,0,0,.06)">
        <div style="font-size:10px;font-weight:800;color:#d97706;text-transform:uppercase;letter-spacing:.7px;margin-bottom:8px">\uD83D\uDCE6 België gasopslag</div>
        ${storageRows}
      </div>
      <div style="flex:1;background:#f0f9ff;border-radius:10px;padding:12px 16px;border-left:4px solid #0284c7;box-shadow:0 1px 3px rgba(0,0,0,.06)">
        <div style="font-size:10px;font-weight:800;color:#0284c7;text-transform:uppercase;letter-spacing:.7px;margin-bottom:8px">\uD83D\uDEE1\uFE0F IEA Strategische Reserves</div>
        ${ieaRows}
      </div>
    </div>

    <!-- FORECASTS -->
    ${secTitle("Forecast Scenario's (apr\u2013mei 2026)", '#0284c7')}
    <div style="display:flex;gap:10px;margin-bottom:14px">${scenarioCards}</div>

    <!-- KEY FACTORS -->
    ${secTitle('Sleutelfactoren om op te volgen', '#475569')}
    <div style="background:#f8fafc;border-radius:10px;padding:10px 14px;margin-bottom:14px;box-shadow:0 1px 2px rgba(0,0,0,.04)">
      ${factorRows}
    </div>

    <!-- ADVICE MATRIX -->
    ${secTitle('Adviesmatrix per Profiel', '#16a34a')}
    <table style="width:100%;border-collapse:collapse;border-radius:8px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.08);margin-bottom:14px">
      <thead><tr style="background:linear-gradient(90deg,#0f172a,#1e293b)">
        ${['Profiel','Aanbeveling','Motivering'].map(h =>
          `<th style="padding:6px 10px;text-align:left;font-size:9px;color:#94a3b8;font-weight:600;text-transform:uppercase;letter-spacing:.5px">${h}</th>`).join('')}
      </tr></thead>
      <tbody>${matrixRows}</tbody>
    </table>

    <!-- KERNBOODSCHAP -->
    <div style="background:linear-gradient(135deg,#eff6ff,#dbeafe);border:2px solid #3b82f6;border-radius:12px;padding:14px 18px;margin-bottom:14px;box-shadow:0 2px 8px rgba(59,130,246,.12)">
      <div style="font-size:12px;font-weight:900;color:#1e40af;margin-bottom:6px;letter-spacing:.5px">\uD83C\uDFAF KERNBOODSCHAP</div>
      <div style="font-size:9.5px;color:#1e3a8a;line-height:1.6;margin-bottom:10px">${d.kernboodschap}</div>
      <div style="display:flex;gap:10px">
        <div style="flex:1;background:#fff;border-radius:8px;padding:8px 12px;border-left:3px solid #3b82f6;box-shadow:0 1px 2px rgba(0,0,0,.04)">
          <div style="font-size:9px;font-weight:800;color:#1d4ed8">Korte termijn (2\u20135 mnd)</div>
          <div style="font-size:8.5px;color:#1e3a8a;line-height:1.4;margin-top:3px">Verhoogd niveau door gasveld schade. TTF \u20AC50\u201365 tot Q3 2026.</div>
        </div>
        <div style="flex:1;background:#fff;border-radius:8px;padding:8px 12px;border-left:3px solid #3b82f6;box-shadow:0 1px 2px rgba(0,0,0,.04)">
          <div style="font-size:9px;font-weight:800;color:#1d4ed8">Middellange termijn (6\u201318 mnd)</div>
          <div style="font-size:8.5px;color:#1e3a8a;line-height:1.4;margin-top:3px">LNG-aanbodgolf + injectieseizoen \u2192 structurele normalisatie.</div>
        </div>
      </div>
    </div>

    <!-- PRACTICAL ADVICE -->
    <div style="background:linear-gradient(135deg,#f0fdf4,#dcfce7);border:2px solid #16a34a;border-radius:12px;padding:14px 18px;margin-bottom:14px;box-shadow:0 2px 8px rgba(22,163,74,.12)">
      <div style="font-size:11px;font-weight:900;color:#15803d;margin-bottom:8px">\u2705 ${d.advice.recommendation}</div>
      ${adviceSteps}
    </div>

    <!-- SOURCES + FOOTER -->
    <div style="font-size:7.5px;color:#94a3b8;line-height:1.5;margin-bottom:4px">
      <span style="font-weight:700;color:#64748b">Bronnen:</span> ENTSO-E \u00B7 EPEX SPOT \u00B7 ICE Endex \u00B7 GIE AGSI+ \u00B7 Trading Economics \u00B7 Reuters \u00B7 Bloomberg \u00B7 IEA \u00B7 VREG \u00B7 CREG
    </div>
    <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0 0;border-top:1px solid #e2e8f0">
      <div style="font-size:7.5px;color:#94a3b8">PWR.IT CommV \u00A9 2026 \u2014 Vertrouwelijk. Niet voor verdere verspreiding.</div>
      <div style="font-size:7.5px;color:#94a3b8">Pagina 2 / 2</div>
    </div>
  </div>`;
};

export const generatePDF = async (data) => {
  const container = document.createElement('div');
  container.style.cssText = `position:fixed;left:-9999px;top:0;width:${PW}px;font-family:system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;-webkit-font-smoothing:antialiased;`;
  document.body.appendChild(container);

  try {
    const pdf = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });

    for (let pageNum = 0; pageNum < 2; pageNum++) {
      if (pageNum > 0) pdf.addPage();
      const page = document.createElement('div');
      page.style.cssText = `width:${PW}px;height:${PH}px;background:#ffffff;color:#1e293b;overflow:hidden;box-sizing:border-box;`;
      page.innerHTML = pageNum === 0 ? buildPage1(data) : buildPage2(data);
      container.appendChild(page);

      if (pageNum === 0) {
        const imgs = page.querySelectorAll('img');
        await Promise.all([...imgs].map(img => new Promise(r => {
          if (img.complete) return r();
          img.onload = r; img.onerror = r;
        })));
      }

      const canvas = await html2canvas(page, {
        scale: SCALE, useCORS: true, backgroundColor: '#ffffff',
        width: PW, height: PH, logging: false,
      });
      pdf.addImage(canvas.toDataURL('image/jpeg', 0.95), 'JPEG', 0, 0, 210, 297, undefined, 'FAST');
      container.removeChild(page);
    }

    return pdf;
  } finally {
    document.body.removeChild(container);
  }
};
