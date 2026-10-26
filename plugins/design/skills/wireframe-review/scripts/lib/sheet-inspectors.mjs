// Presentation only. Callers select authoritative source and supply escaped/trusted body HTML.
const escape = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export function renderInspector(title, bodyHtml) {
  if (typeof title !== 'string' || !title.trim()) throw new TypeError('Inspector title is required');
  if (typeof bodyHtml !== 'string') throw new TypeError('Inspector body must be trusted HTML');
  return `<details data-inspector="${escape(title.toLowerCase())}"><summary>${escape(title)}</summary>${bodyHtml}</details>`;
}
