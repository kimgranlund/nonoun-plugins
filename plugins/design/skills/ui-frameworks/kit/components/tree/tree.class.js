// @ts-check
/**
 * tree.class.js: the class of a tree. Importing it defines no element; tree.js does that.
 *
 * The root has the tree role and never takes focus itself: its items do. rovingFocus keeps one item that shows
 * (every item around it, up to the tree, is expanded) in the Tab order and moves focus with ArrowDown, ArrowUp,
 * Home and End, without wrapping; typeahead moves it to the item whose label starts with what is typed. The
 * tree's own keydown adds ArrowRight and ArrowLeft, which open and close an item or move to its first child or
 * its parent (swapped in a right-to-left scope), and Enter and Space, which select. A click on an item's label
 * focuses the item, selects it, and opens or closes it when it has a group.
 *
 * It finds its items by their ARIA role and names no other component, so it works whichever element is defined
 * first, and with items that arrive later. It sets an item's state through the item's own `selected` and
 * `expanded` attributes, and writes `aria-level`, `aria-setsize` and `aria-posinset` on every item.
 *
 * Rules: docs/specs/patterns.md, J32 to J34; docs/specs/foundation.md, G1 to G3.
 */
import { UIElement } from '../../foundation/element.js';
import { rovingFocus } from '../../behaviours/roving-focus.js';
import { typeahead } from '../../behaviours/typeahead.js';
import { props, role, tabindex } from './tree.props.js';

const ITEM = '[role="treeitem"]';
const GROUP = ':scope > [data-part="group"]';
const LABEL = ':scope > [data-part="label"]';

/** @param {Element} el */
const disabled = (el) => el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true';

/**
 * Sets or removes an attribute, only when it differs. The observer then sees nothing when nothing changes.
 * @param {Element} el @param {string} name @param {string | null} value
 */
const put = (el, name, value) => {
  if (el.getAttribute(name) === value) return;
  if (value === null) el.removeAttribute(name);
  else el.setAttribute(name, value);
};

/** An item's label: its child marked as one. @param {Element} item */
const labelOf = (item) => item.querySelector(LABEL);

export class UITree extends UIElement {
  static props = props;
  static role = role;
  static tabindex = tabindex;

  /** @type {HTMLElement | null} The item last selected by the user or a script, which wins over another item of the same value. */
  #picked = null;
  /** Whether the tree has once settled with items, after which a mark is taken only when it is made. */
  #settled = false;

  /** The items of this tree, and not of another tree nested in one, in document order. @returns {HTMLElement[]} */
  #own() {
    return /** @type {HTMLElement[]} */ ([...this.querySelectorAll(ITEM)].filter((el) => el.closest(this.localName) === this));
  }

  /** The item whose group holds this one, or null at the top of the tree. @param {Element} item @returns {HTMLElement | null} */
  #parent(item) {
    const parent = /** @type {HTMLElement | null} */ (item.parentElement?.closest(ITEM) ?? null);
    return parent && parent.closest(this.localName) === this ? parent : null;
  }

  /** Whether an item shows: every item around it, up to the tree, is expanded. @param {Element} item */
  #shows(item) {
    for (let parent = this.#parent(item); parent; parent = this.#parent(parent)) {
      if (!parent.hasAttribute('expanded')) return false;
    }
    return true;
  }

  /** The items that show, in the order the keys walk them. */
  #showing() { return this.#own().filter((item) => this.#shows(item)); }

  /** An item's value: its `value` attribute, or else the trimmed text of its label. @param {Element} item */
  #valueOf(item) { return item.getAttribute('value') ?? (labelOf(item)?.textContent ?? '').trim(); }

  /** The item `value` selects: the one picked last when it still has that value, or else the first that has it. @param {HTMLElement[]} items */
  #target(items) {
    const self = /** @type {any} */ (this);
    if (self.value === '') return null;
    const picked = this.#picked;
    if (picked && items.includes(picked) && this.#valueOf(picked) === self.value) return picked;
    return items.find((item) => this.#valueOf(item) === self.value) ?? null;
  }

  /** Brings the items' `selected` in step with `value`, and writes their level and position. Writes nothing when they already are. */
  #sync() {
    const self = /** @type {any} */ (this);
    const items = this.#own();
    if (!items.length) return;
    if (!this.#settled) {
      this.#settled = true;
      // No value written: take the item the author marked.
      const marked = items.find((item) => item.hasAttribute('selected'));
      if (self.value === '' && marked && this.#valueOf(marked) !== '') {
        this.#picked = marked;
        self.value = this.#valueOf(marked);
        return; // changed() has run this again with the value in place.
      }
    }
    const target = this.#target(items);
    /** @type {Map<HTMLElement | null, HTMLElement[]>} The items of each parent, the top of the tree under null. */
    const siblings = new Map();
    for (const item of items) {
      const parent = this.#parent(item);
      siblings.set(parent, [...(siblings.get(parent) ?? []), item]);
    }
    for (const item of items) {
      let level = 1;
      for (let parent = this.#parent(item); parent; parent = this.#parent(parent)) level++;
      const set = /** @type {HTMLElement[]} */ (siblings.get(this.#parent(item)));
      put(item, 'aria-level', String(level));
      put(item, 'aria-setsize', String(set.length));
      put(item, 'aria-posinset', String(set.indexOf(item) + 1));
      put(item, 'selected', item === target ? '' : null);
    }
  }

  /**
   * Selects an item because the user asked for it, then tells listeners, who find the items already written.
   * @param {HTMLElement} item
   */
  #choose(item) {
    const self = /** @type {any} */ (this);
    if (item === this.#target(this.#own())) return; // a disabled item takes no focus and its click is ignored
    this.#picked = item;
    const value = this.#valueOf(item);
    if (value !== self.value) self.value = value; // changed() writes the items before this returns.
    else this.#sync(); // another item of the same value
    this.dispatchEvent(new Event('change', { bubbles: true }));
  }

  /** Opens or closes an item, through its own attribute. @param {HTMLElement} item @param {boolean} open */
  #expand(item, open) { put(item, 'expanded', open ? '' : null); }

  /** @param {string} name */
  changed(name) {
    if (name === 'value' && this.isConnected) this.#sync();
  }

  connected() {
    const self = /** @type {any} */ (this);
    const usable = (/** @type {HTMLElement} */ item) => !disabled(item);

    this.use(rovingFocus, {
      items: () => this.#showing(),
      orientation: () => 'vertical',
      wrap: false,
      current: () => this.#own().find((item) => item.hasAttribute('selected') && this.#shows(item)),
      skip: disabled,
      watch: ['expanded', 'aria-expanded', 'aria-selected'],
    });
    this.use(typeahead, {
      items: () => this.#showing(),
      skip: disabled,
      text: (/** @type {HTMLElement} */ item) => labelOf(item)?.textContent ?? '',
      onMatch: (/** @type {HTMLElement} */ item) => item.focus(),
    });

    this.listen(this, 'keydown', (/** @type {KeyboardEvent} */ event) => {
      if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
      // Focus is on an item itself. A key that reaches the tree from inside an item's label, or from an item
      // of another tree, is not this tree's: and the item is the target, so a key is handled once, for it.
      const item = /** @type {HTMLElement} */ (event.target);
      if (!this.#own().includes(item)) return;
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        this.#choose(item);
        return;
      }
      if (event.key !== 'ArrowRight' && event.key !== 'ArrowLeft') return;
      const rtl = getComputedStyle(this).direction === 'rtl';
      const opening = (event.key === 'ArrowRight') !== rtl;
      const group = item.querySelector(GROUP);
      event.preventDefault();
      if (opening) {
        if (!group) return;
        if (!item.hasAttribute('expanded')) { this.#expand(item, true); return; }
        this.#own().find((child) => this.#parent(child) === item && usable(child))?.focus();
      } else {
        if (group && item.hasAttribute('expanded')) { this.#expand(item, false); return; }
        this.#parent(item)?.focus(); // a disabled parent has no tabindex, so it takes no focus
      }
    });

    // A press on a disabled item gives focus to nothing, not to the item around it.
    this.listen(this, 'mousedown', (/** @type {MouseEvent} */ event) => {
      const item = event.target instanceof Element ? event.target.closest(ITEM) : null;
      if (item && item.closest(this.localName) === this && disabled(item)) event.preventDefault();
    });

    // A click on an item's label focuses the item, selects it, and opens or closes it. A click inside a group lands in the label of the item it is on, or in none.
    this.listen(this, 'click', (/** @type {MouseEvent} */ event) => {
      const label = event.target instanceof Element ? event.target.closest('[data-part="label"]') : null;
      const item = /** @type {HTMLElement | null} */ (label?.parentElement ?? null);
      if (!label || !item || !this.#own().includes(item) || labelOf(item) !== label || disabled(item)) return;
      // The press already gave the item focus: it is the focusable element around its label.
      this.#choose(item);
      if (item.querySelector(GROUP)) this.#expand(item, !item.hasAttribute('expanded'));
    });

    // The observer lives as long as the connection: the effect reads no signal, so it runs once, and its
    // cleanup disconnects.
    this.effect(() => {
      const observer = new MutationObserver((records) => {
        // Items defined after the tree: the first look decides between its value and the author's mark.
        if (!this.#settled) this.#sync();
        const items = this.#own();
        for (const record of records) {
          const marks = record.type === 'childList'
            ? [...record.addedNodes].flatMap((node) => (node instanceof Element ? [node, ...node.querySelectorAll(ITEM)] : []))
            : [record.target];
          for (const node of marks) {
            const item = /** @type {HTMLElement} */ (node);
            if (!items.includes(item)) continue;
            const target = this.#target(items);
            if (item.hasAttribute('selected') && item !== target && this.#valueOf(item) !== '') {
              // A script, or the author, marked an item selected: that item is now the value.
              this.#picked = item;
              self.value = this.#valueOf(item);
              this.#sync();
            } else if (record.attributeName === 'selected' && !item.hasAttribute('selected') && item === target) {
              // A script cleared the selected item: nothing is selected.
              this.#picked = null;
              self.value = '';
            }
          }
        }
        this.#sync();
      });
      observer.observe(this, { childList: true, subtree: true, attributes: true, attributeFilter: ['role', 'value', 'selected', 'disabled', 'aria-disabled', 'data-part'] });
      return () => observer.disconnect();
    });
    this.#sync();
  }
}
