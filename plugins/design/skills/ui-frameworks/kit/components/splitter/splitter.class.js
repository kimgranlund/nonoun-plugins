// @ts-check
/**
 * splitter.class.js: the splitter's class. Importing it defines no element; splitter.js does that.
 *
 * The root is a plain element around two panes the author writes, marked data-part="start" and data-part="end".
 * The class creates the bar at the end of the root; the recipe places it between the panes (J62). The share of
 * the first pane, value held between min and max, and both between 0 and 100, goes to the recipe as the private
 * custom property --_share on the root's own inline style, as the meter hands over its share. That is the one style
 * the class writes.
 *
 * The bar has the separator role and is a Tab stop (J63). Its aria-orientation is across the split: a horizontal
 * splitter, panes side by side, has a vertical bar. The arrow keys along the split move it by one, Home and End to
 * the limits, Enter collapses the first pane to its least share and brings back the share it had. In a right-to-left
 * scope the left and right arrows swap, since the first pane is on the right. A drag follows the pointer, with the
 * pointer captured on the bar. The root dispatches input while the bar moves and change when the user has finished.
 *
 * Rules: docs/specs/patterns.md, J62 and J63.
 */
import { UIElement, setAttr } from '../../foundation/element.js';
import { props, parts, role, tabindex } from './splitter.props.js';

/** The bar's name when the author gave none: messages.bar in splitter.manifest.json. */
const NAME = 'Resize';
/** For the ids this class gives to a first pane that has none. */
let serial = 0;

/** @param {number} n @param {number} lo @param {number} hi */
const clamp = (n, lo, hi) => Math.min(Math.max(n, lo), hi);

export class UISplitter extends UIElement {
  static props = props;
  static parts = parts;
  static role = role;
  static tabindex = tabindex;

  /** The share the first pane had when Enter last collapsed it. @type {number | null} */
  #restore = null;

  /** The limits and the share as they are used: 0 ≤ min ≤ value ≤ max ≤ 100. */
  #range() {
    const self = /** @type {any} */ (this);
    const min = clamp(/** @type {number} */ (self.min), 0, 100);
    const max = clamp(/** @type {number} */ (self.max), min, 100);
    const value = clamp(/** @type {number} */ (self.value), min, max);
    return { min, max, value };
  }

  #vertical() { return /** @type {any} */ (this).orientation === 'vertical'; }

  connected() {
    const bar = () => /** @type {HTMLElement} */ (this.ensurePart('bar'));
    this.effect(() => setAttr(bar(), 'aria-valuemin', String(this.#range().min)));
    this.effect(() => setAttr(bar(), 'aria-valuemax', String(this.#range().max)));
    this.effect(() => setAttr(bar(), 'aria-valuenow', String(this.#range().value)));
    this.effect(() => setAttr(bar(), 'aria-orientation', this.#vertical() ? 'horizontal' : 'vertical'));
    this.effect(() => {
      this.style.setProperty('--_share', String(this.#range().value));
      return () => this.style.removeProperty('--_share');
    });
    // The bar's name, and aria-controls on the first pane, which the author may add or replace later.
    this.effect(() => {
      const name = () => {
        const b = bar();
        if (!b.hasAttribute('aria-label') && !b.hasAttribute('aria-labelledby')) b.setAttribute('aria-label', NAME);
        const start = this.ensurePart('start');
        if (start && !start.id) start.id = `splitter-start-${++serial}`;
        const controls = start ? start.id : null;
        if (b.getAttribute('aria-controls') !== controls) setAttr(b, 'aria-controls', controls);
      };
      name();
      const observer = new MutationObserver(name);
      observer.observe(this, { childList: true });
      return () => observer.disconnect();
    });

    this.listen(this, 'keydown', (/** @type {KeyboardEvent} */ event) => {
      if (event.target !== bar() || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
      const { min, max, value } = this.#range();
      const rtl = getComputedStyle(this).direction === 'rtl';
      const keys = /** @type {Record<string, number>} */ (this.#vertical()
        ? { ArrowUp: -1, ArrowDown: 1 }
        : { ArrowLeft: rtl ? 1 : -1, ArrowRight: rtl ? -1 : 1 });
      let next;
      if (event.key in keys) next = value + keys[event.key];
      else if (event.key === 'Home') next = min;
      else if (event.key === 'End') next = max;
      else if (event.key === 'Enter') {
        if (value > min) { this.#restore = value; next = min; }
        else if (this.#restore !== null) next = this.#restore;
        else return;
      } else return;
      event.preventDefault();
      if (this.#move(next)) this.emit('change');
    });

    /** The drag in progress: the pointer, where it held the bar, and the share it started from. */
    let drag = /** @type {{ id: number, grip: number, from: number } | null} */ (null);
    this.listen(this, 'pointerdown', (/** @type {PointerEvent} */ event) => {
      const b = bar();
      if (event.target !== b || event.button !== 0) return;
      // WebKit selects the text a captured drag passes over unless the press is cancelled; Chromium and Firefox do not.
      event.preventDefault();
      b.focus({ preventScroll: true });
      const r = b.getBoundingClientRect();
      drag = { id: event.pointerId, grip: this.#along(event, r), from: this.#range().value };
      b.setPointerCapture(event.pointerId);
    });
    this.listen(this, 'pointermove', (/** @type {PointerEvent} */ event) => {
      if (!drag || event.pointerId !== drag.id) return;
      const room = this.#room();
      if (room.length <= 0) return;
      const at = this.#along(event, room.rect, room) - drag.grip;
      this.#move((at / room.length) * 100);
    });
    const end = (/** @type {PointerEvent} */ event) => {
      if (!drag || event.pointerId !== drag.id) return;
      const moved = this.#range().value !== drag.from;
      drag = null;
      if (moved) this.emit('change');
    };
    // The capture ends when the pointer is released or cancelled, and when the bar leaves the document.
    this.listen(this, 'lostpointercapture', end);
  }

  /**
   * The room the two panes share, along the split: the root's content box less the bar.
   * @returns {{ rect: DOMRect, start: number, length: number }}
   */
  #room() {
    const rect = this.getBoundingClientRect();
    const s = getComputedStyle(this);
    const vertical = this.#vertical();
    const bar = /** @type {HTMLElement} */ (this.ensurePart('bar')).getBoundingClientRect();
    const px = (/** @type {string} */ name) => parseFloat(s.getPropertyValue(name)) || 0;
    const rtl = s.direction === 'rtl';
    const padStart = vertical ? px('padding-top') + px('border-top-width') : px(rtl ? 'padding-right' : 'padding-left') + px(rtl ? 'border-right-width' : 'border-left-width');
    const content = vertical
      ? rect.height - px('padding-top') - px('padding-bottom') - px('border-top-width') - px('border-bottom-width')
      : rect.width - px('padding-left') - px('padding-right') - px('border-left-width') - px('border-right-width');
    return { rect, start: padStart, length: content - (vertical ? bar.height : bar.width) };
  }

  /**
   * How far a pointer is along the split from the start edge of a box: from the top, from the left, or from the
   * right in a right-to-left scope.
   * @param {PointerEvent} event @param {DOMRect} rect @param {{ start: number }} [room] The root's room, to count from its content box.
   */
  #along(event, rect, room) {
    const offset = room ? room.start : 0;
    if (this.#vertical()) return event.clientY - rect.top - offset;
    return getComputedStyle(this).direction === 'rtl' ? rect.right - event.clientX - offset : event.clientX - rect.left - offset;
  }

  /** Moves the bar to a share, rounded to hundredths and held inside the limits, and dispatches input when it moved. @param {number} share @returns {boolean} */
  #move(share) {
    const { min, max, value } = this.#range();
    const next = clamp(Math.round(share * 100) / 100, min, max);
    if (next === value) return false;
    /** @type {any} */ (this).value = next;
    this.emit('input');
    return true;
  }
}
