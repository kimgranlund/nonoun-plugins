// @ts-check
/**
 * submenu.class.js: the class of the element that holds a menu item and the menu it opens. Importing it
 * defines no element; submenu.js does that.
 *
 * It has no role and paints nothing; its box is what its menu is placed against, beside the item (J25). It is
 * the menu button's pattern one level down, with a menu item as the trigger instead of a button: the trigger
 * is the child with the menuitem role, so it is an item of the menu around this element, and the menu is the
 * element with the menu role whose nearest submenu is this one. It writes the pattern's ARIA on the trigger,
 * names the menu after it, and opens and closes the menu through the menu's own `open` attribute (D67).
 *
 * A click on the trigger, and so Enter and Space, and the arrow pointing at the inline end open the menu, which
 * moves focus to its first item. Inside the menu, the arrow pointing at the inline start closes it and returns
 * focus to the trigger; Escape does the same through the menu's own dismiss, which stops the key there, so the
 * menu around stays open (J24). The menu around does not close when its submenu's trigger is activated: it
 * reads aria-haspopup on the item. Activating an item inside closes this menu, which returns focus to the
 * trigger, and the click goes on to the menu around, which closes in turn and returns focus to where it was
 * when it opened; so every level closes, however deep.
 *
 * An arrow it acts on has its default action prevented, which tells a menubar around that the key is taken.
 * Rules: docs/specs/patterns.md, J24 and J25; docs/specs/foundation.md, G1 to G4.
 */
import { UIElement } from '../../foundation/element.js';
import { props } from './submenu.props.js';

const MENU = '[role="menu"]';
const TRIGGER = 'menuitem';
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

export class UISubmenu extends UIElement {
  static props = props;

  /** @type {WeakMap<Element, string>} The aria-labelledby values this element wrote, so that it never replaces an author's. */
  #named = new WeakMap();

  /** The menu and its trigger, or null while either is missing or not yet defined. */
  #pair() {
    const trigger = /** @type {HTMLElement | undefined} */ ([...this.children].find((el) => el.getAttribute('role') === TRIGGER));
    const menu = /** @type {HTMLElement | undefined} */ ([...this.querySelectorAll(MENU)].find((el) => el.closest(this.localName) === this));
    return trigger && menu ? { menu, trigger } : null;
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

  /** The arrow keys that point at the inline end and the inline start, in this element's writing direction. */
  #arrows() {
    const rtl = getComputedStyle(this).direction === 'rtl';
    return { end: rtl ? 'ArrowLeft' : 'ArrowRight', start: rtl ? 'ArrowRight' : 'ArrowLeft' };
  }

  /**
   * Opens the menu, which moves focus to its first item and will return it to the trigger. A menu that is open
   * already closes first, with focus on the trigger, and opens again, so that focus goes back into it.
   * @param {{ menu: HTMLElement, trigger: HTMLElement }} pair
   */
  #open({ menu, trigger }) {
    if (menu.hasAttribute('open')) {
      put(menu, 'open', null);
      trigger.focus();
    }
    put(menu, 'open', '');
    this.#sync();
  }

  connected() {
    /** The pair, when the event happened on a trigger that is not disabled. @param {Event} event */
    const fromTrigger = (event) => {
      const pair = this.#pair();
      return pair && event.target instanceof Node && pair.trigger.contains(event.target) && !disabled(pair.trigger) ? pair : null;
    };

    // A click, and so Enter and Space on the item, opens the menu (J24).
    this.listen(this, 'click', (event) => {
      const pair = fromTrigger(event);
      if (pair) this.#open(pair);
    });

    this.listen(this, 'keydown', (event) => {
      if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
      const { end, start } = this.#arrows();
      if (event.key === end) {
        const pair = fromTrigger(event);
        if (!pair) return;
        event.preventDefault();
        this.#open(pair);
        return;
      }
      if (event.key !== start) return;
      const pair = this.#pair();
      // Only a key pressed on an item of this menu, not of a menu nested deeper, which has its own submenu.
      if (!pair || !pair.menu.hasAttribute('open') || !(event.target instanceof Element) || event.target.closest(MENU) !== pair.menu) return;
      event.preventDefault();
      put(pair.menu, 'open', null);
      pair.trigger.focus();
      this.#sync();
    });

    // While the menu is open, the pointer passing over the trigger leaves focus in the menu: the menu around
    // would otherwise move focus to the trigger, and this menu would close as focus left it.
    this.listen(this, 'pointermove', (event) => {
      if (fromTrigger(event)?.menu.hasAttribute('open')) event.stopPropagation();
    });

    // A menu around this one that closes, by a script or otherwise, closes this one too. toggle does not
    // bubble, so it is caught on its way down.
    this.listen(this.ownerDocument, 'toggle', (event) => {
      const pair = this.#pair();
      const closed = /** @type {ToggleEvent} */ (event).newState === 'closed';
      if (closed && pair && event.target instanceof Node && event.target !== pair.menu && event.target.contains(this)) put(pair.menu, 'open', null);
    }, { capture: true });

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
