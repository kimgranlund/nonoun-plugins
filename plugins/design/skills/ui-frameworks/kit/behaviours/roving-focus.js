// @ts-check
/**
 * rovingFocus: makes a set of items one stop in the Tab order, and moves focus among them with the arrow keys.
 * A behaviour: it imports nothing, takes a root and options, and returns its cleanup (D12).
 *
 * Rules: docs/specs/foundation.md, B6 to B10.
 *
 * - One item that can take focus has `tabindex="0"`: the stop. The others have `tabindex="-1"`. An item that
 *   `skip` names has no tabindex at all, so a click does not focus it. `tabindex` on the items is the only
 *   attribute this behaviour writes.
 * - While focus is inside the root, the stop is the item that has focus. While it is outside, the stop is
 *   the item `current()` names, such as the selected tab; failing that the last stop, or the first item.
 * - The arrow keys of the orientation move focus to the next or the previous item and wrap at the ends.
 *   In a horizontal root they follow the writing direction. Home and End go to the first and the last item.
 * - A key pressed inside a child of an item, or with a modifier key held, is left alone.
 * - The DOM is the source. The items are read again at every event, and an observer brings the stop up to
 *   date when items come or go, or when one of the watched attributes changes.
 *
 * @param {HTMLElement} root
 * @param {{
 *   items: () => HTMLElement[],
 *   orientation?: () => 'horizontal' | 'vertical' | 'both',
 *   current?: () => HTMLElement | null | undefined,
 *   skip?: (item: HTMLElement) => boolean,
 *   wrap?: boolean,
 *   watch?: string[],
 * }} options  `items` returns the items in the order the keys walk them. `watch` lists attributes, beyond
 *   role, disabled, aria-disabled and hidden, whose change can alter what `current` or `skip` answer.
 * @returns {() => void}
 */
export function rovingFocus(root, options) {
  const off = new AbortController();
  const listen = { signal: off.signal };
  /** @param {HTMLElement[]} all */
  const usable = (all) => all.filter((item) => !options.skip?.(item));

  /** Brings every item's tabindex up to date. @param {boolean} [leaving] Focus is on its way out of the root. */
  const sync = (leaving = false) => {
    const all = options.items();
    const can = usable(all);
    const active = root.ownerDocument.activeElement;
    const candidates = [
      !leaving && active && root.contains(active) ? active : null,
      options.current?.(),
      all.find((item) => item.getAttribute('tabindex') === '0'),
      can[0],
    ];
    const stop = candidates.find((item) => item && can.includes(/** @type {HTMLElement} */ (item)));
    for (const item of all) {
      const want = !can.includes(item) ? null : item === stop ? '0' : '-1';
      // Written only when it differs: an observer on the same tree then sees nothing when nothing changes.
      if (item.getAttribute('tabindex') === want) continue;
      if (want === null) item.removeAttribute('tabindex');
      else item.setAttribute('tabindex', want);
    }
  };

  root.addEventListener('keydown', (event) => {
    // B8: a key the component has already acted on, and said so by preventing its default, is not acted on twice.
    if (event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
    const can = usable(options.items());
    const at = can.indexOf(/** @type {HTMLElement} */ (event.target));
    if (at < 0) return;
    const orientation = options.orientation?.() ?? 'horizontal';
    const inline = orientation === 'vertical' ? 0 : getComputedStyle(root).direction === 'rtl' ? -1 : 1;
    const block = orientation === 'horizontal' ? 0 : 1;
    const step = { ArrowRight: inline, ArrowLeft: -inline, ArrowDown: block, ArrowUp: -block }[event.key];
    const last = can.length - 1;
    let to;
    if (step) to = options.wrap === false ? Math.min(last, Math.max(0, at + step)) : (at + step + can.length) % can.length;
    else if (event.key === 'Home') to = 0;
    else if (event.key === 'End') to = last;
    else return;
    event.preventDefault();
    can[to].focus();
  }, listen);

  root.addEventListener('focusin', () => sync(), listen);
  root.addEventListener('focusout', (event) => {
    if (!(event.relatedTarget instanceof Node && root.contains(event.relatedTarget))) sync(true);
  }, listen);

  const observer = new MutationObserver(() => sync());
  observer.observe(root, { childList: true, subtree: true, attributes: true, attributeFilter: ['role', 'disabled', 'aria-disabled', 'hidden', ...(options.watch ?? [])] });
  sync();

  return () => { off.abort(); observer.disconnect(); };
}
