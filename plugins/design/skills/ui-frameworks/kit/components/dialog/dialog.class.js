// @ts-check
/**
 * dialog.class.js: the dialog's class. Importing it defines no element; dialog.js does that.
 *
 * The modal layer is the browser's own dialog element, which the author writes inside the root and marks
 * with data-part="panel" (D91). This class opens it as a modal while `open` is set and closes it when `open`
 * goes, removes `open` when the browser closes it (Escape, a form with method="dialog"), and names it after
 * its title and description. It adds no focus handling, no inertness and no Escape handling (J40): the native
 * dialog does all of it. It names no tag of the kit and dispatches no event; the part's own `close` event and
 * its `returnValue` are the author's interface.
 *
 * Rules: docs/specs/patterns.md, J39 to J42.
 */
import { UIElement } from '../../foundation/element.js';
import { props, parts, role, tabindex } from './dialog.props.js';

/** For the ids this class gives to a title or a description that has none. */
let serial = 0;

export class UIDialog extends UIElement {
  static props = props;
  static parts = parts;
  static role = role;
  static tabindex = tabindex;

  /** @type {HTMLDialogElement | null} The part whose close event is heard. */
  #bound = null;
  #unbind = () => {};
  /** @type {Map<string, string>} What this class wrote on the part, by attribute, so that it never replaces an author's. */
  #wrote = new Map();

  /** The dialog part, or null while it is missing or not a connected dialog element. */
  get #part() {
    const el = this.querySelector(':scope > [data-part="panel"]');
    return el instanceof HTMLDialogElement && el.isConnected ? el : null;
  }

  /** Brings the part in step with `open`. */
  #sync() {
    const part = this.#part;
    if (!part || !this.isConnected) return;
    const open = /** @type {any} */ (this).open;
    if (open && !part.matches(':modal')) {
      // A part that is open but not modal was open when it was put back in the page: it is shown again as a modal.
      if (part.open) part.close();
      part.showModal();
    } else if (!open && part.open) part.close();
  }

  /**
   * Sets or removes an attribute this class wrote, only when it differs.
   * @param {HTMLElement} part @param {string} name @param {string | null} value
   */
  #put(part, name, value) {
    const mine = this.#wrote.get(name);
    const has = part.hasAttribute(name);
    if (has && part.getAttribute(name) !== mine) return; // the author's
    if (value === null) { part.removeAttribute(name); this.#wrote.delete(name); return; }
    if (part.getAttribute(name) !== value) part.setAttribute(name, value);
    this.#wrote.set(name, value);
  }

  /** Names and describes the part, and gives it the alertdialog role. */
  #name() {
    const part = this.#part;
    if (!part) return;
    const idOf = (/** @type {Element | null} */ el, /** @type {string} */ what) => {
      if (!el) return null;
      if (!el.id) el.id = `${this.localName}-${what}-${++serial}`;
      return el.id;
    };
    this.#put(part, 'aria-labelledby', idOf(part.querySelector('[data-part="title"]'), 'title'));
    this.#put(part, 'aria-describedby', idOf(part.querySelector('[data-part="description"]'), 'description'));
    this.#put(part, 'role', /** @type {any} */ (this).alert ? 'alertdialog' : null);
  }

  /** Listens for the close event of the part, and again when the part is replaced. */
  #bind() {
    const part = this.#part;
    if (part === this.#bound) return;
    this.#unbind();
    this.#bound = part;
    this.#wrote.clear();
    if (!part) { this.#unbind = () => {}; return; }
    const onClose = () => { if (!part.open && /** @type {any} */ (this).open) /** @type {any} */ (this).open = false; };
    part.addEventListener('close', onClose);
    this.#unbind = () => part.removeEventListener('close', onClose);
  }

  connected() {
    const refresh = () => { this.#bind(); this.#name(); this.#sync(); };
    refresh();
    const observer = new MutationObserver(refresh);
    observer.observe(this, { childList: true, subtree: true });
    this.effect(() => () => { observer.disconnect(); this.#unbind(); this.#unbind = () => {}; this.#bound = null; });
  }

  /** @param {string} name */
  changed(name) {
    if (name === 'open') this.#sync();
    else if (name === 'alert') this.#name();
  }
}
