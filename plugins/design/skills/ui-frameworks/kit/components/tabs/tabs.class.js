// @ts-check
/**
 * tabs.class.js: the class of the element that holds a tab list and its panels. Importing it defines no
 * element; tabs.js does that.
 *
 * It coordinates three other components and names none of them. It finds tabs and panels by their ARIA role
 * and writes their state through their own attributes, so it works whichever element is defined first, and
 * with tabs or panels that arrive later. An observer on its subtree is what tells it that something changed.
 *
 * Rules: docs/specs/foundation.md, G1 to G6.
 */
import { UIElement } from '../../foundation/element.js';
import { props } from './tabs.props.js';

const TAB = '[role="tab"]';
const PANEL = '[role="tabpanel"]';
/** For the ids this class gives to a tab or a panel that has none. */
let serial = 0;

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

export class UITabs extends UIElement {
  static props = props;

  /** @type {WeakMap<Element, string>} The aria-labelledby values this element wrote, so that it never replaces an author's. */
  #named = new WeakMap();

  /**
   * The elements of one role that belong to this element, and not to another one nested in a panel.
   * @param {string} selector @returns {HTMLElement[]}
   */
  #own(selector) {
    return /** @type {HTMLElement[]} */ ([...this.querySelectorAll(selector)].filter((el) => el.closest(this.localName) === this));
  }

  /**
   * A tab's or a panel's value: its `value` attribute, or else its position among its kind.
   * @param {Element} el @param {Element[]} kind
   */
  #valueOf(el, kind) { return el.getAttribute('value') ?? String(kind.indexOf(el)); }

  /** Brings the tabs and the panels in step with `value`. Writes nothing when they already are. */
  #sync() {
    const self = /** @type {any} */ (this);
    const tabs = this.#own(TAB), panels = this.#own(PANEL);
    if (!tabs.length) return;
    if (self.value === '') {
      // Nothing chosen yet: take what the author marked, or the first tab that can be selected.
      const first = tabs.find((tab) => tab.hasAttribute('selected')) ?? tabs.find((tab) => !disabled(tab)) ?? tabs[0];
      self.value = this.#valueOf(first, tabs);
      return; // changed() has run this again with the value in place.
    }
    // A value that names no tab shows no panel, even when a panel has that value.
    const named = tabs.some((tab) => this.#valueOf(tab, tabs) === self.value);
    for (const panel of panels) {
      if (!panel.id) panel.id = `${this.localName}-${++serial}`;
      put(panel, 'hidden', named && this.#valueOf(panel, panels) === self.value ? null : '');
    }
    for (const tab of tabs) {
      const value = this.#valueOf(tab, tabs);
      const panel = panels.find((candidate) => this.#valueOf(candidate, panels) === value);
      if (!tab.id) tab.id = `${this.localName}-${++serial}`;
      put(tab, 'selected', value === self.value ? '' : null);
      if (!panel) continue;
      put(tab, 'aria-controls', panel.id);
      // A panel the author named keeps its name (A2). One this element named follows its tab.
      const name = panel.getAttribute('aria-labelledby');
      if (panel.hasAttribute('aria-label') || (name !== null && name !== this.#named.get(panel))) continue;
      put(panel, 'aria-labelledby', tab.id);
      this.#named.set(panel, tab.id);
    }
  }

  /**
   * Selects a tab because the user asked for it.
   * @param {EventTarget | null} target  Where the click or the focus landed.
   */
  #choose(target) {
    const self = /** @type {any} */ (this);
    const tabs = this.#own(TAB);
    const tab = /** @type {HTMLElement | null} */ (target instanceof Element ? target.closest(TAB) : null);
    if (!tab || !tabs.includes(tab) || disabled(tab)) return;
    const value = this.#valueOf(tab, tabs);
    if (value === self.value) return;
    self.value = value; // changed() brings the tabs and the panels up to date before this returns.
    this.dispatchEvent(new Event('change', { bubbles: true }));
  }

  /** @param {string} name */
  changed(name) {
    if (name === 'value' && this.isConnected) this.#sync();
  }

  connected() {
    const self = /** @type {any} */ (this);
    this.listen(this, 'click', (event) => this.#choose(event.target));
    this.listen(this, 'focusin', (event) => { if (self.activation === 'automatic') this.#choose(event.target); });

    // The observer lives as long as the connection: the effect reads no signal, so it runs once, and its
    // cleanup disconnects.
    this.effect(() => {
      const observer = new MutationObserver((records) => {
        const tabs = this.#own(TAB);
        for (const record of records) {
          // A script, or the author, marked a tab selected: that tab is now the value.
          const tab = /** @type {HTMLElement} */ (record.target);
          if (record.attributeName !== 'selected' || !tab.hasAttribute('selected') || !tabs.includes(tab)) continue;
          const value = this.#valueOf(tab, tabs);
          if (value !== self.value) self.value = value;
        }
        this.#sync();
      });
      observer.observe(this, { childList: true, subtree: true, attributes: true, attributeFilter: ['role', 'value', 'selected', 'disabled', 'aria-disabled'] });
      return () => observer.disconnect();
    });
    this.#sync();
  }
}
