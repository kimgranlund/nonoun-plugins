// @ts-check
/**
 * menu-button.class.js: the class of the element that holds a trigger and its menu. Importing it defines no
 * element; menu-button.js does that.
 *
 * It has no role and paints nothing; its box is what the menu is placed against. It coordinates two others
 * and names neither: the menu is the element with the menu role, and the trigger is the first element with
 * the button role, or native button, that is not inside the menu (G10). It writes the pattern's ARIA on the
 * trigger, and opens and closes the menu through the menu's own `open` attribute (D67). An observer on its
 * subtree tells it when one of them is defined, added or removed, or when the menu opens or closes by itself.
 *
 * Rules: docs/specs/foundation.md, G1 to G4 and G10, G11.
 */
import { UIElement } from '../../foundation/element.js';
import { props } from './menu-button.props.js';

const MENU = '[role="menu"]';
const BUTTON = 'button, [role="button"]';
/** A menu's items: plain, checkbox and radio items. An item of a submenu's menu belongs to that menu. */
const ITEM = '[role="menuitem"], [role="menuitemcheckbox"], [role="menuitemradio"]';
/** For the ids this class gives to a trigger or a menu that has none. */
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

export class UIMenuButton extends UIElement {
  static props = props;

  /** @type {WeakMap<Element, string>} The aria-labelledby values this element wrote, so that it never replaces an author's. */
  #named = new WeakMap();

  /**
   * The elements that match, and belong to this element rather than to one nested inside it.
   * @param {string} selector @returns {HTMLElement[]}
   */
  #own(selector) {
    return /** @type {HTMLElement[]} */ ([...this.querySelectorAll(selector)].filter((el) => el.closest(this.localName) === this));
  }

  /** The menu and its trigger, or null while either is missing or not yet defined. */
  #pair() {
    const menu = this.#own(MENU)[0];
    const trigger = menu && this.#own(BUTTON).find((el) => !menu.contains(el));
    return trigger ? { menu, trigger } : null;
  }

  /** Brings the trigger's ARIA and the menu's name in step. Writes nothing when they already are. */
  #sync() {
    const pair = this.#pair();
    if (!pair) return;
    const { menu, trigger } = pair;
    if (!trigger.id) trigger.id = `${this.localName}-${++serial}`;
    if (!menu.id) menu.id = `${this.localName}-${++serial}`;
    put(trigger, 'aria-haspopup', 'menu');
    put(trigger, 'aria-controls', menu.id);
    put(trigger, 'aria-expanded', String(menu.hasAttribute('open')));
    // A menu the author named keeps its name (A2). One this element named follows its trigger.
    const name = menu.getAttribute('aria-labelledby');
    if (menu.hasAttribute('aria-label') || (name !== null && name !== this.#named.get(menu))) return;
    put(menu, 'aria-labelledby', trigger.id);
    this.#named.set(menu, trigger.id);
  }

  /**
   * The menu and the trigger when the event happened on a trigger that is not disabled.
   * @param {Event} event
   */
  #fromTrigger(event) {
    const pair = this.#pair();
    if (!pair || !(event.target instanceof Node) || !pair.trigger.contains(event.target) || disabled(pair.trigger)) return null;
    return pair;
  }

  connected() {
    // A click, and so Enter and Space on the kit's button, opens the menu or closes it (G11).
    this.listen(this, 'click', (event) => {
      const pair = this.#fromTrigger(event);
      if (!pair) return;
      put(pair.menu, 'open', pair.menu.hasAttribute('open') ? null : '');
      this.#sync();
    });
    // ArrowDown opens the menu, which moves focus to its first item; ArrowUp then moves focus to the last.
    this.listen(this, 'keydown', (event) => {
      if (event.key !== 'ArrowDown' && event.key !== 'ArrowUp') return;
      const pair = this.#fromTrigger(event);
      if (!pair) return;
      event.preventDefault();
      put(pair.menu, 'open', '');
      this.#sync();
      if (event.key === 'ArrowUp') [.../** @type {NodeListOf<HTMLElement>} */ (pair.menu.querySelectorAll(ITEM))].filter((item) => item.closest(MENU) === pair.menu).filter((item) => !disabled(item)).pop()?.focus();
    });

    // The observer lives as long as the connection: the effect reads no signal, so it runs once, and its
    // cleanup disconnects.
    this.effect(() => {
      const observer = new MutationObserver(() => this.#sync());
      observer.observe(this, { childList: true, subtree: true, attributes: true, attributeFilter: ['role', 'open'] });
      return () => observer.disconnect();
    });
    this.#sync();
  }
}
