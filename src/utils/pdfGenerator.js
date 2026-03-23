import jsPDF from 'jspdf';

export const generatePDF = (data) => {
  const pdf = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4'
  });

  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();
  const margin = 15;
  const contentWidth = pageWidth - (2 * margin);
  let yPos = margin;

  // Professional color palette
  const colors = {
    primary: [14, 165, 233],      // Blue #0ea5e9
    secondary: [167, 139, 250],   // Purple #a78bfa
    success: [34, 197, 94],       // Green #22c55e
    danger: [239, 68, 68],        // Red #ef4444
    warning: [234, 179, 8],       // Yellow #eab308
    dark: [30, 41, 59],           // Dark blue #1e293b
    gray: [148, 163, 184],        // Gray #94a3b8
    lightGray: [226, 232, 240]    // Light gray #e2e8f0
  };

  const addText = (text, x, y, options = {}) => {
    const fontSize = options.fontSize || 10;
    const fontStyle = options.fontStyle || 'normal';
    const align = options.align || 'left';
    
    pdf.setFontSize(fontSize);
    pdf.setFont('helvetica', fontStyle);
    pdf.text(text, x, y, { align });
  };

  const addLine = (y, color = '#CCCCCC') => {
    pdf.setDrawColor(color);
    pdf.setLineWidth(0.2);
    pdf.line(margin, y, pageWidth - margin, y);
  };

  const checkPageBreak = (requiredSpace) => {
    if (yPos + requiredSpace > pageHeight - margin) {
      pdf.addPage();
      yPos = margin;
      return true;
    }
    return false;
  };

  // HEADER BACKGROUND
  pdf.setFillColor(...colors.dark);
  pdf.rect(0, 0, pageWidth, 45, 'F');

  // LOGO
  try {
    const logoImg = document.querySelector('img[alt="PWR.IT CommV"]');
    if (logoImg) {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      canvas.width = logoImg.naturalWidth;
      canvas.height = logoImg.naturalHeight;
      ctx.drawImage(logoImg, 0, 0);
      const logoData = canvas.toDataURL('image/png');
      
      const logoWidth = 45;
      const logoHeight = (logoImg.naturalHeight / logoImg.naturalWidth) * logoWidth;
      pdf.addImage(logoData, 'PNG', margin, yPos + 2, logoWidth, logoHeight);
    }
  } catch (e) {
    console.warn('Logo not loaded for PDF:', e);
  }

  // TITLE
  pdf.setTextColor(255, 255, 255);
  pdf.setFontSize(20);
  pdf.setFont('helvetica', 'bold');
  pdf.text('ENERGIERAPPORT', pageWidth / 2, yPos + 12, { align: 'center' });
  
  pdf.setFontSize(11);
  pdf.setFont('helvetica', 'normal');
  pdf.setTextColor(...colors.primary);
  pdf.text(`Marktanalyse — ${data.date}`, pageWidth / 2, yPos + 20, { align: 'center' });
  
  pdf.setFontSize(8);
  pdf.setTextColor(...colors.gray);
  pdf.text('TTF Gas · Belpex Elektriciteit · Geopolitieke Context · Tariefadvies', pageWidth / 2, yPos + 26, { align: 'center' });
  
  yPos = 45 + 3;
  
  // COPYRIGHT DISCLAIMER
  pdf.setFillColor(250, 250, 250);
  pdf.rect(margin, yPos, contentWidth, 10, 'F');
  pdf.setDrawColor(...colors.lightGray);
  pdf.setLineWidth(0.3);
  pdf.rect(margin, yPos, contentWidth, 10);
  
  pdf.setFontSize(7);
  pdf.setTextColor(80, 80, 80);
  const disclaimer = '© PWR.IT CommV — Alle rechten voorbehouden. Gebruik alleen met schriftelijke toestemming.';
  pdf.text(disclaimer, pageWidth / 2, yPos + 6, { align: 'center' });
  pdf.setTextColor(0, 0, 0);
  yPos += 14;

  // KPI SECTION HEADER
  pdf.setFillColor(...colors.primary);
  pdf.rect(margin, yPos, contentWidth, 8, 'F');
  pdf.setTextColor(255, 255, 255);
  pdf.setFontSize(11);
  pdf.setFont('helvetica', 'bold');
  pdf.text('📊 HUIDIGE MARKTPRIJZEN', margin + 2, yPos + 5.5);
  pdf.setFont('helvetica', 'normal');
  yPos += 10;

  const kpis = [
    { label: 'TTF Gas', value: `€${data.kpis.ttf.toFixed(2)}/MWh`, change: data.kpis.ttfChange, color: colors.primary, icon: '🔥' },
    { label: 'Belpex Elektriciteit', value: `€${data.kpis.belpex.toFixed(2)}/MWh`, change: data.kpis.belpexChange, color: colors.secondary, icon: '⚡' },
    { label: 'EU Gasopslag', value: `${data.kpis.storage.toFixed(0)}%`, change: data.kpis.storageChange, color: colors.warning, icon: '📦' },
    { label: 'Brent Ruwe Olie', value: `$${data.kpis.brent.toFixed(2)}/vat`, change: data.kpis.brentChange, color: colors.dark, icon: '🛢️' }
  ];

  const kpiBoxWidth = (contentWidth - 6) / 2;
  const kpiBoxHeight = 18;
  
  kpis.forEach((kpi, idx) => {
    const col = idx % 2;
    const row = Math.floor(idx / 2);
    const x = margin + (col * (kpiBoxWidth + 3));
    const y = yPos + (row * (kpiBoxHeight + 3));

    // Box background with subtle gradient effect
    pdf.setFillColor(248, 250, 252);
    pdf.rect(x, y, kpiBoxWidth, kpiBoxHeight, 'F');
    
    // Colored left border
    pdf.setFillColor(...kpi.color);
    pdf.rect(x, y, 3, kpiBoxHeight, 'F');
    
    // Border
    pdf.setDrawColor(...colors.lightGray);
    pdf.setLineWidth(0.3);
    pdf.rect(x, y, kpiBoxWidth, kpiBoxHeight);

    // Icon and label
    pdf.setFontSize(9);
    pdf.setTextColor(...colors.gray);
    pdf.text(`${kpi.icon} ${kpi.label}`, x + 5, y + 5);

    // Value
    pdf.setFontSize(13);
    pdf.setTextColor(...kpi.color);
    pdf.setFont('helvetica', 'bold');
    pdf.text(kpi.value, x + 5, y + 12);

    // Change indicator
    if (kpi.change !== null && kpi.change !== undefined) {
      const changeText = `${kpi.change > 0 ? '▲' : '▼'} ${Math.abs(kpi.change).toFixed(1)}%`;
      const changeColor = kpi.change > 0 ? colors.danger : colors.success;
      pdf.setFontSize(9);
      pdf.setTextColor(...changeColor);
      pdf.text(changeText, x + kpiBoxWidth - 3, y + 12, { align: 'right' });
    }
    pdf.setFont('helvetica', 'normal');
    pdf.setTextColor(0, 0, 0);
  });

  yPos += (Math.ceil(kpis.length / 2) * (kpiBoxHeight + 3)) + 8;

  // PRICE CHARTS SECTION
  checkPageBreak(60);
  pdf.setFillColor(...colors.primary);
  pdf.rect(margin, yPos, contentWidth, 8, 'F');
  pdf.setTextColor(255, 255, 255);
  pdf.setFontSize(11);
  pdf.setFont('helvetica', 'bold');
  pdf.text('📈 PRIJSONTWIKKELING (30 DAGEN)', margin + 2, yPos + 5.5);
  pdf.setFont('helvetica', 'normal');
  pdf.setTextColor(0, 0, 0);
  yPos += 10;

  const chartHeight = 45;
  const chartWidth = (contentWidth - 4) / 2;

  drawMiniChart(pdf, data.chartData.ttf, margin, yPos, chartWidth, chartHeight, 'TTF Gas (€/MWh)', colors.primary);
  drawMiniChart(pdf, data.chartData.belpex, margin + chartWidth + 4, yPos, chartWidth, chartHeight, 'Belpex (€/MWh)', colors.secondary);

  yPos += chartHeight + 10;

  // PAGE 2: TABLE & ANALYSIS
  checkPageBreak(80);
  
  // TABLE SECTION HEADER
  pdf.setFillColor(...colors.primary);
  pdf.rect(margin, yPos, contentWidth, 8, 'F');
  pdf.setTextColor(255, 255, 255);
  pdf.setFontSize(11);
  pdf.setFont('helvetica', 'bold');
  pdf.text('📋 HISTORISCHE PRIJZEN (LAATSTE 15 DAGEN)', margin + 2, yPos + 5.5);
  pdf.setFont('helvetica', 'normal');
  pdf.setTextColor(0, 0, 0);
  yPos += 10;

  const tableData = data.priceTable.slice(-15);
  const colWidths = [22, 28, 28, 28, 34];
  const rowHeight = 7;

  // Table header with colored background
  pdf.setFillColor(...colors.dark);
  pdf.rect(margin, yPos, contentWidth, rowHeight, 'F');
  pdf.setFontSize(9);
  pdf.setFont('helvetica', 'bold');
  pdf.setTextColor(255, 255, 255);
  
  const headers = ['Datum', 'TTF', 'Belpex', 'Δ TTF', 'Status'];
  let xPos = margin + 2;
  headers.forEach((header, idx) => {
    pdf.text(header, xPos, yPos + 4.5);
    xPos += colWidths[idx];
  });
  pdf.setFont('helvetica', 'normal');
  pdf.setTextColor(0, 0, 0);
  yPos += rowHeight;

  tableData.forEach((row, idx) => {
    if (idx % 2 === 0) {
      pdf.setFillColor(250, 250, 250);
      pdf.rect(margin, yPos, contentWidth, rowHeight, 'F');
    }

    pdf.setFontSize(8);
    xPos = margin + 1;
    
    pdf.text(row.date + (row.confirmed ? ' ✓' : ''), xPos, yPos + 4);
    xPos += colWidths[0];
    
    pdf.text(`€${row.ttf.toFixed(2)}`, xPos, yPos + 4);
    xPos += colWidths[1];
    
    pdf.text(`€${row.belpex.toFixed(1)}`, xPos, yPos + 4);
    xPos += colWidths[2];
    
    if (row.ttfChange !== null) {
      const changeColor = row.ttfChange > 0 ? [220, 38, 38] : [34, 197, 94];
      pdf.setTextColor(...changeColor);
      pdf.text(`${row.ttfChange > 0 ? '▲' : '▼'}${Math.abs(row.ttfChange).toFixed(1)}%`, xPos, yPos + 4);
      pdf.setTextColor(0, 0, 0);
    }
    xPos += colWidths[3];
    
    if (row.status) {
      pdf.setFontSize(7);
      pdf.text(row.status, xPos, yPos + 4);
      pdf.setFontSize(8);
    }

    yPos += rowHeight;
  });

  yPos += 4;

  // GEOPOLITICAL CONTEXT SECTION
  checkPageBreak(35);
  pdf.setFillColor(...colors.warning);
  pdf.rect(margin, yPos, contentWidth, 8, 'F');
  pdf.setTextColor(255, 255, 255);
  pdf.setFontSize(11);
  pdf.setFont('helvetica', 'bold');
  pdf.text('🌍 GEOPOLITIEKE CONTEXT', margin + 2, yPos + 5.5);
  pdf.setFont('helvetica', 'normal');
  pdf.setTextColor(0, 0, 0);
  yPos += 10;

  // Context box
  pdf.setFillColor(255, 251, 235);
  pdf.rect(margin, yPos, contentWidth, 30, 'F');
  pdf.setDrawColor(...colors.warning);
  pdf.setLineWidth(0.5);
  pdf.rect(margin, yPos, contentWidth, 30);

  pdf.setFontSize(9);
  pdf.setTextColor(60, 60, 60);
  const contextLines = pdf.splitTextToSize(data.geopoliticalContext, contentWidth - 4);
  let contextY = yPos + 4;
  contextLines.forEach(line => {
    pdf.text(line, margin + 2, contextY);
    contextY += 4;
  });
  pdf.setTextColor(0, 0, 0);
  yPos += 34;

  // ADVICE SECTION
  checkPageBreak(30);
  pdf.setFillColor(...colors.success);
  pdf.rect(margin, yPos, contentWidth, 8, 'F');
  pdf.setTextColor(255, 255, 255);
  pdf.setFontSize(11);
  pdf.setFont('helvetica', 'bold');
  pdf.text('💡 ADVIES', margin + 2, yPos + 5.5);
  pdf.setFont('helvetica', 'normal');
  pdf.setTextColor(0, 0, 0);
  yPos += 10;

  // Advice box
  pdf.setFillColor(240, 253, 244);
  pdf.rect(margin, yPos, contentWidth, 28, 'F');
  pdf.setDrawColor(...colors.success);
  pdf.setLineWidth(0.5);
  pdf.rect(margin, yPos, contentWidth, 28);

  // Recommendation
  pdf.setFontSize(10);
  pdf.setFont('helvetica', 'bold');
  pdf.setTextColor(...colors.success);
  pdf.text(data.advice.recommendation, margin + 2, yPos + 5);
  pdf.setFont('helvetica', 'normal');
  yPos += 8;

  // Rationale
  pdf.setFontSize(9);
  pdf.setTextColor(60, 60, 60);
  const adviceLines = pdf.splitTextToSize(data.advice.rationale, contentWidth - 4);
  let adviceY = yPos;
  adviceLines.forEach(line => {
    pdf.text(line, margin + 2, adviceY);
    adviceY += 4;
  });
  pdf.setTextColor(0, 0, 0);
  yPos += 22;

  // Footer
  const footerY = pageHeight - 10;
  pdf.setFontSize(7);
  pdf.setTextColor(120, 120, 120);
  pdf.text(`Gegenereerd: ${new Date().toLocaleString('nl-NL')} | PWR.IT CommV`, pageWidth / 2, footerY, { align: 'center' });

  return pdf;
};

const drawMiniChart = (pdf, data, x, y, width, height, title, color) => {
  // Chart background
  pdf.setFillColor(248, 250, 252);
  pdf.rect(x, y, width, height, 'F');
  
  // Border
  pdf.setDrawColor(...color);
  pdf.setLineWidth(0.5);
  pdf.rect(x, y, width, height);

  // Title
  pdf.setFontSize(9);
  pdf.setFont('helvetica', 'bold');
  pdf.setTextColor(...color);
  pdf.text(title, x + width / 2, y - 3, { align: 'center' });
  pdf.setFont('helvetica', 'normal');

  const values = data.map(d => d.value);
  const minVal = Math.min(...values);
  const maxVal = Math.max(...values);
  const range = maxVal - minVal || 1;

  // Grid lines
  pdf.setDrawColor(220, 220, 220);
  pdf.setLineWidth(0.2);
  for (let i = 1; i <= 3; i++) {
    const gridY = y + (height / 4) * i;
    pdf.line(x, gridY, x + width, gridY);
  }

  // Draw line with thicker stroke
  pdf.setDrawColor(...color);
  pdf.setLineWidth(1.2);

  const points = data.map((d, i) => ({
    x: x + (i / (data.length - 1)) * width,
    y: y + height - ((d.value - minVal) / range) * height
  }));

  points.forEach((point, i) => {
    if (i > 0) {
      pdf.line(points[i - 1].x, points[i - 1].y, point.x, point.y);
    }
  });

  // Draw points
  pdf.setFillColor(...color);
  points.forEach((point, i) => {
    if (i === 0 || i === points.length - 1) {
      pdf.circle(point.x, point.y, 1, 'F');
    }
  });

  // Y-axis labels with background
  pdf.setFontSize(7);
  pdf.setTextColor(100, 100, 100);
  
  // Max value
  pdf.setFillColor(255, 255, 255);
  pdf.rect(x - 14, y - 2, 12, 4, 'F');
  pdf.text(`€${maxVal.toFixed(0)}`, x - 2, y + 1, { align: 'right' });
  
  // Min value
  pdf.setFillColor(255, 255, 255);
  pdf.rect(x - 14, y + height - 2, 12, 4, 'F');
  pdf.text(`€${minVal.toFixed(0)}`, x - 2, y + height + 1, { align: 'right' });
  
  pdf.setTextColor(0, 0, 0);
};
