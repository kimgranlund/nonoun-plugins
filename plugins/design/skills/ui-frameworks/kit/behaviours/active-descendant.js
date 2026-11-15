// @ts-check
/** For the ids this behaviour gives to items that have none. */
let serial = 0;

/**
 * activeDescendant: keeps focus where it is and marks one item as highlighted, for a list that is driven from
 * the element that has focus: a listbox from itself, a combobox from its text field.
 * A behaviour: it imports nothing, takes a root and options, and returns its cleanup (D12).
 *
 * Rules: docs/specs/foundation.md, B16 to B18. The decision behind it is D90.
 *
 * - At most one item is highlighted. It carries `data-highlighted`, and the focus element names its id in
 *   `aria-activedescendant`; with no item highlighted that attribute is absent. An item that has no id is given
 *   one, made from the root's tag and a counter. These three are the only attributes this behaviour writes, and
 *   each is written only when it differs.
 * - ArrowDown, ArrowUp, Home and End, pressed on the focus element with no modifier key, move the highlight
 *   among the items that are not skipped, and their default action is prevented. With nothing highlighted,
 *   ArrowDown goes to the first item and ArrowUp to the last. The arrows wrap at the ends only with `wrap`.
 * - The component moves the highlight by writing `data-highlighted` on an item: the behaviour then clears the
 *   others and names that item. Removing the attribute from the highlighted item clears the highlight.
 * - When the highlighted item is removed or becomes skipped, the item `fallback()` names is highlighted, or
 *   else the highlight is cleared.
 * - A highlight that moves while the focus element has focus is scrolled into view, nearest edge.
 * - The DOM is the source. The items are read again at every event, and an observer brings the attributes up
 *   to date when items come or go, or change an attribute that can alter `skip`.
 *
 * @param {HTMLElement} root  The element that holds the items.
 * @param {{
 *   items: () => HTMLElement[],
 *   skip?: (item: HTMLElement) => boolean,
 *   wrap?: boolean,
 *   focus?: () => HTMLElement,
 *   fallback?: () => HTMLElement | null | undefined,
 *   active?: () => boolean,
 * }} options  `items` returns the items in the order the keys walk them. `focus` returns the element that has
 *   focus and receives the keys; the default is the root. `active` says whether the keys are handled now; the
 *   default is yes.
 * @returns {() => void}
 */
export function activeDescendant(root, options) {
  const off = new AbortController();
  const listen = { signal: off.signal };
  const MARK = 'data-highlighted';
  const focusElement = () => options.focus?.() ?? root;
  /** @param {HTMLElement[]} all */
  const usable = (all) => all.filter((item) => !options.skip?.(item));
  /** @type {HTMLElement | null} The item this behaviour last highlighted. */
  let current = null;

  /** Sets or removes an attribute, only when it differs. @param {Element} el @param {string} name @param {string | null} value */
  const put = (el, name, value) => {
    if (el.getAttribute(name) === value) return;
    if (value === null) el.removeAttribute(name);
    else el.setAttribute(name, value);
  };

  /** Makes `item` the one highlighted item, or clears the highlight. @param {HTMLElement | null} item */
  const highlight = (item) => {
    const moved = item !== current;
    current = item;
    for (const other of options.items()) if (other !== item) put(other, MARK, null);
    if (item) {
      if (!item.id) item.id = `${root.localName}-${++serial}`;
      put(item, MARK, '');
    }
    const target = focusElement();
    put(target, 'aria-activedescendant', item ? item.id : null);
    if (item && moved && root.ownerDocument.activeElement === target) item.scrollIntoView({ block: 'nearest' });
  };

  /** Reads the marks the component wrote, and the items that came, went or changed, and settles the highlight. */
  const sync = () => {
    const all = options.items();
    const can = usable(all);
    const marked = all.filter((item) => item.hasAttribute(MARK));
    // A mark on an item other than the highlighted one is the component's order to highlight it (B18).
    const ordered = marked.filter((item) => item !== current && can.includes(item)).pop();
    /** @type {HTMLElement | null} */
    let next = null;
    if (ordered) next = ordered;
    else if (current && can.includes(current)) next = marked.includes(current) ? current : null;
    else if (current) {
      // The highlighted item was removed or is now skipped.
      const fallback = options.fallback?.();
      next = fallback && can.includes(fallback) ? fallback : null;
    }
    highlight(next);
  };

  /** @param {KeyboardEvent} event */
  const onKey = (event) => {
    if (event.target !== focusElement() || !(options.active?.() ?? true)) return;
    if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
    if (!['ArrowDown', 'ArrowUp', 'Home', 'End'].includes(event.key)) return;
    // A mark a listener wrote as this key went down is taken first, so the keys move on from it. Chromium and
    // WebKit have delivered the observer's records by now; Firefox delivers them only after the last listener.
    observer.takeRecords();
    sync();
    const can = usable(options.items());
    if (!can.length) return;
    const at = current ? can.indexOf(current) : -1;
    const last = can.length - 1;
    let to;
    if (event.key === 'Home') to = 0;
    else if (event.key === 'End') to = last;
    else if (at < 0) to = event.key === 'ArrowDown' ? 0 : last;
    else {
      const step = event.key === 'ArrowDown' ? 1 : -1;
      to = options.wrap ? (at + step + can.length) % can.length : Math.min(last, Math.max(0, at + step));
    }
    event.preventDefault();
    highlight(can[to]);
  };
  root.addEventListener('keydown', onKey, listen);
  // A focus element outside the root, such as a combobox's text field, sends its keys past the root.
  root.ownerDocument.addEventListener('keydown', (event) => {
    if (!(event.target instanceof Node && root.contains(event.target))) onKey(event);
  }, listen);

  const observer = new MutationObserver(() => sync());
  observer.observe(root, { childList: true, subtree: true, attributes: true, attributeFilter: [MARK, 'id', 'role', 'disabled', 'aria-disabled', 'hidden'] });
  sync();

  return () => { off.abort(); observer.disconnect(); };
}
