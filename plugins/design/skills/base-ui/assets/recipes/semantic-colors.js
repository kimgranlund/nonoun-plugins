/* Maintained page-local simulation; no external operations or persistence. */
(() => {
  const root = document.getElementById('semantic-busy-fixture');
  const button = document.getElementById('semantic-busy-button');
  const status = document.getElementById('semantic-busy-status');
  const field = document.getElementById('semantic-role-field');
  if (!root || !button || !status || !field || !root.contains(button) || !root.contains(status) || root.dataset.bound) return;
  root.dataset.bound = 'true';
  let running = false;
  let jobs = 0;
  status.dataset.state = 'ready';
  status.textContent = 'Ready for local word counting.';
  button.addEventListener('click', () => {
    if (running || button.disabled) return;
    running = true;
    const input = field.value;
    root.dataset.jobCount = String(++jobs);
    button.disabled = true;
    button.setAttribute('aria-busy', 'true');
    status.dataset.state = 'running';
    status.textContent = 'Local word count running.';
    setTimeout(() => {
      const words = input.trim() ? input.trim().split(/\s+/u).length : 0;
      status.dataset.state = 'completed';
      status.textContent = `Local word count completed: ${words} words. Job ${jobs}.`;
      button.removeAttribute('aria-busy');
      running = false;
      button.disabled = false;
    }, 600);
  });
  button.disabled = false;
})();
