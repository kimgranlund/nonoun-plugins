// @ts-check
/**
 * toast.class.js: the toast's class, an alert with a time limit. Importing it defines no element; toast.js does that.
 *
 * The role (J92): status, or alert when the variant is critical, unless the author wrote a role. The class keeps
 * the value it wrote, so it updates its own and never the author's. The recipe gives a toast without `open` no box,
 * so it takes no room and is not read.
 *
 * The time (J93): a toast that is open and connected closes itself `duration` milliseconds after it opened; with 0 it
 * stays. The time does not run while the pointer is over the toast or focus is inside it, and starts again from the
 * full duration once both have left (WCAG 2.2.1). A press on a descendant marked data-part="close", and Escape while
 * focus is inside (through the dismiss behaviour), close it. Closing, by any of these or by a script, removes `open`
 * and dispatches `close` once. The toast never removes itself from the document.
 *
 * The entry (J95): when it opens, or connects open for the first time, the class sets the private custom property
 * --_entering to 1 on the root's own inline style for two frames, then removes it. The recipe reads it, only when
 * motion is allowed, as the starting opacity of a transition. That is the one style a class writes.
 *
 * It names no tag. Rules: docs/specs/patterns.md, J92 to J95.
 */
import { UIElement } from '../../foundation/element.js';
import { dismiss } from '../../behaviours/dismiss.js';
import { props, parts, role, tabindex } from './toast.props.js';

const CLOSE = '[data-part="close"]';

export class UIToast extends UIElement {
  static props = props;
  static parts = parts;
  static role = role;
  static tabindex = tabindex;

  /** @type {string | null} The role this element wrote, so that it never replaces an author's. */
  #role = null;
  /** Whether `open` was set the last time it was looked at, so that closing is seen once. */
  #wasOpen = false;
  /** Whether connected() has run and the connection has not ended. */
  #live = false;
  #hovered = false;
  #focused = false;
  /** @type {ReturnType<typeof setTimeout> | undefined} */
  #timer;
  /** @type {number | undefined} */
  #frame;

  get #self() { return /** @type {any} */ (this); }

  /** Writes status, or alert for a critical toast, when the role is absent or the one this element wrote. */
  #writeRole() {
    const current = this.getAttribute('role');
    if (current !== null && current !== this.#role) return;
    const next = this.#self.variant === 'critical' ? 'alert' : 'status';
    if (current !== next) this.setAttribute('role', next);
    this.#role = next;
  }

  /** Starts the time from the full duration, unless it is paused or has no duration. Run out, it closes the toast; on a closed one that does nothing. */
  #start() {
    clearTimeout(this.#timer);
    this.#timer = undefined;
    const duration = /** @type {number} */ (this.#self.duration);
    if (duration <= 0 || this.#hovered || this.#focused) return;
    this.#timer = setTimeout(() => { this.#self.open = false; }, duration);
  }

  /** Hands --_entering to the recipe for two frames: the first paints the start, the second starts the transition. */
  #enter() {
    this.style.setProperty('--_entering', '1');
    this.#frame = requestAnimationFrame(() => {
      this.#frame = requestAnimationFrame(() => { this.#frame = undefined; this.#entered(); });
    });
  }

  /** Removes --_entering, and the style attribute when nothing else is left in it. */
  #entered() {
    this.style.removeProperty('--_entering');
    if (this.getAttribute('style') === '') this.removeAttribute('style');
  }

  /** @param {string} name */
  changed(name) {
    if (name === 'variant' && this.#live) this.#writeRole();
    if (name !== 'open') return;
    const open = /** @type {boolean} */ (this.#self.open);
    if (open === this.#wasOpen) return;
    this.#wasOpen = open;
    if (open) {
      if (!this.#live) return;
      this.#enter();
      this.#start();
    } else {
      this.dispatchEvent(new Event('close', { bubbles: true }));
    }
  }

  connected() {
    const self = this.#self;
    this.#live = true;
    this.#wasOpen = self.open;
    this.#hovered = this.#focused = false;
    this.#writeRole();

    const pause = () => { clearTimeout(this.#timer); this.#timer = undefined; };
    this.listen(this, 'pointerenter', () => { this.#hovered = true; pause(); });
    this.listen(this, 'pointerleave', () => { this.#hovered = false; this.#start(); });
    this.listen(this, 'focusin', () => { this.#focused = true; pause(); });
    // Focus that moves inside the toast leaves one element and enters another: focusin stops the time again.
    this.listen(this, 'focusout', () => { this.#focused = false; this.#start(); });
    // A press on the close part, by the pointer or by a key that clicks it.
    this.listen(this, 'click', (/** @type {MouseEvent} */ event) => {
      const part = event.target instanceof Element ? event.target.closest(CLOSE) : null;
      if (part && part.closest(this.localName) === this && self.open) self.open = false;
    });
    // Escape while focus is inside. A press outside and focus that leaves close nothing.
    this.use(dismiss, {
      active: () => self.open,
      onDismiss: (/** @type {string} */ reason) => { if (reason === 'escape') self.open = false; },
    });

    // The time and a pending entry live as long as the connection. The effect reads no signal, so it runs once.
    this.effect(() => () => {
      this.#live = false;
      clearTimeout(this.#timer);
      this.#timer = undefined;
      if (this.#frame !== undefined) { cancelAnimationFrame(this.#frame); this.#frame = undefined; this.#entered(); }
    });

    // A toast that connects open for the first time enters; one moved in the document, already shown, does not.
    if (self.open && !this.hasAttribute('data-ready')) this.#enter();
    this.#start();
  }
}
