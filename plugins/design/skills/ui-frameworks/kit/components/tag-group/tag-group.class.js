// @ts-check
/**
 * tag-group.class.js: the tag group's class. Importing it defines no element; tag-group.js does that.
 *
 * The root has the group role. Its focus stops are the remove controls of its tags: elements marked
 * data-part="remove" inside a direct child. Roving focus keeps one of them reachable and moves focus among them
 * with the arrow keys, without wrapping (J115).
 *
 * The group never removes a tag. A press on a remove control, and Delete or Backspace on one, dispatch `remove`
 * with the tag in `detail.tag`. When the tag that held focus leaves the group, focus goes to the control of the
 * tag that followed it, else the one before, else the group (J116). The group takes tabindex="-1" only for that
 * moment, and gives it up when focus leaves.
 *
 * A disabled group is inert: it takes no focus and dispatches nothing (J117). It writes aria-disabled and inert on itself.
 */
import { UIElement, setAttr } from '../../foundation/element.js';
import { rovingFocus } from '../../behaviours/roving-focus.js';
import { props, role } from './tag-group.props.js';

const REMOVE = '[data-part="remove"]';
const off = (/** @type {Element} */ el) => el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true';

export class UITagGroup extends UIElement {
  static props = props;
  static role = role;

  /** The tag, a direct child, that holds the focus; null while focus is elsewhere. @type {Element | null} */
  #held = null;
  /** Whether this group wrote inert itself. */
  #inert = false;
  /** Whether this group wrote tabindex itself. */
  #tabindex = false;

  /** The tag, a direct child of the group, that holds `el`. @param {Element | null} el @returns {Element | null} */
  #tagOf(el) {
    let at = el;
    while (at && at.parentElement !== this) at = at.parentElement;
    return at;
  }

  /** The remove controls of the group, in document order: those inside a direct child. @returns {HTMLElement[]} */
  #controls() {
    return /** @type {HTMLElement[]} */ ([...this.children].flatMap((tag) => [...tag.querySelectorAll(REMOVE)]));
  }

  /** The first remove control of the tags from `from` on, in `step` direction, that is still in the group. @param {Node | null} from @param {'nextSibling' | 'previousSibling'} step */
  #walk(from, step) {
    for (let at = from; at; at = at[step]) {
      if (at.parentNode !== this) return null;
      const control = /** @type {Element} */ (at).querySelector?.(REMOVE);
      if (control && !off(control)) return /** @type {HTMLElement} */ (control);
    }
    return null;
  }

  /** The group is the target of focus for as long as it takes. */
  #focusSelf() {
    if (!this.hasAttribute('tabindex')) { this.setAttribute('tabindex', '-1'); this.#tabindex = true; }
    this.focus();
  }

  connected() {
    const self = /** @type {any} */ (this);

    this.effect(() => {
      const disabled = !!self.disabled;
      setAttr(this, 'aria-disabled', disabled ? 'true' : null);
      if (disabled && !this.hasAttribute('inert')) { this.setAttribute('inert', ''); this.#inert = true; }
      else if (!disabled && this.#inert) { this.removeAttribute('inert'); this.#inert = false; }
    });

    this.use(rovingFocus, {
      items: () => this.#controls(),
      skip: (/** @type {HTMLElement} */ el) => !!self.disabled || off(el),
      wrap: false,
    });

    const ask = (/** @type {Element} */ control) => {
      if (self.disabled || off(control)) return;
      const tag = this.#tagOf(control);
      if (tag) this.emit('remove', { tag });
    };

    this.listen(this, 'click', (event) => {
      const control = /** @type {Element | null} */ (event.target instanceof Element ? event.target.closest(REMOVE) : null);
      if (control && this.#controls().includes(/** @type {HTMLElement} */ (control))) ask(control);
    });

    this.listen(this, 'keydown', (event) => {
      if (event.key !== 'Delete' && event.key !== 'Backspace') return;
      if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
      const at = this.#controls().find((control) => control === event.target);
      if (!at) return;
      event.preventDefault();
      ask(at);
    });

    this.listen(this, 'focusin', (event) => { this.#held = this.#tagOf(/** @type {Element} */ (event.target)); });
    this.listen(this, 'focusout', (event) => {
      if (this.#tabindex && event.target === this) { this.removeAttribute('tabindex'); this.#tabindex = false; }
      const to = /** @type {FocusEvent} */ (event).relatedTarget;
      if (to instanceof Node) { this.#held = null; return; }
      // Focus that leaves with nowhere to go is either a click on nothing or the removal of the focused tag, and
      // an engine may report the second before the tag has left. The observer settles that in a microtask; a tag
      // still in the group after a task, with focus outside, was a plain blur.
      setTimeout(() => { if (this.#held?.parentNode === this && !this.contains(document.activeElement)) this.#held = null; });
    });

    // The observer lives as long as the connection: the effect reads no signal, so it runs once.
    this.effect(() => {
      const observer = new MutationObserver((records) => {
        const held = this.#held;
        if (!held || held.parentNode === this) return;
        const record = records.find((r) => [...r.removedNodes].includes(held));
        this.#held = null;
        const next = this.#walk(record?.nextSibling ?? null, 'nextSibling')
          ?? this.#walk(record?.previousSibling ?? null, 'previousSibling')
          ?? this.#controls().find((control) => !off(control));
        if (next) next.focus();
        else this.#focusSelf();
      });
      observer.observe(this, { childList: true });
      return () => observer.disconnect();
    });
  }
}
