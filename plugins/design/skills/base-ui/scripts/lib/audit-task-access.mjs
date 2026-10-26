// Serializable, read-only browser measurement. This checks a declared task-access
// budget, not aesthetic density; the reviewer owns the task choice and rationale.
export function auditTaskAccess({ taskSelector, maxScreens, rationale, requireFocus = false } = {}) {
  const mode = requireFocus ? 'arrival' : 'initial';
  const result = { status: 'unreviewed', scope: 'Declared task access only; visual density requires review.', mode,
    taskSelector: taskSelector || null, maxScreens: maxScreens ?? null, rationale: rationale || '', issues: [] };
  const add = (code, message) => result.issues.push({ code, message });
  if (!taskSelector || !Number.isFinite(maxScreens) || maxScreens < 0 || typeof rationale !== 'string' || !rationale.trim()) {
    add('TASK_ACCESS_UNDECLARED', 'Declare a task selector, nonnegative target-start distance budget (in viewport heights), and task-specific rationale.');
    return result;
  }
  let matches;
  try { matches = document.querySelectorAll(taskSelector); } catch { add('TASK_SELECTOR_INVALID', 'The task selector is invalid.'); return result; }
  if (matches.length !== 1) { add('TASK_TARGET_AMBIGUOUS', `Expected one task target, found ${matches.length}.`); return result; }
  const target = matches[0], rect = target.getBoundingClientRect();
  const width = window.innerWidth, height = window.innerHeight;
  const epsilon = 1; // CSS pixel tolerance for fractional scroll-position rounding.
  const hidden = e => { for (let n=e;n;n=n.parentElement) { const s=getComputedStyle(n); if (s.display==='none'||s.visibility==='hidden'||s.visibility==='collapse'||Number(s.opacity)===0||n.inert) return true; } return !e.getClientRects().length; };
  result.viewport = { width, height, scrollX: window.scrollX, scrollY: window.scrollY };
  result.target = { left: rect.left, top: rect.top, right: rect.right, bottom: rect.bottom, width: rect.width, height: rect.height,
    documentTop: rect.top + window.scrollY, focused: target === document.activeElement || target.contains(document.activeElement) };
  if (hidden(target) || rect.width <= 0 || rect.height <= 0 || target.matches(':disabled')) {
    result.status='fail'; add('TASK_UNAVAILABLE', 'The declared task is hidden, inert, disabled, or has no rendered area.'); return result;
  }
  if (rect.height > height || rect.width > width) {
    add('TASK_TARGET_TOO_LARGE', 'Choose the actual task control or entry point, not a container larger than the viewport.'); return result;
  }
  const scrollDistance = Math.max(0, rect.bottom-height, -rect.top);
  result.access = { verticalScrollPixels: scrollDistance, verticalScrollScreens: scrollDistance/height,
    targetTopScreens: rect.top/height, fullyInViewport: rect.top>=-epsilon && rect.bottom<=height+epsilon && rect.left>=-epsilon && rect.right<=width+epsilon,
    clippingAncestors: [] };
  for (let n=target.parentElement;n && n!==document.body && n!==document.documentElement;n=n.parentElement) {
    const s=getComputedStyle(n), r=n.getBoundingClientRect();
    if ((/(auto|scroll|hidden|clip)/.test(s.overflowY) && (rect.top<r.top+n.clientTop-epsilon || rect.bottom>r.top+n.clientTop+n.clientHeight+epsilon)) ||
        (/(auto|scroll|hidden|clip)/.test(s.overflowX) && (rect.left<r.left+n.clientLeft-epsilon || rect.right>r.left+n.clientLeft+n.clientWidth+epsilon))) {
      result.access.clippingAncestors.push({ element:n.id ? '#'+n.id : n.localName, overflowX:s.overflowX, overflowY:s.overflowY });
    }
  }
  // Count rendered words and controls in the first/current viewport, and before
  // the task in reading order. Counts describe density; they are not pass rules.
  const counts={ viewportWords:0, precedingWords:0, viewportControls:0, precedingControls:0 };
  const before = e => Boolean(e.compareDocumentPosition(target) & Node.DOCUMENT_POSITION_FOLLOWING) && !e.contains(target);
  const intersects = (r, e) => {
    let left=Math.max(0,r.left), top=Math.max(0,r.top), right=Math.min(width,r.right), bottom=Math.min(height,r.bottom);
    for(let n=e.parentElement;n && n!==document.body && n!==document.documentElement;n=n.parentElement) {
      const s=getComputedStyle(n), b=n.getBoundingClientRect();
      if (/(auto|scroll|hidden|clip)/.test(s.overflowY)) { top=Math.max(top,b.top+n.clientTop); bottom=Math.min(bottom,b.top+n.clientTop+n.clientHeight); }
      if (/(auto|scroll|hidden|clip)/.test(s.overflowX)) { left=Math.max(left,b.left+n.clientLeft); right=Math.min(right,b.left+n.clientLeft+n.clientWidth); }
    }
    return bottom>top && right>left;
  };
  const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT); let text;
  while ((text=walker.nextNode())) {
    if (!text.textContent.trim() || ['SCRIPT','STYLE','NOSCRIPT','OPTION'].includes(text.parentElement?.tagName) || hidden(text.parentElement)) continue;
    const words=text.textContent.trim().split(/\s+/).length, range=document.createRange(); range.selectNodeContents(text);
    if ([...range.getClientRects()].some(r=>intersects(r,text.parentElement))) counts.viewportWords+=words;
    if (before(text.parentElement)) counts.precedingWords+=words;
  }
  for (const e of document.querySelectorAll('button,input:not([type=hidden]),select,textarea,a[href],summary,[role=button]')) {
    if (hidden(e)) continue;
    if (intersects(e.getBoundingClientRect(),e)) counts.viewportControls++;
    if (before(e)) counts.precedingControls++;
  }
  result.content=counts;
  result.measurements = { ...result.access, ...counts };
  result.limitations = ['Task choice and budget justification require human review.', 'Counts are descriptive, not aesthetic density verdicts.', 'Occlusion uses the target center only.'];
  if (Math.max(0, rect.top)/height > maxScreens + 1e-6) add('TASK_SCROLL_BUDGET', 'The declared task exceeds its justified target-start distance budget.');
  if (rect.left < -epsilon || rect.right > width+epsilon) add('TASK_HORIZONTAL_CLIPPING', 'The task requires horizontal scrolling or is clipped by the viewport.');
  if (result.access.clippingAncestors.length) add('TASK_CONTAINER_CLIPPING', 'An ancestor clips the target; document scroll distance alone cannot establish access.');
  if (mode==='arrival') {
    if (!result.target.focused) add('TASK_FOCUS_MISSING', 'The jump must move keyboard focus into the declared task.');
    if (!result.access.fullyInViewport) add('TASK_ARRIVAL_OFFSCREEN', 'The task is not fully visible after the jump.');
  }
  if (result.access.fullyInViewport) {
    const hit=document.elementFromPoint((rect.left+rect.right)/2,(rect.top+rect.bottom)/2);
    result.access.centerHit = hit===target || target.contains(hit);
    if (!result.access.centerHit) add('TASK_OCCLUDED', 'Another element covers the task center. Inspect sticky headers, overlays and stacking.');
  }
  result.status=result.issues.length ? 'fail' : 'pass';
  return result;
}
