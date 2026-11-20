// @ts-check
/**
 * popover.class.js: the class of a popover, a non-modal dialog beside the control that opens it. Importing it
 * defines no element; popover.js does that.
 *
 * The root holds two things the author wrote: the content, its child marked data-part="content", and the
 * control, its first other child element, which can be any element that takes focus (J88). The content gets
 * the dialog role unless the author wrote one, an id when it has none, popover="manual" unless the author
 * wrote a popover, and tabindex="-1" unless the author wrote a tabindex, so that it can take focus itself.
 * The control gets aria-haspopup="dialog", aria-expanded in step with `open`, and aria-controls naming the
 * content; a former control loses the three.
 *
 * The content shows in the top layer exactly while the root has `open`, whoever sets it, in the same task as
 * the write; if something else hides the popover, `open` goes. After each change of `open` the root
 * dispatches `toggle`, a ToggleEvent that does not bubble, as the native popover's does. Each change of `open`
 * to true moves focus to the content's first focusable element, or to the content itself (J89); a popover
 * written open shows when it connects and takes no focus, so that two written open do not close each other
 * and the page keeps its focus. The recipe places it (D77).
 *
 * When it opens and closes (J89):
 * - A click on the control opens it, or closes it and returns focus to the control. Enter and Space open and
 *   close it through the click they make on a control that clicks on them: the kit's button, which mounts the
 *   press behaviour, or a native button. This class mounts no press of its own: use() mounts a behaviour on
 *   the root only (B5), the root never has focus, and a second press on the kit's button would click twice.
 * - Escape, through the dismiss behaviour, closes it and returns focus to the control; the Escape goes no
 *   further, so a dialog or a menu around the popover stays open (overlay.escape-innermost).
 * - A press outside the root and focus that leaves the root close it and leave focus where it went. The
 *   content is a descendant of the root, so a press inside it and focus that moves between the content and
 *   the control are not leaving.
 * Nothing else is made inert: the page behind stays operable.
 *
 * It names no tag. Rules: docs/specs/patterns.md, J88 to J91.
 */
import { UIElement } from '../../foundation/element.js';
import { dismiss } from '../../behaviours/dismiss.js';
import { props } from './popover.props.js';

const CONTENT = ':scope > [data-part="content"]';
/** What can take focus inside the content, in document order. */
const FOCUSABLE = 'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';
/** The ARIA this element writes on its control. */
const ARIA = ['aria-haspopup', 'aria-expanded', 'aria-controls'];
/** Whether a child of the root is marked as the content. @param {Element} el */
const isContent = (el) => el.getAttribute('data-part') === 'content';
/** @param {Element} el */
const disabled = (el) => el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true';
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

export class UIPopover extends UIElement {
  static props = props;

  /** @type {HTMLElement | null} The element that last got this element's ARIA. */
  #owned = null;
  /** Whether the last toggle dispatched said open. */
  #reported = false;
  /** Whether connected() has run and the connection holds: before, the upgrade's changed('open') moves no focus. */
  #live = false;

  /** @returns {HTMLElement | null} */
  #content() { return this.querySelector(CONTENT); }

  /** The control: the first child element that is not the content. @returns {HTMLElement | null} */
  #control() {
    return /** @type {HTMLElement | null} */ ([...this.children].find((el) => !isContent(el)) ?? null);
  }

  /** Writes the role, the id, the popover and the tabindex on the content, and the ARIA on the control. */
  #sync() {
    const content = this.#content(), control = this.#control();
    if (content) {
      if (!content.hasAttribute('role')) content.setAttribute('role', 'dialog');
      if (!content.id) content.id = `${this.localName}-${++serial}`;
      if (!content.hasAttribute('popover')) content.setAttribute('popover', 'manual');
      if (!content.hasAttribute('tabindex')) content.setAttribute('tabindex', '-1');
    }
    const before = this.#owned;
    if (before && (before !== control || !content)) {
      for (const name of ARIA) before.removeAttribute(name);
      this.#owned = null;
    }
    if (control && content) {
      put(control, 'aria-haspopup', 'dialog');
      put(control, 'aria-controls', content.id);
      this.#owned = control;
    }
    this.#expanded();
    this.#apply();
  }

  /** Keeps aria-expanded on the control in step with `open`. */
  #expanded() {
    if (this.#owned) put(this.#owned, 'aria-expanded', String(/** @type {any} */ (this).open));
  }

  /**
   * Shows or hides the content so that it is showing exactly while `open` is set, with `focus` moves focus in
   * when it opens, and dispatches `toggle` when the state differs from the last one dispatched. Runs
   * synchronously, so a script that sets `open` finds the popover shown in the same task.
   * @param {boolean} [focus]
   */
  #apply(focus = false) {
    const content = this.#content();
    const open = /** @type {any} */ (this).open;
    // Before connected() has run there is no popover attribute yet, and a removed popover cannot show.
    if (!this.isConnected || !content || !content.hasAttribute('popover')) return;
    if (open !== content.matches(':popover-open')) {
      if (open) {
        content.showPopover();
        // In a microtask, once a property write has set the attribute too, which the recipe displays the content
        // from: an element that is not displayed takes no focus.
        if (focus) queueMicrotask(() => {
          if (/** @type {any} */ (this).open && content.matches(':popover-open')) /** @type {HTMLElement} */ (content.querySelector(FOCUSABLE) ?? content).focus();
        });
      } else content.hidePopover();
    }
    if (open === this.#reported) return;
    this.#reported = open;
    const states = open ? ['closed', 'open'] : ['open', 'closed'];
    this.dispatchEvent(new ToggleEvent('toggle', { oldState: states[0], newState: states[1] }));
  }

  /** Closes the popover, and with `restore` returns focus to the control. @param {boolean} restore */
  #close(restore) {
    /** @type {any} */ (this).open = false;
    if (restore) this.#control()?.focus();
  }

  /** @param {string} name */
  changed(name) {
    if (name !== 'open') return;
    this.#expanded();
    this.#apply(this.#live);
  }

  connected() {
    const self = /** @type {any} */ (this);
    // A click on the control, from the pointer or from a key that clicks it, opens or closes (J89).
    this.listen(this, 'click', (/** @type {MouseEvent} */ event) => {
      const control = this.#control();
      if (!control || !(event.target instanceof Node) || !control.contains(event.target) || disabled(control)) return;
      if (self.open) this.#close(true);
      else self.open = true;
    });
    // Something else hid the popover, such as a script calling hidePopover(): the attribute follows. The
    // content's toggle event does not bubble, so it is caught on its way down.
    this.listen(this, 'toggle', (/** @type {Event} */ event) => {
      const content = this.#content();
      if (event.target === content && self.open && !content?.matches(':popover-open')) self.open = false;
    }, { capture: true });
    // Escape returns focus to the control; a press outside and focus that leaves leave it where it went.
    this.use(dismiss, {
      active: () => self.open,
      onDismiss: (/** @type {string} */ reason) => this.#close(reason === 'escape'),
    });

    // The observer lives as long as the connection: the effect reads no signal, so it runs once, and its
    // cleanup disconnects it.
    this.effect(() => {
      const observer = new MutationObserver(() => this.#sync());
      observer.observe(this, { childList: true, subtree: true, attributes: true, attributeFilter: ['data-part', 'id'] });
      return () => { observer.disconnect(); this.#live = false; };
    });
    this.#sync();
    this.#live = true;
  }
}
