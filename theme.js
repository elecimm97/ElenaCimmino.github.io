// Follow the device theme until the visitor chooses a mode. Remember that choice.
(() => {
  const root = document.documentElement;
  const device = window.matchMedia('(prefers-color-scheme: dark)');
  let preference = null;
  try { preference = localStorage.getItem('portfolio-theme'); } catch (_) {}
  if (!['light', 'dark'].includes(preference)) preference = null;
  let button;

  function apply(theme) {
    root.dataset.theme = theme;
    if (button) {
      button.textContent = theme === 'dark' ? 'Light mode' : 'Dark mode';
      button.setAttribute('aria-label', `Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`);
    }
  }

  // This runs in the page head, before the first paint.
  apply(preference || (device.matches ? 'dark' : 'light'));

  document.addEventListener('DOMContentLoaded', () => {
    button = document.getElementById('theme-toggle');
    if (!button) return;
    button.hidden = false;
    apply(root.dataset.theme);
    button.addEventListener('click', () => {
      preference = root.dataset.theme === 'dark' ? 'light' : 'dark';
      apply(preference);
      try { localStorage.setItem('portfolio-theme', preference); } catch (_) {}
    });
  });

  device.addEventListener('change', () => {
    if (!preference) apply(device.matches ? 'dark' : 'light');
  });
})();
