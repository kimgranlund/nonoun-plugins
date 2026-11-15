// @ts-check
/**
 * menu-group.class.js: the class of a set of menu items that belong together. Importing it defines no
 * element; menu-group.js does that.
 *
 * The root has the group role. It is named after its label, the child the author marked with
 * `data-part="label"`, through aria-labelledby, unless the author named it; the label gets an id only when it
 * has none (J23). Of the radio items that are its children, it keeps at most one checked: when one gains
 * `checked`, from the user or from a script, it removes `checked` from the others, through their own author
 * attribute (J22, G3). An observer on its subtree tells it, as the accordion's does.
 *
 * It does not know the menu around it; the menu finds the items inside it by their role.
 * Rules: docs/specs/patterns.md, J22 and J23.
 */
import { UIElement } from '../../foundation/element.js';
import { props, role } from './menu-group.props.js';

const RADIO = 'menuitemradio';
/** For the ids this class gives to a label that has none. */
let serial = 0;

export class UIMenuGroup extends UIElement {
  static props = props;
  static role = role;

  /** @type {string | null} The aria-labelledby value this element wrote, so that it never replaces an author's. */
  #named = null;

  /** Names the group after its label, unless the author named it. Writes nothing when it already is. */
  #name() {
    const current = this.getAttribute('aria-labelledby');
    if (current !== null && current !== this.#named) return;
    const label = this.ensurePart('label');
    // A name the author gave with aria-label wins: the reference this element wrote would hide it.
    if (!label || this.hasAttribute('aria-label')) {
      if (current !== null) this.removeAttribute('aria-labelledby');
      this.#named = null;
      return;
    }
    if (!label.id) label.id = `${this.localName}-${++serial}`;
    if (current !== label.id) this.setAttribute('aria-labelledby', label.id);
    this.#named = label.id;
  }

  /**
   * Turns off every radio child but the one that was turned on last.
   * @param {MutationRecord[]} records
   */
  #checked(records) {
    /** @type {Element | null} The last radio child that gained checked and still has it. */
    let checked = null;
    for (const r of records) {
      const el = /** @type {Element} */ (r.target);
      if (r.attributeName === 'checked' && el.parentElement === this && el.getAttribute('role') === RADIO && r.oldValue === null && el.hasAttribute('checked')) checked = el;
    }
    if (!checked) return;
    // Removing an attribute that is absent changes nothing and is not recorded, so this writes only what differs.
    for (const child of this.children) if (child !== checked && child.getAttribute('role') === RADIO) child.removeAttribute('checked');
  }

  connected() {
    // The observer lives as long as the connection: the effect reads no signal, so it runs once, and its
    // cleanup disconnects.
    this.effect(() => {
      const observer = new MutationObserver((records) => { this.#checked(records); this.#name(); });
      observer.observe(this, { childList: true, subtree: true, attributes: true, attributeFilter: ['checked', 'data-part', 'id', 'aria-label'], attributeOldValue: true });
      return () => observer.disconnect();
    });
    this.#name();
  }
}
