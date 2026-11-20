<script lang="ts">
  // carousel.svelte: a carousel, a row of slides of which one shows at a time, for Svelte (docs/specs/targets.md, V1
  // to V7; rules J74 to J76 and J78 of docs/specs/patterns.md).
  //
  // The root is a <div role="region" aria-roledescription="carousel">: no native element is a carousel. Both are
  // rendered, so they are in the server markup; a role or a role description the author passes wins, as on the Web
  // Component and the React carousel. Every other element it works with is the author's child, never cloned or
  // wrapped: the element marked `data-part="slides"`, whose child elements are the slides, and the buttons marked
  // `data-part="previous"` and `data-part="next"`, of any family (the kit's Button among them, which renders none of
  // the attributes below). It finds them in the DOM, as the Web Component does, and writes, only where they differ,
  // in an effect after mount, whenever the value changes, and on each change in its subtree: `aria-live="polite"` on
  // the slides part unless the author wrote one (J78), an id on it when it has none (from $props.id()), on each slide
  // the group role, the role description "slide", a name that gives its position unless the author named it, and
  // `inert` on each slide that does not show (J74); on each button `aria-controls`, and `aria-disabled` at its end
  // unless the author disabled it (J75). A part of a carousel nested in a slide is that carousel's. None of it is in
  // the server markup: the parts are the author's children.
  //
  // The view is the slides part's own scrolling, with scroll snap from the recipe. `value` is $bindable: `bind:value`
  // holds it, a plain `value` only starts it, and with neither it is the manifest's 0. A value that names no slide
  // shows the nearest one that exists, and the value becomes that one, as the Web Component's does. A value that
  // changes scrolls the view to its slide, smoothly or at once as the recipe and the user's motion setting say. A
  // click on a button, and so Enter and Space on it, goes to the next or the previous slide; when the view comes to
  // rest after the user's scrolling, the slide nearest its start is the value. Each writes the value and, once the
  // slides, the buttons and the view are up to date, calls onchange(value, event) once, with the click or the
  // scrollend event. A function binding whose setter keeps the value leaves the slide where it is, and onchange is
  // still called: the owner moves the slide by changing the value. It is not called when the value prop changes.
  // Nothing moves by itself. The click is a native listener, so an onclick the author gives the root still runs.
  import { flushSync, untrack, type Snippet } from 'svelte';
  import type { HTMLAttributes } from 'svelte/elements';
  import { props as spec, role } from '../../components/carousel/carousel.props.js';

  type Props = Omit<HTMLAttributes<HTMLDivElement>, 'children' | 'onchange'> & {
    /** Which slide shows, counted from 0: `bind:value` controls it, a plain `value` only starts it. */
    value?: number;
    /** The user went to another slide. */
    onchange?: (value: number, event: Event) => void;
    /** The root, for `bind:ref`. */
    ref?: HTMLDivElement | null;
    children?: Snippet;
  };

  const initial = (spec.value as { default: number }).default;
  let { value = $bindable(initial), onchange, ref = $bindable(null), children, ...rest }: Props = $props();
  const uid = $props.id();

  /** The words of the carousel: messages in carousel.manifest.json. */
  const ROLEDESCRIPTION = 'carousel';
  const SLIDE = 'slide';
  const OF = 'of';
  const ROOT = '[data-ui="carousel"]';

  /** Sets or removes an attribute, only when it differs. The observer then sees nothing when nothing changes. */
  const put = (el: Element, name: string, next: string | null) => {
    if (el.getAttribute(name) === next) return;
    if (next === null) el.removeAttribute(name);
    else el.setAttribute(name, next);
  };

  /** The elements that match, and belong to this carousel rather than to one nested inside it. */
  const own = (root: HTMLElement, selector: string) => [...root.querySelectorAll<HTMLElement>(selector)].filter((el) => el.closest(ROOT) === root);
  /** The element that scrolls: the first one marked data-part="slides". */
  const viewOf = (root: HTMLElement) => own(root, '[data-part="slides"]')[0] ?? null;
  /** The slides: the child elements of the view. */
  const slidesOf = (root: HTMLElement) => [...(viewOf(root)?.children ?? [])] as HTMLElement[];

  /**
   * The slide nearest the view's left edge: the one that shows. Each slide is as wide as the view (J76), so its
   * left edge says as much as its start edge, in either direction.
   */
  const nearest = (root: HTMLElement) => {
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

  /** The slide a value shows: the nearest that exists, or the value itself while there are none. */
  const clamp = (v: number, count: number) => (count ? Math.min(Math.max(Math.round(v), 0), count - 1) : v);
  /** The value as given, or the manifest's when it is no number. */
  const current = () => (typeof value === 'number' && Number.isFinite(value) ? value : initial);
  /** The slide that shows now, for the slides as they are. */
  const index = (el: HTMLElement) => clamp(current(), slidesOf(el).length);

  /** The aria-label values this carousel wrote, so that it never replaces an author's. */
  const named = new WeakMap<Element, string>();

  /** Brings the slides and the buttons in step with the value. Writes nothing when they already are. */
  const sync = (el: HTMLElement) => {
    const view = viewOf(el), slides = slidesOf(el);
    // The slides are a polite live region, so that a slide the user brings into view is announced (J78). The
    // author's aria-live, such as "off" while the author rotates the slides, is kept.
    if (view && !view.hasAttribute('aria-live')) view.setAttribute('aria-live', 'polite');
    if (!view || !slides.length) return;
    const at = clamp(current(), slides.length);
    // A value that names no slide shows the nearest one, and becomes that one.
    if (at !== current()) value = at;
    if (!view.id) view.id = `${uid}-slides`;
    slides.forEach((slide, i) => {
      if (!slide.hasAttribute('role')) slide.setAttribute('role', 'group');
      if (!slide.hasAttribute('aria-roledescription')) slide.setAttribute('aria-roledescription', SLIDE);
      // A slide the author named keeps its name (A2). One this carousel named follows its position.
      const label = slide.getAttribute('aria-label');
      if (!slide.hasAttribute('aria-labelledby') && (label === null || label === named.get(slide))) {
        const name = `${i + 1} ${OF} ${slides.length}`;
        put(slide, 'aria-label', name);
        named.set(slide, name);
      }
      put(slide, 'inert', i === at ? null : '');
    });
    for (const [part, end] of [['previous', 0], ['next', slides.length - 1]] as const) {
      for (const button of own(el, `[data-part="${part}"]`)) {
        put(button, 'aria-controls', view.id);
        // A button the author disabled stays as the author left it.
        if (!button.hasAttribute('disabled')) put(button, 'aria-disabled', at === end ? 'true' : null);
      }
    }
  };

  /** Scrolls the view so that the value's slide shows, unless it already does. */
  const show = (el: HTMLElement) => {
    const view = viewOf(el), slide = slidesOf(el)[index(el)];
    if (!view || !slide || nearest(el) === index(el)) return;
    // No behaviour is named, so the recipe's scroll-behavior decides: smooth, or at once under reduced motion.
    view.scrollTo({ left: view.scrollLeft + slide.getBoundingClientRect().left - view.getBoundingClientRect().left });
  };

  /** Goes to another slide because the user asked for it. */
  const go = (el: HTMLElement, next: number, event: Event) => {
    const to = clamp(next, slidesOf(el).length);
    if (to === index(el)) return;
    value = to;
    // The slides, the buttons and the view are brought up to date before onchange is called (J75).
    flushSync();
    onchange?.(to, event);
  };

  const setup = (el: HTMLDivElement) => {
    /** The slides as the observer last saw them, so that it scrolls only when they change. */
    let seen: Element[] = slidesOf(el);
    const off = new AbortController();
    // The view has come to rest, after the user's scrolling or after a scroll this carousel started. Scroll events
    // do not bubble, so this one is caught on the way down.
    el.addEventListener('scrollend', (event) => {
      const at = nearest(el);
      if (at !== index(el)) go(el, at, event);
    }, { capture: true, signal: off.signal });
    // The next and the previous button: a click, and so Enter and Space on a button.
    el.addEventListener('click', (event) => {
      const button = event.target instanceof Element ? event.target.closest('[data-part="previous"], [data-part="next"]') : null;
      if (!button || button.closest(ROOT) !== el || !slidesOf(el).length) return;
      go(el, index(el) + (button.getAttribute('data-part') === 'next' ? 1 : -1), event);
    }, { signal: off.signal });
    const observer = new MutationObserver(() => {
      sync(el);
      // Slides that arrived or left: show the value's slide. Any other change, such as content inside a slide,
      // leaves the view alone, even in the middle of the user's scrolling.
      const slides = slidesOf(el);
      if (slides.length === seen.length && slides.every((slide, i) => slide === seen[i])) return;
      seen = slides;
      show(el);
    });
    observer.observe(el, { childList: true, subtree: true, attributes: true, attributeFilter: ['data-part', 'role', 'aria-label', 'aria-labelledby', 'aria-disabled', 'disabled'] });
    return () => { off.abort(); observer.disconnect(); };
  };

  // Mounted once. `ref` is read untracked: a rerun would add the listeners again whenever a parent re-reads its
  // binding.
  $effect(() => untrack(() => (ref ? setup(ref) : undefined)));
  // At mount and whenever the value changes: the slides and the buttons follow it, and the view goes to its slide.
  $effect(() => {
    current();
    untrack(() => {
      if (!ref) return;
      sync(ref);
      show(ref);
    });
  });

  // data-ready one frame after the root is in the page, as on every Web Component (L6).
  $effect(() => {
    const root = untrack(() => ref);
    const at = requestAnimationFrame(() => root?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  });
</script>

<div
  {role}
  aria-roledescription={ROLEDESCRIPTION}
  {...rest}
  bind:this={ref}
  data-ui="carousel"
>{@render children?.()}</div>
