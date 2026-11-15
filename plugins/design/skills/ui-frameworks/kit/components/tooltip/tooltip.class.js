// @ts-check
/**
 * tooltip.class.js: the class of a tooltip, a short description shown beside the element it describes.
 * Importing it defines no element; tooltip.js does that.
 *
 * The root holds two things the author wrote: the content, its child marked data-part="content", and the
 * subject, its first other child element. The content gets the tooltip role, an id when it has none and
 * popover="manual"; the subject names the content in aria-describedby unless the author wrote that attribute
 * (J36). The class remembers the values it wrote, so that it updates its own and never the author's.
 *
 * The content shows in the top layer exactly while the root has `open`, whoever sets it, in the same task as
 * the write (J37); if something else hides the popover, `open` goes. The recipe places it (D77).
 *
 * When it opens and closes (J37):
 * - The pointer: resting on the root for `delay` milliseconds opens it; leaving the root closes it after
 *   `closeDelay` milliseconds, which a return of the pointer to the root, or to the content, cancels. The
 *   content is a descendant of the root, so moving onto it is not leaving; the close delay covers the gap
 *   between the subject and the content, which belongs to neither. A touch pointer opens nothing.
 * - The keyboard: focus on the subject that matches :focus-visible opens it at once; focus that leaves the
 *   subject closes it.
 * - Escape, through the dismiss behaviour, closes it and leaves focus where it is; the Escape goes no
 *   further, so a menu or a dialog around the tooltip stays open (overlay.escape-innermost).
 * - A press on the subject closes it: the user has acted.
 *
 * `delay` and `closeDelay` are static fields read from the element's own class, so a subclass, or a test,
 * can set them: `class extends UITooltip { static delay = 50 }`.
 *
 * It names no tag. Rules: docs/specs/patterns.md, J36 to J38.
 */
import { UIElement } from '../../foundation/element.js';
import { dismiss } from '../../behaviours/dismiss.js';
import { props } from './tooltip.props.js';

const CONTENT = ':scope > [data-part="content"]';
/** Whether a child of the root is marked as the content. @param {Element} el */
const isContent = (el) => el.getAttribute('data-part') === 'content';
/** For the ids this class gives to a content that has none. */
let serial = 0;

/**
 * Sets or removes an attribute, only when it differs. The observer then sees nothing when nothing changes.
 * @param {Element} el @param {string} name @param {string | null} value
 */
const put = (el, name, value) => {
  if (el.getAttribute(name) === value) return;
  if (value === null) el.removeAttribute(name);
  else el.setAttribute(name, value);
};

export class UITooltip extends UIElement {
  static props = props;

  /** Milliseconds the pointer rests on the tooltip before it opens. */
  static delay = 500;
  /** Milliseconds between the pointer leaving the tooltip and the tooltip closing. */
  static closeDelay = 100;

  /** @type {WeakMap<Element, string>} The aria-describedby values this element wrote, so that it never replaces an author's. */
  #described = new WeakMap();
  /** @type {Element | null} The subject that last got this element's aria-describedby. */
  #subject = null;
  /** @type {ReturnType<typeof setTimeout> | undefined} */
  #opening;
  /** @type {ReturnType<typeof setTimeout> | undefined} */
  #closing;

  /** @returns {HTMLElement | null} */
  #content() { return this.querySelector(CONTENT); }

  /** The element it describes: its first child element that is not the content. @returns {HTMLElement | null} */
  #describes() {
    return /** @type {HTMLElement | null} */ ([...this.children].find((el) => !isContent(el)) ?? null);
  }

  get #ctor() { return /** @type {typeof UITooltip} */ (this.constructor); }

  /** Cancels a pending open and a pending close. */
  #stop() {
    clearTimeout(this.#opening);
    clearTimeout(this.#closing);
    this.#opening = this.#closing = undefined;
  }

  /** @param {boolean} open */
  #set(open) {
    this.#stop();
    /** @type {any} */ (this).open = open;
  }

  /** Writes the role, the id and the popover on the content, and aria-describedby on the subject. */
  #sync() {
    const content = this.#content(), subject = this.#describes();
    if (content) {
      if (!content.hasAttribute('role')) content.setAttribute('role', 'tooltip');
      if (!content.id) content.id = `${this.localName}-${++serial}`;
      if (!content.hasAttribute('popover')) content.setAttribute('popover', 'manual');
    }
    // A subject this element described, that no longer is the subject or has nothing to name, loses the value
    // this element wrote; a value the author wrote since stays.
    const before = this.#subject;
    if (before && (before !== subject || !content)) {
      if (before.getAttribute('aria-describedby') === this.#described.get(before)) before.removeAttribute('aria-describedby');
      this.#described.delete(before);
      this.#subject = null;
    }
    if (subject && content) {
      const value = subject.getAttribute('aria-describedby');
      if (value === null || value === this.#described.get(subject)) {
        put(subject, 'aria-describedby', content.id);
        this.#described.set(subject, content.id);
        this.#subject = subject;
      }
    }
    this.#apply();
  }

  /**
   * Shows or hides the content so that it is showing exactly while `open` is set. Runs synchronously, so a
   * script that sets `open` finds the tooltip shown in the same task.
   */
  #apply() {
    const content = this.#content();
    const open = /** @type {any} */ (this).open;
    // Before connected() has run there is no popover attribute yet, and a removed tooltip cannot show.
    if (!this.isConnected || !content || !content.hasAttribute('popover') || open === content.matches(':popover-open')) return;
    if (open) content.showPopover();
    else content.hidePopover();
  }

  /** @param {string} name */
  changed(name) {
    if (name === 'open') this.#apply();
  }

  connected() {
    const self = /** @type {any} */ (this);
    /** @param {EventTarget | null} node */
    const onSubject = (node) => node instanceof Node && !!this.#describes()?.contains(node);

    // The pointer. Entering the root, the content included, cancels a pending close and starts the delay.
    this.listen(this, 'pointerenter', (/** @type {PointerEvent} */ event) => {
      if (event.pointerType === 'touch') return;
      clearTimeout(this.#closing);
      this.#closing = undefined;
      if (self.open || this.#opening !== undefined) return;
      this.#opening = setTimeout(() => this.#set(true), this.#ctor.delay);
    });
    this.listen(this, 'pointerleave', (/** @type {PointerEvent} */ event) => {
      if (event.pointerType === 'touch') return;
      clearTimeout(this.#opening);
      this.#opening = undefined;
      if (!self.open || this.#closing !== undefined) return;
      this.#closing = setTimeout(() => this.#set(false), this.#ctor.closeDelay);
    });
    // The keyboard: focus that the browser would show opens at once, and focus that leaves the subject closes.
    this.listen(this, 'focusin', (/** @type {FocusEvent} */ event) => {
      if (onSubject(event.target) && /** @type {Element} */ (event.target).matches(':focus-visible')) this.#set(true);
    });
    this.listen(this, 'focusout', (/** @type {FocusEvent} */ event) => {
      if (onSubject(event.target) && !onSubject(event.relatedTarget)) this.#set(false);
    });
    // A press on the subject, by the pointer or by a key that clicks it, is the user acting: it closes.
    this.listen(this, 'pointerdown', (/** @type {PointerEvent} */ event) => { if (onSubject(event.target)) this.#set(false); });
    this.listen(this, 'click', (/** @type {MouseEvent} */ event) => { if (onSubject(event.target)) this.#set(false); });
    // Something else hid the popover, such as a script calling hidePopover(): the attribute follows. The
    // toggle event does not bubble, so it is caught on its way down.
    this.listen(this, 'toggle', (/** @type {Event} */ event) => {
      if (event.target === this.#content() && self.open && !this.#content()?.matches(':popover-open')) this.#set(false);
    }, { capture: true });
    // Escape closes and leaves focus alone. A press outside and focus that leaves are the pointer's and the
    // focus rules' to answer, so those reasons are ignored.
    this.use(dismiss, {
      active: () => self.open,
      onDismiss: (/** @type {string} */ reason) => { if (reason === 'escape') this.#set(false); },
    });

    // The observer and the timers live as long as the connection: the effect reads no signal, so it runs
    // once, and its cleanup disconnects the observer and cancels a pending open or close.
    this.effect(() => {
      const observer = new MutationObserver(() => this.#sync());
      observer.observe(this, { childList: true, subtree: true, attributes: true, attributeFilter: ['data-part', 'id'] });
      return () => { observer.disconnect(); this.#stop(); };
    });
    this.#sync();
  }
}
