// @ts-check
/**
 * disclosure.class.js: the class of the element that holds a trigger and the panel it shows and hides.
 * Importing it defines no element; disclosure.js does that.
 *
 * It has no role and paints nothing. It names no other component: the panel is its child marked
 * `data-part="panel"`, and the trigger is the first element with the button role, or native button, that
 * belongs to this element and is not inside the panel, wherever the author put it, a heading included (J9).
 * It writes the pattern's ARIA on the trigger, and an id on the panel only when the panel has none. The recipe
 * alone shows and hides the panel, from the root's `open`, so the state is right before the element is
 * defined (J10); this class never writes `hidden`. An observer on its subtree tells it when the trigger or the
 * panel is defined, added or removed.
 *
 * Rules: docs/specs/patterns.md, J9 and J10.
 */
import { UIElement } from '../../foundation/element.js';
import { props, role, tabindex } from './disclosure.props.js';

const PANEL = ':scope > [data-part="panel"]';
const BUTTON = 'button, [role="button"]';
/** For the ids this class gives to a panel that has none. */
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

export class UIDisclosure extends UIElement {
  static props = props;
  static role = role;
  static tabindex = tabindex;

  /** The panel and its trigger, or null while either is missing or the trigger is not yet defined. */
  #pair() {
    const panel = /** @type {HTMLElement | null} */ (this.querySelector(PANEL));
    if (!panel) return null;
    const trigger = /** @type {HTMLElement | undefined} */ ([...this.querySelectorAll(BUTTON)]
      .find((el) => el.closest(this.localName) === this && !panel.contains(el)));
    return trigger ? { panel, trigger } : null;
  }

  /** Brings the trigger's ARIA and the panel's id in step. Writes nothing when they already are. */
  #sync() {
    const pair = this.#pair();
    if (!pair) return;
    const { panel, trigger } = pair;
    if (!panel.id) panel.id = `${this.localName}-${++serial}`;
    put(trigger, 'aria-controls', panel.id);
    put(trigger, 'aria-expanded', String(this.hasAttribute('open')));
  }

  /** @param {string} name */
  changed(name) {
    // A script's write must show on the trigger in the same task (J10).
    if (name === 'open') this.#sync();
  }

  connected() {
    // A click, and so Enter and Space on the kit's button, shows the panel or hides it (J10).
    this.listen(this, 'click', (event) => {
      const pair = this.#pair();
      if (!pair || !(event.target instanceof Node) || !pair.trigger.contains(event.target) || disabled(pair.trigger)) return;
      const self = /** @type {any} */ (this);
      self.open = !self.open;
      this.dispatchEvent(new Event('toggle', { bubbles: true }));
    });

    // The observer lives as long as the connection: the effect reads no signal, so it runs once, and its
    // cleanup disconnects.
    this.effect(() => {
      const observer = new MutationObserver(() => this.#sync());
      observer.observe(this, { childList: true, subtree: true, attributes: true, attributeFilter: ['role', 'data-part'] });
      return () => observer.disconnect();
    });
    this.#sync();
  }
}
