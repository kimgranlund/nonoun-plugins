// Explicit user-requested navigation after rendering. Requires ui-runtime.js.
// Use onAction with data-action; pass an exact ID, not a CSS selector.
// Destination must be a native control or meaningful heading with tabindex=-1.
function focusUITask(root, targetId) {
  const target = findUIElementById(root, targetId);
  if (!target || target.matches(':disabled,[hidden]') || !target.getClientRects().length)
    return {status:'unavailable'};
  target.focus({preventScroll:true});
  if (root.ownerDocument.activeElement !== target) return {status:'not-focusable'};
  target.scrollIntoView({block:'start',inline:'nearest',behavior:'instant'});
  return {status:'focused',id:targetId};
}
// In definition.bind({root,onAction}):
// onAction('edit-entry', () => focusUITask(root, 'entry-note'));
// Never call automatically on page load or unrelated state changes.
