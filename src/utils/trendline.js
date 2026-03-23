/**
 * Compute linear regression over a data array.
 * @param {Array} data - Array of objects
 * @param {string} valueKey - Key to read numeric values from
 * @param {number} [lastN] - Use only last N points (undefined = all)
 * @returns {{ slope: number, intercept: number, startIdx: number, count: number }}
 */
export function linearRegression(data, valueKey, lastN) {
  if (!data || data.length < 2) return null;

  const startIdx = lastN ? Math.max(0, data.length - lastN) : 0;
  const subset = data.slice(startIdx);
  const n = subset.length;
  if (n < 2) return null;

  let sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0;
  for (let i = 0; i < n; i++) {
    const y = subset[i][valueKey];
    if (y == null) continue;
    sumX += i;
    sumY += y;
    sumXY += i * y;
    sumX2 += i * i;
  }

  const denom = n * sumX2 - sumX * sumX;
  if (denom === 0) return null;

  const slope = (n * sumXY - sumX * sumY) / denom;
  const intercept = (sumY - slope * sumX) / n;

  return { slope, intercept, startIdx, count: n };
}

/**
 * Merge trendline values into a data array as new keys.
 * @param {Array} data - Original data array
 * @param {Object} regressions - Map of { outputKey: { valueKey, lastN } }
 * @returns {Array} New array with trendline keys added
 */
export function addTrendlines(data, regressions) {
  const regs = {};
  for (const [outKey, { valueKey, lastN }] of Object.entries(regressions)) {
    regs[outKey] = linearRegression(data, valueKey, lastN);
  }

  return data.map((d, i) => {
    const row = { ...d };
    for (const [outKey, reg] of Object.entries(regs)) {
      if (!reg) continue;
      const localI = i - reg.startIdx;
      if (localI >= 0 && localI < reg.count) {
        row[outKey] = +(reg.intercept + reg.slope * localI).toFixed(2);
      }
    }
    return row;
  });
}
