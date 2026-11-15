// @ts-check
/**
 * menubar.class.js: the class of a row of menus. Importing it defines no element; menubar.js does that.
 *
 * The root has the menubar role and is one stop in the Tab order: roving focus keeps one of its buttons
 * reachable and moves focus among them with the arrow keys of the row, wrapping (J26). Its buttons are the
 * triggers of the menu buttons the author writes inside it: the elements with the button role, or native
 * buttons, that are not inside a menu and that their menu button has marked with aria-haspopup. Each menu button opens its own menu, on ArrowDown, Enter and Space, and
 * the menu returns focus to its button on Escape.
 *
 * While one of its menus is open, the arrows along the row pressed inside that menu close it and open the next
 * or the previous one, through the menu's own `open` attribute, as the menu button does; the menu then moves
 * focus to its first item. An arrow that a submenu has taken, to open or to close a level, has its default
 * action prevented, and is left alone. A button's menu is the element its aria-controls names, which its menu
 * button writes, so this class names no other component.
 *
 * Rules: docs/specs/patterns.md, J26.
 */
import { UIElement } from '../../foundation/element.js';
import { rovingFocus } from '../../behaviours/roving-focus.js';
import { props, role } from './menubar.props.js';

const BUTTON = 'button, [role="button"]';
const MENU = '[role="menu"]';

/** @param {Element} el */
const disabled = (el) => el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true';

export class UIMenubar extends UIElement {
  static props = props;
  static role = role;

  /**
   * The buttons of this menubar, in document order: the triggers of its menu buttons. A trigger is an element
   * with the button role, or a native button, that is not inside a menu and that its menu button has marked
   * with aria-haspopup; not of a menubar nested in this one. Until the menu has its role, a button inside it
   * cannot be told from a trigger, so the mark is waited for, whatever is defined first.
   * @returns {HTMLElement[]}
   */
  #buttons() {
    return /** @type {HTMLElement[]} */ ([...this.querySelectorAll(BUTTON)].filter((el) => el.closest(this.localName) === this
      && el.hasAttribute('aria-haspopup') && !el.closest(MENU)));
  }

  /** The menu a button opens: the element its aria-controls names, inside this menubar. @param {Element} button */
  #menuOf(button) {
    const id = button.getAttribute('aria-controls');
    return id ? /** @type {HTMLElement | null} */ (this.querySelector(`#${CSS.escape(id)}`)) : null;
  }

  connected() {
    this.use(rovingFocus, {
      items: () => this.#buttons(),
      orientation: () => 'horizontal',
      skip: disabled,
      // A trigger becomes a button of the bar when its menu button marks it, after the trigger has its role and
      // the kit's button its own tabindex="0".
      watch: ['aria-haspopup'],
    });

    // An arrow along the row, pressed inside a menu, moves to the next or the previous menu (J26). Focus can
    // only be inside a menu while it is open: a closed one is not displayed.
    this.listen(this, 'keydown', (event) => {
      if (event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
      if (event.key !== 'ArrowRight' && event.key !== 'ArrowLeft') return;
      if (!(event.target instanceof Element)) return;
      const buttons = this.#buttons().filter((button) => !disabled(button));
      const at = buttons.findIndex((button) => {
        const menu = this.#menuOf(button);
        return !!menu && menu.contains(/** @type {Element} */ (event.target));
      });
      if (at < 0) return;
      const forward = (event.key === 'ArrowRight') === (getComputedStyle(this).direction !== 'rtl');
      const next = buttons[(at + (forward ? 1 : -1) + buttons.length) % buttons.length];
      event.preventDefault();
      // Focus leaving the open menu closes it, and every menu inside it (G14); the next menu, opened once focus
      // is on its button, returns focus there when it closes.
      next.focus();
      this.#menuOf(next)?.setAttribute('open', '');
    });
  }
}
