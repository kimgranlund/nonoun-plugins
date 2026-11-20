// @ts-check
/**
 * carousel.js: a carousel, a row of slides of which one shows at a time, for React (docs/specs/targets.md; rules
 * J74 to J76 and J78 of docs/specs/patterns.md).
 *
 * The root is a <div role="region" aria-roledescription="carousel">: no native element is a carousel. Both are
 * rendered, so they are in the server markup; a role or a role description the author passes wins, as on the Web
 * Component. Every other element it works with is the author's child, never cloned or wrapped: the element marked
 * `data-part="slides"`, whose child elements are the slides, and the buttons marked `data-part="previous"` and
 * `data-part="next"`, of any family (the kit's Button among them, which renders none of the attributes below).
 * It finds them in the DOM, as the Web Component does, and writes, only where they differ, after each render and
 * on each change in its subtree: `aria-live="polite"` on the slides part unless the author wrote one (J78), an id
 * on it when it has none, on each slide the group role, the role description "slide", a name that gives its
 * position unless the author named it, and `inert` on each slide that does not show (J74); on each button
 * `aria-controls`, and `aria-disabled` at its end unless the author disabled it (J75). A part of a carousel
 * nested in a slide is that carousel's.
 *
 * The view is the slides part's own scrolling, with scroll snap from the recipe. The slide that shows is
 * controlled (value with onChange) or uncontrolled (defaultValue, or the manifest's 0). A value that names no
 * slide shows the nearest one that exists; uncontrolled, the value then becomes that one, as the Web Component's
 * does. A value that changes scrolls the view to its slide, smoothly or at once as the recipe and the user's
 * motion setting say. A click on a button, and so Enter and Space on it, goes to the next or the previous slide;
 * when the view comes to rest after the user's scrolling, the slide nearest its start is the value. Each calls
 * onChange(value, event) once, with the click or the scrollend event, after the slides, the buttons and the view
 * are up to date when the value is uncontrolled. It is not called when the value prop changes. Nothing moves by
 * itself.
 */
import { createElement, useCallback, useEffect, useId, useLayoutEffect, useRef, useState } from 'react';
import { flushSync } from 'react-dom';
import { props as spec, role } from '../../components/carousel/carousel.props.js';

/**
 * @typedef {Omit<import('react').HTMLAttributes<HTMLDivElement>, 'onChange' | 'defaultValue'> & {
 *   value?: number, defaultValue?: number,
 *   onChange?: (value: number, event: import('react').SyntheticEvent | Event) => void,
 *   ref?: import('react').Ref<HTMLDivElement>,
 * }} CarouselProps
 */

/** The words of the carousel: messages in carousel.manifest.json. */
const ROLEDESCRIPTION = 'carousel';
const SLIDE = 'slide';
const OF = 'of';
const ROOT = '[data-ui="carousel"]';

/**
 * Sets or removes an attribute, only when it differs. The observer then sees nothing when nothing changes.
 * @param {Element} el @param {string} name @param {string | null} value
 */
const put = (el, name, value) => {
  if (el.getAttribute(name) === value) return;
  if (value === null) el.removeAttribute(name);
  else el.setAttribute(name, value);
};

/**
 * The elements that match, and belong to this carousel rather than to one nested inside it.
 * @param {HTMLElement} root @param {string} selector @returns {HTMLElement[]}
 */
const own = (root, selector) => /** @type {HTMLElement[]} */ ([...root.querySelectorAll(selector)].filter((el) => el.closest(ROOT) === root));
/** The element that scrolls: the first one marked data-part="slides". @param {HTMLElement} root */
const viewOf = (root) => own(root, '[data-part="slides"]')[0] ?? null;
/** The slides: the child elements of the view. @param {HTMLElement} root */
const slidesOf = (root) => /** @type {HTMLElement[]} */ ([...(viewOf(root)?.children ?? [])]);

/**
 * The slide nearest the view's left edge: the one that shows. Each slide is as wide as the view (J76), so its left
 * edge says as much as its start edge, in either direction.
 * @param {HTMLElement} root
 */
const nearest = (root) => {
  const view = viewOf(root);
  if (!view) return 0;
  const left = view.getBoundingClientRect().left;
  let best = 0, distance = Infinity;
  slidesOf(root).forEach((slide, i) => {
    const d = Math.abs(slide.getBoundingClientRect().left - left);
    if (d < distance) { best = i; distance = d; }
  });
  return best;
};

/** The slide a value shows: the nearest that exists, or the value itself while there are none. @param {number} value @param {number} count */
const clamp = (value, count) => (count ? Math.min(Math.max(Math.round(value), 0), count - 1) : value);

/** @param {CarouselProps} props */
function CarouselRoot({ value, defaultValue, onChange, onClick, children, ref, ...rest }) {
  const initial = /** @type {number} */ ((/** @type {{ default: number }} */ (spec.value)).default);
  const [ownValue, setOwn] = useState(() => (typeof defaultValue === 'number' && Number.isFinite(defaultValue) ? defaultValue : initial));
  const controlled = value !== undefined;
  const current = controlled ? value : ownValue;
  const base = useId();
  /** @type {import('react').RefObject<HTMLDivElement | null>} */
  const root = useRef(null);
  const setRef = useCallback((/** @type {HTMLDivElement | null} */ node) => {
    root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);
  const latest = useRef({ current, controlled, onChange });
  latest.current = { current, controlled, onChange };
  /** @type {import('react').RefObject<WeakMap<Element, string>>} The aria-label values this carousel wrote, so that it never replaces an author's. */
  const named = useRef(new WeakMap());

  /** The slide that shows now, for the slides as they are. */
  const index = useCallback(() => {
    const el = root.current;
    return el ? clamp(latest.current.current, slidesOf(el).length) : latest.current.current;
  }, []);

  /**
   * Brings the slides and the buttons in step with the value. Writes nothing when they already are. The observer
   * passes the root it watches.
   * @param {HTMLElement | null} [el]
   */
  const sync = useCallback((el = root.current) => {
    if (!el) return;
    const view = viewOf(el), slides = slidesOf(el);
    // The slides are a polite live region, so that a slide the user brings into view is announced (J78). The
    // author's aria-live, such as "off" while the author rotates the slides, is kept.
    if (view && !view.hasAttribute('aria-live')) view.setAttribute('aria-live', 'polite');
    if (!view || !slides.length) return;
    const at = clamp(latest.current.current, slides.length);
    // A value that names no slide shows the nearest one; uncontrolled, it becomes that one.
    if (at !== latest.current.current && !latest.current.controlled) setOwn(at);
    if (!view.id) view.id = `${base}slides`;
    slides.forEach((slide, i) => {
      if (!slide.hasAttribute('role')) slide.setAttribute('role', 'group');
      if (!slide.hasAttribute('aria-roledescription')) slide.setAttribute('aria-roledescription', SLIDE);
      // A slide the author named keeps its name (A2). One this carousel named follows its position.
      const label = slide.getAttribute('aria-label');
      if (!slide.hasAttribute('aria-labelledby') && (label === null || label === named.current.get(slide))) {
        const name = `${i + 1} ${OF} ${slides.length}`;
        put(slide, 'aria-label', name);
        named.current.set(slide, name);
      }
      put(slide, 'inert', i === at ? null : '');
    });
    for (const [part, end] of /** @type {const} */ ([['previous', 0], ['next', slides.length - 1]])) {
      for (const button of own(el, `[data-part="${part}"]`)) {
        put(button, 'aria-controls', view.id);
        // A button the author disabled stays as the author left it.
        if (!button.hasAttribute('disabled')) put(button, 'aria-disabled', at === end ? 'true' : null);
      }
    }
  }, [base]);

  /** Scrolls the view so that the value's slide shows, unless it already does. */
  const show = useCallback(() => {
    const el = root.current;
    if (!el) return;
    const view = viewOf(el), slide = slidesOf(el)[index()];
    if (!view || !slide || nearest(el) === index()) return;
    // No behaviour is named, so the recipe's scroll-behavior decides: smooth, or at once under reduced motion.
    view.scrollTo({ left: view.scrollLeft + slide.getBoundingClientRect().left - view.getBoundingClientRect().left });
  }, [index]);

  /**
   * Goes to another slide because the user asked for it.
   * @param {number} next @param {import('react').SyntheticEvent | Event} event
   */
  const go = useCallback((/** @type {number} */ next, /** @type {import('react').SyntheticEvent | Event} */ event) => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    const to = clamp(next, slidesOf(el).length);
    if (to === index()) return;
    const now = latest.current;
    // The slides, the buttons and the view are brought up to date before onChange is called (J75).
    if (!now.controlled) flushSync(() => setOwn(to));
    now.onChange?.(to, event);
  }, [index]);

  useLayoutEffect(() => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    /** @type {Element[]} The slides as the observer last saw them, so that it scrolls only when they change. */
    let seen = slidesOf(el);
    const off = new AbortController();
    // The view has come to rest, after the user's scrolling or after a scroll this carousel started. Scroll events
    // do not bubble, and React's onScrollEnd is the view's own, so this one is caught on the way down.
    el.addEventListener('scrollend', (event) => {
      const at = nearest(el);
      if (at !== index()) go(at, event);
    }, { capture: true, signal: off.signal });
    const observer = new MutationObserver(() => {
      sync(el);
      // Slides that arrived or left: show the value's slide. Any other change, such as content inside a slide,
      // leaves the view alone, even in the middle of the user's scrolling.
      const slides = slidesOf(el);
      if (slides.length === seen.length && slides.every((slide, i) => slide === seen[i])) return;
      seen = slides;
      show();
    });
    observer.observe(el, { childList: true, subtree: true, attributes: true, attributeFilter: ['data-part', 'role', 'aria-label', 'aria-labelledby', 'aria-disabled', 'disabled'] });
    return () => { off.abort(); observer.disconnect(); };
  }, [sync, show, go, index]);
  // After each render the author's parts may have changed; when the value changed, the view goes to its slide.
  useLayoutEffect(() => sync());
  useLayoutEffect(show, [current, show]);
  useEffect(() => {
    const id = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(id);
  }, []);

  /** The next and the previous button: a click, and so Enter and Space on a button. @param {import('react').MouseEvent<HTMLDivElement>} event */
  const click = (event) => {
    onClick?.(event);
    const el = /** @type {HTMLDivElement} */ (root.current);
    const button = event.target instanceof Element ? event.target.closest('[data-part="previous"], [data-part="next"]') : null;
    if (!button || button.closest(ROOT) !== el || !slidesOf(el).length) return;
    go(index() + (button.getAttribute('data-part') === 'next' ? 1 : -1), event);
  };

  return createElement('div', /** @type {any} */ ({ role, 'aria-roledescription': ROLEDESCRIPTION, ...rest, ref: setRef, 'data-ui': 'carousel', onClick: click }), children);
}
// Marked pure, so a bundle that does not use the component drops the module (X6).
export const Carousel = /* @__PURE__ */ Object.assign(CarouselRoot, { kitRole: role, displayName: 'Carousel' });
