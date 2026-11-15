// @ts-check
/**
 * carousel.class.js: the class of the carousel, a row of slides of which one shows at a time. Importing it
 * defines no element; carousel.js does that.
 *
 * The root has the region role and the role description "carousel". Every element it works with is the
 * author's: the element marked data-part="slides", whose child elements are the slides, and the buttons marked
 * data-part="previous" and data-part="next". It names none of them by tag.
 *
 * The view is the slides part's own scrolling, with scroll snap from the recipe. `value` is the slide that
 * shows. It follows the user's scrolling once the scroll comes to rest, read from where the slides are; and a
 * script that sets it scrolls the view, smoothly or at once as the recipe and the user's motion setting say.
 * The slides that do not show are inert. Nothing moves by itself.
 *
 * Rules: docs/specs/patterns.md, J74, J75 and J78.
 */
import { UIElement } from '../../foundation/element.js';
import { props, role } from './carousel.props.js';

/** The words of the carousel: messages in carousel.manifest.json. */
const ROLEDESCRIPTION = 'carousel';
const SLIDE = 'slide';
const OF = 'of';
/** For the ids this class gives to a slides part that has none. */
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

export class UICarousel extends UIElement {
  static props = props;
  static role = role;

  /** @type {WeakMap<Element, string>} The aria-label values this element wrote, so that it never replaces an author's. */
  #named = new WeakMap();
  /** The slides as the observer last saw them, so that it scrolls only when they change. @type {Element[]} */
  #seen = [];

  /**
   * The elements that match, and belong to this element rather than to a carousel nested inside it.
   * @param {string} selector @returns {HTMLElement[]}
   */
  #own(selector) {
    return /** @type {HTMLElement[]} */ ([...this.querySelectorAll(selector)].filter((el) => el.closest(this.localName) === this));
  }

  /** The element that scrolls: the first one marked data-part="slides". */
  #view() { return this.#own('[data-part="slides"]')[0] ?? null; }

  /** The slides: the child elements of the view. */
  #slides() { return /** @type {HTMLElement[]} */ ([...(this.#view()?.children ?? [])]); }

  /**
   * The slide nearest the view's left edge: the one that shows. Each slide is as wide as the view (J76), so its
   * left edge says as much as its start edge, in either direction.
   */
  #nearest() {
    const view = this.#view();
    if (!view) return 0;
    const left = view.getBoundingClientRect().left;
    let best = 0, distance = Infinity;
    this.#slides().forEach((slide, i) => {
      const d = Math.abs(slide.getBoundingClientRect().left - left);
      if (d < distance) { best = i; distance = d; }
    });
    return best;
  }

  /** Scrolls the view so that the slide of `value` shows, unless it already does. */
  #show() {
    const self = /** @type {any} */ (this);
    const view = this.#view(), slide = this.#slides()[self.value];
    if (!view || !slide || this.#nearest() === self.value) return;
    // No behaviour is named, so the recipe's scroll-behavior decides: smooth, or at once under reduced motion.
    // The view snaps to the slide's edge from wherever this lands.
    view.scrollTo({ left: view.scrollLeft + slide.getBoundingClientRect().left - view.getBoundingClientRect().left });
  }

  /** Brings the slides, the buttons and the root in step with `value`. Writes nothing when they already are. */
  #sync() {
    const self = /** @type {any} */ (this);
    const view = this.#view(), slides = this.#slides();
    if (!this.hasAttribute('aria-roledescription')) this.setAttribute('aria-roledescription', ROLEDESCRIPTION);
    // The slides are a polite live region, so that a slide the user brings into view is announced (J78). The
    // author's aria-live, such as "off" while the author rotates the slides, is kept.
    if (view && !view.hasAttribute('aria-live')) view.setAttribute('aria-live', 'polite');
    if (!view || !slides.length) return;
    // A value that names no slide shows the nearest one that exists.
    const index = Math.min(Math.max(Math.round(self.value), 0), slides.length - 1);
    if (index !== self.value) { self.value = index; return; } // changed() has run this again with the value in place.
    if (!view.id) view.id = `${this.localName}-${++serial}`;
    slides.forEach((slide, i) => {
      if (!slide.hasAttribute('role')) slide.setAttribute('role', 'group');
      if (!slide.hasAttribute('aria-roledescription')) slide.setAttribute('aria-roledescription', SLIDE);
      // A slide the author named keeps its name (A2). One this element named follows its position.
      const label = slide.getAttribute('aria-label');
      if (!slide.hasAttribute('aria-labelledby') && (label === null || label === this.#named.get(slide))) {
        const name = `${i + 1} ${OF} ${slides.length}`;
        put(slide, 'aria-label', name);
        this.#named.set(slide, name);
      }
      put(slide, 'inert', i === index ? null : '');
    });
    for (const [part, end] of /** @type {const} */ ([['previous', 0], ['next', slides.length - 1]])) {
      for (const button of this.#own(`[data-part="${part}"]`)) {
        put(button, 'aria-controls', view.id);
        // A button the author disabled stays as the author left it.
        if (!button.hasAttribute('disabled')) put(button, 'aria-disabled', index === end ? 'true' : null);
      }
    }
  }

  /**
   * Goes to another slide because the user asked for it.
   * @param {number} index
   */
  #go(index) {
    const self = /** @type {any} */ (this);
    const before = self.value;
    self.value = index; // changed() brings everything up to date, and scrolls, before this returns.
    if (self.value !== before) this.dispatchEvent(new Event('change', { bubbles: true }));
  }

  /** The view has come to rest: the slide that shows is now the value. */
  #settle() {
    const index = this.#nearest();
    if (index !== /** @type {any} */ (this).value) this.#go(index);
  }

  /** @param {string} name */
  changed(name) {
    if (name !== 'value' || !this.isConnected) return;
    this.#sync();
    this.#show();
  }

  connected() {
    const self = /** @type {any} */ (this);
    // The next and the previous button: a click, and so Enter and Space on a button.
    this.listen(this, 'click', (event) => {
      const button = event.target instanceof Element ? event.target.closest('[data-part="previous"], [data-part="next"]') : null;
      if (!button || button.closest(this.localName) !== this) return;
      if (!this.#slides().length) return;
      this.#go(self.value + (button.getAttribute('data-part') === 'next' ? 1 : -1));
    });

    // The view has come to rest, after the user's scrolling or after a scroll this element started. Scroll
    // events do not bubble, so this one is caught on the way down. Another scroller inside comes to rest too,
    // and then the view's position, and so the value, is what it was.
    this.listen(this, 'scrollend', () => this.#settle(), { capture: true });

    // The observer lives as long as the connection: the effect reads no signal, so it runs once, and its
    // cleanup disconnects.
    this.effect(() => {
      const observer = new MutationObserver(() => {
        this.#sync();
        // Slides that arrived or left: show the value's slide. Any other change, such as content inside a slide,
        // leaves the view alone, even in the middle of the user's scrolling.
        const slides = this.#slides();
        if (slides.length === this.#seen.length && slides.every((slide, i) => slide === this.#seen[i])) return;
        this.#seen = slides;
        this.#show();
      });
      observer.observe(this, { childList: true, subtree: true, attributes: true, attributeFilter: ['data-part', 'role', 'aria-label', 'aria-labelledby', 'aria-disabled', 'disabled'] });
      return () => observer.disconnect();
    });
    this.#seen = this.#slides();
    this.#sync();
    this.#show();
  }
}
