// @ts-check
/**
 * dismiss: tells a component when the user wants an open layer, such as a menu, closed.
 * A behaviour: it imports nothing, takes a root and options, and returns its cleanup (D12).
 *
 * Rules: docs/specs/foundation.md, B11 to B13.
 *
 * It calls `onDismiss(reason)` and closes nothing itself. The reasons:
 * - "escape": Escape was pressed inside the root. The event goes no further, so a layer around this one
 *   stays open (ui-interaction-dev, overlay.escape-innermost).
 * - "outside": a pointer went down outside the root.
 * - "focus": focus moved from the root to somewhere outside it, as Tab does.
 *
 * An element in `ignore`, such as the button that opened a menu, is not outside for the pointer: a press on
 * it reaches the component as a click, which can then close the layer itself. Focus that moves to it without
 * a press does count as leaving. The behaviour writes no attribute.
 *
 * @param {HTMLElement} root
 * @param {{
 *   onDismiss: (reason: 'escape' | 'outside' | 'focus', event: Event) => void,
 *   active?: () => boolean,
 *   ignore?: () => (Element | null | undefined)[],
 * }} options  `active` says whether the layer is open; it is read at each event.
 * @returns {() => void}
 */
export function dismiss(root, options) {
  const off = new AbortController();
  const listen = { signal: off.signal };
  const active = () => options.active?.() ?? true;
  /** @param {EventTarget | null} node */
  const ignored = (node) => node instanceof Node && (options.ignore?.() ?? []).some((el) => el?.contains(node));
  /** A pointer is down on an ignored element, so the focus it moves is not focus leaving. */
  let pressing = false;

  root.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape' || !active()) return;
    event.preventDefault();
    event.stopPropagation();
    options.onDismiss('escape', event);
  }, listen);

  root.ownerDocument.addEventListener('pointerdown', (event) => {
    if (!active() || (event.target instanceof Node && root.contains(event.target))) return;
    if (ignored(event.target)) { pressing = true; setTimeout(() => { pressing = false; }); return; }
    options.onDismiss('outside', event);
  }, { ...listen, capture: true });

  root.addEventListener('focusout', (event) => {
    const to = event.relatedTarget;
    if (!active() || !(to instanceof Node) || root.contains(to) || (pressing && ignored(to))) return;
    options.onDismiss('focus', event);
  }, listen);

  return () => off.abort();
}
