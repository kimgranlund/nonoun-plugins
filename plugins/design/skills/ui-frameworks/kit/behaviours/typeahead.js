// @ts-check
/**
 * typeahead: finds the item whose text starts with what the user types.
 * A behaviour: it imports nothing, takes a root and options, and returns its cleanup (D12).
 *
 * Rules: docs/specs/foundation.md, B14 and B15.
 *
 * - A printable key pressed inside the root adds to a search text, which is forgotten after a pause.
 * - One letter typed again steps through the items that start with it. Several different letters look
 *   for the item that starts with all of them, beginning at the item that has focus.
 * - It calls `onMatch(item)` and moves nothing itself: a menu focuses the item, a listbox would highlight it.
 * - Space is left alone, because it activates an item. So is a key pressed with Control, Alt or Meta.
 * It writes no attribute.
 *
 * @param {HTMLElement} root
 * @param {{
 *   items: () => HTMLElement[],
 *   onMatch: (item: HTMLElement) => void,
 *   text?: (item: HTMLElement) => string,
 *   current?: () => HTMLElement | null | undefined,
 *   skip?: (item: HTMLElement) => boolean,
 *   pause?: number,
 * }} options  `pause` is how long the search text is kept, in milliseconds. The default is 500. `current` is the
 *   item the search starts from; the default is the element that has focus, which suits items that take focus.
 *   A list that keeps focus on itself passes its highlighted item.
 * @returns {() => void}
 */
export function typeahead(root, options) {
  const off = new AbortController();
  let typed = '';
  /** @type {ReturnType<typeof setTimeout> | undefined} */
  let timer;

  root.addEventListener('keydown', (event) => {
    if (event.ctrlKey || event.altKey || event.metaKey || event.key.length !== 1 || event.key === ' ') return;
    typed += event.key.toLowerCase();
    clearTimeout(timer);
    timer = setTimeout(() => { typed = ''; }, options.pause ?? 500);
    const items = options.items().filter((item) => !options.skip?.(item));
    const text = (/** @type {HTMLElement} */ item) => (options.text?.(item) ?? item.textContent ?? '').trim().toLowerCase();
    const repeated = [...typed].every((letter) => letter === typed[0]);
    // A repeated letter moves on from the current item; a longer text may still match the current one.
    const current = options.current ? options.current() : root.ownerDocument.activeElement;
    const from = Math.max(0, items.indexOf(/** @type {HTMLElement} */ (current)) + (repeated ? 1 : 0));
    const match = [...items.slice(from), ...items.slice(0, from)].find((item) => text(item).startsWith(repeated ? typed[0] : typed));
    if (!match) return;
    event.preventDefault();
    options.onMatch(match);
  }, { signal: off.signal });

  return () => { off.abort(); clearTimeout(timer); };
}
