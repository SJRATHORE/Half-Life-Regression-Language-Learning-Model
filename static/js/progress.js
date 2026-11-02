/**
 * progress.js — Fetches /api/progress_data and renders Chart.js charts
 */

const GOLD      = '#c9a84c';
const GOLD_DIM  = '#8c7232';
const MUTED     = '#6b7280';
const SURFACE2  = '#1e2029';
const CORRECT   = '#22c55e';
const INCORRECT = '#ef4444';

const chartDefaults = {
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: '#1e2029',
      borderColor: '#2a2d3a',
      borderWidth: 1,
      titleColor: '#e2d9c9',
      bodyColor: '#9ca3af',
    },
  },
  scales: {
    x: {
      ticks: { color: MUTED, maxTicksLimit: 8 },
      grid:  { color: 'rgba(255,255,255,0.05)' },
    },
    y: {
      ticks: { color: MUTED },
      grid:  { color: 'rgba(255,255,255,0.05)' },
    },
  },
};

async function loadCharts() {
  let data;
  try {
    const res = await fetch('/api/progress_data');
    data = await res.json();
  } catch (e) {
    document.getElementById('loading-charts').textContent =
      'Failed to load data. Start a study session first!';
    return;
  }

  document.getElementById('loading-charts').classList.add('hidden');
  document.getElementById('charts-grid').classList.remove('hidden');

  renderRecallChart(data.daily);
  renderHLChart(data.half_lives);
  renderWordsChart(data.cumulative);
  renderCategoryTable(data.per_category);
}

/* ── Recall over time ─────────────────────────────────────────────────── */
function renderRecallChart(daily) {
  if (!daily.length) return;

  new Chart(document.getElementById('recallChart'), {
    type: 'line',
    data: {
      labels:   daily.map(d => d.day),
      datasets: [{
        label: 'Recall %',
        data:  daily.map(d => d.avg_recall),
        borderColor:     GOLD,
        backgroundColor: 'rgba(201,168,76,0.1)',
        borderWidth: 2,
        pointRadius: 4,
        pointBackgroundColor: GOLD,
        tension: 0.3,
        fill: true,
      }],
    },
    options: {
      ...chartDefaults,
      scales: {
        ...chartDefaults.scales,
        y: { ...chartDefaults.scales.y, min: 0, max: 100,
             ticks: { color: MUTED, callback: v => v + '%' } },
      },
    },
  });
}

/* ── Half-life histogram ──────────────────────────────────────────────── */
function renderHLChart(halfLives) {
  if (!halfLives.length) return;

  // Bucket into bins: <1d, 1-3d, 3-7d, 7-14d, 14-30d, 30d+
  const bins   = [0, 1, 3, 7, 14, 30, Infinity];
  const labels = ['<1d', '1-3d', '3-7d', '7-14d', '14-30d', '30d+'];
  const counts = new Array(labels.length).fill(0);

  halfLives.forEach(hl => {
    for (let i = 0; i < bins.length - 1; i++) {
      if (hl >= bins[i] && hl < bins[i + 1]) { counts[i]++; break; }
    }
  });

  const colors = [INCORRECT, '#f97316', GOLD_DIM, GOLD, '#84cc16', CORRECT];

  new Chart(document.getElementById('hlChart'), {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Words',
        data:  counts,
        backgroundColor: colors,
        borderRadius: 5,
      }],
    },
    options: {
      ...chartDefaults,
      scales: {
        x: { ...chartDefaults.scales.x },
        y: { ...chartDefaults.scales.y, ticks: { color: MUTED, stepSize: 1 } },
      },
    },
  });
}

/* ── Cumulative words seen ────────────────────────────────────────────── */
function renderWordsChart(cumulative) {
  if (!cumulative.length) return;

  // Build running total
  let running = 0;
  const cum   = cumulative.map(d => { running += d.new_words; return running; });

  new Chart(document.getElementById('wordsChart'), {
    type: 'line',
    data: {
      labels:   cumulative.map(d => d.day),
      datasets: [{
        label: 'Words',
        data:  cum,
        borderColor:     CORRECT,
        backgroundColor: 'rgba(34,197,94,0.1)',
        borderWidth: 2,
        pointRadius: 3,
        pointBackgroundColor: CORRECT,
        tension: 0.2,
        fill: true,
      }],
    },
    options: chartDefaults,
  });
}

/* ── Category table ───────────────────────────────────────────────────── */
function renderCategoryTable(cats) {
  const maxHL = Math.max(...cats.map(c => c.avg_hl || 0), 1);
  const html  = `
    <table class="cat-breakdown">
      <thead>
        <tr>
          <th>Category</th>
          <th>Total</th>
          <th>Seen</th>
          <th>Avg ĥ (days)</th>
          <th>Retention</th>
        </tr>
      </thead>
      <tbody>
        ${cats.map(c => {
          const pct  = c.total ? Math.round(c.seen / c.total * 100) : 0;
          const bar  = c.avg_hl ? Math.round(c.avg_hl / maxHL * 100) : 0;
          return `
            <tr>
              <td>${c.category}</td>
              <td>${c.total}</td>
              <td>${c.seen}</td>
              <td>
                <div class="hl-bar-bg">
                  <div class="hl-bar-fill" style="width:${bar}%"></div>
                </div>
                <small>${c.avg_hl || '—'}</small>
              </td>
              <td>${pct}%</td>
            </tr>`;
        }).join('')}
      </tbody>
    </table>`;

  document.getElementById('category-table').innerHTML = html;
}

/* ── Boot ─────────────────────────────────────────────────────────────── */
loadCharts();
