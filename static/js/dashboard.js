/**
 * dashboard.js — Minor dashboard enhancements
 * (Animates stat numbers, progress bar entrance)
 */
document.addEventListener('DOMContentLoaded', () => {

  /* Animate numeric stat values counting up */
  document.querySelectorAll('.stat-value').forEach(el => {
    const raw   = el.textContent.trim();
    const num   = parseFloat(raw.replace('%', ''));
    const hasPct = raw.includes('%');
    if (isNaN(num) || num === 0) return;

    let start = null;
    const duration = 800;

    function step(ts) {
      if (!start) start = ts;
      const progress = Math.min((ts - start) / duration, 1);
      const eased    = 1 - Math.pow(1 - progress, 3);   // ease-out cubic
      const current  = Math.round(eased * num * 10) / 10;
      el.textContent = hasPct ? current + '%' : current;
      if (progress < 1) requestAnimationFrame(step);
      else el.textContent = raw;  // restore exact original
    }

    el.textContent = hasPct ? '0%' : '0';
    requestAnimationFrame(step);
  });

  /* Animate progress bar entrance */
  const fill = document.querySelector('.progress-fill');
  if (fill) {
    const target = fill.style.width;
    fill.style.width = '0%';
    setTimeout(() => { fill.style.width = target; }, 200);
  }

});
