// @ts-check
/**
 * menu.class.js: the class of a menu, a list of actions that opens over the page. Importing it defines no
 * element; menu.js does that.
 *
 * The root has the menu role and is a manual popover: it shows in the top layer exactly while it has the
 * `open` attribute, whoever sets it (G15). When it opens it remembers the element that had focus and moves
 * focus to its first item that is not disabled. Inside it, roving focus moves among the items, typeahead finds
 * one by its text, and the pointer moves focus to the item under it. Escape and the activation of an item close
 * it and return focus to where it was; a press outside and focus that leaves close it and leave focus alone.
 *
 * Its items are the elements with the menuitem, menuitemcheckbox or menuitemradio role whose nearest menu is
 * this one: an item of a menu nested inside it, such as a submenu's, belongs to that menu, while the item that
 * opens a submenu belongs to this one. A checkable item stays open after a click from the pointer or Space, so
 * that it can be toggled again, and closes after Enter: the press behaviour clicks on Enter while the key is
 * still down, so the item then carries `data-active`, and on Space after the key has come up, when it does not.
 * An item that opens a menu of its own (aria-haspopup) does not close this one.
 *
 * It finds its items by their ARIA role and names no tag. Rules: docs/specs/foundation.md, G12 to G15, and
 * docs/specs/patterns.md, J21, J22 and J24.
 */
import { UIElement } from '../../foundation/element.js';
import { rovingFocus } from '../../behaviours/roving-focus.js';
import { typeahead } from '../../behaviours/typeahead.js';
import { dismiss } from '../../behaviours/dismiss.js';
import { props, role } from './menu.props.js';

const MENU = '[role="menu"]';
const ITEM = '[role="menuitem"], [role="menuitemcheckbox"], [role="menuitemradio"]';
const CHECKABLE = '[role="menuitemcheckbox"], [role="menuitemradio"]';

/** @param {Element} el */
const disabled = (el) => el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true';

/** The item an event happened in, if any. @param {Event} event */
const itemOf = (event) => /** @type {HTMLElement | null} */ (event.target instanceof Element ? event.target.closest(ITEM) : null);

/**
 * Whether activating the item leaves its menu open: it opens a menu of its own, or it is a checkable item
 * that the pointer or Space activated (Enter clicks while press still marks the item `data-active`).
 * @param {Element} item
 */
const staysOpen = (item) => ['true', 'menu'].includes(item.getAttribute('aria-haspopup') ?? '')
  || (item.matches(CHECKABLE) && !item.hasAttribute('data-active'));

export class UIMenu extends UIElement {
  static props = props;
  static role = role;

  /** @type {HTMLElement | null} The element that had focus when the menu last opened. */
  #opener = null;
  /** Whether the click on its way through leaves the menu open: read before any listener has run. */
  #stays = false;

  /** @returns {HTMLElement[]} */
  #items() { return /** @type {HTMLElement[]} */ ([...this.querySelectorAll(ITEM)].filter((el) => el.closest(MENU) === this)); }

  /**
   * Shows or hides the popover so that it is showing exactly while `open` is set. Runs synchronously, so a
   * script that sets `open` finds the menu shown in the same task.
   */
  #apply() {
    const open = /** @type {any} */ (this).open;
    // Before connected() has run there is no popover attribute yet, and a removed menu cannot show.
    if (!this.isConnected || !this.hasAttribute('popover') || open === this.matches(':popover-open')) return;
    if (!open) return this.hidePopover();
    this.#opener = /** @type {HTMLElement | null} */ (this.ownerDocument.activeElement);
    this.showPopover();
    this.#items().find((item) => !disabled(item))?.focus();
  }

  /** Closes the menu, and with `restore` returns focus to where it was when the menu opened. @param {boolean} restore */
  #close(restore) {
    const opener = this.#opener;
    /** @type {any} */ (this).open = false;
    if (restore) opener?.focus();
  }

  /** @param {string} name */
  changed(name) {
    if (name === 'open') this.#apply();
  }

  connected() {
    const self = /** @type {any} */ (this);
    if (!this.hasAttribute('popover')) this.setAttribute('popover', 'manual');
    const items = () => this.#items();

    // Something else hid the popover, such as a script calling hidePopover(): the attribute follows.
    this.listen(this, 'toggle', () => { if (self.open && !this.matches(':popover-open')) self.open = false; });
    // Whether the click leaves the menu open is read as it starts down the tree: by the time it bubbles back,
    // a menu nested in this one may have closed and moved focus, and the item has then lost data-active.
    this.listen(this, 'click', (event) => {
      const item = itemOf(event);
      this.#stays = !!item && staysOpen(item);
    }, { capture: true });
    // Activating an item closes the menu after the item's own click listeners have run. The item may belong to
    // a menu nested in this one, which has closed already: this one closes too, so every level closes (J24).
    this.listen(this, 'click', (event) => {
      const item = itemOf(event);
      if (this.#stays) return;
      if (item && !disabled(item)) this.#close(true);
    });
    // A press moves no focus here. On a disabled item, or between the items, it would take focus from the menu
    // and leave it open with no key to close it; on any other item the pointer has already moved focus there.
    this.listen(this, 'mousedown', (event) => event.preventDefault());
    // One marked row: the pointer moves focus, so the row under it and the row the keys reached are the same.
    // A disabled item has no tabindex (roving focus skips it), so focus() leaves it alone.
    this.listen(this, 'pointermove', (event) => itemOf(event)?.focus({ preventScroll: true }));

    this.use(rovingFocus, { items, orientation: () => 'vertical', skip: disabled });
    // A letter typed in a menu nested in this one is that menu's: this one moves no focus then.
    this.use(typeahead, { items, skip: disabled, onMatch: (/** @type {HTMLElement} */ item) => {
      if (this.ownerDocument.activeElement?.closest(MENU) === this) item.focus();
    } });
    // No `active` option: while the menu is closed, focus cannot be inside it, and the press outside that
    // dismiss then reports closes a closed menu, which writes nothing and moves no focus.
    this.use(dismiss, {
      ignore: () => [this.#opener],
      onDismiss: (/** @type {string} */ reason) => this.#close(reason === 'escape'),
    });
    this.#apply();
  }
}
